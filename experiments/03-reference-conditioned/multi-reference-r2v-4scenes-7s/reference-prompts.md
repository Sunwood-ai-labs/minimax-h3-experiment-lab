# Reference-sheet generation prompts

日本語のメタデータ説明: [reference-prompts.ja.md](./reference-prompts.ja.md)

These three PNG files are the authoritative inputs for the R2V run. They were generated with the built-in `image_gen` tool and then copied into `runtime/4090/input/`.

## Background sheet

```text
Use case: stylized-concept
Asset type: visual reference sheet for a video-generation R2V experiment
Primary request: Create a clean four-panel environment reference sheet for one consistent location: a near-future Tokyo rooftop greenhouse and observation deck at sunset. Panel 1 wide establishing view, panel 2 entrance and stairs, panel 3 glass greenhouse interior, panel 4 rooftop edge overlooking the city. Keep the same architecture, materials, orange-blue sunset lighting, wet reflective surfaces, and cinematic live-action look across all panels. No people.
Composition/framing: landscape 16:9 sheet, four clearly separated panels, generous margins
Lighting/mood: warm sunset, calm but mysterious
Constraints: no text, no labels, no logos, no watermark, no extra characters
Avoid: collage clutter, inconsistent buildings, distorted architecture, illegible signage
```

## Mina sheet

```text
Use case: stylized-concept
Asset type: character reference sheet for a video-generation R2V experiment
Primary request: Create a clean character reference sheet for Mina, a Japanese woman in her late 20s. She has a short dark bob haircut with one subtle teal streak, a small scar above her right eyebrow, a tan utility jacket over a cream shirt, a rust-red scarf, dark cargo trousers, and black ankle boots. Show the same person and exact outfit in four panels: front full body, three-quarter full body, side profile, and face close-up. Neutral confident expression.
Style/medium: cinematic live-action character design photography, realistic skin and fabric
Composition/framing: landscape 16:9 sheet, four clearly separated panels, neutral light gray studio background, full body visible where requested
Lighting/mood: soft even studio lighting
Constraints: preserve identity, hairstyle, scar, clothing, colors and proportions across every panel; no props
Avoid: text, labels, logos, watermark, extra people, outfit changes, fantasy armor, exaggerated anime style
```

## Ren sheet

```text
Use case: stylized-concept
Asset type: character reference sheet for a video-generation R2V experiment
Primary request: Create a clean character reference sheet for Ren, a Japanese man in his early 30s. He is tall and lean with wavy black hair, a calm serious face, and a small silver earpiece in his left ear. He wears a charcoal long coat over an olive knit sweater, dark trousers, and worn brown boots. Show the same person and exact outfit in four panels: front full body, three-quarter full body, side profile, and face close-up.
Style/medium: cinematic live-action character design photography, realistic skin and fabric
Composition/framing: landscape 16:9 sheet, four clearly separated panels, neutral light gray studio background, full body visible where requested
Lighting/mood: soft even studio lighting
Constraints: preserve identity, hairstyle, earpiece, clothing, colors and proportions across every panel; no props
Avoid: text, labels, logos, watermark, extra people, outfit changes, fantasy armor, exaggerated anime style
```
