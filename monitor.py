"""
Rauzen Ecosystem Monitor — Flop Labs Tracker
─────────────────────────────────────────────
Monitors Technocore lobby, flop-labs GitHub repos,
and protocol changes. Generates diff reports.

Runs as GitHub Actions workflow every 6 hours.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone

AGENT_NAME = "rauzen"
AGENT_VERSION = "1.0.0"

# ─── Sources to Monitor ─────────────────────────────────────────────────────────

TECHNOCORE_BASE = "https://technocore.chat"

# Rooms to watch for announcements
WATCH_ROOMS = [
    "lobby",
    "announcements",
    "dev",
    "faucet",
    "testnet",
]

# GitHub repos to track
GITHUB_REPOS = [
    "flop-labs/technocore-chat",
    "flop-labs/technocore",
    "flop-labs/flop",
    "kriptoescobar007/kripto-escobar-technocore",
    "kriptolia/technocore-did-studio",
]

# Keywords that signal important updates
ALERT_KEYWORDS = [
    "faucet", "testnet", "airdrop", "mainnet", "launch",
    "token", "FLOP", "inference", "validator", "bond",
    "breaking", "upgrade", "migration", "deadline",
    "announcement", "duyuru", "güncelleme",
]

STATE_FILE = "monitor_state.json"

# ─── Helpers ─────────────────────────────────────────────────────────────────────

def fetch_url(url: str, timeout: int = 15) -> str | None:
    """URL'den veri çek, hata durumunda None döndür."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": f"Rauzen-Monitor/{AGENT_VERSION}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode('utf-8')
    except Exception as e:
        print(f"   ⚠️ Fetch hatası ({url[:60]}...): {e}")
        return None

def load_state() -> dict:
    """Önceki tarama durumunu yükle."""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"rooms": {}, "repos": {}, "last_run": None}

def save_state(state: dict):
    """Tarama durumunu kaydet."""
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

# ─── Technocore Room Scanner ────────────────────────────────────────────────────

def scan_room(room: str) -> dict | None:
    """Technocore odasını tara, son mesaj bilgisini döndür."""
    url = f"{TECHNOCORE_BASE}/r/{room}?format=json"
    data = fetch_url(url)
    if not data:
        # Try without json format
        url = f"{TECHNOCORE_BASE}/r/{room}"
        data = fetch_url(url)

    if data:
        return {
            "room": room,
            "content_length": len(data),
            "snippet": data[:500],
            "has_content": len(data) > 50
        }
    return None

def check_rooms(state: dict) -> list:
    """Tüm odaları tara, değişiklikleri tespit et."""
    alerts = []

    for room in WATCH_ROOMS:
        print(f"   📡 Oda taraniyor: {room}")
        result = scan_room(room)

        if result and result["has_content"]:
            prev_len = state.get("rooms", {}).get(room, {}).get("content_length", 0)

            if result["content_length"] != prev_len:
                # İçerik değişti
                change_type = "YENİ ODA" if prev_len == 0 else "GÜNCELLENDİ"
                diff = result["content_length"] - prev_len

                # Alert keyword kontrolü
                snippet_lower = result["snippet"].lower()
                found_keywords = [kw for kw in ALERT_KEYWORDS if kw.lower() in snippet_lower]

                alert = {
                    "source": "technocore",
                    "room": room,
                    "type": change_type,
                    "diff_bytes": diff,
                    "keywords": found_keywords,
                    "snippet": result["snippet"][:200],
                    "priority": "HIGH" if found_keywords else "NORMAL"
                }
                alerts.append(alert)

                if found_keywords:
                    print(f"   🚨 ALERT! {room}: {', '.join(found_keywords)}")
                else:
                    print(f"   📝 Değişiklik: {room} ({change_type}, {diff:+d} bytes)")

            # State güncelle
            if "rooms" not in state:
                state["rooms"] = {}
            state["rooms"][room] = {
                "content_length": result["content_length"],
                "last_check": datetime.now(timezone.utc).isoformat()
            }
        else:
            print(f"   ⬜ {room}: erişilemedi veya boş")

    return alerts

