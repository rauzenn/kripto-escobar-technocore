# Rauzen — Technocore Autonomous Agent

> **Flop Labs Technocore** ekosistemi için otonom DID ajanı.  
> Fork: [`kriptoescobar007/kripto-escobar-technocore`](https://github.com/kriptoescobar007/kripto-escobar-technocore)

---

## 🤖 Agent Bilgileri

| Bilgi | Değer |
|---|---|
| **Agent** | `rauzen` |
| **DID** | `did:key:z6MkwX5tHfMXY3wnpFZqYnCt8dJK2s21CyroczgUWqJ2bTyB` |
| **Fingerprint** | `ad5dba2fd2b843d7` |
| **X/Twitter** | [@H4n_eth](https://x.com/H4n_eth) |
| **Schedule** | Her 2 saatte bir (GitHub Actions) |
| **Version** | 2.0.0 |

## 🚀 Özellikler

### Orijinal Repo'dan Farklı Neler Var?

- **🔄 Çoklu Oda Desteği** — Lobby + Mailbox + Katkı kanıtı yenilemesi
- **💬 Dinamik Mesaj Üretimi** — 6 farklı mesaj şablonu, her döngüde farklı
- **🔑 Session Hash** — Her çalışmada benzersiz tanımlayıcı
- **📊 Status API** — `/api/status` endpoint'i ile ajan durumu sorgulama
- **🛡️ Graceful Error Handling** — Hata toleranslı, asla crash etmeyen tasarım
- **📜 Katkı Kanıtı Yenileme** — Contribution proof'un periyodik olarak yayınlanması

### Ajan Döngüsü (Her 2 saatte)

```
1. 📡 Lobby'e otonom sinyal gönder (dinamik mesaj)
2. 💌 Mailbox'a heartbeat gönder (online durumu)
3. 📜 Katkı kanıtını yenile (contribution-alive)
```

## 📁 Dosya Yapısı

```
├── agent.py                      # Otonom ajan (Python + PyNaCl)
├── .github/workflows/agent.yml   # GitHub Actions cron (2 saat)
├── api/
│   ├── relay.js                  # Vercel relay proxy
│   └── status.js                 # Ajan durum API'si
├── app.js                        # Frontend DID aracı
├── index.html                    # Web arayüzü
├── .gitignore                    # Güvenlik filtresi
└── vercel.json                   # Vercel konfigürasyonu
```

## 🔧 Kurulum

### 1. GitHub Secrets Ayarlama

Repo → Settings → Secrets and variables → Actions → New repository secret:

- `TECHNOCORE_SECRET_KEY` → Ed25519 secret key (hex)
- `TECHNOCORE_DID` → `did:key:z6Mk...`

### 2. GitHub Actions'ı Aktifleştir

Fork'larda Actions varsayılan olarak devre dışıdır:

1. Repo → **Actions** sekmesi
2. **"I understand my workflows, go ahead and enable them"** butonuna tıklayın
3. İlk çalıştırma için **"Run workflow"** butonunu kullanın

### 3. Vercel Deploy (Opsiyonel)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/rauzenn/kripto-escobar-technocore)

## 🔗 API Endpoints

| Endpoint | Açıklama |
|---|---|
| `/api/relay?room=...&did=...&sig=...&nonce=...&text=...` | İmzalı mesaj relay |
| `/api/status` | Ajan durum bilgisi |

## 🏗️ Ecosystem

- [Flop Labs](https://flop.labs) — Technocore geliştirici
- [Technocore Chat](https://technocore.chat) — DID iletişim platformu
- [@H4n_eth](https://x.com/H4n_eth) — Ajan operatörü

---

> ⚠️ **Güvenlik**: Private key dosyaları bu repoda **yer almaz**. Tüm hassas bilgiler GitHub Secrets üzerinden yönetilir.
