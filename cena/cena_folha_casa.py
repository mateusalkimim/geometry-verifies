#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A PRIMEIRA FOLHA da arquitetura de matte painting — o elemento, não o quadro.

Roda headless:
    blender.exe -b -P cena_folha_casa.py

O ELEMENTO: a casa do plano 9.2 do E1 ("wide crepúsculo: ele no telhado"),
isolada na prancheta. O modelo NUNCA compõe o quadro; ele pinta uma peça.

CADA ESCOLHA AQUI VEM DE COISA MEDIDA. Em ordem:

1. ELEMENTO APOIADO COM VERTICAL CLARA. É a única classe com verificador
   validado (`pharo/dominio-horizonte-fuga-e-escala.md` §10.4). Canoa não serve
   — casco deitado, sem vertical, e a profundidade é cega a ele (rodada 5).
   Mata não serve — auto-similar, e a pergunta não tem enunciado.

2. DISCO DE CHÃO SOB O ELEMENTO. Medido em 2026-08-15: elemento isolado tem
   inclinação de pitch 0,58; com qualquer chão vai a 0,75-0,96. O chão não é
   cenário, é o que torna a perspectiva decidível.

3. A GRADE, e não ruído, no disco. Medido: no elemento RÍGIDO a grade leva o
   pitch de 0,75 para 0,86. (No orgânico empata — mas este elemento é rígido.)

4. COORDENADA DE OBJETO na textura. Coordenada gerada é normalizada pela caixa
   do objeto e produziu chão liso e chão arco-íris nos dois defeitos de ontem.

5. POSTE DE REFERÊNCIA À MESMA PROFUNDIDADE DA CASA. Este é o item mais sutil
   e o mais barato: o erro do horizonte CANCELA EXATAMENTE quando os dois
   objetos comparados estão à mesma profundidade (medido: -1,5e-16). Comparar
   com algo distante custaria ~5% por pixel de erro. O poste é a régua.

6. LENTE LONGA. A tolerância perceptual do fov é ASSIMÉTRICA: 15° acima é pego,
   até 50° abaixo passa. Perspectiva de menos é quase de graça. Gerar chapado.

7. ELEMENTO GRANDE NO QUADRO (~45% da altura). A canoa a 0,84% foi ilegível por
   construção; a folha que venceu o seminário tinha o cubo a 22,8%.

8. CÂMERA POSICIONADA, não só girada — mira fixa no elemento. Foi o defeito que
   quase envenenou a rodada do GeoCalib: girar sem reposicionar joga o herói
   para fora do quadro na lente longa.

9. clip_end ALTO. O padrão de 100 m apagaria o horizonte, e o horizonte é a
   referência de toda a régua.

10. LUZ NEUTRA, não crepúsculo. A lição das 216 folhas foi "todas as variáveis
    mudaram de uma vez". O crepúsculo (Gurney, dissecado) entra na rodada 2.

SAÍDAS — o contrato de exportação por elemento:
  casa-profundidade.png  mapa para o ControlNet (perto=claro), janela FIXA
  casa-alpha.png         RGBA do elemento SOZINHO — a máscara DECLARADA
  casa-proxy.png         beauty, para a conferência com o olho e para a régua
  casa-geometria.json    matriz da câmera, focal, e as alturas conhecidas
