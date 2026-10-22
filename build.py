'''
Build puyuwang.org with the oxie static site generator (installed from
PyPI, pinned in requirements.txt).

Run with:  python build.py

The previous self-contained build script is kept as build_legacy.py.
'''
import sys
from pathlib import Path

# This repo keeps the old vendored copy of oxie in ./oxie as a backup.
# Python searches this script's folder first, so `import oxie` would load
# that copy instead of the installed package. Drop the folder from the
# import path before importing.
HERE = Path(__file__).resolve().parent
sys.path[:] = [p for p in sys.path if Path(p or '.').resolve() != HERE]

import oxie  # noqa: E402
from oxie import Site, SiteConfig  # noqa: E402

config = SiteConfig(
    # source/, src/, docs/ defaults match this repo's layout
    simple_pages={"readings_note_template.html": "readings_note.html"},
    photography=True,
    thumbnails=True,
    pygments_style="github-dark",
)

if __name__ == "__main__":
    print(f"Building with oxie {oxie.__version__} from {oxie.__file__}")
    Site(config).build()
