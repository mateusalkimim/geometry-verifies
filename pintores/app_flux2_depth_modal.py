# -*- coding: utf-8 -*-
"""
Mesa da fronteira, braço B — o MESMO app, hospedeiro Modal.

Porta 1:1 do app_flux2_depth.py (adendo à emenda da via, 2026-08-15): mesmo
contrato de entrada/saída, mesmos pesos, mesmo commit do VideoX-Fun — muda só
quem aluga o H100. Termos do Modal auditados ✅ (recibos em
../termos-hospedados/modal-*): licença limitada ao serviço, não-treino
explícito, expurgo pós-processamento, SOC 2 Type II.

Membrana: endpoint com PROXY AUTH do Modal (nunca URL aberta); mapa entra e
folha sai como base64 no corpo — nada nosso vai a storage de terceiro. Os
pesos (HF) persistem num modal.Volume; o HF_TOKEN vive num modal.Secret.

Bancada:
  pip install modal                       # (venv ~/venvs/fal serve)
  modal token new                         # login no navegador (operador)
  modal secret create huggingface --from-dotenv <arquivo .env FORA do repo com HF_TOKEN=...>
  modal deploy app_flux2_depth_modal.py   # imprime a URL *.modal.run
  → colar a URL no console local; headers de auth (MODAL_TOKEN_ID/
    MODAL_TOKEN_SECRET de proxy) vivem num .env fora da árvore do repo

Custo: H100 por segundo, escala a zero (scaledown_window=600 segura o worker
entre folhas). Download dos pesos (~75 GB) uma vez, no Volume.
"""
import base64

import modal

VIDEOX_FUN_COMMIT = "6787dc8ed4902b2a49f16e2541bd97936cc1e157"
UNION_CHECKPOINT = "FLUX.2-dev-Fun-Controlnet-Union-2602.safetensors"
PESOS = "/pesos"

app = modal.App("mesa-fronteira-flux2")

