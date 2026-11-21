# Support / Destek

| <kbd>[🇬🇧 **English**](#en)</kbd> | <kbd>[🇹🇷 **Türkçe**](#tr)</kbd> |
|---|---|

---

<a id="en"></a>

<details open>
<summary><b>English</b></summary>

## Getting Help

### Documentation

- Run `python skills.py --readme` — full README.
- Run `python skills.py --list` — list available categories.
- Run `python skills.py --help` — CLI reference.

### Bug Reports

Open a [GitHub Issue](https://github.com/bayraktarozcan/AgentSynapse/issues/new?template=Bug-Report.md).

Include:
- What you ran (full command).
- What you expected vs what happened.
- Relevant log output (timestamped install log; path per `.gitignore`).
- Your OS and Python version (`python --version`).

### Feature Requests

Open a [Feature Request](https://github.com/bayraktarozcan/AgentSynapse/issues/new?template=Feature-Request.md).

### Discussions

For questions, ideas, and community support:
[GitHub Discussions](https://github.com/bayraktarozcan/AgentSynapse/discussions)

### Security Issues

Run `python skills.py --security` or see [SECURITY.md](SECURITY.md) for responsible disclosure.

## Common Issues

### "Git is Not Recognized"

Install Git from https://git-scm.com/ and restart your terminal.

### "Access Denied" When Writing to `~/.agents/skills/`

Run as administrator/root, or manually create the directory:
```
mkdir -p ~/.agents/skills
```

### Skills Not Showing Up in My Agent

- Claude Code: skills in `~/.agents/skills/` are auto-discovered at agent launch.
- OpenCode: same path. If skills aren't showing, restart the agent session.

### Install is Slow

`python skills.py` clones 35 repos with `--depth 1 --single-branch`. First run is network-heavy (~200MB).
Skills persist until you reinstall.

</details>

<a id="tr"></a>

## Yardım Alma

### Dokümantasyon

- `python skills.py --help` — CLI referansı.
- `python skills.py --readme` — tam README.
- `python skills.py --list` — kategorileri listele.

### Hata Bildirimleri

[GitHub Sorunu](https://github.com/bayraktarozcan/AgentSynapse/issues/new?template=Bug-Report.md) açın.

ŞUNLARI EKLEYİN:
- Çalıştırdığınız komut (tam hali).
- Beklediğiniz ve gerçekleşen sonuç.
- Zaman damgalı kurulum günlüğündeki ilgili çıktı (yol `.gitignore` dosyasına göre).
- İşletim sisteminiz ve Python sürümünüz (`python --version`).

### Özellik Talepleri

[GitHub Özellik Talebi](https://github.com/bayraktarozcan/AgentSynapse/issues/new?template=Feature-Request.md) açın.

### Tartışmalar

Sorular, fikirler ve topluluk desteği için: GitHub Discussions.

### Güvenlik Sorunları

Sorumlu ifşa için `python skills.py --security` çalıştırın.

## Sık Karşılaşılan Sorunlar

### "Git Tanınmıyor"

Git'i https://git-scm.com/ adresinden yükleyin ve terminalinizi yeniden başlatın.

### "~/.Agents/Skills/ Konumuna Yazılırken Erişim Reddedildi"

Yönetici/root olarak çalıştırın veya dizini manuel oluşturun:
```
mkdir -p ~/.agents/skills
```

### Beceriler Ajanımda Görünmüyor

- Claude Code: ~/.agents/skills/ içindeki beceriler ajan başlatılırken otomatik keşfedilir.
- OpenCode: aynı yol. Beceriler görünmüyorsa, ajan oturumunu yeniden başlatın.

### Kurulum Yavaş

`python skills.py` 35 depoyu `--depth 1 --single-branch` ile klonlar. İlk çalıştırma ağırlıklı olarak ağ trafiği içerir (~200MB).
Beceriler yeniden yükleyene kadar kalıcıdır.
