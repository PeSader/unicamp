# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 14:58:00 2020

@author: Christoph Deneke
@author: Pedro Sader Azevedo
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import lmfit
import os
from typing import Callable, Tuple

DPI = 1200
DATA_DIR = './data'
FILENAMES = os.listdir(DATA_DIR)
REPORT_FILENAME = 'report.md'
PREFIXO_TITULO_GRAFICO = 'Resfriamento de '
VALORES_DE_M = [3, 4, 5, 6]
NOME_DO_MODELO = {1: 'Condução e Convecção Forçada', 2: 'Convecção Natural'}


def main():
    # limpar arquivo do relatorio e inserir titulo
    with open(REPORT_FILENAME, 'w') as f:
        f.write('# Documento Auxiliar ao Relatório 5\n\n')
    # iterar lista de arquivos com dados para analisa-los
    for f in FILENAMES:
        analize_data(f'./data/{f}')


def exp_cooling(t: float, T0: float, T_inf: float, gamma: float) -> float:
    """modela transferencia de calor por conducao ou conveccao forcada

    :param t: tempo
    :type t: float
    :param T0: temperatura inicial
    :type T0: float
    :param T_inf: temperatura infinita
    :type T_inf: float
    :param gamma: parametro que depende do coef. de transferencia de calor
    :type gamma: float
    :rtype: float
    """
    return (T0-T_inf)*np.exp(-gamma*t)+T_inf


def cooling(t: float, T0: float, A: float, B: float, C: float, m: int) -> float:
    """modela transferencia de calor por conveccao natural

    :param t: tempo
    :type t: float
    :param T0: temperatura inicial
    :type T0: float
    :param m: parametro inversamente proporcional ao coef. de transferencia de calor
    :type m: int
    :rtype: float
    """
    return T0+(A/(B+C*t)**m)


def _fit_exp_cooling(func: Callable, tempo: np.ndarray, temperatura: np.ndarray) -> lmfit.model.ModelResult:
    """configura um ajuste ao modelo de resfriamento por conducao ou conveccao forcada

    :param func: modelo de resfriamento por conducao ou conveccao forcada
    :type func: Callable
    :param tempo: np.a variavel independente
    :type tempo: ndarray
    :param temperatura: np.a variavel dependente
    :type temperatura: ndarray
    :rtype: lmfit.model.ModelResult
    """
    exp_model = lmfit.Model(func)

    # configurar limites maximos e minimos dos parametros
    exp_model.set_param_hint('T0', value=350, min=340, max=370, vary=True)
    exp_model.set_param_hint('T_inf', value=26+273,
                             min=20+273, max=30+273, vary=True)
    exp_model.set_param_hint('gamma', value=0.001, min=0.0001, vary=True)
    param = exp_model.make_params()

    results_exp_cooling = exp_model.fit(temperatura, t=tempo, params=param)
    print(results_exp_cooling.fit_report())

    return results_exp_cooling


def _fit_cooling(func: Callable, tempo: np.ndarray, temperatura: np.ndarray, m: int) -> lmfit.model.ModelResult:
    """configura um ajuste ao modelo de resfriamento por conveccao natural

    :param func: modelo de resfriamento por conveccao natural
    :type func: Callable
    :param tempo: np.a variavel independente
    :type tempo: ndarray
    :param temperatura: np.a variavel dependente
    :type temperatura: ndarray
    :param m: parametro inversamente proporcional ao coef. de transferencia de calor
    :type m: int
    :rtype: lmfit.model.ModelResult
    """
    cooling_model = lmfit.Model(func)
    print('parameter names: {}'.format(cooling_model.param_names))
    print('independent variables: {}'.format(cooling_model.independent_vars))

    cooling_model.set_param_hint('T0', value=300, min=273, max=350, vary=True)
    cooling_model.set_param_hint('A', value=68, min=0.0001, vary=True)
    cooling_model.set_param_hint('B', value=1, min=1, vary=False)
    cooling_model.set_param_hint('C', value=0.00229893, min=0.0001, vary=True)
    cooling_model.set_param_hint('m', value=m, vary=False)
    param = cooling_model.make_params()
    results_cooling = cooling_model.fit(temperatura, t=tempo, params=param)
    return results_cooling


