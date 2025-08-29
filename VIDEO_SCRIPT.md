# VIDEO_SCRIPT.md — Roteiro Sugerido (3–5 min)

## 1) Introdução (30s)
Olá, sou <seu nome>. Este vídeo apresenta minha solução para o case da AutoU: uma aplicação web que lê emails, classifica em Produtivo/Improdutivo e sugere respostas automáticas.

## 2) Demonstração (3 min)
- Abrir a aplicação (UI).
- Colar o conteúdo de `email_status.txt` e clicar em Processar → mostrar “Produtivo (Status)”, resposta sugerida e botão de copiar.
- Repetir com `email_feliz_natal.txt` → mostrar “Improdutivo” e a resposta curta.
- Fazer upload de um `.pdf` demonstrativo para validar a leitura de PDF.
- (Se configurado) alternar “Usar IA da nuvem” e comparar com o modo Regras, explicando diferenças.

## 3) Explicação Técnica (1 min)
- Backend: FastAPI, rota `/api/classify`; leitura `.txt/.pdf`; pré-processamento leve; regras por escore.
- (Opcional) Hugging Face Inference: zero-shot (`facebook/bart-large-mnli`) e geração (`mistralai/Mistral-7B-Instruct`).
- Frontend: HTML + Tailwind; arrastar/soltar ou colar texto; resultados com *badge* e cópia rápida.
- Decisões: manter um **fallback offline** para funcionar sem chaves; permitir upgrade simples com API.

## 4) Conclusão (30s)
- Recapitular: classificação + resposta automática + deploy facilitado (Render/Docker).
- Próximos passos: treinar modelo supervisionado, dashboard, feedback loop, LGPD.
