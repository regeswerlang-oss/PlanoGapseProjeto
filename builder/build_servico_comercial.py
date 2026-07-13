#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Builder do painel "Serviço × Comercial" — DIGITRO (000348D0).

Une, num HTML único TOTVS:
  - Resumo de HORAS em 4 baldes (de-para aprovado pelo usuario):
        Estimado (universo)  | Aprovado como GAP | Estimado nao aprovado | Saindo/Cancelado
  - Conflitos RFP x GAP (8 de grau Alto destacados)
  - Notas comerciais do NotebookLM por grupo de conflito
  - Itens declinados pelo cliente (alimentados pelas decisoes "Recusar")
  - Painel de Tomada de Decisao por item (Aprovar / 2a Fase / Contorno / Recusar)
    com persistencia local (localStorage) que recalcula os baldes ao vivo.

FONTES (offline agora; trocar por API Tasks SC depois):
  - gaps_digitro.json        -> 64 GAPs (id, title, est, status, modulo, categoria, necessidade, tags)
  - subitens_digitro.json    -> horas contratadas por modulo/funcionalidade (baseline comercial)
  - conflitos curados abaixo  -> derivados de conflitos_RFP_x_GAPs / historico_comercial (NotebookLM)

Para plugar a API depois: substituir load_gaps()/load_subitens() por chamadas
a api-tasks-totvs-sc (mesmo schema de dict) — o resto do pipeline nao muda.
"""
import json, os, datetime

# ---- localizacao das fontes (VM mount) -------------------------------------
DADOS = "/sessions/upbeat-great-curie/mnt/Dados"
OUT_PROJ = "/sessions/upbeat-great-curie/mnt/Dashboard análise Serviço - Comercial"
OUT_TMP  = "/sessions/upbeat-great-curie/mnt/outputs"

# ---- de-para dos baldes (APROVADO PELO USUARIO) ----------------------------
TAGS_BLOQ_APROV = {"ORCAMENTO PENDENTE", "AGUARDANDO APROVACAO", "AGUARD. CLIENTE",
                   "PENDENTE COM CLIENTE"}
STATUS_CANCEL = {"CANCELADO", "RECUSADO"}
TAGS_CANCEL   = {"RECUSADO", "DECLINADO"}

def norm(s): return (s or "").strip().upper()

def bucket(g):
    """Classifica um GAP em um dos 4 baldes (estado-base, antes de decisoes)."""
    st = norm(g.get("status"))
    tags = {norm(t) for t in g.get("tags", [])}
    est = float(g.get("est") or 0)
    if st in STATUS_CANCEL or (tags & TAGS_CANCEL):
        return "saindo"
    if ("GAP" in tags) and st == "AGENDADO" and not (tags & TAGS_BLOQ_APROV):
        return "aprovado"
    if est > 0:
        return "naoaprovado"
    return "sem_est"

# ---- carga das fontes ------------------------------------------------------
def load_gaps():
    with open(os.path.join(DADOS, "gaps_digitro.json"), encoding="utf-8") as f:
        return json.load(f)

def load_subitens():
    with open(os.path.join(DADOS, "subitens_digitro.json"), encoding="utf-8") as f:
        return json.load(f)

# ---- conflitos RFP x GAP + notas NotebookLM (curados das fontes) -----------
CONFLITOS = [
    {"ids": ["00012230"], "titulo": "Etiquetas - Código de Barras (EAN)", "modulo": "Estoque", "grau": "Alto",
     "rfp": "Sim / Nativo", "obs": "“Através de personalização do modelo específico.”", "grupo": "etiquetas"},
    {"ids": ["00012226"], "titulo": "Etiquetas - Localização", "modulo": "Estoque", "grau": "Alto",
     "rfp": "Sim / Nativo", "obs": "“Através de personalização do modelo específico.”", "grupo": "etiquetas"},
    {"ids": ["00011332"], "titulo": "Etiquetas - ANATEL", "modulo": "Estoque", "grau": "Alto",
     "rfp": "Sim / Nativo", "obs": "“Através de personalização do modelo específico.”", "grupo": "etiquetas"},
    {"ids": ["00012231"], "titulo": "Etiquetas - Rastreabilidade", "modulo": "Estoque", "grau": "Alto",
     "rfp": "Sim / Nativo", "obs": "Rastreabilidade personalizável de materiais.", "grupo": "etiquetas"},
    {"ids": ["00011561"], "titulo": "Envio de documentos anexados por e-mail ao faturar", "modulo": "Faturamento", "grau": "Alto",
     "rfp": "Sim / Nativo (sem ressalva)", "obs": "Disparo automático de XML/DANFE/boleto + anexos (CNDs).", "grupo": "envio_email"},
    {"ids": ["00013021"], "titulo": "Comissão - Relatório / baixa com NF", "modulo": "Financeiro", "grau": "Alto",
     "rfp": "Sim / Nativo", "obs": "“Regras de comissionamento devem ser personalizadas.”", "grupo": "comissao"},
    {"ids": ["00013007"], "titulo": "Política de precificação personalizada", "modulo": "Comercial", "grau": "Alto",
     "rfp": "Sim / Nativo", "obs": "“A informação de precificação e custos deverá vir do ERP.”", "grupo": "precificacao"},
    {"ids": ["00014126"], "titulo": "Registrar o histórico por cliente", "modulo": "Comercial", "grau": "Alto",
     "rfp": "Sim / Nativo", "obs": "Histórico desde 1ª contratação até renovações.", "grupo": "historico"},
    {"ids": ["00012228", "00012235", "00012369"], "titulo": "Etiquetas - Esp. Técnicas / Minuta / RAC", "modulo": "Estoque", "grau": "Médio",
     "rfp": "Sim / Nativo", "obs": "Subtipos não citados literalmente na RFP.", "grupo": "etiquetas"},
    {"ids": ["00013004"], "titulo": "Comissão multinível", "modulo": "Faturamento", "grau": "Médio",
     "rfp": "Sim / Nativo", "obs": "“Regras de comissionamento devem ser personalizadas.”", "grupo": "comissao"},
    {"ids": ["00013005"], "titulo": "Acompanhamento de metas comerciais no contrato", "modulo": "Faturamento", "grau": "Médio",
     "rfp": "Sim / Nativo", "obs": "Metas/comissões por etapa do funil.", "grupo": "comissao"},
    {"ids": ["00013006"], "titulo": "Dashboard comercial", "modulo": "Faturamento", "grau": "Médio",
     "rfp": "Sim / Nativo", "obs": "Dashboards de performance do funil.", "grupo": "comercial"},
    {"ids": ["00010891"], "titulo": "Fluxo de aprovação - borderô de pagamento", "modulo": "Financeiro", "grau": "Médio",
     "rfp": "Sim / Nativo", "obs": "“Personalização via Workflow.”", "grupo": "workflow"},
    {"ids": ["00014127"], "titulo": "Carteira Cliente / Audit Trail", "modulo": "Comercial", "grau": "Médio",
     "rfp": "Sim / Nativo", "obs": "Controle de histórico com data e responsável.", "grupo": "historico"},
    {"ids": ["00011811"], "titulo": "Classificação de risco e análise de crédito", "modulo": "Financeiro", "grau": "Médio",
     "rfp": "Sim / Nativo", "obs": "“Via integração c/ Protheus.”", "grupo": "credito"},
    {"ids": ["00012992"], "titulo": "Classificação de fornecedores", "modulo": "Compras", "grau": "Médio",
     "rfp": "Sim / Nativo", "obs": "Segmentação personalizável de clientes/fornecedores.", "grupo": "cadastros"},
    {"ids": ["00012993"], "titulo": "Relatório PC em aberto com prazo de entrega", "modulo": "Compras", "grau": "Médio",
     "rfp": "Sim / Nativo", "obs": "Via TOTVS SmartView.", "grupo": "compras"},
    {"ids": ["00011991"], "titulo": "Saldo/notas em poder de terceiros", "modulo": "Fiscal", "grau": "Médio",
     "rfp": "Sim / Nativo", "obs": "Controle de saldo em posse de terceiros.", "grupo": "estoque"},
    {"ids": ["00010911", "00012808", "00012810", "00013512"], "titulo": "Servidor/Gerador/Gestão de licenças", "modulo": "Geral", "grau": "Médio",
     "rfp": "Sim / Nativo", "obs": "Integração c/ servidor de licenças está Fora do Escopo (API).", "grupo": "licencas"},
    {"ids": ["00010910", "00013391", "00014128", "00014129", "00014130", "00014633"], "titulo": "Integração suporte / Field Service / Controle de atendimentos", "modulo": "Gestão de Serviços", "grau": "Médio/Alto",
     "rfp": "Sim / Nativo", "obs": "TOTVS Field Service nativo; integrações externas = Médio.", "grupo": "suporte"},
    {"ids": ["00012999", "00013000", "00013001", "00013002"], "titulo": "Amarrações Plano Contas × CC × Item Contábil + Validadores", "modulo": "Contabilidade", "grau": "Médio",
     "rfp": "Sim / Nativo", "obs": "Gestão de múltiplas UN, CC e contas.", "grupo": "contabil"},
    {"ids": ["00014087"], "titulo": "Campos customizados proposta × contrato", "modulo": "Comercial", "grau": "Médio",
     "rfp": "Sim / Nativo", "obs": "“Avaliar extensão da integração padrão.”", "grupo": "contratos"},
    {"ids": ["00014088"], "titulo": "Integração TCRM × Contratos", "modulo": "Comercial", "grau": "Médio",
     "rfp": "Sim / Integrado Protheus", "obs": "Gerar contrato após aceite da proposta.", "grupo": "contratos"},
]

NLM_NOTAS = {
    "etiquetas": "Proposta previu apenas “Impressão de Etiquetas (1 Modelo)” no módulo ACD. Em reunião, a TOTVS esclareceu que NÃO parametrizará todos os modelos atuais — a proposta contempla UMA etiqueta personalizada; modelos adicionais são itens extras de projeto. Horas diluídas no bloco Personalizações (1.006h / R$ 221.320,00).",
    "comissao": "Vinicius (TOTVS) admitiu: “100% das vezes que entra comissionamento, parte para desenvolvimento”. Regras da Dígitro: liberação só após recebimento financeiro; comissão multinível/split (ex. 5%/3%/1% na mesma venda); validação de margem mínima (ex. 45%). Protheus suporta até 5 representantes por contrato; regras específicas foram para a fila de GAP. Recomendado MIT de mudança de escopo.",
    "precificacao": "A Dígitro busca dar autonomia ao vendedor para obter preço instantâneo (~80% dos casos) sem suporte interno. TOTVS sugeriu transformar variações (prazos 12/24/36, faixas de volume) em Part Numbers (SKUs), tabelas de preço por UF, faixas de desconto e validade; apresentou o módulo Formação de Preço para eliminar planilhas externas.",
    "envio_email": "Envio manual de CNDs/comprovantes a órgãos públicos é gargalo operacional (“processo desgraçado” no Datasul). TOTVS sugeriu Banco de Conhecimento para centralizar documentos por cliente/contrato; a automação de anexos variáveis por cliente exige personalização. Proposta lista “Envio do boleto com a NFe” no bloco de Personalizações.",
    "historico": "Histórico do cliente (1ª contratação → ampliações/renovações) e Audit Trail. Tratado em reunião como necessidade de registro contínuo; parte recai sobre desenvolvimento (Alto) e parte sobre controle de alterações (Médio).",
}

CONTRATO_PERSONALIZACOES_H = 1006
CONTRATO_PERSONALIZACOES_RS = 221320.00

def build():
    gj = load_gaps()
    gaps = gj["gaps"]
    sub = load_subitens()

    for g in gaps:
        g["bucket"] = bucket(g)

    soma = {"estimado": 0.0, "aprovado": 0.0, "naoaprovado": 0.0, "saindo": 0.0}
    cont = {"estimado": 0, "aprovado": 0, "naoaprovado": 0, "saindo": 0}
    for g in gaps:
        e = float(g.get("est") or 0)
        if e > 0:
            soma["estimado"] += e; cont["estimado"] += 1
        b = g["bucket"]
        if b in soma and b != "sem_est":
            soma[b] += e; cont[b] += 1

    contratadas = {k: v.get("total", 0) for k, v in sub.items()}
    total_contratadas = sum(contratadas.values())

    conf_ids = {}
    for c in CONFLITOS:
        for i in c["ids"]:
            conf_ids[i] = c["grau"]

    data = {
        "cliente": gj.get("cliente"), "customer": gj.get("customer"),
        "gerado_em": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "fonte_gaps_em": gj.get("gerado_em"),
        "total_gaps": gj.get("total"), "soma_horas": gj.get("soma_horas"),
        "gaps": gaps,
        "buckets": {"soma": soma, "cont": cont},
        "contratadas": contratadas, "total_contratadas": total_contratadas,
        "conflitos": CONFLITOS, "nlm_notas": NLM_NOTAS, "conf_ids": conf_ids,
        "personalizacoes_h": CONTRATO_PERSONALIZACOES_H,
        "personalizacoes_rs": CONTRATO_PERSONALIZACOES_RS,
    }
    return data

if __name__ == "__main__":
    d = build()
    with open(os.path.join(OUT_TMP, "dados_servico_comercial.json"), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    b = d["buckets"]
    print("OK — cliente:", d["cliente"], d["customer"])
    print("GAPs:", d["total_gaps"], "| soma horas:", d["soma_horas"])
    print("Baldes (h):", {k: round(v, 1) for k, v in b["soma"].items()})
    print("Baldes (qtd):", b["cont"])
    print("Contratadas (h):", d["total_contratadas"], "| módulos:", len(d["contratadas"]))
    print("Conflitos:", len(d["conflitos"]), "| Alto:",
          sum(1 for c in d["conflitos"] if c["grau"] == "Alto"))
