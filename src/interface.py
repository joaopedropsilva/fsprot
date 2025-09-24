import os
import subprocess
import tempfile


def edit_file(content: str) -> bytes:
    fd, tmp_path = tempfile.mkstemp(dir="/tmp")
    with os.fdopen(fd, "w") as temp:
        temp.write(content)
        temp.flush()
        os.fsync(temp.fileno())

    editor = os.environ["EDITOR"]
    assert editor != "", \
        "No default editor set for this operation. " \
        "Make sure $EDITOR is set."

    subprocess.run([editor, tmp_path])

    new_content = b""
    with open(tmp_path, "rb") as temp:
        new_content = temp.read()

    os.unlink(tmp_path)

    return new_content
