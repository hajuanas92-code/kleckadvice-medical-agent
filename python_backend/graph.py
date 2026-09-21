from __future__ import annotations

from typing import TypedDict
from langgraph.graph import StateGraph, END
from extraction import extract_text_from_pdf
from llm import extract_metrics
from typing import List


# ---------------------------------------------------------------------------
# Shared state passed between nodes
# ---------------------------------------------------------------------------
class ReportState(TypedDict, total=False):
    pdf_path: str
    raw_text: str
    page_numbers: List[int]
    result: dict
    error: str


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------
def ocr_node(state: ReportState) -> ReportState:
    try:
        text = extract_text_from_pdf(state["pdf_path"], engine="tesseract", page_numbers=state.get("page_numbers"))
        return {"raw_text": text}
    except Exception as e:
        return {"error": f"OCR failed: {e}"}


def extract_node(state: ReportState) -> ReportState:
    if state.get("error"):
        return state  # skip if OCR already failed

    try:
        result = extract_metrics(state["raw_text"])
        return {"result": result}
    except Exception as e:
        return {"error": f"LLM extraction failed: {e}"}


# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------
def build_graph():
    graph = StateGraph(ReportState)

    graph.add_node("ocr", ocr_node)
    graph.add_node("extract", extract_node)

    graph.set_entry_point("ocr")
    graph.add_edge("ocr", "extract")
    graph.add_edge("extract", END)

    return graph.compile()


# Compiled once at import time, reused across requests
report_graph = build_graph()


def run_pipeline(pdf_path: str, page_numbers: List[int] = None) -> dict:
    """
    Entry point FastAPI will call. Runs the full graph for one PDF
    and returns either {"result": {...}} or {"error": "..."}.
    """
    final_state = report_graph.invoke({"pdf_path": pdf_path, "page_numbers": page_numbers})

    if final_state.get("error"):
        return {"error": final_state["error"]}

    result = final_state["result"]
    result["raw_text"] = final_state["raw_text"]   # <- is this line there?
    return {"result": result}
# ---------------------------------------------------------------------------
# Quick manual test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python graph.py <path_to_report.pdf>")
        sys.exit(1)

    output = run_pipeline(sys.argv[1])
    print(json.dumps(output, indent=2))