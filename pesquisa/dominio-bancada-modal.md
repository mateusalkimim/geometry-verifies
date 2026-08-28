# Domínio: bancada de fronteira na nuvem (Modal) — o diário que evita repagar

*Pesquisa operacional consolidada da noite de 2026-08-15/16 (mesa da
fronteira). Tudo aqui foi EXECUTADO e pago uma vez; o propósito deste
documento é que a próxima subida custe minutos, não a madrugada. Fonte:
sessão ao vivo; artefatos em `pipeline/mesa-fronteira/`.*

## O mapa do território (por que Modal, e não fal/RunPod)

| hospedeiro | veredito | motivo |
|---|---|---|
| fal (cardápio) | sem canal | 49 endpoints FLUX.2, ZERO com imagem de controle (3 vias: OpenAPI público, catálogo autenticado 1450 endpoints, docs llms.txt) |
| fal (serverless próprio) | **BLOQUEADO** | Private Serverless é enterprise/beta privado; formulário exige e-mail corporativo; pedido enviado por e-mail, sem resposta até 2026-08-16 |
| Modal | ✅ USADO | self-serve (só cartão), termos auditados ✅ (não-treino explícito; recibos em `pipeline/termos-hospedados/modal-*`) |
| RunPod | ⚠️ | licença de "melhoria" alcança o conteúdo; sem cláusula de não-treino |

## A pilha que FUNCIONA (estado final, commit `30e1c8a`)

- **app**: `pipeline/mesa-fronteira/app_flux2_depth_modal.py` — `modal.App`,
  H100, `cpu=8`, `memory=163_840` (bf16 pleno ~115 GB mora na RAM p/
  `enable_model_cpu_offload`), `scaledown_window=600`, `max_containers=1`;
- **pesos**: `modal.Volume` `mesa-fronteira-pesos` — FLUX.2-dev (sem o
  single-file de 64 GB, `ignore_patterns`) + Union-2602. Download UMA vez
  (~75 GB); depois disso, boot de container em ~50 s;
- **segredo**: `modal.Secret.from_name("huggingface")` criado com
  `modal secret create huggingface --from-dotenv <arquivo .env fora do repo com HF_TOKEN=...>`
  (`--from-dotenv` evita o token no argv — ver falha F6);
- **inferência**: VideoX-Fun pinado (`6787dc8e`), `Flux2ControlPipeline`,
  espelho do `predict_t2i_control.py` (gabarito publicado). `os.chdir` no
  clone porque `config/flux2/flux2_control.yaml` é relativo à raiz do repo;
- **chamada**: `modal.Cls.from_name(...)().gerar_remoto.remote(corpo)` — via
  SDK, **NUNCA** o endpoint web para inferência (ver F7). O fastapi_endpoint
  com `requires_proxy_auth=True` ficou só para depuração;
- **membrana**: mapa entra base64 no corpo; folha volta base64; nada nosso
  toca storage de terceiro. Endpoint nunca aberto.

## AS FALHAS, uma a uma (o preço já pago)

| # | falha | sintoma | causa | conserto |
|---|---|---|---|---|
| F1 | `fal secrets set HF_TOKEN <v>` | erro de parse | sintaxe é `NAME=VALUE` | e o erro **ecoou o token no terminal** → rotação forçada |
| F2 | serverless fal | `Insufficient permissions` | enterprise gate | via Modal |
| F3 | `modal deploy app.py` | arquivo não achado | o shell da sessão reseta o cwd | **sempre caminho absoluto** |
| F4 | 1º deploy | `add a payment method` | conta sem cartão | cartão no dashboard; a IMAGEM já ficou construída (cache) |
| F5 | crash-loop `GatedRepoError 401` | worker não baixa FLUX.2-dev | token revogado (rotação da F1) **e** o deploy CONGELA a versão do secret | atualizar secret **não basta**: `modal deploy` de novo re-resolve |
| F6 | risco de vazamento | — | token no argv aparece em erro/ps | `--from-dotenv`; filtrar `hf_...` de qualquer saída |
| F7 | request cancelado ~121 s, retry queimando GPU | `Received a cancellation signal` | **gateway web do Modal corta síncrono em ~150 s**; folha leva 100–180 s | `@modal.method()` + `.remote()` via SDK — sem teto |
| F8 | `ModuleNotFoundError: librosa` | worker morre no import | VideoX-Fun importa áudio até em t2i; eu tinha enxugado o requirements | requirements COMPLETO do repo deles (librosa, tomesd, datasets, onnxruntime) |
| F9 | job registrado órfão | quadro mentindo | console reiniciado com job aberto | fechar com `resultado: erro` ANTES de reiniciar |

## Números de referência (H100, medidos)

- boot com pesos no Volume: **~50 s**; download inicial: pago uma vez nos
  boots da F8 (aproveitado);
- folha 1216×832, 50 passos, cpu_offload: **97–180 s** (primeira da sessão é
  a mais lenta; ~3,5 s/passo depois de quente);
- rodada de 6 folhas com `keep_alive`: **12,9 min de worker**;
- custo da noite INTEIRA (3 boots de depuração + prova + teste 0,80 + rodada
  + julgamentos): **~US$ 1,5 ≈ R$ 8**. Teto de US$ 10 nunca ameaçado.

## Checklist da PRÓXIMA subida (o desperdício zero)

1. `modal app list` — conferir parado; Volume `mesa-fronteira-pesos` existe?
   Então o download já está pago;
2. token HF válido? `curl` no resolve com Bearer ANTES de subir worker
   (F5: 200 local ≠ secret válido no deploy — se rotacionou, `secret create
   --force` **e redeploy**);
3. `modal deploy <CAMINHO ABSOLUTO>` (F3);
4. inferência SEMPRE por `.remote()` (F7); console local roda com
   `o ambiente virtual do projeto` (tem o pacote `modal`);
5. processo longo = job registrado aberto pelo caminho que roda, fechado
   inclusive em erro (F9);
6. ao encerrar: `modal app stop <app> --yes` (sem `--yes` trava pedindo
   confirmação interativa). Volume fica — é o que torna a próxima subida
   barata.

## O que a bancada NÃO resolve (recibo da mesa, 2026-08-16)

O canal funciona; a OBEDIÊNCIA do Union ao mapa sintético não veio (M1–M3
reprovados nas 6; escala 0,65–0,80 não é o botão; polaridade confere; o
showcase deles obedece bem — com depth de ESTIMADOR). A investigação da
cirurgia é outro domínio: `dominio-cirurgia-obediencia-flux2.md`.
