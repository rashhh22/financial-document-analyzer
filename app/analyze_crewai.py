from crewai import Agent, Task, Crew, Process

SYSTEM = (
    "You are a financial document analyzer. "
    "Return a JSON with keys: company, period, revenue, operating_income, net_income, ebitda, eps, guidance, cash_flow, highlights[], risks[]. "
    "Unknown → null. After JSON, add a concise Markdown summary (3-6 bullets). No financial advice."
)

def run_crewai(text: str, query: str | None = None) -> str:
    analyst = Agent(
        role="Financial Analyst",
        goal="Extract structured financial metrics from the document",
        backstory="Expert in financial statements and earnings reports.",
        allow_delegation=False,
        verbose=False,
    )
    prompt = f"""
{SYSTEM}

Document text:
{text[:12000]}

Query: {query or "Extract key metrics & risks"}

Return strictly:
1) A JSON with the required keys (unknown → null)
2) A concise Markdown summary
"""
    t = Task(description=prompt, agent=analyst)
    out = Crew(agents=[analyst], tasks=[t], process=Process.sequential).kickoff()
    return str(out)
