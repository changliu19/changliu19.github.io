# Chang Liu — Academic Homepage

A single-page academic homepage. The page reads all of its content from plain
text files at runtime, so **you never have to touch the HTML to update it**.

## What to edit

| File | What it controls |
|------|------------------|
| `profile.json` | Name, title, affiliation, email, office, profile links, citation metrics, **section visibility** |
| `content/about.md` | About / bio, education, experience (Markdown) |
| `content/news.md` | News list (Markdown — each line starts with `- **YYYY.MM** — …`) |
| `content/awards.md` | Honors & awards (Markdown) |
| `content/service.md` | Academic service (Markdown) |
| `content/prospective.md` | Recruiting note (Markdown) |
| `publications.bib` | Publications — **standard BibTeX**, auto-rendered |
| `assets/profile.jpg` | Your photo (drop a file here named exactly `profile.jpg`) |

### Adding a publication
Append a normal BibTeX entry to `publications.bib`. Optional extra fields:

```bibtex
@inproceedings{mykey2025,
  title     = {My Great Paper},
  author    = {Chang Liu and Co Author},
  booktitle = {CVPR},
  venue     = {CVPR 2025},   % short badge shown on the page
  award     = {Oral},        % optional highlight badge
  year      = {2025},
  pdf       = {https://...}, % optional — adds a "PDF" button
  code      = {https://...}, % optional — "Code" button
  project   = {https://...}, % optional — "Project" button
  arxiv     = {https://...}  % optional — "arXiv" button
}
```

Your name (`Chang Liu`) is **bolded automatically** in every author list, and
papers are sorted by year (newest first). Edit `profile.json` if your display
name changes.

### Profile links
Edit the `links` object in `profile.json`. Use `"#"` as a placeholder until you
have a real URL (e.g. fill in `CV` and `GitHub`). Set `CV` to a PDF you place in
the repo, e.g. `"CV": "assets/cv.pdf"`.

### Show / hide sections
Every section can be toggled from the `sections` block in `profile.json` — set a
value to `false` to hide that section, `true` to show it. No HTML edits needed:

```json
"sections": {
  "about": true,
  "prospective": true,
  "news": false,
  "publications": true,
  "awards": false,
  "service": true,
  "contact": true
}
```

## Deploy to GitHub Pages

1. Create a repo (e.g. `your-username.github.io`, or any repo name).
2. Commit **all** files in this folder, keeping the structure intact:
   `index.html`, `profile.json`, `publications.bib`, the `content/` (and
   `assets/`) folders, and — for the Scholar auto-update — `scripts/` and
   `.github/`.
3. In the repo: **Settings → Pages → Build and deployment → Source: Deploy from
   a branch**, pick `main` / root, save.
4. Visit `https://your-username.github.io/` (or `…/repo-name/`). `index.html`
   is the homepage.

> The page loads content with `fetch()`, so it must be served over **http(s)**
> (GitHub Pages does this). Opening the `.html` file directly from disk
> (`file://`) will not load the Markdown/BibTeX — use Pages, or a local server
> such as `python3 -m http.server`.

## Local preview
```bash
python3 -m http.server 8000
# then open http://localhost:8000/
```

## Auto-update citation metrics from Google Scholar

The `citations` / `hindex` / `i10` numbers in `profile.json` can refresh
themselves on GitHub — no manual editing. A scheduled GitHub Action
(`.github/workflows/update-scholar.yml`) runs `scripts/update_scholar.py` weekly,
pulls the latest numbers from your Google Scholar profile via **SerpAPI**, and
commits the change back. The page reads `profile.json` as usual, so nothing on
the front end changes.

Google Scholar has no public API and blocks scrapers, which is why this goes
through SerpAPI (reliable; free tier is 100 searches/month — far more than a
weekly job needs).

**One-time setup:**

1. Sign up at <https://serpapi.com/> and copy your **API key** (Dashboard → Your
   Private API Key).
2. In your GitHub repo: **Settings → Secrets and variables → Actions → New
   repository secret**. Name it `SERPAPI_KEY`, paste the key, save.
3. Make sure **Settings → Actions → General → Workflow permissions** is set to
   **Read and write permissions** (so the job can commit the update).
4. Done. The job runs every Monday; to test it now, go to the **Actions** tab,
   pick *“Update Google Scholar metrics”*, and click **Run workflow**.

The author id is read automatically from your `"Google Scholar"` link in
`profile.json` (the `user=…` part). Change the schedule by editing the `cron`
line in the workflow. Prefer not to use SerpAPI? Swap the fetch in
`scripts/update_scholar.py` for the free `scholarly` library — just expect it to
fail occasionally when Scholar challenges GitHub's IPs.
