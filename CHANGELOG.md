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

- **Fail-closed installer path safety** — every candidate `SKILL.md` is checked for symlink/junction components in its full path chain and required to resolve inside the cloned scan root before it is opened, rewritten or copied; install targets are checked for links before and after directory creation. `--uninstall` refuses linked paths, requires typed confirmation for a custom prefix and removes quarantine directories.
- **Provenance and measured inspection** — each installed skill records its resolved commit SHA, source tier and SHA-256 digest in a structured audit log, and `--check` reports digest drift. `--inspect` clones selected repos without installing and reports real skill names, sizes, digests and tiers; `--dry-run` no longer prints a fabricated `17 × repos` estimate.
- **Real install integration check** — a network `Pinned Source Integration` CI job clones one pinned repo with the installer's own code, verifies the checked-out SHA equals the recorded pin, counts `SKILL.md` files and checks every name against the specialization manifest; `Scripts/check_install_integration.py --all` runs the same audit across all repos in advisory mode during weekly pin refresh to surface inventory drift.
- **Immutable source pins with weekly refresh** — every `REPOS` entry now carries a reviewed 40-hex commit SHA; the installer fetches and checks out that exact commit and records it with each skill's digest. `Scripts/update_pin_refs.py --check` verifies pins against upstream HEAD, `.github/workflows/Pin-Refresh.yml` opens an auto-merge PR when HEAD advances, and a named `pin-refs` guard rejects branch names or missing pins. Currency is therefore preserved without giving up reproducibility.
- **Trust-ranked collision resolution** — installs share a claim registry: identical copies are deduplicated, a lower-trust source receives a deterministic namespaced folder, and when a higher-trust source arrives later it takes the canonical name while the earlier copy is renamed with its frontmatter updated. Different content is never silently overwritten, so every requested skill survives.
- **Installer unit tests** — `Tests/` holds stdlib `unittest` cases for linked files and parents, escaped paths, destination links, frontmatter rewrites, collisions, target dedup, provenance drift and clone retry. `Scripts/check_install_safety.py --selftest` plants a failure to prove the runner can fail; the suite is wired into GitHub CI, GitLab CI, the local gate and the pre-push hook.
- **EOL-aware CI Python floor automation** — `.github/workflows/Python-Floor.yml` reads the Python core team's release calendar (`https://peps.python.org/api/release-cycle.json`) weekly and opens an auto-merge PR when the oldest supported minor advances beyond the declared CI floor. `Scripts/python_floor.py` resolves the floor, refuses downgrades, retries transient network failures, and verifies parity across both hosts' matrices and the agent guide (including the local mirror); `selftest` proves the guards can fail. No minimum Python 3 runtime is advertised to users; the current release is the only recommended runtime.
- **Named CI and release guards** — `Scripts/check_action_refs.py` verifies every action ref against a local default-branch map, forbids SHA/version/digest pins and rejects `${{ ... }}` expressions inside `run:` blocks; `Scripts/check_repo_conventions.py` guards final newlines and hidden-layer names; `Scripts/check_release_hygiene.py` audits published titles, bilingual bodies and changelog coverage on both hosts; `Scripts/verify_mirror.py --selftest` now also detects a deleted unanchored checklist step. All run in `Hygiene` and the local gate (the release audit is network-bound and CI-only).
- **Optional pre-push gate** — tracked `Scripts/pre-push` plus `Scripts/install_hooks.py` (with timestamped backup and `--uninstall`) enforce the local gate before a push. Installation is opt-in because it writes outside the tracked tree.

### Changed

- **Mandatory hygiene and integration gates** — `Hygiene` now runs on every pull request, and the live ruleset requires its `Lint Workflows` job plus `Pinned Source Integration`. The integration job also evaluates inventory drift across all sources before merge; known drift remains visible in its log.
- **Collision provenance rewritten** — when a higher-trust source takes the canonical skill name, the moved copy gets a new provenance record with the updated name and SHA-256 digest and a `moved_from` marker; a regression test asserts the corrected record.
- **Branch protection tightened, owner exemption preserved** — the live `main-guard` ruleset now requires 13 CI status checks (including both Windows installer-safety legs), one code-owner approval with stale-review dismissal and last-push approval. A failing check or missing review blocks ordinary merges; the owner's `always` bypass was restored and remains a recorded exception.

### Fixed

