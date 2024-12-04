import cv2
import numpy as np
import pandas as pd

def calcular_cobertura_vegetal_por_cuadrante(imagen, verde_bajo, verde_alto, umbral_porcentaje=30):
    """
    Calcula el porcentaje de cobertura vegetal dividiendo una cuadrícula en 4 cuadrantes.
    """
    # Convertir la imagen al espacio de color HSV
    imagen_hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    
    # Crear mascara para la tonalidad verde
    mascara_vegetal = cv2.inRange(imagen_hsv, verde_bajo, verde_alto)
    
    # Dividir la Cuadricula en 4 Sectores
    alto, ancho = mascara_vegetal.shape
    mitad_alto, mitad_ancho = alto // 2, ancho // 2
    cuadrantes = [
        mascara_vegetal[0:mitad_alto, 0:mitad_ancho],       # Cuadrante superior izquierdo
        mascara_vegetal[0:mitad_alto, mitad_ancho:ancho],   # C. superior derecho
        mascara_vegetal[mitad_alto:alto, 0:mitad_ancho],    # C. inferior izquierdo
        mascara_vegetal[mitad_alto:alto, mitad_ancho:ancho] # C. inferior derecho
    ]
    
    resultados = []
    for cuadrante in cuadrantes:
        pixeles_totales = cuadrante.size
        pixeles_verdes = cv2.countNonZero(cuadrante)
        porcentaje_cuadrante = (pixeles_verdes / pixeles_totales) * 100
        
        # Solo marcar como 25% si supera la densidad
        if porcentaje_cuadrante >= umbral_porcentaje:
            resultados.append(25)
        else:
            resultados.append(0)
    
    return sum(resultados)

def analizar_cuadriculas(imagen_path, num_filas, num_columnas):
    """
    Divide la imagen en cuadrículas, analiza cada cuadrícula de izquierda a derecha y 
    de arriba a abajo, y devuelve una matriz de resultados.
    """
    # Cargar la imagen
    imagen = cv2.imread(imagen_path)
    if imagen is None:
        print("No se pudo cargar la imagen.")
        return []
    
    # Ajustar los rangos de verde en HSV
    verde_bajo = np.array([30, 20, 20])  # Verde oscuro
    verde_alto = np.array([90, 255, 255])  # Verde claro
    
    alto_img, ancho_img, _ = imagen.shape
    alto_cuadricula = alto_img // num_filas
    ancho_cuadricula = ancho_img // num_columnas
    
    # Creacion de la matriz
    matriz_resultados = np.zeros((num_filas, num_columnas), dtype=int)
    
    for fila in range(num_filas):
        for columna in range(num_columnas):
            y_inicio = fila * alto_cuadricula
            y_fin = y_inicio + alto_cuadricula
            x_inicio = columna * ancho_cuadricula
            x_fin = x_inicio + ancho_cuadricula
            cuadricula = imagen[y_inicio:y_fin, x_inicio:x_fin]
            
            cobertura_cuadrante = calcular_cobertura_vegetal_por_cuadrante(
                cuadricula, verde_bajo, verde_alto, umbral_porcentaje=30)  # Ajustar la densidad de pixeles.
            
            matriz_resultados[fila, columna] = cobertura_cuadrante
    
    return matriz_resultados

def exportar_a_excel_matriz(matriz_resultados, archivo_excel="resultados1.xlsx"):
    """
    Exporta la matriz.
    """
    df = pd.DataFrame(matriz_resultados)
    df.to_excel(archivo_excel, index_label="Fila", header=[f"Columna {i+1}" for i in range(matriz_resultados.shape[1])])
    print(f"Resultados exportados a {archivo_excel} con éxito.")

# P Ejemplo
imagen_ejemplo = "2023/colorimetria.JPG"  # Reemplazar esta monda por la ruta de la imagen
num_filas = 30  
num_columnas = 15  

# Exportacion y analisis
matriz_resultados = analizar_cuadriculas(imagen_ejemplo, num_filas, num_columnas)
if matriz_resultados.size > 0:
    exportar_a_excel_matriz(matriz_resultados)
