# Resultado — mesa da fronteira (braço B: FLUX.2-dev + Fun-Union no Modal)

*2026-08-16. Rodada selada executada por completo: 6 folhas (2 luzes × 3
sementes, prompts/mapa/cena EXATOS do selo), bateria M1–M5 com a MESMA régua
da série (eq. 9 via `metrologia_vista_unica`, receita recuperada do transcrito
de 2026-08-15 e validada no padrão A: 1,342/−0,61% e 1,340/−0,7% — os valores
publicados). Instrumento em `bateria_m1_m5.py`; dados em
`resultado-bateria-m1m5.json`; cantos ampliados em `inspecao-cantos/`.*

## O veredito mecânico

**Nenhuma folha do braço B sobrevive à bateria** (reprovação é da FOLHA, pelo
selo):

| folha B | M1 (régua) | M2 (largura ≤12) | M3 (silhueta ≤4) | M4 (preto) | M5 (fantasma, a olho) |
|---|---|---|---|---|---|
| neutro-15 | −3,0% ✗ | 31 px ✗ | 2,7 ✓ | — | assinatura ✗ |
| neutro-16 | poste AUSENTE ✗ | 30 px ✗ | 4,1 ✗ | — | assinatura ✗ |
| neutro-17 | +13,4% ✗ | 22 px ✗ | 6,7 ✗ | — | rubrica ✗ |
| crep-15 | poste AUSENTE ✗ | >60 px ✗ | 9,4 ✗ | p1=19 ✓ | limpo ✓ |
| crep-16 | poste AUSENTE ✗ | **12 px ✓** | 6,4 ✗ | p1=9 ✓ | assinatura ✗ |
| crep-17 | poste AUSENTE ✗ | >60 px ✗ | 20,8 ✗ | p1=11 ✓ | limpo ✓ |

Padrão A na mesma bateria (validação do instrumento): M1 ✓✓ (−0,6/−0,7%; a
20260817 dá gradiente 5,6 vs limiar 6 — discrepância de fio de navalha com o
recibo da série, declarada), M2 ✓✓✓ (0/2/8 px), M3 ✓ (0,9–1,9 px).

**Leitura**: o único canal de depth existente para FLUX.2-dev (ControlNet
comunitário Fun-Union) obedece profundidade de ESTIMADOR em cena densa (o
showcase deles cola), mas **não segura a prancheta sintética**: geometria fina
instável entre sementes (−3% a +13% onde o SDXL varia 0,2%), paredes derivando
22–60+ px, e o elemento fino (poste) morre em 4/6 — o MESMO modo de falha do
Chroma d65. A vitória isolada do B é real e vale registro: **3/3 no M4** — o
FLUX.2 não esmaga o preto do crepúsculo (p1 9–19 vs 2–3 do SDXL; Gurney
respeitado).

## As 5 apostas do assistente (§7 do selo), conferidas

1. **D1/J2 (sol à esquerda ≥2/3)** — NÃO AFERIDA: comparação cega não montada
   (nenhuma folha B qualificada; julgar borda/luz de folha que não segura
   geometria repetiria o vício "folha sem restrição sempre parece melhor");
2. **M1 nos dois braços ≤1%** — **PERDIDA**: A passa (−0,6/−0,7%), B 0/6;
3. **M4: B falha menos que A** — **CONFIRMADA**: B 3/3 com p1 9–19; A r2
   falhou 3/3 (p1=3, mediana 19–24);
4. **M5: A ≥1, B = 0** — **METADE PERDIDA**: A tem (histórico 3/6), mas B tem
   4/6 — o fantasma veio JUNTO com a fronteira, não embora;
5. **J1 (borda): A vence/empata** — NÃO AFERIDA (mesma razão da 1).

## Decisões que este resultado fecha e abre

- a pergunta selada — *"um modelo de fronteira conserta os 3 defeitos sem
  perder borda e obediência?"* — fecha em **NÃO pela via disponível**: D2
  (preto) o FLUX.2 conserta; D1 não medido às cegas; D3 (fantasma) PIOROU; e o
  preço foi a obediência geométrica, que era inegociável;
- o SDXL + xinsir **permanece o campeão da prancheta** — agora com recibo
  contra a fronteira, não por falta de adversário;
- a comparação cega cega **não se monta** por falta de matéria qualificada
  (registrado como parte do resultado, não como omissão).

## O julgamento cego (emenda de 2026-08-16, pós-veredito)

O autor reafirmou a mesa após a ressalva de folhas mecanicamente
desqualificadas — e o julgamento dele derrubou a minha leitura. Duas mesas
cega (um papel por mesa), lacradas, `contem_obra`; vereditos salvos em
138 s (J1) e 175 s (J2+J3); revelação mecânica pós-veredito:

| critério cego | SDXL (A) | FLUX.2 (B) |
|---|---|---|
| J1 borda (por par) | 5 derrotas, 1 empate atrás | **6/6 vitórias** |
| J2 sol à esquerda (crepúsculo) | 2/3 conforme | **3/3 conforme** |
| J3 lê como rancho pantaneiro | **0/6 (todos desvio)** | **6/6 conforme** |

Apostas restantes: **nº 5 PERDIDA por inteiro** (0/6 — e o selo previa: "se B
vencer J1, a fronteira ganhou onde eu menos esperava — e o registro fica");
nº 1 metade confirmada (B ≥2/3 ✓; A fez 2/3, não ≤1/3 — o julgamento humano
foi mais generoso com A que a medição da rodada 2, ambos registrados).

**Síntese final, com os dois olhos abertos**: a resposta da pergunta selada
segue NÃO — a obediência geométrica era inegociável e perdeu-se. Mas o
retrato mudou de natureza: **a fronteira é o melhor PINTOR da bancada**
(borda, luz, legibilidade, valor — 4 critérios de pintura, 4 vitórias) e **o
SDXL é o melhor ARQUITETO** (geometria a 0,6%, e só ele) — que, aos olhos
cegos do autor, **não lê como Pantanal** (0/6 no J3, o dado mais duro da
noite contra o campeão da casa). A arquitetura do OPERADOR — o 3D dispõe, a
difusão pinta, a geometria confere — é exatamente o casamento que estes dois
recibos pedem; nenhum dos dois pintores sozinho é a prancheta.

## Gasto

Worker H100 no Modal: ~22 min total (3 boots de depuração + prova + teste
escala 0,80 + rodada de 12,9 min) ≈ **US$ 1,5 ≈ R$ 8** (exato no dashboard do
Modal). Teto de US$ 10: respeitado com folga. fal: R$ 0 (bloqueada no gate
enterprise; pedido de acesso enviado).
