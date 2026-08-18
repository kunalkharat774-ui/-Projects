#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================
  Automated Dark Web Leak & Brand Mention Monitor
============================================================
यह टूल Tor SOCKS5 proxy के ज़रिए .onion साइट्स से जुड़ता है,
उनके HTML को BeautifulSoup से parse करता है, और टारगेट कीवर्ड
की मौजूदगी पर टर्मिनल पर बड़ा [!] ALERT print करता है।

उदाहरण:
    python3 darkweb_monitor.py
    python3 darkweb_monitor.py -k "company@example.com" -s "http://xyz.onion"
    python3 darkweb_monitor.py -k "password[0-9]{4}" --regex
"""

import argparse
import random
import re
import sys
import time
from collections import deque
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# onion sites अक्सर self-signed SSL certs use करती हैं,
# इसलिए InsecureRequestWarning को suppress कर रहे हैं।
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except Exception:
    pass


# ================= CONFIGURATION =================
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 9150   # Tor Browser bundle का default port (system tor = 9050)
SOCKS5_PROXY = f"socks5h://{PROXY_HOST}:{PROXY_PORT}"
# ध्यान दें: 'socks5h' में 'h' का मतलब है DNS resolution भी Tor से होकर
# जाएगा — .onion addresses के लिए यह बहुत ज़रूरी है (socks5 के साथ नहीं चलेगा)।

REQUEST_TIMEOUT = 30        # प्रत्येक request का timeout (seconds)
CRAWL_DELAY = 1.0           # requests के बीच polite delay
MAX_PAGES = 50              # डिफ़ॉल्ट: कुल कितने pages scan करने हैं
MAX_DEPTH = 2               # डिफ़ॉल्ट: links कितनी depth तक follow करें

# Random User-Agent rotation — कुछ sites बिना UA के request block कर देती हैं
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]

# डिफ़ॉल्ट seed (.onion) URLs — चेतावनी: onion addresses बार-बार बदलती
# रहती हैं, इसलिए इन्हें अपने intel/research के हिसाब से update करें,
# या फिर --seeds flag से अपनी खुद की URLs दें।
DEFAULT_SEEDS = [
    "http://juhanurmihxlp77nkq76byazcldy2hlcyfu6jdzw7c4t2h5j3k4fqd.onion",  # Ahmia (example)
    "http://darkfailenbsdla5w.onion",                                       # Dark.fail (example)
]


# ================= CUSTOM EXCEPTION =================
class TorConnectionError(Exception):
    """Tor proxy उपलब्ध न होने पर raise होता है"""
    pass


# ================= HELPER FUNCTIONS =================
def log(msg, level="INFO"):
    """Timestamp के साथ log message print करता है"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level:>5}] {msg}")


def build_session(proxy):
    """Requests session बनाता है — Tor SOCKS5 proxy + random User-Agent के साथ"""
    session = requests.Session()
    session.proxies = {"http": proxy, "https": proxy}
    session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
    session.verify = False  # onion sites के self-signed SSL certs के लिए
    return session


def check_tor_connection(session):
    """Tor proxy चालू है या नहीं — check.torproject.org से पुष्टि करता है"""
    try:
        r = session.get("https://check.torproject.org/", timeout=15)
        if "Congratulations" in r.text:
            log("Tor कनेक्शन सफल — ट्रैफ़िक Tor network से होकर जा रहा है।", "OK")
            return True
        log("चेतावनी: Tor का उपयोग नहीं हो रहा (proxy काम नहीं कर रहा)।", "WARN")
        return False
    except requests.exceptions.ProxyError:
        log("Tor proxy unreachable — क्या Tor चल रहा है? (127.0.0.1:9150)", "ERROR")
    except requests.exceptions.ConnectTimeout:
        log("Tor से कनेक्ट करने में timeout।", "ERROR")
    except Exception as e:
        log(f"Tor check में अज्ञात त्रुटि: {e}", "ERROR")
    return False


