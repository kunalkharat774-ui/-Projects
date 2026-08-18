#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================
  Automated Dark Web Leak & Brand Mention Monitor
============================================================
This tool connects to .onion sites through a Tor SOCKS5 proxy,
parses their HTML with BeautifulSoup, and prints a big [!] ALERT
on the terminal whenever the target keyword (e.g. your email)
is found.

It can ALSO auto-discover .onion URLs by searching Ahmia
(a .onion search engine) for your keyword, so you do not need
to know any onion addresses beforehand.

Examples:
    python3 darkweb_monitor.py -k "you@example.com"
    python3 darkweb_monitor.py -k "you@example.com" -s "http://xyz.onion"
    python3 darkweb_monitor.py -k "password[0-9]{4}" --regex
"""

import argparse
import random
import re
import sys
import time
from collections import deque
from datetime import datetime
from urllib.parse import urljoin, urlparse, quote

import requests
from bs4 import BeautifulSoup

# Onion sites often use self-signed SSL certificates,
# so we suppress the InsecureRequestWarning.
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except Exception:
    pass


# ================= CONFIGURATION =================
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 9150   # Default port for Tor Browser bundle (system tor = 9050)
SOCKS5_PROXY = f"socks5h://{PROXY_HOST}:{PROXY_PORT}"
# NOTE: The 'h' in 'socks5h' means DNS resolution also happens through Tor —
# this is critical for .onion addresses (plain 'socks5' will not work).

REQUEST_TIMEOUT = 30        # Timeout per request (seconds)
CRAWL_DELAY = 1.0           # Polite delay between requests
MAX_PAGES = 50              # Default: total pages to scan
MAX_DEPTH = 2               # Default: how deep to follow links
AHMIA_MAX_RESULTS = 10      # Max .onion URLs to take from Ahmia search

# Random User-Agent rotation — some sites block requests without a UA
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]

# Default seed (.onion) URLs — used only if no seeds are provided and
# Ahmia discovery is declined. Onion addresses change frequently.
DEFAULT_SEEDS = [
    "http://juhanurmihxlp77nkq76byazcldy2hlcyfu6jdzw7c4t2h5j3k4fqd.onion",  # Ahmia (example)
    "http://darkfailenbsdla5w.onion",                                       # Dark.fail (example)
]


# ================= CUSTOM EXCEPTION =================
class TorConnectionError(Exception):
    """Raised when the Tor proxy is not available"""
    pass


# ================= HELPER FUNCTIONS =================
def log(msg, level="INFO"):
    """Prints a log message with a timestamp"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level:>5}] {msg}")


def build_session(proxy):
    """Builds a requests session with the Tor SOCKS5 proxy + random User-Agent"""
    session = requests.Session()
    session.proxies = {"http": proxy, "https": proxy}
    session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
    session.verify = False  # for onion sites' self-signed SSL certs
    return session


def check_tor_connection(session):
    """Confirms Tor is working by hitting check.torproject.org"""
    try:
        r = session.get("https://check.torproject.org/", timeout=15)
        if "Congratulations" in r.text:
            log("Tor connection successful — traffic is going through the Tor network.", "OK")
            return True
        log("Warning: NOT using Tor (proxy is not routing traffic).", "WARN")
        return False
    except requests.exceptions.ProxyError:
        log("Tor proxy unreachable — is Tor running? (127.0.0.1:9150)", "ERROR")
    except requests.exceptions.ConnectTimeout:
        log("Timeout while connecting to Tor.", "ERROR")
    except Exception as e:
        log(f"Unknown error during Tor check: {e}", "ERROR")
    return False


