# src/tasks/composite.py
from __future__ import annotations
from typing import Dict, Any


def composite_from_task_outputs(outputs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    outputs: dict of {task_name: task_result_dict}
    Produces a single composite score with higher=better.
    """
    # Pull what we need
    mem = outputs.get("memory_immediate_recall", {}).get("score")
    delayed = outputs.get("memory_delayed_recall", {}).get("score")
    rt = outputs.get("reaction_simple", {}).get("metrics", {}).get("avg_rt_ms")
    multi = outputs.get("multidomain_screen", {}).get("metrics", {}).get("percent")

    # Convert RT to a higher=better component
    speed = (1000.0 / rt) if rt and rt > 0 else None

    # Weighted blend; tweak as desired
    parts = []
    weights = []

    if mem is not None:
        parts.append(mem); weights.append(0.25)
    if delayed is not None:
        parts.append(delayed); weights.append(0.30)
    if speed is not None:
        parts.append(speed); weights.append(0.25)
    if multi is not None:
        # multi is 0-1, bring it to 0-10 scale
        parts.append(multi * 10.0); weights.append(0.20)

    if not parts:
        return {"task": "composite", "score": None, "max_score": None, "metrics": {}, "raw": {}}

    # Normalize by sum weights actually present
    wsum = sum(weights)
    score = sum(p * w for p, w in zip(parts, weights)) / wsum

    return {
        "task": "composite",
        "score": score,
        "max_score": None,
        "metrics": {"components_present": len(parts), "weights_sum": wsum},
        "raw": {"parts": parts, "weights": weights}
    }
