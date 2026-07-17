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
| `svc_comercial.v_gaps` (view) | Lê os GAPs ao vivo de `cockpit.tickets`, **recortada pelos clientes liberados** ao usuário logado. Expõe `customer`; o painel filtra `000348D0`. Só `authenticated`. |
| `svc_comercial.set_decisao(...)` (função `security definer`) | Grava/atualiza/remove a decisão na **`cockpit.decisoes`** real. Exige sessão + cliente liberado. |
| `svc_comercial.me()` | Devolve `email`, `nome`, `is_admin` e os `clientes` liberados do usuário logado. |

Nenhum segredo vai para o repositório — só a chave publishable. Credenciais do
Tasks SC/Gmail continuam apenas nas Edge Functions do Supabase.

## Controle de acesso (login + filtro por cliente)

Conceito da skill `controle-acesso-por-cliente`, adaptado a site estático:
identidade no **Supabase Auth**, allowlist e perfil no **`cockpit.usuarios_login`**,
liberação em **`cockpit.usuario_clientes`** — as mesmas tabelas do Cockpit Único.

**Regras (modo estrito):**

- `is_admin = true` → enxerga todos os clientes.
- Usuário comum → só os `customer` listados em `cockpit.usuario_clientes`.
- Sem sessão, fora da allowlist, `ativo = false` ou sem nenhum cliente liberado → **não vê nada** (nem entra).
- `anon` não tem `USAGE` no schema `svc_comercial`: sem login, nem a URL nem a chave publishable trazem dado algum.

O recorte é no **banco** (view + RLS + funções `security definer` que checam
`svc_comercial.pode_ver(customer)`), não no front — mexer no JS não fura a liberação.
O `p_by` das gravações foi removido do front: a auditoria usa o e-mail do JWT.

### Administração (SQL, via MCP/SQL Editor)

```sql
-- 1) criar/liberar um usuário na allowlist
insert into cockpit.usuarios_login (email, nome, ativo, is_admin)
values ('nome.sobrenome@totvs.com.br', 'Nome Sobrenome', true, false)
on conflict (email) do update set ativo = true;

-- 2) liberar clientes para ele
insert into cockpit.usuario_clientes (email, customer)
values ('nome.sobrenome@totvs.com.br', '000348D0')
on conflict do nothing;

-- 3) criar o usuário no Supabase Auth (Dashboard → Authentication → Add user,
--    marcando "Auto Confirm User"), ou via SQL com auth.users + auth.identities.

-- tirar o acesso a um cliente
delete from cockpit.usuario_clientes where email = '...' and customer = '000348D0';

-- inativar de vez (some de todos os painéis do ecossistema)
update cockpit.usuarios_login set ativo = false where email = '...';
```

Trocar senha: Authentication → o usuário → Reset password / Update password.

**Senha provisória** dos 4 usuários criados agora (cassio, diego, juciane, percio):
`Tsc@2026-trocar` — trocar no primeiro acesso.

> ⚠️ **Limitação conhecida:** `cockpit.tickets` ainda tem a policy `anon_read_tickets USING (true)`,
> herdada dos outros dashboards do ecossistema (DashboardIndex lê como `anon`). Ou seja: este painel
> está fechado, mas quem tiver a chave publishable ainda consegue ler `cockpit.tickets` **direto**.
> Fechar isso exige migrar os demais dashboards para `authenticated` — tarefa separada.

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

O backend já é multi-cliente: `v_gaps` expõe `customer` e devolve todos os clientes
liberados ao usuário; as funções recebem `p_customer`. O que ainda prende o painel na
DÍGITRO é o front — a constante `CUSTOMER = '000348D0'` no `index.html` e a curadoria
estática (`CONFLITOS`, `NLM_NOTAS`, totais da proposta), que é da DÍGITRO. Próximo passo:
seletor de cliente alimentado por `svc_comercial.me().clientes` + curadoria por cliente.

## De-para dos baldes de horas (editável)

Calculado no `index.html` (`baseBucket`), adaptado ao schema `cockpit`:

- **Saindo/Cancelado** — `status_tasks = 'Cancelado'` (ou decisão *Recusar*).
- **Aprovado** — `etapa_gap ∈ {Aprovado, Desenvolvimento, Homologacao, Go-Live}` ou `status_tasks ∈ {Em Andamento, Resolvido, Validacao Cliente}` (ou decisão *Aprovar/2ª Fase/Contorno*).
- **Estimado não aprovado** — `time_estimate > 0` que não caiu acima (Backlog/Levantamento/Orçamento).
- **Estimado (universo)** — todos com `time_estimate > 0`.

## Segurança / limpeza

Leitura e gravação exigem **login** e **cliente liberado** (ver *Controle de acesso* acima).
`anon` não tem acesso a nada dentro de `svc_comercial`.

Deployment Protection da Vercel deixa de ser obrigatória (o painel se protege sozinho),
mas continua útil como camada extra em previews.

Para reverter tudo: `drop schema svc_comercial cascade;` (não afeta `cockpit`).
As tabelas de acesso (`cockpit.usuarios_login`, `cockpit.usuario_clientes`) são
**compartilhadas** com o Cockpit Único — não apague.
