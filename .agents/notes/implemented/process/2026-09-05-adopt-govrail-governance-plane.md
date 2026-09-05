# Agent Note: Adopt govrail governance plane

Status: implemented

## Problem

The profile repo's core promise is that `README.md` (en) and `README.zh-CN.md`
(zh) stay in sync, but nothing enforced it — the two sides could drift after any
edit, and nothing would notice. "Why is the profile structured this way?" lived
only in chat history.

## Decision

The repo is governed by govrail (`gov init --hooks --ci`): rules in
`.gov/rules.md`, a pre-push hook and GitHub Actions workflow both run `gov run`.
The shipped `pairing` gate is baselined via `README.i18n.yaml` (git blob hashes
of both sides) and made enforcing by removing `allowFailure`, so any one-sided
edit fails loud at push and CI.

## Alternatives considered

- **Trust + manual review** — zero setup, but drift ships silently; it is
  exactly the "on their honor" mode govrail exists to replace.
- **Hand-rolled CI script diffing the two READMEs** — checks only line counts
  at best, reinvents blob-hash pairing, and has no notes/decisions record.
- **Single bilingual README** — rejected by product choice: the profile page
  must show English only (the zh side lives in a separate file), which is also
  why the pair needs a mechanical sync guard at all.
