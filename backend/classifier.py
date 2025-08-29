import os
import re
import json
import requests
from typing import Dict, Any, List, Tuple

# ------------------------- Helpers NLP -------------------------

PT_STOP = {
    "a","à","às","agora","ainda","além","algum","alguma","alguns","algumas","ali","ano","anos",
    "ante","antes","ao","aos","após","as","assim","até","cada","como","com","contra","cujo","cuja",
    "da","das","de","dela","dele","deles","demais","depois","desde","dessa","desse","desta","deste",
    "do","dos","e","ela","elas","ele","eles","em","entre","era","eram","es","essa","essas","esse","esses",
    "esta","estas","este","estes","eu","foi","foram","há","isso","isto","já","lhe","lhes","lá","mais",
    "mas","me","mesmo","mesma","meus","minha","minhas","muito","muitos","na","nas","não","nem","no","nos",
    "nós","num","numa","o","os","ou","para","pela","pelas","pelo","pelos","por","qual","quais","quando",
    "que","quem","se","sem","seu","seus","sua","suas","só","também","tão","te","tem","têm","ti","tua","tuas",
    "um","uma","você","vocês"
}

EN_STOP = {
    "a","an","the","and","or","but","with","without","of","to","in","on","for","from","by","at",
    "is","are","was","were","be","been","being","as","that","this","these","those","it","its","into",
    "we","you","they","i","he","she","them","us","our","your","their","do","does","did","not"
}

def normalize(text: str) -> str:
    text = text or ""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def tokenize(text: str) -> List[str]:
    text = re.sub(r"[^\wáéíóúàãõâêîôûç%/.-]", " ", text.lower())
    toks = [t for t in re.split(r"\s+", text) if t]
    return toks

def remove_stopwords(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in PT_STOP and t not in EN_STOP]

# --------------------- Rule-based classifier -------------------

PRODUCTIVE_HINTS = {
    "status": 2.5, "andamento": 2.0, "protocolo": 2.2, "ticket": 2.2, "chamado": 2.0, "prazo": 1.5,
    "erro": 2.5, "bug": 2.3, "falha": 2.2, "indisponível": 2.2, "instável": 2.0, "suporte": 2.0,
    "anexo": 2.2, "arquivo": 2.0, "comprovante": 2.2, "documento": 2.0, "pdf": 1.8,
    "boleto": 2.2, "fatura": 2.2, "cobrança": 2.2, "pagamento": 2.0, "estorno": 2.3, "nota": 1.8,
    "dúvida": 1.5, "solicito": 2.0, "solicitação": 2.0, "pedido": 1.6, "acesso": 1.7, "cadastro": 1.6,
    "reembolso": 2.2, "contato": 1.4, "retorno": 1.4
}

UNPRODUCTIVE_HINTS = {
    "feliz": 2.0, "natal": 2.2, "ano": 1.0, "novo": 1.0, "parabéns": 2.0, "obrigado": 1.0, "obrigada": 1.0,
    "bom": 1.0, "dia": 0.8, "boa": 0.8, "tarde": 0.8, "noite": 0.8, "agradeço": 1.5, "abraços": 1.3,
    "atenciosamente": 0.8, "grato": 1.2, "grata": 1.2, "saudações": 1.2
}

SUBTYPE_PATTERNS = [
    ("status", [r"\bstatus\b", r"\bandamento\b", r"\bprotocolo\b", r"\bticket\b", r"\bchamado\b"]),
    ("anexo",  [r"\banexo\b", r"\barquivo\b", r"\bcomprovante\b", r"\bsegue\s+em\s+anexo\b", r"\bsegue\s+o\b"]),
    ("suporte",[r"\berro\b", r"\bbug\b", r"\bfalha\b", r"\bindispon[ií]vel\b", r"\bsuporte\b", r"\bacesso\b"]),
    ("financeiro",[r"\bboleto\b", r"\bfatura\b", r"\bcobrança\b", r"\bpagamento\b", r"\bestorno\b", r"\breembolso\b"]),
]

