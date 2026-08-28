#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cirurgia da obediência — rodada P1–P3 (pesquisa/dominio-cirurgia-obediencia-flux2.md).

UMA variável por protótipo, contra a linha de base da mesa (z-buffer cru):
  P1  controle = depth ESTIMADO sobre o nosso proxy (DA-V2-Small, Apache — H1)
  P2  controle = z-buffer cru + proxy como REFERÊNCIA (via predict_*_ref oficial)
  P3  controle = canny(proxy) (elemento fino: a aresta carrega o poste)

Constantes seladas da mesa: prompt neutro EXATO, 3 sementes, 1216×832,
escala 0,75, guidance 4,0, 50 passos. Régua: M1–M3 da bateria calibrada.

Roda:  o ambiente virtual do projeto rodar_prototipos.py   (precisa do pacote modal)
"""
import base64
import hashlib
import json
import os
import sys
import time

import registro as _j

AQUI = os.path.dirname(os.path.abspath(__file__))
PIPELINE = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(RAIZ, "metrologia"))


RAIZ = os.path.dirname(AQUI)
PROXY = os.path.join(RAIZ, "cena", "casa-proxy.png")
ZBUF = os.path.join(RAIZ, "cena", "casa-profundidade-0001.png")
SAIDA = os.path.join(RAIZ, "resultados", "prototipos")
SEMENTES = [20260815, 20260816, 20260817]
PROMPT = ("a simple wooden stilt house with a pitched thatch roof standing on "
          "open flat ground, Pantanal wetland dwelling, weathered timber walls, "
          "painterly concept art, soft diffuse daylight, muted earth palette, "
          "loose brushwork, atmospheric depth")
BASE = {"prompt": PROMPT, "width": 1216, "height": 832,
        "control_context_scale": 0.75, "guidance_scale": 4.0,
        "num_inference_steps": 50}
JOB = "guariba-cirurgia-p1p3"


def b64_de(caminho):
    with open(caminho, "rb") as f:
        return base64.b64encode(f.read()).decode()


def salvar(caminho, b64):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "wb") as f:
        f.write(base64.b64decode(b64))


def preparar_canny():
    import cv2
    img = cv2.imread(PROXY, cv2.IMREAD_GRAYSCALE)
    borda = cv2.Canny(img, 100, 200)          # limiares padrão, declarados
    dest = os.path.join(SAIDA, "insumos", "P3-canny-proxy.png")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    cv2.imwrite(dest, borda)
    return dest


def medir_tudo():
    """M1–M3 com a MESMA régua da bateria (importada, não copiada)."""
    import numpy as np
    from PIL import Image

    import bateria_m1_m5 as bat

    geo = json.load(open(bat.GEO, encoding="utf-8"))
    mapa = np.array(Image.open(bat.MAPA).convert("L"))
    alpha = np.array(Image.open(bat.ALPHA).convert("L").resize((geo["W"], geo["H"])))
    conv, pts, _ = bat.escolher_convencao(geo, mapa, alpha)
    if conv is None:
        raise SystemExit("régua desalinhada")
    R = np.array(geo["rotacao"])
    l, v = bat.horizonte_e_vertical(R, geo["focal_px"], geo["W"], geo["H"])
    ctx = (pts["chao_casa"], pts["cumeeira"], pts["poste_base"],
           pts["poste_topo"], l, v)

    linhas = []
    import glob
    for f in sorted(glob.glob(os.path.join(SAIDA, "P?-*.png"))):
        g = np.array(Image.open(f).convert("L"))
        r = {"folha": os.path.basename(f),
             "M1": bat.m1_regua(g, ctx),
             "M2": bat.m2_largura(g, alpha),
             "M3": bat.m3_silhueta(g, alpha)}
        linhas.append(r)
        resumo = " ".join(f"{k}:{'✓' if r[k]['passa'] else '✗'}"
                          for k in ("M1", "M2", "M3"))
        det1 = r["M1"].get("erro_pct", r["M1"].get("motivo"))
        print(f"{r['folha']:28s} {resumo}  M1={det1}  "
              f"M2={r['M2'].get('desvio_px')}px  M3={r['M3'].get('mediana_px')}px")
    with open(os.path.join(SAIDA, "resultado-p1p3.json"), "w", encoding="utf-8") as f:
        json.dump(linhas, f, ensure_ascii=False, indent=1)
    return linhas


if __name__ == "__main__":
    import modal
    Cls = modal.Cls.from_name("mesa-fronteira-flux2", "MesaFronteiraFlux2")
    app = Cls()

    proxy_b64 = b64_de(PROXY)
    zbuf_b64 = b64_de(ZBUF)

    _j.abrir_job(JOB, "Cirurgia da obediência: P1–P3 (9 folhas + insumos)", 10,
                 dono="Modal: FLUX.2-dev + Fun-Union (H100)",
                 detalhe="1 variável por protótipo; régua M1–M3")
    feito = 0
    try:
        # insumo P1: depth estimado sobre o proxy (no worker)
        print("P1: estimando depth do proxy no worker…", flush=True)
        est = app.estimar_depth.remote({"image_b64": proxy_b64})
        p1_depth = est["depth_b64"]
        salvar(os.path.join(SAIDA, "insumos", "P1-depth-estimado.png"), p1_depth)
        canny_path = preparar_canny()
        canny_b64 = b64_de(canny_path)
        feito += 1
        _j.avancar(JOB, feito, detalhe="insumos prontos (depth estimado + canny)")

        planos = [
            ("P1", {"control_image_b64": p1_depth}),
            ("P2", {"control_image_b64": zbuf_b64,
                    "reference_image_b64": proxy_b64}),
            ("P3", {"control_image_b64": canny_b64}),
        ]
        manif = os.path.join(SAIDA, "manifesto.jsonl")
        for nome, extra in planos:
            for s in SEMENTES:
                corpo = dict(BASE, seed=s, **extra)
                t0 = time.time()
                saida = app.gerar_remoto.remote(corpo)
                dt = time.time() - t0
                dest = os.path.join(SAIDA, f"{nome}-{s}.png")
                salvar(dest, saida["image_b64"])
                with open(manif, "a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "prototipo": nome, "seed": s,
                        "segundos": round(dt, 1),
                        "sha256": hashlib.sha256(
                            base64.b64decode(saida["image_b64"])).hexdigest(),
                        "params": {k: v for k, v in corpo.items()
                                   if not k.endswith("_b64")},
                        "quando": time.strftime("%Y-%m-%d %H:%M:%S"),
                    }, ensure_ascii=False) + "\n")
                feito += 1
                _j.avancar(JOB, feito, detalhe=f"{nome}-{s} ({dt:.0f}s)")
                print(f"ok {nome}-{s} em {dt:.0f}s", flush=True)

        print("\n════ RÉGUA M1–M3 ════", flush=True)
        medir_tudo()
        _j.fechar(JOB, "ok")
    except BaseException as e:
        _j.fechar(JOB, f"erro: {e}")
        raise
