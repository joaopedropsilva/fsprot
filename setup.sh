#!/usr/bin/env bash

APP_PREFIX=fsprot
SOURCE_PATH="$(realpath "$(dirname $0)")"
APP_EXECUTOR_PATH=/usr/local/bin/$APP_PREFIX
INSTALL_PATH=/usr/local/lib/$APP_PREFIX

if [[ -d $INSTALL_PATH && -z "$1" ]]; then
    echo [fsprot-setup] Application already installed. Use -r option to force reinstall.
    exit
fi
if [[ "$1" != "-r" ]]; then
    echo Unknown argument $1.
    exit 1
fi

if [[ $EUID -gt 0 ]]; then
    echo [fsprot-setup] Application setup must be run as root.
    exit 1
fi

echo [fsprot-setup] Installing app at $INSTALL_PATH.
rm -rf $INSTALL_PATH > /dev/null
mkdir $INSTALL_PATH
cp -r $SOURCE_PATH/src/* $INSTALL_PATH

echo [fsprot-setup] Installing app dependencies.
python3 -m venv $INSTALL_PATH/venv
$INSTALL_PATH/venv/bin/python3 -m pip install -r $SOURCE_PATH/requirements.txt

echo [fsprot-setup] Compiling scripts.
# Add compilation with -D flag
gcc -o $INSTALL_PATH/cap $INSTALL_PATH/cap.c
rm $INSTALL_PATH/cap.c
setcap cap_dac_override,cap_dac_read_search+ep $INSTALL_PATH/cap

echo [fsprot-setup] Creating app executable.
cat <<END_SCRIPT > $APP_EXECUTOR_PATH
#!/usr/bin/env bash

INSTALL_PATH=$INSTALL_PATH
\$INSTALL_PATH/venv/bin/python3 \$INSTALL_PATH/cli.py "\$@"
END_SCRIPT
chmod +x $APP_EXECUTOR_PATH
