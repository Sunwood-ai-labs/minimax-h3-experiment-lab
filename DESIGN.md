# MiniMax-H3 Experiment Lab — Montage Design

> 日本語版: [DESIGN.ja.md](./DESIGN.ja.md)

## Style Prompt

Dark cinematic experiment-lab editorial: real generated frames are the hero, while restrained warm measurement accents and cool data labels make the comparison legible at a glance. The composition should feel like a reproducible benchmark board rather than a flashy promo. Keep the footage dominant, use translucent surfaces for context, and preserve generous contrast for Japanese and Latin text.

## Colors

- `#080b11` — deep blue-black canvas
- `#141b27` — translucent lab panel
- `#ffd166` — primary measurement accent and headline marker
- `#ff8a5c` — experiment emphasis and timeline cue
- `#85caff` — technical metadata and links
- `#7be3ac` — successful result / no-OOM status

## Typography

- Display and explanatory copy: `IBM Plex Sans`, with Japanese system fallback.
- Measurements and sampler labels: `IBM Plex Mono`, with monospace fallback.
- Use 72px+ display headlines, 24px+ explanatory copy, and 18px+ data labels at 1920×1080.
- Use tabular numerals for timings, dimensions, and benchmark values.

## Motion Rules

- The four real videos begin together so the viewer can compare the same time range.
- Labels enter in a short stagger; the overview bar remains readable and stable.
- No decorative motion may obscure the generated frames or benchmark values.

## What NOT to Do

- Do not replace any generated video with AI-created visual filler.
- Do not use a neon gradient, generic stock imagery, or a glossy product-promo treatment.
- Do not shrink experiment labels below readable video-scale typography.
- Do not claim a speedup without naming the sampler and measured time.
