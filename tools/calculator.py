"""Calculator tool — safe mathematical expression evaluator."""

from __future__ import annotations

import math
import re


def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression safely.

    Supports: +, -, *, /, **, %, sqrt, pow, abs, round, max, min, pi, e, log, sin, cos, tan.

    Args:
        expression: Math expression string, e.g. "sqrt(16)", "2**10", "500/65000".

    Returns:
        Numeric result as a string, or an error message.
    """
    expr = expression.strip().strip('"').strip("'")

    safe_names = {
        "sqrt": math.sqrt,
        "pow": math.pow,
        "abs": abs,
        "round": round,
        "max": max,
        "min": min,
        "sum": sum,
        "log": math.log,
        "log10": math.log10,
        "log2": math.log2,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "floor": math.floor,
        "ceil": math.ceil,
        "pi": math.pi,
        "e": math.e,
        "inf": math.inf,
    }

    # Allow only safe characters
    allowed = re.compile(r"^[\d\s\+\-\*\/\.\(\)\,\^\%\_a-zA-Z]+$")
    if not allowed.match(expr):
        return "Error: expression contains invalid characters."

    # Replace ^ with ** for exponentiation
    expr = expr.replace("^", "**")

    try:
        result = eval(expr, {"__builtins__": {}}, safe_names)  # noqa: S307
        if isinstance(result, float):
            if math.isnan(result):
                return "Error: result is NaN"
            if math.isinf(result):
                return "Error: result is infinite"
            return str(round(result, 10)).rstrip("0").rstrip(".")
        return str(result)
    except ZeroDivisionError:
        return "Error: division by zero."
    except Exception as exc:
        return f"Error evaluating expression: {exc}"
