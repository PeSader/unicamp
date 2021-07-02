# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 14:58:00 2020

@author: Christoph
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import lmfit
import os
from uncertainties import ufloat
from typing import Tuple

DPI = 1200
DATA_DIR = './data'
FILENAMES = os.listdir(DATA_DIR)
PREFIXO_TITULO_GRAFICO = 'Resfriamento de '
VALORES_DE_M = [3, 4, 5, 6]
NOME_DO_MODELO = {1: 'Condução e Convecção Forçada',
                  2: 'Convecção Natural'}


def exp_cooling(t, T0, T_inf, gamma):
    """Modelo para transferencia de calor por conducao ou conveccao forcada

    :param t: tempo
    :param T0: temperatura inicial
    :param T_inf: temperatura infinita
    :param gamma: parametro que depende do coef. de transferencia de calor
    """
    return (T0-T_inf)*np.exp(-gamma*t)+T_inf


def cooling(t, T0, A, B, C, m):
    """Modelo para transferencia de calor por conveccao natural

    :param t: tempo
    :param T0: temperatura inicial
    :param m: parametro inversamente proporcional ao coef. de transferencia de calor
    """
    return T0+(A/(B+C*t)**m)


def main():
    with open('report.md', 'w') as f:
        f.write('# Documento Auxiliar ao Relatório 5\n\n')
    for f in FILENAMES:
        analisar_dados(f'./data/{f}')


def generate_plot_tile(path: str, prefix: str = PREFIXO_TITULO_GRAFICO, suffix: str = "") -> str:
    title = prefix
    for w in path.split('/')[-1].split('.')[0].split('_'):
        if len(w) > 3:
            title += f'{w.capitalize()} '
        else:
            title += f'{w} '
    title += suffix
    return title


