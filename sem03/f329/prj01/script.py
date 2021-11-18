import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import math
from uncertainties import ufloat

import matplotlib as mpl
mpl.rc('font', size=15)

DPI = 100
DATA_DIR = 'data'
IMG_DIR = 'img'
ADICIONAL_SUPERIOR = 14.86e-1      # centimetros
ADICIONAL_INFERIOR = 144.75e-1     # centimetros
ADICIONAL_PERPENDICULAR = ADICIONAL_SUPERIOR     # centimetros
B_TERRA = 22                       # microtesla
PERMEABILIDADE_MAGNETICA = 1.2566  # microtesla*metro/A
COLUNA_DIST = 'distância (m)'

tables = []
fig1, ax1 = plt.subplots(1, 1, figsize=[8, 5])
fig2, ax2 = plt.subplots(1, 1, figsize=[8, 5])

ax1.set_title("Intensidade de Campo Magnético (μT) por distancia (m)")
ax1.set_xlabel("Distância (m)")
ax1.set_ylabel("Intensidade do Campo Magnético (μT)")

ax2.set_title("Linearização da Lei de Potência")
ax2.set_xlabel("X")
ax2.set_ylabel("Y(X)")


for d in os.listdir(DATA_DIR):
    list_y = []
    list_By = []
    list_linBy = []
    if 'perpendicular' in d or ('superior' in d and 'ida' in d):
        if 'superior' in d:
            label = f"{d.split('_')[0]} na {d.split('_')[1]}"
        else:
            label = 'perpendicular'
        files = os.listdir(os.path.join(DATA_DIR, d))

        for f in files:
            print(d, f)
            path = os.path.join(DATA_DIR, d, f)
            df = pd.read_csv(path, delimiter=';', decimal=',')  # dataframe

            # o nome do arquivo e a distancia ao celular
            y = float(f.split('.')[0].split(' ')[0].replace(',', '.'))
            if 'superior' in d:
                y += ADICIONAL_SUPERIOR
            if 'perpendicular' in d:
                y += ADICIONAL_PERPENDICULAR

            # usar as amostras com o menor valor absoluto de Bx
            df['Bx'] = df['Bx'].abs()
            df['Bz'] = df['Bz'].abs()
            df['BxBz'] = (df['Bx']**2 + df['Bz']**2) ** (1/2)

            # ajustar medidas com relacao ao campo magnetico da Terra
            if 'ida' in d:
                df['BT'] = (df['BT'] - B_TERRA).abs()
            if 'volta' in d:
                df['BT'] = (B_TERRA - df['BT']).abs()

            Bt = df.nsmallest(1, 'BxBz')['BT'].array[0]

            # escrever valores de y, Bt, em um vetor
            list_y.append(y)
            list_By.append(Bt)

        coluna_Bt = f'intensidade do campo magnético {label} (μT)'

        data = {COLUNA_DIST: list_y,
                coluna_Bt: list_By,
                }
        table = pd.DataFrame(data).sort_values(by=COLUNA_DIST)
        table[COLUNA_DIST] = (table[COLUNA_DIST].round(1))/100

        # incertezas
        table['uy_lin'] = 0.001/table[COLUNA_DIST]
        table['uB_lin'] = 0.020/(table[coluna_Bt])

        # grafico de dados brutos
        ax1.errorbar(table[COLUNA_DIST], table[coluna_Bt], ls='none', fmt='o',
                     elinewidth=1, capsize=2, capthick=1, markersize=3, label=label,
                     xerr=0.002, yerr=0.04)
        plt.show()

    if 'perpendicular' not in d:
        label = f"{d.split('_')[0]} na {d.split('_')[1]}"
        files = os.listdir(os.path.join(DATA_DIR, d))

        for f in files:
            path = os.path.join(DATA_DIR, d, f)
            df = pd.read_csv(path, delimiter=';', decimal=',')  # dataframe

            # o nome do arquivo e a distancia ao celular
            y = float(f.split('.')[0].split(' ')[0].replace(',', '.'))
            if 'superior' in d:
                y += ADICIONAL_SUPERIOR
            if 'inferior' in d:
                y += ADICIONAL_INFERIOR

            # usar as amostras com o menor valor absoluto de Bx
            df['Bx'] = df['Bx'].abs()
            df['Bz'] = df['Bz'].abs()
            df['BxBz'] = (df['Bx']**2 + df['Bz']**2) ** (1/2)

            # ajustar medidas com relacao ao campo magnetico da Terra
            if 'ida' in d:
                df['BT'] = (df['BT'] - B_TERRA).abs()
            if 'volta' in d:
                df['BT'] = (B_TERRA - df['BT']).abs()

            Bt = df.nsmallest(1, 'BxBz')['BT'].array[0]
            line = df.nsmallest(1, 'BxBz')['BT']

            # escrever valores de y, Bt, em um vetor
            list_y.append(y)
            list_By.append(Bt)

        coluna_Bt = f'intensidade do campo magnético {label} (μT)'

        data = {COLUNA_DIST: list_y,
                coluna_Bt: list_By,
                }
        table = pd.DataFrame(data).sort_values(by=COLUNA_DIST)
        table[COLUNA_DIST] = (table[COLUNA_DIST].round(1))/100

        # remoção de dados espurios
        # if 'superior' in d and 'ida' in d:
        #     table = table.iloc[2:]

        # incertezas
        table['uy_lin'] = 0.001/table[COLUNA_DIST]
        table['uB_lin'] = 0.020/(table[coluna_Bt])

        # grafico de dados brutos
        ax1.errorbar(table[COLUNA_DIST], table[coluna_Bt], ls='none', fmt='o',
                     elinewidth=1, capsize=2, capthick=1, markersize=3, label=label,
                     xerr=0.002, yerr=0.04)

        # grafico de dados linearizados
        x = np.log10(table[COLUNA_DIST] * 2*np.pi)
        y = np.log10(table[coluna_Bt])
        print(d)
        print(y)

        ax2.errorbar(np.log10(table[COLUNA_DIST] * 2*np.pi),
                     np.log10(table[coluna_Bt]), label=label,
                     ls='none', fmt='o', elinewidth=1, capsize=2, capthick=1,
                     markersize=3, xerr=table['uy_lin'], yerr=table['uB_lin'])

        a, c = np.polyfit(x, y, 1)
        l = np.arange(0, 7)
        ax2.plot(x, a*x + c, color='black', alpha=0.5)
        m = (10 ** c)/PERMEABILIDADE_MAGNETICA
        print(m)

ax2.legend()
ax1.legend()
plt.tight_layout()

# fig2.savefig(os.path.join(IMG_DIR, 'dados_linearizados.png'), dpi=DPI)
fig1.savefig(os.path.join(IMG_DIR, 'dados_brutos.png'), dpi=DPI)
