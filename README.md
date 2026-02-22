# Tin Cheuk Leung Academic Website (Jekyll)

A lightweight, data-driven academic website compatible with GitHub Pages.

## Local development

1. Install Ruby and Bundler.
2. Install dependencies:
   ```bash
   bundle install
   ```
3. Run locally:
   ```bash
   make serve
   ```
4. Open `http://127.0.0.1:4000`.

## Paper update workflow (drop-in)

Single command:

```bash
make update-papers
```

This command runs `python3 scripts/build_paper_index.py` and updates:

- `/Users/tincheukleung/Dropbox (Personal)/Website/_data/working_papers.yml`
- `/Users/tincheukleung/Dropbox (Personal)/Website/_data/publications.yml`
- `/Users/tincheukleung/Dropbox (Personal)/Website/_data/papers_autodraft.yml`
- `/Users/tincheukleung/Dropbox (Personal)/Website/assets/search/papers_index.json`

### Data schema for papers

Each paper entry in `working_papers.yml` and `publications.yml` includes:

- `id` (stable)
- `title`
- `authors` (list)
- `year`
- `date`
- `type` (`working_paper` or `publication`)
- `external_url` (optional)
- `pdf_path` (optional)
- `abstract` (auto-generated)
- `fulltext_hash` (auto-generated)
- `fulltext_excerpt` (auto-generated)

Optional flags:

- `featured: true` on working papers to show on the homepage Featured Working Papers section.

### Adding a new paper

1. Put the PDF in one of:
   - `/Users/tincheukleung/Dropbox (Personal)/Website/papers/working papers/`
   - `/Users/tincheukleung/Dropbox (Personal)/Website/papers/publications/`
2. Add a minimal metadata entry to:
   - `/Users/tincheukleung/Dropbox (Personal)/Website/_data/working_papers.yml` or
   - `/Users/tincheukleung/Dropbox (Personal)/Website/_data/publications.yml`
3. Run:
   ```bash
   make update-papers
   ```
4. Check `/Users/tincheukleung/Dropbox (Personal)/Website/_data/papers_autodraft.yml`.
   - If a PDF did not match any metadata entry, a draft entry will be generated there.
   - Move/copy the draft entry into the correct main data file.
5. Commit and push.

### Updating an existing paper

1. Replace the PDF:
   - Same filename: preferred, the existing entry will update automatically.
   - New filename: supported; matching uses normalized title and fuzzy matching, but verify `pdf_path` after running.
2. Run:
   ```bash
   make update-papers
   ```
3. Commit and push.

### Notes on matching

The updater is robust to common filename differences:

- Case changes
- Punctuation differences
- `:` vs `-`
- Unicode punctuation differences

It also uses SHA-256 hashes (`fulltext_hash`) to skip abstract/fulltext extraction when a PDF is unchanged, unless `--refresh` is used.

## Search index

The generated search index is:

- `/Users/tincheukleung/Dropbox (Personal)/Website/assets/search/papers_index.json`

Each index item includes combined `searchable_text` (`title + authors + year/date + abstract + fulltext_excerpt`) for client-side filtering.

## Automation on GitHub (optional but enabled)

Workflow file:

- `/Users/tincheukleung/Dropbox (Personal)/Website/.github/workflows/update_papers.yml`

Behavior:

- Triggers on pushes to `main` when PDFs change under:
  - `papers/working papers/**`
  - `papers/publications/**`
- Runs `python3 scripts/build_paper_index.py`
- Commits generated files if there is a diff with message:
  - `Auto-update paper abstracts and search index`

Loop prevention:

- The workflow trigger only watches `papers/**`, while generated files are under `_data/` and `assets/search/`, so the bot commit does not retrigger the workflow.

## Utility commands

- Update papers/index: `make update-papers`
- Serve locally: `make serve`
- Quick checks/build: `make test`

## Deploy to GitHub Pages

1. Push this repository to GitHub.
2. In GitHub repo settings, enable Pages and select deployment from the default branch root.
3. GitHub Pages will build the site automatically.

## Where to edit content

- Site bio, contact, social links, CV links: `/Users/tincheukleung/Dropbox (Personal)/Website/_data/site.yml`
- Working papers metadata: `/Users/tincheukleung/Dropbox (Personal)/Website/_data/working_papers.yml`
- Publications metadata: `/Users/tincheukleung/Dropbox (Personal)/Website/_data/publications.yml`
- Work in progress / other working papers: `/Users/tincheukleung/Dropbox (Personal)/Website/_data/research.yml`
- Media mentions and Chinese columns links: `/Users/tincheukleung/Dropbox (Personal)/Website/_data/media.yml`

## Custom domain (CNAME)

After domain DNS and GitHub verification are complete:

1. Add a `CNAME` file at repo root with your domain (for example `www.example.com`).
2. In GitHub Pages settings, set the same custom domain.
3. Enable HTTPS in Pages settings.
