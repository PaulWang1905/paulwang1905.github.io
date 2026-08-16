'''
Parallel build entry using the oxie package (decoupling work in progress).

The official build remains `python build.py`. This file exercises the new
`oxie` package with this site's configuration and must produce output
identical to build.py. Once verified and adopted, this config can simply
replace build.py.

Run with:  python build_oxie.py
'''
from oxie import Site, SiteConfig

config = SiteConfig(
    # source/, src/, docs/ defaults match this repo's layout
    simple_pages={"readings_note_template.html": "readings_note.html"},
    photography=True,
    thumbnails=True,
    pygments_style="github-dark",
)

if __name__ == "__main__":
    Site(config).build()
