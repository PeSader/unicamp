 import math

def lefetivo_tubo(l: float, r: float, m: int) -> float:
    """

    :param l: float: comprimento do tubo
    :param r: float: raio do tubo
    :param m: int: numero de aberturas no tubo

    :return: float: comprimento efetivo do tubo

    """
    return l + 0.6*r*m

def lefetivo_ressoador(l: float, r: float) -> float:
    """

    :param l: float: comprimento do gargalo do ressoador
    :param r: float: raio do gargalo do ressoador

    :return: float: comprimento efetivo do gargalo do ressoador

    """
    return l + 1.45*r

def incerteza_triangular(v: float) -> float:
    """

    :param v: float: variacao com relacao a melhor estimativa, por exemplo
        'esse objeto tem 20cm mais ou menos 1cm de altura' onde u=1cm

    :return: incerteza padrao associada a variacao dada para uma funcao de
        distribuicao de probabilidade triangular

    """
    return v/(6**0.5)

def incerteza_quadrada(v: float) -> float:
    """

    :param v: float: variacao com relacao a melhor estimativa, por exemplo
        'esse objeto tem 20cm mais ou menos 1cm de altura' onde u=1cm

    :return: incerteza padrao associada a variacao dada para uma funcao de
        distribuicao de probabilidade quadrada

    """
    return v/(3**0.5)
