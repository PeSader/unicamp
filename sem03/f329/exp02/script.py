import math
import os
from typing import Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from uncertainties import ufloat
mpl.rc('font', size=14)

# configuracoes
DPI = 500
FILENAME = 'data.csv'
IMG_FOLDER = 'img'
DATA_FOLDER = 'data'

# dados
NUMERO_DE_ESPIRAS = 140
RAIO_BOBINA = ufloat(10.65E-2, 0.06E-2, "R")
COMPRIMENTO_IMA = ufloat(1.25E-2, 0.02E-2, "L")
RAIO_IMA = ufloat(0.3E-2, 0.02E-2, "r")
MASSA_IMA = ufloat(5.15E-3, 0.03E-3, "m")
MOMENTO_DE_INERCIA_IMA = (MASSA_IMA/12)*(3*RAIO_IMA**2 + COMPRIMENTO_IMA**2)
PERMEABILIDADE_MAGNETICA = 4*math.pi*10**(-7)


def uncertainty_components(n: ufloat):
    for var, error in n.error_components().items():
        print(f"{var.tag}: {error}")


def momento_magnetico_ima(A,
                          mI=MOMENTO_DE_INERCIA_IMA,
                          R=RAIO_BOBINA,
                          mu0=PERMEABILIDADE_MAGNETICA,
                          N=NUMERO_DE_ESPIRAS):
    return ((4*math.pi**2)*mI*5**(3/2)*R*A)/(8*mu0*N)


def campo_magnetico_terra(C,
                          mu,
                          mI=MOMENTO_DE_INERCIA_IMA):
    return ((4*math.pi**2)*mI*C)/mu


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


def main():
    filepath = os.path.join(DATA_FOLDER, FILENAME)
    df = pd.read_csv(filepath)
    df['frequencia ao quadrado'] = df['frequencia']**2
    df['periodo'] = df['frequencia']**(-1)
    df['incerteza'] = 0.018*df['periodo']**(-3)
    # df.to_excel(os.path.join(DATA_FOLDER, 'data.xlsx'),
    # encoding='utf-8', index=False)

    x = df['corrente'].to_numpy()
    y = df['frequencia ao quadrado'].to_numpy()
    err = df['incerteza'].to_numpy()

    _, ax1 = plt.subplots(1, 1, figsize=[8, 5])
    ax1.set_ylabel('Inverso do período ao quadrado ($s^{-1}$)', fontsize=12)
    ax1.set_xlabel('Corrente ($10^{-3}A$)', fontsize=12)
    ax1.set_title('Linearização de Período de Oscilação por Corrente Elétrica')
    plt.tight_layout()

    min_index = np.where(y == np.amin(y))[0][0]
    print(f"xmin = {x[min_index]}")
    print(f"ymin = {y[min_index]}")
    yerr = np.mean(err)

    x_decres = x[min_index:]
    y_decres = y[min_index:]
    a_decres, c_decres = np.polyfit(x_decres, y_decres, 1)
    print(f"a_decres = {a_decres}")
    print(f"c_decres = {c_decres}")
    ax1.plot(x_decres, (a_decres*x_decres + c_decres),
             label="$B_{bobina} > B_{Terra}$")
    a, b = regressao_linear(x_decres, y_decres, yerr)
    momento_magnetico_ima_decres = momento_magnetico_ima(A=a)
    print(f"momento_magnetico_ima_decres = {momento_magnetico_ima_decres}")
    mu = ((4*math.pi**2)*MOMENTO_DE_INERCIA_IMA*5**(3/2)*RAIO_BOBINA*a) / \
        (8*PERMEABILIDADE_MAGNETICA*NUMERO_DE_ESPIRAS)
    campo_magnetico_terra_decres = campo_magnetico_terra(C=b,
                                                         mu=mu)
    print(f"campo_magnetico_terra_decres = {campo_magnetico_terra_decres}")

    x_cres = x[:min_index+1]
    y_cres = y[:min_index+1]
    a_cres, c_cres = np.polyfit(x_cres, y_cres, 1)
    print(f"a_cres = {a_cres}")
    print(f"c_cres = {c_cres}")
    ax1.plot(x_cres, (a_cres*x_cres + c_cres),
             label="$B_{bobina} < B_{Terra}$")
    a, b = regressao_linear(x_cres, y_cres, yerr)
    momento_magnetico_ima_cres = momento_magnetico_ima(A=a)
    print(f"momento_magnetico_ima_cres = {momento_magnetico_ima_cres}")
    mu = ((4*math.pi**2)*MOMENTO_DE_INERCIA_IMA*5**(3/2)*RAIO_BOBINA*a) / \
        (8*PERMEABILIDADE_MAGNETICA*NUMERO_DE_ESPIRAS)
    campo_magnetico_terra_cres = campo_magnetico_terra(C=b,
                                                         mu=mu)
    print(f"campo_magnetico_terra_cres = {campo_magnetico_terra_cres}")

    ax1.errorbar(x, y, xerr=0.2, yerr=err, ls='none', fmt='o', elinewidth=1,
                 capsize=2, capthick=1, markersize=3, color='black', ecolor='black')

    print(np.size(x_decres))
    print(np.size(x_cres))
    ax1.legend(loc='best')
    # plt.savefig(os.path.join(IMG_FOLDER, 'plot.png'), dpi=DPI)


if __name__ == "__main__":
    main()
