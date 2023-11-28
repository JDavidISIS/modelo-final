import streamlit as st
import pandas as pd
from visualization import generate_efi, generate_graph, generate_efi2
from optimization import optimizar_posicion_alabes
from preprocessor import CustomPreprocessor
from joblib import load

st.set_page_config(page_title='Optimización de Álabes')

modelo = load('modelo_regresion_lineal.joblib')

st.markdown("<h1 style='text-align: center; color: #D5752D;'>Aplicación para la Optimización de Posición de Álabes</h1>", unsafe_allow_html=True)


st.write('Por favor, cargue el archivo Excel con los registros necesarios para la visualización y la optimización.')
st.write('El Excel debe incluir, como minimo, las columnas: POTENCIA_ACTIVA_ALT_GI, MED_CAUDAL_TUBERÍA_REG_REG_TGI, NIVEL2_TANQ_CARGA y POSICION_DIST_TGI')
uploaded_file = st.file_uploader("", type=["xlsx"])



if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    preprocessor = CustomPreprocessor()
    processed_data = preprocessor.transform(df)


    # Generar y mostrar gráfica
    st.header('Curvas de Nivel')
    grafico = generate_graph(processed_data)
    st.pyplot(grafico)


    cabeza_min, cabeza_max = processed_data['Cabeza'].min(), processed_data['Cabeza'].max()
    potencia_min, potencia_max = processed_data['POTENCIA_ACTIVA_ALT_GI'].min(), processed_data['POTENCIA_ACTIVA_ALT_GI'].max()

    # Mostrar mensaje con los rangos de los datos
    st.info(f"Rango de cabeza: {cabeza_min} (m) - {cabeza_max} (m)")
    st.info(f"Rango de potencia: {potencia_min} (MW) - {potencia_max} (MW)")

    # Pedir parámetros para la optimización
    st.header('Parámetros de Optimización')
    potencia_deseada = st.number_input('Potencia (MW) deseada:', min_value=0.0)
    cabeza = st.number_input('Cabeza (m):', min_value=0.0)
    eficiencia_min = st.number_input('Límite Inferior Eficiencia (0-1):', 0.0, 1.0, 0.0)
    eficiencia_max = st.number_input('Límite Superior Eficiencia (0-1):', 0.0, 1.0, 1.0)
    optimizar_button = st.button('Optimizar')

    # Mostrar resultados de la optimización
    if optimizar_button and uploaded_file is not None:

        st.write('Tenga en cuenta que en caso que en muchos casos los resultados que genera el modelo son aproximados')

        if potencia_deseada < potencia_min or potencia_deseada > potencia_max or cabeza < cabeza_min or cabeza > cabeza_max:
            st.error("Los valores de entrada están fuera del rango aceptable.")
        else:
            resultados_optimizacion = optimizar_posicion_alabes(
                processed_data, modelo, potencia_deseada, cabeza, eficiencia_min, eficiencia_max
            )
            if resultados_optimizacion is not None:
                st.header('Resultados de Optimización')
                st.table(resultados_optimizacion)

                grafico_eficiencia = generate_efi(processed_data, best_results=resultados_optimizacion)
                st.pyplot(grafico_eficiencia)

                grafico_efi_ = generate_efi2(processed_data, best_results=resultados_optimizacion)
                st.pyplot(grafico_eficiencia)