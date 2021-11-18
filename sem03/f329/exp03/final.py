import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from uncertainties import ufloat

# configuracoes
DPI = 200
IMG_DIR = 'img'
DATA_DIR = 'data/dispositivos'
FILENAMES = os.listdir(DATA_DIR)

# dados
MELHOR_CIRCUITO = 'b'


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
    # print(f)
    # print(df)

    # ajuste de unidade de medida
    if 'resistor' in f:
        if 'a' in f:
            df['Corrente (A)'] = df['Corrente (miliA)']*10
            df['Menor dígito'] = df['Menor dígito']*10
            df['Resistencia (ohm)'] = (
                df['Tensão (v)']/df['Corrente (A)'])*10000
            # df = df[df['Resistencia (ohm)'] < 110]
            # df = df[df['Resistencia (ohm)'] > 90]
        elif 'b' in f:
            df['Corrente (A)'] = df['Corrente (miliA)']*10
            df['Menor dígito'] = df['Menor dígito']*10
            df['Resistencia (ohm)'] = (
                df['Tensão (v)']/df['Corrente (A)'])*10
            df['Tensão (v)'] = df['Tensão (v)']/1000

    if 'diodo' in f:
        df['Corrente (A)'] = df['Corrente (microA)']/1e6
        df['Menor dígito'] = df['Menor dígito']/1e6
        df['Resistencia (ohm)'] = (df['Tensão (v)']/df['Corrente (A)'])*10000
        df.loc[df['Corrente (A)'] == 0, 'Corrente (A)'] = 1e-6
        df['log'] = df['Corrente (A)'].apply(np.log10)

    x = df['Tensão (v)']
    y = df['Corrente (A)']
    circuito = f.split('.')[0].split('_')[1]
    # dispositivo = f.split('.')[0].split('_')[0]

    # criar colunas de incerteza
    df['Incerteza de cal de Tensão'] = x.apply(incerteza_tensao_cal)
    df['Incerteza de ltr de Tensão'] = 0.001/(2*(3**(1/2)))
    df['Incerteza de Tensão'] = (df['Incerteza de ltr de Tensão']**2 +
                                 df['Incerteza de ltr de Tensão']**2)**(1/2)

    df['Incerteza de cal de Corrente'] = y.apply(incerteza_corrente_cal)
    df['Incerteza de ltr de Corrente'] = df['Menor dígito']/(2*(3**(1/2)))
    df['Incerteza de Corrente'] = (df['Incerteza de ltr de Corrente']**2 +
                                   df['Incerteza de ltr de Corrente']**2)**(1/2)

    # if 'tratado' not in f:
    #     df.to_csv(os.path.join(DATA_DIR, f'tratado_{f}'))

    ux = df['Incerteza de Tensão']
    uy = df['Incerteza de Corrente']
    if 'resistor' in f:
        figr, axr = plt.subplots(1, 1)
        axr.errorbar(x, y, xerr=ux, yerr=uy, fmt='o',
                     elinewidth=2, capthick=2, ms=3, label=f'Circuito {circuito}')
        axr.set_title('Curvas características de um resistor')
        axr.set_xlabel('Tensão (v)')
        axr.set_ylabel(r'Corrente (A)')
        axr.plot(x, x*100, color='black', alpha=0.5)
        axr.legend()
        plt.tight_layout()
        figr.savefig(os.path.join(IMG_DIR, f.replace('csv', 'png')))

        # a, b = np.polyfit(x, y, 1)
        figr2, axr2 = plt.subplots(1, 1)
        axr2.axhspan(95, 105, alpha=0.3, color='orange')
        axr2.axhline(y=100, color='orange')
        r = df['Resistencia (ohm)']
        axr2.scatter(x, r, label=f'Circuito {circuito}')
        c = np.polyfit(x, r, 0)
        axr2.axhline(y=c, color='blue')
        # print(f'\n\nRESISTENCIA NO CIRCUITO {circuito}', c, '\n')
        axr2.legend()
        axr2.set_title(r'Resistência ($\Omega$) por Tensão (v) em um resistor')
        axr2.set_ylabel(r'Resistência ($\Omega$)')
        axr2.set_xlabel(r'Tensão (v)')
        axr2.set_ylim([50, 150])
        plt.tight_layout()
        figr2.savefig(os.path.join(
            IMG_DIR, 'resistencia_'+f.replace('csv', 'png')))

    elif 'diodo' in f and MELHOR_CIRCUITO in f:
        figd, axd = plt.subplots(1, 1)
        axd.errorbar(x, y, xerr=ux, yerr=uy, fmt='o', label=f'Circuito {circuito}',
                     elinewidth=2, capthick=2, ms=3)
        axd.set_title(r'Curva característica de um diodo')
        axd.set_ylabel(r'Corrente (A)')
        axd.set_xlabel(r'Tensão (v)')
        axd.legend()
        # axd.set_ylim([50, 150])
        plt.tight_layout()
        figd.savefig(os.path.join(IMG_DIR, f.replace('csv', 'png')))

        figd2, axd2 = plt.subplots(1, 1)
        axd2.scatter(x, np.log10(y), label=f'Circuito {circuito}')
        axd2.set_title(
            r'Curva característica de um diodo em escala logarítmica')
        axd2.set_ylabel(r'ln Corrente (A)')
        axd2.set_xlabel(r'Tensão (v)')
        axd2.legend()
        # axd.set_ylim([50, 150])
        plt.tight_layout()
        figd2.savefig(os.path.join(IMG_DIR, 'log_'+f.replace('csv', 'png')))

        figd3, axd3 = plt.subplots(1, 1)
        r = df['Resistencia (ohm)']
        axd3.scatter(x, r, label=f'Circuito {circuito}')
        # print(f'\n\nRESISTENCIA NO CIRCUITO {circuito}', c, '\n')
        axd3.legend()
        axd3.set_title(r'Resistência ($\Omega$) por Tensão (v) em um diodo')
        axd3.set_ylabel(r'Resistência ($\Omega$)')
        axd3.set_xlabel(r'Tensão (v)')
        plt.tight_layout()
        figd3.savefig(os.path.join(
            IMG_DIR, 'resistencia_'+f.replace('csv', 'png')))

        figd4, axd4 = plt.subplots(1, 1)
        axd4.scatter(x, np.log(r), label=f'Circuito {circuito}')
        # print(f'\n\nRESISTENCIA NO CIRCUITO {circuito}', c, '\n')
        axd4.legend()
        axd4.set_title(r'ln Resistência ($\Omega$) por Tensão (v) em um diodo')
        axd4.set_ylabel(r'ln Resistência ($\Omega$)')
        axd4.set_xlabel(r'Tensão (v)')
        plt.tight_layout()
        figd4.savefig(os.path.join(
            IMG_DIR, 'log_resistencia_'+f.replace('csv', 'png')))