def discover_seeds_from_ahmia(session, keyword, max_results=AHMIA_MAX_RESULTS):
    """
    Searches Ahmia (a .onion search engine, https://ahmia.fi) for the
    keyword and returns discovered .onion URLs to use as crawl seeds.
    This way the user does not need to know any onion addresses.
    """
    onion_urls = []
    search_url = f"https://ahmia.fi/search/?q={quote(keyword)}"
    log(f"Searching Ahmia for '{keyword}' ...", "INFO")
    try:
        resp = session.get(search_url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if href.startswith("http://") and ".onion" in href:
                onion_urls.append(href)
        # remove duplicates while keeping order
        onion_urls = list(dict.fromkeys(onion_urls))
    except requests.exceptions.ProxyError:
        log("Proxy error during Ahmia search (is Tor running?).", "ERROR")
    except Exception as e:
        log(f"Ahmia search failed: {e}", "ERROR")
    return onion_urls[:max_results]


def fetch_page(session, url, retries=2):
    """
    Fetches HTML from a URL.
    Exception handling: ProxyError, timeouts, connection errors, etc.
    are handled with proper messages and retried.
    """
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()          # raises on 4xx/5xx
            return resp
        except requests.exceptions.ProxyError:
            # This is fatal — if Tor is down, nothing further will work
            log(f"Proxy error (is Tor down?) — {url}", "ERROR")
            raise TorConnectionError("Tor proxy unreachable")
        except requests.exceptions.ConnectTimeout:
            log(f"Connect timeout (attempt {attempt}/{retries}) — {url}", "WARN")
        except requests.exceptions.ReadTimeout:
            log(f"Read timeout (attempt {attempt}/{retries}) — {url}", "WARN")
        except requests.exceptions.ConnectionError as e:
            log(f"Connection error (attempt {attempt}/{retries}) — {url}: {e}", "WARN")
        except requests.exceptions.TooManyRedirects:
            log(f"Too many redirects — {url}", "WARN")
            break                          # no point retrying
        except requests.exceptions.SSLError as e:
            log(f"SSL error — {url}: {e}", "WARN")
        except requests.exceptions.InvalidSchema:
            log(f"Invalid URL scheme (http/https required) — {url}", "WARN")
            break
        except Exception as e:
            log(f"Unexpected error on {url}: {e}", "WARN")
        time.sleep(CRAWL_DELAY * attempt)  # short wait before retry
    return None


def extract_text(html):
    """Extracts only the text of a page via BeautifulSoup (drops scripts/styles)"""
    soup = BeautifulSoup(html, "html.parser")
    # We don't want content from these tags — removed to avoid false positives
    for tag in soup(["script", "style", "noscript", "svg", "form", "iframe"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


def extract_links(base_url, html):
    """Extracts all .onion links from a page (for further crawling)"""
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        # handle protocol-relative links (//host/path)
        if href.startswith("//"):
            href = "http:" + href
        if href.startswith(("http://", "https://")):
            absolute = urljoin(base_url, href)   # relative -> absolute URL
            host = urlparse(absolute).hostname or ""
            if host.endswith(".onion"):          # follow only .onion sites
                links.append(absolute)
    return links


def keyword_hit(text, keyword, use_regex=False):
    """Returns True if the keyword is present in the page text (case-insensitive)"""
    if use_regex:
        try:
            return re.search(keyword, text, re.IGNORECASE) is not None
        except re.error as e:
            log(f"Invalid regex '{keyword}': {e}", "ERROR")
            return False
    return keyword.lower() in text.lower()


def get_snippet(text, keyword, width=80):
    """Extracts a context snippet around the match (for the alert banner)"""
    idx = text.lower().find(keyword.lower())
    if idx == -1:
        return ""
    start = max(0, idx - width)
    end = min(len(text), idx + len(keyword) + width)
    return "..." + text[start:end].strip() + "..."


def print_alert(url, keyword, snippet):
    """Prints a big [!] ALERT banner when the keyword is found"""
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
    BFS-based crawler — starts from seed URLs, searches each page for the
    keyword, and follows discovered .onion links within the depth limit.
    """
    queue = deque((s, 0) for s in seeds)   # (url, depth) pairs
    visited = set()                         # avoid duplicate visits
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
            continue                        # page could not be fetched — skip

        pages_scanned += 1
        text = extract_text(resp.content)   # HTML -> plain text

        # ----- keyword found? -----
        if keyword_hit(text, keyword, use_regex):
            snippet = get_snippet(text, keyword)
            print_alert(url, keyword, snippet)      # big [!] alert
            matches.append((url, snippet))
            log(f"MATCH FOUND on {url}", "HIT")

        # ----- follow further links within the depth limit -----
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
    parser.add_argument("-k", "--keyword", help="Target keyword (email / company name / regex)")
    parser.add_argument("-s", "--seeds", nargs="+", help="Starting .onion URLs (one or more)")
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES,
                        help=f"Total pages to scan (default: {MAX_PAGES})")
    parser.add_argument("--max-depth", type=int, default=MAX_DEPTH,
                        help=f"How deep to follow links (default: {MAX_DEPTH})")
    parser.add_argument("--delay", type=float, default=CRAWL_DELAY,
                        help="Delay between requests in seconds (default: 1.0)")
    parser.add_argument("--proxy", default=SOCKS5_PROXY,
                        help=f"SOCKS5 proxy (default: {SOCKS5_PROXY})")
    parser.add_argument("--regex", action="store_true",
                        help="Treat the keyword as a regex")
    parser.add_argument("-o", "--output", help="Save found matches to a file")
    args = parser.parse_args()

    # ---------- Startup banner ----------
    print("""
    ====================================================================
      Automated Dark Web Leak & Brand Mention Monitor  (Tor + .onion)
    ====================================================================
    """)

    # ---------- Keyword: from flag or interactive prompt ----------
    keyword = args.keyword
    if not keyword:
        keyword = input("[?] Enter the target keyword (e.g. you@example.com): ").strip()
        if not keyword:
            log("No keyword provided. Exiting.", "ERROR")
            sys.exit(1)

    log(f"Proxy      : {args.proxy}")
    log(f"Keyword    : {keyword}")

    # ---------- Tor connectivity check (early, clear error) ----------
    session = build_session(args.proxy)
    if not check_tor_connection(session):
        log("Tor is not running — start Tor Browser or the tor daemon first.", "ERROR")
        sys.exit(1)

    # ---------- Seeds: flag -> Ahmia auto-discovery -> manual -> defaults ----------
    if args.seeds:
        seeds = list(args.seeds)
        log(f"Using {len(seeds)} seed(s) from --seeds.", "INFO")
    else:
        choice = input(f"[?] No onion URLs given. Auto-discover via Ahmia search for '{keyword}'? (y/N): ").strip().lower()
        if choice == "y":
            found = discover_seeds_from_ahmia(session, keyword)
            if found:
                seeds = found
                log(f"Ahmia returned {len(seeds)} onion URL(s) — using them as seeds.", "OK")
                for u in seeds:
                    log(f"  seed: {u}", "INFO")
            else:
                log("Ahmia returned no results, falling back to default seeds.", "WARN")
                seeds = DEFAULT_SEEDS
        else:
            choice2 = input("[?] Enter your own .onion URLs? (comma-separated, or press Enter): ").strip()
            if choice2:
                seeds = [u.strip() for u in choice2.split(",") if u.strip().startswith("http")]
                if not seeds:
                    log("No valid URLs found, falling back to default seeds.", "WARN")
                    seeds = DEFAULT_SEEDS
            else:
                seeds = DEFAULT_SEEDS

    log(f"Max pages  : {args.max_pages}  |  Max depth: {args.max_depth}  |  Regex: {args.regex}")

    # ---------- Start crawling ----------
    start = time.time()
    try:
        matches, scanned = crawl(session, seeds, keyword,
                                 args.max_pages, args.max_depth, args.regex)
    except TorConnectionError:
        log("Crawl aborted — the Tor proxy is not working.", "ERROR")
        sys.exit(1)
    except KeyboardInterrupt:
        log("Interrupted by user (Ctrl+C).", "WARN")
        sys.exit(130)

    elapsed = time.time() - start

    # ---------- Summary ----------
    print("\n" + "=" * 70)
    log(f"Scan complete — {scanned} pages scanned, "
        f"{len(matches)} match(es) found in {elapsed:.1f}s", "DONE")
    if matches:
        print("\n[!] YOUR EMAIL WAS FOUND ON THE DARK WEB — take action:")
        for url, _ in matches:
            print(f"  [!] {url}")
        if args.output:
            with open(args.output, "a", encoding="utf-8") as f:
                for url, snip in matches:
                    f.write(f"{datetime.now().isoformat()} | {keyword} | {url} | {snip}\n")
            log(f"Matches saved to {args.output}", "OK")
    else:
        log("No matches found on the crawled pages. Try new seeds or a higher max-pages value.", "INFO")


if __name__ == "__main__":
    main()
