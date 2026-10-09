# AgentSynapse

| <kbd>[🇬🇧 **English**](#en)</kbd> | <kbd>[🇹🇷 **Türkçe**](#tr)</kbd> |
|---|---|

---

<a id="en"></a>

<details open>
<summary><b>English</b></summary>

**571+ curated AI agent skills** from 35 top-tier repositories, organized into 10 functional categories, installable in one command. Built for [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview), [OpenCode](https://opencode.ai), and any agent framework that reads SKILL.md.

[![Skills](https://img.shields.io/badge/skills-571%2B-blue?style=flat-square&color=58a6ff)](https://github.com/bayraktarozcan/AgentSynapse)
[![Repos](https://img.shields.io/badge/repos-35-success?style=flat-square&color=3fb950)](https://github.com/bayraktarozcan/AgentSynapse)
[![Categories](https://img.shields.io/badge/categories-10-purple?style=flat-square&color=bc8cff)](#category-reference)
[![License](https://img.shields.io/badge/license-MIT-yellow?style=flat-square)](LICENSE)

---

## Quickstart

```bash
git clone https://github.com/bayraktarozcan/AgentSynapse.git
cd AgentSynapse

# Recommended -- 571+ curated skills (default)
python skills.py

# Or if Python 3 is installed as python3:
python3 skills.py

# Full trusted suite (K1-K8)
python skills.py trusted

# Everything (including opt-in categories)
python skills.py all

# Just AI skills
python skills.py K2

# Launch graphical interface
python skills.py --gui
```

Skills land in `~/.agents/skills/<name>/SKILL.md` -- auto-discovered by Claude Code and OpenCode.

---

## Requirements

- **Python 3.8+** (stdlib only -- no pip install needed)
- **Git** (for cloning repositories)
- **tkinter** (optional, for `--gui` mode)

---

## Features

- **One-command install** -- clone 34 repos, extract skills, deduplicate, done.
- **10 functional categories** -- Core, AI & LLM, Cloud & Backend, Frontend & UI, Mobile, Security, Testing, Content, Community, Risk.
- **Bilingual** -- English and Turkish interfaces. Auto-detects or `--lang tr`.
- **Cross-platform** -- Windows, macOS, Linux. Single Python file, no dependencies.
- **Trust by default** -- Recommended profile ships verified repos; Community & Risk are opt-in.
- **Automatic dedup** -- when two repos ship the same skill, the higher-category copy wins.
- **Agent-native format** -- all skills are standard SKILL.md. No conversion needed.
- **Full audit trail** -- timestamped logs, tree output per run.
- **Graphical interface** -- `--gui` launches a tkinter installer with profile quick-select.

---

## Usage

### Profiles

| Command | Scope | Repos | Skills (approx) |
|---------|-------|-------|-----------------|
| `python skills.py` | Recommended | 35 | ~571 |
| `python skills.py trusted` | Trusted (K1-K8) | 40 | ~645 |
| `python skills.py all` | All (K1-K10) | 49 | ~1000 |

### Specialization

`skill-specialization.json` maps every skill to a specialization class (C1–C5). The `--profile` flag scopes what stays installed:

| Profile | Classes | Skills |
|---------|---------|--------|
| `temel` | C1, C2 | 227 |
| `dengeli` | C1, C2, C3, first 76 of C4 | 360 |
| `tam` (default) | All C1–C5 | 571 |

After an install with `--profile temel` or `--profile dengeli`, out-of-profile skills are moved to `~/.agents/_quarantine_<profile>_<date>/` (a `_moved-list.txt` is written). Preview with `--dry-run`, inspect via `--list` / `--check`:

```bash
python skills.py --dry-run --profile temel    # preview what would move
python skills.py --check --profile dengeli    # coverage report
python skills.py --list --profile temel       # profile map
```

### Categories

```bash
python skills.py K1          # Core -- languages, tooling
python skills.py K2          # AI & LLM -- agents, RAG, prompting
python skills.py K3          # Cloud & Backend
python skills.py K4          # Frontend & UI
python skills.py K5          # Mobile
python skills.py K6          # Security
python skills.py K7          # Testing
python skills.py K8          # Content
python skills.py K9          # Community (opt-in)
python skills.py K10         # Risk (opt-in)
```

Multiple categories at once:

```bash
python skills.py K2 K4 K6    # AI + Frontend + Security
```

### Options

| Flag | Description |
|------|-------------|
| `--gui` | Launch graphical interface |
| `--lang tr` | Force Turkish language |
| `--lang en` | Force English |
| `--dry-run` | Preview repos without installing |
| `--prefix PATH` | Custom install directory |
| `--profile P` | Enforce specialization profile (temel, dengeli, tam; default tam) |
| `--uninstall` | Remove all installed skills |
| `--check` | Pre-flight environment check (Python, Git, network, disk) |
| `--list` | List available categories |
| `--show-config` | Dump repo registry as JSON |
| `--version` | Show version |
| `--readme` | Show full README |
| `--changelog` | Show changelog |
| `--conduct` | Show code of conduct |
| `--security` | Show security policy |
| `--support` | Show support info |
| `--license` | Show license |
| `--help` | Show help |

### Turkish CLI

```bash
python skills.py --lang tr onerilen      # Onerilen profili yukle
python skills.py --lang tr guvenli       # Guvenli kategorileri yukle
python skills.py --lang tr tumu          # Tumunu yukle
python skills.py --lang tr K2            # Sadece AI kategorisi
python skills.py --lang tr --list        # Kategorileri listele
python skills.py --lang tr --gui         # Grafik arayuzu baslat
```

---

## Category Reference

| Code | Category | Repos | Status |
|------|----------|-------|--------|
| **K1** | Core (languages, tooling, code quality) | 5 | Default |
| **K2** | AI & LLM (agents, RAG, prompting, browser agents) | 9 | Default |
| **K3** | Cloud & Backend (AWS, Vercel, Stripe, Neon, Supabase) | 11 | Default |
| **K4** | Frontend & UI (React, Next.js, Expo, shadcn, WordPress) | 8 | Default |
| **K5** | Mobile (iOS, Android, React Native, Expo) | 1 | Default |
| **K6** | Security (review, scanning, hardening) | 2 | Default |
| **K7** | Testing (E2E, unit, visual regression) | 1 | Default |
| **K8** | Content (writing, docs, editing, publishing) | 2 | Default |
| **K9** | Community (third-party, lower star counts) | 5 | Opt-in |
| **K10** | Risk (experimental, unmaintained) | 4 | Opt-in |

---

## How It Works

```
git clone --depth 1 --single-branch <repo> -> parse SKILL.md frontmatter -> deduplicate -> copy to ~/.agents/skills/<name>/
```

1. **Clone** -- each repo is shallow-cloned (single branch only) to a temp directory.
2. **Parse** -- every `SKILL.md` is read for its `name:` field and subdirectory path.
3. **Deduplicate** -- if two repos share a skill name, the higher-category (higher K number) copy wins.
4. **Install** -- skills land in `~/.agents/skills/<name>/SKILL.md`.

---

## Project Structure

```
AgentSynapse/
+-- skills.py            # The entire project -- CLI + GUI, bilingual, self-contained
+-- README.md            # This file (bilingual EN/TR)
+-- CHANGELOG.md         # Bilingual changelog
+-- CODE_OF_CONDUCT.md   # Bilingual code of conduct
+-- SECURITY.md          # Bilingual security policy
+-- SUPPORT.md           # Bilingual support info
+-- CONTRIBUTING.md      # Bilingual contributing guide
+-- LICENSE              # MIT License
+-- <run artifacts>      # Timestamped install logs and trees (auto-generated; paths per `.gitignore`)
+-- skill-specialization.json # Specialization manifest (571 skills, C1-C5)
+-- .github/             # Issue templates, funding, dependabot
```

---

## Development

```bash
# Clone repo
git clone https://github.com/bayraktarozcan/AgentSynapse.git
cd AgentSynapse

# Run regression
python skills.py recommended           # 35 repos, ~571 skills
python skills.py trusted               # 40 repos, ~645 skills
python skills.py all                   # 49 repos, ~1000 skills
```

### Adding a Repository

1. Edit the `REPOS` dict in `skills.py` -- add repo entry under the appropriate category.
2. Run `python skills.py K<category>` to verify it installs.

### Adding a Language

Edit the `S` dict in `skills.py` -- add a new language key and translate all strings.

---

## Agent Compatibility

| Agent | Global Path | Native Support |
|-------|-------------|----------------|
| **Claude Code** | `~/.agents/skills/` | Full |
| **OpenCode** | `~/.agents/skills/` | Full |
| **Gemini CLI** | `~/.config/gemini/` | Researching |
| **Cursor** | `.cursor/rules/` (`.mdc`) | Different format |

---

## License

MIT -- see [LICENSE](LICENSE).

---

## Community

- [Issues](https://github.com/bayraktarozcan/AgentSynapse/issues) -- bugs, feature requests, questions.
- [Discussions](https://github.com/bayraktarozcan/AgentSynapse/discussions) -- ideas, showcase, help.

Built for the AI agent community.

</details>

<a id="tr"></a>

**571'den fazla küratörlü AI ajan becerisi**, 35 üst düzey depodan alınmış, 10 işlevsel kategoriye ayrılmış, tek komutla yüklenebilir. Claude Code, OpenCode ve SKILL.md okuyan her ajan çerçevesi için üretilmiştir.

[![Skills](https://img.shields.io/badge/skills-571%2B-blue?style=flat-square&color=58a6ff)](https://github.com/bayraktarozcan/AgentSynapse)
[![Repos](https://img.shields.io/badge/repos-35-success?style=flat-square&color=3fb950)](https://github.com/bayraktarozcan/AgentSynapse)
[![Categories](https://img.shields.io/badge/categories-10-purple?style=flat-square&color=bc8cff)](#category-reference)
[![License](https://img.shields.io/badge/license-MIT-yellow?style=flat-square)](LICENSE)

---

## Hızlı Başlangıç

```bash
git clone https://github.com/bayraktarozcan/AgentSynapse.git
cd AgentSynapse

# Önerilen -- 571+ küratörlü beceri (varsayılan)
python skills.py

# Veya Python 3, python3 olarak yüklendiyse:
python3 skills.py

# Tam güvenli suite (K1-K8)
python skills.py trusted

# Her şey (opsiyonel kategoriler dahil)
python skills.py all

# Sadece AI becerileri
python skills.py K2

# Grafik arayüzü başlat
python skills.py --gui
```

Beceriler `~/.agents/skills/<name>/SKILL.md` konumuna kurulur -- Claude Code ve OpenCode tarafından otomatik keşfedilir.

---

## Gereksinimler

- **Python 3.8+** (sadece standart kütüphane -- pip gerekmez)
- **Git** (depoları klonlamak için)
- **tkinter** (opsiyonel, `--gui` modu için)

---

## Özellikler

- **Tek komutla kurulum** -- 34 depoyu klonla, becerileri çıkar, tekrarları temizle, bitti.
- **10 işlevsel kategori** -- Çekirdek, AI & LLM, Bulut & Backend, Ön yüz & UI, Mobil, Güvenlik, Test, İçerik, Topluluk, Risk.
- **İki dilli** -- İngilizce ve Türkçe. Otomatik algılama veya `--lang tr`.
- **Çapraz platform** -- Windows, macOS, Linux. Tek Python dosyası, bağımlılık yok.
- **Varsayılan olarak güvenilir** -- Önerilen profili yalnızca doğrulanmış depolar içerir; Topluluk ve Risk opsiyoneldir.
- **Otomatik tekrar temizleme** -- iki depo aynı beceriye sahipse, üst kategorideki (yüksek K numarası) kazanır.
- **Ajan-yerel formatı** -- tüm beceriler standart SKILL.md formatındadır. Dönüşüm gerekmez.
- **Tam denetim izi** -- zaman damgalı günlükler, çalıştırma başına klasör ağacı.
- **Grafik arayüz** -- `--gui` ile tkinter yükleyici, profil hızlı seçimi.

---

## Kullanım

### Profiller

| Komut | Kapsam | Depo | Beceri (yaklaşık) |
|-------|--------|------|--------------------|
| `python skills.py` | Önerilen | 35 | ~571 |
| `python skills.py trusted` | Güvenli (K1-K8) | 40 | ~645 |
| `python skills.py all` | Tümü (K1-K10) | 49 | ~1000 |

### Uzmanlaşma

`skill-specialization.json`, her beceriyi bir uzmanlaşma sınıfına (C1–C5) eşler. `--profile` bayrağı neyin kurulu kalacağını kapsamlar:

| Profil | Sınıflar | Beceri |
|--------|----------|--------|
| `temel` | C1, C2 | 227 |
| `dengeli` | C1, C2, C3, C4'ün ilk 76'sı | 360 |
| `tam` (varsayılan) | Tüm C1–C5 | 571 |

`--profile temel` veya `--profile dengeli` ile yapılan bir kurulumun ardından profil dışı beceriler `~/.agents/_quarantine_<profil>_<tarih>/` klasörüne taşınır (`_moved-list.txt` yazılır). `--dry-run` ile önizleyin, `--list` / `--check` ile inceleyin:

```bash
python skills.py --dry-run --profile temel    # neyin taşınacağını önizle
python skills.py --check --profile dengeli    # kapsam raporu
python skills.py --list --profile temel       # profil haritası
```

### Kategoriler

```bash
python skills.py K1          # Çekirdek -- diller, araçlar
python skills.py K2          # AI & LLM -- ajanlar, RAG, yönlendirme
python skills.py K3          # Bulut & Backend
python skills.py K4          # Ön yüz & UI
python skills.py K5          # Mobil
python skills.py K6          # Güvenlik
python skills.py K7          # Test
python skills.py K8          # İçerik
python skills.py K9          # Topluluk (opsiyonel)
python skills.py K10         # Risk (opsiyonel)
```

### Seçenekler

| Bayrak | Açıklama |
|--------|----------|
| `--gui` | Grafik arayüzü başlat |
| `--lang tr` | Türkçe'yi zorla |
| `--lang en` | İngilizce'yi zorla |
| `--dry-run` | Repoları kurmadan önizle |
| `--prefix PATH` | Özel kurulum dizini |
| `--profile P` | Uzmanlaşma profilini uygula (temel, dengeli, tam; varsayılan tam) |
| `--uninstall` | Tüm becerileri kaldır |
| `--check` | Ön uçuş ortam kontrolü (Python, Git, ağ, disk) |
| `--list` | Kategorileri listele |
| `--show-config` | Repo kaydını JSON olarak göster |
| `--version` | Sürümü göster |
| `--readme` | Tam README'yi göster |
| `--changelog` | Değişiklik günlüğünü göster |
| `--conduct` | Davranış kurallarını göster |
| `--security` | Güvenlik politikasını göster |
| `--support` | Destek bilgilerini göster |
| `--license` | Lisansı göster |
| `--help` | Yardım mesajını göster |

### Türkçe CLI

```bash
python skills.py --lang tr onerilen      # Önerilen profili yükle
python skills.py --lang tr guvenli       # Güvenli kategorileri yükle
python skills.py --lang tr tumu          # Tümünü yükle
python skills.py --lang tr K2            # Sadece AI kategorisi
python skills.py --lang tr --list        # Kategorileri listele
python skills.py --lang tr --gui         # Grafik arayüzü başlat
```

---

## Kategori Referansı

| Kod | Kategori | Depo | Durum |
|-----|----------|------|-------|
| **K1** | Çekirdek (diller, araçlar, kod kalitesi) | 5 | Varsayılan |
| **K2** | AI & LLM (ajanlar, RAG, yönlendirme, tarayıcı ajanları) | 9 | Varsayılan |
| **K3** | Bulut & Backend (AWS, Vercel, Stripe, Neon, Supabase) | 11 | Varsayılan |
| **K4** | Ön yüz & UI (React, Next.js, Expo, shadcn, WordPress) | 8 | Varsayılan |
| **K5** | Mobil (iOS, Android, React Native, Expo) | 1 | Varsayılan |
| **K6** | Güvenlik (inceleme, tarama, sağlamlaştırma) | 2 | Varsayılan |
| **K7** | Test (E2E, birim, görsel regresyon) | 1 | Varsayılan |
| **K8** | İçerik (yazma, dokümantasyon, düzenleme, yayıncılık) | 2 | Varsayılan |
| **K9** | Topluluk (üçüncü taraf, düşük yıldız sayısı) | 5 | Opsiyonel |
| **K10** | Risk (deneysel, bakımı yapılmayan) | 4 | Opsiyonel |

---

## Nasıl Çalışır

```
git clone --depth 1 --single-branch <repo> -> SKILL.md ön yüzünü ayrıştır -> tekrarları temizle -> ~/.agents/skills/<name>/ konumuna kopyala
```

1. **Klonla** -- her depo geçici dizine --depth 1 --single-branch ile klonlanır (yalnızca tek dal).
2. **Ayrıştır** -- her SKILL.md dosyasının `name:` alanı ve alt dizin yolu okunur.
3. **Tekrarları temizle** -- iki depo aynı beceri adına sahipse, üst kategorideki (yüksek K) kazanır.
4. **Kur** -- beceriler `~/.agents/skills/<name>/SKILL.md` konumuna kopyalanır.

---

## Proje Yapısı

```
AgentSynapse/
+-- skills.py            # Tüm proje -- CLI + GUI, iki dilli, kendi kendine yeter
+-- README.md            # Bu dosya (çift dilli EN/TR)
+-- CHANGELOG.md         # Çift dilli değişiklik günlüğü
+-- CODE_OF_CONDUCT.md   # Çift dilli davranış kuralları
+-- SECURITY.md          # Çift dilli güvenlik politikası
+-- SUPPORT.md           # Çift dilli destek bilgileri
+-- CONTRIBUTING.md      # Çift dilli katkı rehberi
+-- LICENSE              # MIT Lisansı
+-- <çalışma yapıtları>  # Zaman damgalı kurulum günlükleri ve ağaçları (otomatik; yollar `.gitignore` dosyasına göre)
+-- skill-specialization.json # Uzmanlaşma manifesti (571 beceri, C1-C5)
+-- .github/             # Issue şablonları, finansman, dependabot
```

---

## Geliştirme

```bash
# Depoyu klonla
git clone https://github.com/bayraktarozcan/AgentSynapse.git
cd AgentSynapse

# Regresyon testi
python skills.py recommended           # 35 depo, ~571 beceri
python skills.py trusted               # 40 depo, ~645 beceri
python skills.py all                   # 49 depo, ~1000 beceri
```

### Depo Ekleme

1. `skills.py` içindeki `REPOS` sözlüğünü düzenleyin -- uygun kategori altına depo girişi ekleyin.
2. `python skills.py K<kategori>` ile kurulumu doğrulayın.

### Dil Ekleme

`skills.py` içindeki `S` sözlüğünü düzenleyin -- yeni bir dil anahtarı ekleyin ve tüm dizeleri çevirin.

---

## Ajan Uyumluluğu

| Ajan | Genel Yol | Yerel Destek |
|------|-----------|--------------|
| **Claude Code** | `~/.agents/skills/` | Tam |
| **OpenCode** | `~/.agents/skills/` | Tam |
| **Gemini CLI** | `~/.config/gemini/` | Araştırılıyor |
| **Cursor** | `.cursor/rules/` (`.mdc`) | Farklı format |

---

## Lisans

MIT -- detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## Topluluk

- [Sorunlar](https://github.com/bayraktarozcan/AgentSynapse/issues) -- hatalar, özellik talepleri, sorular.
- [Tartışmalar](https://github.com/bayraktarozcan/AgentSynapse/discussions) -- fikirler, vitrin, yardım.

AI ajan topluluğu için üretilmiştir.
