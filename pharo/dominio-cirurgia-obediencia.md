# Domínio: a cirurgia da obediência — alimentar a fronteira com o NOSSO palco

*Aberto 2026-08-16, por decisão do operador após a mesa da fronteira: "o que
ele não pegou foi porque precisa ser feita uma cirurgia, e uma adaptação dos
nossos recursos para alimentar o FLUX". Alvo declarado: **replicar o
resultado da primeira folha (a do post do LinkedIn) num modelo de fronteira**
— geometria na régua E a pintura que o julgamento cego coroou 6 a 0.*

## O que a mesa provou (os dois recibos que fundam este domínio)

1. o FLUX.2+Fun-Union é o melhor PINTOR da bancada às cegas (borda 6/6, luz
   3/3, legibilidade 6/6, preto 3/3) — a pintura NÃO é o problema;
2. ele não obedece o NOSSO mapa (M1–M3 reprovados nas 6; poste morto em 4/6;
   escala 0,65–0,80 não é o botão; polaridade confere) — **mas obedece o
   próprio showcase com precisão**. O defeito não é do modelo nem do nosso
   palco: é do CASAMENTO entre os dois.

## A hipótese-mãe (H1): fora da distribuição de treino

ControlNets de depth são treinados com **depth de ESTIMADOR sobre imagem
real** (o do SD1.5: 3M pares gerados pelo MiDaS; o showcase do Fun-Union é
visivelmente estimador: denso, suave, sem zero absoluto). O nosso mapa é
z-buffer sintético: céu 0 absoluto, chão em gradiente linear, elemento fino
de 6 px. O Union nunca viu essa gramática. O xinsir (SDXL) tolera — foi a
sorte da casa, não a regra.

**Corolário testável (P1, o protótipo central):** não dar o z-buffer — dar o
**depth ESTIMADO sobre o NOSSO render proxy** (`casa-proxy.png`, o beauty do
Blender). Geometria continua exata POR CONSTRUÇÃO (o proxy é nosso, câmera
nossa), mas o formato entra na distribuição que o Union conhece. Precedente
publicado: DiffCAD usa ZoeDepth sobre renders sintéticos exatamente para
cruzar essa ponte. Portões de licença dos estimadores: Depth Anything V2
**Large é cc-by-nc (vetado)**; Small é Apache; MiDaS/DPT ok; conferir na
fonte antes de rodar (regra da casa).

## As demais hipóteses, em escada de custo (bancada Modal quente: ~R$ 1/folha)

| # | protótipo | o que testa | custo |
|---|---|---|---|
| **P1** | depth = estimador(proxy render) | H1, a mãe | 3 folhas |
| **P2** | `image` = **proxy render como REFERÊNCIA** + depth como controle (o `predict_t2i_control_ref.py` do repo faz exatamente isso; nosso app já tem o parâmetro `image` plumbado com None) | estrutura por DUPLA via — referência carrega o poste que o depth fino perde | 3 folhas |
| **P3** | controle = **canny(proxy render)** (o Union é multi-condição) | elemento fino: aresta preserva o poste que o depth não segura | 3 folhas |
| **P4** | depth adocicado: céu ≠ 0 (névoa longínqua), disparidade (1/z) em vez de z linear, leve blur | H1 barata, sem estimador (mantém pipeline 100% nossa) | 3 folhas |
| **P5** | checkpoint Union BASE (não-2602, sem destilação de CFG) + CFG verdadeiro | a destilação come obediência? | 3 folhas |
| P6 | fine-tune/LoRA do Union com pares NOSSOS (render+z-buffer do Blender — dataset infinito por construção) | a cirurgia profunda; VideoX-Fun **não publica** script de treino do controlnet flux2 (só inference) — custo real de engenharia | dias |

Regra de rodada: 1 variável por vez, 3 sementes, régua M1–M3 da bateria
(`mesa-fronteira/bateria_m1_m5.py`, já calibrada no padrão A), régua ANTES.
P1/P2/P3 são combináveis depois de medidos isolados.

## "Melhorar as referências" (a ordem do operador)

- prompt: o card do Union pede **prompt detalhado** para estabilidade — o da
  rodada era o selado (curto). Fora do selo da mesa (que já fechou), o
  protótipo pode usar prompt rico SEM trair a comparação: a régua é
  geométrica, não de texto;
- referência de imagem (P2) abre a porta que o mapa de produção pedia:
  o palco 3D REAL alimentando o pintor por dois canais (estrutura + aspecto);
- coletar 2–3 referências de valor/atmosfera da casa (capivara/garça, Gurney
  dissecado) para a fase pós-obediência — primeiro a régua, depois o gosto.

## Fuçada de comunidade (rodada 1 — 2026-08-16, inicial)

