# Plano de GAPs e Projeto — Painel Serviço × Comercial

Painel que une, numa tela só, a leitura de **Serviço** (GAPs do Tasks SC) com a de
**Comercial** (RFP, proposta, itens declinados) para o cliente **DÍGITRO (000348D0)**.

## Estrutura

```
.
├── vercel-online/          ← publicado na Vercel (site estático, dados ao vivo do Supabase)
│   ├── index.html          painel online completo
│   ├── vercel.json         site estático, sem build
│   └── README.md           deploy + de-para dos baldes de horas
├── builder/                gerador da versão offline
│   ├── build_servico_comercial.py   consolida as fontes e calcula os 4 baldes
│   └── gen_html.py                  gera o HTML único
└── painel_servico_comercial_DIGITRO.html   versão offline (dados embutidos)
```

## O que o painel mostra

- **4 baldes de horas** — Estimado (universo) · Aprovado como GAP · Estimado não aprovado · Saindo/Cancelado.
- **Conflitos RFP × GAP** — 23 itens, 8 de grau **Alto** (vendidos como “atende nativo”, orçados como desenvolvimento).
- **NotebookLM** — notas comerciais por grupo de conflito (58 fontes indexadas).
- **Decisões por tag** — conceito `dashboard-tags-gaps`: horas por dimensão de tag empilhadas por decisão.
- **Tomada de decisão** — Aprovar / 2ª Fase / Contorno / Recusar por item.

## Duas versões

| Versão | Dados | Decisões |
|---|---|---|
| `painel_servico_comercial_DIGITRO.html` (offline) | embutidos (snapshot dos 64 GAPs) | `localStorage` |
| `vercel-online/index.html` (online) | ao vivo do Supabase (`svc_comercial.v_gaps`, 131 GAPs) | gravadas em `cockpit.decisoes` |

## Deploy

O deploy da Vercel aponta para a pasta **`vercel-online`** (Root Directory).
Passo a passo em [`vercel-online/README.md`](vercel-online/README.md).

## Backend (Supabase compartilhado `kpimalwnswxalwbidkog`)

Schema isolado `svc_comercial` — não altera o schema `cockpit`:

- `svc_comercial.v_gaps` — view de leitura dos GAPs da DÍGITRO (de `cockpit.tickets`).
- `svc_comercial.set_decisao(...)` — função `security definer` que grava em `cockpit.decisoes`, restrita ao cliente `000348D0`.
- `svc_comercial.pgrupos` — grupos de personalização (de-para proposta × GAPs) com a **Est. Proposta** editável; `prop_seed` guarda o de-para original para o botão *Reset*.
- `svc_comercial.set_pgrupo(...)` / `reset_pgrupos(...)` — gravam os grupos e **sincronizam** o `horas_contratadas` dos cancelamentos de personalização, para o *Acerto de contas* refletir a edição.
- `svc_comercial.cancelamentos` / `acerto_gaps` + `set_cancelamento(...)` / `set_acerto_gap(...)` — o acerto de contas.

Só a **chave publishable** (pública por design) vai no front. Nenhum segredo no repositório.