def analisar_dados(path: str):

    data = pd.read_excel(path)

    # desconsiderar medidas repetidas de temperatura
    data = data.drop_duplicates(subset=['Temperatura (K)'])

    # armazenar ultimas medidas de tempo e de temperatura
    last_tempo = data['Tempo (s)'].to_numpy()[-1]
    last_temperatura = data['Temperatura (K)'].to_numpy()[-1]

    # excluir ultima medida, que usaremos para comparar a performance dos modelos
    tempo = data['Tempo (s)'].to_numpy()[:-1]
    temperatura = data['Temperatura (K)'].to_numpy()[:-1]

    # considerar que mudancas de temperatura ocorrem no meio do intervalo de tempo
    # para o qual a medida de temperatura foi constante
    tempo_intervall = np.diff(tempo)/2
    tempo_intervall = np.append(tempo_intervall, [67.5])
    tempo = tempo+tempo_intervall

    _, ax1 = plt.subplots(1, 1)

    # considerar o intervalo de tempo com temperatura constante como incerteza
    ax1.errorbar(tempo, temperatura, yerr=0.5, xerr=tempo_intervall, fmt='o',
                 elinewidth=1, capsize=3, capthick=1, ms=3, c='b', ecolor='black')

    # configurar aparencia dos graficos
    ax1.set_ylabel('Temperatura (K)', fontsize=12)
    ax1.set_xlabel('Tempo (s)', fontsize=12)
    ax1.set_title(generate_plot_tile(path, suffix='- Ajustes Não-Lineares'))
    plt.tight_layout()
    ax1.tick_params(direction='in', which='both',
                    top=True, right=True, labelsize=12)

    exp_model = lmfit.Model(exp_cooling)

    exp_model.set_param_hint('T0', value=350, min=340, max=370, vary=True)
    exp_model.set_param_hint('T_inf', value=26+273,
                             min=20+273, max=30+273, vary=True)
    exp_model.set_param_hint('gamma', value=0.001, min=0.0001, vary=True)
    param = exp_model.make_params()

    results_exp_cooling = exp_model.fit(temperatura, t=tempo, params=param)
    print(results_exp_cooling.fit_report())

    ax1.plot(tempo, results_exp_cooling.best_fit,
             label='Modelo de Condução ou Convecção Forçada')

    cooling_model = lmfit.Model(cooling)
    print('parameter names: {}'.format(cooling_model.param_names))
    print('independent variables: {}'.format(cooling_model.independent_vars))

    cooling_model.set_param_hint('T0', value=300, min=273,
                                 max=350, vary=True)
    cooling_model.set_param_hint('A', value=68, min=0.0001, vary=True)
    cooling_model.set_param_hint('B', value=1, min=1, vary=False)
    cooling_model.set_param_hint(
        'C', value=0.00229893, min=0.0001, vary=True)

    for m in VALORES_DE_M:
        cooling_model.set_param_hint('m', value=m, vary=False,
                                     min=min(VALORES_DE_M), max=max(VALORES_DE_M))
        param = cooling_model.make_params()

        results_cooling = cooling_model.fit(temperatura, t=tempo, params=param)
        print(results_cooling.fit_report())
        ax1.plot(tempo, results_cooling.best_fit, alpha=0.5,
                 label=f'Modelo de Convecção Natural, m={m}')

    # ax1.legend(['Modelo 1', 'Modelo 2', 'Dados experimentais'])
    ax1.legend(loc='best')

    ajustes_plot_path = os.path.join(
        'img', f"{path.split('/')[-1].split('.')[0]}_ajuste.png")
    plt.savefig(ajustes_plot_path, dpi=DPI)

    diff_squared_exp_cooling = (results_exp_cooling.eval(
        t=last_tempo) - last_temperatura)**2
    diff_squared_cooling = (results_cooling.eval(
        t=last_tempo) - last_temperatura)**2

    _, ax2 = plt.subplots(1, 1)
    ax2.set_ylabel('Grandeza corr. a temperatura (u.a.)', fontsize=12)
    ax2.set_xlabel('Tempo (s)', fontsize=12)
    ax2.set_title(generate_plot_tile(path, suffix='- Ajuste Linear'))
    plt.tight_layout()
    ax2.tick_params(direction='in', which='both',
                    top=True, right=True, labelsize=12)

    def linearizar_exp(results, temperatura):
        param_T0 = results.params['T0'].value
        param_Tinf = results.params['T_inf'].value
        y = np.log((temperatura - param_Tinf) /
                   (param_T0 - param_Tinf))*(-1)
        return y

    if results_exp_cooling.chisqr < results_cooling.chisqr:
        # linearização de exponencial
        ax2.plot(tempo, tempo*results_exp_cooling.params['gamma'].value,
                 label='Linearização do Modelo de Condução ou Convecção Forçada')
        ax2.errorbar(tempo, linearizar_exp(results_exp_cooling, temperatura), yerr=0.5/temperatura, xerr=tempo_intervall, fmt='o',
                     elinewidth=1, capsize=3, capthick=1, ms=3, c='b', ecolor='black')
    elif results_cooling.chisqr < results_exp_cooling.chisqr:
        param_A = results_cooling.params['A'].value
        param_B = results_cooling.params['B'].value
        param_C = results_cooling.params['C'].value
        param_m = results_cooling.params['m'].value
        param_T0 = results_cooling.params['T0'].value

        a = param_C/(param_A**(1/param_m))  # coefieciente angular
        b = param_B/(param_A**(1/param_m))  # coefieciente linear
        # y = (results_cooling.best_fit - param_T0)**(-1/param_m)
        ax2.errorbar(tempo, (temperatura - param_T0)**((-1)/param_m), yerr=0.002, xerr=tempo_intervall, fmt='o',
                     elinewidth=1, capsize=3, capthick=1, ms=3, c='b', ecolor='black', label='Dados Experimentais')
        ax2.plot(tempo, (a*tempo + b),
                 label='Linearização do Modelo de Convecção Natural')

    ax2.legend(loc='best')
    linear_plot_path = os.path.join(
        'img', f"{path.split('/')[-1].split('.')[0]}_linear.png")
    plt.savefig(linear_plot_path, dpi=DPI)

    # escrever resumo dos resultados em um documento md
    with open('report.md', 'a') as f:
        f.write('\n## ' + generate_plot_tile(path, prefix='', suffix='' + '\n'))

        f.write('\n### Modelo 1 - ' + NOME_DO_MODELO[1] + '\n\n')
        f.write('Chi Square Test: ' + str(results_exp_cooling.chisqr) + '\n')
        f.write('Quadrado da Diferença da Previsão e do Modelo: ' +
                str(diff_squared_exp_cooling) + '\n')

        f.write('\n### Modelo 2 - ' + NOME_DO_MODELO[2] + '\n\n')
        f.write('Chi Square Test: ' + str(results_cooling.chisqr) + '\n')
        f.write('Quadrado da Diferença da Previsão e do Modelo: ' +
                str(diff_squared_cooling) + '\n')

        f.write('\n### Gráfico\n\n')
        f.write(f'![]({ajustes_plot_path})\n')

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


if __name__ == "__main__":
    main()
