from __future__ import annotations
import json, re, subprocess, sys, threading, importlib.util
from typing import Dict, List, Set
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

def _ensure(pkg: str) -> None:
    if importlib.util.find_spec(pkg) is None:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
    globals()[pkg] = __import__(pkg)

for _p in ("requests", "bs4"):
    _ensure(_p)

import requests
from bs4 import BeautifulSoup

_BANNER_ART = r"""
██╗███╗   ██╗███████╗ ██████╗ ██╗  ██╗ █████╗ ██████╗ ██╗   ██╗███████╗███████╗████████╗
██║████╗  ██║██╔════╝██╔═══██╗██║  ██║██╔══██╗██╔══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝
██║██╔██╗ ██║█████╗  ██║   ██║███████║███████║██████╔╝██║   ██║█████╗  ███████╗   ██║   
██║██║╚██╗██║██╔══╝  ██║   ██║██╔══██║██╔══██║██╔══██╗╚██╗ ██╔╝██╔══╝  ╚════██║   ██║   
██║██║ ╚████║██║     ╚██████╔╝██║  ██║██║  ██║██║  ██║ ╚████╔╝ ███████╗███████║   ██║   
╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚══════╝   ╚═╝   
"""
_SUBTITLE = "W E B S I T E   C O N T A C T   I N F O   S C R A P E R"
_VERSION  = "Version 1.00"

def _is_repeating_chars(s: str) -> bool:
    cleaned = re.sub(r"[^0-9a-z]", "", s.lower())
    return bool(cleaned) and len(set(cleaned)) == 1

EMAIL_RE  = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE  = re.compile(r"(?:\+?\d{1,3}[\s\-.])?(?:\(?\d{3}\)?[\s\-.])?\d{3}[\s\-.]\d{4}")
FAX_HINTS = re.compile(r"\b(?:fax|facsimile)\b", re.I)
SOCIAL_RE = re.compile(r"https?://(?:www\.)?(facebook|twitter|linkedin|instagram|youtube|t\.me|telegram|pinterest|threads|mastodon)\.[^\s\"'<>]+", re.I)

def scrape_contact(url: str) -> Dict[str, str]:
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    html = resp.text
    seen_emails: Set[str] = set()
    seen_digits: Set[str] = set()
    seen_social: Set[str] = set()

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
        raw = m.group(0).strip()
        digits = re.sub(r"\D", "", raw)
        if len(digits) < 10 or _is_repeating_chars(digits) or digits in seen_digits:
            continue
        seen_digits.add(digits)
        ctx = html[max(m.start() - 60, 0):m.start()].lower()
        (faxes if FAX_HINTS.search(ctx) else phones).append(raw)

    socials: List[str] = []
    for m in SOCIAL_RE.finditer(html):
        u = m.group(0)
        if _is_repeating_chars(u) or u in seen_social:
            continue
        seen_social.add(u)
        socials.append(u)

    fmt = lambda v: ", ".join(v) if v else "NOT PRESENT"
    return {
        "Phone numbers":         fmt(phones),
        "Fax number":            fmt(faxes),
        "Email addresses":       fmt(emails),
        "Social media profiles": fmt(socials),
    }

class ScraperGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Website Contact Info Scraper")
        self.configure(bg="white")
        self._build_widgets()

    def _build_widgets(self):
        ttk.Label(self, text=_BANNER_ART, font=("Courier", 8), foreground="red", background="white", justify="left").pack(anchor="w", padx=10, pady=(10,0))
        ttk.Label(self, text=_SUBTITLE, font=("Courier", 10, "bold"), foreground="blue", background="white").pack(anchor="w", padx=10)
        ttk.Label(self, text=_VERSION, font=("Courier", 9), foreground="red", background="white").pack(anchor="w", padx=10, pady=(0,10))

        frm = ttk.Frame(self)
        frm.pack(fill="x", padx=10, pady=5)
        ttk.Label(frm, text="URL:", width=5).pack(side="left")
        self.url_entry = ttk.Entry(frm)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0,5))
        ttk.Button(frm, text="Scrape", command=self._start_scrape).pack(side="left")

        out_frame = ttk.Frame(self)
        out_frame.pack(fill="both", expand=True, padx=10)
        self.output = scrolledtext.ScrolledText(out_frame, height=15, wrap="word", font=("Courier", 10))
        self.output.pack(side="left", fill="both", expand=True)
        ttk.Button(out_frame, text="Copy", command=self._copy_to_clip).pack(side="right", padx=(5,0), fill="y")

        ttk.Button(self, text="Exit", command=self.destroy).pack(pady=5)

    def _start_scrape(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return
        if not url.lower().startswith(("http://", "https://")):
            url = "http://" + url
        self.output.delete("1.0", "end")
        threading.Thread(target=self._scrape_thread, args=(url,), daemon=True).start()

    def _scrape_thread(self, url: str):
        try:
            data = scrape_contact(url)
        except Exception as exc:
            self._append_output(f"Error: {exc}")
            return
        self._append_output(json.dumps(data, indent=2, ensure_ascii=False))

    def _append_output(self, text: str):
        self.output.insert("end", text + "\n")
        self.output.see("end")

    def _copy_to_clip(self):
        self.clipboard_clear()
        self.clipboard_append(self.output.get("1.0", "end-1c"))
        self.update()

if __name__ == "__main__":
    ScraperGUI().mainloop()