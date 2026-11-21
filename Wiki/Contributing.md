# Contributing — Katkıda Bulunma

| <kbd>[🇬🇧 **English**](#en)</kbd> | <kbd>[🇹🇷 **Türkçe**](#tr)</kbd> |

<a id="en"></a>
<details open>
<summary>English</summary>

Contributions are welcome! Here's how you can help improve AgentSynapse.

## Adding a Repository

If you know a repository that contains useful `SKILL.md` files for AI agents, open a pull request against `skills.py` and add it to the appropriate category.

### Step-by-Step

1. **Find the right category** in the `REPOS` dict inside `skills.py` (lines 301–437). Categories are K1–K10.
2. **Add your repo entry** to the `repos` list of that category:

```python
{
    "id": "K4",
    "name": "Frontend & UI",
    "description": "User interfaces, design systems...",
    "repos": [
        # Add here:
        {"repo": "owner/repo-name"},
        # With subpath if skills are in a subdirectory:
        {"repo": "owner/repo-name", "subpath": "path/to/skills"},
    ],
}
```

3. **Mark as recommended** (optional, only if the repo meets quality criteria):

```python
{"repo": "owner/repo-name", "recommended": True},
```

4. **Run validation**:

```bash
python -c "import py_compile; py_compile.compile('skills.py', doraise=True); print('OK')"
python skills.py --list
```

5. **Submit a pull request** with a description of what the repository adds.

## Quality Criteria for `recommended: true`

| Criterion | Requirement |
|-----------|-------------|
| GitHub stars | 100+ stars |
| Maintenance | Active — updated within the last 6 months |
| Skill format | Valid SKILL.md files following the standard format |
| Safety | No harmful, malicious, or deceptive content |
| Licensing | Clear open-source license (MIT, Apache 2.0, etc.) |
| Documentation | Clear description of what each skill does |

## Proposing a Reclassification

If you believe a skill or repository belongs in a different category, open a GitHub issue with:

- **Current classification**: Which category it's in now
- **Proposed classification**: Which category it should move to
- **Reasoning**: Why the move improves organization

## Adding Wiki Pages

The wiki content lives in the `Wiki/` directory at the project root. Each page must be **bilingual** (English and Turkish) using the `<details>` collapsible pattern:

```markdown
# Page Title

| <kbd>[🇬🇧 **English**](#en)</kbd> | <kbd>[🇹🇷 **Türkçe**](#tr)</kbd> |

<a id="en"></a>
<details open>
<summary>English</summary>

English content here...

</details>

<a id="tr"></a>

Türkçe içerik burada...

</details>
```

## Code Style

- **Python**: Follow PEP 8. Zero external dependencies (stdlib only).
- **Markdown**: Bilingual with collapsible `<details>` sections. Language toggle at the top.
- **Commits**: Use conventional commits (`feat:`, `fix:`, `docs:`, `refactor:`, etc.).

## Reporting Issues

Report bugs, feature requests, or questions via [GitHub Issues](https://github.com/bayraktarozcan/AgentSynapse/issues).

When reporting a bug, include:
- Your operating system (Windows / macOS / Linux)
- Python version (`python --version`)
- Git version (`git --version`)
- The full command you ran (with `--lang tr` if applicable)
- Any error messages from the log file

</details>

<a id="tr"></a>

Katkılarınız memnuniyetle karşılanır! Agent Beceri Projesi'ni iyileştirmek için nasıl yardımcı olabileceğiniz aşağıda açıklanmıştır.

## Depo Ekleme

AI ajanları için yararlı `SKILL.md` dosyaları içeren bir depo biliyorsanız, `skills.py` dosyasına karşı bir çekme talebi (pull request) açın ve uygun kategoriye ekleyin.

### Adım Adım

1. **Doğru kategoriyi bulun**: `skills.py` içindeki `REPOS` sözlüğünde (satır 301–437). Kategoriler K1–K10'dur.
2. **Depo girişinizi ekleyin** o kategorinin `repos` listesine:

```python
{
    "id": "K4",
    "name": "Ön Yüz & Arayüz",
    "description": "Kullanıcı arayüzleri, tasarım sistemleri...",
    "repos": [
        # Buraya ekleyin:
        {"repo": "sahip/depo-adi"},
        # Alt klasör varsa:
        {"repo": "sahip/depo-adi", "subpath": "beceriler/yolu"},
    ],
}
```

3. **Önerilen olarak işaretleyin** (isteğe bağlı, yalnızca depo kalite kriterlerini karşılıyorsa):

```python
{"repo": "sahip/depo-adi", "recommended": True},
```

4. **Doğrulamayı çalıştırın**:

```bash
python -c "import py_compile; py_compile.compile('skills.py', doraise=True); print('TAMAM')"
python skills.py --list
```

5. **Bir çekme talebi gönderin** ve deponun ne eklediğini açıklayın.

## `recommended: true` İçin Kalite Kriterleri

| Kriter | Gereklilik |
|--------|------------|
| GitHub yıldızları | 100+ yıldız |
| Bakım | Aktif — son 6 ay içinde güncellenmiş |
| Beceri formatı | Standart formatta geçerli SKILL.md dosyaları |
| Güvenlik | Zararlı, kötü niyetli veya aldatıcı içerik yok |
| Lisanslama | Açık kaynak lisans (MIT, Apache 2.0, vb.) |
| Dokümantasyon | Her becerinin ne yaptığına dair net açıklama |

## Yeniden Sınıflandırma Önerme

Bir becerinin veya deponun farklı bir kategoride olması gerektiğini düşünüyorsanız, bir GitHub issues açın:

- **Mevcut sınıflandırma**: Şu anda hangi kategoride
- **Önerilen sınıflandırma**: Hangi kategoriye taşınmalı
- **Gerekçe**: Taşımanın organizasyonu neden iyileştirdiği

## Wiki Sayfası Ekleme

Wiki içeriği, proje kökündeki `Wiki/` dizininde bulunur. Her sayfa, `<details>` daraltılabilir deseni kullanılarak **çift dilli** (İngilizce ve Türkçe) olmalıdır:

```markdown
# Sayfa Başlığı

| <kbd>[🇬🇧 **English**](#en)</kbd> | <kbd>[🇹🇷 **Türkçe**](#tr)</kbd> |

<a id="en"></a>
<details open>
<summary>English</summary>

İngilizce içerik burada...

</details>

<a id="tr"></a>

Türkçe içerik burada...

</details>
```

## Kod Stili

- **Python**: PEP 8'i takip edin. Sıfır harici bağımlılık (yalnızca standart kütüphane).
- **Markdown**: Daraltılabilir `<details>` bölümleriyle çift dilli. Dil değiştirme en üstte.
- **Commit'ler**: Geleneksel commit'ler kullanın (`feat:`, `fix:`, `docs:`, `refactor:`, vb.).

## Sorun Bildirme

Hataları, özellik taleplerini veya sorularınızı [GitHub Issues](https://github.com/bayraktarozcan/AgentSynapse/issues) üzerinden bildirin.

Bir hata bildirirken şunları ekleyin:
- İşletim sisteminiz (Windows / macOS / Linux)
- Python sürümü (`python --version`)
- Git sürümü (`git --version`)
- Çalıştırdığınız tam komut (varsa `--lang tr` ile birlikte)
- Günlük dosyasındaki hata mesajları
