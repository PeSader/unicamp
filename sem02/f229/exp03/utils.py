 import math

def lefetivo_tubo(l: float, r: float, m: int) -> float:
    return l + 0.6*r*m

def lefetivo_ressoador(l: float, r: float) -> float:
    return l + 1.45*r

def incerteza_triangular(u: float) -> float:
   return u/(6**0.5)

def incerteza_quadrada(u: float) -> float:
   return u/(3**0.5)