def fetch_page(session, url, retries=2):
    """
    URL से HTML fetch करता है।
    Exception handling: ProxyError, timeout, connection error आदि को
    सही message के साथ handle करता है, और retry करता है।
    """
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()          # 4xx/5xx पर exception उठाएगा
            return resp
        except requests.exceptions.ProxyError:
            # यह fatal है — Tor बंद है तो आगे कुछ नहीं चलेगा
            log(f"Proxy error (Tor बंद है?) — {url}", "ERROR")
            raise TorConnectionError("Tor proxy unreachable")
        except requests.exceptions.ConnectTimeout:
            log(f"Connect timeout (attempt {attempt}/{retries}) — {url}", "WARN")
        except requests.exceptions.ReadTimeout:
            log(f"Read timeout (attempt {attempt}/{retries}) — {url}", "WARN")
        except requests.exceptions.ConnectionError as e:
            log(f"Connection error (attempt {attempt}/{retries}) — {url}: {e}", "WARN")
        except requests.exceptions.TooManyRedirects:
            log(f"Too many redirects — {url}", "WARN")
            break                          # retry करने का फायदा नहीं
        except requests.exceptions.SSLError as e:
            log(f"SSL error — {url}: {e}", "WARN")
        except requests.exceptions.InvalidSchema:
            log(f"Invalid URL scheme (http/https चाहिए) — {url}", "WARN")
            break
        except Exception as e:
            log(f"Unexpected error on {url}: {e}", "WARN")
        time.sleep(CRAWL_DELAY * attempt)  # retry से पहले छोटा wait
    return None


