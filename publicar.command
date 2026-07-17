#!/bin/bash
# Commita as alterações locais e envia para o GitHub (regeswerlang-oss/PlanoGapseProjeto).
# Deploy na Vercel acontece automaticamente a cada push, se o projeto já estiver importado lá.
set -e
cd "$(dirname "$0")"

echo "==> Repositório: $(pwd)"

# Sanidade: se o .git estiver corrompido, re-clona os metadados sem tocar nos arquivos.
if ! git rev-parse HEAD >/dev/null 2>&1; then
  echo "==> .git inconsistente — recuperando metadados do remoto..."
  TMP="$(mktemp -d)"
  git clone --no-checkout https://github.com/regeswerlang-oss/PlanoGapseProjeto.git "$TMP/r"
  rm -rf .git
  mv "$TMP/r/.git" .git
  rm -rf "$TMP"
  git reset >/dev/null
fi

git add -A
git status --short

if git diff --cached --quiet; then
  echo "==> Nada novo para commitar."
else
  git commit -m "Renomeia aba Conflitos RFP x GAP para RFP x GAP"
fi

echo "==> Enviando para o GitHub..."
git push origin main

echo
echo "==> Pronto. Commit no ar em:"
echo "    https://github.com/regeswerlang-oss/PlanoGapseProjeto"
echo
echo "Se o projeto ainda NÃO estiver na Vercel:"
echo "  vercel.com -> Add New -> Project -> importar PlanoGapseProjeto"
echo "  Framework Preset: Other | Root Directory: vercel-online | Deploy"
