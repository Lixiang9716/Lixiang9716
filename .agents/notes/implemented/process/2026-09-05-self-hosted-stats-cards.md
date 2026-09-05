# Agent Note: Self-hosted profile stats cards via GitHub Actions

Status: implemented

## Problem

The profile README's stats images came from the shared
`github-readme-stats.vercel.app` public instance, which returns HTTP 503 on a
recurring basis (the maintainer's Vercel account exceeds its limits — see
anuraghazra/github-readme-stats#4658). Profile visitors saw broken images; the
stats section, a core part of the profile, was the least reliable part of it.

## Decision

Stats are now generated inside the repo by GitHub Actions and committed as SVGs
(no personal token needed — both actions run on `GITHUB_TOKEN`):

- `profile-summary-cards` → `profile-summary-card-output/tokyonight/*.svg` on
  main, referenced by relative path (served by github.com itself); daily
  schedule + push trigger
- `Platane/snk` contribution snake → `output` branch, embedded via the standard
  `prefers-color-scheme` `<picture>` pattern; weekly schedule

The repo's default workflow permissions were set to read/write to allow the
auto-commits.

## Alternatives considered

- **Self-host github-readme-stats on own Vercel** — keeps the familiar cards,
  but needs a personal access token and a Vercel account (interactive setup we
  cannot do from here), plus an external host to maintain.
- **lowlighter/metrics** — the most powerful generator, but explicitly requires
  a PAT (rejects repository-scoped tokens), same interactive-setup blocker.
- **Keep the public instance** — free until it 503s again, which is the bug.
