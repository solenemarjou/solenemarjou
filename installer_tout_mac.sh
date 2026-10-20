#!/bin/bash
# Installe la boîte à outils créateur sur Mac.
# Usage : ouvrir Terminal, puis coller :
#   curl -fsSL https://raw.githubusercontent.com/solenemarjou/solenemarjou/master/installer_tout_mac.sh | bash
set -u
REPO_RAW="https://raw.githubusercontent.com/solenemarjou/solenemarjou/master"
ok()   { echo "✅ $1"; }
warn() { echo "⚠️  $1"; }

echo "=== 1/5 Homebrew ==="
if ! command -v brew >/dev/null 2>&1; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  [ -x /opt/homebrew/bin/brew ] && eval "$(/opt/homebrew/bin/brew shellenv)" \
    && echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> "$HOME/.zprofile"
fi
command -v brew >/dev/null 2>&1 && ok "Homebrew prêt" || { warn "Homebrew non installé, arrêt."; exit 1; }

echo "=== 2/5 Applications ==="
# Retire une ligne si tu ne veux pas l'app.
APPS="
claude
raycast
obsidian
cleanshot
textexpander
keyboard-maestro
"
for app in $APPS; do
  if brew list --cask "$app" >/dev/null 2>&1; then ok "$app déjà installé"
  elif brew install --cask "$app"; then ok "$app installé"
  else warn "$app : échec, à installer à la main"; fi
done

echo "=== 3/5 Claude Code (ligne de commande) ==="
if command -v claude >/dev/null 2>&1; then ok "Claude Code déjà installé"
else curl -fsSL https://claude.ai/install.sh | bash && ok "Claude Code installé" || warn "Claude Code : échec"; fi

echo "=== 4/5 Effets DaVinci ==="
curl -fsSL "$REPO_RAW/telecharger_effets_davinci.sh" | bash || warn "Téléchargement des effets incomplet"

echo "=== 5/5 Script Glow dans DaVinci ==="
SCRIPTS="$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility"
mkdir -p "$SCRIPTS"
curl -fsSL "$REPO_RAW/glow_effect_davinci.py" -o "$SCRIPTS/Glow Effect.py" \
  && ok "Script Glow installé (DaVinci > Espace de travail > Scripts > Glow Effect)" \
  || warn "Script Glow : échec"

echo
echo "Terminé. Redémarre DaVinci Resolve, puis suis la checklist du guide."
