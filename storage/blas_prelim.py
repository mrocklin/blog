from sympy.matrices.expressions.gen import build_rule, top_down, rr_from_blas
from sympy.matrices.expressions import MatrixSymbol
from sympy import Symbol, Q

n = Symbol('n')
X = MatrixSymbol('X', n, n)
Z = MatrixSymbol('Z', n, n)
target = (4*X*X.T + 2*Z).I*X
assumptions = (Q.positive_definite(X) & Q.positive_definite(Z) &
               Q.symmetric(Z))

computations = list(top_down(build_rule(assumptions))(target))

print computations[0].print_Fortran(str, assumptions)
f = computations[0].build(str, assumptions)
