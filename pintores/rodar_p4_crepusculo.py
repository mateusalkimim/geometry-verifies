#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P4 no crepúsculo — a receita que fechou a régua (estimado + enxerto do poste
+ proxy como referência), agora na SEGUNDA luz do selo. O que se mede:

  M1–M3  a geometria segura na luz nova?
  M4     o critério do crepúsculo (p1 ≥ 8, mediana ≥ 25 — "dark but not black")
  M5     fantasma de canto, com recortes p/ conferência a olho
  D1     INDICADOR mecânico de direção da luz (esq vs dir) — registra a
         leitura; o julgamento da luz é do autor, a olho.

Insumos REUSADOS de disco (mesma proveniência da rodada P4 neutra):
prototipos/insumos/P4-depth-composto.png + casa-proxy.png como referência.
Prompt = o crepúsculo SELADO do console (idêntico ao do braço B da mesa).

Roda:  o ambiente virtual do projeto rodar_p4_crepusculo.py
"""
import base64
import hashlib
import json
import os
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from rodar_prototipos import (BASE, PROXY, SAIDA, SEMENTES,  # noqa: E402
                              _j, b64_de, salvar)

JOB = "guariba-cirurgia-p4-crepusculo"
COMPOSTO = os.path.join(SAIDA, "insumos", "P4-depth-composto.png")

# o SELO do crepúsculo (console/servidor.py, PROMPTS["crepusculo"] — idêntico)
PROMPT_CREPUSCULO = (
    "a simple wooden stilt house with a pitched thatch roof standing on open "
    "flat ground, Pantanal wetland dwelling, weathered timber walls, "
    "at dusk, low golden sunset light from the left, warm glow on the thatch "
    "edges, shadows bluer than usual with readable local color, dark ground "
    "silhouette but not black, sky gradient from deep blue above through soft "
    "yellow to dull red at the horizon, warm glow strongest at the horizon, "
    "soft violet haze, painterly concept art, muted palette, loose brushwork, "
    "atmospheric depth")


def d1_indicador(rgb):
    """Leitura, não verificação: luz pedida 'from the left' → terço esquerdo do céu
    (metade de cima) mais claro que o direito. Devolve razão esq/dir."""
    import numpy as np
    topo = rgb[: rgb.shape[0] // 2].astype(float).mean(axis=2)
    w = topo.shape[1]
    esq, dir_ = float(topo[:, : w // 3].mean()), float(topo[:, -w // 3:].mean())
    return {"esq": round(esq, 1), "dir": round(dir_, 1),
            "razao_esq_dir": round(esq / dir_, 3),
            "lado_mais_claro": "esquerda" if esq > dir_ else "direita"}


def medir(caminhos):
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
    for f in caminhos:
        nome = os.path.basename(f).replace(".png", "")
        rgb = np.array(Image.open(f).convert("RGB"))
        g = np.array(Image.open(f).convert("L"))
        r = {"folha": os.path.basename(f), "luz": "crepusculo",
             "M1": bat.m1_regua(g, ctx),
             "M2": bat.m2_largura(g, alpha),
             "M3": bat.m3_silhueta(g, alpha),
             "M4": bat.m4_preto(g, alpha),
             "M5": bat.m5_fantasma(rgb, nome),
             "D1_indicador": d1_indicador(rgb)}
        linhas.append(r)
        resumo = " ".join(f"{k}:{'✓' if r[k]['passa'] else '✗'}"
                          for k in ("M1", "M2", "M3", "M4", "M5"))
        print(f"{r['folha']:32s} {resumo}")
        print(f"    M1={r['M1'].get('erro_pct', r['M1'].get('motivo'))}%  "
              f"M2={r['M2'].get('desvio_px')}px  M3={r['M3'].get('mediana_px')}px  "
              f"M4 p1={r['M4']['p1']} med={r['M4']['mediana']}  "
              f"D1 {r['D1_indicador']['lado_mais_claro']} "
              f"({r['D1_indicador']['razao_esq_dir']})")
    dest = os.path.join(SAIDA, "resultado-p4-crepusculo.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(linhas, fh, ensure_ascii=False, indent=1)
    print(f"salvo em {dest}")
    return linhas


if __name__ == "__main__":
    import modal
    Cls = modal.Cls.from_name("mesa-fronteira-flux2", "MesaFronteiraFlux2")
    app = Cls()

    controle_b64 = b64_de(COMPOSTO)
    proxy_b64 = b64_de(PROXY)

    _j.abrir_job(JOB, "Cirurgia P4 no crepúsculo: 3 folhas + régua M1–M5/D1",
                 3, dono="Modal: FLUX.2-dev + Fun-Union (H100)",
                 detalhe="receita P4 na segunda luz do selo")
    feito = 0
    try:
        manif = os.path.join(SAIDA, "manifesto.jsonl")
        gerados = []
        for s in SEMENTES:
            corpo = dict(BASE, prompt=PROMPT_CREPUSCULO, seed=s,
                         control_image_b64=controle_b64,
                         reference_image_b64=proxy_b64)
            t0 = time.time()
            saida = app.gerar_remoto.remote(corpo)
            dt = time.time() - t0
            dest = os.path.join(SAIDA, f"P4-crepusculo-{s}.png")
            salvar(dest, saida["image_b64"])
            gerados.append(dest)
            with open(manif, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "prototipo": "P4-crepusculo", "seed": s,
                    "segundos": round(dt, 1),
                    "sha256": hashlib.sha256(
                        base64.b64decode(saida["image_b64"])).hexdigest(),
                    "params": {k: v for k, v in corpo.items()
                               if not k.endswith("_b64")},
                    "insumo": "P4-depth-composto.png + referencia proxy",
                    "quando": time.strftime("%Y-%m-%d %H:%M:%S"),
                }, ensure_ascii=False) + "\n")
            feito += 1
            _j.avancar(JOB, feito, detalhe=f"P4-crepusculo-{s} ({dt:.0f}s)")
            print(f"ok P4-crepusculo-{s} em {dt:.0f}s", flush=True)

        print("\n════ RÉGUA M1–M5 + D1 (crepúsculo) ════", flush=True)
        medir(gerados)
        _j.fechar(JOB, "ok")
    except BaseException as e:
        _j.fechar(JOB, f"erro: {e}")
        raise