- **Provenance digest correctness** — a skill's recorded SHA-256 is now computed from the installed bytes after any frontmatter rewrite; previously a rewritten file carried its pre-rewrite digest and produced false drift on the next `--check`.
- **Installer robustness** — `--inspect` reports the full frontmatter name without the old 2000-character limit, BOM-prefixed files are handled, and an invalid UTF-8 byte in one skill no longer aborts the whole run.
- **CWD-independent provenance** — audit records are anchored to the script location, so `--check` run from another directory still finds them.
- **Guard precision** — repo-count tables are parsed by cell structure rather than substrings, the count guard runs in GitHub Hygiene as well as locally, and CI now triggers on `Scripts/` and `Tests/` changes.
- **Windows safety coverage** — the installer unit suite now also runs in the cross-platform CI job, so the Windows junction/reparse-point path is exercised on `windows-latest` instead of only under Ubuntu.
- **Quarantine and tree traversal hardened** — `reconcile()` rejects a quarantine path chain or entry that resolves through a symlink/junction before moving skills, and `save_tree()` lists linked directories without traversing them or following a linked root.
- **CodeQL clear-text logging alert cleared** — the version-parity checker's validation messages no longer flow through a variable CodeQL classifies as a sensitive `key`.
- **Encoding gate survives history rewrites** — after a force push, `BEFORE..AFTER` is not a linear range; `check_encoding.py --commits` now scans `AFTER` alone instead of failing the gate, with a planted regression case in its selftest.
- **Frontmatter rewrite corrected** — name detection and rewriting are case-insensitive, confined to the frontmatter block and preserve the original key casing; a `Name:` line no longer leaves the installed folder name and file content out of sync.
- **Documentation drift closed** — the landing page statistic and every wiki profile table now report 35/41/50 repositories, and `check_version_parity.py` guards those exact cells with a planted-drift selftest.
- **Turkish CLI strings** keep Turkish characters and use a consistent product name.
- **SECURITY.md corrected** — the supported-version table now names `1.2.1` as active (was `1.0.2`), and EN/TR sections record the accepted risk of mutable CI references with date, zone and compensating controls.
- **Release title descriptions** are derived from the canonical `CHANGELOG.md` `Summary` section instead of a curated dictionary, so a new tag cannot drift from the changelog.
- **Release workflow fails closed** on a missing or empty `skills.py` / `skills.py.sha256`; Python-Floor PRs get `automated` and `auto-merge` labels before creation. All workflow expressions now reach scripts through `env:` instead of inline `run:` text (shell-injection surface).
- **v1.2.0 notes completed** — the omitted Security / Güvenlik bullet was added on both hosts so every changelog bullet is represented in its release notes.
- **Release-note generator corrected** — `build_release_notes.py` now reads the canonical Summary (plain prose included), emits `###` sections and Files/Documentation in both halves, and no longer falls back to a generic "Release X." line; TR Summary sections were added for all six versions. `check_release_hygiene.py` guards the generator output. Both the generator and `release_title.py` now expose `--help` like the other named checks.
- **Least-privilege release audit** — the GitLab release audit reads the public API anonymously; the write-capable `GITLAB_PUSH_TOKEN` was removed from the Hygiene workflow.
- **Workflow inventory corrected** — both guides now list all ten workflows (`Python-Floor` and `Dependabot-AutoMerge` were missing); `check_repo_conventions.py` guards the inventory.
- **Release-note audit strengthened** — the generator now emits the same `## vX — ... (date)` version headings as published bodies, and `check_release_hygiene.py` verifies non-empty EN/TR summaries, matched content-section counts and exactly two version headings in generated notes.
- **Stale-version guard generalized** — `check_repo_conventions.py` now reads the CI floor from `python_floor.py` and flags any advertised `Python 3.X+` below it, not just the former 3.8 case.
- **Release audit resilient to rate limits** — the anonymous GitLab read retries transient errors three times and falls back to the local `glab` CLI when available; CI remains token-free.
- **File-naming guard** — `check_repo_conventions.py` now enforces the §Naming convention (root UPPER, PascalCase top dirs, snake_case Python, lowercase-hyphenated skill leaves) with the recorded platform exemptions.
- **Dependabot auto-merge serialized** — a `concurrency` group prevents concurrent Dependabot PR runs from racing.
- **Wiki link form pinned** — `check_repo_conventions.py` rejects `.md` file links inside Wiki pages; links must use GitHub Wiki page form.
- **Bypass description corrected** — AGENTS.md (EN/TR) no longer claims classic branch protection allows force pushes; the live `main-guard` ruleset is active with required checks and `non_fast_forward`. The owner's `always` bypass was subsequently removed in Unreleased, so this note describes the state as of 2026-11-22, not the current configuration.
- **CONTRIBUTING.md corrected** — the remaining Python 3.8+ compatibility advice (EN/TR) was removed; `check_repo_conventions.py` now guards against reintroducing such a claim.
- **Heading-case guard** — `check_repo_conventions.py` now enforces the title-case rule from AGENTS.md across tracked Markdown (code fences, backticks, version headings and skill names exempt) and detects Turkish dotted I in English words; eight skill-spec headings were capitalized to satisfy it.
- **Line-ending guard** — `Scripts/check_line_endings.py` fails on mixed endings, on a working tree that disagrees with its declared `eol`, and on a `.gitattributes`/`.editorconfig` declaration disagreement; `--selftest` plants all three. `.editorconfig` now declares CRLF for `.ps1`/`.bat`/`.cmd` so both declarations agree. Wired into the local gate, pre-push and Hygiene.
- **Local gate / CI parity guard** — `Scripts/check_gate_parity.py` reads the gate block and every workflow and fails when the two check lists diverge in either direction, with declared CI-only and local-only exceptions. The local gate now also runs the `--dry-run` matrix, `--help` and the full encoding check that CI runs.

## [1.2.1] - 2026-11-21

### Summary

Release workflow and documentation fixes

### Changed

- **Release workflow publishes once** — the matrix-driven `Release.yml` now gates the publish step to the `3.x` leg, preventing duplicate/draft releases from concurrent matrix jobs.
- **Older releases deprecated** — `v1.0.0`–`v1.2.0` now carry `[DEPRECATED]` on both GitHub and GitLab; `v1.2.1` is the only supported release.

## [1.2.0] - 2026-11-21

### Summary

Specialization, CI currency and security release

### Added

