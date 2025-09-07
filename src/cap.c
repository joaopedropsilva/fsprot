#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv) {
    execv("/usr/bin/python3", (char *[]){"python3", "/home/joaopedropsilva/fsprot/main.py", argv[1], argv[2], NULL});
    return 1;
}

