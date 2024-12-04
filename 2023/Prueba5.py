import cv2
import numpy as np
import pandas as pd

def calcular_cobertura_vegetal_por_cuadrante(imagen, verde_bajo, verde_alto, umbral_cuadrante=35):
    """
    Calcula el porcentaje de cobertura vegetal dividiendo una cuadrícula en 4 cuadrantes y marca el cuadrante como cubierto
    si más del umbral (35%) de los píxeles son verdes.
    """
    imagen_hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    
    # Crear una máscara para los tonos verdes
    mascara_vegetal = cv2.inRange(imagen_hsv, verde_bajo, verde_alto)
    
    alto, ancho = mascara_vegetal.shape
    mitad_alto, mitad_ancho = alto // 2, ancho // 2

    cuadrantes = [
        mascara_vegetal[0:mitad_alto, 0:mitad_ancho],       
        mascara_vegetal[0:mitad_alto, mitad_ancho:ancho],   
        mascara_vegetal[mitad_alto:alto, 0:mitad_ancho],    
        mascara_vegetal[mitad_alto:alto, mitad_ancho:ancho] 
    ]
    
    resultados = []
    for cuadrante in cuadrantes:
        pixeles_totales = cuadrante.size
        pixeles_verdes = cv2.countNonZero(cuadrante)
        porcentaje_verde = (pixeles_verdes / pixeles_totales) * 100
        
        # Si el porcentaje de verde en el cuadrante es mayor al umbral, se considera cubierto
        if porcentaje_verde > umbral_cuadrante:
            resultados.append(25)
        else:
            resultados.append(0)
    
    return resultados

def analizar_cuadriculas(imagen_path, num_filas, num_columnas):
    imagen = cv2.imread(imagen_path)
    if imagen is None:
        print("No se pudo cargar la imagen.")
        return
    
    # Nuevos umbrales de color verde en HSV
    verde_bajo = np.array([35, 60, 60])
    verde_alto = np.array([85, 255, 255])
    
    alto_img, ancho_img, _ = imagen.shape
    alto_cuadricula = alto_img // num_filas
    ancho_cuadricula = ancho_img // num_columnas
    
    resultados_totales = []
    
    for fila in range(num_filas):
        for columna in range(num_columnas):
            y_inicio = fila * alto_cuadricula
            y_fin = y_inicio + alto_cuadricula
            x_inicio = columna * ancho_cuadricula
            x_fin = x_inicio + ancho_cuadricula
            cuadricula = imagen[y_inicio:y_fin, x_inicio:x_fin]
            
            porcentajes = calcular_cobertura_vegetal_por_cuadrante(cuadricula, verde_bajo, verde_alto)
            total_cobertura = sum(porcentajes)
            resultados_totales.append(total_cobertura)
    
    return resultados_totales

def exportar_a_excel(resultados, archivo_excel="resultados_ajustados.xlsx"):
    df = pd.DataFrame(resultados, columns=["Cobertura Vegetal (%)"])
    df.to_excel(archivo_excel, index_label="Cuadrícula")
    print(f"Resultados exportados a {archivo_excel} con éxito.")

# Parámetros de ejemplo
imagen_ejemplo = "2023/Slide1.JPG"
num_filas = 30
num_columnas = 15

# Ejecutar el análisis
resultados = analizar_cuadriculas(imagen_ejemplo, num_filas, num_columnas)

if resultados:
    exportar_a_excel(resultados)
