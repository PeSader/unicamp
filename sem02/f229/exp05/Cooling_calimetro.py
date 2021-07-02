# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 14:58:00 2020

@author: Christoph
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import lmfit

data = pd.read_csv('cal_alberto.csv')

tempo = data['C1'].to_numpy()[:28]
Temperature = data['C3'].to_numpy()[:28]

# tempo_intervall=np.diff(tempo)/2
# tempo_intervall=np.append(tempo_intervall,[67.5])

# tempo=tempo+tempo_intervall

fig, ax1 = plt.subplots(1, 1)

ax1.errorbar(tempo, Temperature, yerr=0.2, xerr=5, fmt='o',
             elinewidth=1, capsize=3, capthick=1, ms=3, c='b', ecolor='black')

ax1.tick_params(direction='in', which='both',
                top=True, right=True, labelsize=12)


ax1.set_ylabel('Temperature (K)', fontsize=12)
ax1.set_xlabel('Time (s)', fontsize=12)
# ax1.set_ylim(0.2,3.5)
# ax1.set_xlim(0,0.75)


def cooling(t, A, B, C, m):
    return (A/(B+C*t)**m)


def exp_cooling(t, delta, gamma):
    return delta*np.exp(-gamma*t)


exp_model = lmfit.Model(exp_cooling)

exp_model.set_param_hint('delta', value=70, min=71, max=69, vary=True)
# exp_model.set_param_hint(,value=26+273.15,min=20+273,max=30+273,vary=True)
exp_model.set_param_hint('gamma', value=0.001, min=0.0001, vary=True)
param = exp_model.make_params()

results = exp_model.fit(Temperature, t=tempo, params=param)
print(results.fit_report())

ax1.plot(tempo, results.best_fit, label="Exponetial")

cooling_model = lmfit.Model(cooling)
print('parameter names: {}'.format(cooling_model.param_names))
print('independent variables: {}'.format(cooling_model.independent_vars))

cooling_model.set_param_hint('m', value=3, vary=False, min=3, max=6)
# cooling_model.set_param_hint('T0',value=300,min=273,max=350,vary=True)
cooling_model.set_param_hint('A', value=68, min=0.0001, vary=True)
cooling_model.set_param_hint('B', value=1, min=1, vary=False)
cooling_model.set_param_hint('C', value=0.00229893, min=0.0001, vary=True)
param = cooling_model.make_params()

results = cooling_model.fit(Temperature, t=tempo, params=param)
print(results.fit_report())

ax1.plot(tempo, results.best_fit, label="m=3")

cooling_model.set_param_hint('m', value=4, vary=False, min=3, max=6)
# cooling_model.set_param_hint('T0',value=300,min=273,max=350,vary=True)
cooling_model.set_param_hint('A', value=68, min=0.0001, vary=True)
cooling_model.set_param_hint('B', value=1, min=1, vary=False)
cooling_model.set_param_hint('C', value=0.00229893, min=0.0001, vary=True)
param = cooling_model.make_params()

results = cooling_model.fit(Temperature, t=tempo, params=param)
print(results.fit_report())

ax1.plot(tempo, results.best_fit, label="m=4")

cooling_model.set_param_hint('m', value=6, vary=False, min=3, max=6)
# cooling_model.set_param_hint('T0',value=300,min=273,max=350,vary=True)
cooling_model.set_param_hint('A', value=68, min=0.0001, vary=True)
cooling_model.set_param_hint('B', value=1, min=1, vary=False)
cooling_model.set_param_hint('C', value=0.00229893, min=0.0001, vary=True)
param = cooling_model.make_params()

results = cooling_model.fit(Temperature, t=tempo, params=param)
print(results.fit_report())

ax1.plot(tempo, results.best_fit, label="m=6")

plt.tight_layout()
plt.show()

ax1.legend(fontsize='small')

