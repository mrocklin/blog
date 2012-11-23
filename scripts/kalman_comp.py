from kalman import newmu, newSigma, assumptions, mu, Sigma, R, H, data, I

from sympy.computations.matrices.compile import make_rule, patterns
from sympy.computations.core import Identity

ident = Identity(newmu, newSigma)
rule = make_rule(patterns, assumptions)
mathcomp = next(rule(ident))

assert set(mathcomp.inputs) == set((mu, Sigma, H, R, data, I))
assert set(mathcomp.outputs).issuperset(set((newmu, newSigma)))

mathcomp.show()