# ─── GitHub Repo Scanner ────────────────────────────────────────────────────────

def check_github_repos(state: dict) -> list:
    """GitHub repolarını tara, yeni commit/release/değişiklik tespit et."""
    alerts = []

    for repo in GITHUB_REPOS:
        print(f"   🐙 Repo taraniyor: {repo}")

        # Son commit kontrolü
        commits_url = f"https://api.github.com/repos/{repo}/commits?per_page=3"
        data = fetch_url(commits_url)

        if data:
            try:
                commits = json.loads(data)
                if isinstance(commits, list) and len(commits) > 0:
                    latest_sha = commits[0]["sha"][:8]
                    latest_msg = commits[0]["commit"]["message"].split("\n")[0]
                    latest_date = commits[0]["commit"]["committer"]["date"]

                    prev_sha = state.get("repos", {}).get(repo, {}).get("latest_sha", "")

                    if latest_sha != prev_sha and prev_sha != "":
                        # Yeni commit!
                        new_count = 0
                        for c in commits:
                            if c["sha"][:8] == prev_sha:
                                break
                            new_count += 1

                        # Alert keyword kontrolü
                        msg_lower = latest_msg.lower()
                        found_keywords = [kw for kw in ALERT_KEYWORDS if kw.lower() in msg_lower]

                        alert = {
                            "source": "github",
                            "repo": repo,
                            "type": "NEW_COMMITS",
                            "count": new_count,
                            "latest_sha": latest_sha,
                            "latest_message": latest_msg[:120],
                            "date": latest_date,
                            "keywords": found_keywords,
                            "priority": "HIGH" if found_keywords else "NORMAL"
                        }
                        alerts.append(alert)

                        if found_keywords:
                            print(f"   🚨 ALERT! {repo}: {latest_msg[:60]}")
                        else:
                            print(f"   📝 Yeni commit: {repo} → {latest_msg[:60]}")

                    # State güncelle
                    if "repos" not in state:
                        state["repos"] = {}
                    state["repos"][repo] = {
                        "latest_sha": latest_sha,
                        "latest_message": latest_msg[:120],
                        "last_check": datetime.now(timezone.utc).isoformat()
                    }

            except (json.JSONDecodeError, KeyError, IndexError) as e:
                print(f"   ⚠️ Parse hatası: {repo} — {e}")
        else:
            print(f"   ⬜ {repo}: erişilemedi")

        time.sleep(1)  # Rate limit

    # Release kontrolü (sadece flop-labs repoları)
    for repo in GITHUB_REPOS:
        if "flop-labs" in repo:
            releases_url = f"https://api.github.com/repos/{repo}/releases?per_page=1"
            data = fetch_url(releases_url)
            if data:
                try:
                    releases = json.loads(data)
                    if isinstance(releases, list) and len(releases) > 0:
                        latest_tag = releases[0].get("tag_name", "")
                        prev_tag = state.get("repos", {}).get(repo, {}).get("latest_release", "")

                        if latest_tag and latest_tag != prev_tag and prev_tag != "":
                            alert = {
                                "source": "github_release",
                                "repo": repo,
                                "type": "NEW_RELEASE",
                                "tag": latest_tag,
                                "name": releases[0].get("name", ""),
                                "priority": "HIGH"
                            }
                            alerts.append(alert)
                            print(f"   🚨 YENİ RELEASE! {repo} → {latest_tag}")

                        if "repos" not in state:
                            state["repos"] = {}
                        if repo not in state["repos"]:
                            state["repos"][repo] = {}
                        state["repos"][repo]["latest_release"] = latest_tag

                except (json.JSONDecodeError, KeyError, IndexError):
                    pass

            time.sleep(1)

    return alerts

# ─── Faucet Checker ──────────────────────────────────────────────────────────────

