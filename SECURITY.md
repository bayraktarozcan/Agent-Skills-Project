# Security Policy / Güvenlik Politikası

| <kbd>[🇬🇧 **English**](#en)</kbd> | <kbd>[🇹🇷 **Türkçe**](#tr)</kbd> |
|---|---|

---

<a id="en"></a>

<details open>
<summary><b>English</b></summary>

## Supported Versions

Only the latest release is actively supported. All older releases are [DEPRECATED] (their release titles carry the `[DEPRECATED]` prefix) and receive no security fixes.

| Version | Supported |
|---------|-----------|
| 1.2.1  | Active |
| 1.2.0 and older | [DEPRECATED] |

## Accepted Risk: Mutable CI References

On 2026-11-21 (UTC+03:00) the project deliberately moved CI to the always-latest model: third-party actions track their upstream default branch and Docker images use rolling tags. This accepts the risk that an upstream branch or tag can change between runs, including a compromised upstream. Compensating controls: the repository `sha_pinning_required` setting is disabled by decision, permissions are narrowly scoped per workflow, status checks gate auto-merge, both hosts run their pipelines on every push, and secrets are only available through the OS key store or CI secret store. A future upstream default-branch rename is a reviewed code change recorded in `Scripts/check_action_refs.py`. The `main-guard` ruleset additionally requires 13 status checks and one code-owner approval, and the owner bypass has been removed (live check 2026-11-23 UTC+03:00), so a failing check or a missing review blocks the merge.

## Reporting a Vulnerability

If you discover a security vulnerability in AgentSynapse, please report it privately:

1. **DO NOT** open a public GitHub issue.
2. Open a [GitHub Security Advisory](https://github.com/bayraktarozcan/AgentSynapse/security/advisories/new).

You should receive a response within **48 hours**. If you don't, please follow up.

</details>

---

<a id="tr"></a>

<details>
<summary><b>Türkçe</b></summary>

## Desteklenen Sürümler

Yalnızca en son sürüm aktif olarak desteklenir. Diğer tüm eski sürümler [DEPRECATED] olarak işaretlenir (release başlıkları `[DEPRECATED]` ön ekini taşır) ve güvenlik düzeltmeleri almaz.

| Sürüm | Destek |
|-------|--------|
| 1.2.1  | Aktif |
| 1.2.0 ve öncesi | [DEPRECATED] |

## Kabul Edilen Risk: Değişken CI Referansları

21.11.2026 tarihinde (UTC+03:00) proje bilinçli olarak CI'ı her daim en güncel modeline geçirdi: üçüncü taraf eylemler upstream varsayılan dalını, Docker imajları ise güncel etiketleri izler. Bu, bir upstream dalının veya etiketinin çalıştırmalar arasında değişme — bir upstream'in ele geçirilmesi — riskini kabul eder. Telafi kontrolleri: depodaki `sha_pinning_required` ayarı bilinçli olarak kapalı, iş akışları en dar izinlerle çalışıyor, durum denetimleri otomatik birleştirmeyi kapıyor, her iki host her push'ta ardışık düzenini çalıştırıyor ve sırlar yalnızca işletim sistemi anahtar deposu veya CI sır deposu üzerinden erişilebilir. Gelecekte bir upstream varsayılan dalının yeniden adlandırılması, `Scripts/check_action_refs.py` içinde kaydedilen gözden geçirilmiş bir kod değişikliğidir. `main-guard` kural takımı ayrıca 13 durum denetimi ve bir kod sahibi onayı istiyor ve sahip atlatması kaldırıldı (canlı kontrol 2026-11-23 UTC+03:00); başarısız bir denetim veya eksik onay birleştirmeyi engelliyor.

## Güvenlik Açığı Bildirimi

AgentSynapse'te bir güvenlik açığı keşfederseniz lütfen gizli şekilde bildirin:

1. **TOPLUMA AÇIK** bir GitHub issue açmayın.
2. Bir [GitHub Security Advisory](https://github.com/bayraktarozcan/AgentSynapse/security/advisories/new) açın.

**48 saat** içinde yanıt almalısınız. Yanıt alamazsanız lütfen takip edin.

</details>
