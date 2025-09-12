#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv) {
    execv(
        "/home/joaopedropsilva/fsprot/venv/bin/python",
        (char *[]){"python", "/home/joaopedropsilva/fsprot/src/write.py", argv[1], argv[2], argv[3], NULL}
    );

    return 1;
}