def check_faucet(state: dict) -> list:
    """Faucet endpoint'inin aktif olup olmadığını kontrol et."""
    alerts = []
    faucet_urls = [
        f"{TECHNOCORE_BASE}/faucet",
        f"{TECHNOCORE_BASE}/r/faucet",
        f"{TECHNOCORE_BASE}/api/faucet",
    ]

    for url in faucet_urls:
        data = fetch_url(url, timeout=10)
        if data and "404" not in data[:50] and "not found" not in data.lower()[:100]:
            prev_status = state.get("faucet", {}).get(url, "inactive")
            if prev_status == "inactive":
                alert = {
                    "source": "faucet",
                    "url": url,
                    "type": "FAUCET_DETECTED",
                    "snippet": data[:200],
                    "priority": "CRITICAL"
                }
                alerts.append(alert)
                print(f"   🚨🚨🚨 FAUCET AKTİF: {url}")

            if "faucet" not in state:
                state["faucet"] = {}
            state["faucet"][url] = "active"

    return alerts

# ─── Report Generator ───────────────────────────────────────────────────────────

def generate_report(all_alerts: list) -> str:
    """Tarama raporu oluştur."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    critical = [a for a in all_alerts if a.get("priority") == "CRITICAL"]
    high = [a for a in all_alerts if a.get("priority") == "HIGH"]
    normal = [a for a in all_alerts if a.get("priority") == "NORMAL"]

    lines = [
        f"# 📊 Rauzen Monitor Report — {ts}",
        f"",
        f"**Toplam alert**: {len(all_alerts)} "
        f"(🔴 {len(critical)} critical, 🟠 {len(high)} high, 🟢 {len(normal)} normal)",
        f"",
    ]

    if critical:
        lines.append("## 🔴 CRITICAL ALERTS")
        for a in critical:
            lines.append(f"- **{a['type']}**: {a.get('url', a.get('repo', a.get('room', '?')))}")
            if 'snippet' in a:
                lines.append(f"  ```\n  {a['snippet'][:150]}\n  ```")

    if high:
        lines.append("## 🟠 HIGH PRIORITY")
        for a in high:
            source = a.get('repo', a.get('room', '?'))
            lines.append(f"- **{a['type']}** [{a['source']}] {source}")
            if 'keywords' in a:
                lines.append(f"  Keywords: {', '.join(a['keywords'])}")
            if 'latest_message' in a:
                lines.append(f"  Commit: {a['latest_message']}")

    if normal:
        lines.append("## 🟢 NORMAL")
        for a in normal:
            source = a.get('repo', a.get('room', '?'))
            lines.append(f"- {a['type']} [{a['source']}] {source}")

    if not all_alerts:
        lines.append("✅ Değişiklik tespit edilmedi. Ekosistem stabil.")

    return "\n".join(lines)

# ─── Main ────────────────────────────────────────────────────────────────────────

def run_monitor():
    print("=" * 60)
    print(f"🔍 Rauzen Ecosystem Monitor v{AGENT_VERSION}")
    print(f"   Time: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    state = load_state()
    all_alerts = []

    # 1. Technocore Rooms
    print("\n📡 Technocore odaları taranıyor...")
    room_alerts = check_rooms(state)
    all_alerts.extend(room_alerts)

    # 2. GitHub Repos
    print("\n🐙 GitHub repoları taranıyor...")
    repo_alerts = check_github_repos(state)
    all_alerts.extend(repo_alerts)

    # 3. Faucet Check
    print("\n🚰 Faucet kontrol ediliyor...")
    faucet_alerts = check_faucet(state)
    all_alerts.extend(faucet_alerts)

    # Save state
    save_state(state)

    # Generate report
    report = generate_report(all_alerts)
    print("\n" + report)

    # Summary
    print("\n" + "=" * 60)
    critical_count = sum(1 for a in all_alerts if a.get("priority") == "CRITICAL")
    high_count = sum(1 for a in all_alerts if a.get("priority") == "HIGH")

    if critical_count > 0:
        print(f"🚨🚨🚨 {critical_count} CRITICAL ALERT — ACİL AKSİYON GEREKLİ!")
    elif high_count > 0:
        print(f"🟠 {high_count} önemli değişiklik tespit edildi.")
    elif all_alerts:
        print(f"📝 {len(all_alerts)} değişiklik tespit edildi.")
    else:
        print("✅ Ekosistem stabil — değişiklik yok.")
    print("=" * 60)

if __name__ == "__main__":
    run_monitor()
