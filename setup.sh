#!/usr/bin/env bash

APP_PREFIX=fsprot
SOURCE_PATH="$(realpath "$(dirname $0)")"
INSTALL_PATH=/usr/local/bin/$APP_PREFIX

if [[ -d $INSTALL_PATH ]]; then
    echo [fsprot-setup] Application already installed.
    exit
fi

if [[ $EUID -gt 0 ]]; then
    echo [fsprot-setup] Application setup must be run as root.
    exit 1
fi

echo [fsprot-setup] Installing app at $INSTALL_PATH.
mkdir -p $INSTALL_PATH/src
cp -r $SOURCE_PATH/src/* $INSTALL_PATH/src
chmod 0644 $INSTALL_PATH/src/*.{py,c}

echo [fsprot-setup] Installing app dependencies.
python3 -m venv $INSTALL_PATH/venv
$INSTALL_PATH/venv/bin/python3 -m pip install -r $SOURCE_PATH/requirements.txt

echo [fsprot-setup] Compiling scripts.
# Add compilation with -D flag
gcc -o $INSTALL_PATH/src/cap $INSTALL_PATH/src/cap.c
rm $INSTALL_PATH/src/cap.c
setcap cap_dac_override,cap_dac_read_search+ep $INSTALL_PATH/src/cap

echo [fsprot-setup] Creating app executable.
cat <<END_SCRIPT > $INSTALL_PATH/fsprot
#!/usr/bin/env bash

INSTALL_PATH=$INSTALL_PATH
\$INSTALL_PATH/venv/bin/python3 \$INSTALL_PATH/src/cli.py "\$@"
END_SCRIPT
chmod +x $INSTALL_PATH/fsprot
