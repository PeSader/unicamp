from typing import List, Tuple

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

def incerteza_triangular(v: float) -> float:
    """ Determina a incerteza padrao associada a uma medida cuja funcao de
    distribuicao de probabilidade e triangular. Isso ocorre, por exemplo, em
    instrumentos analogicos

    :param v: variacao com relacao a melhor estimativa, por exemplo
        'esse objeto tem 20cm mais ou menos 1cm de altura' onde u=1cm
    :type v: float
    :return: incerteza padrao associada a variacao dada para uma funcao de
        distribuicao de probabilidade triangular
    """
    return v/(6**0.5)

def incerteza_quadrada(v: float) -> float:
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
    return v/(3**0.5)

def incerteza_padrao(l: List[Tuple[float, float]]) -> float:
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
