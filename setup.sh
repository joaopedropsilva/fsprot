#!/usr/bin/env bash

SETUP_PATH="$(realpath "$(dirname $0)")"
APP_PREFIX=.fsprot
NO_PATH_EXPORT=0
INSTALL_PATH=$HOME/$APP_PREFIX

while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-path-export)
            NO_PATH_EXPORT=1
            shift
            ;;
        *)
            INSTALL_PATH=$1/$APP_PREFIX
            shift
            ;;
    esac
done

if [ ! -d $(dirname "$INSTALL_PATH") ]; then
    echo "Unable to install app on $INSTALL_PATH, check if directory exists." >&2
    exit 1
fi

echo [fsprot-setup] Installing app at $INSTALL_PATH
mkdir -p $INSTALL_PATH/src
cp -r $SETUP_PATH/src/* $INSTALL_PATH/src
chmod 0644 $INSTALL_PATH/src/*.{py,c}

echo [fsprot-setup] Installing app dependencies
python3 -m venv $INSTALL_PATH/venv
$INSTALL_PATH/venv/bin/python3 -m pip install -r ./requirements.txt

echo [fsprot-setup] Compiling scripts
# Add compilation with -D flag
gcc -o $INSTALL_PATH/src/cap $INSTALL_PATH/src/cap.c
rm $INSTALL_PATH/src/cap.c
if (( "$EUID" != 0 )); then
    sudo setcap cap_dac_override,cap_dac_read_search+ep $INSTALL_PATH/src/cap
else
    setcap cap_dac_override,cap_dac_read_search+ep $INSTALL_PATH/src/cap
fi

echo [fsprot-setup] Creating app executable
cat <<END_SCRIPT > $INSTALL_PATH/fsprot
#!/usr/bin/env bash

INSTALL_PATH=$INSTALL_PATH
\$INSTALL_PATH/venv/bin/python3 \$INSTALL_PATH/src/cli.py "\$@"
END_SCRIPT
chmod +x $INSTALL_PATH/fsprot

if [[ "$NO_PATH_EXPORT" -eq 0 ]]; then
    echo [fsprot-setup] Adding CLI to PATH
    USER_SHELL=$(getent passwd "$USER" | cut -d: -f7)
    case "$USER_SHELL" in
        */bash)  SHELL_CONFIG_FILE="$HOME/.bashrc" ;;
        */zsh)   SHELL_CONFIG_FILE="$HOME/.zshrc" ;;
        *)       echo "Unable to add to PATH - unknown shell: $USER_SHELL" >&2; exit 1 ;;
    esac
    [ -f "$SHELL_CONFIG_FILE" ] || touch "$SHELL_CONFIG_FILE"
    PATH_EXP='export PATH=$PATH:'"$INSTALL_PATH"
    if ! grep -qxF "$PATH_EXP" "$SHELL_CONFIG_FILE"; then
        echo $PATH_EXP >> $SHELL_CONFIG_FILE
    fi
fi