- **GitGuardian/agent-skills in K6** — official MIT-licensed secret-scanning skills (`scan-secrets`, `scan-machine`, `check-hmsl`, `triage-incidents`, `create-honeytokens`, `install-hooks`) installed via `subpath: skills`. Registry moves to 35 recommended repos; the catalog reaches 1001 skills with NVIDIA/skills later in this release.
- **Project-local skill `git-remote-credential-hygiene`** — under `Skills/`, owns the remote-URL-to-OS-credential-manager move plus GitHub/GitLab dual-remote authentication proof (read-only by default, approval-gated move, rotation-first). Complements scanner skills; ships a read-only `scan_remote_hygiene.py` script.
- **NVIDIA/skills in K2** — 430 NVIDIA-authored skills for Physical AI, robotics, CUDA-X libraries, RAG/AI Blueprints, platform tools (Nemotron, NeMo, BioNeMo, cuOpt, DOCA, Jetson, etc.), installed via `subpath: skills`, `recommended: false`. All classified as **C4** (provider-locked) in `SKILL-SPECIALIZATION.json`; specialization manifest grows to 1001 skills (tam profile), temel/dengeli profiles unchanged (227/360). Registry remains 36 recommended repos.
- **Specialization data layer** — bundled `SKILL-SPECIALIZATION.json` maps all 1001 skills to C1–C5 (190/37/57/620/97) with `temel` 227, `dengeli` 360, `tam` 1001 profiles; `--list`, `--check`, and post-install reconciliation were added and covered by a version-parity checker and local gate.
- **Wiki publishing** — `Wiki/` is the single source, published to GitHub and GitLab wikis by `Scripts/Sync-Wiki.ps1` and `.github/workflows/Sync-Wiki.yml` on changes and weekly.
- **Security and quality gates** — Gitleaks full-history secret scan, encoding/mojibake gate, link checker, GitLab CI parity jobs, Dependabot auto-merge (with status-check polling via `gh api`), and a reproducible local gate.
- **Bilingual documentation and standards** — universal agent guide adopted as `AGENTS.md` with a gitignored TR review mirror, LOW-GLOW design core, privacy/support/security docs, CODEOWNERS, release-note template, and checked machine-time and line-ending rules.

### Changed

- **CI/CD currency policy** — third-party GitHub Actions now track their default branches (`@main`/`@master`) with `sha_pinning_required: false` in repository settings; Python jobs run a 3.11 + latest matrix on both hosts; GitLab images use rolling `python:${PYTHON_VERSION}`, `lychee:master-alpine`, and `alpine:latest` tags. AGENTS.md and its local mirror record the deliberate bypass.
- **Workflow hardening** — replaced the third-party status-check waiter with `gh api` polling, passed PR context through environment variables to prevent script injection, and made LF authoritative for all text files in `.gitattributes`.
- **Dependency-model audit** — grep verification confirmed there is no `pyproject.toml`, `requirements*.in`/`requirements.txt`, compiled lockfile, `pip install` consumer, regeneration workflow, sync script, `cache-dependency-path`, or bandit ignore in the repository; nothing needed unpinning or deletion. The stale `pip` entry was removed from Dependabot because no Python manifest exists. The program remains stdlib-only, and any future dependency list must be unpinned and latest-by-default.
- **Stale metadata corrected** — AGENTS.md no longer claims an unregistered "Latest Release" badge; all five registered SVG badges were re-probed (HTTP 200, `image/svg+xml`, 2026-11-21). The specialization manifest no longer hardcodes a superseded source count, dropped the inaccurate `ratio: 0.4` field (76 of 620 C4 skills, not 40%), and refreshed its `generated` date.
- **Release notes use the template** — `Release.yml` no longer publishes the whole `CHANGELOG.md` as the release body; `Scripts/build_release_notes.py` fills `RELEASE-NOTE-TEMPLATE.md` with the requested version section and drops empty sections. The already-published `v1.1.0` bodies on both hosts were corrected to the short bilingual notes.
- **Naming and hygiene sweep** — paths moved to PascalCase/UPPER with recorded exemptions (`docs/` stays platform-fixed); LF is authoritative for all text files, final newlines are present, PowerShell scripts keep BOM/CRLF, and tree snapshots now land in `Logs/`.
- **Documentation accuracy** — repo counts aligned to the embedded registry (35 recommended / 41 trusted / 50 total), host-tool version snapshots removed in favour of on-demand verification commands, heading capitalization standardized, bootstrap checklist and CodeQL/branch-protection facts aligned with the platform, and root documents linked from README.

### Fixed

- **Stale `resolving-merge-conflicts` entry removed** — upstream `mattpocock/skills` no longer ships it as a SKILL.md, so it can never install. Manifest counts corrected to 571 skills (C1 190; profiles 227/360/571).
- **Skill spec compliance rework** — `git-remote-credential-hygiene` now follows the Agent Skills shape (router SKILL.md with open-when table, trigger-rich description, `SPEC.md` contract, `evals/evals.json` cases).
- **Naming compliance sweep** — non-conforming paths renamed to PascalCase/UPPER (`Scripts/`, `Skills/`, `Temp/`, `SKILL-SPECIALIZATION.json`, workflows, templates, `Sync-Wiki.ps1`, skill leaves, web assets); `docs/` was reverted after the GitHub Pages legacy `/docs` source broke the build, and stays as a recorded platform-fixed exemption. CI, code, docs, and contract references updated together.
- **CI and script fixes** — PR context passed through environment variables to prevent script injection, third-party status-check waiter replaced with `gh api` polling, actionlint findings resolved, GitLab encoding job given `git`, Mojibake checkout made full-depth, `Sync-Wiki.ps1` saved with UTF-8 BOM, link-check exclusions corrected, Dependabot auto-merge noop job added, clone counts and bilingual skill counts corrected, and final newlines normalized.
- **Manifest metadata corrections** — stale source count and inaccurate `ratio: 0.4` removed, `generated` date refreshed; unregistered "Latest Release" badge claim removed after re-probing all five live SVG badges.

### Removed

