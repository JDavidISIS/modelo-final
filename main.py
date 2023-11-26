import json
from fastapi import FastAPI, File, UploadFile, Form
from matplotlib import pyplot as plt
import pandas as pd
from io import BytesIO
from preprocessor import CustomPreprocessor
from visualization import generate_graph
from optimization import optimizar_posicion_alabes
from joblib import load
from pydantic import BaseModel
import base64
import time

app = FastAPI()

# Cargar el modelo entrenado
modelo = load('modelo_entrenado.joblib')


class InputParams(BaseModel):
    potencia_deseada: float
    cabeza: float
    eficiencia_min: float
    eficiencia_max: float

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/optimizar/")
async def optimizar(input_params: str = Form(...), file: UploadFile = File(...)):
    start_time = time.time()

    params = json.loads(input_params)
    input_data = InputParams(**params)
    
    contents = await file.read()
    df = pd.read_excel(BytesIO(contents))

    # Preprocesamiento
    preprocessor = CustomPreprocessor()
    processed_data = preprocessor.transform(df)

    # Llamada a la función de optimización con los parámetros del usuario
    resultados_optimizacion = optimizar_posicion_alabes(
        processed_data, 
        modelo,  
        input_data.potencia_deseada, 
        input_data.cabeza, 
        input_data.eficiencia_min, 
        input_data.eficiencia_max
    )

    # Convertir los resultados a un formato que pueda ser serializado por FastAPI, por ejemplo, a un diccionario
    if isinstance(resultados_optimizacion, pd.DataFrame):
        resultados_dict = resultados_optimizacion.to_dict(orient='records')
    else:
        resultados_dict = {"message": "No se encontraron resultados válidos."}

    end_time = time.time()  # Detiene el cronómetro
    processing_time = end_time - start_time
    print(f"Tiempo de procesamiento: {processing_time} segundos")

    return {"resultados_optimizacion": resultados_dict}

@app.post("/generar_grafico/")
async def generar_grafico(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_excel(BytesIO(contents))

    # Preprocesamiento
    preprocessor = CustomPreprocessor()
    processed_data = preprocessor.transform(df)

    # Generar gráfico
    grafico = generate_graph(processed_data)

    # Convertir el gráfico a formato base64 para Power BI
    buf = BytesIO()
    grafico.savefig(buf, format='png')
    buf.seek(0)
    grafico_base64 = base64.b64encode(buf.read()).decode("ascii")

    # No olvides cerrar el gráfico después de guardar
    plt.close(grafico)

    return {"grafico_base64": grafico_base64}