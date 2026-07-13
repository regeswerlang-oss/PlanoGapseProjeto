# Painel Serviço × Comercial — DIGITRO (online)

Site **estático** (sem build) que roda na Vercel e lê os dados **ao vivo** do Supabase
compartilhado (`kpimalwnswxalwbidkog`). É a versão online do protótipo local
`painel_servico_comercial_DIGITRO.html`.

## O que tem

- **index.html** — o painel inteiro (HTML/CSS/JS + Chart.js + supabase-js via CDN).
- **vercel.json** — força site estático puro (`framework: null`, sem build).

## Como os dados chegam (sem backend próprio)

O front usa `@supabase/supabase-js` com a **chave publishable** (pública por design,
protegida por policies) e fala com um schema **isolado** provisionado só para este painel:

| Objeto | Papel |
|---|---|
| `svc_comercial.v_gaps` (view) | Lê os GAPs da DÍGITRO ao vivo de `cockpit.tickets` (customer `000348D0`) já com a decisão atual. Leitura liberada para `anon`. |
| `svc_comercial.set_decisao(...)` (função `security definer`) | Grava/atualiza/remove a decisão na **`cockpit.decisoes`** real. Restrita ao cliente DÍGITRO. |

Nenhum segredo vai para o repositório — só a chave publishable. Credenciais do
Tasks SC/Gmail continuam apenas nas Edge Functions do Supabase.

## Deploy na Vercel (1 vez)

1. **Crie o repositório** com esta pasta (`vercel-online/`) como raiz. Ex.:
   ```bash
   cd "vercel-online"
   git init && git add . && git commit -m "Painel Serviço x Comercial DIGITRO (online)"
   git branch -M main
   git remote add origin https://github.com/<sua-conta>/painel-servico-comercial.git
   git push -u origin main
   ```
   (Ou adicione estes arquivos ao repo `regeswerlang-oss/DashboardIndex` e ligue um card no `index.html` do hub.)
2. **Vercel** → Add New → Project → importe o repositório → Framework Preset **Other** → Root `./` → **Deploy**.
3. **Proteção (recomendado)** → Settings → Deployment Protection → Vercel Authentication.

Deploy automático a cada `git push`.

## Trocar de cliente

Hoje o painel é fixo na DÍGITRO (`000348D0`), definido na view `svc_comercial.v_gaps`
e na função `set_decisao`. Para outro cliente: parametrizar por querystring
(`?customer=XXXX`) e trocar a view por uma função `list_gaps(customer)` — próximo passo.

## De-para dos baldes de horas (editável)

Calculado no `index.html` (`baseBucket`), adaptado ao schema `cockpit`:

- **Saindo/Cancelado** — `status_tasks = 'Cancelado'` (ou decisão *Recusar*).
- **Aprovado** — `etapa_gap ∈ {Aprovado, Desenvolvimento, Homologacao, Go-Live}` ou `status_tasks ∈ {Em Andamento, Resolvido, Validacao Cliente}` (ou decisão *Aprovar/2ª Fase/Contorno*).
- **Estimado não aprovado** — `time_estimate > 0` que não caiu acima (Backlog/Levantamento/Orçamento).
- **Estimado (universo)** — todos com `time_estimate > 0`.

## Segurança / limpeza

Protótipo com **leitura pública** da DÍGITRO e **gravação pública** de decisão
(via função restrita ao cliente). Para produção: exigir login Supabase e trocar as
policies `anon` por `authenticated` + RLS por cliente (skill `controle-acesso-por-cliente`).
Para reverter tudo: `drop schema svc_comercial cascade;` (não afeta `cockpit`).