def extract_text(html):
    """BeautifulSoup से page का सिर्फ text निकालता है (scripts/styles हटाकर)"""
    soup = BeautifulSoup(html, "html.parser")
    # इन tags का content हमें नहीं चाहिए — false positive से बचने के लिए हटाते हैं
    for tag in soup(["script", "style", "noscript", "svg", "form", "iframe"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


def extract_links(base_url, html):
    """Page में मौजूद सभी .onion links निकालता है (आगे crawl करने के लिए)"""
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        # protocol-relative links (//host/path) को भी handle करें
        if href.startswith("//"):
            href = "http:" + href
        if href.startswith(("http://", "https://")):
            absolute = urljoin(base_url, href)   # relative → absolute URL
            host = urlparse(absolute).hostname or ""
            if host.endswith(".onion"):          # सिर्फ .onion sites follow करें
                links.append(absolute)
    return links


def keyword_hit(text, keyword, use_regex=False):
    """कीवर्ड page text में मिला या नहीं (case-insensitive)"""
    if use_regex:
        try:
            return re.search(keyword, text, re.IGNORECASE) is not None
        except re.error as e:
            log(f"Invalid regex '{keyword}': {e}", "ERROR")
            return False
    return keyword.lower() in text.lower()


def get_snippet(text, keyword, width=80):
    """Match के आस-पास का context snippet निकालता है (alert में दिखाने के लिए)"""
    idx = text.lower().find(keyword.lower())
    if idx == -1:
        return ""
    start = max(0, idx - width)
    end = min(len(text), idx + len(keyword) + width)
    return "..." + text[start:end].strip() + "..."


def print_alert(url, keyword, snippet):
    """बड़ा [!] ALERT banner print करता है — keyword मिलने पर"""
    banner = f"""
    ====================================================================
       [!]  [!]  [!]  LEAK / BRAND MENTION DETECTED  [!]  [!]  [!]
    ====================================================================
       Keyword     : {keyword}
       Target URL  : {url}
       Detected at : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
       Snippet     : {snippet}
    ====================================================================
    """
    print(banner)


def crawl(session, seeds, keyword, max_pages, max_depth, use_regex):
    """
    BFS-based crawler — seed URLs से शुरू करके हर page पर keyword खोजता है,
    और depth limit के अंदर मिले .onion links को follow करता है।
    """
    queue = deque((s, 0) for s in seeds)   # (url, depth) pairs
    visited = set()                         # duplicate visits से बचने के लिए
    matches = []
    pages_scanned = 0

    while queue and pages_scanned < max_pages:
        url, depth = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        log(f"Fetching (depth {depth}): {url}")
        resp = fetch_page(session, url)
        if resp is None:
            continue                        # page fetch नहीं हुआ — skip

        pages_scanned += 1
        text = extract_text(resp.content)   # HTML → सिर्फ text

        # ----- कीवर्ड मिला? -----
        if keyword_hit(text, keyword, use_regex):
            snippet = get_snippet(text, keyword)
            print_alert(url, keyword, snippet)      # बड़ा [!] alert
            matches.append((url, snippet))
            log(f"MATCH FOUND on {url}", "HIT")

        # ----- depth limit के अंदर आगे के links follow करो -----
        if depth < max_depth:
            for link in extract_links(url, resp.text):
                if link not in visited:
                    queue.append((link, depth + 1))

        time.sleep(CRAWL_DELAY)             # polite crawling

    return matches, pages_scanned


def main():
    parser = argparse.ArgumentParser(
        description="Automated Dark Web Leak & Brand Mention Monitor (Tor + .onion)"
    )
    parser.add_argument("-k", "--keyword", help="टारगेट कीवर्ड (कंपनी नाम / email / regex)")
    parser.add_argument("-s", "--seeds", nargs="+", help="शुरुआती .onion URLs (एक या अधिक)")
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES,
                        help=f"कुल कितने pages scan करने हैं (default: {MAX_PAGES})")
    parser.add_argument("--max-depth", type=int, default=MAX_DEPTH,
                        help=f"links कितनी depth तक follow करें (default: {MAX_DEPTH})")
    parser.add_argument("--delay", type=float, default=CRAWL_DELAY,
                        help="requests के बीच delay seconds में (default: 1.0)")
    parser.add_argument("--proxy", default=SOCKS5_PROXY,
                        help=f"SOCKS5 proxy (default: {SOCKS5_PROXY})")
    parser.add_argument("--regex", action="store_true",
                        help="कीवर्ड को regex की तरह treat करें")
    parser.add_argument("-o", "--output", help="मिले हुए matches को file में save करें")
    args = parser.parse_args()

    # ---------- शुरुआती banner ----------
    print("""
    ====================================================================
      Automated Dark Web Leak & Brand Mention Monitor  (Tor + .onion)
    ====================================================================
    """)

    # ---------- Keyword: flag से या interactive prompt से ----------
    keyword = args.keyword
    if not keyword:
        keyword = input("[?] टारगेट कीवर्ड दर्ज करें (जैसे company@mail.com या ब्रांड नाम): ").strip()
        if not keyword:
            log("कोई keyword नहीं दिया गया। Exiting.", "ERROR")
            sys.exit(1)

    # ---------- Seeds: flag से या interactive prompt से ----------
    seeds = args.seeds or DEFAULT_SEEDS
    if not args.seeds:
        log(f"कोई --seeds नहीं दिया गया, default seeds उपयोग हो रहे हैं: {seeds}", "INFO")
        choice = input("[?] अपनी खुद की .onion URLs दर्ज करें? (comma से अलग करें, या Enter दबाएँ): ").strip()
        if choice:
            seeds = [u.strip() for u in choice.split(",") if u.strip().startswith("http")]
            if not seeds:
                log("कोई valid URL नहीं मिला, default seeds use होंगे।", "WARN")
                seeds = DEFAULT_SEEDS

    log(f"Proxy      : {args.proxy}")
    log(f"Keyword    : {keyword}")
    log(f"Max pages  : {args.max_pages}  |  Max depth: {args.max_depth}  |  Regex: {args.regex}")

    # ---------- Tor connectivity check ----------
    session = build_session(args.proxy)
    if not check_tor_connection(session):
        log("Tor चालू नहीं है — पहले Tor Browser या tor daemon start करें।", "ERROR")
        sys.exit(1)

    # ---------- Crawl शुरू ----------
    start = time.time()
    try:
        matches, scanned = crawl(session, seeds, keyword,
                                 args.max_pages, args.max_depth, args.regex)
    except TorConnectionError:
        log("Crawl रोका गया — Tor proxy काम नहीं कर रहा।", "ERROR")
        sys.exit(1)
    except KeyboardInterrupt:
        log("User द्वारा रोका गया (Ctrl+C)।", "WARN")
        sys.exit(130)

    elapsed = time.time() - start

    # ---------- Summary ----------
    print("\n" + "=" * 70)
    log(f"Scan complete — {scanned} pages scanned, "
        f"{len(matches)} match(es) found in {elapsed:.1f}s", "DONE")
    if matches:
        for url, _ in matches:
            print(f"  [!] {url}")
        if args.output:
            with open(args.output, "a", encoding="utf-8") as f:
                for url, snip in matches:
                    f.write(f"{datetime.now().isoformat()} | {keyword} | {url} | {snip}\n")
            log(f"Matches saved to {args.output}", "OK")
    else:
        log("कोई match नहीं मिला — नए seeds या ज़्यादा max-pages के साथ try करें।", "INFO")


if __name__ == "__main__":
    main()
