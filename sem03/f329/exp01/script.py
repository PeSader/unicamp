import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os
mpl.rc('font', size=14)

DPI = 200
FILENAME = 'video04_simetria.csv'
IMG_FOLDER = 'img'
INCERTEZA_ABSOLUTA = 0.022
INCERTEZA_RELATIVA = 0.003

filepath = os.path.join('data', FILENAME)

df = pd.read_csv(filepath)
df['Tensão (V)'] = df['Tensão (V)'] / 1000
df['Incerteza'] = (((df['Tensão (V)'] * INCERTEZA_RELATIVA) /
                    3**(1/2))**2 + INCERTEZA_ABSOLUTA**2)**(1/2)

tens = df.pivot(index='y', columns='Experimento', values='Tensão (V)')
errors = df.pivot(index='y', columns='Experimento', values='Incerteza')

print("TENSÕES\n", tens)
print("INCERTEZAS\n", errors)

fig, ax = plt.subplots(1, 1, figsize=[10, 8])
for k in tens:
    ax.errorbar(tens[k].index, tens[k].values, yerr=errors[k].values, xerr=0.1,
                linestyle='none', linewidth=0.8, elinewidth=1, capsize=1.5,
                capthick=1, ms=3, label=k)
plt.yticks(np.arange(0, 5, 0.5))
ax.tick_params(direction='in', which='both',
               top=True, right=True, labelsize=12)
ax.set_title("Tensões de Campo Elétrico em seu Eixo de Simetria")
ax.set_ylabel("Tensão (V)")
ax.set_xlabel("Posição da ponteira (cm)")
ax.legend(loc='best')
plt.tight_layout()
plt.savefig(os.path.join(IMG_FOLDER, 'simetria.png'), dpi=DPI)