imagem = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "ffmpeg", "libgl1", "libglib2.0-0")
    .pip_install(
        "torch==2.6.0",
        "torchdiffeq",
        "torchsde",
        "accelerate==1.6.0",
        "transformers==4.51.3",
        "diffusers==0.33.1",
        "safetensors",
        "omegaconf",
        "einops",
        "timm",
        "sentencepiece",
        "Pillow",
        "opencv-python-headless",
        "albumentations",
        "ftfy",
        "beautifulsoup4",
        "func_timeout",
        "decord",
        "imageio[ffmpeg]",
        "scikit-image",
        "librosa",          # importado pelo videox_fun mesmo em t2i
        "tomesd",
        "datasets",
        "onnxruntime",
        "huggingface_hub",
        "hf_transfer==0.1.9",
        "fastapi[standard]",
        extra_index_url="https://download.pytorch.org/whl/cu124",
    )
    .run_commands(
        "git clone https://github.com/aigc-apps/VideoX-Fun.git /videox-fun "
        f"&& cd /videox-fun && git checkout {VIDEOX_FUN_COMMIT}"
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

volume_pesos = modal.Volume.from_name("mesa-fronteira-pesos", create_if_missing=True)


@app.cls(
    image=imagem,
    gpu="H100",
    cpu=8,
    memory=163_840,            # bf16 pleno (~115 GB) mora na RAM p/ cpu_offload
    timeout=3_600,
    scaledown_window=600,      # vivo entre as folhas da rodada; depois, zero
    volumes={PESOS: volume_pesos},
    secrets=[modal.Secret.from_name("huggingface")],
    max_containers=1,
)
class MesaFronteiraFlux2:
    @modal.enter()
    def setup(self):
        import os
        import sys

        sys.path.insert(0, "/videox-fun")
        os.chdir("/videox-fun")  # config/flux2/*.yaml é relativo à raiz do repo

        from huggingface_hub import hf_hub_download, snapshot_download

        modelo_dir = f"{PESOS}/FLUX.2-dev"
        snapshot_download(
            "black-forest-labs/FLUX.2-dev",   # gated: HF_TOKEN do secret
            local_dir=modelo_dir,
            ignore_patterns=["flux2-dev.safetensors"],  # single-file redundante
        )
        union_path = hf_hub_download(
            "alibaba-pai/FLUX.2-dev-Fun-Controlnet-Union",
            UNION_CHECKPOINT,
            local_dir=f"{PESOS}/fun-controlnet-union",
        )
        volume_pesos.commit()

        # montagem — espelho do predict_t2i_control.py (gabarito publicado)
        import torch
        from diffusers import FlowMatchEulerDiscreteScheduler
        from omegaconf import OmegaConf
        from safetensors.torch import load_file
        from videox_fun.models import (AutoencoderKLFlux2,
                                       Flux2ControlTransformer2DModel,
                                       Mistral3ForConditionalGeneration,
                                       PixtralProcessor)
        from videox_fun.pipeline import Flux2ControlPipeline

        dtype = torch.bfloat16
        config = OmegaConf.load("config/flux2/flux2_control.yaml")

        transformer = Flux2ControlTransformer2DModel.from_pretrained(
            modelo_dir, subfolder="transformer",
            low_cpu_mem_usage=True, torch_dtype=dtype,
            transformer_additional_kwargs=OmegaConf.to_container(
                config["transformer_additional_kwargs"]),
        ).to(dtype)
        estado = load_file(union_path)
        faltando, sobrando = transformer.load_state_dict(estado, strict=False)
        print(f"union: missing={len(faltando)} unexpected={len(sobrando)}")

        vae = AutoencoderKLFlux2.from_pretrained(modelo_dir, subfolder="vae").to(dtype)
        tokenizer = PixtralProcessor.from_pretrained(modelo_dir, subfolder="tokenizer")
        text_encoder = Mistral3ForConditionalGeneration.from_pretrained(
            modelo_dir, subfolder="text_encoder",
            torch_dtype=dtype, low_cpu_mem_usage=True,
        )
        scheduler = FlowMatchEulerDiscreteScheduler.from_pretrained(
            modelo_dir, subfolder="scheduler")

        self.pipeline = Flux2ControlPipeline(
            vae=vae, tokenizer=tokenizer, text_encoder=text_encoder,
            transformer=transformer, scheduler=scheduler,
        )
        self.pipeline.enable_model_cpu_offload(device="cuda")

    @modal.method()
    def gerar_remoto(self, corpo: dict) -> dict:
        """Via SDK (.remote()): sem o teto de ~150s do gateway web — é a via
        do console. Mesmo contrato do app da fal: FolhaInput → FolhaOutput.
        P2 (cirurgia): `reference_image_b64` opcional entra como `image` do
        pipeline (a via do predict_t2i_control_ref.py, oficial do repo)."""
        return self._gerar(corpo)

    @modal.method()
    def estimar_depth(self, corpo: dict) -> dict:
        """P1 da cirurgia: depth de ESTIMADOR sobre o NOSSO render (H1).
        Depth Anything V2 SMALL (Apache-2.0, conferido na fonte 2026-08-16;
        o Large é cc-by-nc e está vetado). Roda no worker (torch já na
        imagem); saída = mapa em base64 no tamanho pedido."""
        import io

        import numpy as np
        import torch
        from PIL import Image as PILImage
        from transformers import pipeline as hf_pipeline

        png = base64.b64decode(corpo["image_b64"])
        img = PILImage.open(io.BytesIO(png)).convert("RGB")
        est = hf_pipeline("depth-estimation",
                          model="depth-anything/Depth-Anything-V2-Small-hf",
                          device=0 if torch.cuda.is_available() else -1)
        prof = est(img)["depth"]                     # PIL, perto = claro
        prof = prof.resize(img.size)
        arr = np.array(prof).astype(np.float32)
        arr = (arr - arr.min()) / max(1e-6, arr.max() - arr.min()) * 255.0
        buf = io.BytesIO()
        PILImage.fromarray(arr.astype("uint8")).save(buf, format="PNG")
        return {"depth_b64": base64.b64encode(buf.getvalue()).decode()}

    @modal.fastapi_endpoint(method="POST", requires_proxy_auth=True)
    def gerar(self, corpo: dict) -> dict:
        """Via HTTP (fica para depuração rápida; sujeita ao teto de ~150s)."""
        return self._gerar(corpo)

    def _gerar(self, corpo: dict) -> dict:
        import io
        import time

        import torch
        from videox_fun.utils.utils import get_image, get_image_latent

        png = base64.b64decode(corpo["control_image_b64"])
        caminho_mapa = "/tmp/mapa-controle.png"
        with open(caminho_mapa, "wb") as f:
            f.write(png)

        referencia = None
        if corpo.get("reference_image_b64"):
            with open("/tmp/referencia.png", "wb") as f:
                f.write(base64.b64decode(corpo["reference_image_b64"]))
            referencia = get_image("/tmp/referencia.png")

        altura = int(corpo.get("height", 832))
        largura = int(corpo.get("width", 1216))
        sample_size = [altura, largura]
        control = get_image_latent(caminho_mapa, sample_size=sample_size)[:, :, 0]
        inpaint = torch.zeros([1, 3, *sample_size])
        mask = torch.ones([1, 1, *sample_size]) * 255

        gen = torch.Generator(device="cuda").manual_seed(int(corpo["seed"]))
        t0 = time.time()
        with torch.no_grad():
            folha = self.pipeline(
                prompt=corpo["prompt"],
                height=altura,
                width=largura,
                generator=gen,
                guidance_scale=float(corpo.get("guidance_scale", 4.0)),
                image=referencia,
                inpaint_image=inpaint,
                mask_image=mask,
                control_image=control,
                num_inference_steps=int(corpo.get("num_inference_steps", 50)),
                control_context_scale=float(corpo.get("control_context_scale", 0.75)),
            ).images[0]
        dt = time.time() - t0

        buf = io.BytesIO()
        folha.save(buf, format="PNG")
        return {
            "image_b64": base64.b64encode(buf.getvalue()).decode(),
            "seed": int(corpo["seed"]),
            "segundos_inferencia": round(dt, 1),
        }
