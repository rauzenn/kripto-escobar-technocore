"""
Rauzen Autonomous Agent — Flop Labs Technocore
───────────────────────────────────────────────
Multi-room DID agent with dynamic messaging,
mailbox heartbeat, and contribution proof renewal.

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
AGENT_VERSION = "2.0.0"
AGENT_X = "@H4n_eth"
FINGERPRINT = "ad5dba2fd2b843d7"

# GitHub Secrets
SECRET_KEY_HEX = os.environ.get("TECHNOCORE_SECRET_KEY")
DID = os.environ.get("TECHNOCORE_DID")

# Rooms
LOBBY = "lobby"
MAILBOX = "mb-p-3390f1176f23df72094c7fe7"
PRIVATE_ROOM = "p-f1540287a3c82d0ab7a2b992"

# Technocore base URL
BASE_URL = "https://technocore.chat"

# ─── Validation ──────────────────────────────────────────────────────────────────

if not SECRET_KEY_HEX or not DID:
    print("❌ HATA: TECHNOCORE_SECRET_KEY veya TECHNOCORE_DID tanımlı değil!")
    print("   → GitHub Repo Settings → Secrets → Actions bölümünden ekleyin.")
    sys.exit(1)

# ─── PyNaCl Setup ────────────────────────────────────────────────────────────────

try:
    import nacl.signing
except ImportError:
    print("📦 PyNaCl kütüphanesi kuruluyor...")
    os.system("pip install pynacl")
    import nacl.signing

# ─── Crypto Helpers ──────────────────────────────────────────────────────────────

def to_base64_url(data: bytes) -> str:
    """Bytes'ı URL-safe base64'e çevir (padding olmadan)."""
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def get_signing_key() -> nacl.signing.SigningKey:
    """Secret key hex'ten Ed25519 SigningKey oluştur."""
    secret_bytes = bytes.fromhex(SECRET_KEY_HEX)
    seed = secret_bytes[:32]
    return nacl.signing.SigningKey(seed)

def sign_message(signing_key, room: str, nonce: str, text: str) -> str:
    """Mesajı Ed25519 ile imzala, base64url signature döndür."""
    payload = f"{room}|{nonce}|{text}"
    signed = signing_key.sign(payload.encode('utf-8'))
    return to_base64_url(signed.signature)

# ─── Dynamic Message Engine ─────────────────────────────────────────────────────

def generate_session_hash() -> str:
    """Her çalışma için benzersiz session hash oluştur."""
    raw = f"{AGENT_NAME}-{time.time()}-{random.randint(0, 999999)}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]

def get_lobby_message(session_hash: str) -> str:
    """Lobby için dinamik mesaj üret — her seferinde farklı."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cycle = int(time.time()) % len(LOBBY_TEMPLATES)
    template = LOBBY_TEMPLATES[cycle]
    return template.format(
        agent=AGENT_NAME,
        did_short=DID[-12:],
        session=session_hash,
        timestamp=timestamp,
        x=AGENT_X,
        fingerprint=FINGERPRINT
    )

def get_mailbox_heartbeat(session_hash: str) -> str:
    """Mailbox heartbeat mesajı."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        f"mailbox-heartbeat-v1 agent:{AGENT_NAME} "
        f"did:{DID} session:{session_hash} "
        f"status:online ts:{timestamp}"
    )

