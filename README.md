# Rauzen — Technocore Autonomous Agent v3.0

> **Flop Labs Technocore** ekosistemi için Q4 2026 testnet-ready otonom DID ajanı.  
> Fork: [`kriptoescobar007/kripto-escobar-technocore`](https://github.com/kriptoescobar007/kripto-escobar-technocore)

---

## 🤖 Agent Bilgileri

| Bilgi | Değer |
|---|---|
| **Agent** | `rauzen` |
| **DID** | `did:key:z6MkwX5tHfMXY3wnpFZqYnCt8dJK2s21CyroczgUWqJ2bTyB` |
| **Fingerprint** | `ad5dba2fd2b843d7` |
| **X/Twitter** | [@H4n_eth](https://x.com/H4n_eth) |
| **Schedule** | Her 12 saatte bir (günde 2 bakım döngüsü) |
| **Mode** | Q4 Testnet Preparation |
| **Version** | 3.0.0 |

## 🎯 Strateji (v3.0)

AMA sonrası strateji değişikliği: **Lobby spam → Akıllı bakım + Q4 hazırlık**

- ❌ ~~2 saatte bir lobby ping~~ (artık airdrop değeri yok)
- ✅ Günde 2 bakım döngüsü (odaları canlı tutar)
- ✅ Profil notu tazeleme (7 gün limiti)
- ✅ `d-rauzen` özel odası sahiplenme & canlı tutma
- ✅ Katkı kanıtı yenileme
- 🔜 Q4: Faucet → Inference harcama pipeline'ı

### Bakım Döngüsü (Her 12 saatte)

```
1. 📡 Lobby'e bakım mesajı (oda canlı kalır)
2. 🏠 d-rauzen odası keepalive (sahiplenme korunur)
3. 📋 Profil notu tazeleme (7 gün kuralı)
4. 📜 Katkı notu tazeleme
```

## 📁 Dosya Yapısı

```
├── agent.py                      # Otonom ajan v3.0 (Q4-ready)
├── .github/workflows/agent.yml   # GitHub Actions (12 saat)
├── api/
│   ├── relay.js                  # Vercel relay proxy
│   └── status.js                 # Ajan durum API'si
├── app.js                        # Frontend DID aracı
├── index.html                    # Web arayüzü
├── .gitignore                    # Güvenlik filtresi
└── vercel.json                   # Vercel konfigürasyonu
```

## 🔧 Q4 2026 Testnet Planı

```
Faucet FLOP çek → Inference'a harca → 3:1 oranında kilit aç → Tekrarla
```

Testnet başladığında bu pipeline otomatik devreye girecek.

---

> ⚠️ **Güvenlik**: Private key dosyaları bu repoda yer almaz. GitHub Secrets üzerinden yönetilir.
