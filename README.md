# AutoU Email Assistant — Classificação & Resposta Automática

Solução simples (FastAPI + HTML) para **classificar emails** em *Produtivo* ou *Improdutivo* e **sugerir respostas automáticas**.  
Funciona **100% local** com um **classificador por regras** e pode ficar mais inteligente ao **conectar a API do Hugging Face Inference** (opcional).

> 🇧🇷 **Linguagem:** Interface PT-BR, regras PT/EN.  
> ⚙️ **Stack:** FastAPI, Vanilla HTML+JS (Tailwind), SQLite, opcional Hugging Face Inference API.  
> ☁️ **Deploy sugerido:** Render (free).

---

## 🚀 Como rodar localmente

1. **Pré-requisitos**
   - Python 3.10+
   - (Opcional) Chave da Hugging Face Inference API em `HUGGINGFACE_API_KEY` para melhorar a classificação e geração de respostas.

2. **Instalação**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **(Opcional) Configurar variáveis**
   ```bash
   cp .env.example .env
   # edite o arquivo e preencha HUGGINGFACE_API_KEY se quiser usar a IA hospedada
   ```

4. **Executar**
   ```bash
   uvicorn backend.main:app --reload
   ```

5. **Usar**
   - Abra: http://127.0.0.1:8000  
   - Cole texto ou envie `.txt/.pdf`. Veja a **categoria** e a **resposta sugerida**, com botão para copiar.

6. **Resposta**
   - Resposta compativel com markdown.

---

## 🧠 Como funciona

- **Pré-processamento NLP** leve (normalização, remoção de stopwords PT/EN).
- **Classificador por Regras** (sempre disponível):  
  Pontua termos e padrões típicos de:
  - *Produtivo*: "status", "protocolo", "erro", "suporte", "anexo", "comprovante", "fatura", etc.
  - *Improdutivo*: "feliz natal", "bom dia", "parabéns", "agradecemos", etc.
- **Opcional — Hugging Face Inference API**:
  - *Zero-shot classification* (ex.: `facebook/bart-large-mnli`) para decidir entre **Produtivo** e **Improdutivo**.
  - *Text-generation* (ex.: `mistralai/Mistral-7B-Instruct`) para **refinar a resposta** sugerida.
- **Templates de resposta**:
  - *Produtivo* → variações: **Status de solicitação**, **Envio de arquivo/anexo**, **Suporte/erro**, **Cobrança/financeiro**, **Outros produtivos**.
  - *Improdutivo* → agradecimento/encerramento cordial.

> Se a API não estiver configurada, tudo funciona com o modo **Regra + Templates**.

---

## 🌐 Deploy (Render)

### Opção A — `render.yaml` (Infra como código)
1. Crie um novo repositório com estes arquivos.
2. No Render, escolha **"New + Blueprint"** e aponte para o seu GitHub com este projeto.
3. Defina a env var `HUGGINGFACE_API_KEY` (opcional).  
4. Deploy. O serviço subirá em uma URL pública.

### Opção B — Manual (Web Service)
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

> Alternativa: `Dockerfile` incluído para rodar onde quiser.

---

## 📂 Estrutura

```
AutoU-Email-Assistant/
├── backend/
│   ├── main.py               # FastAPI + rotas + serve frontend
│   └── classifier.py         # NLP simples + regras + (opcional) Inference API
├── frontend/
│   └── index.html            # UI HTML + Tailwind + fetch API
├── sample_data/
│   ├── emails_improdutivos/
│   │   ├── email_feliz_natal.txt
│   └── emails_produtivos/
│       ├── email_anexo.txt
│       ├── email_financeiro.txt
│       ├── email_status.txt
│       ├── email_statusII.txt
│       ├── email_suporte.txt
│       └── email_anexo.pdf       # (placeholder explicativo)
├── .env.example
├── Dockerfile
├── LICENSE
├── README.md
├── render.yaml               # Deploy Render
└── requirements.txt
```

## 🧪 Dados de exemplo

- `sample_data/emails_produtivos/email_status.txt` — solicita status/protocolo → **Produtivo** (Status)
- `sample_data/emails_improdutivos/email_feliz_natal.txt` — felicitações → **Improdutivo**

---

## 🔒 Privacidade

- Não armazena emails no servidor.  
- Processa somente em memória para esta demo.  
- Em produção: adicionar logs anonimizados, retention mínima e adequação à LGPD.

---

## 🛣️ Minhas ideais para próximos Passos

- Treinar um classificador supervisionado com base real.
- Ajustar prompts/temperatura do gerador.
- Afinar regras e subtipos (mais rótulos “produtivo”).
- Fila e *rate limit*; dashboards; *feedback loop* com clique “Essa resposta ajudou?”.

---
