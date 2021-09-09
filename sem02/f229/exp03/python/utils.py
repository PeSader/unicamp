import math
import numpy as np
from uncertainties import ufloat
from typing import List, Tuple

class LinearFitException(Exception):
    """Uma classe de excecoes para regressao linear"""

def lefetivo_tubo(l: float, r: float, m: int) -> float:
    """ Aplica na medida de comprimento do tubo uma correcao para contabilizar
    que a reflexao das ondas nao ocorre exatamente nas terminacoes do mesmo

    :param l: comprimento do tubo
    :type l: float
    :param r: raio do tubo
    :type r: float
    :param m: numero de aberturas no tubo
    :type m: int
    :return: comprimento efetivo do tubo
    :rtype: float
    """
    return l + 0.6*r*m

def lefetivo_ressoador(l: float, r: float) -> float:
    """ Aplica na medida de comprimento do gargalo do ressoador uma correcao
    para contabilizar que a reflexao das ondas nao ocorre exatamente nas
    terminacoes do mesmo

    :param l: comprimento do gargalo do ressoador
    :type l: float
    :param r: raio do gargalo do ressoador
    :type r: float
    :return: comprimento efetivo do gargalo do ressoador
    :rtype: float
    """
    return l + 1.45*r

def incerteza_padrao_triangular(v: float) -> float:
    """ Determina a incerteza padrao associada a uma medida cuja funcao de
    distribuicao de probabilidade e triangular. Isso ocorre, por exemplo, em
    instrumentos analogicos

    :param v: variacao com relacao a melhor estimativa, por exemplo
        'esse objeto tem 20cm mais ou menos 1cm de altura' onde u=1cm
    :type v: float
    :return: incerteza padrao associada a variacao dada para uma funcao de
        distribuicao de probabilidade triangular
    """
    return v/2*(6**0.5)

def incerteza_padrao_quadrada(v: float) -> float:
    """ Determina a incerteza padrao associada a uma medida cuja funcao de
    distribuicao de probabilidade e quadrada. Isso ocorre, por exemplo, em
    instrumentos de medida digitais

    :param v: variacao com relacao a melhor estimativa, por exemplo
        'esse objeto tem 20cm mais ou menos 1cm de altura' onde u=1cm
    :type v: float
    :return: incerteza padrao associada a variacao dada para uma funcao de
        distribuicao de probabilidade quadrada
    :rtype: float
    """
    return v/2*(3**0.5)

def incerteza_padrao_combinada(l: List[Tuple[float, float]]) -> float:
    """ Avalia a incerteza padrao combinada para uma grandeza, dadas uma lista
    de coeficientes de sensibilidade e incertezas padrao

    :param l: lista de tuplas que descrevem a incerteza de um parametro
        o primeiro elemento da tupla deve ser o coeficiente de sensibilidade
        e o segundo elemento da tupla deve ser a incerteza padrao
    :type l: List[Tuple[float, float]]
    :return: incerteza padrao combinada para uma grandeza
    :rtype: float
    """
    result_squared = 0
    for i in l:
        result_squared += i[0]**2 * i[1]**2
    result = result_squared ** (1/2)
    return result

def freq_fundamental_ressoador(vs: float, r: float, vol: float, lefetivo: float):
    result = ((vs*r)/(2*math.pi))*math.sqrt(math.pi/(vol*lefetivo))
    return result

def regressao_linear(x, y, yerror) -> Tuple[float, float]:

    if len(x) != len(y):
        raise Exception("x e y precisam ter o mesmo numero de elementos")

    n = len(x)
    sum_x = np.sum(x)
    sum_y = np.sum(y)

    # calcular o somatorio dos produtos de x e y
    sum_xy = 0
    for i in range(n):
        sum_xy += x[i]*y[i]

    # calcular o somatorio de x ao quadrado
    sum_x_squared = 0
    for i in range(n):
        sum_x_squared += x[i]**2

    delta = n*sum_x_squared - sum_x**2

    coef_angular = (n*sum_xy - sum_x*sum_y)/delta
    incerteza_coef_angular = math.sqrt(n/delta)*yerror
    a = ufloat(coef_angular, incerteza_coef_angular)

    coef_linear = (sum_y*sum_x_squared - sum_xy*sum_x)/delta
    incerteza_coef_linear = math.sqrt(sum_x_squared/delta)*yerror
    b = ufloat(coef_linear, incerteza_coef_linear)

    return a, b


