import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import io
import base64


def generate_graph(data_final_positive, best_results=None):
    # Define el número de puntos en la malla para una mayor resolución
    num_points = 10

    # Genera la malla de puntos con una densidad mayor
    x = np.linspace(data_final_positive['Cabeza'].min(), data_final_positive['Cabeza'].max(), num_points)
    y = np.linspace(data_final_positive['MED_CAUDAL_TUBERÍA_REG_REG_TGI'].min(), data_final_positive['MED_CAUDAL_TUBERÍA_REG_REG_TGI'].max(), num_points)
    X, Y = np.meshgrid(x, y)

    # Interpola los valores de eficiencia para la malla de puntos
    Z = griddata(
        (data_final_positive['Cabeza'], data_final_positive['MED_CAUDAL_TUBERÍA_REG_REG_TGI']),
        data_final_positive['Eficiencia'],
        (X, Y), method='linear', fill_value=np.nan
    )

    # Crea una máscara basada en los datos existentes
    mask = np.isfinite(griddata(
        (data_final_positive['Cabeza'], data_final_positive['MED_CAUDAL_TUBERÍA_REG_REG_TGI']),
        data_final_positive['Eficiencia'],
        (X, Y), method='nearest'
    ))

    # Aplica la máscara a los datos interpolados
    Z = np.where(mask, Z, np.nan)
    Z = np.clip(Z, 0, 1)

    # Define los niveles del contorno
    levels = np.linspace(0, 1, num=40)

    # Crear una nueva figura y guardar la referencia
    fig, ax = plt.subplots(figsize=(12, 10))

    # Utilizar ax para dibujar los contornos
    contour_eficiencia = ax.contour(X, Y, Z, levels=levels, colors='black', linewidths=0.5)
    ax.clabel(contour_eficiencia, inline=True, fontsize=10, fmt='%1.2f')

    contourf_eficiencia = ax.contourf(X, Y, Z, levels=levels, cmap='viridis', alpha=0.75)
    fig.colorbar(contourf_eficiencia, ax=ax, label='Eficiencia')

    min_potencia = data_final_positive['POTENCIA_ACTIVA_ALT_GI'].min()
    max_potencia = data_final_positive['POTENCIA_ACTIVA_ALT_GI'].max()
    potencia_levels = np.round(np.linspace(min_potencia, max_potencia, 5)).astype(int)

    Z_potencia = griddata(
        (data_final_positive['Cabeza'], data_final_positive['MED_CAUDAL_TUBERÍA_REG_REG_TGI']),
        data_final_positive['POTENCIA_ACTIVA_ALT_GI'],
        (X, Y), method='linear', fill_value=np.nan
    )

    contour_potencia = ax.contour(X, Y, Z_potencia, levels=potencia_levels, colors='blue', linestyles='dashed')
    for i in range(len(potencia_levels)):
        ax.clabel(contour_potencia, [contour_potencia.levels[i]], inline=True, fmt=f'{potencia_levels[i]} MW', fontsize=10)

    ax.set_xlabel('Cabeza (m)')
    ax.set_ylabel('Caudal (m^3/s)')
    ax.set_title('Eficiencia y Potencia en función de Cabeza y Caudal')

    return fig

def generate_efi(data_final_positive, best_results=None):
    plt.figure(figsize=(8, 6))
    plt.scatter(data_final_positive['POTENCIA_ACTIVA_ALT_GI'], data_final_positive['Eficiencia'], label='Puntos de Eficiencia')

    # Resaltar el mejor punto de eficiencia
    if best_results is not None and not best_results.empty:
        # Suponiendo que best_results está ordenado por eficiencia y el mejor resultado es el primero
        best_point = best_results.iloc[0]
        plt.scatter(best_point['Potencia (MW)'], best_point['Eficiencia'], color='red', label='Mejor Punto de Eficiencia')

    plt.xlabel('Potencia Activa (MW)')
    plt.ylabel('Eficiencia')
    plt.title('Potencia vs Eficiencia')
    plt.legend()

    return plt


def generate_efi2(data_final_positive, best_results=None):
    # Gráfico de Caudal vs Eficiencia con línea de tendencia
    plt.figure(figsize=(8, 6))
    plt.scatter(data_final_positive['MED_CAUDAL_TUBERÍA_REG_REG_TGI'], data_final_positive['Eficiencia'])

    # Resaltar el mejor punto de eficiencia
    if best_results is not None and not best_results.empty:
        # Suponiendo que best_results está ordenado por eficiencia y el mejor resultado es el primero
        best_point = best_results.iloc[0]
        plt.scatter(best_point['Caudal (m^3/s)'], best_point['Eficiencia'], color='red', label='Mejor Punto de Eficiencia')

    plt.xlabel('Caudal (m^3/s)')
    plt.ylabel('Eficiencia')
    plt.title('Caudal vs Eficiencia')

    return plt
