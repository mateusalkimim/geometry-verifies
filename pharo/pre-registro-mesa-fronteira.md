# Pré-registro — mesa da fronteira: um modelo novo conserta o que o SDXL erra?

*Aberto 2026-08-16, por ordem do operador ("vamos fazer o pré-registro da mesa").
SELADO antes de qualquer folha dos braços. Emendas só datadas, com o texto
original intacto. Apostas do assistente carimbadas na §7, antes da primeira
geração.*

## A pergunta — e por que ela é esta

**"Um modelo de fronteira conserta os três defeitos MEDIDOS do SDXL na
prancheta, sem perder a borda perdida e sem perder a obediência geométrica?"**

Não é "qual modelo é mais potente". A lição está paga: as 216 folhas da linha
morta trocaram modelo e ambição juntos; a folha que prestou veio de arquitetura,
com o modelo mais velho da casa ("o ganho não veio do modelo" — post público de
2026-08-15). Fronteira só entra com pergunta que o SDXL comprovadamente falha.

**Os três defeitos, medidos nas rodadas 1–2 da folha da casa:**

| defeito | medida | onde |
|---|---|---|
| D1. direção de luz não obedece ao prompt | pedida "from the left"; obedecida em **1 de 3** folhas | rodada 2 (crepúsculo) |
| D2. preto esmagado na sombra | percentil 1 da silhueta em **2–3 de 255** (Gurney: *"dark but not black"*) | rodada 2 |
| D3. assinatura fantasma em canto | **3 folhas de 9** da série SDXL (r1: 20260816; r2: 20260815 e 20260816) | rodadas 1–2 |

## Contexto que este pré-registro herda (tudo medido antes)

- SDXL + depth (xinsir) na prancheta: razão cumeeira/poste com erro **−0,1% a
  −0,7%** em 6/6 folhas — o campeão a bater em geometria;
- Chroma1-HD (rodada exploratória 2026-08-15): **lei da destilação CONFIRMADA**
  (borda perdida genuína a denoise 0,80), mas **img2img não tem ponto doce** —
  d50 preserva e não pinta; d65 **apaga o poste** (elemento fino morre); d80
  pinta e **transforma a construção** (deriva de 40 px). Consequência de
  desenho: **braço de prancheta só entra com condicionamento de profundidade
  REAL**; img2img está vetado como via de prancheta;
- termos auditados 2026-08-15/16: **BFL API ⛔** (treina no input, sem opt-out);
  **fal.ai ✅** (input licenciado só para prestar o serviço; cláusula-cinza de
  Usage Data anonimizada/agregada, declarada; DPA SOC 2/ISO 27001);
  **Replicate ⚠️**; **Marble ✅ só no pago**. Documentos em
  `termos-hospedados/`;
- membrana: o que sai da casa é **proxy e mapa de profundidade** (bastidor).
  Obra nunca sai.

## Os braços

| braço | modelo | onde roda | condicionamento | custo |
|---|---|---|---|---|
| **A** | SDXL 1.0 + ControlNet depth (xinsir), 28p, cfg 6,5, força 0,8 | local | depth, força 0,8 | R$ 0 |
| **B** | FLUX.2-dev com condicionamento de profundidade | **fal.ai** | rota de depth NATIVA a confirmar no cardápio ANTES da rodada | ~US$ 0,03–0,05/folha |

**Portão do braço B**: se a fal não oferecer rota de profundidade real para o
FLUX.2-dev (depth control/tool, não img2img), **o braço cai e a mesa é adiada**
— não improvisada com via desigual. A desigualdade de condicionamento foi
exatamente o que a rodada exploratória do Chroma mediu como fatal.

> *Emenda pré-execução, 2026-08-16 (correção de redação, por apontamento do
> operador):* **"rota de profundidade" significa que o endpoint ACEITA O NOSSO
> mapa** — o `casa-profundidade.png` do Blender, injetado como imagem de
> controle. Nunca estimativa de profundidade da fal: o mapa da casa é exato por
> construção e é a vantagem estrutural da pipeline. O que o portão confirma é
> só a existência do canal de injeção. E fica registrado o horizonte do braço:
> em rodada futura, o **LoRA do traço do autor** também entra injetado no
> endpoint (a fal suporta LoRA custom na família FLUX) — com a ressalva de
> membrana marcada: subir o LoRA é subir um derivado das páginas da mão do
> autor; o termo da fal cobre input como serviço, mas a decisão de deixar esse
> derivado atravessar a membrana é do operador, no dia em que chegar.

