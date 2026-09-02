"""
Rauzen Autonomous Agent v3.0 — Flop Labs Technocore
────────────────────────────────────────────────────
Q4 2026 Testnet-Ready Agent

Strategy shift: No more 2h lobby spam.
- Smart maintenance mode: keep rooms alive, refresh profile
- Room ownership: d-rauzen private room
- Profile note refresh: every cycle
- Q4 Ready: faucet + inference pipeline placeholder

Agent  : rauzen
DID    : did:key:z6MkwX5tHfMXY3wnpFZqYnCt8dJK2s21CyroczgUWqJ2bTyB
X      : @H4n_eth
"""

import os
import sys
import time
import json
import base64
import hashlib
import random
import urllib.request
import urllib.parse
from datetime import datetime, timezone

# ─── Configuration ──────────────────────────────────────────────────────────────

AGENT_NAME = "rauzen"
AGENT_VERSION = "3.0.0"
AGENT_X = "@H4n_eth"
FINGERPRINT = "ad5dba2fd2b843d7"

# GitHub Secrets
SECRET_KEY_HEX = os.environ.get("TECHNOCORE_SECRET_KEY")
DID = os.environ.get("TECHNOCORE_DID")

# Rooms
LOBBY = "lobby"
MAILBOX = "mb-p-3390f1176f23df72094c7fe7"
PRIVATE_ROOM = "p-f1540287a3c82d0ab7a2b992"
OWNED_ROOM = "d-rauzen"  # Sahiplenilecek özel oda

# Technocore base URL
BASE_URL = "https://technocore.chat"

# Contribution info
CONTRIBUTION_TYPE = "guide"
CONTRIBUTION_URL = "https://x.com/H4n_eth/status/2092552079147417743"
CONTRIBUTION_SUMMARY = "Technocore ecosystem introductory thread"

# ─── Validation ──────────────────────────────────────────────────────────────────

if not SECRET_KEY_HEX or not DID:
    print("❌ HATA: TECHNOCORE_SECRET_KEY veya TECHNOCORE_DID tanımlı değil!")
    sys.exit(1)

# ─── PyNaCl Setup ────────────────────────────────────────────────────────────────

try:
    import nacl.signing
except ImportError:
    print("📦 PyNaCl kuruluyor...")
    os.system("pip install pynacl")
    import nacl.signing

# ─── Crypto ──────────────────────────────────────────────────────────────────────

def to_base64_url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def get_signing_key() -> nacl.signing.SigningKey:
    secret_bytes = bytes.fromhex(SECRET_KEY_HEX)
    seed = secret_bytes[:32]
    return nacl.signing.SigningKey(seed)

def generate_session_hash() -> str:
    raw = f"{AGENT_NAME}-{time.time()}-{random.randint(0, 999999)}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]

# ─── Network Layer ───────────────────────────────────────────────────────────────

