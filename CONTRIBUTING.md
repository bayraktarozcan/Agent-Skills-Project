# Contributing / Katkıda Bulunma

| <kbd>[🇬🇧 **English**](#en)</kbd> | <kbd>[🇹🇷 **Türkçe**](#tr)</kbd> |
|---|---|

---

<a id="en"></a>

<details open>
<summary><b>English</b></summary>

First off, thanks for taking the time to contribute!

## How Can I Contribute?

### Add a Repository

1. Fork the repo and create a branch.
2. Add the repo to `skills.py` under the appropriate category in the `REPOS` dict.
3. Run `python skills.py K<category>` to verify it installs.
4. Open a pull request.

### Reclassify a Repository

If you believe a repo belongs in a different category:

1. Open an issue to discuss the reclassification.
2. Provide rationale: what the repo does, why it fits better elsewhere.
3. If accepted, update `skills.py` and submit a PR.

### Update the Specialization Manifest

When repos are added, removed or reclassified, regenerate `skill-specialization.json` so its class counts and profiles (`temel`, `dengeli`, `tam`) stay in sync with the installed universe.

### Add or Improve a Skill

1. Check if the skill already exists in the ecosystem.
2. If it's new, add it to the appropriate upstream repository.
3. For edits, submit improvements upstream first.

### Report a Bug

Open an issue with:

- **Description** — what happened vs what you expected.
- **Logs** — paste the relevant section from the timestamped install log (path per `.gitignore`).
- **Environment** — OS and Python version (`python --version`).

### Request a Feature

Open an issue with:

- **Use case** — what you're trying to accomplish.
- **Proposed solution** — if you have one.
- **Alternatives** — what else you've considered.

## Style Guide

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

feat(repo): add anthropics/skills to K2
fix(dedup): handle duplicate skill names across categories
docs(readme): add quickstart section
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`.

### Code Style

- Follow existing conventions in `skills.py`.
- Keep the code Python 3.8+ compatible.
- Add imports in alphabetical order.
- Comment non-obvious logic.

## Pull Request Process

1. Ensure all existing commands still work: `python skills.py recommended`, `trusted`, `all`.
2. Update `skills.py` and keep `skill-specialization.json` in sync if classifications changed.
3. PRs require at least one review before merging.
4. Keep PRs focused — one change per PR.

## Code of Conduct

Please note that this project is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code.

</details>

<a id="tr"></a>

Öncelikle, katkıda bulunmaya zaman ayırdığınız için teşekkürler!

## Nasıl Katkıda Bulunabilirim?

### Depo Ekleme

1. Depoyu forklayın ve bir dal oluşturun.
2. Depoyu `skills.py` içindeki uygun kategoriye ekleyin.
3. `python skills.py K<kategori>` ile kurulumu doğrulayın.
4. Bir pull request açın.

### Depo Yeniden Sınıflandırma

Bir deponun farklı bir kategoride olması gerektiğini düşünüyorsanız:

1. Yeniden sınıflandırmayı tartışmak için bir sorun açın.
2. Gerekçe sunun: depo ne yapıyor, neden başka yere daha uygun.
3. Kabul edilirse, `skills.py`'yi güncelleyin ve bir PR gönderin.

### Uzmanlaşma Manifestini Güncelleme

Depolar eklendiğinde, kaldırıldığında veya yeniden sınıflandırıldığında, sınıf sayıları ve profillerin (`temel`, `dengeli`, `tam`) kurulan evrenle senkron kalması için `skill-specialization.json` dosyasını yeniden oluşturun.

### Beceri Ekleme veya İyileştirme

1. Becerinin ekosistemde zaten var olup olmadığını kontrol edin.
2. Yeniyse, uygun üst depoya ekleyin.
3. Düzenlemeler için iyileştirmeleri önce üst depoya gönderin.

### Hata Bildirme

Bir sorun açın ve şunları ekleyin:

- **Açıklama** — ne oldu vs ne bekliyordunuz.
- **Günlükler** — zaman damgalı kurulum günlüğünden ilgili bölümü yapıştırın (yol `.gitignore` dosyasına göre).
- **Ortam** — işletim sistemi ve Python sürümü (`python --version`).

### Özellik Talep Etme

Bir sorun açın ve şunları ekleyin:

- **Kullanım senaryosu** — ne yapmaya çalışıyorsunuz.
- **Çözüm** — varsa öneriniz.
- **Alternatifler** — başka neleri değerlendirdiniz.

## Stil Rehberi

### Commit Mesajları

Conventional Commits kullanıyoruz:

```
<tür>(<kapsam>): <açıklama>
```

### Kod Stili

- `skills.py` içindeki mevcut kurallara uyun.
- Python 3.8+ uyumlu kalın.
- Karmaşık olmayan mantığı yorum satırıyla açıklayın.

## Pull Request Süreci

1. Tüm mevcut komutların çalıştığını doğrulayın: `python skills.py recommended`, `trusted`, `all`.
2. Sınıflandırmalar değiştiyse `skills.py`'yi güncelleyin ve `skill-specialization.json` dosyasını senkron tutun.
3. PR'ler birleştirilmeden önce en az bir inceleme gerektirir.
4. PR'ları odaklı tutun — her PR'da tek bir değişiklik.

## Davranış Kuralları

Bu proje [Davranış Kuralları](CODE_OF_CONDUCT.md) ile yönetilmektedir.
Katılımınızla bu kurallara uymayı kabul etmiş olursunuz.
