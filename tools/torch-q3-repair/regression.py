"""CPU-only reproduction of the reported Inductor symbolic-range assertion."""
import sys
import sympy
import torch
from torch._inductor.sizevars import SizeVarAllocator
from torch.utils._sympy.functions import FloorDiv, Max, Min, ModularIndexing

print('Python:', sys.version, flush=True)
print('Torch:', torch.__version__, 'CUDA build:', torch.version.cuda, flush=True)
q3 = sympy.Symbol('q3', integer=True, nonnegative=True)
base = Min(Min(28, FloorDiv(q3, 2) + 1) - 1, Max(0, FloorDiv(q3 - 1, 2)))
expr = ModularIndexing(base, 1, 14)
print('Input:', expr, flush=True)
result = SizeVarAllocator().simplify_with_ranges(expr, {q3: 28})
for value in range(28):
    assert expr.subs(q3, value) == result.subs(q3, value), (value, expr, result)
print('PASS: simplification preserves results for every loop index:', result, flush=True)

from torch._inductor.sizevars import SizeVarAllocator
from torch.fx.experimental.symbolic_shapes import ShapeEnv
from torch.utils._sympy.functions import FloorDiv, Max, Min, ModularIndexing
from torch.utils._sympy.value_ranges import ValueRanges
print('Additional symbolic regression cases:', flush=True)
count = 0
for name in ['q0', 'q3', 'q17']:
    q = sympy.Symbol(name, integer=True, nonnegative=True)
    for n in [2, 4, 14, 28, 32, 64]:
        for div in [2, 3, 4]:
            base = Min(Min(n, FloorDiv(q, div) + 1) - 1, Max(0, FloorDiv(q - 1, div)))
            expr = ModularIndexing(base, 1, n // 2)
            result = SizeVarAllocator().simplify_with_ranges(expr, {q: n})
            for value in range(n):
                assert expr.subs(q, value) == result.subs(q, value), (name, n, div, value)
            count += 1
q = sympy.Symbol('q3', integer=True, nonnegative=True)
env = ShapeEnv()
expr = Max(1, q - 1)
assert env.simplify(expr, var_to_range=((q, ValueRanges(2, 10)),)) == q - 1
# This pass only removes Max when its variable branch wins. It must not
# reuse the high-range simplification for a different local range.
low_result = env.simplify(expr, var_to_range=((q, ValueRanges(0, 1)),))
for value in (0, 1):
    assert low_result.subs(q, value) == expr.subs(q, value)
assert q not in env.var_to_range
print('PASS:', count, 'range-preserving cases and independent range-context cache checks', flush=True)
