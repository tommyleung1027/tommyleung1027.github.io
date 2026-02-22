#!/usr/bin/env python3
"""Build paper metadata and search index from local PDF folders.

This script keeps `_data/working_papers.yml` and `_data/publications.yml` in sync
with PDFs under:
  - papers/working papers/
  - papers/publications/

It updates abstracts and excerpts incrementally using `fulltext_hash`, writes an
autodraft file for unmatched PDFs, and generates `assets/search/papers_index.json`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import quote, unquote

import yaml
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
WORKING_FILE = ROOT / "_data" / "working_papers.yml"
PUBLICATIONS_FILE = ROOT / "_data" / "publications.yml"
RESEARCH_FILE = ROOT / "_data" / "research.yml"
AUTODRAFT_FILE = ROOT / "_data" / "papers_autodraft.yml"
SEARCH_INDEX_FILE = ROOT / "assets" / "search" / "papers_index.json"

PAPER_DIRS = {
    "working_paper": ROOT / "papers" / "working papers",
    "publication": ROOT / "papers" / "publications",
}

AUTHOR_SELF = "Tin Cheuk Leung"
DEFAULT_ABSTRACT = "Abstract unavailable. Please use the paper links."
ABSTRACT_MAX_CHARS = 2200
EXCERPT_MAX_CHARS = 2600
EXCERPT_SCAN_PAGES = 8
ABSTRACT_SCAN_PAGES = 12

MONTH_MAP = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "sept": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-extract abstract/fulltext excerpt even when fulltext_hash is unchanged.",
    )
    return parser.parse_args()


def load_yaml(path: Path, default: Any) -> Any:
    if not path.exists():
        return deepcopy(default)
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    if loaded is None:
        return deepcopy(default)
    return loaded


def dump_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(
            data,
            handle,
            sort_keys=False,
            allow_unicode=False,
            default_flow_style=False,
            width=1000,
        )


def normalize_title(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower()
    normalized = normalized.replace(":", " ")
    normalized = normalized.replace("-", " ")
    normalized = normalized.replace("_", " ")
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def title_match_keys(text: str) -> List[str]:
    base = normalize_title(text)
    compact = base.replace(" ", "")
    keys = [k for k in (base, compact) if k]
    return list(dict.fromkeys(keys))


def slugify(text: str) -> str:
    compact = normalize_title(text).replace(" ", "-")
    compact = re.sub(r"[^a-z0-9\-]+", "-", compact)
    compact = re.sub(r"\-+", "-", compact).strip("-")
    return compact or "paper"


def pdf_to_web_path(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    return "/" + quote(rel, safe="/")


def web_path_to_stem(web_path: str) -> str:
    unquoted = unquote(web_path or "").lstrip("/")
    if not unquoted:
        return ""
    return Path(unquoted).stem


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_space(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" *\n *", "\n", text)
    return text.strip()


def read_pdf_text(path: Path, max_pages: int) -> str:
    reader = PdfReader(str(path))
    parts: List[str] = []
    page_limit = min(max_pages, len(reader.pages))
    for idx in range(page_limit):
        try:
            page_text = reader.pages[idx].extract_text() or ""
        except Exception:  # noqa: BLE001
            page_text = ""
        if page_text:
            parts.append(page_text)
    return normalize_space("\n\n".join(parts))


def extract_abstract(text: str) -> str:
    if not text:
        return DEFAULT_ABSTRACT

    abstract_re = re.compile(
        r"(?:^|\n)\s*abstract\s*[:\-]?\s*(.{120,4000}?)(?:\n\s*(?:jel|keywords?|introduction|1[\.\s]))",
        flags=re.IGNORECASE | re.DOTALL,
    )
    match = abstract_re.search(text)
    if match:
        candidate = normalize_space(match.group(1))
        if candidate:
            return candidate[:ABSTRACT_MAX_CHARS]

    chunks = [c.strip() for c in re.split(r"\n{2,}", text) if c.strip()]
    for chunk in chunks:
        cleaned = normalize_space(chunk)
        if len(cleaned) >= 120:
            cleaned = re.sub(r"^abstract\s*[:\-]?\s*", "", cleaned, flags=re.IGNORECASE)
            return cleaned[:ABSTRACT_MAX_CHARS]

    return DEFAULT_ABSTRACT


def extract_excerpt(text: str) -> str:
    if not text:
        return ""
    cleaned = normalize_space(text)
    return cleaned[:EXCERPT_MAX_CHARS]


def infer_year_from_text(*values: str) -> Optional[int]:
    for value in values:
        if not value:
            continue
        found = re.findall(r"\b(19\d{2}|20\d{2})\b", value)
        if found:
            return int(found[0])
    return None


def infer_year_from_pdf_metadata(path: Path) -> Optional[int]:
    try:
        metadata = PdfReader(str(path)).metadata
    except Exception:  # noqa: BLE001
        return None
    if not metadata:
        return None

    for key in ("/CreationDate", "/ModDate"):
        raw = str(metadata.get(key, ""))
        match = re.search(r"(19\d{2}|20\d{2})", raw)
        if match:
            return int(match.group(1))
    return None


def ensure_list_authors(value: Any) -> List[str]:
    if isinstance(value, list):
        out = [str(v).strip() for v in value if str(v).strip()]
        return out or [AUTHOR_SELF]
    if isinstance(value, str) and value.strip():
        return [v.strip() for v in value.split(";") if v.strip()] or [value.strip()]
    return [AUTHOR_SELF]


def parse_citation(citation: str) -> Tuple[str, List[str], Optional[int]]:
    quoted_titles = re.findall(r'"([^"]+)"', citation or "")
    if quoted_titles:
        title = max((t.strip() for t in quoted_titles), key=len)
    else:
        title = citation.strip()
    title = title.rstrip(" ,.;")

    year_match = re.search(r"\((19\d{2}|20\d{2})\)", citation or "")
    year = int(year_match.group(1)) if year_match else None

    authors_raw = (citation or "").split("(")[0].strip().rstrip(":")
    pair_matches = re.findall(r"([A-Z][A-Za-z.\- ]+,\s*[A-Z][A-Za-z.\- ]+)", authors_raw)
    if pair_matches:
        authors = [re.sub(r"\s+", " ", p).strip().strip(",") for p in pair_matches]
    else:
        authors_raw = authors_raw.replace(", and ", ";").replace(" and ", ";")
        authors = [a.strip() for a in authors_raw.split(";") if a.strip()]

    return title, authors or [AUTHOR_SELF], year


def bootstrap_from_research() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    raw = load_yaml(RESEARCH_FILE, {})
    if not isinstance(raw, dict):
        return [], []

    working_entries: List[Dict[str, Any]] = []
    for item in raw.get("working_papers", []):
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        if not title:
            continue

        coauthors: List[str] = []
        for person in item.get("coauthors", []):
            if isinstance(person, dict) and person.get("name"):
                coauthors.append(str(person["name"]).strip())
            elif isinstance(person, str):
                coauthors.append(person.strip())

        authors = [AUTHOR_SELF] + [n for n in coauthors if n and n != AUTHOR_SELF]
        year = item.get("year")
        month = str(item.get("month", "")).strip()
        date = f"{month} {year}".strip() if month and year else (str(year) if year else "")

        working_entries.append(
            {
                "id": str(item.get("paper_id") or f"wp-{slugify(title)}"),
                "title": title,
                "authors": authors,
                "year": int(year) if isinstance(year, int) or str(year).isdigit() else "",
                "date": date,
                "type": "working_paper",
                "external_url": str(item.get("url", "")).strip(),
                "pdf_path": "",
                "abstract": str(item.get("abstract", "")).strip() or DEFAULT_ABSTRACT,
                "fulltext_hash": "",
                "fulltext_excerpt": "",
                "featured": bool(item.get("featured", False)),
            }
        )

    publication_entries: List[Dict[str, Any]] = []
    for item in raw.get("publications", []):
        if not isinstance(item, dict):
            continue
        citation = str(item.get("citation", "")).strip()
        if not citation:
            continue

        title, authors, year = parse_citation(citation)
        links = item.get("links") or []
        external_url = ""
        if isinstance(links, list):
            for link in links:
                if not isinstance(link, dict):
                    continue
                url = str(link.get("url", "")).strip()
                label = str(link.get("label", "")).lower()
                if url and ("journal" in label or not external_url):
                    external_url = url
                    if "journal" in label:
                        break

        publication_entries.append(
            {
                "id": f"pub-{slugify(title)}",
                "title": title,
                "authors": authors,
                "year": year or "",
                "date": str(year) if year else "",
                "type": "publication",
                "external_url": external_url,
                "pdf_path": "",
                "abstract": DEFAULT_ABSTRACT,
                "fulltext_hash": "",
                "fulltext_excerpt": "",
            }
        )

    return working_entries, publication_entries


def ensure_schema(entries: Iterable[Dict[str, Any]], paper_type: str) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for raw in entries:
        if not isinstance(raw, dict):
            continue
        title = str(raw.get("title", "")).strip()
        if not title:
            continue

        item: Dict[str, Any] = {
            "id": str(raw.get("id") or f"{'wp' if paper_type == 'working_paper' else 'pub'}-{slugify(title)}"),
            "title": title,
            "authors": ensure_list_authors(raw.get("authors")),
            "year": raw.get("year", ""),
            "date": str(raw.get("date", "")).strip(),
            "type": paper_type,
            "external_url": str(raw.get("external_url", "")).strip(),
            "pdf_path": str(raw.get("pdf_path", "")).strip(),
            "abstract": str(raw.get("abstract", "")).strip() or DEFAULT_ABSTRACT,
            "fulltext_hash": str(raw.get("fulltext_hash", "")).strip(),
            "fulltext_excerpt": str(raw.get("fulltext_excerpt", "")).strip(),
        }
        if "featured" in raw:
            item["featured"] = bool(raw.get("featured"))
        normalized.append(item)
    return normalized


def resolve_match(
    pdf_path: Path,
    paper_type: str,
    by_title: Dict[str, List[Dict[str, Any]]],
    by_pdf_stem: Dict[str, List[Dict[str, Any]]],
    by_id: Dict[str, List[Dict[str, Any]]],
    entries: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    for key in title_match_keys(pdf_path.stem):
        candidates.extend(by_pdf_stem.get(key, []))
        candidates.extend(by_title.get(key, []))
        candidates.extend(by_id.get(key, []))

    filtered: List[Dict[str, Any]] = []
    seen_ids = set()
    for item in candidates:
        if item.get("type") != paper_type:
            continue
        item_id = str(item.get("id"))
        if item_id in seen_ids:
            continue
        seen_ids.add(item_id)
        filtered.append(item)

    if len(filtered) == 1:
        return filtered[0]

    if not filtered:
        stem_tokens = set(normalize_title(pdf_path.stem).split())
        scored: List[Tuple[float, Dict[str, Any]]] = []
        for item in entries:
            if item.get("type") != paper_type:
                continue
            title_tokens = set(normalize_title(str(item.get("title", ""))).split())
            if not stem_tokens or not title_tokens:
                continue
            overlap = len(stem_tokens & title_tokens)
            score = (2.0 * overlap) / (len(stem_tokens) + len(title_tokens))
            scored.append((score, item))

        scored.sort(key=lambda row: row[0], reverse=True)
        if scored:
            best_score, best_item = scored[0]
            second_score = scored[1][0] if len(scored) > 1 else 0.0
            if best_score >= 0.72 and (best_score - second_score) >= 0.08:
                return best_item

    return None


def paper_sort_key(item: Dict[str, Any]) -> Tuple[int, int, str]:
    year_raw = item.get("year")
    year = int(year_raw) if str(year_raw).isdigit() else 0

    date_text = str(item.get("date", "")).lower()
    month = 0
    for token, value in MONTH_MAP.items():
        if re.search(rf"\b{token}\b", date_text):
            month = value
            break
    title = str(item.get("title", "")).lower()
    return (year, month, title)


def update_entries_for_type(
    paper_type: str,
    entries: List[Dict[str, Any]],
    refresh: bool,
) -> Dict[str, Any]:
    folder = PAPER_DIRS[paper_type]
    pdf_files = sorted(folder.glob("*.pdf"), key=lambda p: p.name.lower())

    by_title: Dict[str, List[Dict[str, Any]]] = {}
    by_pdf_stem: Dict[str, List[Dict[str, Any]]] = {}
    by_id: Dict[str, List[Dict[str, Any]]] = {}
    for item in entries:
        for key in title_match_keys(str(item.get("title", ""))):
            by_title.setdefault(key, []).append(item)
        for key in title_match_keys(web_path_to_stem(str(item.get("pdf_path", "")))):
            by_pdf_stem.setdefault(key, []).append(item)
        for key in title_match_keys(str(item.get("id", ""))):
            by_id.setdefault(key, []).append(item)

    updated = 0
    skipped = 0
    unmatched: List[Dict[str, Any]] = []

    for pdf_path in pdf_files:
        entry = resolve_match(pdf_path, paper_type, by_title, by_pdf_stem, by_id, entries)
        pdf_web_path = pdf_to_web_path(pdf_path)
        file_hash = sha256_file(pdf_path)

        inferred_year = infer_year_from_text(pdf_path.stem)
        if inferred_year is None:
            inferred_year = infer_year_from_pdf_metadata(pdf_path)

        if entry is None:
            title_guess = pdf_path.stem.replace("_", " ").replace(" - ", ": ").strip()
            title_guess = re.sub(r"\s+", " ", title_guess)
            draft_id = f"{'wp' if paper_type == 'working_paper' else 'pub'}-{slugify(title_guess)}"
            unmatched.append(
                {
                    "id": draft_id,
                    "title": title_guess,
                    "authors": [AUTHOR_SELF],
                    "year": inferred_year or "",
                    "date": str(inferred_year) if inferred_year else "",
                    "type": paper_type,
                    "external_url": "",
                    "pdf_path": pdf_web_path,
                    "abstract": "",
                    "fulltext_hash": file_hash,
                }
            )
            continue

        changed = False
        if entry.get("pdf_path") != pdf_web_path:
            entry["pdf_path"] = pdf_web_path
            changed = True

        if (not entry.get("year")) and inferred_year:
            entry["year"] = inferred_year
            if not str(entry.get("date", "")).strip():
                entry["date"] = str(inferred_year)
            changed = True

        old_hash = str(entry.get("fulltext_hash", "")).strip()
        abstract_now = str(entry.get("abstract", "")).strip()
        excerpt_now = str(entry.get("fulltext_excerpt", "")).strip()
        needs_extract = refresh or not old_hash or old_hash != file_hash or not abstract_now or not excerpt_now
        if needs_extract:
            text_for_abstract = read_pdf_text(pdf_path, max_pages=ABSTRACT_SCAN_PAGES)
            text_for_excerpt = read_pdf_text(pdf_path, max_pages=EXCERPT_SCAN_PAGES)
            entry["abstract"] = extract_abstract(text_for_abstract)
            entry["fulltext_excerpt"] = extract_excerpt(text_for_excerpt)
            entry["fulltext_hash"] = file_hash
            changed = True
        else:
            skipped += 1

        if changed:
            updated += 1

    entries.sort(key=paper_sort_key, reverse=True)

    return {
        "entries": entries,
        "updated": updated,
        "skipped": skipped,
        "unmatched": unmatched,
        "pdf_count": len(pdf_files),
    }


def build_search_index(all_entries: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    index: List[Dict[str, Any]] = []
    for item in all_entries:
        title = str(item.get("title", "")).strip()
        if not title:
            continue
        authors = ensure_list_authors(item.get("authors"))
        year = str(item.get("year", "")).strip()
        date = str(item.get("date", "")).strip()
        abstract = str(item.get("abstract", "")).strip()
        excerpt = str(item.get("fulltext_excerpt", "")).strip()

        searchable_text = normalize_space(" ".join([title, " ".join(authors), year, date, abstract, excerpt]))
        index.append(
            {
                "id": str(item.get("id", "")).strip(),
                "type": str(item.get("type", "")).strip(),
                "title": title,
                "authors": authors,
                "year": year,
                "date": date,
                "external_url": str(item.get("external_url", "")).strip(),
                "pdf_path": str(item.get("pdf_path", "")).strip(),
                "abstract": abstract,
                "fulltext_excerpt": excerpt,
                "searchable_text": searchable_text,
            }
        )
    return index


def write_search_index(index: List[Dict[str, Any]]) -> None:
    SEARCH_INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with SEARCH_INDEX_FILE.open("w", encoding="utf-8") as handle:
        json.dump(index, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def load_or_bootstrap_entries() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], bool]:
    created = False
    working = load_yaml(WORKING_FILE, None)
    publications = load_yaml(PUBLICATIONS_FILE, None)

    if isinstance(working, list) and isinstance(publications, list):
        return (
            ensure_schema(working, "working_paper"),
            ensure_schema(publications, "publication"),
            created,
        )

    boot_working, boot_publications = bootstrap_from_research()
    created = True
    return (
        ensure_schema(boot_working, "working_paper"),
        ensure_schema(boot_publications, "publication"),
        created,
    )


def main() -> int:
    args = parse_args()

    working_entries, publication_entries, bootstrapped = load_or_bootstrap_entries()

    working_result = update_entries_for_type("working_paper", working_entries, refresh=args.refresh)
    publication_result = update_entries_for_type("publication", publication_entries, refresh=args.refresh)

    dump_yaml(WORKING_FILE, working_result["entries"])
    dump_yaml(PUBLICATIONS_FILE, publication_result["entries"])

    unmatched = working_result["unmatched"] + publication_result["unmatched"]
    dump_yaml(AUTODRAFT_FILE, unmatched)

    search_index = build_search_index(working_result["entries"] + publication_result["entries"])
    write_search_index(search_index)

    print("Paper index update summary")
    print(
        f"- Working papers: {working_result['pdf_count']} PDFs scanned, "
        f"{working_result['updated']} entries updated, {working_result['skipped']} unchanged."
    )
    print(
        f"- Publications: {publication_result['pdf_count']} PDFs scanned, "
        f"{publication_result['updated']} entries updated, {publication_result['skipped']} unchanged."
    )
    print(f"- Search index entries: {len(search_index)} -> {SEARCH_INDEX_FILE.relative_to(ROOT)}")
    print(f"- Autodraft entries: {len(unmatched)} -> {AUTODRAFT_FILE.relative_to(ROOT)}")
    if bootstrapped:
        print("- Metadata files bootstrapped from _data/research.yml")
    if unmatched:
        print("Unmatched PDFs (review and move entries into data files):")
        for item in unmatched:
            print(f"  * {item['type']}: {item['pdf_path']} -> {item['title']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
