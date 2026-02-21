#!/usr/bin/env python3
"""Fetch SSRN abstracts for working papers and persist them in _data/research.yml."""

from __future__ import annotations

import argparse
import random
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import yaml
from bs4 import BeautifulSoup

PLACEHOLDER = "Abstract unavailable. Please see SSRN page."
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-file",
        default="_data/research.yml",
        help="Path to the research data YAML file (default: _data/research.yml)",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-fetch abstracts even when an abstract already exists",
    )
    parser.add_argument(
        "--min-delay",
        type=float,
        default=1.0,
        help="Minimum delay in seconds between SSRN requests (default: 1.0)",
    )
    parser.add_argument(
        "--max-delay",
        type=float,
        default=2.0,
        help="Maximum delay in seconds between SSRN requests (default: 2.0)",
    )
    return parser.parse_args()


def normalize_whitespace(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n\s*\n", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return text.strip()


def clean_abstract(text: str) -> str:
    cleaned = normalize_whitespace(text)
    cleaned = re.sub(r"^abstract\s*[:\-]?\s*", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip() or PLACEHOLDER


def extract_paper_id(item: Dict[str, Any]) -> str:
    url = str(item.get("url", ""))
    match = re.search(r"abstract_id=(\d+)", url)
    if match:
        return f"ssrn-{match.group(1)}"

    title = str(item.get("title", "paper")).lower()
    slug = re.sub(r"[^a-z0-9]+", "-", title).strip("-")
    return f"wp-{slug or 'paper'}"


def first_text(soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
    for selector in selectors:
        node = soup.select_one(selector)
        if node:
            text = node.get_text("\n", strip=True)
            if text:
                return text
    return None


def extract_from_meta(soup: BeautifulSoup) -> Optional[str]:
    for name in ("citation_abstract", "description", "dc.description"):
        node = soup.select_one(f'meta[name="{name}"]')
        if node and node.get("content"):
            value = str(node["content"]).strip()
            if value and "SSRN" not in value:
                return value
    return None


def fetch_abstract(url: str, session: requests.Session, timeout: int = 25) -> str:
    response = session.get(url, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    selectors = [
        "#abstract-text",
        ".abstract-text",
        "section.abstract p",
        "div.abstract p",
        "[data-testid='abstract']",
        "div#viewAbstract p",
    ]

    text = first_text(soup, selectors)

    if not text:
        header = soup.find(string=re.compile(r"^\s*Abstract\s*$", re.IGNORECASE))
        if header and getattr(header, "parent", None):
            container = header.parent.find_next("p")
            if container:
                text = container.get_text("\n", strip=True)

    if not text:
        text = extract_from_meta(soup)

    if not text:
        return PLACEHOLDER

    return clean_abstract(text)


def load_data(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Unexpected YAML top-level type in {path}")
    return data


def dump_data(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(
            data,
            handle,
            sort_keys=False,
            allow_unicode=False,
            default_flow_style=False,
            width=1000,
        )


def should_skip(item: Dict[str, Any], refresh: bool) -> bool:
    if refresh:
        return False
    abstract = str(item.get("abstract", "")).strip()
    return bool(abstract and abstract != PLACEHOLDER)


def main() -> int:
    args = parse_args()
    data_path = Path(args.data_file)

    if args.min_delay <= 0 or args.max_delay <= 0 or args.min_delay > args.max_delay:
        print("Invalid delay bounds.", file=sys.stderr)
        return 2

    data = load_data(data_path)
    working_papers = data.get("working_papers")
    if not isinstance(working_papers, list):
        print("No working_papers list found.", file=sys.stderr)
        return 2

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"})

    updated = 0
    fetched = 0

    for item in working_papers:
        if not isinstance(item, dict):
            continue

        item.setdefault("paper_id", extract_paper_id(item))

        url = str(item.get("url", "")).strip()
        if "papers.ssrn.com" not in url.lower():
            item.setdefault("abstract", PLACEHOLDER)
            continue

        if should_skip(item, args.refresh):
            continue

        try:
            abstract = fetch_abstract(url, session)
            item["abstract"] = abstract
            fetched += 1
            updated += 1
            print(f"Fetched abstract: {item.get('title', 'Unknown')} ({url})")
        except Exception as exc:  # noqa: BLE001
            item["abstract"] = PLACEHOLDER
            updated += 1
            print(f"Failed abstract fetch: {item.get('title', 'Unknown')} ({exc})", file=sys.stderr)

        time.sleep(random.uniform(args.min_delay, args.max_delay))

    if updated:
        dump_data(data_path, data)
        print(f"Updated {updated} working paper entries ({fetched} fetched from SSRN).")
    else:
        print("No changes needed. All SSRN abstracts already cached.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
