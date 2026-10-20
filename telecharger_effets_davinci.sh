#!/bin/bash
# Télécharge les effets gratuits DaVinci Resolve (GitHub) dans ~/Downloads/Effets-DaVinci
# Usage sur Mac : ouvrir Terminal, puis :  bash telecharger_effets_davinci.sh
set -u
DEST="$HOME/Downloads/Effets-DaVinci"
mkdir -p "$DEST" && cd "$DEST" || exit 1

REPOS="
Akascape/Rembg-Fuse:main
Akascape/RemObj-Fuse:main
50asa/shitsukan-diffusion-kit:main
nmbr73/Shaderfuse:main
J-i-P-i/Shadertoys:main
FusionPixelStudio/Free-Davinci-Resolve-Tools:main
purzbeats/purzos-ofx:main
jdanna/Resolve_Tools_Public:main
mrJohnHolt/davinci-resolve-fusion-expressions:master
brunocbreis/macros:master
aconstlink/DRMacros:main
nxy7/fusion_effects:main
Demystify-Color/DCTLs:main
ecpwll/dctl-tools:main
ijrunner/filmmatch:main
Greenysmac/awesome-davinci-resolve:main
"

for entry in $REPOS; do
  repo="${entry%%:*}"; branch="${entry##*:}"
  name="$(echo "$repo" | tr '/' '_')"
  echo "→ $repo"
  if curl -fsSL "https://github.com/$repo/archive/refs/heads/$branch.zip" -o "$name.zip"; then
    unzip -qo "$name.zip" -d "$name" && rm "$name.zip"
  else
    echo "   échec du téléchargement : $repo"
  fi
done

echo "Terminé : tout est dans $DEST"
open "$DEST"
