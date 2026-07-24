from __future__ import annotations

import ast
import operator
from collections.abc import Callable
from typing import Any

from app.tools.base import ToolResult

_BinOpFunc = Callable[[Any, Any], Any]
_UnaryOpFunc = Callable[[Any], Any]

_BINARY_OPS: dict[type[ast.operator], _BinOpFunc] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPS: dict[type[ast.unaryop], _UnaryOpFunc] = {
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


class CalculatorTool:
    name = "calculator"
    description = (
        "Safely evaluates mathematical expressions "
        "(addition, subtraction, multiplication, division, parentheses)."
    )
    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression to evaluate, e.g. '(2 + 3) * 4'",
            }
        },
        "required": ["expression"],
    }

    async def execute(self, **kwargs: Any) -> ToolResult:
        expression = kwargs.get("expression", "")
        if not expression or not isinstance(expression, str):
            return ToolResult(success=False, error="A non-empty expression string is required")

        try:
            tree = ast.parse(expression.strip(), mode="eval")
            value = self._eval_node(tree.body)
            return ToolResult(success=True, data=value)
        except (ValueError, TypeError, ZeroDivisionError, SyntaxError, KeyError) as exc:
            return ToolResult(success=False, error=f"Evaluation error: {exc}")

    def _eval_node(self, node: ast.expr) -> float | int:
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
            return node.value
        if isinstance(node, ast.BinOp):
            bin_op_type = type(node.op)
            if bin_op_type not in _BINARY_OPS:
                raise ValueError(f"Unsupported operator: {bin_op_type.__name__}")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            result = _BINARY_OPS[bin_op_type](left, right)
            return float(result) if isinstance(result, float) else int(result)
        if isinstance(node, ast.UnaryOp):
            unary_op_type = type(node.op)
            if unary_op_type not in _UNARY_OPS:
                raise ValueError(f"Unsupported unary operator: {unary_op_type.__name__}")
            operand = self._eval_node(node.operand)
            result = _UNARY_OPS[unary_op_type](operand)
            return float(result) if isinstance(result, float) else int(result)
        raise ValueError(f"Unsupported expression type: {type(node).__name__}")