- Pinned action SHAs, digest-pinned Docker images, the unsupported `poseidon` action, and the stale `pip` Dependabot ecosystem entry — the pipeline now resolves rolling branches/tags and the latest interpreter at run time.

### Security

- Secret scanning runs on every push and PR; only the latest release is supported and older releases are marked `[DEPRECATED]` on both hosts.

## [1.1.0] - 2026-09-09

### Summary

Specialization profiles release

### Added

- **Specialization profiles** — `--profile temel|dengeli|tam` scopes what stays installed in `~/.agents/skills/`: `temel` (222 skills, classes C1+C2), `dengeli` (355, classes C1+C2+C3 plus the first 76 of C4), `tam` (566, everything; the default).
- **`skill-specialization.json`** — bundled manifest mapping all 566 skills to specialization classes C1–C5 (counts 185/37/57/190/97).
- **`--list` specialization map** — prints the classes, per-class counts and the three profiles, marking the active one.
- **`--check` profile coverage** — reports installed-vs-expected per profile and per-class installed counts.
- **Post-install reconciliation** — when a profile other than `tam` is used, out-of-profile skills move to `~/.agents/_quarantine_<profile>_<date>/` with a `_moved-list.txt`; `--dry-run` previews what would move.
- **Version bump to 1.1.0** — `--version` now reports `AgentSynapse v1.1.0`.

## [1.0.2] - 2026-09-09

### Summary

Compatibility and documentation update

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

### Summary

Reliability improvements

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

### Summary

Functional categories and installer

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