> *Emenda pós-sondagem, 2026-08-15 (portão executado por ordem do operador;
> registro autorizado: "Pode registrar os dois"):* **o portão FALHOU e a mesa
> está ADIADA.** Sondado por três vias independentes, todas concordes e a custo
> zero: (1) OpenAPI público da fal; (2) catálogo autenticado completo
> (`api.fal.ai/v1/models`, 1450 endpoints — 49 da família FLUX.2, nenhum com
> canal de imagem de controle: só t2i, edit por referência, lora e trainers);
> (3) índice de docs `docs.fal.ai/llms.txt`. Todo o depth da fal é FLUX.**1**
> (`flux-control-lora-depth`, `flux-general`, `flux-lora-depth`). O braço B cai
> pela regra acima, sem discrição.
>
> **Achado colateral da sondagem** (registrado aqui, decidido fora daqui):
> `fal-ai/z-image/turbo/controlnet` tem canal genuíno de injeção — `image_url`
> obrigatório, **`preprocess: none` por default** (o nosso mapa entra cru),
> `control_scale` 0–1, `control_start/end` — e o checkpoint é público
> (Z-Image-Turbo-Fun-Controlnet-Union, família alibaba-pai/Fun; roda local no
> ComfyUI, 6B). **Não reabre esta mesa**: o Z-Image segue excluído pela lei da
> destilação (granito; máx. 8 passos confirma o turbo). O encaixe dele é o
> departamento de CONCEITO do mapa de produção ("LoRA da mão do autor + depth
> local") — mesma família da LoRA do caderno, via local, sem membrana.
> Caminhos possíveis adiante, todos decisão do operador por emenda: manter
> adiada; trocar o braço B por FLUX.1-dev+depth na fal (canal existe, mas não é
> fronteira); ou explorar Z-Image ControlNet local fora da mesa.

> *Emenda da via, 2026-08-15 (por decisão do operador: "Vamos mover dossiê →
> emenda da via → app"):* **a mesa DESADIA pela via do deploy próprio.** O
> braço B passa a ser **FLUX.2-dev + FLUX.2-dev-Fun-Controlnet-Union
> (alibaba-pai) servido por app `fal.App` NOSSO na infra da fal** — worker
> H100, efêmero (`fal run`, `min_concurrency=0`), endpoint privado atrás da
> nossa chave; pesos via `FAL_MODEL_WEIGHTS_DIR` (download uma vez); token HF
> como secret da fal (o FLUX.2-dev é gated). O canal de injeção passa a
> existir **por construção**: o input do app recebe o NOSSO
> `casa-profundidade.png` como imagem de controle, sem estimador de terceiro.
> Base documental: dossiê completo em `fal-docs/` (hospedagem + cliente) e
> termos já auditados em `termos-hospedados/`.
>
> Ressalvas declaradas: (a) **licença** — em deploy próprio a licença do
> FLUX.2-dev é a nossa (não-comercial p/ self-host); cobre bancada/bastidor
> desta mesa; adoção em produção exigiria licença BFL, o que o selo já previa;
> (b) **desigualdade residual dos braços** — A roda local no ControlNet xinsir,
> B roda na fal no ControlNet Fun; o condicionamento é depth REAL nos dois (a
> exigência do selo), mas os ControlNets são de autores distintos — registrado
> como limite de leitura da mesa, não como via desigual do tipo vetado;
> (c) **custo** — worker por segundo; teto US$ 10 da rodada inalterado, gasto
> declarado no resultado. Cliente da rodada: console web local em Python
> (padrão da casa — Limín/Têmis/Delfos), com job no Delfos aberto por
> construção; o console é instrumento, não critério — M1–M5 e a mesa na Têmis
> ficam exatamente como selados.

> *Adendo à emenda da via, 2026-08-15 (por decisão do operador: "Já mandei o
> e-mail; porta pro Modal em paralelo"):* o Private Serverless da fal revelou-se
> **enterprise gated** (formulário de vendas exige e-mail corporativo; pedido de
> acesso enviado por e-mail pelo operador). A via 1 ganha **hospedeiro paralelo:
> Modal**, com termos auditados em 2026-08-15 na mesma régua (recibos em
> `termos-hospedados/modal-*`): dono do dado é o cliente; licença limitada a
> prestar o serviço; **cláusula explícita de não-treino** sem consentimento
> escrito; expurgo pós-processamento; SOC 2 Type II — veredito ✅, mesmo degrau
> da fal. (RunPod auditado junto: ⚠️, licença de "melhoria" alcança o conteúdo;
> fora.) O app é o MESMO por contrato (mesmo input/output, mesmos pesos, mesmo
> commit do VideoX-Fun); muda só o hospedeiro — `app_flux2_depth_modal.py`.
> **Quem abrir primeiro (fal ou Modal) leva a rodada**; o outro fica de recibo.
> Nada disso toca critérios, folhas ou julgamento.

**Chroma NÃO é braço da mesa.** Ele está aprovado como **pintor livre**
(referência do método da capivara — geração livre + mão do autor); entra como
material de referência fora de julgamento. Colocá-lo na mesa repetiria o vício
já pago: *"a minha mesa só podia coroar o BASE"* — folha sem restrição sempre
parece melhor.

**Sem braço novo local**: klein base e Z-Image ficam fora — o primeiro pela
mesma falta de depth (mesmo veto do img2img), o segundo pela lei da destilação
já medida (granito).

## As folhas

Mesma cena da casa (`cena_folha_casa.py`, intocada), mesmo mapa de
profundidade, mesmas **3 sementes** (20260815/16/17; se a API não aceitar
semente, sorteia-se e declara-se), **2 regimes de luz** com os prompts EXATOS
das rodadas 1 e 2 (neutro e crepúsculo-Gurney):

> **6 folhas por braço, 12 julgáveis.** Custo estimado do braço B: < US$ 1.
> Teto autorizado desta rodada: **US$ 10** (~R$ 55) — sobra vira margem para
> re-rodadas de falha técnica, nunca para braço novo sem emenda.

## Critérios — mecânicos primeiro, cegos depois

### Mecânicos (rodam por script, sem julgamento; reprovação é da FOLHA)

| # | critério | limiar | origem do limiar |
|---|---|---|---|
| M1 | régua eq. (9): razão cumeeira/poste, **com poste PRESENTE** (gradiente ≥ 6 na coluna prevista) | \|erro\| ≤ 2% | 6/6 folhas SDXL ficaram ≤ 0,7%; 2% é folga honesta |
| M2 | **largura** contra o alpha declarado (linha y=448): bordas esq/dir | desvio ≤ 12 px | a deriva do Chroma d80 foi 40 px; a lição: régua vertical é necessária, não suficiente |
| M3 | obediência de silhueta (mediana da distância declarado→aresta forte) | ≤ 4 px | SDXL mediu 1,9–3,3 px |
| M4 | preto esmagado (só crepúsculo): percentil 1 e mediana da silhueta | p1 ≥ 8 **e** mediana ≥ 25 | Gurney (*dark but not black*); SDXL falhou com p1=2–3 |
| M5 | assinatura fantasma: varredura dos 4 cantos (70×300 px, ampliados) | presença = falha | 3/9 folhas SDXL tinham |

### Julgados às CEGAS pelo operador (mesa na Têmis)

| # | faceta | forma da pergunta (decidível, nunca estética global) |
|---|---|---|
| J1 | borda perdida | por PAR anônimo: "qual tratamento de borda está mais próximo das referências da casa (capivara/garça)?" |
| J2 | direção de luz (só crepúsculo) | por folha: "o sol desta folha está à esquerda?" sim/não |
| J3 | legibilidade | por folha: "isto lê como rancho pantaneiro?" sim/parcial/não |

## O julgamento

- mesa montada **pela API canônica da Têmis** (`core.montar` +
  `registrar_mesa`) — nunca JSON à mão; categoria visual; **`contem_obra`**
  (elemento da obra, mesmo sendo bastidor);
- rótulos aleatórios; **identidade só no gabarito-LACRADO**; nenhum canal desta
  conversa liga rótulo a braço depois de montada;
- web, fila PENDENTE, avisar o operador — **nunca abrir a UI por ele**;
- veredito e `tempo_humano_s` registrados como evento. **O julgamento é do
  operador; parecer meu não destrava gabarito.**

## §7 — APOSTAS DO ASSISTENTE, carimbadas antes da primeira folha

1. **D1 (direção de luz)**: braço B obedece "sol à esquerda" em **≥ 2 de 3**
   folhas de crepúsculo; braço A repete ≤ 1 de 3. É a aposta central — aderência
   de prompt é a força declarada da família FLUX;
2. **M1 (geometria)**: os dois braços passam, com \|erro\| ≤ 1% — depth real
   segura a geometria em ambos;
3. **M4 (preto)**: B falha menos que A (p1 de B ≥ 8 em ≥ 2 folhas de
   crepúsculo);
4. **M5 (fantasma)**: A apresenta ≥ 1; **B apresenta 0**;
5. **J1 (borda) — a aposta mais arriscada, e é a minha contra a fronteira**: A
   **vence ou empata**. O painterly do SDXL a cfg 6,5 é forte, e a família FLUX
   tende ao acabamento liso "digital". Se B vencer J1, a fronteira ganhou onde
   eu menos esperava — e o registro fica.

## O que esta mesa NÃO decide

- **adoção** — decide se existe candidato; trocar pilha da obra é decisão do
  operador com mesa vencida E custo/licença pesados juntos;
- **consistência entre planos** (a pergunta do Marble) — outra rodada;
- **figura humana** — o menino do 9.2 é outra classe de elemento, não coberta;
- **nada sobre os modelos fora dos braços** — Chroma livre é referência, não
  competidor; ausência ≠ reprovação;
- **o veredito da fal como fornecedor de produção** — a mesa usa a fal como
  bancada de teste; contrato de produção é outra leitura, na hora certa.

## Registro

Rodada com job no Delfos (braço B: `dono: fal.ai`), log em
`um log local`. Resultado em `resultado-mesa-fronteira.md`, com
as cinco apostas conferidas item a item e o gasto real declarado em R$.
