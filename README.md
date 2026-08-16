# geometry-verifies

*3D disposes, diffusion paints, geometry verifies — a matte painting pipeline
where every AI-painted image must pass a pre-registered geometric ruler before
it counts. Full docs in Portuguese below; the research diary lives in
[`pharo/`](pharo/).*

**O 3D dispõe, a difusão pinta, a geometria confere.** Este repositório é o
método de matte painting assistido por IA de uma produção autoral (a série
**Guariba**): uma cena leve no Blender dispõe o elemento e exporta
profundidade, alpha e a câmera exata; um modelo de difusão pinta o elemento
condicionado por esse mapa; e a **metrologia de vista única** (Criminisi,
Reid & Zisserman, 2000) mede a folha pintada contra a verdade geométrica —
sem conhecer a distância focal. A pintura fica livre; a geometria fica presa.
Régua pré-registrada, julgamento cego, recibo de cada afirmação. **IA é
bastidor e referência; plano final é pintado — fronteira declarada.**

## Início rápido

```bash
git clone https://github.com/mateusalkimim/geometry-verifies
cd geometry-verifies

# medir as folhas incluídas contra a cena incluída (só numpy/PIL/OpenCV):
python3 metrologia/bateria_m1_m5.py
```

A bateria imprime M1–M5 por folha: razão de alturas (eq. 9, ≤2% de erro),
largura na linha de referência (≤12 px), silhueta (mediana ≤4 px), preto do
crepúsculo (p1 ≥ 8) e fantasma de canto. Os detalhes de instalação e as vias
de pintura (SDXL local via ComfyUI; FLUX.2 em H100 via Modal) estão em
[`docs/INSTALACAO.md`](docs/INSTALACAO.md).

## O que tem aqui

| pasta | conteúdo |
|---|---|
| `metrologia/` | a régua: `metrologia_vista_unica.py` (eq. 9) e `bateria_m1_m5.py` (M1–M5 com autocalibração anti-circular contra o próprio mapa) |
| `cena/` | o 3D que dispõe: script Blender da cena + os 4 insumos exatos (proxy, z-buffer, alpha, geometria da câmera) |
| `pintores/` | os que pintam: SDXL+ControlNet local (ComfyUI) e a bancada de fronteira FLUX.2+Fun-Union (Modal, H100) com a cirurgia P1–P4 |
| `resultados/` | as folhas medidas (SDXL e P1–P4 nas duas luzes), JSONs da régua e manifesto com sha256 |
| `pharo/` | o caderno de pesquisa: pré-registro da mesa, resultado, a cirurgia da obediência e a bancada — com glossário em `pharo/LEIA-ME.md` |

## O lugar no ciclo maior

Este método serve a uma produção onde **nada generativo renderiza plano
final**. O fluxo aqui coberto é o de *storyboard/conceito*: a folha que passa
na régua vira referência de composição — o filme continua sendo fechado à mão.
A história completa (por que o z-buffer sintético falha num ControlNet de
fronteira, e a cirurgia que o faz obedecer) está em
`pharo/dominio-cirurgia-obediencia.md`.

## Proveniência e garantias

- **Sem segredo na árvore**: tokens vivem em `.env` fora do repo (Modal
  Secrets/variáveis de ambiente); o código documenta o caminho, nunca o valor;
- **Licenças conferidas na fonte**: SDXL (CreativeML Open RAIL++-M),
  ControlNet xinsir (Apache-2.0), FLUX.2-dev (gated, licença própria da BFL —
  leia antes de usar), Fun-Controlnet-Union (alibaba-pai), Depth Anything
  V2 **Small** (Apache-2.0; o Large é CC-BY-NC e foi vetado por isso);
- **Nada aqui foi treinado com dado de terceiros**: o repositório é método e
  medição, não modelo;
- as imagens de `cena/` e `resultados/` são obra do autor (cena-cenário de
  teste da produção), licenciadas em CC BY 4.0 — ver `LICENSE-MEDIA`.

## Estado e mesas abertas

- régua completa (M1–M5) passando 3/3 nas duas luzes com a receita P4
  (depth estimado + enxerto do elemento fino + referência) — recibos em
  `resultados/`;
- aberto: o custo estético da imagem de referência (o chapado do proxy na
  pincelada) aguarda julgamento cego; fine-tune do ControlNet com pares
  sintéticos próprios (P6) é a cirurgia profunda não iniciada;
- este repo é um recorte publicado de um caderno maior e segue vivo junto da
  produção.

---
Código sob [MIT](LICENSE) · imagens e documentos sob [CC BY 4.0](LICENSE-MEDIA) ·
autor: [Mateus Alkimim](https://github.com/mateusalkimim)
