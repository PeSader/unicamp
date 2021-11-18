import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

DATA_DIR = 'data'
IMAGE_DIR = 'img'
DPI = 200

INTERVALO_DE_AMOSTRAGEM = 1e-5   # segundos
MENOR_DIVISAO_TEMPO_OSC = 1e-6   # segundos
MENOR_DIVISAO_TENSAO_OSC = 1e-3  # volts
MENOR_DIVISAO_TENSAO_MUL = 1e-6  # volts
INCERTEZA_DE_DIGITALIZACAO_TENSAO = 1e-4  # volts


def main():
    circuitos = os.listdir(DATA_DIR)
    freqs = []
    amps = {'1': [], '2': []}
    u_amps = {'1': [], '2': []}

    for c in circuitos:
        files = sorted(os.listdir(os.path.join(DATA_DIR, c)))
        fig, ax = plt.subplots(1, 1, figsize=[8, 5])
        freqs = []
        i = 0

        for f in files:
            canal = int(f.split('.')[0].split('_')[-1][2:])
            num_circuito = int(f.split('.')[0].split('_')[1])
            nome_circuito = c.replace('_', ' ')
            frequencia = 0
            if 'Filtro' in c:
                frequencia = int(f.split('.')[0].split('_')[-2][:-2])

            # para garantir que cada grafico tem apenas curvas da mesma
            # frequencia, especialmente para o circuito do Filtro RC
            if i >= 2:
                fig, ax = plt.subplots(1, 1, figsize=[8, 5])
                i = 0
            df = pd.read_csv(os.path.join(DATA_DIR, c, f))
            # df.columns = ['', 'Info', '', 'Tempo (s)', 'Tensão (V)', '', ]
            mapping = {df.columns[3]: 'Tempo (s)', df.columns[4]: 'Tensão (V)'}
            df = df.rename(columns=mapping)
            df['Incerteza de Tempo (s)'] = incerteza_de_tempo()
            df['Incerteza de Tensão (V)'] = incerteza_de_tensao(
                df['Tensão (V)'])

            # x = df['Tempo (s)']
            # y = df['Tensão (V)']
            # xerr = df['Incerteza de Tempo (s)']
            # yerr = df['Incerteza de Tensão (V)']

            # ax.errorbar(x, y, xerr=xerr, yerr=yerr, fmt='o', elinewidth=2,
            #             capthick=2, ms=2, label=f'Canal {canal}')
            # ax.set_title(titulo(nome_circuito, num_circuito, frequencia))
            # ax.set_ylabel("Tensão (V)")
            # ax.set_xlabel("Tempo (s)")
            # ax.legend(loc='best')
            # plt.tight_layout()
            i += 1

            # salvar graficos
            # fig.savefig(os.path.join(IMAGE_DIR, f'{c}_{frequencia}'), dpi=DPI)

            amplitude = df['Tensão (V)'].max()
            u_amplitude = df['Incerteza de Tensão (V)'].max()
            if i == 1:
                freqs.append(frequencia)
            amps[str(canal)].append(amplitude)
            u_amps[str(canal)].append(u_amplitude)

    data = {'Frequência (Hz)': freqs[1:],
            'Amplitude no Canal 1 (V)': amps['1'][:-3][1:],
            'Amplitude no Canal 2 (V)': amps['2'][:-3][1:],
            'Incerteza de Amplitude no Canal 1 (V)': u_amps['1'][:-3][1:],
            'Incerteza de Amplitude no Canal 2 (V)': u_amps['2'][:-3][1:],
            }

    df2 = pd.DataFrame(data)
    df2['Razão de Amplitude'] = df2['Amplitude no Canal 2 (V)'] / \
        df2['Amplitude no Canal 1 (V)']
    df2['Incerteza de Razão de Amplitude'] = incerteza_da_divisao(df2['Amplitude no Canal 2 (V)'],
                                                                  df2['Incerteza de Amplitude no Canal 2 (V)'],
                                                                  df2['Amplitude no Canal 1 (V)'],
                                                                  df2['Incerteza de Amplitude no Canal 1 (V)'])

    x = df2['Frequência (Hz)']
    y = df2['Razão de Amplitude']
    yerr = df2['Incerteza de Razão de Amplitude']
    fig, ax = plt.subplots(1, 1, figsize=[8, 5])
    ax.errorbar(x, y, yerr, elinewidth=1, capsize=3,
                capthick=1, ms=3, ecolor='black')
    ax.set_title('Circuito 3 - Filtro RC: Razão de Amplitude por Frequência')
    ax.set_ylabel(r'$V_{max}$ canal 2 / $V_{max}$ canal 1 ')
    ax.set_xlabel('Frequência (Hz)')
    fig.savefig(os.path.join(IMAGE_DIR, 'Filtro_RC_razao_amplitude'), dpi=DPI)

    fig.savefig(os.path.join(IMAGE_DIR, 'Filtro_RC_razao_amplitude'), dpi=DPI)


def incerteza_de_tempo() -> float:
    u_calibracao = (INTERVALO_DE_AMOSTRAGEM + 1e-4 *
                    MENOR_DIVISAO_TEMPO_OSC + 4e-10)/2*3**(1/2)
    u_leitura = (MENOR_DIVISAO_TEMPO_OSC)/2*3**(1/2)
    return np.sqrt(u_calibracao**2 + u_leitura**2)


def incerteza_de_tensao(tensao: float) -> float:
    u_calibracao = (3e-2*tensao + 10e-2 *
                    MENOR_DIVISAO_TEMPO_OSC + 1e-3)/2*3**(1/2)
    u_leitura = (MENOR_DIVISAO_TENSAO_OSC)/2*3**(1/2)
    u_digitalizacao = INCERTEZA_DE_DIGITALIZACAO_TENSAO
    return np.sqrt(u_calibracao**2 + u_leitura**2 + u_digitalizacao**2)


def incerteza_da_divisao(a: float, ua: float, b: float, ub: float):
    return(np.sqrt(b**(-2)*ua - ((a/b**2)**2)*ub))


def titulo(nome_circuito: str, num_circuito: int, freq: int):
    titulo = f'Circuito {num_circuito} - {nome_circuito}'
    if freq != 0:
        titulo += f' (Frequência = {freq}Hz)'
    return titulo


if __name__ == "__main__":
    main()