def send_signed_message(room: str, text: str, signing_key) -> dict:
    """Technocore'a imzalı mesaj gönder."""
    nonce = str(int(time.time() * 1000))
    payload = f"{room}|{nonce}|{text}"
    signed = signing_key.sign(payload.encode('utf-8'))
    signature = to_base64_url(signed.signature)

    url = (
        f"{BASE_URL}/r/{room}/say-signed/"
        f"{urllib.parse.quote(DID)}/"
        f"{signature}/{nonce}/"
        f"{urllib.parse.quote(text)}"
    )

    req = urllib.request.Request(
        url,
        headers={"User-Agent": f"Rauzen-Agent/{AGENT_VERSION}"}
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            res_data = response.read().decode('utf-8')
            return {"success": True, "status": response.status, "data": res_data, "room": room}
    except Exception as e:
        return {"success": False, "error": str(e), "room": room}

def publish_kv_note(namespace: str, key: str, value: str, signing_key) -> dict:
    """Technocore KV store'a imzalı not yayınla."""
    nonce = str(int(time.time() * 1000))
    kv_path = f"/kv/{namespace}/{key}"
    payload = f"{kv_path}|{nonce}|{value}"
    signed = signing_key.sign(payload.encode('utf-8'))
    signature = to_base64_url(signed.signature)

    url = (
        f"{BASE_URL}{kv_path}/set/"
        f"{urllib.parse.quote(value)}"
    )

    req = urllib.request.Request(
        url,
        headers={"User-Agent": f"Rauzen-Agent/{AGENT_VERSION}"}
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            res_data = response.read().decode('utf-8')
            return {"success": True, "data": res_data}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Smart Message Templates ────────────────────────────────────────────────────

def get_maintenance_message(session: str) -> str:
    """Haftalık bakım mesajı — odayı canlı tutar."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    templates = [
        f"agent-maintenance-v3 agent:{AGENT_NAME} did:...{DID[-12:]} session:{session} mode:q4-ready contribution:{CONTRIBUTION_TYPE} x:{AGENT_X} ts:{ts}",
        f"rauzen-alive-v3 fingerprint:{FINGERPRINT} status:q4-standby session:{session} rooms:lobby,d-rauzen x:{AGENT_X} ts:{ts}",
        f"ecosystem-presence-v3 agent:{AGENT_NAME} did:...{DID[-12:]} contribution:verified mode:testnet-ready session:{session} ts:{ts}",
        f"did-heartbeat-v3 agent:{AGENT_NAME} version:{AGENT_VERSION} session:{session} strategy:q4-preparation x:{AGENT_X} ts:{ts}",
    ]
    return templates[int(time.time()) % len(templates)]

def get_room_keepalive(session: str) -> str:
    """Sahiplenilmiş odayı canlı tutan mesaj."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        f"room-keepalive-v1 agent:{AGENT_NAME} "
        f"room:{OWNED_ROOM} owner:{DID} "
        f"session:{session} x:{AGENT_X} ts:{ts}"
    )

def get_profile_note() -> str:
    """DID profil notu — 7 günde bir tazelenmeli."""
    return (
        f"technocore-profile-v1 "
        f"did:{DID} "
        f"agent:{AGENT_NAME} "
        f"mailbox:{MAILBOX} "
        f"contribution:/kv/contrib/{FINGERPRINT} "
        f"x:{AGENT_X} "
        f"guide:{CONTRIBUTION_URL}"
    )

def get_contribution_note() -> str:
    """Katkı notu."""
    return (
        f"technocore-contribution-v1 "
        f"did:{DID} "
        f"agent:{AGENT_NAME} "
        f"type:{CONTRIBUTION_TYPE} "
        f"summary:{CONTRIBUTION_SUMMARY} "
        f"url:{CONTRIBUTION_URL} "
        f"x:{AGENT_X}"
    )

# ─── Agent Actions ───────────────────────────────────────────────────────────────

def action_lobby_maintenance(signing_key, session: str) -> dict:
    """Lobby'de varlık göster — odayı canlı tut."""
    msg = get_maintenance_message(session)
    print(f"   Mesaj: {msg[:80]}...")
    return send_signed_message(LOBBY, msg, signing_key)

def action_owned_room_keepalive(signing_key, session: str) -> dict:
    """Sahiplenilmiş d-rauzen odasını canlı tut."""
    msg = get_room_keepalive(session)
    print(f"   Mesaj: {msg[:80]}...")
    return send_signed_message(OWNED_ROOM, msg, signing_key)

def action_profile_refresh(signing_key) -> dict:
    """Profil notunu tazele (7 gün limiti var)."""
    note = get_profile_note()
    print(f"   Not: {note[:80]}...")
    # Profil notu KV store üzerinden yayınlanır
    # Fallback: lobby'e profil mesajı olarak gönder
    url = (
        f"{BASE_URL}/kv/did-ad/{FINGERPRINT[:-2]}/{FINGERPRINT[-2:]}/set/"
        f"{urllib.parse.quote(note)}"
    )
    req = urllib.request.Request(
        url,
        headers={"User-Agent": f"Rauzen-Agent/{AGENT_VERSION}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            res_data = response.read().decode('utf-8')
            return {"success": True, "data": res_data}
    except Exception as e:
        # Fallback: lobby'e gönder
        return send_signed_message(LOBBY, f"profile-refresh-v1 {note}", signing_key)

def action_contribution_refresh(signing_key) -> dict:
    """Katkı notunu tazele."""
    note = get_contribution_note()
    print(f"   Not: {note[:80]}...")
    url = (
        f"{BASE_URL}/kv/contrib/{FINGERPRINT}/set/"
        f"{urllib.parse.quote(note)}"
    )
    req = urllib.request.Request(
        url,
        headers={"User-Agent": f"Rauzen-Agent/{AGENT_VERSION}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            res_data = response.read().decode('utf-8')
            return {"success": True, "data": res_data}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Main Agent Lifecycle ────────────────────────────────────────────────────────

def run_agent():
    session = generate_session_hash()
    signing_key = get_signing_key()

    print("=" * 60)
    print(f"🤖 Rauzen Autonomous Agent v{AGENT_VERSION}")
    print(f"   Mode: Q4 Testnet Preparation")
    print(f"   Agent: {AGENT_NAME}")
    print(f"   Session: {session}")
    print(f"   X: {AGENT_X}")
    print(f"   Fingerprint: {FINGERPRINT}")
    print(f"   Time: {datetime.now(timezone.utc).isoformat()}")
    print(f"   Strategy: Smart maintenance + Q4 ready")
    print("=" * 60)

    results = []

    # ── 1. Lobby Maintenance ─────────────────────────────────────
    print("\n📡 [1/4] Lobby bakım mesajı gönderiliyor...")
    result = action_lobby_maintenance(signing_key, session)
    results.append(("Lobby", result))
    if result["success"]:
        print(f"   ✅ Yanıt: {result['data'][:100]}")
    else:
        print(f"   ⚠️ Hata: {result['error']}")

    time.sleep(2)

    # ── 2. Owned Room Keepalive ──────────────────────────────────
    print("\n🏠 [2/4] d-rauzen odası canlı tutuluyor...")
    result = action_owned_room_keepalive(signing_key, session)
    results.append(("d-rauzen", result))
    if result["success"]:
        print(f"   ✅ Yanıt: {result['data'][:100]}")
    else:
        print(f"   ⚠️ Hata: {result['error']}")

    time.sleep(2)

    # ── 3. Profile Note Refresh ──────────────────────────────────
    print("\n📋 [3/4] Profil notu tazeleniyor...")
    result = action_profile_refresh(signing_key)
    results.append(("Profil", result))
    if result["success"]:
        print(f"   ✅ Yanıt: {result.get('data', 'OK')[:100]}")
    else:
        print(f"   ⚠️ Hata: {result.get('error', 'unknown')}")

    time.sleep(2)

    # ── 4. Contribution Note Refresh ─────────────────────────────
    print("\n📜 [4/4] Katkı notu tazeleniyor...")
    result = action_contribution_refresh(signing_key)
    results.append(("Katkı", result))
    if result["success"]:
        print(f"   ✅ Yanıt: {result.get('data', 'OK')[:100]}")
    else:
        print(f"   ⚠️ Hata: {result.get('error', 'unknown')}")

    # ── Summary ──────────────────────────────────────────────────
    success_count = sum(1 for _, r in results if r["success"])
    total = len(results)

    print("\n" + "=" * 60)
    print(f"📊 Sonuç: {success_count}/{total} işlem başarılı")
    for name, r in results:
        status = "✅" if r["success"] else "⚠️"
        print(f"   {status} {name}")

    if success_count == total:
        print("🎯 Bakım döngüsü tamamlandı!")
    elif success_count > 0:
        print("⚡ Kısmi başarı — sonraki döngüde tekrar denenecek.")
    else:
        print("🔄 Sunucu erişilemedi — sonraki döngüde tekrar.")

    print(f"\n💡 Q4 2026 Testnet'e hazırız. Faucet açıldığında devreye gireceğiz.")
    print("=" * 60)

    sys.exit(0)

# ─── Entry Point ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_agent()
