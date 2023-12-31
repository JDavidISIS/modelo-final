import pandas as pd
import numpy as np

def optimizar_posicion_alabes(data_final_positive, pipeline, potencia_deseada, cabeza, eficiencia_min, eficiencia_max):
    cabeza_min, cabeza_max = data_final_positive['Cabeza'].min(), data_final_positive['Cabeza'].max()
    potencia_min, potencia_max = data_final_positive['POTENCIA_ACTIVA_ALT_GI'].min(), data_final_positive['POTENCIA_ACTIVA_ALT_GI'].max()

    if cabeza < cabeza_min or cabeza > cabeza_max or potencia_deseada < potencia_min or potencia_deseada > potencia_max:
        print("Los valores de entrada están fuera del rango aceptable.")
        return pd.DataFrame() 
    
    
    data_cercana = data_final_positive[(data_final_positive['POTENCIA_ACTIVA_ALT_GI'] >= potencia_deseada - 0.1) & 
                        (data_final_positive['POTENCIA_ACTIVA_ALT_GI'] <= potencia_deseada + 0.1) &
                        (data_final_positive['Cabeza'] >= cabeza - 0.1) &
                        (data_final_positive['Cabeza'] <= cabeza + 0.1)]

    resultados_validos = []
    if data_cercana.empty:
        for posicion_alabes in range(101):  # De 0 a 100
            datos_prediccion = pd.DataFrame([[posicion_alabes, cabeza]],
                                    columns=['POSICION_DIST_TGI', 'Cabeza'])
            
            caudal_predicho = pipeline.predict(datos_prediccion)[0]

            eficiencia_calculada = (potencia_deseada * 1000000) / (1000 * 9.81 * caudal_predicho * cabeza)

            if eficiencia_min <= eficiencia_calculada <= eficiencia_max:
                resultados_validos.append({
                    'Eficiencia': eficiencia_calculada,
                    'Posicion Álabes (%)': posicion_alabes,
                    'Caudal (m^3/s)': caudal_predicho  
                })
    else:
    
        for _, row in data_cercana.iterrows():
            if eficiencia_min <= row['Eficiencia'] <= eficiencia_max:
                resultados_validos.append({
                    'Eficiencia': row['Eficiencia'],
                    'Posicion Álabes (%)': row['POSICION_DIST_TGI'],
                    'Caudal (m^3/s)': row['MED_CAUDAL_TUBERÍA_REG_REG_TGI']
                })
                
    if resultados_validos:
        df_resultados = pd.DataFrame(resultados_validos)
        df_resultados['Cabeza (m)'] = cabeza
        df_resultados['Potencia (MW)'] = potencia_deseada
        df_resultados.sort_values(by='Eficiencia', ascending=False, inplace=True)
        return df_resultados
    else:
        return pd.DataFrame({'Mensaje': ['No se encontraron configuraciones válidas dentro del rango de eficiencia.']})
    

