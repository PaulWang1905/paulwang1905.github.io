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
from oxie import Site, SiteConfig, SitemapEntry, load_updates_file  # noqa: E402

UPDATES_PAGE = "updates.html"


class PersonalSite(Site):
    '''
    oxie's Site plus an "All updates" page. oxie puts only the latest few
    updates on the home page; this renders every entry in
    source/updates.yaml to docs/updates.html and lists it in the sitemap.
    '''

    def __init__(self, config: SiteConfig = None) -> None:
        super().__init__(config)
        self.all_updates = []

    def render_simple_pages(self) -> None:
        # Hooked here so the page is written before the CSS step, which
        # scans the generated HTML for Tailwind classes.
        super().render_simple_pages()
        self.render_updates_page()

    def render_updates_page(self) -> None:
        updates_file = self.config.updates_file
        self.all_updates = (load_updates_file(updates_file, self.config)
                            if updates_file.exists() else [])
        html = self.template("updates_template.html").render(
            meta_data=self.meta_data,
            phrases=self.meta_data["phrases"],
            canonical=self.url_for(UPDATES_PAGE),
            updates=self.all_updates,
        )
        with open(self.config.output_dir / UPDATES_PAGE, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"{UPDATES_PAGE} built ({len(self.all_updates)} updates)")

    def sitemap_entries(self) -> list:
        latest = self.all_updates[0].date.strftime("%Y-%m-%d") if self.all_updates else None
        return super().sitemap_entries() + [SitemapEntry(self.url_for(UPDATES_PAGE), latest)]


config = SiteConfig(
    # source/, src/, docs/ defaults match this repo's layout
    simple_pages={"readings_note_template.html": "readings_note.html"},
    photography=True,
    thumbnails=True,
    pygments_style="github-dark",
)

if __name__ == "__main__":
    print(f"Building with oxie {oxie.__version__} from {oxie.__file__}")
    PersonalSite(config).build()
