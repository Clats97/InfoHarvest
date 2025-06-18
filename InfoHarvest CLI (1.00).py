from __future__ import annotations
import json, re, subprocess, sys
from typing import Dict, List, Set

def _ensure(pkg: str) -> None:
    try:
        __import__(pkg)
    except ImportError:
        print(f"[+] Installing '{pkg}' …", file=sys.stderr, flush=True)
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
    finally:
        globals()[pkg] = __import__(pkg)

for _p in ("requests", "bs4"):
    _ensure(_p)

import requests
from bs4 import BeautifulSoup

_RED   = "\033[31m"
_BLUE  = "\033[34m"
_RESET = "\033[0m"

_BANNER_ART = r"""
██╗███╗   ██╗███████╗ ██████╗ ██╗  ██╗ █████╗ ██████╗ ██╗   ██╗███████╗███████╗████████╗
██║████╗  ██║██╔════╝██╔═══██╗██║  ██║██╔══██╗██╔══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝
██║██╔██╗ ██║█████╗  ██║   ██║███████║███████║██████╔╝██║   ██║█████╗  ███████╗   ██║   
██║██║╚██╗██║██╔══╝  ██║   ██║██╔══██║██╔══██║██╔══██╗╚██╗ ██╔╝██╔══╝  ╚════██║   ██║   
██║██║ ╚████║██║     ╚██████╔╝██║  ██║██║  ██║██║  ██║ ╚████╔╝ ███████╗███████║   ██║   
╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚══════╝   ╚═╝   
"""

_SUBTITLE = "W E B S I T E   C O N T A C T   I N F O   S C R A P E R"
_VERSION  = "Version 1.01"

def _print_banner() -> None:
    print(f"{_RED}{_BANNER_ART}{_RESET}")
    print(f"{_BLUE}{_SUBTITLE}{_RESET}  {_RED}{_VERSION}{_RESET}\n")

def _is_repeating_chars(s: str) -> bool:
    cleaned = re.sub(r"[^0-9a-z]", "", s.lower())
    return bool(cleaned) and len(set(cleaned)) == 1

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(
    r"""
    (?:\+?\d{1,3}[\s\-.])?
    (?:\(?\d{3}\)?[\s\-.])?
    \d{3}[\s\-.]\d{4}
    """,
    re.VERBOSE,
)
FAX_HINTS = re.compile(r"\b(?:fax|facsimile)\b", re.I)
SOCIAL_RE = re.compile(
    r"https?://(?:www\.)?"
    r"(facebook|twitter|linkedin|instagram|youtube|t\.me|telegram|pinterest|threads|mastodon)"
    r"\.[^\s\"'<>]+",
    re.I,
)

def scrape_contact(url: str) -> Dict[str, str]:
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    html = resp.text

    seen_emails:  Set[str] = set()
    seen_digits:  Set[str] = set()
    seen_social:  Set[str] = set()

    emails: List[str] = []
    for raw in EMAIL_RE.findall(html):
        canon = raw.lower()
        if _is_repeating_chars(canon) or canon in seen_emails:
            continue
        seen_emails.add(canon)
        emails.append(raw)

    phones: List[str] = []
    faxes:  List[str] = []

    for m in PHONE_RE.finditer(html):
        raw_num = m.group(0).strip()
        digits  = re.sub(r"\D", "", raw_num)

        if len(digits) < 10 or _is_repeating_chars(digits) or digits in seen_digits:
            continue
        seen_digits.add(digits)

        context = html[max(m.start() - 60, 0) : m.start()].lower()
        if FAX_HINTS.search(context):
            faxes.append(raw_num)
        else:
            phones.append(raw_num)

    socials: List[str] = []
    for m in SOCIAL_RE.finditer(html):
        url_found = m.group(0)
        if _is_repeating_chars(url_found) or url_found in seen_social:
            continue
        seen_social.add(url_found)
        socials.append(url_found)

    def _fmt(vals: List[str]) -> str:
        return ", ".join(vals) if vals else "NOT PRESENT"

    return {
        "Phone numbers":         _fmt(phones),
        "Fax number":            _fmt(faxes),
        "Email addresses":       _fmt(emails),
        "Social media profiles": _fmt(socials),
    }

def main() -> None:
    while True:
        _print_banner()
        url = input("Enter the full URL to scrape (or press Enter to exit) ➜ ").strip()
        if url == "":
            print("\nGoodbye!\n")
            break
        if not url.lower().startswith(("http://", "https://")):
            url = "http://" + url
        try:
            data = scrape_contact(url)
            print("\n" + json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as exc:
            print(f"\n[!] Error: {exc}", file=sys.stderr)
            continue
        input("\n── Press Enter to continue ──")
    input("\n── Press Enter to close the program ──")

if __name__ == "__main__":
    main()