"""
import json
import math
import os

import bpy
from mathutils import Vector

W, H = 1216, 832            # o mesmo latente do grafo do seminário
SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)))  # gera ao lado

FOV_H = 32.0                # lente longa — item 6
ALT_REF = 4.2               # altura de referência para o enquadramento
FRACAO = 0.45               # fração da altura do quadro — item 7

CASA_XY = (-1.2, 0.0)
POSTE_XY = (3.4, 0.0)       # MESMA profundidade (mesmo y) — item 5
POSTE_H = 3.0
RAIO_DISCO = 11.0
ALVO = (0.6, 0.0, 1.9)


def mat(nome, cor, rug=0.9):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*cor, 1.0)
    b.inputs["Roughness"].default_value = rug
    return m


def mat_grade():
    """Disco de chão em grade — itens 3 e 4."""
    m = bpy.data.materials.new("chao_grade")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.95
    coord = nt.nodes.new("ShaderNodeTexCoord")
    tex = nt.nodes.new("ShaderNodeTexChecker")
    tex.inputs["Scale"].default_value = 0.35          # quadrados de ~2,9 m
    tex.inputs["Color1"].default_value = (0.55, 0.52, 0.45, 1.0)
    tex.inputs["Color2"].default_value = (0.31, 0.29, 0.25, 1.0)
    nt.links.new(coord.outputs["Object"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    return m


def casa(x, y, larg=4.4, prof=3.6, alt=2.6):
    """Rancho pantaneiro: corpo + telhado de duas águas + esteios.

    Verticais claras em toda parte — cantos do corpo e esteios. É o que doa
    ponto de fuga, e ponto de fuga é a única grandeza de vista única que dá
    orientação sem passar pela escala.
    """
    partes = []
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, alt / 2))
    o = bpy.context.object
    o.scale = (larg, prof, alt)
    partes.append(o)

    # telhado de duas águas — prisma CONSTRUÍDO À MÃO, não cilindro girado.
    #
    # DEFEITO PEGO NA CONFERÊNCIA VISUAL: `primitive_cylinder_add(vertices=3)`
    # girado 90° põe a seção triangular numa orientação arbitrária e com raio
    # grande demais. Saiu uma LAJE CHAPADA ATRÁS da casa, que lê como parede.
    # É a mesma família do "caixa de topo reto virou prédio" da rodada 4 — e é
    # exatamente o que a gramática da obra proíbe: a silhueta tem que LER como
    # a coisa que representa. Seis vértices declarados não têm ambiguidade.
    bx, by = larg / 2 + 0.35, prof / 2 + 0.35     # beiral
    cume = 1.45
    vs = [(-bx, -by, alt), (bx, -by, alt), (bx, by, alt), (-bx, by, alt),
          (-bx, 0.0, alt + cume), (bx, 0.0, alt + cume)]
    fs = [(0, 1, 5, 4), (3, 2, 5, 4), (0, 1, 2, 3), (0, 3, 4), (1, 2, 5)]
    me = bpy.data.meshes.new("telhado")
    me.from_pydata([(x + a, y + b, c) for a, b, c in vs], [], fs)
    me.update()
    t = bpy.data.objects.new("telhado", me)
    bpy.context.collection.objects.link(t)
    partes.append(t)

    # esteios — verticais puras, sem ambiguidade de telhado
    for dx in (-larg * 0.42, larg * 0.42):
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.10, depth=alt, location=(x + dx, y - prof * 0.62, alt / 2))
        partes.append(bpy.context.object)
    return partes


def montar():
    bpy.ops.wm.read_factory_settings(use_empty=True)

    mundo = bpy.data.worlds.new("mundo")
    mundo.use_nodes = True
    mundo.node_tree.nodes["Background"].inputs["Color"].default_value = \
        (0.58, 0.60, 0.63, 1.0)
    bpy.context.scene.world = mundo

    # luz NEUTRA — item 10
    bpy.ops.object.light_add(type="SUN", location=(18, -26, 34))
    sol = bpy.context.object
    sol.data.energy = 3.2
    sol.data.angle = math.radians(2.0)
    sol.rotation_euler = (math.radians(52), 0.0, math.radians(28))

    m_parede = mat("parede", (0.70, 0.66, 0.58))
    m_telha = mat("telha", (0.42, 0.28, 0.22))
    m_poste = mat("poste", (0.52, 0.48, 0.42))

    grupos = {"chao": [], "elemento": [], "referencia": []}

    bpy.ops.mesh.primitive_circle_add(vertices=96, radius=RAIO_DISCO,
                                      fill_type="NGON",
                                      location=(ALVO[0], ALVO[1], 0.0))
    d = bpy.context.object
    d.data.materials.append(mat_grade())
    grupos["chao"].append(d)

    partes = casa(*CASA_XY)
    partes[0].data.materials.append(m_parede)
    partes[1].data.materials.append(m_telha)
    for p in partes[2:]:
        p.data.materials.append(m_parede)
    grupos["elemento"] = partes

    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.075, depth=POSTE_H,
        location=(POSTE_XY[0], POSTE_XY[1], POSTE_H / 2))
    pst = bpy.context.object
    pst.data.materials.append(m_poste)
    grupos["referencia"].append(pst)

    bpy.ops.object.camera_add(location=(0, 0, 0))
    cam = bpy.context.object
    cam.data.clip_end = 3000.0                        # item 9
    cam.data.sensor_fit = "HORIZONTAL"
    cam.data.angle_x = math.radians(FOV_H)
    bpy.context.scene.camera = cam

    # câmera POSICIONADA — item 8
    vfov = 2.0 * math.atan(math.tan(cam.data.angle_x / 2.0) * (H / W))
    dist = ALT_REF / (2.0 * FRACAO * math.tan(vfov / 2.0))
    cam.rotation_euler = (math.radians(90.0 - 4.0), 0.0, 0.0)
    bpy.context.view_layer.update()
    fwd = (cam.matrix_world.to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()
    cam.location = Vector(ALVO) - fwd * dist
    bpy.context.view_layer.update()
    return grupos, cam, dist, vfov


def render_para(caminho, transparente=False):
    s = bpy.context.scene
    s.render.film_transparent = transparente
    s.render.image_settings.color_mode = "RGBA" if transparente else "RGB"
    s.render.filepath = caminho
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    grupos, cam, dist, vfov = montar()

    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.device = "CPU"
    s.cycles.samples = 64
    s.cycles.use_denoising = True
    s.render.resolution_x, s.render.resolution_y = W, H
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = "PNG"
    s.view_layers[0].use_pass_z = True

    os.makedirs(bpy.path.abspath(SAIDA), exist_ok=True)

    # ── 1. beauty, para o olho e para a régua ────────────────────────────
    render_para(SAIDA + "casa-proxy")

    # ── 2. alpha do elemento SOZINHO — a máscara DECLARADA ───────────────
    for o in grupos["chao"] + grupos["referencia"]:
        o.hide_render = True
    render_para(SAIDA + "casa-alpha", transparente=True)
    for o in grupos["chao"] + grupos["referencia"]:
        o.hide_render = False

    # ── 3. mapa de profundidade, janela FIXA e declarada ─────────────────
    # Janela derivada da distância da câmera, não de Normalize: Normalize usa
    # min/max da imagem inteira e o fundo vazio (z infinito) achataria a faixa
    # útil. Perto = claro, que é a convenção que o depth do xinsir espera.
    # DEFEITO PEGO NA CONFERÊNCIA VISUAL: com janela de 22 m, a casa (3,6 m de
    # fundura) ocupava ~13% da faixa e saía quase CHAPADA no mapa — silhueta
    # sem relevo, condicionamento fraco de forma. Apertada para 16 m, a casa
    # passa a ~23% e o chão ainda mantém gradiente de recuo, que é o que torna
    # a perspectiva decidível.
    perto, longe = dist - 6.0, dist + 10.0
    s.use_nodes = True
    nt = s.node_tree
    nt.nodes.clear()
    rl = nt.nodes.new("CompositorNodeRLayers")
    mr = nt.nodes.new("CompositorNodeMapRange")
    mr.inputs[1].default_value = perto      # From Min
    mr.inputs[2].default_value = longe      # From Max
    mr.inputs[3].default_value = 1.0        # To Min  (perto = branco)
    mr.inputs[4].default_value = 0.0        # To Max  (longe = preto)
    mr.use_clamp = True
    fo = nt.nodes.new("CompositorNodeOutputFile")
    fo.base_path = SAIDA
    fo.format.file_format = "PNG"
    fo.format.color_mode = "BW"
    fo.file_slots[0].path = "casa-profundidade-"
    nt.links.new(rl.outputs["Depth"], mr.inputs[0])
    nt.links.new(mr.outputs[0], fo.inputs[0])
    s.render.film_transparent = False
    s.render.filepath = SAIDA + "lixo-depth"
    bpy.ops.render.render(write_still=True)

    # ── 4. a geometria, para a régua ─────────────────────────────────────
    R = cam.matrix_world.to_3x3()
    f = (W / 2.0) / math.tan(cam.data.angle_x / 2.0)
    right = (R @ Vector((1.0, 0.0, 0.0))).normalized()
    up = (R @ Vector((0.0, 1.0, 0.0))).normalized()
    fwd = (R @ Vector((0.0, 0.0, -1.0))).normalized()
    wup = Vector((0.0, 0.0, 1.0))
    roll = math.atan2(wup.dot(right), wup.dot(up))
    pitch = math.asin(max(-1.0, min(1.0, fwd.dot(wup))))

    geo = {
        "W": W, "H": H, "focal_px": f,
        "hfov_deg": math.degrees(cam.data.angle_x),
        "vfov_deg": math.degrees(vfov),
        "roll_deg": math.degrees(roll), "pitch_deg": math.degrees(pitch),
        "horizonte_un": math.tan(pitch) / (2.0 * math.tan(vfov / 2.0)),
        "rotacao": [list(R[i]) for i in range(3)],
        "posicao": list(cam.matrix_world.translation),
        "altura_camera_m": cam.matrix_world.translation.z,
        "distancia_alvo_m": dist,
        "janela_profundidade_m": [perto, longe],
        "elemento": {"nome": "casa (plano 9.2)", "xy": list(CASA_XY),
                     "altura_corpo_m": 2.6, "altura_cumeeira_m": 2.6 + 1.45},
        "referencia": {"nome": "poste", "xy": list(POSTE_XY),
                       "altura_m": POSTE_H,
                       "mesma_profundidade": POSTE_XY[1] == CASA_XY[1]},
    }
    with open(bpy.path.abspath(SAIDA + "casa-geometria.json"), "w",
              encoding="utf-8") as fh:
        json.dump(geo, fh, indent=2, ensure_ascii=False)

    print(f"[folha-casa] dist {dist:.1f} m · câmera a "
          f"{geo['altura_camera_m']:.2f} m · pitch {geo['pitch_deg']:.2f}° · "
          f"vfov {geo['vfov_deg']:.2f}° · horizonte_un "
          f"{geo['horizonte_un']:.3f}")
    print(f"[folha-casa] saídas em {SAIDA}")