- confirmado na fonte: Union treina Canny/HED/Depth/Pose/MLSD/Scribble/Gray;
  showcase interno obedece; SEM script de treino publicado p/ flux2;
- `predict_t2i_control_ref.py` existe no repo (controle+referência juntos) —
  a via P2 é oficial, não gambiarra;
- prática comum da comunidade ControlNet: depth de estimador sobre render 3D
  (não z-buffer cru) — reforça H1.
- PENDENTE (próxima rodada de fuçada): discussões do repo Fun/HF sobre depth
  sintético; issues do VideoX-Fun; se alguém já mediu obediência do 2602 vs
  base; alternativas de controlnet FLUX.2 que surgirem (o campo tem semanas).

## RESULTADO da rodada P1–P4 (2026-08-16, mesma noite)

Régua = bateria M1–M3 calibrada no padrão A; 3 sementes; prompt/params
selados; folhas e insumos em `../pipeline/mesa-fronteira/prototipos/`.

| protótipo | M1 | M2 | M3 | leitura |
|---|---|---|---|---|
| base (z-buffer cru, mesa) | 0/6 | 1/6 | 1/6 | fora da distribuição |
| P1 estimado(proxy) | 2/3 · **−0,25/+0,49%** | 0/3 | 3/3 | H1 CONFIRMADA; poste dilui |
| P2 z-buffer+referência | 1/3 | 1/3 · **4 px** | 2/3 | referência trava parede |
| P3 canny(proxy) | 0/3 | 0/3 | 1/3 | DESCARTADO (perspectiva diverge) |
| **P4 = P1+P2+enxerto do poste** | **3/3** (−1,07/−0,98/+0,39%) | **3/3** (0/6/1 px) | **3/3** | **RÉGUA COMPLETA** |

**A receita que fecha o alvo (geometria):** depth ESTIMADO (DA-V2-Small,
Apache) sobre o proxy + **poste enxertado do z-buffer** (janela apertada
252–592×822–882, valor = mediana da parede estimada — a 1ª máscara vazou 54k
px de chão e custou 1 folha descartada, registrado) + proxy como `image` de
referência. M2 ficou MELHOR que o SDXL (0/6/1 vs 0/2/8 px).

Custo da rodada P1–P4: ~13 folhas ≈ US$ 2,5.

## FECHAMENTO da receita (2026-08-16, manhã) — crepúsculo e M5 dos cantos

**M5 das P4 neutras**: heurística limpa 3/3 E cantos conferidos a olho
(recortes `insp-P4-*` em `inspecao-cantos/`; `resultado-m5-p4.json`). Valor:
o braço B da mesa tinha fantasma em 4/6 — a receita P4 veio limpa; a
referência parece suprimir a assinatura.

**Crepúsculo na receita P4** (`rodar_p4_crepusculo.py`; prompt = o SELADO do
console; mesmos insumos compostos; job `guariba-cirurgia-p4-crepusculo`):

| folha | M1 | M2 | M3 | M4 (p1/med) | M5 | D1 indicador |
|---|---|---|---|---|---|---|
| 20260815 | ✓ −1,34% | ✓ 0 px | ✓ 1,91 px | ✓ 22/48 | ✓ | esq (1,009) |
| 20260816 | ✓ −0,35% | ✓ 4 px | ✓ 2,74 px | ✓ 17/40 | ✓ | dir (0,980) |
| 20260817 | ✓ +0,94% | ✓ 1 px | ✓ 1,91 px | ✓ 14/45 | ✓ | esq (1,042) |

**RÉGUA COMPLETA 3/3 na segunda luz — M4 folgado** (limiar p1 ≥ 8/med ≥ 25;
o SDXL r2 falhara com p1=3). **D1 a olho: 3/3 com o poente à ESQUERDA** — o
indicador mecânico mede a metade de cima do céu e o clarão fica baixo, por
isso marcou "dir" na 0816; a leitura fica registrada como indicador, não
portão. Cantos do crepúsculo quase pretos mas SEM traço de assinatura (olho +
heurística). Custo: 3 folhas (210/142/137 s) ≈ US$ 1; app descido ao final
(0 deployed), Volume fica. `resultado-p4-crepusculo.json` ao lado das folhas.

**A receita P4 está FECHADA nas duas luzes do selo.** Aberto:
- o custo estético da referência (o chapado do proxy contamina a pincelada —
  J-mesa quando o operador quiser julgar borda do P4 vs SDXL).

## Ligações

- bancada: `dominio-bancada-modal-flux2.md` (subir de novo custa minutos);
- recibos da mesa: `../pipeline/mesa-fronteira/resultado-mesa-fronteira.md`;
- a arquitetura que este domínio serve: o 3D dispõe, a difusão pinta, a
  geometria confere — agora com o pintor que o julgamento cego escolheu.
