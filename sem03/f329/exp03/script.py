import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from uncertainties import ufloat

# configuracoes
DPI = 200
IMG_DIR = 'img'
DATA_DIR = 'data'
FILENAMES = os.listdir(DATA_DIR)

# dados


def fundo_de_escala(filename: str):
    if '10' in filename:
        return 10
    if 'mili' in filename:
        return 1e-3
    if 'micro' in filename:
        return 1e-6


def multiplicador_ampere(filename: str):
    if '10' in filename:
        return r'10'
    if 'mili' in filename:
        return r'm'
    if 'micro' in filename:
        return r'$\mu$'


def gerar_titulo_grafico(filename: str, prefix: str = '', suffix: str = ''):
    title = prefix
    m = multiplicador_ampere(filename)
    if 'amperimetro' in filename:
        title += f'Curva característica do amperímetro (fundo de escala = {m}A)'
    title += suffix
    return title


def incerteza_corrente_cal(corr: float) -> float:
    """calcula a incerteza de calibração associada a uma medida de corrente

    :param corr: medida nominal de corrente
    """
    if corr < 600e-3:
        a = corr*0.005
        if corr < 6000e-6:
            a += 3*0.1e-6
        elif corr < 60e-3:
            a += 3*1e-6
        elif corr < 600e-3:
            a += 3*0.01e-3
    elif corr < 10:
        a = corr*0.008 + 3*0.1e-3
    else:
        a = corr*0.012 + 3*10e-3

    return a/(2*(3**(1/2)))  # fdp retangular


def incerteza_tensao_cal(tens: float) -> float:
    """calcula a incerteza de calibração associada a uma medida de tensao

    :param tens: medida nominal de tensao
    """
    if tens < 6:
        a = tens*0.006 + 2*0.1e-3
    elif tens < 1000:
        a = 0.003*tens
        if tens < 60:
            a += 2*0.001
        elif tens < 600:
            a += 2*0.01
        elif tens < 1000:
            a += 2*0.1
    else:
        a = 0.005*tens + 3*1

    return a/(2*(3**(1/2)))  # fdp retangular


for f in FILENAMES:
    df = pd.read_csv(os.path.join(DATA_DIR, f))
    df = df.drop_duplicates(subset=['Tensão do amperímetro (v)'])

    if 'amperimetro' in f and 'tratado' not in f:
        x = df['Tensão do amperímetro (v)']
        y = df['Corrente']*fundo_de_escala(f)

        # criar colunas de incerteza
        df['Incerteza de cal de Tensão'] = x.apply(incerteza_tensao_cal)
        df['Incerteza de ltr de Tensão'] = 0.001/(2*(3**(1/2)))
        df['Incerteza de Tensão'] = (df['Incerteza de cal de Tensão']**2 +
                                     df['Incerteza de ltr de Tensão']**2)**(1/2)

        df['Incerteza de cal de Corrente'] = y.apply(incerteza_corrente_cal)
        df['Incerteza de ltr de Corrente'] = df['Menor dígito']/(2*(3**(1/2)))
        df['Incerteza de Corrente'] = (df['Incerteza de cal de Corrente']**2 +
                                       df['Incerteza de ltr de Corrente']**2)**(1/2)

        df.to_csv(os.path.join(DATA_DIR, f'tratado_{f}'))

        ux = df['Incerteza de Tensão']
        uy = df['Incerteza de Corrente']

        # tratar dados
        if 'micro' in f:
            # remover dados nao lineares
            y = y[:4]
            x = x[:4]
            ux = ux[:4]
            uy = uy[:4]

            # remover dados abaixo do menor fundo de escala
            y = y[2:]
            x = x[2:]
            ux = ux[2:]
            uy = uy[2:]

        # plotar pontos experimentais
        fig, ax = plt.subplots(1, 1)
        ax.errorbar(x, y, xerr=ux, yerr=uy, fmt='o',
                    elinewidth=2, capthick=2, ms=3)

        # plotar regressao linear
        a, b = np.polyfit(x, y, 1)
        # p, cov = np.polyfit(x, y, 1, cov=True)
        ax.plot(x, a*x + b, color='black', alpha=0.5)

        # configurações do plot
        ax.set_title(gerar_titulo_grafico(f))
        ax.set_ylabel("Corrente (A)")
        ax.set_xlabel("Tensão (v)")
        plt.tight_layout()
        # plt.show()

        print(f)
        print(f'resistencia: {1/a}')
        print(f'coeficiente angular: {a}')
        print(f'coeficiente linear:  {b}\n')
        # print(np.sqrt(np.diag(cov)))

        # calcular incerteza dos coeficientes
        n = len(x)
        sum_x = np.sum(x)
        sum_y = np.sum(y)
        yerror = df['Incerteza de Corrente'].mean()

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
        incerteza_coef_angular = np.sqrt(n/delta)*yerror

        coef_linear = (sum_y*sum_x_squared - sum_xy*sum_x)/delta
        incerteza_coef_linear = np.sqrt(sum_x_squared/delta)*yerror

        print(f'coef angular = {coef_angular} ± {incerteza_coef_angular}')
        print(f'coef linear = {coef_linear} ± {incerteza_coef_linear}')

        a = ufloat(coef_angular, incerteza_coef_angular)
        b = ufloat(coef_linear, incerteza_coef_linear)

        print(f'resistência = {1/a}')
        print(f'indicativo de qualidade = {1/b}')

        # salvar figura
        fig.savefig(os.path.join(IMG_DIR, f.replace('csv', 'png')))
