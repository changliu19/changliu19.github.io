#!/usr/bin/env python3
"""Update citation metrics in profile.json from Google Scholar via SerpAPI.

Runs in CI (see .github/workflows/update-scholar.yml). Reads the Scholar author
id from profile.json's "Google Scholar" link (or the SCHOLAR_ID env var),
queries the SerpAPI Google Scholar Author API, and writes citations / h-index /
i10 back into profile.json.

The write is a targeted regex replace of just the three numbers, so the commit
diff stays minimal and the file's hand-formatting is preserved.

Env:
  SERPAPI_KEY  (required)  -- your serpapi.com API key
  SCHOLAR_ID   (optional)  -- override the author id; otherwise parsed from the
                              "Google Scholar" link in profile.json
"""

import os
import re
import sys
import json
import urllib.parse
import urllib.request

PROFILE = os.path.join(os.path.dirname(__file__), "..", "profile.json")


def scholar_id_from_profile(text):
    m = re.search(r'"Google Scholar"\s*:\s*"([^"]+)"', text)
    if not m:
        return None
    qs = urllib.parse.urlparse(m.group(1)).query
    return urllib.parse.parse_qs(qs).get("user", [None])[0]


def fetch_metrics(author_id, api_key):
    url = "https://serpapi.com/search.json?" + urllib.parse.urlencode({
        "engine": "google_scholar_author",
        "author_id": author_id,
        "api_key": api_key,
    })
    with urllib.request.urlopen(url, timeout=60) as r:
        data = json.load(r)
    if "error" in data:
        raise RuntimeError("SerpAPI error: " + data["error"])
    table = data.get("cited_by", {}).get("table", [])
    out = {}
    for row in table:
        for key, field in (("citations", "citations"),
                           ("h_index", "hindex"),
                           ("i10_index", "i10")):
            if key in row and isinstance(row[key], dict) and "all" in row[key]:
                out[field] = int(row[key]["all"])
    if "citations" not in out or "hindex" not in out:
        raise RuntimeError("Could not parse citations/h-index from response: "
                           + json.dumps(table)[:500])
    return out


def main():
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        sys.exit("SERPAPI_KEY is not set")

    with open(PROFILE, encoding="utf-8") as f:
        text = f.read()

    author_id = os.environ.get("SCHOLAR_ID") or scholar_id_from_profile(text)
    if not author_id:
        sys.exit("No Scholar author id (set SCHOLAR_ID or add a Google Scholar link)")

    metrics = fetch_metrics(author_id, api_key)
    print("Fetched from Scholar:", metrics)

    new_text = text
    for field, value in metrics.items():
        new_text, n = re.subn(
            r'("%s"\s*:\s*)\d+' % field, r"\g<1>%d" % value, new_text, count=1)
        if n == 0:
            print("  (note: %r not present in profile.json, skipped)" % field)

    if new_text == text:
        print("No change — metrics already up to date.")
        return

    with open(PROFILE, "w", encoding="utf-8") as f:
        f.write(new_text)
    print("profile.json updated.")


if __name__ == "__main__":
    main()
