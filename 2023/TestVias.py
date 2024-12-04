import cv2
import numpy as np
import pandas as pd

def visualizar_detecciones(cuadricula, bordes, lineas, nombre_archivo):
    """
    Guarda una imagen con los bordes y las líneas detectadas sobre la cuadrícula.
    """
    salida = cv2.cvtColor(bordes, cv2.COLOR_GRAY2BGR)  # Convertir bordes a BGR para superponer líneas
    if lineas is not None:
        for linea in lineas:
            x1, y1, x2, y2 = linea[0]
            cv2.line(salida, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Dibujar líneas en rojo
    cv2.imwrite(nombre_archivo, salida)

def calcular_cobertura_vial(cuadricula, umbral_longitud, diagnostico=False, nombre_archivo=""):
    """
    Calcula la cobertura vial en una cuadrícula utilizando la Transformada de Hough.
    Guarda imágenes de diagnóstico si es necesario.
    """
    # Convertir a escala de grises y aplicar detección de bordes
    gris = cv2.cvtColor(cuadricula, cv2.COLOR_BGR2GRAY)
    bordes = cv2.Canny(gris, 30, 200)  # Ajustar los parámetros de Canny si es necesario

    # Detectar líneas usando la Transformada de Hough
    lineas = cv2.HoughLinesP(bordes, 1, np.pi / 180, threshold=30, minLineLength=50, maxLineGap=20)
    longitud_total = 0

    if lineas is not None:
        for linea in lineas:
            x1, y1, x2, y2 = linea[0]
            longitud_total += np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)  # Calcular la longitud de la línea

    # Guardar imágenes de diagnóstico
    if diagnostico and nombre_archivo:
        visualizar_detecciones(cuadricula, bordes, lineas, nombre_archivo)

    # Calcular porcentaje basado en la longitud total de las líneas detectadas
    if longitud_total >= umbral_longitud:
        return 100
    elif longitud_total >= 0.75 * umbral_longitud:
        return 75
    elif longitud_total >= 0.5 * umbral_longitud:
        return 50
    elif longitud_total >= 0.25 * umbral_longitud:
        return 25
    else:
        return 0

def analizar_cuadriculas_vial(imagen, num_filas, num_columnas, umbral_longitud, diagnostico=False):
    """
    Divide la imagen en cuadrículas y analiza la cobertura vial en cada cuadrícula.
    """
    alto_img, ancho_img, _ = imagen.shape
    alto_cuadricula = alto_img // num_filas
    ancho_cuadricula = ancho_img // num_columnas

    matriz_resultados = np.zeros((num_filas, num_columnas), dtype=int)

    for fila in range(num_filas):
        for columna in range(num_columnas):
            y_inicio = fila * alto_cuadricula
            y_fin = y_inicio + alto_cuadricula
            x_inicio = columna * ancho_cuadricula
            x_fin = x_inicio + ancho_cuadricula
            cuadricula = imagen[y_inicio:y_fin, x_inicio:x_fin]

            # Calcular cobertura vial para la cuadrícula
            nombre_diagnostico = f"diagnostico_cuadricula_{fila}_{columna}.jpg" if diagnostico else ""
            cobertura = calcular_cobertura_vial(cuadricula, umbral_longitud, diagnostico, nombre_diagnostico)
            matriz_resultados[fila, columna] = cobertura

    return matriz_resultados

def exportar_a_excel_vial(resultados, archivo_excel="resultados_vial.xlsx"):
    """
    Exporta los resultados viales a un archivo Excel.
    """
    df = pd.DataFrame(resultados)
    df.to_excel(archivo_excel, index_label="Fila", header=[f"Columna {i+1}" for i in range(resultados.shape[1])])
    print(f"Resultados exportados a {archivo_excel} con éxito.")

# Parámetros
imagen_path = "2023/colorimetria.JPG"  # Cambia esto por el path de tu imagen
num_filas = 30
num_columnas = 15
umbral_longitud = 50  # Ajusta este valor según la longitud mínima para considerar cobertura

# Cargar la imagen
imagen = cv2.imread(imagen_path)
if imagen is None:
    print("No se pudo cargar la imagen.")
else:
    # Analizar cobertura vial con diagnóstico activado
    resultados_vial = analizar_cuadriculas_vial(imagen, num_filas, num_columnas, umbral_longitud, diagnostico=True)

    # Exportar resultados a Excel
    exportar_a_excel_vial(resultados_vial)

