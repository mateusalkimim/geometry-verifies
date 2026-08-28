# -*- coding: utf-8 -*-
"""Registro de progresso dos processos longos.

Na casa de origem, todo processo longo abre um job num governador central
(registro de processos) — o autor nunca fica cego ao andamento, e o job FECHA mesmo em
erro. Fora dela, este shim vira diário no stdout com o mesmo contrato.
Para plugar o seu: exporte DELFOS_JOBS=<caminho de um jobs.py com
abrir_job/avancar/fechar>.
"""
import importlib.util
import os

_caminho = os.environ.get("DELFOS_JOBS")
if _caminho and os.path.exists(_caminho):
    _spec = importlib.util.spec_from_file_location("delfos_jobs", _caminho)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    abrir_job, avancar, fechar = _mod.abrir_job, _mod.avancar, _mod.fechar
else:
    def abrir_job(nome, descricao, total, **kw):
        print(f"[job] {nome}: {descricao} (0/{total})", flush=True)

    def avancar(nome, feito, detalhe=""):
        print(f"[job] {nome}: {feito} · {detalhe}", flush=True)

    def fechar(nome, resultado):
        print(f"[job] {nome}: FECHADO — {resultado}", flush=True)
