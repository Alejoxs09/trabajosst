import cv2
import numpy as np
import pandas as pd

def calcular_cobertura_vegetal_por_cuadrante(imagen, verde_bajo, verde_alto):
    """
    Calcula el porcentaje de cobertura vegetal dividiendo una cuadrícula en 4 cuadrantes.
    """
    # Color HSV
    imagen_hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    
    # Mascara de verdeeee
    mascara_vegetal = cv2.inRange(imagen_hsv, verde_bajo, verde_alto)
    
    # Division de imagen en 4 cuadrantes de las cuacdriculas
    alto, ancho = mascara_vegetal.shape
    mitad_alto, mitad_ancho = alto // 2, ancho // 2

    cuadrantes = [
        mascara_vegetal[0:mitad_alto, 0:mitad_ancho],       # Cuadrante superior izquierdo 1
        mascara_vegetal[0:mitad_alto, mitad_ancho:ancho],   # Cuadrante superior derecho 2
        mascara_vegetal[mitad_alto:alto, 0:mitad_ancho],    # Cuadrante inferior izquierdo 3
        mascara_vegetal[mitad_alto:alto, mitad_ancho:ancho] # Cuadrante inferior derecho 4
    ]
    
    # Calcular el porcentaje de vegetación en cada cuadrante (1,2,3,4 me estoyvolviendoloco)
    resultados = []
    for cuadrante in cuadrantes:
        pixeles_totales = cuadrante.size
        pixeles_verdes = cv2.countNonZero(cuadrante)
        porcentaje_cuadrante = (pixeles_verdes / pixeles_totales) * 100
        resultados.append(porcentaje_cuadrante)
    
    return resultados

def analizar_cuadriculas(imagen_path, num_filas, num_columnas):
    # Cargar la image
    imagen = cv2.imread(imagen_path)
    if imagen is None:
        print("No se pudo cargar la imagen.")
        return
    
    # definir los rangos de colores (AJUSTABLE)
    verde_bajo = np.array([92, 78, 49])
    verde_alto = np.array([77, 164, 70])
    
    # Dimensiones de cada cuadricula
    alto_img, ancho_img, _ = imagen.shape
    alto_cuadricula = alto_img // num_filas
    ancho_cuadricula = ancho_img // num_columnas
    
    # Almacenamiento de resultados
    resultados_totales = []
    
    # Iterar sobre cada cuadrícula
    for fila in range(num_filas):
        for columna in range(num_columnas):
            # Extraer cada cuadrícula de la imagen plaplalaaa
            y_inicio = fila * alto_cuadricula
            y_fin = y_inicio + alto_cuadricula
            x_inicio = columna * ancho_cuadricula
            x_fin = x_inicio + ancho_cuadricula
            cuadricula = imagen[y_inicio:y_fin, x_inicio:x_fin]
            
            # Cobertura vegetal de los cuatro cuadrantes (1,2,3,4)
            porcentajes = calcular_cobertura_vegetal_por_cuadrante(cuadricula, verde_bajo, verde_alto)
            
            # determinar el porcentaje total de la cuadrícula basado en los cuadrantes
            # si un cuadrante tiene más del 20% de verde, cuenta como cubierto AJUSTAR DENSIDAD DE PIXELES.
            total_cobertura = sum(1 for p in porcentajes if p > 20) * 25
            
            # GUARDAR RES
            resultados_totales.append(total_cobertura)
    
    return resultados_totales

def exportar_a_excel(resultados, archivo_excel="resultados.xlsx"):
    # DATAFRAME PANDA EXCEL
    df = pd.DataFrame(resultados, columns=["Cobertura Vegetal (%)"])
    
    # EXPORTAR DATAFRAME
    df.to_excel(archivo_excel, index_label="Cuadrícula")
    print(f"Resultados exportados a {archivo_excel} con éxito.")

# Parámetros de ejemplo
imagen_ejemplo = "2023/Slide1.JPG"  # Cambia esto al nombre de tu imagen
num_filas = 30
num_columnas = 15

# Analisis
resultados = analizar_cuadriculas(imagen_ejemplo, num_filas, num_columnas)

# EXp rresultados en excel
if resultados:
    exportar_a_excel(resultados)
