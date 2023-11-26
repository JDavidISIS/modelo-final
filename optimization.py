import pandas as pd
import numpy as np

def optimizar_posicion_alabes(data_final_positive, pipeline, potencia_deseada, cabeza, eficiencia_min, eficiencia_max):
    cabeza_min, cabeza_max = data_final_positive['Cabeza'].min(), data_final_positive['Cabeza'].max()
    potencia_min, potencia_max = data_final_positive['POTENCIA_ACTIVA_ALT_GI'].min(), data_final_positive['POTENCIA_ACTIVA_ALT_GI'].max()
    caudal_min, caudal_max = data_final_positive['MED_CAUDAL_TUBERÍA_REG_REG_TGI'].min(), data_final_positive['MED_CAUDAL_TUBERÍA_REG_REG_TGI'].max()

    if cabeza < cabeza_min or cabeza > cabeza_max or potencia_deseada < potencia_min or potencia_deseada > potencia_max:
        print("Los valores de entrada están fuera del rango aceptable.")
        return None, None
    
    # Filtrar los datos para registros cercanos tanto a la potencia como a la cabeza deseada
    data_cercana = data_final_positive[(data_final_positive['POTENCIA_ACTIVA_ALT_GI'] >= potencia_deseada - 0.1) & 
                        (data_final_positive['POTENCIA_ACTIVA_ALT_GI'] <= potencia_deseada + 0.1) &
                        (data_final_positive['Cabeza'] >= cabeza - 0.1) &
                        (data_final_positive['Cabeza'] <= cabeza + 0.1)]

    if data_cercana.empty:
        eficiencias_validas = []
        posiciones_validas = []
        caudales = []

        for posicion_alabes in range(0, 100 + 1):
            datos_prediccion = pd.DataFrame([[posicion_alabes, potencia_deseada, cabeza]],
                                    columns=['POSICION_DIST_TGI', 'POTENCIA_ACTIVA_ALT_GI', 'Cabeza'])
            
            # Predecir el caudal para esta posición de álabes
            caudal_predicho = pipeline.predict(datos_prediccion)[0]

            # Calcular la eficiencia teórica
            eficiencia_predicha = (potencia_deseada * 1000000)/(1000 * 9.81 * caudal_predicho * cabeza)

            # Guardar los resultados si cumplen con los criterios
            if eficiencia_min <= eficiencia_predicha <= eficiencia_max and 0 <= posicion_alabes <= 100:
                eficiencias_validas.append(eficiencia_predicha)
                posiciones_validas.append(posicion_alabes)

        # Convertir los resultados en un DataFrame y ordenarlos
        df_resultados = pd.DataFrame({'Eficiencia': eficiencias_validas, 'PosicionAlabes': posiciones_validas})
        df_resultados.sort_values(by='Eficiencia', ascending=False, inplace=True)

        return df_resultados

    if eficiencia_min <= data_cercana['Eficiencia'] <= eficiencia_max:
        datos = pd.DataFrame(data_cercana)
        datos.sort_values(by='Eficiencia', ascending=False, inplace=True)

    return datos