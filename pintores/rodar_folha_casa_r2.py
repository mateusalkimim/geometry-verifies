#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RODADA 2 da folha da casa — o crepúsculo, com o Gurney aberto na mesa.

    python3 rodar_folha_casa_r2.py

UMA VARIÁVEL: o prompt de luz. O mapa de profundidade não carrega luz, então a
cena, a câmera, o grafo e as três sementes são EXATAMENTE os da rodada 1 — o
que mudar entre as rodadas é atribuível só à luz pedida.

REGRA CONSULTADA ANTES DE PRODUZIR (mouseion/_dissecado/gurney-color-light,
"Color Changes at Day's End" + "Sunsets"), cada linha do prompt rastreada:

  "Forms lit by the setting sun take on a golden color, and the shadows are
   bluer than usual"                      -> golden low sunlight / cool blue shadows
  "progression of color from the blue above to the soft yellows and dull reds
   near the horizon"                      -> o gradiente do céu, nomeado
  "boldest red-orange glow ... nearest where the sun crosses the horizon"
                                          -> warm glow at the horizon
  "The earth below the sunset is dark, but NOT BLACK as it appears in a photo.
   The eye can usually see some local color in a ground silhouette"
                                          -> a regra anti-foto: sombra com cor
                                             local legível, nunca silhueta preta
  "a soft violet glow"                    -> violet haze

O que NÃO entra, de propósito: lanterna/janela acesa (Gurney: "lamps and
lanterns were lit at dusk") — seria segunda variável; fica para outra rodada.
E nenhuma palavra de lente/ângulo: perspectiva é do mapa, e o excesso de
perspectiva é o erro caro (tolerância do fov é assimétrica).
"""
import os

import rodar_folha_casa as r1

PROMPT_R2 = (
    "a simple wooden stilt house with a pitched thatch roof standing on open "
    "flat ground, Pantanal wetland dwelling, weathered timber walls, "
    "at dusk, low golden sunset light from the left, warm glow on the thatch "
    "edges, shadows bluer than usual with readable local color, dark ground "
    "silhouette but not black, sky gradient from deep blue above through soft "
    "yellow to dull red at the horizon, warm glow strongest at the horizon, "
    "soft violet haze, painterly concept art, muted palette, loose brushwork, "
    "atmospheric depth")

if __name__ == "__main__":
    # reusa o runner da rodada 1 por MONKEY-PATCH declarado: mesmo grafo,
    # mesmas sementes, mesmo mapa; muda o prompt e o prefixo de saída.
    r1.PROMPT = PROMPT_R2
    origem = os.path.join(r1.SAIDA, "casa-profundidade-0001.png")
    import shutil
    shutil.copy(origem, os.path.join(r1.COMFY_INPUT, r1.MAPA))

    JOB = "guariba-folha-casa-r2"
    r1._j.abrir_job(JOB, "Folha da casa, rodada 2: crepúsculo (Gurney)",
                    len(r1.SEMENTES),
                    dono="GPU: SDXL 1.0 + ControlNet depth (xinsir)",
                    detalhe="mesma cena/sementes; muda SÓ o prompt de luz")
    feito = 0
    try:
        for s in r1.SEMENTES:
            alvo = os.path.join(r1.SAIDA, f"folha-casa-r2-{s}.png")
            if os.path.exists(alvo):
                feito += 1
                r1._j.avancar(JOB, feito, f"{s} (já existia)")
                continue
            dt = r1.rodar(s, alvo)
            feito += 1
            r1._j.avancar(JOB, feito, f"semente {s} · {feito}/{len(r1.SEMENTES)}")
            print(f"semente {s}: ok ({dt:.0f}s)", flush=True)
    except BaseException as e:
        r1._j.fechar(JOB, f"erro: {e}")
        raise
    r1._j.fechar(JOB, f"ok: {feito}/{len(r1.SEMENTES)} folhas")
    print(f"\nfolhas r2 em {r1.SAIDA}")
