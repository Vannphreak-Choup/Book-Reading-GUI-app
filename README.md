# Book-Reading-GUI-app
# Read da Book

A lightweight PDF reader desktop app built with Python and CustomTkinter. Supports adding PDFs from your local machine or directly from a URL, with lazy rendering for smooth performance on large documents.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![PyPI](https://img.shields.io/pypi/v/pdfreading-app)

---

## Features

- 📂 Add PDFs from your local file system
- 🌐 Add PDFs directly from a URL
- 🔍 Zoom in and out while staying on the current page
- ⬅️ ➡️ Navigate pages with previous/next buttons or by typing a page number
- 💾 Automatically saves and restores your reading progress per book
- ⚡ Lazy rendering — only renders pages near the visible area for smooth scrolling on large documents
- 🗂️ Persistent library — your added PDFs are saved and restored on every startup

---

## Installation

```bash
pip install pdfreading-app
```

Then launch it from anywhere with:

```bash
pdfreading-app
```

---

## Adding PDFs via URL
 
You can load a PDF directly from the internet by clicking the **From URL** button and pasting a link.
 
### What works
- Direct links to `.pdf` files hosted on open servers (e.g. university sites, government sites, open-access repositories)
- URLs that end with `.pdf` and don't require login or authentication
- Examples:
  - `https://pdfobject.com/pdf/sample.pdf`
 
### What doesn't work
- Sites that block programmatic downloads (**403 Forbidden**) — this is a server-side restriction that cannot be bypassed. Common examples include file-sharing sites, academic paywalls, and sites that require you to click through a page before downloading.
- Links that redirect to a download page instead of the PDF file directly
- PDFs behind a login or authentication wall
- Google Drive, Dropbox, or similar cloud storage share links
 
### Tip
If a URL gives you a **403 Access Denied** error, just download the PDF manually in your browser and use the **Add PDF** button instead.
 
---

## Requirements

- Python 3.9+
- Windows, macOS, or Linux

Dependencies are installed automatically:
- [PyMuPDF](https://pymupdf.readthedocs.io/) — PDF rendering
- [Pillow](https://python-pillow.org/) — image handling
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — modern UI

> **Linux / macOS users:** Tkinter does not come pre-installed on all systems.
> If you get a `No module named 'tkinter'` error, install it manually:
>
> **Ubuntu / Debian:**
> ```bash
> sudo apt install python3-tk
> ```
> **Fedora:**
> ```bash
> sudo dnf install python3-tkinter
> ```
> **macOS (Homebrew):**
> ```bash
> brew install python-tk
> ```

---

## Run from source

```bash
# Clone the repo
git clone https://github.com/Vannphreak-Choup/Book-Reading-GUI-app.git
cd Book-Reading-GUI-app

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

# Install in editable mode
pip install -e .

# Run
python -m pdfreading.main
```

---

## Project Structure

```
src/
└── pdfreading/
    ├── main.py              # entry point
    ├── assets/              # icons and images
    ├── openDialog/          # file and URL dialogs
    │   ├── AddFile.py
    │   └── Addurl.py
    └── utils/
        ├── Data.py          # shared app state
        ├── UI.py            # UI layout
        └── functionality.py # core logic
```

---

## License

MIT