#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Metrologia de vista única — a régua de perspectiva da pipeline de camadas.

Autoteste (não precisa de venv especial, só numpy):
    python3 metrologia_vista_unica.py

O QUE ESTE ARQUIVO É

A implementação da equação (9) de Criminisi, Reid & Zisserman, *Single View
Metrology*, IJCV 40(2):123-148, 2000:

    alfa*Z = - ||x x x'|| / ( (l_barra . x) * ||v x x'|| )

com `x` o pé do objeto no plano de referência, `x'` o topo, `l_barra` a linha
de fuga do chão normalizada e `v` o ponto de fuga vertical.

POR QUE ELA, E NÃO A REGRA DO ARTISTA

A regra de produção — *"o horizonte corta o objeto na fração h/H da altura
dele"* — é EXATA só com a câmera nivelada. Sob pitch, a altura do mundo vira
função projetiva da posição na imagem; sob roll, a regra nem pode ser
enunciada, porque não existe "linha" da imagem quando o horizonte está torto.

Medido nas 7 câmeras do teste de 2026-08-15 (`teste-geocalib/geometria.json`),
recuperando a altura de um poste de 4,00 m:

    regra ingênua h/H .................. erro até 4,2%    (pitch -14°)
    forma fechada de Hoiem et al. ...... erro 0,14% a 3,0%
    equação (9) daqui .................. erro <= 7,3e-8   (7/7)

O 7,3e-8 relativo é ruído de ponto flutuante da cadeia — 0,3 micrômetro num
poste de 4 m. Não é "zero" e não vale escrever zero; é exatidão até onde a
aritmética da máquina alcança.

E ela não precisa de FOCAL. Isso importa porque a rodada de 2026-08-14 mediu
que o estimador neural não recupera distância focal das nossas folhas: o
controle positivo devolveu 49,17 / 21,65 / 24,29 / 24,95 / 43,75 graus para o
mesmo vfov verdadeiro de 32,64°. A régua passa POR FORA do eixo que morreu.

CONVENÇÃO DE SINAL

`l_barra` tem duas orientações possíveis e a eq. (9) troca de sinal com ela.
Aqui a reta é orientada de modo que `l_barra . x > 0` para pontos ABAIXO do
horizonte, que é onde vive o pé de qualquer objeto apoiado. Com isso `alfa*Z`
sai positivo para objeto acima do chão. Não deduza o sinal: `alfa_Z` levanta
se o pé cair do lado errado, porque pé acima do horizonte é insumo defeituoso,
não caso de uso.

O QUE ELA NÃO FAZ

- **exige que o objeto TOQUE o plano de referência.** Nuvem, fumaça, galho no
  ar e pássaro ficam fora — é a lacuna que está em pesquisa;
- **confere a extensão vertical, não a perspectiva INTERNA do elemento.** Uma
  casa pintada com a altura certa e linhas de fuga próprias inconsistentes
  passa neste teste;
- o erro do horizonte NÃO se propaga igual para todo mundo: ele cancela quando
  os dois objetos comparados estão à mesma profundidade, e explode para
  objetos perto da linha do horizonte. Ver `sensibilidade_horizonte`.