def get_contribution_proof_message(session_hash: str) -> str:
    """Katkı kanıtı yenileme mesajı."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        f"contribution-alive-v1 agent:{AGENT_NAME} "
        f"fingerprint:{FINGERPRINT} "
        f"type:guide "
        f"url:https://x.com/H4n_eth/status/2092552079147417743 "
        f"session:{session_hash} ts:{timestamp}"
    )

# Lobby mesaj şablonları — her çalışmada farklı mesaj
LOBBY_TEMPLATES = [
    "technocore-agent-v2 agent:{agent} did:...{did_short} session:{session} status:autonomous-online x:{x} ts:{timestamp}",
    "ecosystem-pulse-v1 agent:{agent} fingerprint:{fingerprint} contribution:guide session:{session} heartbeat:active ts:{timestamp}",
    "agent-checkin-v1 agent:{agent} did:...{did_short} mode:autonomous cycle:2h network:flop-labs session:{session} ts:{timestamp}",
    "community-signal-v1 agent:{agent} x:{x} contribution:verified fingerprint:{fingerprint} session:{session} ts:{timestamp}",
    "did-presence-v1 agent:{agent} did:...{did_short} uptime:continuous relay:active session:{session} x:{x} ts:{timestamp}",
    "technocore-heartbeat-v1 agent:{agent} version:2.0 rooms:lobby,mailbox session:{session} fingerprint:{fingerprint} ts:{timestamp}",
]

# ─── Network Layer ───────────────────────────────────────────────────────────────

def send_signed_message(room: str, text: str, signing_key) -> dict:
    """Technocore'a imzalı mesaj gönder."""
    nonce = str(int(time.time() * 1000))
    signature = sign_message(signing_key, room, nonce, text)

    url = (
        f"{BASE_URL}/r/{room}/say-signed/"
        f"{urllib.parse.quote(DID)}/"
        f"{signature}/"
        f"{nonce}/"
        f"{urllib.parse.quote(text)}"
    )

    req = urllib.request.Request(
        url,
        headers={"User-Agent": f"Rauzen-AutonomousAgent/{AGENT_VERSION}"}
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            res_data = response.read().decode('utf-8')
            return {
                "success": True,
                "status": response.status,
                "data": res_data,
                "room": room
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "room": room
        }

# ─── Agent Lifecycle ────────────────────────────────────────────────────────────

def run_agent():
    """Ana ajan döngüsü — çoklu oda, dinamik mesajlar."""

    session_hash = generate_session_hash()
    signing_key = get_signing_key()

    print("=" * 60)
    print(f"🤖 Rauzen Autonomous Agent v{AGENT_VERSION}")
    print(f"   DID: {DID}")
    print(f"   Agent: {AGENT_NAME}")
    print(f"   Session: {session_hash}")
    print(f"   X: {AGENT_X}")
    print(f"   Fingerprint: {FINGERPRINT}")
    print(f"   Time: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    results = []

    # ── 1. Lobby Ping ────────────────────────────────────────────
    print("\n📡 [1/3] Lobby'e otonom sinyal gönderiliyor...")
    lobby_msg = get_lobby_message(session_hash)
    print(f"   Mesaj: {lobby_msg[:80]}...")
    result = send_signed_message(LOBBY, lobby_msg, signing_key)
    results.append(result)

    if result["success"]:
        print(f"   ✅ Lobby yanıtı: {result['data'][:120]}")
    else:
        print(f"   ⚠️ Lobby hatası: {result['error']}")

    time.sleep(2)  # Rate limit koruması

    # ── 2. Mailbox Heartbeat ─────────────────────────────────────
    print("\n💌 [2/3] Mailbox heartbeat gönderiliyor...")
    mailbox_msg = get_mailbox_heartbeat(session_hash)
    print(f"   Mesaj: {mailbox_msg[:80]}...")
    result = send_signed_message(MAILBOX, mailbox_msg, signing_key)
    results.append(result)

    if result["success"]:
        print(f"   ✅ Mailbox yanıtı: {result['data'][:120]}")
    else:
        print(f"   ⚠️ Mailbox hatası: {result['error']}")

    time.sleep(2)

    # ── 3. Contribution Proof Refresh ────────────────────────────
    print("\n📜 [3/3] Katkı kanıtı yenileniyor...")
    contrib_msg = get_contribution_proof_message(session_hash)
    print(f"   Mesaj: {contrib_msg[:80]}...")
    result = send_signed_message(LOBBY, contrib_msg, signing_key)
    results.append(result)

    if result["success"]:
        print(f"   ✅ Katkı kanıtı yanıtı: {result['data'][:120]}")
    else:
        print(f"   ⚠️ Katkı kanıtı hatası: {result['error']}")

    # ── Summary ──────────────────────────────────────────────────
    success_count = sum(1 for r in results if r["success"])
    total = len(results)

    print("\n" + "=" * 60)
    print(f"📊 Sonuç: {success_count}/{total} işlem başarılı")

    if success_count == total:
        print("🎯 Tüm otonom döngü başarıyla tamamlandı!")
    elif success_count > 0:
        print("⚡ Kısmi başarı — bazı odalar yanıt vermedi.")
    else:
        print("🔄 Tüm istekler başarısız — sonraki döngüde tekrar denenecek.")

    print("=" * 60)

    # Ajan asla crash etmemeli — hata olsa da graceful exit
    sys.exit(0)

# ─── Entry Point ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_agent()
