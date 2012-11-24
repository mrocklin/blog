from sympy.matrices.expressions import MatrixSymbol, Identity
from sympy import Symbol, Q

n, k    = Symbol('n'), Symbol('k')
mu      = MatrixSymbol('mu', n, 1)
Sigma   = MatrixSymbol('Sigma', n, n)
H       = MatrixSymbol('H', k, n)
R       = MatrixSymbol('R', k, k)
data    = MatrixSymbol('data', k, 1)
I       = Identity(n)

new_mu      = mu + Sigma*H.T * (R + H*Sigma*H.T).I * (H*mu - data)
new_Sigma   = (I - Sigma*H.T * (R + H*Sigma*H.T).I * H) * Sigma

assumptions = (Q.positive_definite(Sigma) & Q.symmetric(Sigma) &
               Q.positive_definite(R) & Q.symmetric(R))
