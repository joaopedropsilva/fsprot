#!/usr/bin/bash

INSTALL_PATH=/usr/local/share/fsprot

echo [fsprot-setup] Installing app at $INSTALL_PATH
# overrides everything, change install path to
# private user path or deny this behaviour
sudo rm -rf $INSTALL_PATH
sudo mkdir $INSTALL_PATH
sudo cp -r ./src/* $INSTALL_PATH
sudo chmod --recursive 0644 $INSTALL_PATH
sudo chmod 0755 $INSTALL_PATH
sudo chmod +x $INSTALL_PATH/fsprot

echo [fsprot-setup] Installing app dependencies
python3 -m venv $INSTALL_PATH/venv
$INSTALL_PATH/venv/bin/python3 -m pip install -r ./requirements.txt

echo [fsprot-setup] Compiling scripts
# Add compilation with -D flag
gcc -o $INSTALL_PATH/cap $INSTALL_PATH/cap.c
sudo rm $INSTALL_PATH/cap.c
sudo setcap cap_dac_override,cap_dac_read_search+ep $INSTALL_PATH/cap

echo [fsprot-setup] Adding CLI to PATH
USER_SHELL=$(getent passwd "$USER" | cut -d: -f7)
case "$USER_SHELL" in
    */bash)  SHELL_CONFIG_FILE="$HOME/.bashrc" ;;
    */zsh)   SHELL_CONFIG_FILE="$HOME/.zshrc" ;;
    */fish)  SHELL_CONFIG_FILE="$HOME/.config/fish/config.fish" ;;
    *)       echo "Unable to add to PATH - unknown shell: $user_shell" >&2; exit 1 ;;
esac
echo 'export PATH=$PATH:'"$INSTALL_PATH/fsprot" >> $SHELL_CONFIG_FILE
