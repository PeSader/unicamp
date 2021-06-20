# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 14:58:00 2020

@author: Christoph
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import lmfit

data = pd.read_csv('Al_form.csv')

tempo=data['C1'].to_numpy()[5:]
Temperature = data['C2'].to_numpy()[5:]+273.15

tempo_intervall=np.diff(tempo)/2
tempo_intervall=np.append(tempo_intervall,[67.5])

tempo=tempo+tempo_intervall

fig,ax1 = plt.subplots(1,1)

ax1.errorbar(tempo,Temperature,yerr=0.5,xerr=tempo_intervall,fmt='o',elinewidth=1,capsize=3,capthick=1,ms=3,c='b',ecolor='black')

ax1.tick_params(direction='in', which='both',top=True,right=True,labelsize=12)

#ax1.legend(fontsize='small')
ax1.set_ylabel('Temperature (K)',fontsize=12)
ax1.set_xlabel('Time (s)',fontsize=12)
#ax1.set_ylim(0.2,3.5)
#ax1.set_xlim(0,0.75)

plt.tight_layout()
# plt.show()

def exp_cooling(t,T0,T_inf,gamma):
    return (T0-T_inf)*np.exp(-gamma*t)+T_inf

def cooling(t,T0,A,B,C,m):
    return T0+(A/(B+C*t)**m)


def exp_cooling(t,T0,T_inf,gamma):
    return (T0-T_inf)*np.exp(-gamma*t)+T_inf

exp_model=lmfit.Model(exp_cooling)

exp_model.set_param_hint('T0',value=350,min=340,max=370,vary=True)
exp_model.set_param_hint('T_inf',value=26+273.15,min=20+273,max=30+273,vary=True)
exp_model.set_param_hint('gamma',value=0.001,min=0.0001,vary=True)
param = exp_model.make_params()

results = exp_model.fit(Temperature, t = tempo, params= param)
print(results.fit_report())

ax1.plot(tempo,results.best_fit)

cooling_model=lmfit.Model(cooling)
print('parameter names: {}'.format(cooling_model.param_names))
print('independent variables: {}'.format(cooling_model.independent_vars))

cooling_model.set_param_hint('m',value=1/4,vary=True,min=1/6, max=1/3)
cooling_model.set_param_hint('T0',value=350,vary=True)
cooling_model.set_param_hint('A',value=523,min=0.0001, vary=True)
cooling_model.set_param_hint('B',value=350,min=1,vary=True)
cooling_model.set_param_hint('C',value=11,min=1,vary=True)
param = cooling_model.make_params()

results = cooling_model.fit(Temperature, t = tempo, params= param)
print(results.fit_report())

ax1.plot(tempo,results.best_fit)

