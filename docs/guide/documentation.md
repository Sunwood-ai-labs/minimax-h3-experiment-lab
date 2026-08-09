# Documentation language policy

This repository is bilingual by design. Public guidance and experiment entry points must be readable in both English and Japanese.

## Pairing rules

- Root entry points use `README.md` (English) and `README.ja.md` (Japanese).
- VitePress pages use `docs/guide/*.md` (English) and `docs/ja/guide/*.md` (Japanese).
- Experiment records keep the existing `README.md` path for backward-compatible Japanese links and add `README.en.md` as the English counterpart. Both files must link to each other, `experiment.json`, the tracked frame tile, and the direct X/source URL section.
- Global repository guides use an explicit language suffix when the historical filename is already in use, for example `LAB.md` + `LAB.en.md` and `experiments/index.md` + `experiments/index.en.md`.
- Prompts remain in English when English is the model input. Their surrounding explanation and reproducibility metadata still need a Japanese counterpart or a bilingual document.

## Exemptions

Raw benchmark reports, generated simulator payloads, tool-owned `AGENTS.md` / `CLAUDE.md`, and social-copy drafts are evidence or input artifacts rather than reader-facing guides. They are indexed from bilingual pages and are not required to have line-by-line translations.

Every exemption must remain linked from a bilingual index and must not be the only place where an experiment conclusion, public URL, or reproducibility instruction is documented.

## Review checklist

When adding a Markdown file:

1. Decide whether it is public guidance, an experiment entry point, a source/prompt note, or generated evidence.
2. Add the counterpart or record the exemption in the nearest bilingual index.
3. Keep URLs, workflow paths, status labels, timings, hashes, and local-only boundaries identical between language versions.
4. Run `scripts/validate-documentation-parity.ps1` and the normal experiment validator.
