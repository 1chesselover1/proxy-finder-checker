# Full minimal working script with explicit imports, error handling, and usage instructions

import requests
import re
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import filedialog
import concurrent.futures
import os
import sys

# Colors for console output
class Colors:
    RED = "\033[91m"
    WHITE = "\033[97m"
    BLUE_LIGHT = "\033[94m"
    BLUE_DARK = "\033[34m"
    LIGHT_BLUE_3 = "\033[96m"
    BLUE_SKY = "\033[36m"
    RESET = "\033[0m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner():
    print(f"{Colors.LIGHT_BLUE_3}=== PROXY FINDER TOOL ==={Colors.RESET}")

def fetch_proxies_from_table(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0 Safari/537.36"
    }
    proxies = []
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        table = None
        tables = soup.find_all("table")
        for t in tables:
            if 'proxylisttable' in t.get("id", "") or 'table' in t.get("class", []):
                table = t
                break

        if not table:
            print(f"{Colors.RED}[!] Proxy table not found on {url}{Colors.RESET}")
            return proxies

        tbody = table.find("tbody")
        if not tbody:
            print(f"{Colors.RED}[!] Table tbody not found on {url}{Colors.RESET}")
            return proxies

        for row in tbody.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 8:
                continue
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            https = cols[6].text.strip().lower()
            scheme = "https" if https == "yes" else "http"
            proxy = f"{scheme}://{ip}:{port}"
            proxies.append(proxy)
    except Exception as e:
        print(f"{Colors.RED}[!] Error fetching proxies from {url}: {e}{Colors.RESET}")
    return proxies

def check_proxy(proxy: str) -> (str, bool):
    try:
        resp = requests.get(
            "http://httpbin.org/ip",
            proxies={"http": proxy, "https": proxy},
            timeout=4)
        if resp.status_code == 200:
            return proxy, True
    except:
        pass
    return proxy, False

def save_proxies(proxies):
    try:
        print(f"{Colors.LIGHT_BLUE_3}[*] Choose where to save proxies...{Colors.RESET}")
        root = tk.Tk()
        root.withdraw()
        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Save proxy list as..."
        )
        if not save_path:
            print(f"{Colors.RED}[!] No save location selected.{Colors.RESET}")
            return
        with open(save_path, "w", encoding="utf-8") as f:
            f.write("\n".join(proxies))
        print(f"{Colors.WHITE}[✓] Proxies saved to: {save_path}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[!] Failed to save proxies: {e}{Colors.RESET}")

def proxy_finder():
    clear_screen()
    display_banner()
    print(f"{Colors.BLUE_SKY}[~] Fetching proxies from multiple sources...{Colors.RESET}")

    urls = [
        "https://free-proxy-list.net/",
        "https://www.us-proxy.org/",
        "https://www.sslproxies.org/",
        "https://www.socks-proxy.net/"
    ]

    proxies = []
    for url in urls:
        proxies += fetch_proxies_from_table(url)

    proxies = list(set(proxies))

    if not proxies:
        print(f"{Colors.RED}[!] No proxies found from all sources.{Colors.RESET}")
        input("Press Enter to return to menu...")
        return

    print(f"{Colors.WHITE}Found {len(proxies)} unique proxies.{Colors.RESET}")
    print(f"{Colors.BLUE_LIGHT}Do you want to check which proxies are working? (y/n){Colors.RESET}")
    if input(" > ").strip().lower() == 'y':
        print(f"{Colors.LIGHT_BLUE_3}[=] Checking proxies...{Colors.RESET}")
        working = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(check_proxy, p): p for p in proxies}
            for future in concurrent.futures.as_completed(futures):
                proxy, status = future.result()
                if status:
                    print(f"{Colors.BLUE_DARK}[+] {proxy} is working{Colors.RESET}")
                    working.append(proxy)
                else:
                    print(f"{Colors.BLUE_LIGHT}[-] {proxy} is not working{Colors.RESET}")
        if not working:
            print(f"{Colors.RED}[!] No working proxies found.{Colors.RESET}")
            return
        proxies_to_use = working
        print(f"{Colors.BLUE_SKY}[+] {len(working)} working proxies found.{Colors.RESET}")
    else:
        proxies_to_use = proxies

    print(f"{Colors.WHITE}Do you want to save the proxies to a file? (y/n){Colors.RESET}")
    if input(" > ").strip().lower() == 'y':
        save_proxies(proxies_to_use)
    else:
        print(f"{Colors.BLUE_LIGHT}[+] Finished. You can now use the proxies.{Colors.RESET}")

if __name__ == "__main__":
    try:
        proxy_finder()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Interrupted by user. Exiting.{Colors.RESET}")
        sys.exit(0)
