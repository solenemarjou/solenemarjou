#!/usr/bin/env python
# Effet "GLOW" (silhouette lumineuse) pour DaVinci Resolve.
# A lancer dans DaVinci : Espace de travail > Console > onglet "Py3" > coller > Entrée.
# Le script crée une NOUVELLE timeline "GLOW FX" dans le projet ouvert,
# avec 2 rushes du Media Pool, et ajoute l'effet en alternance avec le plan normal.

# --- Réglages -------------------------------------------------------------
RUSH_NAMES = []          # ex: ["C0012.MP4", "C0015.MP4"] ; vide = les 2 premières vidéos du Media Pool
TIMELINE_NAME = "GLOW FX"
GLOW_TEXT = "CREATE\nTHE\nGLOW\nEFFECT"
# Séquence par rush : (durée en secondes, avec effet ?)
PATTERN = [(1.0, True), (0.6, False), (1.0, True), (0.6, False), (1.6, True)]
# --------------------------------------------------------------------------

try:
    resolve  # existe déjà dans la console DaVinci
except NameError:
    import DaVinciResolveScript as dvr
    resolve = dvr.scriptapp("Resolve")

project = resolve.GetProjectManager().GetCurrentProject()
mp = project.GetMediaPool()


def all_clips(folder):
    out = list(folder.GetClipList() or [])
    for sub in folder.GetSubFolderList() or []:
        out += all_clips(sub)
    return out


clips = [c for c in all_clips(mp.GetRootFolder())
         if "Video" in (c.GetClipProperty("Type") or "")]
if RUSH_NAMES:
    clips = [c for n in RUSH_NAMES for c in clips if c.GetName() == n]
rushes = clips[:2]
if len(rushes) < 2:
    raise SystemExit("Il faut au moins 2 clips vidéo dans le Media Pool.")
print("Rushes :", [c.GetName() for c in rushes])

timeline = mp.CreateEmptyTimeline(TIMELINE_NAME)
project.SetCurrentTimeline(timeline)
fps = float(timeline.GetSetting("timelineFrameRate") or 25)


def set_in(tool, name, value):
    try:
        tool.SetInput(name, value)
    except Exception:
        pass


def build_glow(item, with_text):
    item.AddFusionComp()
    comp = item.GetFusionCompByIndex(1)
    comp.Lock()
    media_in = comp.FindTool("MediaIn1")
    media_out = comp.FindTool("MediaOut1")

    # 1) Fond : plus sombre, désaturé, teinté bleu
    bg = comp.AddTool("BrightnessContrast", -32768, -32768)
    bg.ConnectInput("Input", media_in)
    set_in(bg, "Gain", 0.55)
    set_in(bg, "Saturation", 0.7)
    tint = comp.AddTool("ColorGain", -32768, -32768)
    tint.ConnectInput("Input", bg)
    set_in(tint, "GainRed", 0.6)
    set_in(tint, "GainGreen", 0.85)
    set_in(tint, "GainBlue", 1.25)

    # 2) Silhouette : on brûle les hautes lumières en blanc
    burn = comp.AddTool("BrightnessContrast", -32768, -32768)
    burn.ConnectInput("Input", media_in)
    set_in(burn, "Saturation", 0.0)
    set_in(burn, "Gain", 2.6)
    set_in(burn, "Contrast", 0.8)
    set_in(burn, "Lift", -0.35)

    # 3) Halo + rayons
    glow = comp.AddTool("SoftGlow", -32768, -32768)
    glow.ConnectInput("Input", burn)
    set_in(glow, "Threshold", 0.4)
    set_in(glow, "Gain", 3.0)
    set_in(glow, "XGlowSize", 25.0)
    rays = comp.AddTool("DirectionalBlur", -32768, -32768)
    rays.ConnectInput("Input", glow)
    set_in(rays, "Type", 3)       # Zoom
    set_in(rays, "Length", 0.15)
    set_in(rays, "Glow", 0.6)

    # 4) Glow en mode Écran sur le fond bleu
    merge = comp.AddTool("Merge", -32768, -32768)
    merge.ConnectInput("Background", tint)
    merge.ConnectInput("Foreground", rays)
    set_in(merge, "ApplyMode", "Screen")
    last = merge

    # 5) Texte sur le corps lumineux (dernier plan)
    if with_text:
        txt = comp.AddTool("TextPlus", -32768, -32768)
        set_in(txt, "StyledText", GLOW_TEXT)
        set_in(txt, "Size", 0.06)
        set_in(txt, "Red1", 0.15)
        set_in(txt, "Green1", 0.15)
        set_in(txt, "Blue1", 0.15)
        merge2 = comp.AddTool("Merge", -32768, -32768)
        merge2.ConnectInput("Background", merge)
        merge2.ConnectInput("Foreground", txt)
        last = merge2

    media_out.ConnectInput("Input", last)
    comp.Unlock()


for clip in rushes:
    total = int(float(clip.GetClipProperty("Frames") or 0))
    need = int(sum(d for d, _ in PATTERN) * fps)
    scale = min(1.0, total / float(need)) if need else 1.0
    pos = max(0, (total - int(need * scale)) // 2)   # on prend le milieu du rush
    for i, (dur, fx) in enumerate(PATTERN):
        n = max(2, int(dur * fps * scale))
        items = mp.AppendToTimeline([{
            "mediaPoolItem": clip,
            "startFrame": pos,
            "endFrame": pos + n - 1,
            "trackIndex": 1,
        }])
        pos += n
        if fx and items:
            build_glow(items[0], with_text=(i == len(PATTERN) - 1))

print("OK : timeline '%s' créée avec l'effet Glow sur %d rushes." % (TIMELINE_NAME, len(rushes)))
