import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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


def prefixo_ampere(filename: str):
    if '10' in filename:
        return ''
    if 'mili' in filename:
        return 'm'
    if 'micro' in filename:
        return '\\mu'


def incerteza_corrente(corr: float, escala: float) -> float:
    """calcula a incerteza associada a uma medida de corrente

    :param corr: medida nominal de corrente
    :param escala: escala utilizada pelo amperimetro
    """
    # incerteza de calibração, com base no manual do medidor
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

    ucorr_cal = a/(2*(3**(1/2)))  # fdp retangular

    # incerteza de leitura


def incerteza_tensao(tens: float, escala: float = 1) -> float:
    """calcula a incerteza associada a uma medida de tensao

    :param tens: medida nominal de tensao
    :param escala: escala utilizada pelo voltimetro
    """
    if tens < 6:
        utens = tens*0.006 + 2*0.1e-3
    elif tens < 1000:
        utens = 0.003*tens
        if tens < 60:
            utens += 2*0.001
        elif tens < 600:
            utens += 2*0.01
        elif tens < 1000:
            utens += 2*0.1
    else:
        utens = 0.005*tens + 3*1
    return utens/(2*(3**(1/2)))  # fdp retangular


for f in FILENAMES:
    df = pd.read_csv(os.path.join(DATA_DIR, f))
    df = df.drop_duplicates(subset=['Tensão do amperímetro (v)'])

    if 'amperimetro' in f:
        x = df['Tensão do amperímetro (v)']
        y = df['Corrente']*fundo_de_escala(f)

        # criar colunas de incerteza
        # df['Incerteza de Tensão'] = (x*0.003 + 0.002)/(2*(3**(1/2)))
        df['Incerteza de Tensão'] = x.apply(incerteza_tensao,
                                            args=(fundo_de_escala(f),))
        ux = df['Incerteza de Tensão']
        df['Incerteza de Corrente'] = y.apply(incerteza_corrente,
                                              args=(fundo_de_escala(f),))
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
        ax.plot(x, a*x + b, color='black', alpha=0.5)
        plt.show()

        print(f)
        print(f'resistencia: {1/a}')
        print(f'coeficiente angular: {a}')
        print(f'coeficiente linear:  {b}\n')

        # salvar figura
        fig.savefig(os.path.join(IMG_DIR, f.replace('csv', 'png')))
