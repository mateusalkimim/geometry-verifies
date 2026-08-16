#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P4 — a cirurgia combinada: o que cada via de P1–P3 provou, junto.

controle  = depth ESTIMADO do proxy (P1: régua fina a −0,25/+0,49%)
            + POSTE ENXERTADO do z-buffer (exato por construção no elemento
            fino que o estimador dilui), pintado no BRILHO da parede estimada
            (mesma escala do mapa hospedeiro, sem costura de contraste);
referência = proxy render (P2: travou parede a 4 px).

3 folhas, sementes/prompt/params selados. Régua M1–M3 da bateria.
Roda:  ~/venvs/fal/bin/python rodar_p4.py
"""
import base64
import hashlib
import json
import os
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from rodar_prototipos import (BASE, PROXY, SAIDA, SEMENTES, ZBUF,  # noqa: E402
                              _j, b64_de, medir_tudo, salvar)

JOB = "guariba-cirurgia-p4"


def compor_mapa():
    import numpy as np
    from PIL import Image

    est = np.array(Image.open(
        os.path.join(SAIDA, "insumos", "P1-depth-estimado.png")).convert("L")
    ).astype(np.float32)
    zb = np.array(Image.open(ZBUF).convert("L")).astype(np.float32)

    # poste no z-buffer: SÓ a estrutura fina — janela apertada em colunas
    # (852±30) e linhas ACIMA do contato com o chão (318–590 medidos na
    # bateria), com piso de valor p/ excluir o gradiente de chão. A 1ª versão
    # desta máscara vazou 54k px de chão (folha descartada, job fechado com
    # erro): janela larga + limiar baixo = enxerto que pinta o terreno.
    mask = np.zeros_like(zb, dtype=bool)
    mask[250:592, 822:882] = zb[250:592, 822:882] > 150

    # brilho do enxerto = mediana da PAREDE estimada (mesma profundidade do
    # poste por construção da cena) — amostra o miolo da casa
    parede = float(np.median(est[380:520, 300:600]))
    comp = est.copy()
    comp[mask] = parede
    dest = os.path.join(SAIDA, "insumos", "P4-depth-composto.png")
    Image.fromarray(comp.astype("uint8")).save(dest)
    n = int(mask.sum())
    print(f"enxerto: {n} px de poste pintados a {parede:.0f} (parede estimada)")
    return dest


if __name__ == "__main__":
    import modal
    Cls = modal.Cls.from_name("mesa-fronteira-flux2", "MesaFronteiraFlux2")
    app = Cls()

    composto = compor_mapa()
    controle_b64 = b64_de(composto)
    proxy_b64 = b64_de(PROXY)

    _j.abrir_job(JOB, "Cirurgia P4: estimado+enxerto do poste+referência (3 folhas)",
                 3, dono="Modal: FLUX.2-dev + Fun-Union (H100)",
                 detalhe="combinação do que P1/P2 provaram")
    feito = 0
    try:
        manif = os.path.join(SAIDA, "manifesto.jsonl")
        for s in SEMENTES:
            corpo = dict(BASE, seed=s, control_image_b64=controle_b64,
                         reference_image_b64=proxy_b64)
            t0 = time.time()
            saida = app.gerar_remoto.remote(corpo)
            dt = time.time() - t0
            salvar(os.path.join(SAIDA, f"P4-{s}.png"), saida["image_b64"])
            with open(manif, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "prototipo": "P4", "seed": s, "segundos": round(dt, 1),
                    "sha256": hashlib.sha256(
                        base64.b64decode(saida["image_b64"])).hexdigest(),
                    "params": {k: v for k, v in corpo.items()
                               if not k.endswith("_b64")},
                    "insumo": "P4-depth-composto.png + referencia proxy",
                    "quando": time.strftime("%Y-%m-%d %H:%M:%S"),
                }, ensure_ascii=False) + "\n")
            feito += 1
            _j.avancar(JOB, feito, detalhe=f"P4-{s} ({dt:.0f}s)")
            print(f"ok P4-{s} em {dt:.0f}s", flush=True)

        print("\n════ RÉGUA M1–M3 (P1–P4) ════", flush=True)
        medir_tudo()
        _j.fechar(JOB, "ok")
    except BaseException as e:
        _j.fechar(JOB, f"erro: {e}")
        raise
