#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bateria mecânica M1–M5 da mesa da fronteira — critérios EXATOS do selo
(`../pre-registro-mesa-fronteira.md`, §Critérios). Reprovação é da FOLHA.

Roda a MESMA sonda sobre a série inteira (regra do instrumento: uma régua,
todas as folhas). Uso:

    ~/venvs/geocalib/bin/python bateria_m1_m5.py

AUTOCHECAGEM (anti-circularidade): a projeção prevista do poste é conferida
contra o PRÓPRIO mapa de profundidade antes de medir folha pintada — se a
coluna prevista não bater com o poste do mapa (±3 px), a bateria ABORTA em vez
de medir com régua desalinhada. A convenção de câmera (duas candidatas) é
escolhida pela que passa nessa prova.
"""
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metrologia_vista_unica import horizonte_e_vertical, razao_alturas  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
GEO = os.path.join(RAIZ, "cena", "casa-geometria.json")
MAPA = os.path.join(RAIZ, "cena", "casa-profundidade-0001.png")
ALPHA = os.path.join(RAIZ, "cena", "casa-alpha.png")

RAZAO_VERDADE = 4.05 / 3.0          # cumeeira/poste, mesma profundidade
M1_TOL = 0.02                        # |erro| ≤ 2%
M2_TOL = 12                          # px, linha y=448
M3_TOL = 4.0                         # px, mediana
M4_P1, M4_MED = 8, 25                # crepúsculo
CANTO = (300, 70)                    # M5: 300 largura × 70 altura por canto


def projetar(geo, convencao):
    """Projeta pontos-chave do mundo para pixels; devolve dict de pontos.

    convencao = (usar_Rt, sy) — transposta da rotação e sinal do eixo y da
    imagem. A escolha NUNCA é minha: é da autocalibração contra o mapa/alpha.
    """
    usar_Rt, sy = convencao
    f, W, H = geo["focal_px"], geo["W"], geo["H"]
    R = np.array(geo["rotacao"])
    C = np.array(geo["posicao"])

    def px(p):
        p = np.asarray(p, dtype=float)
        v = (R.T if usar_Rt else R) @ (p - C)
        z = -v[2] if v[2] < 0 else v[2]      # câmera Blender olha -Z local
        u = W / 2 + f * v[0] / z
        w = H / 2 + sy * f * v[1] / z
        return np.array([u, w])

    e = geo["elemento"]["xy"]
    r = geo["referencia"]["xy"]
    return {
        "poste_base": px([r[0], r[1], 0.0]),
        "poste_topo": px([r[0], r[1], geo["referencia"]["altura_m"]]),
        "cumeeira": px([e[0], e[1], geo["elemento"]["altura_cumeeira_m"]]),
        "chao_casa": px([e[0], e[1], 0.0]),
    }


def observaveis_do_mapa(mapa, alpha):
    """Alvos de calibração medidos no PRÓPRIO insumo (nunca da álgebra):
    coluna e topo do poste no mapa; topo da cumeeira e base no alpha."""
    h, w = mapa.shape
    ceu = float(mapa[:h // 4].mean())
    # poste: estrutura FINA e clara contra o céu, à DIREITA do elemento
    # (o alpha é só a casa; o poste mora fora dele)
    dir_alpha = int(np.where(alpha.max(axis=0) > 128)[0].max())
    ini = min(w - 8, dir_alpha + 15)
    claros = (mapa[:h // 2, ini:] > ceu + 40).sum(axis=0)
    col_poste = int(ini + np.argmax(claros))
    linhas = np.where(mapa[:, col_poste] > ceu + 40)[0]
    topo_poste = int(linhas.min())
    cume_topo = int(np.where(alpha.max(axis=1) > 128)[0].min())
    base_alpha = int(np.where(alpha.max(axis=1) > 128)[0].max())
    return {"col_poste": col_poste, "topo_poste": topo_poste,
            "cume_topo": cume_topo, "base": base_alpha}


def escolher_convencao(geo, mapa, alpha):
    """Varre as convenções; fica a que bate com os observáveis (±6 px)."""
    alvos = observaveis_do_mapa(mapa, alpha)
    melhor, melhor_erro = None, 1e9
    for usar_Rt in (False, True):
        for sy in (1.0, -1.0):
            try:
                pts = projetar(geo, (usar_Rt, sy))
            except Exception:
                continue
            e = (abs(pts["poste_base"][0] - alvos["col_poste"]) +
                 abs(pts["poste_topo"][1] - alvos["topo_poste"]) +
                 abs(pts["cumeeira"][1] - alvos["cume_topo"]))
            if e < melhor_erro:
                melhor, melhor_erro = ((usar_Rt, sy), pts), e
    if melhor is None or melhor_erro > 18:      # ~6 px por alvo
        return None, None, alvos
    return melhor[0], melhor[1], alvos


def coluna_gradiente(img, col, meia=3):
    """Gradiente horizontal máximo numa janela em torno da coluna prevista."""
    a = img.astype(float)
    g = np.abs(np.diff(a, axis=1))
    j = g[:, max(0, col - meia):col + meia]
    return j.max(axis=1)


def _refinar(im, x, y_prev, meia=35):
    """A MESMA sonda da série (transcrito 2026-08-15): topo por gradiente
    máximo na coluna prevista, janela ±meia do previsto."""
    col = im[:, max(0, int(x) - 2):int(x) + 3].mean(axis=1)
    gy = np.abs(np.gradient(col))
    lo = max(0, int(y_prev) - meia)
    return lo + int(np.argmax(gy[lo:int(y_prev) + meia]))


def m1_regua(folha, m1ctx):
    """M1 = a régua ORIGINAL da série: eq. (9) via razao_alturas, bases
    previstas pela projeção, topos refinados por gradiente. Poste PRESENTE
    = gradiente máx > 6 na coluna prevista (janela ±28) — igual à receita."""
    cb, ct, pb, pt, l, v = m1ctx
    im = folha.astype(float)
    col = im[:, int(pt[0]) - 2:int(pt[0]) + 3].mean(axis=1)
    forca = float(np.abs(np.gradient(col))[max(0, int(pt[1]) - 28):int(pt[1]) + 28].max())
    if forca <= 6:
        return {"passa": False,
                "motivo": f"poste AUSENTE (gradiente máx {forca:.1f} na coluna prevista)"}
    ctop = _refinar(im, ct[0], ct[1])
    ptop = _refinar(im, pt[0], pt[1], 28)
    r = float(razao_alturas(cb, [ct[0], ctop], pb, [pt[0], ptop], l, v))
    erro = r / RAZAO_VERDADE - 1.0
    return {"passa": abs(erro) <= M1_TOL, "razao": round(r, 3),
            "erro_pct": round(100 * erro, 2),
            "cume_topo_med": int(ctop), "poste_topo_med": int(ptop),
            "gradiente_poste": round(forca, 1)}


def m2_largura(folha, alpha, y=448, janela=60):
    """Bordas esq/dir na linha y: aresta mais forte NUMA JANELA em torno da
    borda declarada — aresta de textura longe da parede não conta; borda que
    fugiu da janela conta como >janela (falha honesta, não pesca)."""
    m = alpha[y] > 128
    idx = np.where(m)[0]
    if len(idx) == 0:
        return {"passa": False, "motivo": f"alpha vazio na linha {y}"}
    declarado = [int(idx.min()), int(idx.max())]
    linha = folha[y].astype(float)
    # suaviza 3px para aresta de parede vencer pincelada fina
    suave = np.convolve(linha, np.ones(3) / 3, mode="same")
    g = np.abs(np.diff(suave))
    medido, desvios = [], []
    for borda in declarado:
        a, b = max(0, borda - janela), min(len(g), borda + janela)
        candidatos = a + np.where(g[a:b] >= 8)[0]
        if len(candidatos) == 0:
            medido.append(None)
            desvios.append(janela + 1)
            continue
        # a aresta válida MAIS PRÓXIMA do declarado — a mais forte da janela
        # seria pescar quina interna pintada em vez da parede
        pos = int(candidatos[np.argmin(np.abs(candidatos - borda))])
        medido.append(pos)
        desvios.append(abs(pos - borda))
    desvio = max(desvios)
    return {"passa": desvio <= M2_TOL,
            "desvio_px": int(desvio) if desvio <= janela else f">{janela}",
            "declarado": declarado, "medido": medido}


def m3_silhueta(folha, alpha):
    import cv2
    borda_decl = cv2.Canny((alpha > 128).astype(np.uint8) * 255, 50, 150)
    borda_folha = cv2.Canny(folha, 60, 140)
    ys, xs = np.where(borda_decl > 0)
    if len(ys) == 0:
        return {"passa": False, "motivo": "alpha sem borda"}
    dist = cv2.distanceTransform((borda_folha == 0).astype(np.uint8), cv2.DIST_L2, 3)
    d = dist[ys, xs]
    med = float(np.median(d))
    return {"passa": med <= M3_TOL, "mediana_px": round(med, 2)}


def m4_preto(folha, alpha):
    sil = folha[alpha > 128]
    p1, med = float(np.percentile(sil, 1)), float(np.median(sil))
    return {"passa": p1 >= M4_P1 and med >= M4_MED,
            "p1": round(p1, 1), "mediana": round(med, 1)}


def m5_fantasma(folha_rgb, nome_folha=None):
    """Heurística de tinta em canto (assinatura): contraste local concentrado.
    Marca SUSPEITO e salva os cantos AMPLIADOS (2,5×) — o veredito do selo é
    por presença, conferida a olho como na série (insp-*-canto.png)."""
    if nome_folha:
        base = os.path.join(RAIZ, "resultados", "inspecao-cantos")
        os.makedirs(base, exist_ok=True)
        h0, w0 = folha_rgb.shape[:2]
        cw0, ch0 = CANTO
        for tag, (yy, xx) in {"inf-dir": (h0 - ch0, w0 - cw0),
                              "inf-esq": (h0 - ch0, 0)}.items():
            rec = Image.fromarray(folha_rgb[yy:yy + ch0, xx:xx + cw0])
            rec = rec.resize((cw0 * 2, ch0 * 2), Image.NEAREST)
            rec.save(os.path.join(base, f"insp-{nome_folha}-{tag}.png"))
    h, w = folha_rgb.shape[:2]
    cw, ch = CANTO
    suspeitos = []
    for nome, (y0, x0) in {"inf-dir": (h - ch, w - cw), "inf-esq": (h - ch, 0),
                           "sup-dir": (0, w - cw), "sup-esq": (0, 0)}.items():
        c = folha_rgb[y0:y0 + ch, x0:x0 + cw].astype(float)
        cinza = c.mean(axis=2)
        # traço de assinatura: pixels bem mais claros/escuros que a vizinhança
        desvio = np.abs(cinza - np.median(cinza))
        marca = (desvio > 55).sum()
        croma = np.abs(c - c.mean(axis=2, keepdims=True)).max(axis=2)
        tinta_colorida = ((croma > 28) & (desvio > 25)).sum()
        if marca > 120 or tinta_colorida > 80:
            suspeitos.append({"canto": nome, "marca_px": int(marca),
                              "croma_px": int(tinta_colorida)})
    return {"passa": len(suspeitos) == 0, "suspeitos": suspeitos}


def medir_folha(caminho, luz, m1ctx, alpha):
    rgb = np.array(Image.open(caminho).convert("RGB"))
    g = np.array(Image.open(caminho).convert("L"))
    r = {"folha": os.path.basename(caminho), "luz": luz}
    r["M1"] = m1_regua(g, m1ctx)
    r["M2"] = m2_largura(g, alpha)
    r["M3"] = m3_silhueta(g, alpha)
    if luz == "crepusculo":
        r["M4"] = m4_preto(g, alpha)
    r["M5"] = m5_fantasma(rgb, os.path.basename(caminho).replace(".png", ""))
    return r


if __name__ == "__main__":
    geo = json.load(open(GEO, encoding="utf-8"))
    mapa = np.array(Image.open(MAPA).convert("L"))
    alpha = np.array(Image.open(ALPHA).convert("L").resize((geo["W"], geo["H"])))

    conv, pts, alvos = escolher_convencao(geo, mapa, alpha)
    if conv is None:
        raise SystemExit(f"ABORTA: nenhuma convenção bate com os observáveis {alvos} — régua desalinhada")
    print(f"convenção validada contra o mapa/alpha: Rt={conv[0]} sy={conv[1]:+.0f} | alvos {alvos}")
    print(f"  poste base/topo: {pts['poste_base'].round(1)} {pts['poste_topo'].round(1)}")
    print(f"  cumeeira: {pts['cumeeira'].round(1)}  chão da casa: {pts['chao_casa'].round(1)}\n")

    # contexto da régua original (eq. 9): horizonte + vertical + bases previstas
    R = np.array(geo["rotacao"])
    l, v = horizonte_e_vertical(R, geo["focal_px"], geo["W"], geo["H"])
    m1ctx = (pts["chao_casa"], pts["cumeeira"],
             pts["poste_base"], pts["poste_topo"], l, v)

    resultados = []
    series = [("A", os.path.join(RAIZ, "resultados", "folha-casa-*.png"))]
    for braco, padrao in series:
        for f in sorted(glob.glob(padrao)):
            if "chroma" in f:
                continue
            luz = "crepusculo" if ("crepusculo" in f or "-r2-" in f) else "neutro"
            r = medir_folha(f, luz, m1ctx, alpha)
            r["braco"] = braco
            resultados.append(r)
            criterios = [k for k in ("M1", "M2", "M3", "M4", "M5") if k in r]
            resumo = " ".join(f"{k}:{'✓' if r[k]['passa'] else '✗'}" for k in criterios)
            print(f"[{braco}] {r['folha']:44s} {resumo}")
            for k in criterios:
                det = {kk: vv for kk, vv in r[k].items() if kk != "passa"}
                print(f"      {k}: {det}")

    with open(os.path.join(AQUI, "resultado-bateria-m1m5.json"), "w", encoding="utf-8") as f:
        json.dump({"convencao": conv, "pontos": {k: v.tolist() for k, v in pts.items()},
                   "resultados": resultados}, f, ensure_ascii=False, indent=1)
    print("\nsalvo em resultado-bateria-m1m5.json")
