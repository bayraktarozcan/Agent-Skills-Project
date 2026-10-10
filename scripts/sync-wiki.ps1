# Sync the repo's Wiki/ folder (source of truth) to both GitHub and GitLab wikis.
#
# Model: edit Wiki/*.md in this repo, run once, both wikis update. The wikis are
# derived artifacts; manual edits made directly on a wiki are overwritten by the
# next run. GitLab is a mirror of GitHub, so a GitLab wiki with commits this repo
# has never seen is refused unless -Force is passed (force-with-lease, not blind).
#
# Usage:
#   pwsh ./scripts/sync-wiki.ps1            # both wikis, fast-forward only
#   pwsh ./scripts/sync-wiki.ps1 -Force     # also overwrite a diverged GitLab wiki
#   pwsh ./scripts/sync-wiki.ps1 -SkipGitHubWiki  # only publish to GitLab

param(
    [string]$WikiDir = (Join-Path (Split-Path -Parent $PSScriptRoot) 'Wiki'),
    [string]$GitHubWikiUrl = 'https://github.com/bayraktarozcan/AgentSynapse.wiki.git',
    [string]$GitLabWikiUrl = 'https://gitlab.com/bayraktarozcan/AgentSynapse.wiki.git',
    [string]$CommitMessage = 'docs: sync wiki from Wiki/',
    [switch]$Force,
    [switch]$SkipGitHubWiki,
    [switch]$Keep
)

# No global $ErrorActionPreference = 'Stop': in PowerShell 5.1 it turns native
# stderr (e.g. harmless Git Credential Manager noise) into a terminating error,
# making real pushes look like failures. Native steps are guarded by
# $LASTEXITCODE checks below instead.

function Fail([string]$msg) { Write-Host "FAILED: $msg" -ForegroundColor Red; exit 1 }
function Info([string]$msg) { Write-Host $msg }

$WikiDir = [System.IO.Path]::GetFullPath($WikiDir)
if (-not (Test-Path -LiteralPath $WikiDir)) { Fail "Wiki folder not found: $WikiDir" }

$git = (Get-Command git -ErrorAction Stop).Source

$repoRoot = Split-Path -Parent $PSScriptRoot
$authorName = & $git -C $repoRoot config user.name
$authorEmail = & $git -C $repoRoot config user.email
if (-not $authorName -or -not $authorEmail) { Fail 'set user.name/user.email on this repo first (git config user.name/email)' }
$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ('wiki-sync-' + [guid]::NewGuid().ToString('N'))
$clone = Join-Path $tmp 'wiki'

try {
    & $git clone --quiet -c core.autocrlf=false $GitHubWikiUrl $clone 2>$null
    if ($LASTEXITCODE -ne 0) { Fail "could not clone GitHub wiki ($GitHubWikiUrl)" }

    $branch = (& $git -C $clone symbolic-ref refs/remotes/origin/HEAD) -replace '^refs/remotes/origin/', ''
    if (-not $branch) { Fail 'could not determine GitHub wiki default branch' }

    Copy-Item -Path (Join-Path $WikiDir '*') -Destination $clone -Force -Recurse -ErrorAction Stop
    & $git -C $clone add -A
    $changed = (& $git -C $clone status --porcelain)

    if ($changed) {
        & $git -C $clone -c "user.name=$authorName" -c "user.email=$authorEmail" commit -m $CommitMessage 2>$null
        if ($LASTEXITCODE -ne 0) { Fail 'git commit failed (is git user.name/email set?)' }
        Info "Committed $($changed.Count) changed file(s) to the local wiki clone."
    } else {
        Info 'Wiki files unchanged on GitHub side.'
    }

    if (-not $SkipGitHubWiki) {
        if ($changed) {
            & $git -C $clone push --quiet origin $branch 2>$null
            if ($LASTEXITCODE -ne 0) { Fail "push to GitHub wiki failed" }
            Info 'Pushed GitHub wiki -> done.'
        } else {
            Info 'GitHub wiki side: nothing to push.'
        }
    }

    & $git -C $clone remote add gitlab $GitLabWikiUrl
    & $git -C $clone fetch --quiet gitlab
    if ($LASTEXITCODE -ne 0) { Fail "could not fetch GitLab wiki ($GitLabWikiUrl)" }

    $hasRemote = $true
    $null = (& $git -C $clone rev-parse --verify --quiet "gitlab/$branch") 2>$null
    if ($LASTEXITCODE -ne 0) { $hasRemote = $false }

    if (-not $hasRemote) {
        & $git -C $clone push --quiet gitlab $branch 2>$null
        if ($LASTEXITCODE -ne 0) { Fail 'push to GitLab wiki failed' }
        Info 'Pushed GitLab wiki (new default branch).'
        return
    }

    $diverged = [int](& $git -C $clone rev-list --count "HEAD..gitlab/$branch")
    $localAhead = [int](& $git -C $clone rev-list --count "gitlab/$branch..HEAD")

    if ($diverged -eq 0) {
        if ($localAhead -eq 0) {
            Info 'GitLab wiki already in sync.'
        } else {
            & $git -C $clone push --quiet gitlab $branch 2>$null
            if ($LASTEXITCODE -ne 0) { Fail 'push to GitLab wiki failed' }
            Info 'Pushed GitLab wiki (fast-forward).'
        }
    } else {
        if ($Force) {
            & $git -C $clone push --quiet --force-with-lease gitlab $branch 2>$null
            if ($LASTEXITCODE -ne 0) { Fail 'force push to GitLab wiki failed' }
            Info 'Pushed GitLab wiki (force-with-lease; GitLab-only edits overwritten).'
        } else {
            Fail 'GitLab wiki has commits this repo has never seen. Re-run with -Force to overwrite them, or reconcile manually.'
        }
    }
} finally {
    if (-not $Keep) { Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue }
}