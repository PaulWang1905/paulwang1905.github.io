# oxie

## Introduction

**oxie** is a static site/blog generator written in Python. It converts Markdown files into a styled, SEO-friendly static website using Jinja2 templates and Tailwind CSS. It is designed for personal blogs and supports posts, pages, categories, tags, and structured data (JSON-LD).

## Status
[![Awesome](https://awesome.re/badge.svg)](https://github.com/PaulWang1905/paulwang1905.github.io) 
![](https://img.shields.io/github/last-commit/PaulWang1905/paulwang1905.github.io?color=green) 
[![Build Status](https://github.com/PaulWang1905/Readings/workflows/CI/badge.svg)](https://github.com/PaulWang1905/paulwang1905.github.io/actions?workflow=Deploy)

## Features

- Converts Markdown posts and pages to HTML
- Uses Jinja2 templates for flexible theming
- Tailwind CSS for modern styling
- Category and tag pages
- Blog index and category index generation
- JSON-LD structured data for SEO
- Static asset copying (images, etc.)
- Google Spreadsheet integration for updates (requires configuration)
- Easy to extend and customize

## Folder Structure

```
source/
  index.md
  post/
    *.md
  page/
    *.md
docs/
  index.html
  post/
    *.html
  page/
    *.html
  styles.css
  image/
src/
  *.html (templates)
  styles.css
build.py
requirements.txt
package.json
tailwind.config.js
postcss.config.js
```

## Requirements

- Python 3.8+
- Node.js & npm

Python dependencies (see `requirements.txt`):
- Jinja2
- Markdown
- pymdown-extensions
- MarkupSafe
- pandas

Node.js dependencies (see `package.json`):
- tailwindcss
- autoprefixer
- daisyui
- postcss
- @tailwindcss/typography
- @tailwindcss/forms
- tailwindcss-animate

## Usage

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Build the site:**
   ```bash
   python build.py
   ```

   This will:
   - Clean old files in `docs/`
   - Convert Markdown to HTML using templates
   - Copy static assets (images, etc.)
   - Build CSS with Tailwind

4. **Serve the site:**
   - Open `docs/index.html` in your browser, or use a static file server.

## Customization

- Edit templates in `src/`
- Add or edit Markdown files in `source/post/` and `source/page/`
- Update site metadata in `src/meta_data.json`
- Configure Tailwind in `tailwind.config.js`