def score_rules(text: str) -> Tuple[float, float, List[str]]:
    toks = remove_stopwords(tokenize(text))
    prod = 0.0
    unprod = 0.0
    reasons = []
    for t in toks:
        if t in PRODUCTIVE_HINTS:
            prod += PRODUCTIVE_HINTS[t]
        if t in UNPRODUCTIVE_HINTS:
            unprod += UNPRODUCTIVE_HINTS[t]
    if prod > 0:
        reasons.append(f"Regras Produtivo: escore={prod:.2f}")
    if unprod > 0:
        reasons.append(f"Regras Improdutivo: escore={unprod:.2f}")
    return prod, unprod, reasons

def detect_subtype(text: str) -> str:
    for label, patterns in SUBTYPE_PATTERNS:
        for pat in patterns:
            if re.search(pat, text, flags=re.IGNORECASE):
                return label
    # heurística adicional: menção a PDF/extensão
    if re.search(r"\.(pdf|docx|xlsx|csv)\b", text, flags=re.IGNORECASE):
        return "anexo"
    return "outros"

# ------------------ Optional: Hugging Face API -----------------

def hf_request(endpoint: str, payload: Dict[str, Any], api_key: str, timeout: int = 25) -> Any:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    r = requests.post(endpoint, headers=headers, data=json.dumps(payload), timeout=timeout)
    r.raise_for_status()
    return r.json()

def zeroshoot_label(text: str, labels: List[str], api_key: str, model: str) -> Tuple[str, float, List[str]]:
    endpoint = f"https://api-inference.huggingface.co/models/{model}"
    payload = {
        "inputs": text,
        "parameters": {"candidate_labels": labels, "multi_label": False}
    }
    data = hf_request(endpoint, payload, api_key)
    # resposta pode variar — normalizamos
    if isinstance(data, dict) and "labels" in data and "scores" in data:
        labels_resp = data["labels"]
        scores_resp = data["scores"]
    elif isinstance(data, list) and data and isinstance(data[0], dict) and "labels" in data[0]:
        labels_resp = data[0]["labels"]
        scores_resp = data[0].get("scores", [])
    else:
        return "", 0.0, ["HF zero-shot retornou formato inesperado"]
    if not labels_resp:
        return "", 0.0, ["HF zero-shot não retornou rótulos"]
    best = labels_resp[0]
    best_score = scores_resp[0] if scores_resp else 0.0
    return best, float(best_score), [f"HF zero-shot: {best} ({best_score:.2f})"]

def hf_generate(prompt: str, api_key: str, model: str) -> str:
    endpoint = f"https://api-inference.huggingface.co/models/{model}"
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 180, "temperature": 0.3, "return_full_text": False}
    }
    data = hf_request(endpoint, payload, api_key)
    # formatos variam
    if isinstance(data, list) and data and "generated_text" in data[0]:
        return data[0]["generated_text"].strip()
    if isinstance(data, dict) and "generated_text" in data:
        return data["generated_text"].strip()
    return ""

# --------------------- Suggest reply (PT-BR) -------------------

