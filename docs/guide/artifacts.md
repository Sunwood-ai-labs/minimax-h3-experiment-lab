# Public artifacts and media boundary

The repository separates durable public evidence from large local capture files. This is intentional: a fresh clone should be useful without silently pretending that an ignored MP4 is downloadable.

## What a fresh clone contains

| Artifact | Public clone | Where to start |
|---|---:|---|
| Experiment README | Yes | `experiments/<category>/<slug>/README.md` |
| Machine-readable record | Yes | `experiment.json` |
| Frame tile | Yes | `previews/contact-sheet.jpg` |
| Tile manifest | Yes | `previews/contact-sheet.json` |
| Reference sheets and workflows | When used by the experiment | The experiment directory |
| Generated MP4/audio | Usually no (`local-only`) | Path, media facts, and SHA-256 remain in the record |
| Model weights and dependency caches | No | Download with the documented bootstrap flow |

The [visual gallery](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/master/experiments/README.md) is the fastest way to inspect behavior. The [experiment ledger](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/master/experiments/index.md) is the complete navigation table.

## Why tiles are canonical

A tile samples the actual generated source video at recorded timestamps. It is not a replacement generation or a hand-selected illustration. Its manifest preserves the source path, byte count, SHA-256, dimensions, frame rate, duration, and sampling order. This makes temporal behavior reviewable in GitHub and in an X thread even when the original video is kept local.

## Simulator behavior

The X simulators under `sunwood-x-simulator-*` model the long-thread layout and retain the original prompt, timing, and hash information in `payload.json`. Large video sources are local-only. When a fresh clone cannot load a video asset, the simulator uses a tracked poster or experiment tile so the page still communicates the tested behavior and the provenance text says exactly what is unavailable.

## Fresh-clone checks

```powershell
git clone https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab.git
cd minimax-h3-experiment-lab
pwsh -File .\scripts\validate-experiment-lab.ps1
pwsh -File .\scripts\validate-public-media.ps1
docker compose config --quiet
```

A passing validation means the public records, tracked tiles, manifests, and Markdown media links are internally consistent. It does not mean that model weights or local-only generated videos have been bundled.