def _generate_plot_tile(path: str, prefix: str = PREFIXO_TITULO_GRAFICO, suffix: str = "") -> str:
    """cria um titulo baseado no nome do arquivo de dados

    :param path: caminho para o arquivo de dados
    :type path: str
    :param prefix: texto a ser incluido antes
    :type prefix: str, optional
    :param suffix: texto a ser incluido depois
    :type suffix: str, optional
    :rtype: str
    """
    title = prefix
    for w in path.split('/')[-1].split('.')[0].split('_'):
        if len(w) > 3:
            title += f'{w.capitalize()} '
        else:
            title += f'{w} '
    title += suffix
    return title


def _linearize_exp(results: lmfit.model.ModelResult, temperatura: np.ndarray) -> np.ndarray:
    """lineariza dados experimentais assumindo modelo de conducao ou conveccao forcada

    :param results: resultado do ajuste dos dados experimentais ao modelo
    :type results: lmfit.model.ModelResult
    :param temperatura: dados experimentais de temperatura
    :type temperatura: np.ndarray
    :rtype: np.ndarray
    """
    param_T0 = results.params['T0'].value
    param_Tinf = results.params['T_inf'].value
    y = np.log((temperatura - param_Tinf) /
               (param_T0 - param_Tinf))*(-1)
    return y


def _linearize_cooling(results) -> Tuple[float, float]:
    """lineariza dados experimentais assumindo modelo de conveccao natural

    :param results: resultado do ajuste dos dados experimentais ao modelo
    :type results: lmfit.model.ModelResult
    :rtype: Tuple[float, float]
    """
    param_A = results.params['A'].value
    param_B = results.params['B'].value
    param_C = results.params['C'].value
    param_m = results.params['m'].value

    a = param_C/(param_A**(1/param_m))  # coefieciente angular
    b = param_B/(param_A**(1/param_m))  # coefieciente linear
    return a, b


def _get_last_values(data: pd.DataFrame) -> Tuple[float, float]:
    """obtem os ultimos valores de tempo e de temperatura

    :param data: dados de temperatura por tempo
    :type data: pd.DataFrame
    :rtype: Tuple[float, float]
    """
    last_tempo = data['Tempo (s)'].to_numpy()[-1]
    last_temperatura = data['Temperatura (K)'].to_numpy()[-1]
    return last_temperatura, last_tempo


def _prepare_data(data: pd.DataFrame) -> Tuple[pd.DataFrame, ...]:
    """prepara dados para analise

    :param data: dados de temperatura por tempo
    :type data: pd.DataFrame
    """
    # excluir ultima medida, que usaremos para comparar a performance dos modelos
    tempo = data['Tempo (s)'].to_numpy()[:-1]
    temperatura = data['Temperatura (K)'].to_numpy()[:-1]

    # considerar que mudancas de temperatura ocorrem no meio do intervalo de tempo
    # para o qual a medida de temperatura foi a mesma
    tempo_intervall = np.diff(tempo)/2
    tempo_intervall = np.append(tempo_intervall, [67.5])
    tempo = tempo+tempo_intervall

    return temperatura, tempo, tempo_intervall


