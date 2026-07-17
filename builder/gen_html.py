#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o HTML unico do painel Servico x Comercial a partir de build_servico_comercial.build()."""
import json, os
from build_servico_comercial import build, OUT_TMP, OUT_PROJ

CHARTJS = ('<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.0/dist/chart.umd.js" '
           'integrity="sha384-iU8HYtnGQ8Cy4zl7gbNMOhsDTTKX02BTXptVP/vqAWIaTfM7isw76iyZCsjL2eVi" '
           'crossorigin="anonymous"></script>')

TEMPLATE = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Serviço × Comercial — __CLIENTE__</title>
__CHARTJS__
<style>
:root{
  color-scheme: light;
  --navy:#0C2340; --roxo:#6F5BFF; --lilas:#E8E5FF; --cinza:#F4F4F8;
  --gray:#6A6A7B; --gray-light:#9A9AAC; --ink:#2A2A35;
  --approve:#1E9E6A; --phase2:#E8A33D; --workaround:#0099B5; --refuse:#D64550; --pending:#B9B9C8;
  --grad:linear-gradient(135deg,#6F5BFF 0%,#0C2340 100%);
  --font:-apple-system,"Segoe UI",Arial,sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{font-family:var(--font);background:#F4F6F8;color:var(--navy);line-height:1.5;min-height:100vh}
button{font-family:inherit;cursor:pointer}
a{color:var(--roxo)}

/* TOPBAR */
.topbar{position:sticky;top:0;z-index:100;background:var(--navy);color:#fff;border-bottom:3px solid;border-image:var(--grad) 1;box-shadow:0 4px 18px rgba(12,35,64,.18)}
.topbar-inner{max-width:1600px;margin:0 auto;padding:12px 24px;display:flex;align-items:center;gap:20px;flex-wrap:wrap}
.tb-brand{display:flex;align-items:center;gap:12px}
.tb-logo{width:36px;height:36px;border-radius:8px;background:var(--grad);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:11px;color:#fff}
.tb-titles .t1{font-size:11px;letter-spacing:1.3px;text-transform:uppercase;color:var(--roxo);font-weight:700}
.tb-titles .t2{font-size:15px;font-weight:600;margin-top:1px}
.tb-titles .t3{font-size:11px;color:var(--gray-light);margin-top:1px}
.tb-kpis{display:flex;gap:8px;flex:1;justify-content:flex-end;flex-wrap:wrap}
.kpi-pill{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.10);border-radius:10px;padding:7px 13px;display:flex;flex-direction:column;gap:1px;min-width:104px}
.kpi-pill .lbl{font-size:9px;letter-spacing:.6px;text-transform:uppercase;color:var(--gray-light);font-weight:700}
.kpi-pill .val{font-size:18px;font-weight:800;color:#fff;line-height:1}
.kpi-pill .val .u{font-size:9px;color:var(--gray-light);font-weight:500;margin-left:2px}
.kpi-pill .pct{font-size:9.5px;color:var(--gray-light);margin-top:1px}
.kpi-pill.aprovado .val{color:#46D69E} .kpi-pill.naoaprovado .val{color:#FFC368}
.kpi-pill.saindo .val{color:#FF7A88} .kpi-pill.estimado .val{color:#E6E6F0}
.kpi-pill.contratadas .val{color:#5BD3FF}

/* TABS */
.tabs{max-width:1600px;margin:16px auto 0;padding:0 24px;display:flex;gap:6px;flex-wrap:wrap}
.tab{padding:10px 16px;border:1px solid #DCE3E8;border-bottom:none;border-radius:10px 10px 0 0;background:#fff;font-size:13px;font-weight:600;color:var(--gray)}
.tab.active{color:var(--navy);border-color:var(--roxo);box-shadow:0 -2px 0 var(--roxo) inset}
.tab .b{margin-left:7px;background:var(--lilas);color:#6F2BC9;border-radius:8px;padding:1px 7px;font-size:10px;font-weight:800}

.container{max-width:1600px;margin:0 auto;padding:18px 24px 120px}
.panel{display:none} .panel.active{display:block;animation:fade .2s}
@keyframes fade{from{opacity:.3}to{opacity:1}}
.note{font-size:12px;color:var(--gray);margin:2px 0 14px}

.grid2{display:grid;grid-template-columns:1.1fr .9fr;gap:16px}
@media(max-width:980px){.grid2{grid-template-columns:1fr}}
.card{background:#fff;border-radius:14px;box-shadow:0 1px 4px rgba(12,35,64,.06);padding:18px 20px;margin-bottom:16px}
.card h3{font-size:14px;font-weight:800;color:var(--navy);margin-bottom:3px;display:flex;align-items:center;gap:8px}
.card h3 .num{width:22px;height:22px;border-radius:6px;background:var(--grad);color:#fff;font-size:11px;font-weight:800;display:inline-flex;align-items:center;justify-content:center}
.card .sub{font-size:11.5px;color:var(--gray);margin-bottom:12px}
.chart-box{position:relative;height:260px}
.chart-box.tall{height:340px}

/* hero risco */
.hero{background:var(--grad);color:#fff;border-radius:14px;padding:20px 22px;margin-bottom:16px;display:grid;grid-template-columns:1fr auto;gap:18px;align-items:center}
.hero .big{font-size:30px;font-weight:800;line-height:1}
.hero .big .u{font-size:13px;opacity:.8}
.hero .lbl{font-size:11px;letter-spacing:.6px;text-transform:uppercase;opacity:.85;font-weight:700;margin-top:2px}
.hero .desc{font-size:12.5px;opacity:.92;max-width:560px;margin-top:8px}
.hero-stats{display:flex;gap:20px;text-align:right}

/* funil */
.funnel{display:flex;flex-direction:column;gap:8px}
.fbar{display:grid;grid-template-columns:160px 1fr 86px;align-items:center;gap:10px}
.fbar .fn{font-size:12px;font-weight:700;color:var(--navy)}
.fbar .ft{height:24px;border-radius:6px;background:#EDF1F4;overflow:hidden}
.fbar .ft span{display:block;height:100%;border-radius:6px}
.fbar .fv{font-size:12.5px;font-weight:800;text-align:right}
.f-estimado span{background:#9AA3B5} .f-aprovado span{background:var(--approve)}
.f-naoaprovado span{background:var(--phase2)} .f-saindo span{background:var(--refuse)}

/* tabela conflitos */
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{background:var(--navy);color:#fff;text-align:left;padding:9px 11px;font-size:11px;letter-spacing:.4px;text-transform:uppercase;position:sticky;top:0}
td{padding:9px 11px;border-bottom:1px solid #EDF1F4;vertical-align:top}
tr:nth-child(even) td{background:#F8F9FC}
tr.alto td{background:#FCEDEF}
tr.alto:hover td,tr:hover td{background:#FFF7E6}
.code{font-family:'SF Mono',Monaco,Consolas,monospace;font-size:11px;background:var(--navy);color:#fff;padding:2px 6px;border-radius:5px;font-weight:600;display:inline-block;margin:1px 2px 1px 0}
.grau{font-size:10px;font-weight:800;padding:2px 8px;border-radius:7px;white-space:nowrap}
.grau.Alto{background:#FAD4D8;color:#B0212E} .grau.Médio{background:#FCEBCF;color:#8A5A00}
.grau.MédioAlto{background:#F3DCC9;color:#9A3A12}
.nlmtag{font-size:10px;background:#E2F5EC;color:var(--approve);padding:2px 8px;border-radius:7px;font-weight:700;cursor:pointer;border:1px solid #BFE8D2}
.nlmtag:hover{background:#CFEEDD}
.nlmrow td{background:#F2FBF6 !important;border-left:3px solid var(--approve);font-size:12px;color:#1c5e42}

/* NotebookLM cards */
.nlm-card{background:#fff;border-radius:12px;border-left:4px solid var(--approve);box-shadow:0 1px 4px rgba(12,35,64,.06);padding:15px 18px;margin-bottom:12px}
.nlm-card h4{font-size:13.5px;color:var(--navy);margin-bottom:4px}
.nlm-card .ids{margin-bottom:8px}
.nlm-card p{font-size:12.5px;color:var(--ink)}
.nlm-src{font-size:11px;color:var(--gray);margin:0 0 14px;padding:9px 13px;background:#E2F5EC;border-radius:9px}

/* decisao */
.dec-controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:14px}
.dec-controls select,.dec-controls input{padding:9px 12px;border:1px solid #DCE3E8;border-radius:9px;font-family:var(--font);font-size:12.5px;background:#fff;color:var(--navy)}
.dec-controls input{flex:1;min-width:200px}
.btn-ghost{padding:9px 13px;background:#fff;border:1px solid #DCE3E8;border-radius:9px;font-size:12px;font-weight:600;color:var(--gray)}
.btn-ghost:hover{border-color:var(--navy);color:var(--navy)}
.task{background:#fff;border:1px solid #EDF1F4;border-radius:10px;padding:13px 15px;border-left:4px solid #DCE3E8;margin-bottom:9px;transition:all .15s}
.task.d-approve{border-left-color:var(--approve);background:linear-gradient(90deg,#F0FAF5,#fff 55%)}
.task.d-phase2{border-left-color:var(--phase2);background:linear-gradient(90deg,#FFF7EC,#fff 55%)}
.task.d-workaround{border-left-color:var(--workaround);background:linear-gradient(90deg,#E8F7FB,#fff 55%)}
.task.d-refuse{border-left-color:var(--refuse);background:linear-gradient(90deg,#FCEDEF,#fff 55%);opacity:.95}
.task.hidden{display:none}
.task-top{display:grid;grid-template-columns:1fr auto;gap:13px;align-items:start}
.task-id-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:5px}
.task-title{font-size:13.5px;font-weight:700;color:var(--navy)}
.task-meta{display:flex;gap:5px;flex-wrap:wrap;margin-top:6px}
.tag-mini{font-size:10px;background:#EDF1F4;color:var(--gray);padding:2px 7px;border-radius:5px;font-weight:600}
.tag-mini.modulo{background:#F0E5FF;color:#6F2BC9}
.tag-mini.alto{background:#FAD4D8;color:#B0212E}
.tag-mini.medio{background:#FCEBCF;color:#8A5A00}
.task-hours{text-align:right;min-width:60px}
.task-hours .h{font-size:17px;font-weight:800;color:var(--navy);line-height:1}
.task-hours .h .u{font-size:10px;color:var(--gray);font-weight:500}
.task-hours .l{font-size:9px;color:var(--gray);text-transform:uppercase;letter-spacing:.4px;font-weight:600;margin-top:2px}
.task-actions{display:flex;gap:7px;margin-top:11px;flex-wrap:wrap}
.btn-decide{padding:7px 12px;border:1.5px solid;border-radius:8px;font-size:12px;font-weight:700;background:#fff;transition:all .12s}
.btn-approve{border-color:var(--approve);color:var(--approve)} .btn-approve.active{background:var(--approve);color:#fff}
.btn-phase2{border-color:var(--phase2);color:var(--phase2)} .btn-phase2.active{background:var(--phase2);color:#fff}
.btn-workaround{border-color:var(--workaround);color:var(--workaround)} .btn-workaround.active{background:var(--workaround);color:#fff}
.btn-refuse{border-color:var(--refuse);color:var(--refuse)} .btn-refuse.active{background:var(--refuse);color:#fff}
.empty{padding:26px;text-align:center;color:var(--gray);font-size:13px}
.footer{max-width:1600px;margin:0 auto;padding:18px 24px 30px;color:var(--gray-light);font-size:11px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
.footer b{color:var(--navy)}
</style>
</head>
<body>
<div class="topbar">
  <div class="topbar-inner">
    <div class="tb-brand">
      <div class="tb-logo">TOTVS</div>
      <div class="tb-titles">
        <div class="t1">TOTVS · Santa Catarina</div>
        <div class="t2">Serviço × Comercial — __CLIENTE__</div>
        <div class="t3">Cliente __CUSTOMER__ · GAPs de __FONTE_EM__ · painel gerado em __GERADO_EM__</div>
      </div>
    </div>
    <div class="tb-kpis" id="kpis"></div>
  </div>
</div>

<div class="tabs" id="tabs">
  <button class="tab active" data-p="geral">Visão geral</button>
  <button class="tab" data-p="conflitos">RFP × GAP <span class="b" id="bconf">0</span></button>
  <button class="tab" data-p="nlm">NotebookLM</button>
  <button class="tab" data-p="declinados">Declinados <span class="b" id="bdecl">0</span></button>
  <button class="tab" data-p="decisao">Tomada de decisão <span class="b" id="bdec">0</span></button>
</div>

<div class="container">
  <!-- GERAL -->
  <div class="panel active" id="p-geral">
    <div class="hero">
      <div>
        <div class="lbl">Risco comercial — horas estimadas ainda não aprovadas</div>
        <div class="big" id="heroH">— <span class="u">h</span></div>
        <div class="desc">Funcionalidades vendidas na RFP como “atende nativo” que internamente estão orçadas como desenvolvimento (GAP). Enquanto não há decisão formal, todo o esforço fica em aberto entre Serviço e Comercial.</div>
      </div>
      <div class="hero-stats">
        <div><div class="big" id="heroConf">8</div><div class="lbl">conflitos Alto</div></div>
        <div><div class="big" id="heroPers">1.006<span class="u">h</span></div><div class="lbl">personalizações<br>(R$ 221.320)</div></div>
      </div>
    </div>
    <div class="grid2">
      <div class="card">
        <h3><span class="num">1</span> Funil de horas — Serviço × Comercial</h3>
        <div class="sub">De-para: Estimado (universo) → Aprovado como GAP · Estimado não aprovado · Saindo/Cancelado. Atualiza com as decisões.</div>
        <div class="funnel" id="funnel"></div>
      </div>
      <div class="card">
        <h3><span class="num">2</span> GAPs por módulo (horas estimadas)</h3>
        <div class="sub">Onde está concentrado o esforço de desenvolvimento.</div>
        <div class="chart-box"><canvas id="chMod"></canvas></div>
      </div>
    </div>
    <div class="card">
      <h3><span class="num">3</span> Horas contratadas (baseline comercial) por módulo</h3>
      <div class="sub">Escopo de serviço já vendido (subitens da proposta) — referência para dimensionar o peso dos GAPs.</div>
      <div class="chart-box tall"><canvas id="chContr"></canvas></div>
    </div>
  </div>

  <!-- CONFLITOS -->
  <div class="panel" id="p-conflitos">
    <p class="note">Requisitos respondidos na RFP como “Atende = Sim / Escopo” que internamente viraram GAP. Clique em <b>NotebookLM</b> para ver o que foi tratado comercialmente. Linhas vermelhas = grau Alto (revisão imediata).</p>
    <div class="card" style="padding:0;overflow:hidden">
      <table id="tConf"><thead><tr>
        <th>GAP(s)</th><th>Funcionalidade</th><th>Módulo</th><th>Resp. RFP</th><th>Observação RFP</th><th>Grau</th><th>NLM</th>
      </tr></thead><tbody></tbody></table>
    </div>
  </div>

  <!-- NLM -->
  <div class="panel" id="p-nlm">
    <p class="nlm-src">Fonte: NotebookLM “Projeto Digitro” — 58 fontes indexadas (RFP, proposta, atas de reunião, conferência de GAPs). Resumos consolidados por grupo de conflito; no fluxo real são gravados como histórico no ticket com prefixo <b>NOTEBOOKLM:</b>.</p>
    <div id="nlmCards"></div>
  </div>

  <!-- DECLINADOS -->
  <div class="panel" id="p-declinados">
    <p class="note">Itens que o cliente declinou (decisão “Recusar” no painel). Hoje começa vazio — marque itens na aba <b>Tomada de decisão</b> e eles caem aqui e no balde “Saindo/Cancelado”.</p>
    <div id="declList"></div>
  </div>

  <!-- DECISAO -->
  <div class="panel" id="p-decisao">
    <p class="note">Sente com o stakeholder e decida item a item. As decisões ficam salvas <b>localmente</b> (neste navegador) e recalculam os KPIs — nada é gravado no Tasks SC até promover.</p>
    <div class="dec-controls">
      <select id="decGroup">
        <option value="modulo">Agrupar: Módulo</option>
        <option value="bucket">Agrupar: Balde de horas</option>
        <option value="grau">Agrupar: Grau de conflito</option>
        <option value="none">Sem agrupamento</option>
      </select>
      <select id="decFilter">
        <option value="all">Todos</option>
        <option value="conf">Só em conflito RFP</option>
        <option value="est">Só com estimativa (&gt;0h)</option>
        <option value="pend">Só pendentes de decisão</option>
      </select>
      <input id="decSearch" placeholder="Buscar por id, título, módulo, tag…">
      <button class="btn-ghost" id="btnReset">Limpar decisões</button>
      <button class="btn-ghost" id="btnExport">Exportar CSV</button>
    </div>
    <div id="decList"></div>
  </div>
</div>

<div class="footer">
  <div>Protótipo <b>Serviço × Comercial</b> · combina dashboard-tomada-decisao + dashboard-tags-gaps + analise-doc-estimativa-gap + NotebookLM.</div>
  <div><b>totvs.com</b> · fonte offline (gaps_digitro.json) — pronto para plugar a API Tasks SC.</div>
</div>

<script>
const DATA = __DATA__;
const DEC = {approve:'Aprovar',phase2:'2ª Fase',workaround:'Contorno',refuse:'Recusar'};
const LS_KEY = 'svc_com_decisoes_' + (DATA.customer||'x');
let decisions = {};
try{ decisions = JSON.parse(localStorage.getItem(LS_KEY)||'{}'); }catch(e){ decisions={}; }
const fmt = n => (Math.round(n*10)/10).toLocaleString('pt-BR');

// ----- efetiva o balde considerando a decisão tomada -----
function effBucket(g){
  const d = decisions[g.id] && decisions[g.id].decision;
  if(d==='refuse') return 'saindo';
  if(d==='approve') return 'aprovado';
  if(d==='phase2'||d==='workaround') return 'aprovado'; // entram como compromisso
  return g.bucket;
}
function computeBuckets(){
  const soma={estimado:0,aprovado:0,naoaprovado:0,saindo:0};
  const cont={estimado:0,aprovado:0,naoaprovado:0,saindo:0};
  DATA.gaps.forEach(g=>{
    const e=+g.est||0;
    if(e>0){soma.estimado+=e;cont.estimado++;}
    const b=effBucket(g);
    if(b in soma && b!=='estimado'){ soma[b]+=e; if(e>0||b==='saindo')cont[b]++; }
  });
  return {soma,cont};
}

// ----- KPIs -----
function renderKpis(){
  const {soma}=computeBuckets();
  const tot=soma.estimado||1;
  const pills=[
    ['estimado','Estimado',soma.estimado,DATA.buckets.cont.estimado,'h'],
    ['aprovado','Aprovado GAP',soma.aprovado,null,'h'],
    ['naoaprovado','Não aprovado',soma.naoaprovado,null,'h'],
    ['saindo','Saindo/Cancel.',soma.saindo,null,'h'],
    ['contratadas','Contratadas',DATA.total_contratadas,Object.keys(DATA.contratadas).length,'h'],
  ];
  document.getElementById('kpis').innerHTML = pills.map(([c,l,v,n,u])=>{
    const pct = c==='contratadas' ? '' : `<div class="pct">${fmt(v/tot*100)}% do estimado</div>`;
    const sub = n!=null ? `<div class="pct">${n} ${c==='contratadas'?'módulos':'itens'}</div>` : pct;
    return `<div class="kpi-pill ${c}"><div class="lbl">${l}</div><div class="val">${fmt(v)}<span class="u">${u}</span></div>${sub}</div>`;
  }).join('');
  document.getElementById('heroH').innerHTML = fmt(soma.naoaprovado)+' <span class="u">h</span>';
  // funil
  const fb=[['estimado','Estimado (universo)',soma.estimado],['aprovado','Aprovado como GAP',soma.aprovado],
    ['naoaprovado','Estimado, não aprovado',soma.naoaprovado],['saindo','Saindo / Cancelado',soma.saindo]];
  document.getElementById('funnel').innerHTML = fb.map(([k,l,v])=>
    `<div class="fbar"><div class="fn">${l}</div><div class="ft f-${k}"><span style="width:${Math.max(2,v/tot*100)}%"></span></div><div class="fv">${fmt(v)} h</div></div>`).join('');
}

// ----- charts -----
let chMod,chContr;
function renderCharts(){
  const byMod={};
  DATA.gaps.forEach(g=>{ const e=+g.est||0; if(e>0){ byMod[g.modulo]=(byMod[g.modulo]||0)+e; }});
  const me=Object.entries(byMod).sort((a,b)=>b[1]-a[1]);
  const ce=Object.entries(DATA.contratadas).sort((a,b)=>b[1]-a[1]);
  const opt=(horiz)=>({responsive:true,maintainAspectRatio:false,indexAxis:horiz?'y':'x',
    plugins:{legend:{display:false}},scales:{x:{grid:{display:!horiz}},y:{grid:{display:horiz}}}});
  if(chMod)chMod.destroy();
  chMod=new Chart(document.getElementById('chMod'),{type:'bar',
    data:{labels:me.map(x=>x[0]),datasets:[{data:me.map(x=>x[1]),backgroundColor:'#6F5BFF',borderRadius:5}]},options:opt(true)});
  if(chContr)chContr.destroy();
  chContr=new Chart(document.getElementById('chContr'),{type:'bar',
    data:{labels:ce.map(x=>x[0]),datasets:[{data:ce.map(x=>x[1]),backgroundColor:'#0C2340',borderRadius:5}]},options:opt(false)});
}

// ----- conflitos -----
function renderConflitos(){
  const tb=document.querySelector('#tConf tbody');
  document.getElementById('bconf').textContent=DATA.conflitos.length;
  tb.innerHTML=DATA.conflitos.map((c,i)=>{
    const ids=c.ids.map(x=>`<span class="code">${x}</span>`).join('');
    const gcls=c.grau.replace('/','');
    const nlm=DATA.nlm_notas[c.grupo]?`<span class="nlmtag" data-i="${i}">＋ NLM</span>`:'—';
    return `<tr class="${c.grau==='Alto'?'alto':''}">
      <td>${ids}</td><td><b>${c.titulo}</b></td><td>${c.modulo}</td><td>${c.rfp}</td>
      <td>${c.obs}</td><td><span class="grau ${gcls}">${c.grau}</span></td><td>${nlm}</td></tr>`;
  }).join('');
  tb.querySelectorAll('.nlmtag').forEach(t=>t.onclick=()=>{
    const i=+t.dataset.i, c=DATA.conflitos[i], row=t.closest('tr');
    if(row.nextElementSibling&&row.nextElementSibling.classList.contains('nlmrow')){row.nextElementSibling.remove();return;}
    const tr=document.createElement('tr');tr.className='nlmrow';
    tr.innerHTML=`<td colspan="7"><b>NotebookLM · ${c.titulo}:</b> ${DATA.nlm_notas[c.grupo]}</td>`;
    row.after(tr);
  });
}

// ----- NotebookLM cards -----
function renderNlm(){
  const titles={etiquetas:'Etiquetas (código de barras, localização, ANATEL, rastreabilidade)',
    comissao:'Comissão — relatório, baixa com NF, multinível, metas',precificacao:'Política de precificação personalizada',
    envio_email:'Envio de documentos anexados por e-mail ao faturar',historico:'Registrar histórico por cliente'};
  const idsByGrupo={};
  DATA.conflitos.forEach(c=>{(idsByGrupo[c.grupo]=idsByGrupo[c.grupo]||[]).push(...c.ids);});
  document.getElementById('nlmCards').innerHTML=Object.keys(DATA.nlm_notas).map(g=>{
    const ids=(idsByGrupo[g]||[]).map(x=>`<span class="code">${x}</span>`).join('');
    return `<div class="nlm-card"><h4>${titles[g]||g}</h4><div class="ids">${ids}</div><p>${DATA.nlm_notas[g]}</p></div>`;
  }).join('');
}

// ----- decisão + declinados -----
function gapMeta(g){
  const grau=DATA.conf_ids[g.id];
  return {grau, conf:!!grau};
}
function taskHTML(g){
  const d=decisions[g.id]&&decisions[g.id].decision;
  const m=gapMeta(g);
  const dcls=d?('d-'+d):'';
  const e=+g.est||0;
  const graut=m.grau?`<span class="tag-mini ${m.grau==='Alto'?'alto':'medio'}">RFP: ${m.grau}</span>`:'';
  const btns=Object.entries(DEC).map(([k,l])=>
    `<button class="btn-decide btn-${k} ${d===k?'active':''}" data-id="${g.id}" data-d="${k}">${l}</button>`).join('');
  return `<div class="task ${dcls}" data-id="${g.id}">
    <div class="task-top"><div>
      <div class="task-id-row"><span class="code">${g.id}</span><span class="task-title">${g.title}</span></div>
      <div class="task-meta"><span class="tag-mini modulo">${g.modulo}</span>
        <span class="tag-mini">${g.status}</span>${graut}
        <span class="tag-mini">${g.necessidade||'—'}</span></div>
    </div><div class="task-hours"><div class="h">${e>0?fmt(e):'—'}<span class="u">h</span></div><div class="l">estim.</div></div></div>
    <div class="task-actions">${btns}</div></div>`;
}
function renderDec(){
  const grp=document.getElementById('decGroup').value;
  const flt=document.getElementById('decFilter').value;
  const q=document.getElementById('decSearch').value.trim().toLowerCase();
  let gaps=DATA.gaps.filter(g=>{
    if(flt==='conf'&&!DATA.conf_ids[g.id])return false;
    if(flt==='est'&&!(+g.est>0))return false;
    if(flt==='pend'&&decisions[g.id]&&decisions[g.id].decision)return false;
    if(q){const hay=(g.id+' '+g.title+' '+g.modulo+' '+(g.tags||[]).join(' ')).toLowerCase();if(!hay.includes(q))return false;}
    return true;
  });
  document.getElementById('bdec').textContent=gaps.length;
  const cont=document.getElementById('decList');
  if(!gaps.length){cont.innerHTML='<div class="empty">Nenhum item para os filtros atuais.</div>';return;}
  if(grp==='none'){cont.innerHTML=gaps.map(taskHTML).join('');}
  else{
    const keyf={modulo:g=>g.modulo,bucket:g=>({estimado:'Estimado',aprovado:'Aprovado GAP',naoaprovado:'Não aprovado',saindo:'Saindo/Cancelado',sem_est:'Sem estimativa'})[effBucket(g)],grau:g=>DATA.conf_ids[g.id]?('Conflito '+DATA.conf_ids[g.id]):'Sem conflito RFP'}[grp];
    const groups={};gaps.forEach(g=>{const k=keyf(g)||'—';(groups[k]=groups[k]||[]).push(g);});
    cont.innerHTML=Object.keys(groups).sort().map(k=>{
      const hrs=groups[k].reduce((s,g)=>s+(+g.est||0),0);
      return `<div class="card" style="padding:12px 15px"><h3 style="font-size:13px"><span class="num">${groups[k].length}</span> ${k} · ${fmt(hrs)} h</h3>${groups[k].map(taskHTML).join('')}</div>`;
    }).join('');
  }
  bindDecBtns();
}
function bindDecBtns(){
  document.querySelectorAll('.btn-decide').forEach(b=>b.onclick=()=>{
    const id=b.dataset.id,d=b.dataset.d;
    if(decisions[id]&&decisions[id].decision===d){delete decisions[id];}
    else{decisions[id]={decision:d,ts:new Date().toISOString()};}
    localStorage.setItem(LS_KEY,JSON.stringify(decisions));
    renderKpis();renderDec();renderDeclinados();
  });
}
function renderDeclinados(){
  const list=DATA.gaps.filter(g=>decisions[g.id]&&decisions[g.id].decision==='refuse');
  document.getElementById('bdecl').textContent=list.length;
  const c=document.getElementById('declList');
  if(!list.length){c.innerHTML='<div class="empty">Nenhum item declinado ainda. Marque “Recusar” na aba Tomada de decisão.</div>';return;}
  c.innerHTML=list.map(taskHTML).join('');
  c.querySelectorAll('.btn-decide').forEach(b=>b.onclick=()=>{
    const id=b.dataset.id,d=b.dataset.d;
    if(decisions[id]&&decisions[id].decision===d)delete decisions[id];else decisions[id]={decision:d,ts:new Date().toISOString()};
    localStorage.setItem(LS_KEY,JSON.stringify(decisions));renderKpis();renderDec();renderDeclinados();
  });
}

// ----- tabs -----
document.querySelectorAll('.tab').forEach(t=>t.onclick=()=>{
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(x=>x.classList.remove('active'));
  t.classList.add('active');
  document.getElementById('p-'+t.dataset.p).classList.add('active');
  if(t.dataset.p==='geral')renderCharts();
});
['decGroup','decFilter'].forEach(id=>document.getElementById(id).onchange=renderDec);
document.getElementById('decSearch').oninput=renderDec;
document.getElementById('btnReset').onclick=()=>{if(confirm('Limpar todas as decisões locais?')){decisions={};localStorage.removeItem(LS_KEY);renderKpis();renderDec();renderDeclinados();}};
document.getElementById('btnExport').onclick=()=>{
  const rows=[['id','titulo','modulo','horas','balde_base','decisao','ts']];
  DATA.gaps.forEach(g=>{const d=decisions[g.id]||{};rows.push([g.id,'"'+g.title.replace(/"/g,'""')+'"',g.modulo,g.est,g.bucket,d.decision||'',d.ts||'']);});
  const blob=new Blob([rows.map(r=>r.join(';')).join('\n')],{type:'text/csv;charset=utf-8'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='decisoes_servico_comercial_'+(DATA.customer||'')+'.csv';a.click();
};

// init
renderKpis();renderCharts();renderConflitos();renderNlm();renderDec();renderDeclinados();
</script>
</body>
</html>
"""

def gen():
    d = build()
    html = (TEMPLATE
            .replace("__CHARTJS__", CHARTJS)
            .replace("__CLIENTE__", str(d["cliente"]))
            .replace("__CUSTOMER__", str(d["customer"]))
            .replace("__FONTE_EM__", str(d["fonte_gaps_em"]))
            .replace("__GERADO_EM__", str(d["gerado_em"]))
            .replace("__DATA__", json.dumps(d, ensure_ascii=False)))
    name = "painel_servico_comercial_DIGITRO.html"
    for outdir in (OUT_TMP, OUT_PROJ):
        try:
            with open(os.path.join(outdir, name), "w", encoding="utf-8") as f:
                f.write(html)
            print("escrito:", os.path.join(outdir, name))
        except Exception as e:
            print("FALHA em", outdir, "->", e)
    return os.path.join(OUT_TMP, name)

if __name__ == "__main__":
    gen()