- **Kapalı devre yükleyici yol güvenliği** — her aday `SKILL.md`, tam yol zincirindeki sembolik bağlantı/junction bileşenleri için denetlenir ve açılmadan, düzeltilmeden veya kopyalanmadan önce klonlanan tarama kökü içinde çözümlenmesi zorunlu kılınır; kurulum hedefleri dizin oluşturmadan önce ve sonra bağlantı yönünden kontrol edilir. `--uninstall` bağlantılı yolları reddeder, özel önek için tam yol yazımı ister ve karantina dizinlerini temizler.
- **Köken ve ölçülmüş inceleme** — kurulan her beceri, çözümlenen commit SHA'sını, kaynak düzeyini ve SHA-256 özetini yapılandırılmış denetim kaydına yazar; `--check` özet sapmasını bildirir. `--inspect` seçili depoları kurmadan klonlayıp gerçek beceri adlarını, boyutları, özetleri ve düzeyleri raporlar; `--dry-run` artık uydurma `17 × depo` tahmini basmıyor.
- **Gerçek kurulum bütünleşme kontrolü** — ağ üzerinden çalışan `Pinned Source Integration` CI işi tek bir sabit depoyu yükleyicinin koduyla klonlar, çıkarılan SHA'nın kayıtlı pin ile eşleştiğini doğrular, `SKILL.md` dosyalarını sayar ve her adı uzmanlaşma manifestosuyla karşılaştırır. `Scripts/check_install_integration.py --all` aynı denetimi haftalık pin yenilemesinde tüm depolar için uyarı modunda çalıştırarak envanter sapmasını gösterir.
- **Değişmez kaynak pinleri ve haftalık yenileme** — her `REPOS` girdisi gözden geçirilmiş 40 haneli bir commit SHA'sı taşıyor; yükleyici o commit'i getirip çıkarıyor ve beceri özetiyle birlikte kaydediyor. `Scripts/update_pin_refs.py --check` pinleri yukarı akış HEAD ile karşılaştırıyor, `.github/workflows/Pin-Refresh.yml` HEAD ilerlediğinde otomatik birleştirme PR'ı açıyor ve `pin-refs` adlı koruma dal adlarını veya eksik pinleri reddediyor. Böylece güncellik, yeniden üretilebilirlikten vazgeçilmeden korunuyor.
- **Güven sıralamasına göre çakışma çözümü** — kurulumlar arasında paylaşılan bir kayıt tutuluyor: özdeş kopyalar tekilleştiriliyor, daha az güvenilir kaynak deterministik bir adlandırılmış klasör alıyor, daha güvenilir kaynak sonra gelirse kanonik adı alıyor ve önceki kopya frontmatter'i güncellenerek yeniden adlandırılıyor. Farklı içerik sessizce üzerine yazılmıyor; istenen her beceri korunuyor.
- **Yükleyici birim sınamaları** — `Tests/` altında bağlantılı dosya ve ebeveyn, kaçan yol, hedef bağlantısı, frontmatter düzeltmesi, çakışma, hedef tekilleştirme, köken sapması ve klon yeniden denemesi için standart kütüphane `unittest` durumları var. `Scripts/check_install_safety.py --selftest` çalıştırıcının başarısız olabileceğini kanıtlamak için hata ekler; takım GitHub CI, GitLab CI, yerel kapı ve pre-push kancasına bağlıdır.
- **CI Python alt sınırı için EOL otomasyonu** — `.github/workflows/Python-Floor.yml`, Python çekirdek ekibinin yayın takvimini (`https://peps.python.org/api/release-cycle.json`) haftalık okur ve desteklenen en eski küçük sürüm bildirilen CI alt sınırını geçtiğinde otomatik birleştirme PR'ı açar. `Scripts/python_floor.py` alt sınırı çözer, düşürmeyi reddeder, geçici ağ hatalarını yeniden dener ve iki hostun matrisleri ile ajan kılavuzu (yerel ayna dahil) arasındaki eşliği doğrular; `selftest` kontrollerin işe yaradığını kanıtlar. Kullanıcıya asgari bir Python 3 sürümü önerilmez; yalnızca güncel sürüm önerilen çalışma zamanıdır.
- **Adlandırılmış CI ve yayın kontrolleri** — `Scripts/check_action_refs.py` her aksiyon referansını yerel varsayılan dal haritasıyla doğrular, SHA/sürüm/özet pinlerini yasaklar ve `run:` bloklarındaki `${{ ... }}` ifadelerini reddeder; `Scripts/check_repo_conventions.py` son satırları ve gizli katman adlarını denetler; `Scripts/check_release_hygiene.py` her iki hosttaki yayın başlıklarını, iki dilli gövdeleri ve changelog kapsamını denetler; `Scripts/verify_mirror.py --selftest` artık işaretsiz bir kontrol maddesinin silinmesini de yakalar. Hepsi `Hygiene` ve yerel kapıda çalışır (yayın denetimi ağa bağlı, yalnızca CI'da).
- **İsteğe bağlı pre-push kapısı** — takipli `Scripts/pre-push` ve `Scripts/install_hooks.py` (zaman damgalı yedek + `--uninstall`) yerel kapıyı push öncesi zorunlu kılar. Kurulum takip edilmeyen ağaca yazdığı için isteğe bağlıdır.

### Değiştirilenler

- **Zorunlu hijyen ve bütünleşme kapıları** — `Hygiene` artık her pull request'ta çalışıyor; canlı kural takımı `Lint Workflows` ve `Pinned Source Integration` işlerini zorunlu denetimlere ekledi. Bütünleşme işi birleştirme öncesinde tüm kaynakların envanter sapmasını da değerlendiriyor; bilinen sapma günlükte görünür kalıyor.
- **Çakışma köken kaydı güncellendi** — daha güvenilir kaynak kanonik adı aldığında taşınan kopya için yeni adı ve SHA-256 özetini içeren, `moved_from` işaretli bir köken kaydı ekleniyor; regresyon sınaması düzeltilmiş kaydı doğruluyor.
- **Dal koruması sıkılaştırıldı, sahip istisnası korundu** — canlı `main-guard` kural takımı artık 13 CI durum denetimi (iki Windows güvenlik kolu dahil), kod sahibinden bir onay, bayat onayların düşürülmesi ve son push onayı istiyor. Başarısız denetim veya eksik onay olağan birleştirmeleri engelliyor; sahibin `always` atlatması geri getirildi ve kayıtlı istisna olarak kalıyor.

### Düzeltmeler

- **Köken özeti doğruluğu** — bir becerinin kaydedilen SHA-256'sı, frontmatter düzeltmesinden sonra kurulan baytlardan hesaplanıyor; öncesinde düzeltilmiş dosya eski özeti taşıyor ve sonraki `--check` yanlış sapma bildiriyordu.
- **Yükleyici sağlamlığı** — `--inspect` artık eski 2000 karakter sınırı olmadan tam frontmatter adını bildiriyor, BOM'lu dosyalar işleniyor ve tek bir becerideki geçersiz UTF-8 baytı tüm çalışmayı durdurmuyor.
- **CWD'den bağımsız köken** — denetim kayıtları betik konumuna sabitlendi; başka dizinden çalıştırılan `--check` kayıtları buluyor.
- **Koruma hassasiyeti** — depo sayısı tabloları alt dizeler yerine hücre yapısına göre okunuyor; sayı koruması yerel kapının yanında GitHub Hygiene'de de çalışıyor ve CI artık `Scripts/` ve `Tests/` değişikliklerinde tetikleniyor.
- **Windows güvenlik kapsamı** — yükleyici birim takımı artık çapraz platform CI işinde de çalışıyor; Windows junction/reparse-point yolu yalnızca Ubuntu'da değil, `windows-latest` üzerinde de sınanıyor.
- **Karantina ve ağaç gezinmesi sağlamlaştırıldı** — `reconcile()` becerileri taşımadan önce karantina yol zincirinde veya hedef girişte sembolik bağlantı/junction varsa işlemi reddediyor; `save_tree()` bağlantılı dizinleri listeliyor ama içlerine girmiyor, bağlantılı kökü de izlemiyor.
- **CodeQL açık metin günlükleme uyarısı kapatıldı** — sürüm-eşlik denetiminin doğrulama mesajları artık CodeQL'ın hassas `key` olarak sınıflandırdığı bir değişkenden geçmiyor.
- **Kodlama kapısı geçmiş yeniden yazımına dayanıklı** — force-push sonrası `BEFORE..AFTER` doğrusal aralık olmadığı için `check_encoding.py --commits` kapıyı düşürmek yerine yalnızca `AFTER` commit'ini tarıyor; selftest'te yerleştirilmiş regresyon durumu var.
- **Frontmatter düzeltmesi düzeltildi** — isim algılama ve yazım büyük/küçük harfe duyarsız, yalnızca frontmatter bloğuyla sınırlı ve özgün anahtar büyüklüğünü koruyor; `Name:` satırı kurulan klasör adı ile dosya içeriğinin uyumsuz kalmasına yol açmıyor.
- **Belgelendirme sapması kapatıldı** — açılış sayfası istatistiği ve tüm wiki profil tabloları artık 35/41/50 depoyu bildiriyor; `check_version_parity.py` bu hücreleri yerleştirilmiş sapma selftest'iyle koruyor.
- **Türkçe CLI dizeleri** Türkçe karakterlerini koruyor ve tutarlı bir ürün adı kullanıyor.
- **SECURITY.md düzeltildi** — desteklenen sürüm tablosu `1.2.1`'i aktif gösteriyor (önce `1.0.2`); EN ve TR bölümleri değişken CI referanslarının kabul edilen riskini tarih, saat dilimi ve telafi kontrolleriyle kaydediyor.
- **Yayın başlığı açıklamaları** sabit sözlük yerine kanonik `CHANGELOG.md` `Summary` bölümünden türetiliyor; yeni etiket changelog'dan sapamaz.
- **Yayın iş akışı** eksik veya boş `skills.py` / `skills.py.sha256` durumunda başarısız oluyor; Python-Floor PR'ları oluşturulmadan önce `automated` ve `auto-merge` etiketlerini alıyor. Tüm iş akışı ifadeleri satır içi `run:` metni yerine `env:` üzerinden betiklere iletiliyor (kabuk enjeksiyon yüzeyi).
- **v1.2.0 notları tamamlandı** — atlanan Security / Güvenlik maddesi her iki hostta eklendi; böylece her changelog maddesi yayın notlarında temsil ediliyor.
- **Sürüm notu üreticisi düzeltildi** — `build_release_notes.py` artık kanonik Özet'i (düz metin dahil) okuyor, `###` bölümleri ve iki yarıda Dosyalar/Belgelendirme üretiyor ve genel "Release X." yedeğini kullanmıyor; altı sürümün TR Özet bölümü eklendi. `check_release_hygiene.py` üretici çıktısını denetliyor. Üretici ve `release_title.py` artık diğer adlandırılmış kontroller gibi `--help` sunuyor.
- **En az yetkiyle yayın denetimi** — GitLab yayın denetimi herkese açık API'yi anonim okuyor; yazma yetkili `GITLAB_PUSH_TOKEN` Hygiene iş akışından kaldırıldı.
- **İş akışı envanteri düzeltildi** — her iki kılavuz da on iş akışını listeliyor (`Python-Floor` ve `Dependabot-AutoMerge` eksikti); `check_repo_conventions.py` envanteri koruyor.
- **Yayın notu denetimi güçlendirildi** — üretici artık yayınlanmış gövdelerle aynı `## vX — ... (tarih)` sürüm başlıklarını üretiyor; `check_release_hygiene.py` üretilen notlarda boş olmayan EN/TR özetlerini, eşit içerik bölümü sayısını ve tam iki sürüm başlığını doğruluyor.
- **Bayat sürüm kapısı genelleştirildi** — `check_repo_conventions.py`, CI alt sınırını `python_floor.py`'den okuyor ve yalnızca eski 3.8 durumu yerine alt sınırın altındaki her `Python 3.X+` iddiasını işaretliyor.
- **Yayın denetimi hız sınırlarına dayanıklı** — anonim GitLab okuması geçici hataları üç kez yeniden dener ve yerel `glab` varsa ona düşer; CI'da token kullanılmaz.
- **Dosya adlandırma kapısı** — `check_repo_conventions.py`, §Naming kuralını (kök UPPER, PascalCase üst dizinler, snake_case Python, küçük harfli tireli beceri yaprakları) kayıtlı platform muafiyetleriyle zorunlu kılıyor.
- **Dependabot otomatik birleştirme serileştirildi** — eşzamanlı Dependabot PR çalıştırmalarının yarışmasını önleyen bir `concurrency` grubu eklendi.
- **Wiki bağlantı biçimi sabitlendi** — `check_repo_conventions.py`, Wiki sayfalarındaki `.md` dosya bağlantılarını reddediyor; bağlantılar GitHub Wiki sayfa biçiminde olmalı.
- **Atlatma açıklaması düzeltildi** — AGENTS.md (EN/TR) artık klasik dal korumasının force-push'a izin verdiğini iddia etmiyor; canlı `main-guard` kural takımı zorunlu denetimler ve `non_fast_forward` ile etkin. Sahibin `always` atlatması daha sonra Unreleased bölümünde kaldırıldı; bu madde 2026-11-22 durumu anlatıyor, güncel yapılandırma değil.
- **CONTRIBUTING.md düzeltildi** — kalan Python 3.8+ uyumluluk önerisi (EN/TR) kaldırıldı; `check_repo_conventions.py` artık böyle bir iddianın yeniden eklenmesini engelliyor.
- **Başlık büyüklüğü kapısı** — `check_repo_conventions.py`, AGENTS.md'deki başlık büyüklüğü kuralını takipli Markdown dosyalarında zorunlu kılıyor (kod blokları, backtick'ler, sürüm başlıkları ve beceri adları muaf) ve İngilizce sözcüklerde Türkçe noktalı I'yı tespit ediyor; kurala uymak için sekiz beceri-belge başlığı büyütüldü.
- **Satır sonu kapısı** — `Scripts/check_line_endings.py`; karışık sonlarda, çalışma ağacı ile bildirilen `eol` uyuşmadığında ve `.gitattributes`/`.editorconfig` bildirimleri çeliştiğinde başarısız oluyor; `--selftest` üç ihlali de yerleştiriyor. `.editorconfig` artık `.ps1`/`.bat`/`.cmd` için CRLF bildiriyor; böylece iki bildirim uyuşuyor. Yerel kapıya, pre-push'a ve Hygiene'e bağlandı.
- **Yerel kapı / CI eşlik kapısı** — `Scripts/check_gate_parity.py` kapı bloğunu ve tüm iş akışlarını okuyor; iki denetim listesi herhangi bir yönde ayrıldığında başarısız oluyor (bildirilen CI-only ve yerel-only istisnalar var). Yerel kapı artık CI'ın çalıştırdığı `--dry-run` matrisini, `--help`'i ve tam kodlama denetimini de çalıştırıyor.

