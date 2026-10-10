# Changelog / Değişiklik Günlüğü

| <kbd>[🇬🇧 **English**](#en)</kbd> | <kbd>[🇹🇷 **Türkçe**](#tr)</kbd> |
|---|---|

---

<a id="en"></a>

<details open>
<summary><b>English</b></summary>

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **GitGuardian/agent-skills in K6** — official MIT-licensed secret-scanning skills (`scan-secrets`, `scan-machine`, `check-hmsl`, `triage-incidents`, `create-honeytokens`, `install-hooks`) installed via `subpath: skills`. Registry counts move to 35 recommended repos and ~571 skills.
- **Project-local skill `git-remote-credential-hygiene`** — under `Skills/`, owns the remote-URL-to-OS-credential-manager move plus GitHub/GitLab dual-remote authentication proof (read-only by default, approval-gated move, rotation-first). Complements scanner skills; ships a read-only `scan_remote_hygiene.py` script.

### Fixed

- **Stale `resolving-merge-conflicts` entry removed** — upstream `mattpocock/skills` no longer ships it as a SKILL.md, so it can never install. Manifest counts corrected to 571 skills (C1 190; profiles 227/360/571).
- **Skill spec compliance rework** — `git-remote-credential-hygiene` now follows the Agent Skills shape (router SKILL.md with open-when table, trigger-rich description, `SPEC.md` contract, `evals/evals.json` cases).
- **Naming compliance sweep** — non-conforming paths renamed to PascalCase/UPPER (`Scripts/`, `Skills/`, `Temp/`, `SKILL-SPECIALIZATION.json`, workflows, templates, `Sync-Wiki.ps1`, skill leaves, web assets); `docs/` was reverted after the GitHub Pages legacy `/docs` source broke the build, and stays as a recorded platform-fixed exemption. CI, code, docs, and contract references updated together.

## [1.1.0] - 2026-09-09

### Added

- **Specialization profiles** — `--profile temel|dengeli|tam` scopes what stays installed in `~/.agents/skills/`: `temel` (222 skills, classes C1+C2), `dengeli` (355, classes C1+C2+C3 plus the first 76 of C4), `tam` (566, everything; the default).
- **`skill-specialization.json`** — bundled manifest mapping all 566 skills to specialization classes C1–C5 (counts 185/37/57/190/97).
- **`--list` specialization map** — prints the classes, per-class counts and the three profiles, marking the active one.
- **`--check` profile coverage** — reports installed-vs-expected per profile and per-class installed counts.
- **Post-install reconciliation** — when a profile other than `tam` is used, out-of-profile skills move to `~/.agents/_quarantine_<profile>_<date>/` with a `_moved-list.txt`; `--dry-run` previews what would move.
- **Version bump to 1.1.0** — `--version` now reports `AgentSynapse v1.1.0`.

## [1.0.2] - 2026-09-09

### Changed

- Sparse partial clone for `subpath` repos (`--filter=blob:none --sparse` + `sparse-checkout set`) keeps huge monorepos (e.g. `metabase/metabase`) installable without downloading the full tree.
- Only `SKILL.md` is copied per skill folder; references, scripts, templates and nested dirs are no longer installed (`~/.agents/skills/<name>/` is clean).
- Cross-repo name collisions are now surfaced: reinstalling over a different source with different content logs a `[WARN] ... overwriting` message instead of silently replacing the file.
- Success estimates refreshed in help/README/docs: Recommended profile measured 566+ skills (2026-09-09), table updated from stale ~450.

### Fixed

- GUI progress bar now redraws live during install (previously only refreshed on window resize).
- `process_repo` no longer aborts the whole install when a partial-clone blob read fails; a failed copy is logged and counted instead of crashing.
- Clone timeout now includes the timeout detail in the log/error message.
- **Duplicate install targets**: CLI install/dry-run targets are now deduplicated case-insensitively (e.g. `K2 K2`, `K2 k2`) and across profile aliases (e.g. `recommended onerilen`, `tum tumu` collapse to one run).

## [1.0.1] - 2026-08-15

### Changed

- **Single-branch clones**: repos are now cloned with `--depth 1 --single-branch --no-tags` (one branch, no tags).
- **Deterministic colors**: `color_for_cat` uses SHA-256 (md5 is unavailable under FIPS mode).
- **GUI Recommended parity**: the Recommended profile honors per-repo filtering, and any manual checkbox change falls back to full-category installs.
- **`--prefix` timing**: the install prefix is now applied before dry-run/list commands.

### Fixed

- **Unicode crash on legacy Windows consoles**: UTF-8 bootstrap in `main()` switches codepages and pins stdout/stderr (cp125x could not encode box-drawing characters).
- **GUI `_` shadowing TypeError**: tuple unpacking shadowed the i18n `_()` helper in CLI `install()` and GUI `run_install()` (renamed to `_cat_color`).
- **Frontmatter rewrite guard**: the `name:` rewrite only runs when a frontmatter `name:` line actually exists, so body lines were never corrupted.

## [1.0.0] - 2026-06-25

### Added

- **Functional categories (K1–K10)**: replaced the old trust-based Kademe system with 10 functional categories (Core, AI, Cloud, Frontend, Mobile, Security, Testing, Content, Community, Risk).
- **Onerilen (Recommended) profile**: new default install profile — 34 repos, ~450 skills, curated for quality and relevance.
- **Cross-platform Python script**: single `skills.py` replaces old skills.ps1/skills.sh.
- **GUI mode**: `--gui` launches tkinter installer with profile quick-select.
- **Bilingual support**: English + Turkish, auto-detected or `--lang tr`.
- **Embedded repo data**: all repo config in skills.py, no external files needed.
- **Embedded docs**: accessible via `--readme`, `--changelog`, `--conduct`, `--security`, `--support`, `--license` flags.
- `--show-config` flag to dump embedded repo registry as JSON.

### Changed

- Default profile changed from `guvenli` (trusted) to `onerilen` (recommended).
- `sickn33/antigravity-awesome-skills` removed due to quality/trust concerns.
- CLI parameter names updated to English/category-based names (Turkish aliases retained).

### Fixed

- Missing target-path safety check (skill name could escape `$SKILLS_DIR`).
- `git clone` timeout and FileNotFoundError handling.
- GUI set_profile() wrong default for categories without explicit `recommended` field.
- list_repos() excluding categories with absent `recommended` key.

### Removed

- skills.ps1, skills.sh, docs/, CONTRIBUTING.md, karar.md, CATEGORIES.md — replaced by skills.py.
- repos.json, repos.example.json — data embedded in skills.py.
- External .md files — content embedded as bilingual constants in skills.py.

## [0.1.0] - 2026-06-24

### Added

- Initial project scaffolding.
- `skills.ps1` — PowerShell installer with Kademe-based trust classification (K1–K6).
- `karar.md` — classification document.
- `guvenli` (trusted), `tum` (all), and individual category installs.
- Git repository initialization.

</details>

<a id="tr"></a>

Projedeki tüm kayda değer değişiklikler bu dosyada belgelenmiştir.

## [Unreleased]

### Eklenenler

- **K6'da GitGuardian/agent-skills** — resmi MIT lisanslı secret tarama becerileri (`scan-secrets`, `scan-machine`, `check-hmsl`, `triage-incidents`, `create-honeytokens`, `install-hooks`), `subpath: skills` ile kuruluyor. Kayıt sayıları 35 önerilen depo ve ~571 beceriye çıktı.
- **Proje-içi beceri `git-remote-credential-hygiene`** — `Skills/` altında; uzak URL'den işletim sistemi kimlik deposuna taşıma ile GitHub/GitLab çift-uzak kimlik doğrulama kanıtını üstlenir (varsayılan salt-okunur, taşıma onaylı, önce döndür). Salt-okunur `scan_remote_hygiene.py` betiği dahil.

### Düzeltmeler

- **Kullanılmayan `resolving-merge-conflicts` girdisi kaldırıldı** — üst depo `mattpocock/skills` artık bunu SKILL.md olarak sunmuyor, kurulması mümkün değil. Manifest sayıları 571 beceri olarak düzeltildi (C1 190; profiller 227/360/571).
- **Beceri spec uyumu** — `git-remote-credential-hygiene` artık Agent Skills biçiminde (yönlendiren SKILL.md, tetikleyici açıklama, `SPEC.md` sözleşmesi, `evals/evals.json` vakaları).
- **Adlandırma uyum süpürmesi** — kural dışı yollar PascalCase/UPPER biçime taşındı (`Scripts/`, `Skills/`, `Temp/`, `SKILL-SPECIALIZATION.json`, iş akışları, şablonlar, `Sync-Wiki.ps1`, beceri yaprakları, web varlıkları); GitHub Pages eski `/docs` kaynağı derlemeyi bozunca `docs/` geri alındı ve platform-sabit muafiyet olarak kaydedildi. CI, kod, belge ve sözleşme referansları birlikte güncellendi.

## [1.1.0] - 2026-09-09

### Eklenenler

- **Uzmanlaşma profilleri** — `--profile temel|dengeli|tam`, `~/.agents/skills/` klasöründe neyin kurulu kalacağını kapsamlar: `temel` (222 beceri, C1+C2 sınıfları), `dengeli` (355, C1+C2+C3 sınıfları artı C4'ün ilk 76'sı), `tam` (566, hepsi; varsayılan).
- **`skill-specialization.json`** — tüm 566 beceriyi C1–C5 uzmanlaşma sınıflarına eşleyen gömülü manifest (sayılar 185/37/57/190/97).
- **`--list` uzmanlaşma haritası** — sınıfları, sınıf başına sayıları ve üç profili yazdırır, aktif olanı işaretler.
- **`--check` profil kapsamı** — profil başına kurulu/beklenen ve sınıf başına kurulu sayıları raporlar.
- **Kurulum sonrası uzlaştırma** — `tam` dışında bir profil kullanıldığında profil dışı beceriler `~/.agents/_quarantine_<profil>_<tarih>/` klasörüne taşınır (`_moved-list.txt` yazılır); `--dry-run` neyin taşınacağını önizler.
- **Sürüm 1.1.0'a yükseltildi** — `--version` artık `Agent Beceri Projesi v1.1.0` gösterir.

## [1.0.2] - 2026-09-09

### Değişiklikler

- **Kısmi (sparse) klonlama**: `subpath`'li depolar `--filter=blob:none --sparse` + `sparse-checkout set` ile klonlanıyor; dev monorepolarda (örn. `metabase/metabase`) tüm ağaç indirilmeden kurulum yapılabiliyor.
- **Yalnızca SKILL.md kopyalanıyor**: beceri klasörü başına artık sadece `SKILL.md` kuruluyor; referanslar, script'ler, şablonlar ve iç içe klasörler kuruluma girmez (`~/.agents/skills/<ad>/` temiz).
- **Çapraz-depo isim çakışmaları görünür kılındı**: farklı kaynak ve farklı içerikle aynı ad üzerine kurulum yapılırsa `[WARN] ... overwriting` mesajı loglanıyor; sessiz üzerine yazma sona erdi.
- Yardım/README dok sayıları güncellendi: Recommended profili 566+ beceri olarak ölçüldü (2026-09-09), eski ~450 tablosu güncellendi.

### Düzeltmeler

- GUI ilerleme çubuğu artık kurulum sırasında canlı çiziliyor (önceden yalnızca pencere yeniden boyutlanınca yenileniyordu).
- `process_repo` kısmi klon blob okuma hatasında tüm kurulumu durdurmuyor; hatalı kopya loglanıp geçiliyor.
- Klon zaman aşımı hatası artık ayrıntıyı log/mesaja dahil ediyor.
- **Mükerrer kurulum hedefleri**: CLI kurulum/dry-run hedefleri artık büyük/küçük harfe duyarsız (örn. `K2 K2`, `K2 k2`) ve profil takma adları arasında (örn. `recommended onerilen`, `tum tumu` tek çalıştırmaya iner) tekilleştiriliyor.

## [1.0.1] - 2026-08-15

### Değişiklikler

- **Tek dal klonlama**: depolar artık `--depth 1 --single-branch --no-tags` ile klonlanıyor (tek dal, tag yok).
- **Deterministik renkler**: `color_for_cat` SHA-256 kullanıyor (md5, FIPS modunda kullanılamaz).
- **GUI Önerilen uyumu**: Önerilen profili depo bazlı filtrelemeyi dikkate alıyor; elle yapılan işaretleme değişikliği tam kategori kurulumuna döner.
- **`--prefix` zamanlaması**: kurulum öneki artık dry-run/list komutlarından önce uygulanıyor.

### Düzeltmeler

- **Eski Windows konsollarında Unicode çökmesi**: `main()` içindeki UTF-8 bootstrap kod sayfalarını değiştirip stdout/stderr'i sabitliyor (cp125x kutu çizgi karakterlerini kodlayamıyordu).
- **GUI `_` gölgeleme TypeError'ı**: tuple açılımı, CLI `install()` ve GUI `run_install()` içindeki i18n `_()` yardımcısını gölgeliyordu (`_cat_color` olarak yeniden adlandırıldı).
- **Frontmatter yeniden yazım koruması**: `name:` yeniden yazımı yalnızca frontmatter'da gerçek bir `name:` satırı varsa çalışır, böylece gövde satırları asla bozulmaz.

## [1.0.0] - 2026-06-25

### Eklenenler

- **İşlevsel kategoriler (K1–K10)**: eski Kademe sistemi yerine 10 işlevsel kategori.
- **Önerilen profili**: varsayılan kurulum profili — 34 depo, ~450 beceri.
- **Çapraz platform Python betiği**: tek `skills.py`, eski skills.ps1/skills.sh yerine.
- **GUI modu**: `--gui` ile tkinter yükleyici, profil hızlı seçimi.
- **İki dilli destek**: İngilizce + Türkçe, otomatik algılama veya `--lang tr`.
- **Gömülü depo verisi**: tüm depo yapılandırması skills.py içinde, harici dosya gerekmez.
- **Gömülü dokümanlar**: `--readme`, `--changelog`, `--conduct`, `--security`, `--support`, `--license` ile erişilebilir.
- `--show-config` bayrağı ile gömülü depo kaydını JSON olarak dökme.

### Değişenler

- Varsayılan profil `güvenli`'den `önerilen`'e değiştirildi.
- `sickn33/antigravity-awesome-skills` kalite endişeleri nedeniyle kaldırıldı.
- CLI parametre adları İngilizce/kategori tabanlı olarak güncellendi (Türkçe takma adlar korundu).

### Düzenlenenler

- Eksik hedef yol güvenlik kontrolü (beceri adı SKILLS_DIR dışına çıkabiliyordu).
- `git clone` zaman aşımı ve FileNotFoundError yönetimi.
- GUI set_profile()'da açık recommended alanı olmayan kategoriler için yanlış varsayılan.
- list_repos()'un recommended anahtarı olmayan kategorileri dışlaması.

### Kaldırılanlar

- skills.ps1, skills.sh, docs/, CONTRIBUTING.md, karar.md, CATEGORIES.md — skills.py ile değiştirildi.
- repos.json, repos.example.json — veriler skills.py içine gömüldü.
- Tüm harici .md dosyaları — içerik skills.py içinde iki dilli sabitler olarak gömüldü.

## [0.1.0] - 2026-06-24

### Eklenenler

- İlk proje iskeleti.
- skills.ps1 — PowerShell yükleyici, Kademe tabanlı sınıflandırma (K1–K6).
- karar.md — sınıflandırma belgesi.
- Git deposu başlatma.
