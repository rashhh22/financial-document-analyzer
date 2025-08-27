import re, json
from typing import Any, Dict
from .settings import settings

def _extract_json_and_md(text: str, fallback: dict):
    try:
        json_str = re.search(r"\{[\s\S]*\}", text).group(0)
        parsed = json.loads(json_str)
        md = text.split(json_str, 1)[-1].strip()
        return {"json": parsed, "markdown": md}
    except Exception:
        return fallback

def analyze_with_fallback(text: str, query: str | None = None) -> Dict[str, Any]:
    import re
    amounts = re.findall(r"\$?\b([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|[0-9]+\.[0-9]+)\b", text)
    amounts = [a.replace(",", "") for a in amounts]
    first = float(amounts[0]) if amounts else None
    json_obj = {"company": None, "period": None, "revenue": first, "operating_income": None, "net_income": None,
                "ebitda": None, "eps": None, "guidance": None, "cash_flow": None, "highlights": [], "risks": [], "_note": "Fallback analyzer used"}
    md = "**Summary (heuristic)**: " + (text[:300].replace("\n", " ") + "...")
    return {"json": json_obj, "markdown": md}

def analyze_with_openai(text: str, query: str | None = None) -> Dict[str, Any]:
    from openai import OpenAI
    if not settings.OPENAI_API_KEY: return analyze_with_fallback(text, query)
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    system = ("You are a financial document analyzer. Return a JSON with keys: company, period, revenue, operating_income, net_income, ebitda, eps, guidance, cash_flow, highlights[], risks[]. "
              "Unknown → null. After JSON, add a concise Markdown summary (3-6 bullets). No financial advice.")
    user = f"Document text:\n{text[:12000]}\n\nQuery: {query or 'Extract key metrics & risks'}"
    resp = client.chat.completions.create(model=settings.MODEL_NAME, messages=[{"role":"system","content":system},{"role":"user","content":user}], temperature=0.1)
    content = resp.choices[0].message.content
    return _extract_json_and_md(content, analyze_with_fallback(text, query))

def analyze_with_crewai(text: str, query: str | None = None) -> Dict[str, Any]:
    from .analyze_crewai import run_crewai
    raw = run_crewai(text, query)
    return _extract_json_and_md(raw, analyze_with_fallback(text, query))

def analyze_text(text: str, query: str | None = None) -> Dict[str, Any]:
    provider = settings.ANALYZER_PROVIDER.lower()
    if provider == "crewai": return analyze_with_crewai(text, query)
    if provider == "openai": return analyze_with_openai(text, query)
    return analyze_with_fallback(text, query)
