# Installation Guide — Kurulum Kılavuzu

| <kbd>[🇬🇧 **English**](#en)</kbd> | <kbd>[🇹🇷 **Türkçe**](#tr)</kbd> |

<a id="en"></a>
<details open>
<summary>English</summary>

## Prerequisites

| Requirement | Check command | Notes |
|-------------|---------------|-------|
| Python 3.8+ | `python --version` | If not installed, download from [python.org](https://python.org) |
| Git | `git --version` | If not installed, download from [git-scm.com](https://git-scm.com) |
| tkinter (optional) | — | Needed only for `--gui` mode. Included with Python on Windows & macOS. Linux: `sudo apt install python3-tk` |

## Installation Steps

### 1. Clone the repository

```bash
git clone https://github.com/bayraktarozcan/AgentSynapse.git
cd AgentSynapse
```

### 2. Run the installer

```bash
python skills.py
```

This installs the **recommended** profile (35 repos, ~572 skills). Output goes to `~/.agents/skills/`.

### Profiles

| Command | What it installs | Repos | Skills |
|---------|-----------------|-------|--------|
| `python skills.py` | Recommended — curated subset | 35 | ~572 |
| `python skills.py trusted` | All trusted (K1–K8) | 40 | ~646 |
| `python skills.py all` | Everything (K1–K10) | 49 | ~1001 |
| `python skills.py K2` | Single category (AI & LLM) | 9 | varies |
| `python skills.py K1 K3 K5` | Multiple categories | varies | varies |

### Turkish Aliases

| Turkish command | Equivalent |
|----------------|------------|
| `python skills.py onerilen` | `python skills.py` (recommended) |
| `python skills.py guvenli` | `python skills.py trusted` |
| `python skills.py tumu` | `python skills.py all` |
| `python skills.py tum` | `python skills.py all` |

### GUI Mode

```bash
python skills.py --gui
```

Launches a tkinter interface with:
- Category checkboxes (toggle each K1–K10)
- Profile quick-select buttons (Recommended / Trusted / All)
- Progress bar showing installation progress
- Live scrolled log output
- Language toggle button (English / Türkçe)

### Language Selection

- **Auto-detect**: The installer reads the `LANG` or `LC_ALL` environment variable. If it starts with `tr`, Turkish is used.
- **Force a language**: `python skills.py --lang tr` or `python skills.py --lang en`
- **GUI toggle**: Click the language button in the bottom-right corner of the GUI window.

### Documentation Flags

All documentation is available at runtime without opening separate files:

| Flag | Shows |
|------|-------|
| `--help` | Help message with all options |
| `--version` | Version string |
| `--dry-run` | Preview repos without installing |
| `--prefix PATH` | Custom install directory |
| `--uninstall` | Remove all installed skills |
| `--check` | Pre-flight environment check (Python, Git, network, disk) |
| `--list` | List all available categories with descriptions |
| `--show-config` | Dump the embedded repo registry as JSON |
| `--readme` | Display README.md (bilingual) |
| `--changelog` | Display CHANGELOG.md (bilingual) |
| `--conduct` | Display CODE_OF_CONDUCT.md (bilingual) |
| `--security` | Display SECURITY.md (bilingual) |
| `--support` | Display SUPPORT.md (bilingual) |
| `--license` | Display LICENSE |

### Pre-Flight Check

Before installing, run a pre-flight check to verify your environment:

```bash
python skills.py --check
```

This checks:
- **Python version** — requires 3.8+
- **Git availability** — searches common install paths if not in `PATH`; shows OS-specific install hint if missing
- **Network connectivity** — pings `https://github.com` with a 10-second timeout
- **Disk space** — warns if less than 500 MB free
- **Skills directory** — auto-creates `~/.agents/skills/` if missing

### Dry Run

Preview which repositories will be installed without actually cloning anything:

```bash
python skills.py --dry-run
python skills.py --dry-run all
python skills.py --dry-run K2 K4
```

### Custom Install Directory

Install skills to a custom location instead of `~/.agents/skills/`:

```bash
python skills.py --prefix /path/to/custom/dir
```

### Uninstall

Remove all installed skills:

```bash
python skills.py --uninstall
```

You will be prompted for confirmation before deletion.

### Proactive Error Handling

The installer automatically handles common issues:

| Issue | Handling |
|-------|----------|
| Git not found | Searches common paths (`C:\Program Files\Git\cmd\git.exe`, `/usr/local/bin/git`, etc.); shows OS-specific install hint (`apt install git`, `brew install git`, `winget install Git.Git`) |
| Clone failure | Auto-retries up to 3 times with 2-second delay |
| Permission denied | Auto-creates `~/.agents/skills/` with `mkdir -p` equivalent |
| Skills directory exists | Safe re-install; deduplicates correctly |
| Missing subpath | Reports error per repo; continues with remaining repos |

### Output Files

All generated files are created in your **current working directory** (where you run `skills.py`), not in the project directory. This ensures global compatibility regardless of where you cloned the repo.

| File | Description |
|------|-------------|
| `Logs/skills-install_YYYY-MM-DD_HH-MM-SS.log` | Full installation log with timestamps, errors, and warnings |
| `skills-tree_YYYY-MM-DD_HH-MM-SS.txt` | Directory tree of `~/.agents/` showing installed skills structure |

### Verification

After installation, verify the skills are in place:

```bash
ls ~/.agents/skills/          # macOS / Linux
dir %USERPROFILE%\.agents\skills  # Windows
```

Each subdirectory should contain at least one `SKILL.md` file.

</details>

<a id="tr"></a>

## Gereksinimler

| Gereksinim | Kontrol komutu | Notlar |
|------------|----------------|--------|
| Python 3.8+ | `python --version` | Yüklü değilse [python.org](https://python.org) adresinden indirin |
| Git | `git --version` | Yüklü değilse [git-scm.com](https://git-scm.com) adresinden indirin |
| tkinter (isteğe bağlı) | — | Yalnızca `--gui` modu için gerekli. Windows ve macOS'ta Python ile gelir. Linux: `sudo apt install python3-tk` |

## Kurulum Adımları

### 1. Depoyu klonlayın

```bash
git clone https://github.com/bayraktarozcan/AgentSynapse.git
cd AgentSynapse
```

### 2. Yükleyiciyi çalıştırın

```bash
python skills.py
```

Bu, **önerilen** profili (35 depo, ~572 beceri) yükler. Çıktı `~/.agents/skills/` klasörüne gider.

### Profiller

| Komut | Ne yükler | Depo | Beceri |
|-------|-----------|------|--------|
| `python skills.py` | Önerilen — küratörlü alt küme | 35 | ~572 |
| `python skills.py guvenli` | Tüm güvenli (K1–K8) | 40 | ~646 |
| `python skills.py tumu` | Her şey (K1–K10) | 49 | ~1001 |
| `python skills.py K2` | Tek kategori (AI & LLM) | 9 | değişir |
| `python skills.py K1 K3 K5` | Birden çok kategori | değişir | değişir |

### Türkçe Alias'lar

| Türkçe komut | Eşdeğeri |
|--------------|----------|
| `python skills.py onerilen` | `python skills.py` (önerilen) |
| `python skills.py guvenli` | `python skills.py trusted` |
| `python skills.py tumu` | `python skills.py all` |
| `python skills.py tum` | `python skills.py all` |

### GUI Modu

```bash
python skills.py --gui
```

tkinter arayüzünü başlatır:
- Kategori onay kutuları (her K1–K10'u açıp kapatma)
- Profil hızlı seçim düğmeleri (Önerilen / Güvenli / Tümü)
- İlerleme çubuğu
- Canlı kaydırılabilir günlük çıktısı
- Dil değiştirme düğmesi (English / Türkçe)

### Dil Seçimi

- **Otomatik algılama**: Yükleyici, `LANG` veya `LC_ALL` ortam değişkenini okur. `tr` ile başlıyorsa Türkçe kullanılır.
- **Dili zorlama**: `python skills.py --lang tr` veya `python skills.py --lang en`
- **GUI değiştirme**: Pencere sağ alt köşesindeki dil düğmesine tıklayın.

### Dokümantasyon Flag'leri

Tüm dokümantasyon çalışma zamanında ayrı dosya açmadan kullanılabilir:

| Flag | Gösterir |
|------|----------|
| `--help` | Tüm seçeneklerle yardım mesajı |
| `--version` | Sürüm numarası |
| `--dry-run` | Repoları kurmadan önizle |
| `--prefix PATH` | Özel kurulum dizini |
| `--uninstall` | Tüm becerileri kaldır |
| `--check` | Ön uçuş ortam kontrolü (Python, Git, ağ, disk) |
| `--list` | Tüm kategorileri açıklamalarıyla listeler |
| `--show-config` | Repo kaydını JSON olarak döker |
| `--readme` | README.md'yi gösterir (çift dilli) |
| `--changelog` | CHANGELOG.md'yi gösterir (çift dilli) |
| `--conduct` | CODE_OF_CONDUCT.md'yi gösterir (çift dilli) |
| `--security` | SECURITY.md'yi gösterir (çift dilli) |
| `--support` | SUPPORT.md'yi gösterir (çift dilli) |
| `--license` | LICENSE'ı gösterir |

### Ön Uçuş Kontrolü

Kurulumdan önce ortamınızı kontrol etmek için:

```bash
python skills.py --check
```

Şunları kontrol eder:
- **Python sürümü** — 3.8+ gerektirir
- **Git kullanılabilirliği** — `PATH`'te yoksa yaygın kurulum yollarını arar; eksikse işletim sistemine özel kurulum ipucu gösterir
- **Ağ bağlantısı** — 10 saniye zaman aşımı ile `https://github.com` adresine ping atar
- **Disk alanı** — 500 MB'den az boş alan varsa uyarır
- **Beceriler dizini** — eksikse `~/.agents/skills/` otomatik oluşturulur

### Kuru Çalıştırma

Hiçbir şey klonlamadan hangi depoların kurulacağını önizleyin:

```bash
python skills.py --dry-run
python skills.py --dry-run tumu
python skills.py --dry-run K2 K4
```

### Özel Kurulum Dizini

Becerileri `~/.agents/skills/` yerine özel bir konuma kurun:

```bash
python skills.py --prefix /ozel/dizin/yolu
```

### Kaldırma

Yüklenen tüm becerileri kaldırın:

```bash
python skills.py --uninstall
```

Silme işleminden önce onay istenecektir.

### Proaktif Hata Yönetimi

Yükleyici, yaygın sorunları otomatik olarak yönetir:

| Sorun | Yönetim |
|-------|---------|
| Git bulunamadı | Yaygın yolları arar (`C:\Program Files\Git\cmd\git.exe`, `/usr/local/bin/git`, vb.); işletim sistemine özel kurulum ipucu gösterir (`apt install git`, `brew install git`, `winget install Git.Git`) |
| Klonlama hatası | 2 saniye gecikmeyle 3 kez otomatik dener |
| İzin reddedildi | `~/.agents/skills/` otomatik oluşturulur |
| Beceriler dizini mevcut | Güvenli yeniden kurulum; tekrarlar doğru şekilde temizlenir |
| Eksik alt klasör | Depo başına hata bildirir; kalan depolarla devam eder |

### Çıktı Dosyaları

Tüm oluşturulan dosyalar **geçerli çalışma dizininizde** (`skills.py`'yi çalıştırdığınız yerde) oluşturulur, proje dizininde değil. Bu, repoyu nereye klonlarsanız klonlayın global uyumluluk sağlar.

| Dosya | Açıklama |
|-------|----------|
| `Logs/skills-install_YYYY-MM-DD_HH-MM-SS.log` | Zaman damgalı tam kurulum günlüğü, hatalar ve uyarılar |
| `skills-tree_YYYY-MM-DD_HH-MM-SS.txt` | `~/.agents/` klasör yapısını gösteren ağaç görünümü |

### Doğrulama

Kurulumdan sonra becerilerin yerinde olduğunu doğrulayın:

```bash
ls ~/.agents/skills/          # macOS / Linux
dir %USERPROFILE%\.agents\skills  # Windows
```

Her alt klasör en az bir `SKILL.md` dosyası içermelidir.
