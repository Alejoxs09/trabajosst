import cv2
import numpy as np
import pandas as pd

def calcular_cobertura_vegetal_por_cuadrante(imagen, verde_bajo, verde_alto, umbral_porcentaje=10):
    """
    Calcula el porcentaje de cobertura vegetal dividiendo una cuadrícula en 4 cuadrantes.
    """
    # Convertir la imagen al espacio de color HSV
    imagen_hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    
    # Crear una máscara para los tonos verdes
    mascara_vegetal = cv2.inRange(imagen_hsv, verde_bajo, verde_alto)
    
    # Mostrar la máscara para verificar si está detectando correctamente
    cv2.imshow('Mascara Vegetal', mascara_vegetal)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # Dividir la imagen en 4 cuadrantes
    alto, ancho = mascara_vegetal.shape
    mitad_alto, mitad_ancho = alto // 2, ancho // 2
    cuadrantes = [
        mascara_vegetal[0:mitad_alto, 0:mitad_ancho],       # Cuadrante superior izquierdo
        mascara_vegetal[0:mitad_alto, mitad_ancho:ancho],   # Cuadrante superior derecho
        mascara_vegetal[mitad_alto:alto, 0:mitad_ancho],    # Cuadrante inferior izquierdo
        mascara_vegetal[mitad_alto:alto, mitad_ancho:ancho] # Cuadrante inferior derecho
    ]
    
    resultados = []
    for cuadrante in cuadrantes:
        pixeles_totales = cuadrante.size
        pixeles_verdes = cv2.countNonZero(cuadrante)
        porcentaje_cuadrante = (pixeles_verdes / pixeles_totales) * 100
        
        # Solo marcar como 25% si supera el umbral
        if porcentaje_cuadrante >= umbral_porcentaje:
            resultados.append(25)
        else:
            resultados.append(0)
    
    return sum(resultados)

def analizar_cuadriculas(imagen_path, num_filas, num_columnas):
    # Cargar la imagen
    imagen = cv2.imread(imagen_path)
    if imagen is None:
        print("No se pudo cargar la imagen.")
        return []
    
    # Ajustar los rangos de verde aquí según tu imagen
    verde_bajo = np.array([35, 40, 40])
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
            
            total_cobertura = calcular_cobertura_vegetal_por_cuadrante(
                cuadricula, verde_bajo, verde_alto, umbral_porcentaje=10)
            
            resultados_totales.append(total_cobertura)
    
    return resultados_totales

def exportar_a_excel(resultados, archivo_excel="resultados.xlsx"):
    df = pd.DataFrame(resultados, columns=["Cobertura Vegetal (%)"])
    df.to_excel(archivo_excel, index_label="Cuadrícula")
    print(f"Resultados exportados a {archivo_excel} con éxito.")

# Parámetros de ejemplo
imagen_ejemplo = "2023/Slide1.JPG"
num_filas = 30
num_columnas = 15

resultados = analizar_cuadriculas(imagen_ejemplo, num_filas, num_columnas)
if resultados:
    exportar_a_excel(resultados)
