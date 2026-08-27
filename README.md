<!-- idioma: linha gerada por i18n.py -->
> [!NOTE]
> ### 🇧🇷 **[Leia esta página em português →](README.pt-BR.md)**

# geometry-verifies

*3D disposes, diffusion paints, geometry verifies — a matte painting pipeline
where every AI-painted image must pass a pre-registered geometric ruler before
it counts. Full docs in Portuguese below; the research diary lives in
[`pharo/`](pharo/).*

**3D arranges, diffusion paints, geometry verifies.** This repository is the  
AI-assisted matte painting method of an original production (the series  
**Guariba**): a lightweight scene in Blender arranges the element and exports  
depth, alpha, and the exact camera; a diffusion model paints the element  
conditioned by that map; and **single-view metrology** (Criminisi, Reid &  
Zisserman, 2000) measures the painted sheet against the geometric truth —  
without knowing the focal length. The painting is free; the geometry is  
bound. Pre-registered ruler, blind judgment, receipt of each claim. **AI is  
backdrop and reference; final plan is painted — boundary declared.**

## Quick Start

```bash
git clone https://github.com/mateusalkimim/geometry-verifies  
cd geometry-verifies  

# measure the included leaves against the included scene (only numpy/PIL/OpenCV):  
python3 metrologia/bateria_m1_m5.py
```

The battery prints M1–M5 per sheet: ratio of heights (eq. 9, ≤2% error),  
width on the reference line (≤12 px), silhouette (median ≤4 px), black of  
twilight (p1 ≥ 8) and corner ghost. The installation details and the  
painting paths (SDXL local via ComfyUI; FLUX.2 on H100 via Modal) are in  
[`docs/INSTALACAO.md`](docs/INSTALACAO.en.md).

## What's here

| folder | content |  
|---|---|  
| `metrologia/` | the ruler: `metrologia_vista_unica.py` (eq. 9) and `bateria_m1_m5.py` (M1–M5 with anti-circular autocalibration against the map itself) |  
| `cena/` | the 3D that arranges: Blender scene script + the 4 exact inputs (proxy, z-buffer, alpha, camera geometry) |  
| `pintores/` | the ones who paint: local SDXL+ControlNet (ComfyUI) and the boundary bench FLUX.2+Fun-Union (Modal, H100) with surgery P1–P4 |  
| `resultados/` | the measured sheets (SDXL and P1–P4 in the two lights), JSONs of the ruler and manifesto with sha256 |  
| `pharo/` | the research notebook: pre-registration of the table, result, the surgery of obedience, and the bench — with glossary in `pharo/LEIA-ME.md` |

## The place in the larger cycle

This method is used in a production where **nothing generative renders the final plane**. The flow covered here is that of *storyboard/concept*: the sheet that passes through the ruler becomes a composition reference — the film continues to be closed by hand. The complete story (why the synthetic z-buffer fails in a ControlNet of boundary, and the surgery that makes it obey) is in `pharo/dominio-cirurgia-obediencia.md`.

## Provenance and guarantees

- **No secrets in the tree**: tokens live in `.env` outside the repo (Modal  
  Secrets/environment variables); the code documents the path, never the value;  
- **Licenses granted at source**: SDXL (CreativeML Open RAIL++-M),  
  ControlNet xinsir (Apache-2.0), FLUX.2-dev (gated, proprietary license from  
  BFL — read before use), Fun-Controlnet-Union (alibaba-pai), Depth Anything  
  V2 **Small** (Apache-2.0; the Large is CC-BY-NC and was vetoed for that);  
- **Nothing here was trained with third-party data**: the repository is method  
  and measurement, not a model;  
- the images of `cena/` and `resultados/` are the author's work (scene-test  
  scenario of production), licensed under CC BY 4.0 — see `LICENSE-MEDIA`.

## State and open tables

- complete ruler (M1–M5) passing 3/3 on both lights with recipe P4  
  (depth estimated + grafting of the fine element + reference) — receipts in  
  `resultados/`;  
- open: the aesthetic cost of the reference image (the flatness of the proxy in  
  the brushstroke) awaits blind judgment; fine-tuning of ControlNet with own  
  synthetic pairs (P6) is the deep surgery not yet initiated;  
- this repo is a published excerpt from a larger notebook and continues to live  
  alongside the production.

---  
Code under [MIT](LICENSE) · images and documents under [CC BY 4.0](LICENSE-MEDIA) ·  
author: [Mateus Alkimim](https://github.com/mateusalkimim)