def template_reply(category: str, subtype: str, text: str) -> str:
    if category == "Produtivo":
        if subtype == "status":
            return (
                "Olá! Obrigado pelo contato. Identificamos sua solicitação como um pedido de **status**. "
                "Se possível, confirme o **número de protocolo/ticket** para agilizar a verificação. "
                "Vamos consultar o andamento e retornamos em seguida com a atualização."
            )
        if subtype == "anexo":
            return (
                "Olá! Recebemos o **arquivo/anexo**. Vamos realizar a validação necessária e, caso haja "
                "alguma pendência, retornamos solicitando informações adicionais."
            )
        if subtype == "suporte":
            return (
                "Olá! Sentimos pelo inconveniente. Para darmos sequência no **suporte**, por favor informe, "
                "se possível, prints do erro, horário aproximado da ocorrência e e-mail de acesso. "
                "Vamos analisar e retornar com as próximas etapas."
            )
        if subtype == "financeiro":
            return (
                "Olá! Recebemos sua mensagem relacionada a **cobrança/pagamentos**. "
                "Vamos verificar os dados e retornamos com as orientações ou confirmações necessárias."
            )
        return (
            "Olá! Obrigado pelo contato. Classificamos sua mensagem como **produtiva** e vamos dar "
            "sequência ao atendimento. Caso tenha detalhes adicionais, por favor responda a este e-mail."
        )
    else:
        return (
            "Olá! Agradecemos a mensagem. "
            "Registramos seu contato e ficamos à disposição para qualquer necessidade."
        )

def llm_refine_reply(base_reply: str, text: str, category: str, api_key: str, model: str) -> str:
    # Usa LLM para reescrever a resposta mantendo o conteúdo essencial, tom profissional e concisão.
    prompt = (
        "Reescreva a mensagem de resposta abaixo em português, mantendo tom profissional, conciso e claro. "
        "Se houver dados concretos no e-mail, contextualize sutilmente. Não invente prazos nem números. "
        "Mensagem base:\n"
        f"{base_reply}\n\n"
        "E-mail do usuário:\n"
        f"{text}\n\n"
        "Responda apenas com o texto final, sem explicações."
    )
    try:
        refined = hf_generate(prompt, api_key, model)
        return refined or base_reply
    except Exception:
        return base_reply

# ------------------------ Public API ---------------------------

def classify_email(text: str, use_llm: bool = False) -> Dict[str, Any]:
    """
    Classifica um e-mail em 'Produtivo' ou 'Improdutivo', detecta subtipo e sugere resposta.
    Integração opcional com Hugging Face Zero-Shot e geração de resposta via LLM.
    """
    text_norm = normalize(text)

    # 1️⃣ Score por regras
    prod, unprod, reasons = score_rules(text_norm)
    subtype = detect_subtype(text_norm)

    # 2️⃣ Categoria inicial baseada em regras
    category = "Produtivo" if prod >= unprod else "Improdutivo"
    confidence = float(abs(prod - unprod) / (prod + unprod + 1e-6))  # 0..1 aprox

    # 3️⃣ Integração opcional Hugging Face
    hf_key = os.getenv("HUGGINGFACE_API_KEY", "").strip()
    zs_model = os.getenv("HF_ZEROSHOT_MODEL", "facebook/bart-large-mnli")
    gen_model = os.getenv("HF_GENERATION_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")

    if use_llm and hf_key:
        try:
            # Zero-shot classification
            label, score, expl = zeroshoot_label(
                text_norm,
                ["Produtivo", "Improdutivo"],
                hf_key,
                zs_model
            )
            if label:
                # Normaliza label e atualiza categoria/confiança
                category = label.strip().capitalize()  # garante "Produtivo" ou "Improdutivo"
                confidence = float(score)  # confiança retornada pelo zero-shot
                reasons.extend(expl)
        except Exception as e:
            reasons.append(f"Falha HF zero-shot: {e}")

    # 4️⃣ Geração opcional de resposta via LLM
    reply = template_reply(category, subtype, text_norm)
    if use_llm and hf_key:
        try:
            refined = llm_refine_reply(reply, text_norm, category, hf_key, gen_model)
            if refined:
                reply = refined
                reasons.append("Resposta refinada por LLM (HF Inference).")
        except Exception as e:
            reasons.append(f"Falha ao refinar com LLM: {e}")

    # 5️⃣ Resultado final
    return {
        "category": category,
        "confidence": round(confidence, 3),
        "subtype": subtype,
        "suggested_reply": reply,
        "reasons": reasons[:6]  # limita a 6 explicações
    }

