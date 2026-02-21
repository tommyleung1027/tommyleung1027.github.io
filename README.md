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
   bundle exec jekyll serve
   ```
4. Open `http://127.0.0.1:4000`.

## Deploy to GitHub Pages

1. Push this repository to GitHub.
2. In GitHub repo settings, enable Pages and select deployment from the default branch root.
3. GitHub Pages will build the site automatically.

## Where to edit content

- Site bio, contact, social links, CV links: `/Users/tincheukleung/Dropbox (Personal)/Website/_data/site.yml`
- Working papers, publications, work in progress: `/Users/tincheukleung/Dropbox (Personal)/Website/_data/research.yml`
- Media mentions and Chinese columns links: `/Users/tincheukleung/Dropbox (Personal)/Website/_data/media.yml`

## Custom domain (CNAME)

After domain DNS and GitHub verification are complete:

1. Add a `CNAME` file at repo root with your domain (for example `www.example.com`).
2. In GitHub Pages settings, set the same custom domain.
3. Enable HTTPS in Pages settings.
