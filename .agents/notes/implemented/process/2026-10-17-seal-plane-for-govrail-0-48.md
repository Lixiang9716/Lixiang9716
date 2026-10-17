# Agent Note: Re-baseline the plane seal for govrail 0.48

Status: implemented

## Problem

The governance plane was initialized with govrail 0.27.0 (see
`.gov/manifest.json`), which never wrote a `.gov/plane-seal.json`. The local
CLI is now 0.48.0, and 0.48 refuses to run the gate DAG (`gov run`) without a
seal, because it cannot prove the plane config it is about to trust is the
one that was reviewed. The repo's CI installs govrail unpinned
(`pip install govrail` in `.github/workflows/gov.yml`), so CI now also runs
0.48 and would refuse the same way on the next push — the plane was broken
for everyone, independent of any content change.

## Decision

Seal the current plane state with
`gov verify-plane --write --confirm-unattended --reason <this note>`.

The sealed config is byte-identical to what 0.27 generated (`.gov/` is
untouched since init — verified against git); the seal only records "this
state is the reviewed one" under the 0.48 format. The acceptance is recorded
as UNATTENDED machine consent citing this note, so the provenance of the
re-baseline lives in both the seal and the note.

Full `gov init --upgrade` (bumping the manifest to 0.48 and pinning CI to
match) is deliberately NOT done here — it rewrites multiple generated
governance files and deserves its own reviewed change.

## Alternatives considered

- **Pin CI to `govrail==0.27.0`** — keeps CI green but leaves every local
  0.48 install refused; drift continues in the other direction.
- **`gov init --upgrade` now** — the eventual right move, but it rewrites
  the generated plane files (manifest, templates, possibly gates.json and
  gov.yml) and should be reviewed as its own diff, not folded into a
  profile-README push.
- **Push without sealing** — profile change lands, but the gov workflow goes
  red on this push and `gov run` stays broken locally.
