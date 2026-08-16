# Instalação

Três níveis, do mais leve ao mais pesado — cada um funciona sem o seguinte.

## 1. Só medir (a régua) — qualquer máquina

```bash
pip install numpy pillow opencv-python-headless
python3 metrologia/bateria_m1_m5.py
```

Mede as folhas de `resultados/` contra a cena de `cena/`. A bateria
autocalibra a convenção de câmera contra o próprio mapa/alpha e ABORTA se a
régua estiver desalinhada (anti-circularidade) — se ela rodar, a medida vale.

## 2. Pintar local (SDXL + ControlNet depth) — GPU ~8 GB+

1. instale o [ComfyUI](https://github.com/comfyanonymous/ComfyUI) e suba na
   porta 8188;
2. baixe `sd_xl_base_1.0.safetensors` e o
   `controlnet-depth-sdxl` do xinsir (Apache-2.0) para as pastas de modelos;
3. ajuste `COMFY_INPUT` em `pintores/rodar_folha_casa.py` para o `input/` do
   seu ComfyUI;
4. `python3 pintores/rodar_folha_casa.py` — 3 sementes fixas, e a régua se
   roda em seguida (nível 1).

## 3. Pintar na fronteira (FLUX.2-dev + Fun-Union) — Modal, H100

O FLUX.2-dev é **gated** na Hugging Face (aceite os termos na sua conta) e a
licença é própria da BFL — leia antes. Custo: H100 por segundo (~50 s de boot
com Volume quente; ~100–180 s por folha 1216×832 em 50 passos).

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

As falhas pagas da bancada (deploy congela secret, gateway corta em ~150 s →
sempre `.remote()`, requirements que quebram) estão documentadas em
`pharo/dominio-bancada-modal.md` — leia antes da primeira subida.

## Regerar a cena (opcional) — Blender 4.x

`cena/cena_folha_casa.py` roda dentro do Blender (Scripting → Run) e regera
proxy, z-buffer, alpha e `casa-geometria.json` ao lado do script. Os insumos
commitados são exatamente os desta cena.

## Registro de processos longos

Os pintores abrem "jobs" via `pintores/registro.py`: por padrão é diário no
stdout; exporte `DELFOS_JOBS=<seu jobs.py>` para plugar um governador próprio
(contrato: `abrir_job/avancar/fechar` — fechar SEMPRE, inclusive em erro).
