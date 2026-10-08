# Command Reference — Komut Referansı

| <kbd>[🇬🇧 **English**](#en)</kbd> | <kbd>[🇹🇷 **Türkçe**](#tr)</kbd> |

<a id="en"></a>
<details open>
<summary>English</summary>

## Usage

```
python skills.py [profile|category...] [options]
```

## Profiles

If no argument is given, the **recommended** profile is used.

| Argument | Effect | Repos | Skills |
|----------|--------|:-----:|:------:|
| _(none)_ | Recommended — curated subset, best quality | 35 | ~571 |
| `recommended` | Same as default | 35 | ~571 |
| `trusted` | All trusted categories K1–K8 | 40 | ~645 |
| `all` | Everything including K9–K10 | 49 | ~1000 |

## Single Categories

Install a specific category by its code:

| Argument | Category | Repos |
|----------|----------|:-----:|
| `K1` | Core | 5 |
| `K2` | AI & LLM | 9 |
| `K3` | Cloud & Backend | 11 |
| `K4` | Frontend & UI | 8 |
| `K5` | Mobile | 1 |
| `K6` | Security | 2 |
| `K7` | Testing | 1 |
| `K8` | Content | 2 |
| `K9` | Community | 5 |
| `K10` | Risk | 4 |

Multiple categories can be combined: `python skills.py K1 K2 K3`

## Turkish Aliases

| Turkish | English Equivalent | Effect |
|---------|-------------------|--------|
| `onerilen` | `recommended` | Default profile |
| `guvenli` | `trusted` | K1–K8 trusted categories |
| `tumu` | `all` | All categories including K9–K10 |
| `tum` | `all` | All categories (shorthand) |

## Options

| Flag | Description |
|------|-------------|
| `--gui` | Launch tkinter graphical interface |
| `--lang tr` | Force Turkish language |
| `--lang en` | Force English language |
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
| `--license` | Display LICENSE (MIT) |
| `--help` | Show help message with all options |
| `--version` | Show version string |

## Examples

```bash
# Recommended install (default)
python skills.py

# GUI mode with Turkish interface
python skills.py --gui --lang tr

# Install all AI-related categories
python skills.py K2 K3 K6

# Show documentation without installing
python skills.py --readme
python skills.py --changelog
python skills.py --license

# Dump configuration
python skills.py --show-config > config.json
```

## Exit Codes

| Code | Meaning |
|:----:|---------|
| 0 | Success |
| 1 | Error (git not found, clone failed, etc.) |

## Environment Variables

| Variable | Effect |
|----------|--------|
| `LANG` | Language detection (auto: `tr` prefix → Turkish) |
| `LC_ALL` | Alternative language detection variable |

</details>

<a id="tr"></a>

## Kullanım

```
python skills.py [profil|kategori...] [seçenekler]
```

## Profiller

Hiçbir argüman verilmezse **önerilen** profil kullanılır.

| Argüman | Etki | Depo | Beceri |
|---------|------|:----:|:------:|
| _(yok)_ | Önerilen — küratörlü alt küme, en iyi kalite | 35 | ~571 |
| `onerilen` | Varsayılan ile aynı | 35 | ~571 |
| `guvenli` | Tüm güvenli kategoriler K1–K8 | 40 | ~645 |
| `tumu` | K9–K10 dahil her şey | 49 | ~1000 |

## Tek Kategoriler

Koduna göre belirli bir kategoriyi yükleyin:

| Argüman | Kategori | Depo |
|---------|----------|:----:|
| `K1` | Temel | 5 |
| `K2` | AI & LLM | 9 |
| `K3` | Bulut & Arka Uç | 11 |
| `K4` | Ön Yüz & Arayüz | 8 |
| `K5` | Mobil | 1 |
| `K6` | Güvenlik | 2 |
| `K7` | Test | 1 |
| `K8` | İçerik | 2 |
| `K9` | Topluluk | 5 |
| `K10` | Risk | 4 |

Birden çok kategori birleştirilebilir: `python skills.py K1 K2 K3`

## Türkçe Alias'lar

| Türkçe | İngilizce Karşılığı | Etki |
|--------|---------------------|------|
| `onerilen` | `recommended` | Varsayılan profil |
| `guvenli` | `trusted` | K1–K8 güvenli kategoriler |
| `tumu` | `all` | K9–K10 dahil tüm kategoriler |
| `tum` | `all` | Tümü (kısa yazım) |

## Seçenekler

| Flag | Açıklama |
|------|----------|
| `--gui` | tkinter grafik arayüzünü başlat |
| `--lang tr` | Türkçe dilini zorla |
| `--lang en` | İngilizce dilini zorla |
| `--dry-run` | Repoları kurmadan önizle |
| `--prefix PATH` | Özel kurulum dizini |
| `--uninstall` | Tüm becerileri kaldır |
| `--check` | Ön uçuş ortam kontrolü (Python, Git, ağ, disk) |
| `--list` | Tüm kategorileri açıklamalarıyla listele |
| `--show-config` | Gömülü repo kaydını JSON olarak dök |
| `--readme` | README.md'yi göster (çift dilli) |
| `--changelog` | CHANGELOG.md'yi göster (çift dilli) |
| `--conduct` | CODE_OF_CONDUCT.md'yi göster (çift dilli) |
| `--security` | SECURITY.md'yi göster (çift dilli) |
| `--support` | SUPPORT.md'yi göster (çift dilli) |
| `--license` | LICENSE'ı göster (MIT) |
| `--help` | Tüm seçeneklerle yardım mesajını göster |
| `--version` | Sürüm numarasını göster |

## Örnekler

```bash
# Önerilen kurulum (varsayılan)
python skills.py

# Türkçe arayüzlü GUI modu
python skills.py --gui --lang tr

# Tüm AI ile ilgili kategorileri yükle
python skills.py K2 K3 K6

# Kurulum yapmadan dokümantasyon göster
python skills.py --readme
python skills.py --changelog
python skills.py --license

# Yapılandırmayı dök
python skills.py --show-config > config.json
```

## Çıkış Kodları

| Kod | Anlamı |
|:---:|--------|
| 0 | Başarılı |
| 1 | Hata (git bulunamadı, klonlama başarısız, vb.) |

## Ortam Değişkenleri

| Değişken | Etki |
|----------|------|
| `LANG` | Dil algılama (otomatik: `tr` öneki → Türkçe) |
| `LC_ALL` | Alternatif dil algılama değişkeni |
