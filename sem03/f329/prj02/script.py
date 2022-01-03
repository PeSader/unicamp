import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import os

from typing import List, Tuple
from uncertainties import ufloat

DPI = 200
PLOTS_DIR = "plots"
DATA_DIR = "data"
COLUMN_TIME = "Time (s)"
COLUMN_SPL = "Sound pressure level (dB)"
UNCERTAINTY_NPS = 0.48
UNCERTAINTY_TIME = 0.2/(2*np.sqrt(3))
RESISTOR_BUZZER = 1125


def main():
    # fazer grafico de dados brutos
    # raw_data_dir = os.path.join(DATA_DIR, os.listdir(DATA_DIR)[0])
    # raw_data_paths = os.listdir(raw_data_dir)
    # for i in range(len(raw_data_paths)):
    #     raw_data_paths[i] = os.path.join(raw_data_dir, raw_data_paths[i])
    # plot_data(raw_data_paths, "Dados Brutos de ")

    # fazer grafico da parte linear dos dados
    processed_data_dir = os.path.join(DATA_DIR, os.listdir(DATA_DIR)[1])
    processed_data_paths = os.listdir(processed_data_dir)
    for i in range(len(processed_data_paths)):
        processed_data_paths[i] = os.path.join(
            processed_data_dir, processed_data_paths[i])
    plot_data(processed_data_paths, "Parte Linear dos Dados de ")


def plot_data(paths: List[str], title_prefix: str):
    fig1, ax1 = plt.subplots(1, 1, figsize=[1.2 * 8, 1.2 * 5])

    m_variando_resistencia = []
    capacitancias = []
    m_variando_capacitancia = []
    resistencias = []

    for p in paths:
        df = pd.read_csv(p)
        df[COLUMN_TIME] = df[COLUMN_TIME] - df[COLUMN_TIME][0]
        r = path_to_resistance(p)
        c = path_to_capacitance(p)

        # traçar pontos experimentais
        x = df[COLUMN_TIME]
        y = df[COLUMN_SPL]
        label = create_label(r, c)
        color = next(ax1._get_lines.prop_cycler)['color']
        ax1.errorbar(x, y, fmt='o', alpha=0.5, ms=1, color=color, ecolor=color,
                     xerr=UNCERTAINTY_TIME, yerr=UNCERTAINTY_NPS, label=label)

        # traçar linearização
        m, b = linearizar(x, y, UNCERTAINTY_NPS)
        ax1.plot(x, m.n*x + b.n, linewidth=2, color=color)

        # separar dados variando resistencia e capacitancia
        if (c == 1000):
            m_variando_resistencia += [m.n]
            resistencias += [r]
        if (r == 1):
            m_variando_capacitancia += [m.n]
            capacitancias += [c]

        # calcular constante de tempo tau
        tau_estimado = (ufloat(r, 0.03*r)*1000 +
                        ufloat(RESISTOR_BUZZER, 0.1))*(ufloat(c, 0.03*c)*1e-6)
        tau_obtido = -20*np.log10(math.e)/m

        # imprimir resultados
        print(label, "m =", m, "tau estimado =",
              tau_estimado, "tau obtido =", tau_obtido, "\n")

    # grafico de m para diferentes valores de resistencia
    fig2, ax2 = plt.subplots(1, 1)
    ax2.scatter(resistencias, m_variando_resistencia)
    fig2.savefig(os.path.join(PLOTS_DIR, "m_por_resistencia"))

    # grafico de m para diferentes valores de capacitancia
    fig3, ax3 = plt.subplots(1, 1)
    ax3.scatter(capacitancias, m_variando_capacitancia)
    fig3.savefig(os.path.join(PLOTS_DIR, "m_por_capacitancia"))

    ax1.set_title(title_prefix + "Nível de Pressão Sonora por Tempo")
    ax1.set_ylabel("Nível de pressão sonora (dB)")
    ax1.set_xlabel("Tempo (s)")
    ax1.legend(loc="best")
    fig1.savefig(os.path.join(PLOTS_DIR, "nps_por_tempo"), dpi=DPI)


def create_label(resistance: int, capacitance: int):
    """cria uma legenda baseada no caminho relativo para o arquivo de dados

    :param path: caminho relativo para o arquivo de dados
    """
    label = ""
    label += "R=" + str(resistance) + r'k$\Omega$, '
    label += "C=" + str(capacitance) + r'$\mu$F'
    return label


def path_to_resistance(path: str):
    """extrai a resistencia do caminho relativo para o arquivo de dados

    :param path: caminho relativo para o arquivo de dados
    """
    return int(path.split('.')[0].split('/')[-1].split(' ')[0][2:])


def path_to_capacitance(path: str):
    """extrai a capacitancia do caminho relativo para o arquivo de dados

    :param path: caminho relativo para o arquivo de dados
    """
    return int(path.split('.')[0].split('/')[-1].split(' ')[1][2:])


def linearizar(x, y, yerror) -> Tuple[ufloat, ufloat]:

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
    incerteza_coef_angular = np.sqrt(n/delta)*yerror
    a = ufloat(coef_angular, incerteza_coef_angular)

    coef_linear = (sum_y*sum_x_squared - sum_xy*sum_x)/delta
    incerteza_coef_linear = np.sqrt(sum_x_squared/delta)*yerror
    b = ufloat(coef_linear, incerteza_coef_linear)

    return a, b


if __name__ == "__main__":
    main()