"""
import math

import numpy as np


def horizonte_e_vertical(R, altura_focal_px, largura_px, altura_px):
    """Linha de fuga do chão e ponto de fuga vertical, da matriz da câmera.

    `R` é a rotação MUNDO<-CÂMERA (3x3, convenção do Blender: a câmera olha
    para -Z, +X à direita, +Y para cima). Devolve `(l_barra, v)` em
    coordenadas homogêneas de pixel, com `l_barra` já orientada e normalizada
    para que `l_barra . x` seja a distância COM SINAL em pixels.
    """
    R = np.asarray(R, dtype=np.float64)
    f, W, H = float(altura_focal_px), float(largura_px), float(altura_px)

    # ponto de fuga da direção do mundo `d`: a direção em coordenadas de
    # câmera projetada, em homogêneas (vale também quando cai no infinito)
    def vp(d):
        vx, vy, vz = R.T @ np.asarray(d, dtype=np.float64)
        return np.array([W / 2 * (-vz) + f * vx, H / 2 * (-vz) - f * vy, -vz])

    l = np.cross(vp((1.0, 0.0, 0.0)), vp((0.0, 1.0, 0.0)))
    l = l / math.hypot(l[0], l[1])

    # orienta a reta: ponto MUITO abaixo do horizonte deve dar produto > 0
    if l @ np.array([W / 2, H * 10.0, 1.0]) < 0:
        l = -l
    return l, vp((0.0, 0.0, 1.0))


def alfa_Z(pe_px, topo_px, l_barra, v):
    """Eq. (9). Altura do objeto vezes o fator de escala desconhecido alfa."""
    x = np.array([pe_px[0], pe_px[1], 1.0])
    xl = np.array([topo_px[0], topo_px[1], 1.0])
    denom = (l_barra @ x) * np.linalg.norm(np.cross(v, xl))
    if l_barra @ x <= 0:
        raise ValueError(
            "o pé do objeto caiu SOBRE ou ACIMA da linha do horizonte: "
            "ou o elemento não toca o chão, ou o pé foi extraído errado")
    return float(np.linalg.norm(np.cross(x, xl)) / denom)


def razao_alturas(pe1, topo1, pe2, topo2, l_barra, v):
    """H1/H2 — sem focal, sem calibração, sem altura de referência.

    É a forma em que o fator alfa cancela, e é a que a pipeline usa para
    comparar o elemento PINTADO com o proxy 3D que o gerou.
    """
    return alfa_Z(pe1, topo1, l_barra, v) / alfa_Z(pe2, topo2, l_barra, v)


def altura_absoluta(pe_px, topo_px, l_barra, v, altura_camera_m):
    """Z em metros, usando a altura da câmera como referência (eq. 20)."""
    aZc = -1.0 / (l_barra @ v)
    return alfa_Z(pe_px, topo_px, l_barra, v) / abs(aZc) * altura_camera_m


def sensibilidade_horizonte(pe1_px, pe2_px, l_barra, epsilon_px):
    """Erro relativo na razão de alturas por deslocamento do horizonte.

    dR/R ~ eps * (1/d1 - 1/d2), com d_i a distância COM SINAL do pé do objeto
    i até a linha. Duas leituras que mudam o desenho da mesa de conferência:
    o erro CANCELA quando os dois pés estão à mesma distância do horizonte
    (mesma profundidade), e é dominado pelo objeto mais PRÓXIMO da linha.
    """
    d1 = l_barra @ np.array([pe1_px[0], pe1_px[1], 1.0])
    d2 = l_barra @ np.array([pe2_px[0], pe2_px[1], 1.0])
    return float(epsilon_px * (1.0 / d1 - 1.0 / d2))


def _autoteste():
    """Contra a verdade exata das 7 câmeras do teste de 2026-08-15."""
    import json
    import os

    aqui = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(aqui, "teste-geocalib", "geometria.json")
    if not os.path.exists(caminho):
        print(f"autoteste PULADO: {caminho} não existe")
        return
    with open(caminho, encoding="utf-8") as fh:
        geo = json.load(fh)

    W, H, ALVO = 1024, 576, 4.0
    print(f"{'cam':4}{'Z_est_m':>10}{'erro_rel':>12}")
    pior = 0.0
    for cid, d in geo.items():
        l, v = horizonte_e_vertical(d["rotacao"], d["focal_px"], W, H)
        Z = altura_absoluta(d["poste"]["base_px"], d["poste"]["topo_px"],
                            l, v, d["altura_camera_m"])
        rel = abs(Z - ALVO) / ALVO
        pior = max(pior, rel)
        print(f"{cid:4}{Z:10.5f}{rel:12.2e}")

    # limiar em 1e-6: três ordens acima do ruído observado (7,3e-8) e ainda
    # sete ordens abaixo de qualquer erro que a pipeline vá cometer extraindo
    # pé e topo de uma folha pintada. Limiar apertado demais reprova a
    # aritmética da máquina e não o método — foi o que aconteceu na 1ª versão.
    assert pior < 1e-6, f"eq. (9) não fechou: pior erro relativo {pior:.2e}"
    print(f"\nOK — 7/7 recuperam {ALVO:.2f} m; pior erro relativo {pior:.2e}")


if __name__ == "__main__":
    _autoteste()
