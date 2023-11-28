import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class CustomPreprocessor(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        # No hay cálculo necesario para el ajuste en este caso
        return self

    def transform(self, X):
        # Crear una copia del DataFrame para asegurarnos de que estamos trabajando en una copia y no en una vista
        X_reducida = X.copy()
       
        # Mantener solo las columnas de interés
        columnas_de_interes = ['NIVEL2_TANQ_CARGA', 'MED_CAUDAL_TUBERÍA_REG_REG_TGI', 'POTENCIA_ACTIVA_ALT_GI', 'POSICION_DIST_TGI']
        X_reducida = X_reducida[columnas_de_interes]

        # Imputación de valores nulos utilizando .loc para asignaciones
        for col in ['MED_CAUDAL_TUBERÍA_REG_REG_TGI', 'POTENCIA_ACTIVA_ALT_GI', 'POSICION_DIST_TGI']:
            X_reducida.loc[:, col] = X_reducida.loc[:, col].interpolate(method='polynomial', order=2)
        X_reducida.loc[:, 'NIVEL2_TANQ_CARGA'] = X_reducida.loc[:, 'NIVEL2_TANQ_CARGA'].interpolate(method='linear')

        # Eliminar filas con valores nulos o negativos
        X_reducida = X_reducida.dropna()
        X_reducida = X_reducida[X_reducida['POTENCIA_ACTIVA_ALT_GI'] >= 0]

        # Cálculos adicionales para 'Cabeza' y 'Eficiencia', utilizando .loc para asignaciones
        g = 9.81  # m/s^2
        densidad_agua = 1000  # kg/m^3
        altura_inferior = 1180.81 # m.s.n.m.
        X_reducida.loc[:, 'Cabeza'] = X_reducida.loc[:, 'NIVEL2_TANQ_CARGA'] - altura_inferior
        X_reducida.loc[:, 'Eficiencia'] = (X_reducida.loc[:, 'POTENCIA_ACTIVA_ALT_GI'] * 1000000) / (densidad_agua * g * X_reducida.loc[:, 'MED_CAUDAL_TUBERÍA_REG_REG_TGI'] * X_reducida.loc[:, 'Cabeza'])
        
        # Reemplazar infinitos y valores no numéricos con NaN y eliminar estas filas
        X_reducida.replace([np.inf, -np.inf], np.nan, inplace=True)
        X_reducida.dropna(subset=['Eficiencia'], inplace=True)

        return X_reducida
