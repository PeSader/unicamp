# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 14:58:00 2020

@author: Christoph
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import lmfit

data = pd.read_excel('resfriamento_termometro.xlsx')

# excluir ultima medida, que usaremos para comparar a performance dos modelos
tempo = data['Tempo (s)'].to_numpy()[:-1]
temperatura = data['Temperatura (K)'].to_numpy()[:-1]

# considerar que mudancas de temperatura ocorrem no meio do intervalo de tempo
# para o qual a medida de temperatura foi constante
tempo_intervall = np.diff(tempo)/2
tempo_intervall = np.append(tempo_intervall, [67.5])
tempo = tempo+tempo_intervall

fig, ax1 = plt.subplots(1, 1)

# considerar o intervalo de tempo com temperatura constante como incerteza
ax1.errorbar(tempo, temperatura, yerr=0.5, xerr=tempo_intervall, fmt='o',
             elinewidth=1, capsize=3, capthick=1, ms=3, c='b', ecolor='black')

# configurar aparencia dos graficos
ax1.set_ylabel('Temperatura (K)', fontsize=12)
ax1.set_xlabel('Tempo (s)', fontsize=12)
plt.tight_layout()
ax1.tick_params(direction='in', which='both',
                top=True, right=True, labelsize=12)


def exp_cooling(t, T0, T_inf, gamma):
    """exp_cooling.

    :param t: tempo
    :param T0: temperatura inicial
    :param T_inf: temperatura infinita
    :param gamma: parametro que depende do coef. de transferencia de calor
    """
    return (T0-T_inf)*np.exp(-gamma*t)+T_inf


def cooling(t, T0, A, B, C, m):
    """cooling.

    :param t: tempo
    :param T0: temperatura inicial
    :param m: parametro inversamente proporcional ao coef. de transferencia de calor
    """
    return T0+(A/(B+C*t)**m)


exp_model = lmfit.Model(exp_cooling)

exp_model.set_param_hint('T0', value=350, min=340, max=370, vary=True)
exp_model.set_param_hint('T_inf', value=26+273.15,
                         min=20+273, max=30+273, vary=True)
exp_model.set_param_hint('gamma', value=0.001, min=0.0001, vary=True)
param = exp_model.make_params()

results = exp_model.fit(temperatura, t=tempo, params=param)
print(results.fit_report())

ax1.plot(tempo, results.best_fit)

cooling_model = lmfit.Model(cooling)
print('parameter names: {}'.format(cooling_model.param_names))
print('independent variables: {}'.format(cooling_model.independent_vars))

cooling_model.set_param_hint('m', value=1/4, vary=True, min=1/6, max=1/3)
cooling_model.set_param_hint('T0', value=350, vary=True)
cooling_model.set_param_hint('A', value=523, min=0.0001, vary=True)
cooling_model.set_param_hint('B', value=350, min=1, vary=True)
cooling_model.set_param_hint('C', value=11, min=1, vary=True)
param = cooling_model.make_params()

results = cooling_model.fit(temperatura, t=tempo, params=param)
print(results.fit_report())

ax1.plot(tempo, results.best_fit)