## [1.2.1] - 2026-11-21

### Özet

Yayın iş akışı ve belgelendirme düzeltmeleri

### Değişiklikler

- **Yayın iş akışı bir kez yayımlıyor** — matris kullanan `Release.yml`, eşzamanlı matris işlerinden yinelenen/taslak yayın çıkmasını önlemek için yayın adımını yalnızca `3.x` bacağıyla sınırlıyor.
- **Eski yayınlar kullanımdan kaldırıldı** — `v1.0.0`–`v1.2.0` artık GitHub ve GitLab'da `[DEPRECATED]` taşıyor; yalnızca `v1.2.1` destekleniyor.

## [1.2.0] - 2026-11-21

### Özet

Uzmanlaşma, CI güncelliği ve güvenlik sürümü

### Eklenenler

- **K6'da GitGuardian/agent-skills** — resmi MIT lisanslı secret tarama becerileri (`scan-secrets`, `scan-machine`, `check-hmsl`, `triage-incidents`, `create-honeytokens`, `install-hooks`), `subpath: skills` ile kuruluyor. Kayıt 35 önerilen depoya çıktı; NVIDIA/skills ile katalog bu sürümde 1001 beceriye ulaşıyor.
- **Proje-içi beceri `git-remote-credential-hygiene`** — `Skills/` altında; uzak URL'den işletim sistemi kimlik deposuna taşıma ile GitHub/GitLab çift-uzak kimlik doğrulama kanıtını üstlenir (varsayılan salt-okunur, taşıma onaylı, önce döndür). Salt-okunur `scan_remote_hygiene.py` betiği dahil.
- **K2'de NVIDIA/skills** — Fiziksel AI, robotik, CUDA-X kütüphaneleri, RAG/AI Blueprint'lar, platform araçları (Nemotron, NeMo, BioNeMo, cuOpt, DOCA, Jetson, vb.) için 430 NVIDIA yazılı beceri, `subpath: skills` ile kuruluyor, `recommended: false`. Tümü `SKILL-SPECIALIZATION.json` içinde **C4** olarak sınıflandırıldı; uzmanlaşma manifesti 1001 beceriye çıktı (tam profil), temel/dengeli profiller değişmedi (227/360). Kayıt 36 önerilen depoya çıktı.
- **Uzmanlaşma veri katmanı** — `SKILL-SPECIALIZATION.json` tüm 1001 beceriyi C1–C5 sınıflarına eşler (190/37/57/620/97); `temel` 227, `dengeli` 360, `tam` 1001 profilleri; `--list`, `--check` ve kurulum sonrası uzlaştırma eklendi, sürüm-eşlik denetimi ve yerel kapı ile kapsandı.
- **Wiki yayını** — `Wiki/` tek doğruluk kaynağı; `Scripts/Sync-Wiki.ps1` ve `.github/workflows/Sync-Wiki.yml` ile değişikliklerde ve haftalık olarak GitHub ve GitLab wiki'lerine yayınlanır.
- **Güvenlik ve kalite kapıları** — Gitleaks tam-geçmiş sır taraması, kodlama/mojibake kapısı, bağlantı denetimi, GitLab CI eşlik işleri, Durum denetimlerini `gh api` ile bekleyen Dependabot otomatik birleştirme ve yeniden üretilebilir yerel kapı.
- **İki dilli dokümantasyon ve standartlar** — evrensel ajan kılavuzu `AGENTS.md` olarak benimsendi, gitignored TR inceleme aynası, LOW-GLOW tasarım çekirdeği, gizlilik/destek/güvenlik belgeleri, CODEOWNERS, sürüm notu şablonu ve teyit edilmiş makine saati/satır sonu kuralları eklendi.