def analize_data(path: str):
    """analisa arquivo de dados e produz um resumo em formato markdown

    :param path:
    :type path: str
    """
    data = pd.read_excel(path)
    data = data.drop_duplicates(subset=['Temperatura (K)'])
    last_temperatura, last_tempo = _get_last_values(data)
    temperatura, tempo, tempo_intervall = _prepare_data(data)

    # ---------------------------------------------------------------------
    # graficos de ajustes nao-lineares

    _, ax1 = plt.subplots(1, 1)

    # considerar o intervalo de tempo com temperatura constante como incerteza
    ax1.errorbar(tempo, temperatura, yerr=0.5, xerr=tempo_intervall, fmt='o', elinewidth=1, capsize=3, capthick=1, ms=3, c='b', ecolor='black')
    ax1.set_ylabel('Temperatura (K)', fontsize=12)
    ax1.set_xlabel('Tempo (s)', fontsize=12)
    ax1.set_title(_generate_plot_tile(path, suffix='- Ajustes Não-Lineares'))
    ax1.tick_params(direction='in', which='both',
                    top=True, right=True, labelsize=12)
    plt.tight_layout()

    # plotar curvas dos dois modelos no mesmo grafico
    results_exp_cooling = _fit_exp_cooling(exp_cooling, tempo, temperatura)
    ax1.plot(tempo, results_exp_cooling.best_fit,
             label='Modelo de Condução ou Convecção Forçada')
    for m in VALORES_DE_M:
        results_cooling = _fit_cooling(cooling, tempo, temperatura, m)
        ax1.plot(tempo, results_cooling.best_fit, alpha=0.5,
                 label=f'Modelo de Convecção Natural, m={m}')
    ax1.legend(loc='best')

    # salvar o grafico obtido com nome semelhante ao do arquivo de dados
    ajustes_plot_path = os.path.join(
        'img', f"{path.split('/')[-1].split('.')[0]}_ajuste.png")
    plt.savefig(ajustes_plot_path, dpi=DPI)

    # ---------------------------------------------------------------------
    # graficos de ajuste linear

    _, ax2 = plt.subplots(1, 1)

    ax2.set_ylabel('Grandeza corr. a temperatura (u.a.)', fontsize=12)
    ax2.set_xlabel('Tempo (s)', fontsize=12)
    ax2.set_title(_generate_plot_tile(path, suffix='- Ajuste Linear'))
    ax2.tick_params(direction='in', which='both',
                    top=True, right=True, labelsize=12)
    plt.tight_layout()

    # linearizar apenas o modelo de melhor ajuste
    if results_exp_cooling.chisqr < results_cooling.chisqr:
        # linearização de exponencial
        ax2.plot(tempo, tempo*results_exp_cooling.params['gamma'].value,
                 label='Linearização do Modelo de Condução ou Convecção Forçada')
        ax2.errorbar(tempo, _linearize_exp(results_exp_cooling, temperatura), yerr=0.5/temperatura, xerr=tempo_intervall, fmt='o',
                     elinewidth=1, capsize=3, capthick=1, ms=3, c='b', ecolor='black')
    else:
        param_T0 = results_cooling.params['T0'].value
        param_m = results_cooling.params['m'].value
        a, b = _linearize_cooling(results_cooling)
        ax2.errorbar(tempo, (temperatura - param_T0)**((-1)/param_m), yerr=0.002,
                     xerr=tempo_intervall, fmt='o', elinewidth=1, capsize=3, capthick=1,
                     ms=3, c='b', ecolor='black', label='Dados Experimentais')
        ax2.plot(tempo, (a*tempo + b),
                 label='Linearização do Modelo de Convecção Natural')
    ax2.legend(loc='best')

    # salvar os graficos obtidos
    linear_plot_path = os.path.join(
        'img', f"{path.split('/')[-1].split('.')[0]}_linear.png")
    plt.savefig(linear_plot_path, dpi=DPI)

    # ---------------------------------------------------------------------
    # escrever resultados a um arquivo markdown para melhor legibilidade

    diff_squared_exp_cooling = (results_exp_cooling.eval(
        t=last_tempo) - last_temperatura)**2
    diff_squared_cooling = (results_cooling.eval(
        t=last_tempo) - last_temperatura)**2

    with open('report.md', 'a') as f:
        f.write('\n## ' + _generate_plot_tile(path, prefix='', suffix='' + '\n'))

        f.write('\n### Modelo 1 - ' + NOME_DO_MODELO[1] + '\n\n')
        f.write('Chi Square Test: ' + str(results_exp_cooling.chisqr) + '\n')
        f.write('Quadrado da Diferença da Previsão e do Modelo: ' +
                str(diff_squared_exp_cooling) + '\n')

        f.write('\n### Modelo 2 - ' + NOME_DO_MODELO[2] + '\n\n')
        f.write('Chi Square Test: ' + str(results_cooling.chisqr) + '\n')
        f.write('Quadrado da Diferença da Previsão e do Modelo: ' +
                str(diff_squared_cooling) + '\n')

        f.write('\n### Veredito\n\n')
        if results_exp_cooling.chisqr < results_cooling.chisqr:
            f.write(
                'O melhor Modelo foi o 1, pelo Teste de Associação (ou "do Chi-Quadrado")')
            if diff_squared_exp_cooling < diff_squared_cooling:
                f.write('e pelo Teste do Último Valor\n')
            else:
                f.write('\n')
        else:
            f.write(
                'O melhor Modelo foi o 2, pelo Teste de Associação ( ou "do Chi-Quadrado")')
            if diff_squared_cooling < diff_squared_exp_cooling:
                f.write(' e pelo Teste do Último Valor\n')
            else:
                f.write('\n')

        f.write('\n### Gráficos\n\n')
        f.write('| Ajuste não-linear | Ajuste linear |\n')
        f.write('| ----------------- | ------------- |\n')
        f.write(f'| ![]({ajustes_plot_path}) | ![]({linear_plot_path}) |\n')


if __name__ == "__main__":
    main()
