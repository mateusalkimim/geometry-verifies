<!-- idioma: linha gerada por i18n.py -->
> [!NOTE]
> ### 🇧🇷 **[Leia esta página em português →](INSTALACAO.md)**

# Installation

Three levels, from lightest to heaviest — each one works without the next.

## 1. Just Measure (the Ruler) — Any Machine

```bash
pip install numpy pillow opencv-python-headless
python3 metrologia/bateria_m1_m5.py
```

Measures the sheets from `resultados/` against the scene in `cena/`. The battery  
autocalibrates the camera convention against its own map/alpha and ABORTS if the  
ruler is misaligned (anti-circularity) — if it runs, the measurement is valid.

## 2. Paint Local (SDXL + ControlNet Depth) — GPU ~8 GB+

1. Install the [ComfyUI](https://github.com/comfyanonymous/ComfyUI) and launch on port 8188;  
2. Download `sd_xl_base_1.0.safetensors` and the  
   `controlnet-depth-sdxl` from xinsir (Apache-2.0) into the model folders;  
3. Adjust `COMFY_INPUT` in `pintores/rodar_folha_casa.py` to your ComfyUI's `input/`;  
4. `python3 pintores/rodar_folha_casa.py` — 3 fixed seeds, and the ruler runs next (level 1).

## 3. Painting on the Border (FLUX.2-dev + Fun-Union) — Modal, H100

The FLUX.2-dev is **gated** on Hugging Face (accept the terms on your account) and the license is proprietary to BFL — read before. Cost: H100 per second (~50 s boot with Volume hot; ~100–180 s per page 1216×832 in 50 steps).

```bash
pip install modal
modal token new
modal secret create huggingface --from-dotenv <arquivo .env fora do repo com HF_TOKEN=...>
modal deploy pintores/app_flux2_depth_modal.py
python3 pintores/rodar_prototipos.py      # a escada P1–P3
python3 pintores/rodar_p4.py              # a receita combinada
python3 pintores/rodar_p4_crepusculo.py   # a segunda luz
modal app stop mesa-fronteira-flux2 --yes # descer ao terminar (custo!)
```

Paid failures of the bench (deploy freezes secret, gateway cuts at ~150 s →  
always `.remote()`, requirements that break) are documented in  
`pesquisa/dominio-bancada-modal.md` — read before the first launch.

## Regenerate the Scene (Optional) — Blender 4.x

`scene/scene_page_house.py` runs inside Blender (Scripting → Run) and regenerates proxy, z-buffer, alpha, and `house-geometry.json` next to the script. The committed inputs are exactly those of this scene.

## Long Process Logging

The painters open "jobs" via `pintores/registro.py`: by default, it's daily in  
stdout; export `DELFOS_JOBS=<your jobs.py>` to plug in a custom governor  
(contract: `open_job/advance/close` — close ALWAYS, even on error).