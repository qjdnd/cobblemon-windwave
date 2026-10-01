"""Zips pack/ into dist/ so it can be dropped into resourcepacks/ and datapacks/."""
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(ROOT, "pack")
DIST = os.path.join(ROOT, "dist")
NAME = "cobblemon-windwave-gulpin-swalot.zip"


def main():
    os.makedirs(DIST, exist_ok=True)
    out = os.path.join(DIST, NAME)
    files = []
    for base, _, names in os.walk(PACK):
        for n in names:
            full = os.path.join(base, n)
            files.append((os.path.relpath(full, PACK).replace(os.sep, "/"), full))
    files.sort()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for arc, full in files:
            info = zipfile.ZipInfo(arc, date_time=(2026, 10, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            with open(full, "rb") as f:
                z.writestr(info, f.read())
    print(out, len(files), "files")


if __name__ == "__main__":
    main()
