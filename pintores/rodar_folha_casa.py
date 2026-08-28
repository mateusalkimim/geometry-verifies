#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PRIMEIRA FOLHA — pinta a casa do plano 9.2 na prancheta.

    python3 rodar_folha_casa.py

A PILHA É A DO SEMINÁRIO, NÚMERO POR NÚMERO: SDXL 1.0 + controlnet-depth-sdxl
do xinsir, 28 passos, cfg 6,5, força 0,8, euler/normal, 1216x832. Não é
nostalgia — é a única pilha deste projeto com resultado medido a favor:

  - venceu a comparação cega contra o condicionamento (linha de base, 3 de 3);
  - é NÃO-DESTILADA com CFG de verdade, que é o regime de BORDA PERDIDA pela
    lei da destilação (o Z-Image só existe como Turbo, e Turbo dá granito);
  - obedeceu à geometria com mediana de 0,0 px no seminário.

UMA VARIÁVEL POR RODADA. Aqui muda só uma coisa contra o seminário: o insumo
deixa de ser um cubo de estúdio e passa a ser um ELEMENTO DA OBRA com chão em
grade sob ele. Luz neutra; crepúsculo é a rodada 2.

TRÊS SEMENTES. Uma folha só não distingue acerto de sorte — e o piso de ruído
entre sementes (20,60) foi medido como maior que o efeito de trocar a régua
(8,53). Sem repetição não há leitura.
"""
import json
import os
import shutil
import sys
import time
import urllib.parse
import urllib.request

import registro as _j

API = "http://127.0.0.1:8188"
AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(os.path.dirname(AQUI), "resultados")
COMFY_INPUT = os.path.expanduser("~/comfyui/ComfyUI/input")
MAPA = "casa-profundidade.png"
SEMENTES = [20260815, 20260816, 20260817]
JOB = "guariba-folha-casa"

# O prompt descreve O QUE A COISA É, não como a câmera está. Perspectiva,
# posição e escala vêm do mapa de profundidade — pedir "wide angle" ou
# "dramatic perspective" seria justamente o erro caro: a tolerância do fov é
# assimétrica e o excesso de perspectiva é pego em quatro segundos.
PROMPT = ("a simple wooden stilt house with a pitched thatch roof standing on "
          "open flat ground, Pantanal wetland dwelling, weathered timber walls, "
          "painterly concept art, soft diffuse daylight, muted earth palette, "
          "loose brushwork, atmospheric depth")
NEG = ("photograph, 3d render, cgi, cartoon outline, text, watermark, people, "
       "logo, frame, border, blurry, lowres")


def grafo(seed, pref):
    return {
     "1": {"class_type": "CheckpointLoaderSimple",
           "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
     "2": {"class_type": "CLIPTextEncode",
           "inputs": {"clip": ["1", 1], "text": PROMPT}},
     "3": {"class_type": "CLIPTextEncode",
           "inputs": {"clip": ["1", 1], "text": NEG}},
     "4": {"class_type": "ControlNetLoader",
           "inputs": {"control_net_name": "controlnet-depth-sdxl-xinsir.safetensors"}},
     "5": {"class_type": "LoadImage", "inputs": {"image": MAPA}},
     "6": {"class_type": "ControlNetApplyAdvanced",
           "inputs": {"positive": ["2", 0], "negative": ["3", 0],
                      "control_net": ["4", 0], "image": ["5", 0],
                      "strength": 0.8, "start_percent": 0.0,
                      "end_percent": 1.0}},
     "7": {"class_type": "EmptyLatentImage",
           "inputs": {"width": 1216, "height": 832, "batch_size": 1}},
     "8": {"class_type": "KSampler",
           "inputs": {"model": ["1", 0], "positive": ["6", 0],
                      "negative": ["6", 1], "latent_image": ["7", 0],
                      "seed": seed, "steps": 28, "cfg": 6.5,
                      "sampler_name": "euler", "scheduler": "normal",
                      "denoise": 1.0}},
     "9": {"class_type": "VAEDecode",
           "inputs": {"samples": ["8", 0], "vae": ["1", 2]}},
     "10": {"class_type": "SaveImage",
            "inputs": {"images": ["9", 0], "filename_prefix": pref}}}


def rodar(seed, alvo):
    r = urllib.request.Request(
        API + "/prompt",
        json.dumps({"prompt": grafo(seed, os.path.basename(alvo))}).encode(),
        {"Content-Type": "application/json"})
    pid = json.load(urllib.request.urlopen(r))["prompt_id"]
    t0 = time.time()
    while time.time() - t0 < 900:
        h = json.load(urllib.request.urlopen(API + f"/history/{pid}"))
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("status_str") == "error":
                raise RuntimeError(str(st)[:400])
            for o in h[pid].get("outputs", {}).values():
                for im in o.get("images", []):
                    q = urllib.parse.urlencode(
                        {"filename": im["filename"],
                         "subfolder": im.get("subfolder", ""),
                         "type": im.get("type", "output")})
                    with urllib.request.urlopen(API + "/view?" + q) as src, \
                            open(alvo, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    return time.time() - t0
        time.sleep(2)
    raise TimeoutError(f"semente {seed} passou de 900 s")


if __name__ == "__main__":
    origem = os.path.join(os.path.dirname(AQUI), "cena", "casa-profundidade-0001.png")
    if not os.path.exists(origem):
        sys.exit(f"mapa de profundidade ausente: {origem}")
    shutil.copy(origem, os.path.join(COMFY_INPUT, MAPA))

    _j.abrir_job(JOB, "A primeira folha: a casa do plano 9.2", len(SEMENTES),
                 dono="GPU: SDXL 1.0 + ControlNet depth (xinsir)",
                 detalhe="prancheta com chão em grade · 3 sementes")
    feito = 0
    try:
        for s in SEMENTES:
            alvo = os.path.join(SAIDA, f"folha-casa-{s}.png")
            if os.path.exists(alvo):
                feito += 1
                _j.avancar(JOB, feito, f"{s} (já existia)")
                continue
            dt = rodar(s, alvo)
            feito += 1
            _j.avancar(JOB, feito, f"semente {s} · {feito}/{len(SEMENTES)}")
            print(f"semente {s}: ok ({dt:.0f}s)", flush=True)
    except BaseException as e:
        _j.fechar(JOB, f"erro: {e}")
        raise
    _j.fechar(JOB, f"ok: {feito}/{len(SEMENTES)} folhas")
    print(f"\nfolhas em {SAIDA}")
