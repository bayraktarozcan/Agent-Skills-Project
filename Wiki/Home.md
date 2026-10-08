# AgentSynapse

| <kbd>[🇬🇧 **English**](#en)</kbd> | <kbd>[🇹🇷 **Türkçe**](#tr)</kbd> |

<a id="en"></a>
<details open>
<summary>English</summary>

Welcome to the **AgentSynapse** wiki.

This project aggregates **~571 SKILL.md files** (Recommended profile) from **35 top-tier repositories** across **10 functional categories** (K1–K10). It provides a unified, cross-platform Python installer (`skills.py`) that clones all repos, extracts every SKILL.md, deduplicates, and organizes them into `~/.agents/skills/` — ready for discovery by Claude Code, OpenCode, Cursor, and any agent that reads the standard SKILL.md format.

### Quick Start

```bash
git clone https://github.com/bayraktarozcan/AgentSynapse.git
cd AgentSynapse
python skills.py
```

That's it. The recommended profile installs ~571 skills from 35 curated repos.

### Profiles

| Profile | Repos | Skills | Description |
|---------|-------|--------|-------------|
| `recommended` (default) | 35 | ~571 | Curated subset — highest quality |
| `trusted` | 40 | ~645 | K1–K8, all trusted categories |
| `all` | 49 | ~1000 | Everything including K9–K10 |

### Features

- **Zero dependencies** — Python stdlib only (no pip install required)
- **Bilingual** — English & Turkish, auto-detect or `--lang tr`
- **Cross-platform** — Windows, macOS, Linux
- **CLI + GUI** — Terminal mode or `--gui` for tkinter interface
- **Full audit trail** — Timestamped logs and directory tree snapshots
- **Automatic deduplication** — When two repos ship the same skill, the higher-category copy wins

### Wiki Pages

| Page | Description |
|------|-------------|
| [Installation](Installation) | Full install guide, prerequisites, profiles, Turkish aliases |
| [Categories](Categories) | All 10 categories with complete repo lists (48 repos) |
| [Command-Reference](Command-Reference) | CLI flags, profiles, Turkish aliases, options |
| [Contributing](Contributing) | How to add repos, quality criteria, reclassification |
| [FAQ](FAQ) | Troubleshooting, common questions, uninstall |

</details>

<a id="tr"></a>

**Agent Beceri Projesi** wiki'sine hoş geldiniz.

Bu proje, **35 üst düzey depodan ~571 SKILL.md dosyasını** **10 işlevsel kategoride** (K1–K10) toplar. Tek bir platformlar arası Python yükleyici (`skills.py`) ile tüm repoları klonlar, her SKILL.md'yi çıkarır, tekilleştirir ve `~/.agents/skills/` altına düzenler — Claude Code, OpenCode, Cursor ve SKILL.md formatını okuyan her ajan tarafından keşfedilmeye hazır.

### Hızlı Başlangıç

```bash
git clone https://github.com/bayraktarozcan/AgentSynapse.git
cd AgentSynapse
python skills.py
```

Bu kadar. Önerilen profil, 35 küratörlü depodan ~571 beceri yükler.

### Profiller

| Profil | Depo | Beceri | Açıklama |
|--------|------|--------|----------|
| `onerilen` (varsayılan) | 35 | ~571 | Küratörlü alt küme — en yüksek kalite |
| `guvenli` | 40 | ~645 | K1–K8, tüm güvenli kategoriler |
| `tumu` | 49 | ~1000 | K9–K10 dahil her şey |

### Özellikler

- **Sıfır bağımlılık** — Sadece Python standart kütüphanesi (pip gerekmez)
- **Çift dilli** — İngilizce & Türkçe, otomatik algılama veya `--lang tr`
- **Platformlar arası** — Windows, macOS, Linux
- **CLI + GUI** — Terminal modu veya `--gui` ile tkinter arayüzü
- **Tam denetim izi** — Zaman damgalı günlükler ve klasör yapısı görüntüleri
- **Otomatik tekilleştirme** — İki depo aynı beceriyi içerdiğinde üst kategorideki kazanır

### Wiki Sayfaları

| Sayfa | Açıklama |
|-------|----------|
| [Kurulum](Installation) | Tam kurulum rehberi, gereksinimler, profiller, Türkçe alias'lar |
| [Kategoriler](Categories) | 10 kategori ve 48 deponun tam listesi |
| [Komut-Referansi](Command-Reference) | CLI flag'leri, profiller, Türkçe alias'lar, seçenekler |
| [Katkida-Bulunma](Contributing) | Depo ekleme, kalite kriterleri, yeniden sınıflandırma |
| [SSS](FAQ) | Sorun giderme, sık sorulan sorular, kaldırma |