### Değişiklikler

- **CI/CD güncellik politikası** — üçüncü taraf GitHub Actions artık varsayılan dallarını (`@main`/`@master`) izliyor; depo ayarında `sha_pinning_required: false`; Python işleri her iki hostta 3.11 + güncel matrisinde çalışıyor; GitLab imajları rolling `python:${PYTHON_VERSION}`, `lychee:master-alpine` ve `alpine:latest` etiketlerini kullanıyor. AGENTS.md ve yerel aynası bilinçli atlatmayı kaydediyor.
- **İş akışı sıkılaştırması** — üçüncü taraf durum-bekleme eylemi `gh api` sorgusuna çevrildi; script injection'i önlemek için PR bağlamı ortam değişkenlerinden geçirildi; `.gitattributes` içinde tüm metin dosyaları için LF esas kılındı.
- **Bağımlılık modeli denetimi** — grep ile doğrulandı: depoda `pyproject.toml`, `requirements*.in`/`requirements.txt`, derlenmiş kilit dosyası, `pip install` tüketicisi, yeniden üretim iş akışı, senkron betiği, `cache-dependency-path` veya bandit ignore yok; sabitlemesi kaldırılacak veya silinecek bir şey yok. Python bildirimi olmadığı için Dependabot'taki bayat `pip` girdisi kaldırıldı. Program stdlib-only kalıyor; ileride eklenecek bağımlılık listesi sabitlemesiz ve varsayılan olarak güncel olacak.
- **Bayat üst veri düzeltildi** — AGENTS.md artık kayıtlı olmayan "Latest Release" rozetini iddia etmiyor; kayıtlı beş SVG rozetinin tamamı yeniden sorgulandı (HTTP 200, `image/svg+xml`, 2026-11-21). Uzmanlaşma manifesti artık güncel olmayan kaynak sayısını sabitlemiyor, yanlış `ratio: 0.4` alanını kaldırdı (620 C4 becerisinin 76'sı, %40 değil) ve `generated` tarihini yeniledi.
- **Sürüm notları şablonu kullanıyor** — `Release.yml` artık tüm `CHANGELOG.md`'yi yayın gövdesi olarak yayımlamıyor; `Scripts/build_release_notes.py`, `RELEASE-NOTE-TEMPLATE.md`'yi istenen sürüm bölümüyle dolduruyor ve boş bölümleri atıyor. Her iki hosttaki `v1.1.0` gövdeleri kısa iki dilli notlarla düzeltildi.
- **Adlandırma ve hijyen süpürmesi** — yollar kayıtlı muafiyetlerle PascalCase/UPPER biçime taşındı (`docs/` platform-sabit kalıyor); tüm metin dosyaları için LF esas, son satırlar mevcut, PowerShell betikleri BOM/CRLF saklıyor, ağaç anlık görüntüleri artık `Logs/` altına yazılıyor.
- **Belge doğruluğu** — depo sayıları gömülü kayıtla hizalandı (35 önerilen / 41 güvenli / 50 tümü), ana makine araç sürümü dökümleri yerine anlık doğrulama komutları kullanılıyor, başlık büyük harfi standartlaştırıldı, bootstrap kontrol listesi ile CodeQL/dal koruması olguları platformla hizalandı ve tüm kök belgeler README'den linklendi.

### Düzeltmeler

- **Kullanılmayan `resolving-merge-conflicts` girdisi kaldırıldı** — üst depo `mattpocock/skills` artık bunu SKILL.md olarak sunmuyor, kurulması mümkün değil. Manifest sayıları 571 beceri olarak düzeltildi (C1 190; profiller 227/360/571).
- **Beceri spec uyumu** — `git-remote-credential-hygiene` artık Agent Skills biçiminde (yönlendiren SKILL.md, tetikleyici açıklama, `SPEC.md` sözleşmesi, `evals/evals.json` vakaları).
- **Adlandırma uyum süpürmesi** — kural dışı yollar PascalCase/UPPER biçime taşındı (`Scripts/`, `Skills/`, `Temp/`, `SKILL-SPECIALIZATION.json`, iş akışları, şablonlar, `Sync-Wiki.ps1`, beceri yaprakları, web varlıkları); GitHub Pages eski `/docs` kaynağı derlemeyi bozunca `docs/` geri alındı ve platform-sabit muafiyet olarak kaydedildi. CI, kod, belge ve sözleşme referansları birlikte güncellendi.
- **CI ve betik düzeltmeleri** — script injection'i önlemek için PR bağlamı ortam değişkenlerinden geçirildi, üçüncü taraf durum-bekleme eylemi `gh api` sorgusuna çevrildi, actionlint bulguları giderildi, GitLab kodlama işine `git` eklendi, Mojibake checkout tam geçmişe çekildi, `Sync-Wiki.ps1` UTF-8 BOM ile kaydedildi, bağlantı denetimi dışlamaları düzeltildi, Dependabot otomatik birleştirmeye noop işi eklendi, klon ve iki dilli beceri sayıları düzeltildi, son satırlar normalize edildi.
- **Manifest üst veri düzeltmeleri** — bayat kaynak sayısı ve yanlış `ratio: 0.4` kaldırıldı, `generated` tarihi yenilendi; kayıtlı olmayan "Latest Release" rozeti iddiası, beş canlı SVG rozetinin yeniden sorgulanmasının ardından kaldırıldı.

### Kaldırılanlar

- Sabitlenmiş action SHA'ları, özet-doğrulamalı Docker imajları, desteklenmeyen `poseidon` eylemi ve bayat `pip` Dependabot girdisi — hat artık çalışma anında güncel dal/etiket ve yorumlayıcıyı çözüyor.

### Güvenlik

- Sır taraması her push ve PR'da çalışıyor; yalnızca en yeni sürüm desteklenir, eski sürümler her iki hostta `[DEPRECATED]` olarak işaretlidir.

## [1.1.0] - 2026-09-09

### Özet

Uzmanlaşma profilleri sürümü

### Eklenenler

- **Uzmanlaşma profilleri** — `--profile temel|dengeli|tam`, `~/.agents/skills/` klasöründe neyin kurulu kalacağını kapsamlar: `temel` (222 beceri, C1+C2 sınıfları), `dengeli` (355, C1+C2+C3 sınıfları artı C4'ün ilk 76'sı), `tam` (566, hepsi; varsayılan).
- **`skill-specialization.json`** — tüm 566 beceriyi C1–C5 uzmanlaşma sınıflarına eşleyen gömülü manifest (sayılar 185/37/57/190/97).
- **`--list` uzmanlaşma haritası** — sınıfları, sınıf başına sayıları ve üç profili yazdırır, aktif olanı işaretler.
- **`--check` profil kapsamı** — profil başına kurulu/beklenen ve sınıf başına kurulu sayıları raporlar.
- **Kurulum sonrası uzlaştırma** — `tam` dışında bir profil kullanıldığında profil dışı beceriler `~/.agents/_quarantine_<profil>_<tarih>/` klasörüne taşınır (`_moved-list.txt` yazılır); `--dry-run` neyin taşınacağını önizler.
- **Sürüm 1.1.0'a yükseltildi** — `--version` artık `Agent Beceri Projesi v1.1.0` gösterir.

## [1.0.2] - 2026-09-09

### Özet

Uyumluluk ve belgelendirme güncellemesi

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

### Özet

Güvenilirlik iyileştirmeleri

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

### Özet

İşlevsel kategoriler ve yükleyici

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
