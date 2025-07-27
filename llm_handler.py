import subprocess
import json
import logging
import argparse
import re

from data_queries import (
    get_top_mutated_genes,
    get_least_mutated_genes,
    get_mutation_count_for_gene,
    get_genes_with_mutation_count_greater_than,
    get_total_patients,
    get_mutation_types_for_gene,
    get_mrna_expression,
    get_average_age_at_diagnosis,
    get_patient_count_by_stage,
)

# ── CLI args ────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="cbio LLM-driven chatbot")
parser.add_argument("--model", default="phi", help="Ollama model name")
parser.add_argument("--timeout", type=int, default=180, help="LLM timeout in seconds")
args = parser.parse_args()

# ── Logging ─────────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
h = logging.StreamHandler()
h.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
logger.addHandler(h)

# ── Regex fallback for key patterns ─────────────────────────────────────────────
def fallback_parse(q: str):
    q = q.lower().strip()
    # Top N least mutated genes
    m = re.match(r"top\s+(\d+)\s+least mutated genes", q)
    if m:
        return "get_least_mutated_genes", {"n": int(m.group(1))}
    # Top N mutated genes
    m = re.match(r"top\s+(\d+)\s+mutated genes", q)
    if m:
        return "get_top_mutated_genes", {"n": int(m.group(1))}
    # Mutation count for a gene
    m = re.match(r"mutation count for (\w+)", q)
    if m:
        return "get_mutation_count_for_gene", {"gene": m.group(1).upper()}
    # Genes with > X mutations
    m = re.match(r"genes with more than\s+(\d+)\s+mutations", q)
    if m:
        return "get_genes_with_mutation_count_greater_than", {"x": int(m.group(1))}
    # How many patients?
    if "how many patients" in q:
        return "get_total_patients", {}
    # Average age at diagnosis
    if "average age at diagnosis" in q:
        return "get_average_age_at_diagnosis", {}
    # Patient count by tumor stage
    if "patient count by tumor stage" in q or "patients in each tumor stage" in q:
        return "get_patient_count_by_stage", {}
    # Mutation types for a gene
    m = re.match(r"mutation types for (\w+)", q)
    if m:
        return "get_mutation_types_for_gene", {"gene": m.group(1).upper()}
    # mRNA expression for a gene
    m = re.match(r"mrna expression of (\w+)", q)
    if m:
        return "get_mrna_expression", {"gene": m.group(1).upper()}
    return None, None

# ── LLM orchestration ────────────────────────────────────────────────────────────
def call_llm(query: str, model: str, timeout: int) -> dict | None:
    prompt = (
        """
You are a data-driven assistant with these tools:
  • get_top_mutated_genes(n)
  • get_least_mutated_genes(n)
  • get_mutation_count_for_gene(gene)
  • get_genes_with_mutation_count_greater_than(x)
  • get_total_patients()
  • get_mutation_types_for_gene(gene)
  • get_mrna_expression(gene)
  • get_average_age_at_diagnosis()
  • get_patient_count_by_stage()

For any user query, choose exactly one tool + args and respond with JSON ONLY:
{"tool":"<tool_name>","args":{ /* args */ }}

Examples:
Query: "Top 5 mutated genes"
Response: {"tool":"get_top_mutated_genes","args":{"n":5}}

Query: "Top 10 least mutated genes"
Response: {"tool":"get_least_mutated_genes","args":{"n":10}}

Query: "Mutation count for EGFR"
Response: {"tool":"get_mutation_count_for_gene","args":{"gene":"EGFR"}}

Query: "Mutation types for TP53"
Response: {"tool":"get_mutation_types_for_gene","args":{"gene":"TP53"}}

Query: "Average age at diagnosis"
Response: {"tool":"get_average_age_at_diagnosis","args":{}}

Query: "Patient count by tumor stage"
Response: {"tool":"get_patient_count_by_stage","args":{}}

IMPORTANT: Output only the JSON object, nothing else.
"""
        + "\n" + query + "\n"
    )
    llm_input = json.dumps([prompt, query])
    try:
        proc = subprocess.run(
            ["ollama", "run", "--format=json", model, llm_input],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            timeout=timeout,
        )
        if proc.stderr:
            logger.warning(proc.stderr.strip())
        raw = proc.stdout.strip()
        if not raw:
            return None
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        payload = json.loads(raw[start:end])
        logger.info("🔍 LLM payload: %r", payload)
        return payload
    except Exception as e:
        logger.error("LLM call failed: %s", e)
        return None

# ── Dispatch & format ───────────────────────────────────────────────────────────
def handle_query(raw: str) -> str:
    # strip leading '>' and spaces
    query = raw.lstrip("> ").strip()

    # 1) Regex fallback first
    tool, tool_args = fallback_parse(query)

    # 2) Otherwise, ask the LLM
    if tool is None:
        resp = call_llm(query, args.model, args.timeout) or {}
        low = {k.lower(): v for k, v in resp.items()}
        tool = low.get("tool")
        tool_args = low.get("args", {})

    if not tool:
        return "🚫 Sorry, I couldn’t find a tool for that query."

    try:
        if tool == "get_top_mutated_genes":
            res = get_top_mutated_genes(**tool_args)
        elif tool == "get_least_mutated_genes":
            res = get_least_mutated_genes(**tool_args)
        elif tool == "get_mutation_count_for_gene":
            res = get_mutation_count_for_gene(**tool_args)
        elif tool == "get_genes_with_mutation_count_greater_than":
            res = get_genes_with_mutation_count_greater_than(tool_args.get("x"))
        elif tool == "get_total_patients":
            res = get_total_patients()
        elif tool == "get_mutation_types_for_gene":
            res = get_mutation_types_for_gene(**tool_args)
        elif tool == "get_mrna_expression":
            res = get_mrna_expression(**tool_args)
        elif tool == "get_average_age_at_diagnosis":
            res = get_average_age_at_diagnosis()
        elif tool == "get_patient_count_by_stage":
            dist = get_patient_count_by_stage()
            return ", ".join(f"{stage}: {count}" for stage, count in dist.items())
        else:
            return f"🚫 I don’t know how to handle `{tool}`."

        # format list vs scalar
        if isinstance(res, list):
            return ", ".join(res) or "(none)"
        return str(res)

    except Exception as e:
        logger.error("Error running %s: %s", tool, e)
        return f"❗️ Error ({tool}): {e}"

# ── REPL ─────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("cbio LLM-driven chatbot. Type queries, or 'quit' to exit.")
    while True:
        raw = input("> ")
        if raw.lower().startswith(("quit", "exit")):
            break
        print(handle_query(raw), "\n")
