# Dev Notes

Working notes for the `oxie` site (paulwang1905.github.io). Not published —
`docs/` is the generated output and is cleaned on every build, so notes live
here in `notes/` (outside the build) instead.

---

## Build pipeline (how it fits together)

`python build.py` runs, in order ([build.py](../build.py) `__main__`):

1. `clean_old_files()` — wipes generated files in `docs/` (incl. `docs/styles.css`).
2. `generate_html()` — Markdown in `source/` → HTML in `docs/` via Jinja2 templates.
3. `render_reading_notes()`, `render_photography_page()`, `collect_static_files()`, `generate_thumbnails()`.
4. `build_css()` — `npm run build:css` = `NODE_ENV=production tailwindcss -i src/styles.css -o docs/styles.css`.
5. `build_pygments_css()`.

**Key ordering fact:** HTML is generated *before* CSS. Tailwind's `content`
globs in [tailwind.config.js](../tailwind.config.js) scan `docs/**/*.html`, so any
Tailwind/DaisyUI utility class must exist in the compiled HTML or it gets purged
from `docs/styles.css`. Editing `source/*.md` alone is not enough — rebuild.

---

## Timeline reimplementation (About page)

The About-page timeline in [source/page/aboutme.md](../source/page/aboutme.md) was
rebuilt (2026-07-06).

**Before:** each of 5 entries carried ~500 characters of repeated inline Tailwind
utilities, including fragile `before:`/`after:` pseudo-element positioning hacks.
Hard to read, hard to edit, and it hid two silent bugs (see gotchas).

**After:** semantic `<ol class="cv-timeline">` / `<li class="cv-item">` markup in
the Markdown, backed by one plain-CSS block in [src/styles.css](../src/styles.css).

**Why plain CSS instead of `@apply` component classes:** the CSS is written
directly against DaisyUI theme variables (`oklch(var(--p))`, `--b1`, `--b3`,
`--a`, `--bc`) and kept **outside** any `@layer`. That means:

- Never purged, regardless of build order (raw CSS outside `@layer` is untouched
  by Tailwind's tree-shaking; `@layer components` rules *are* purged if unused).
- No `@apply` validation pitfalls (see gotchas).
- Adapts to both the `winter` (light) and `dark` themes for free, since it reads
  the same variables DaisyUI swaps per theme.

To add an entry: copy one `<li class="cv-item">…</li>` block (date pill → phase
label → title → description). To restyle: edit the one `.cv-*` block.

---

## Gotchas discovered (reusable knowledge)

These bit us during the timeline work and will bite again elsewhere:

1. **DaisyUI v4 removed the `*-focus` color shades.** Classes like
   `text-primary-focus`, `bg-primary-focus`, `secondary-focus` no longer exist.
   In HTML they fail *silently* (Tailwind ignores unknown classes found in
   content), so the original timeline's label hover-color never actually did
   anything. The same class inside `@apply` is a hard build error. Use base
   colors + opacity (`oklch(var(--p) / 0.15)`) or a different real color instead.

2. **DaisyUI v4 colors are OKLCH, not HSL.** Theme variables are stored as
   space-separated OKLCH components, e.g. `--p: 56.86% 0.255 257.57`. Use them as
   `oklch(var(--p))` and `oklch(var(--bc) / 0.72)` — **not** `hsl(var(--p))`.

3. **`@apply group` is illegal.** `group` is a marker class with no styles; it
   must be a literal class on the element in the HTML. `@apply group` throws
   *"@apply should not be used with the 'group' utility"*.

4. **Production vs dev `@apply` strictness.** `npx tailwindcss` (no env) may
   compile CSS that `NODE_ENV=production npm run build:css` rejects. Always
   validate with the production command, since that's what `build.py` runs.

5. **`@layer components` is purgeable; raw CSS is not.** If you want CSS that
   survives regardless of what the HTML references, write plain CSS outside any
   layer.

---

## Improvement backlog

### Content — [source/page/aboutme.md](../source/page/aboutme.md)
Fixed on 2026-07-06 (typos): "Memberof" → "Member of", "ArtificiaI" (capital I)
→ "Artificial", "Univeresity" → "University", "three month" → "three months",
"DPhil (PHD)" → "DPhil (PhD)". If reverted, re-apply.

### Maintainability — templates
`grep -rlE 'class="[^"]{120,}"' src/` finds long inline utility blobs in
[src/template.html](../src/template.html), [src/footer.html](../src/footer.html),
[src/blog_template.html](../src/blog_template.html),
[src/category_template.html](../src/category_template.html),
[src/photography_template.html](../src/photography_template.html). Same readability
problem the timeline had. Candidates for extraction into named CSS the same way,
if/when they need editing. Low priority — they render fine.

### Housekeeping
- Audit the whole `source/` tree for any remaining DaisyUI `*-focus` classes
  (they're dead no-ops): `grep -rn "\-focus" source/`.
- `package.json` lists React-oriented deps (`lucide-react`, `class-variance-
  authority`, `tailwind-merge`, `clsx`) that this static Python/Jinja site does
  not appear to use. Worth confirming and pruning to slim `node_modules`.

---

## Quick reference

```bash
# Full rebuild (regenerates docs/ then compiles CSS)
python build.py

# Just recompile CSS (only picks up classes already present in docs/*.html)
NODE_ENV=production npm run build:css

# Preview
# open docs/index.html, or serve docs/ with a static file server
```
