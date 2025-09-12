import os
import tempfile
from sys import argv

from header import FileHeader


def write_to_file(file: str, passphrase: str, content: str) -> None:
    file_dir = os.path.dirname(file)
    fd, tmp_path = tempfile.mkstemp(dir=file_dir)
    try:
        with os.fdopen(fd, "w") as temp:
            temp.write(content)
            temp.flush()
            os.fsync(temp.fileno())

        # Revalidate file parameters to check if 
        # it was not altered during execution
        FileHeader.get_header_info(file, passphrase.encode("utf-8"))

        os.rename(tmp_path, file)
    except Exception as e:
        print(e)
        os.unlink(tmp_path)


if __name__ == "__main__":
    file = argv[1]
    passphrase = argv[2]
    content = argv[3]

    write_to_file(file, passphrase, content)
