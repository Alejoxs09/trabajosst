import cv2
import numpy as np
import pandas as pd

def calcular_cobertura_vial_gris(cuadricula, umbral_longitud, diagnostico=False, nombre_archivo="", imagen_lineas=None, x_offset=0, y_offset=0):
    """
    Calcula la cobertura vial en una cuadrícula detectando áreas grises y contornos.
    """
    # Convertir a espacio HSV para filtrar tonalidades grises
    hsv = cv2.cvtColor(cuadricula, cv2.COLOR_BGR2HSV)
    # Ajuste más estricto del rango de grises
    gris_bajo = np.array([0, 0, 85])  # Tonos oscuros de gris (ajustado)
    gris_alto = np.array([180, 30, 250])  # Tonos claros de gris (ajustado)
    mascara_gris = cv2.inRange(hsv, gris_bajo, gris_alto)

    # Suavizar la máscara para eliminar ruido
    mascara_gris = cv2.GaussianBlur(mascara_gris, (5, 5), 0)

    # Aplicar detección de bordes solo en las áreas grises
    bordes = cv2.Canny(mascara_gris, 50, 150)  # Ajuste de parámetros de Canny

    # Detectar contornos
    contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    longitud_total = 0

    cv2.imshow("Máscara de grises", mascara_gris)

    for contorno in contornos:
        longitud = cv2.arcLength(contorno, closed=False)
        if longitud > umbral_longitud:  # Considerar solo contornos suficientemente largos
            longitud_total += longitud
            if imagen_lineas is not None:
                # Dibujar el contorno en la imagen principal, ajustando por el desplazamiento
                cv2.drawContours(imagen_lineas, [contorno], -1, (0, 255, 0), 2, offset=(x_offset, y_offset))

    # Guardar imágenes de diagnóstico
    if diagnostico and nombre_archivo:
        diagnostico_img = cv2.cvtColor(mascara_gris, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(diagnostico_img, contornos, -1, (0, 255, 0), 2)  # Dibujar contornos detectados
        cv2.imwrite(nombre_archivo, diagnostico_img)

    # Calcular porcentaje basado en la longitud total de los contornos detectados
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

def analizar_cuadriculas_vial_gris(imagen, num_filas, num_columnas, umbral_longitud, diagnostico=False):
    """
    Divide la imagen en cuadrículas y analiza la cobertura vial considerando solo tonalidades grises.
    """
    alto_img, ancho_img, _ = imagen.shape
    alto_cuadricula = alto_img // num_filas
    ancho_cuadricula = ancho_img // num_columnas

    matriz_resultados = np.zeros((num_filas, num_columnas), dtype=int)

    # Crear una copia de la imagen original para superponer las curvas detectadas
    imagen_lineas = imagen.copy()

    for fila in range(num_filas):
        for columna in range(num_columnas):
            y_inicio = fila * alto_cuadricula
            y_fin = y_inicio + alto_cuadricula
            x_inicio = columna * ancho_cuadricula
            x_fin = x_inicio + ancho_cuadricula
            cuadricula = imagen[y_inicio:y_fin, x_inicio:x_fin]

            # Calcular cobertura vial para la cuadrícula
            nombre_diagnostico = f"diagnostico_cuadricula_{fila}_{columna}.jpg" if diagnostico else ""
            cobertura = calcular_cobertura_vial_gris(
                cuadricula, umbral_longitud, diagnostico, nombre_diagnostico, imagen_lineas, x_inicio, y_inicio
            )
            matriz_resultados[fila, columna] = cobertura

    # Guardar la imagen final con todas las curvas detectadas
    cv2.imwrite("lineas_detectadas_gris.jpg", imagen_lineas)
    print("Imagen final con carreteras grises detectadas guardada como 'lineas_detectadas_gris.jpg'.")

    return matriz_resultados

def exportar_a_excel(matriz_resultados, archivo_excel="resultados_vial_german.xlsx"):
    """
    Exporta los resultados de la matriz a un archivo Excel.
    """
    # Convertir la matriz a un DataFrame de pandas
    df = pd.DataFrame(matriz_resultados)

    # Crear nombres de columnas
    columnas = [f"Columna {i+1}" for i in range(matriz_resultados.shape[1])]
    df.columns = columnas

    # Añadir índices de filas
    df.index = [f"Fila {i+1}" for i in range(matriz_resultados.shape[0])]

    # Guardar en un archivo Excel
    df.to_excel(archivo_excel, index_label="Filas")
    print(f"Resultados exportados con éxito a {archivo_excel}.")

# Parámetros
imagen_path = "2023/coberturagerman.jpg"  # Cambia esto por el path de tu imagen
num_filas = 18
num_columnas = 25
umbral_longitud = 50  # Ajusta este valor según la longitud mínima para considerar cobertura

# Cargar la imagen
imagen = cv2.imread(imagen_path)
if imagen is None:
    print("No se pudo cargar la imagen.")
else:
    # Analizar cobertura vial con diagnóstico activado
    resultados_vial_gris = analizar_cuadriculas_vial_gris(imagen, num_filas, num_columnas, umbral_longitud, diagnostico=True)

    # Exportar resultados a Excel
    exportar_a_excel(resultados_vial_gris, "resultados_vial_german.xlsx")


def calcular_cobertura_vial_gris(cuadricula, umbral_longitud, diagnostico=False, nombre_archivo="", imagen_lineas=None, x_offset=0, y_offset=0):
    """
    Calcula la cobertura vial en una cuadrícula detectando áreas grises y contornos.
    """
    hsv = cv2.cvtColor(cuadricula, cv2.COLOR_BGR2HSV)
    gris_bajo = np.array([0, 0, 85])  # Tonos oscuros de gris
    gris_alto = np.array([180, 30, 250])  # Tonos claros de gris
    mascara_gris = cv2.inRange(hsv, gris_bajo, gris_alto)

    bordes = cv2.Canny(mascara_gris, 50, 150)

    contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    longitud_total = 0

    for contorno in contornos:
        longitud = cv2.arcLength(contorno, closed=False)
        if longitud > umbral_longitud:
            longitud_total += longitud
            if imagen_lineas is not None:
                cv2.drawContours(imagen_lineas, [contorno], -1, (0, 255, 0), 2, offset=(x_offset, y_offset))

    if diagnostico and nombre_archivo:
        diagnostico_img = cv2.cvtColor(mascara_gris, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(diagnostico_img, contornos, -1, (0, 255, 0), 2)
        cv2.imwrite(nombre_archivo, diagnostico_img)

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

def analizar_cuadriculas_vial_gris(imagen, num_filas, num_columnas, umbral_longitud, diagnostico=False):
    """
    Divide la imagen en cuadrículas y analiza la cobertura vial considerando solo tonalidades grises.
    """
    alto_img, ancho_img, _ = imagen.shape
    alto_cuadricula = alto_img // num_filas
    ancho_cuadricula = ancho_img // num_columnas

    matriz_resultados = np.zeros((num_filas, num_columnas), dtype=int)
    imagen_lineas = imagen.copy()

    for fila in range(num_filas):
        for columna in range(num_columnas):
            y_inicio = fila * alto_cuadricula
            y_fin = y_inicio + alto_cuadricula
            x_inicio = columna * ancho_cuadricula
            x_fin = x_inicio + ancho_cuadricula
            cuadricula = imagen[y_inicio:y_fin, x_inicio:x_fin]

            nombre_diagnostico = f"diagnostico_cuadricula_{fila}_{columna}.jpg" if diagnostico else ""
            cobertura = calcular_cobertura_vial_gris(
                cuadricula, umbral_longitud, diagnostico, nombre_diagnostico, imagen_lineas, x_inicio, y_inicio
            )
            matriz_resultados[fila, columna] = cobertura

    cv2.imwrite("lineas_detectadas_gris.jpg", imagen_lineas)
    print("Imagen final con carreteras grises detectadas guardada como 'lineas_detectadas_gris.jpg'.")
    return matriz_resultados

def exportar_a_excel_resultados(resultados, archivo_excel="resultadosvialalejo.xlsx"):
    """
    Exporta los resultados a diferentes hojas de un archivo Excel como porcentaje en formato numérico.
    """
    with pd.ExcelWriter(archivo_excel, engine='xlsxwriter') as writer:
        for tipo, matriz in resultados.items():
            df = pd.DataFrame(matriz / 100)
            df.columns = [f"Columna {i+1}" for i in range(matriz.shape[1])]
            df.index.name = "Fila"

            df.to_excel(writer, sheet_name=tipo.capitalize(), index=True, startrow=1)

            workbook = writer.book
            worksheet = writer.sheets[tipo.capitalize()]

            porcentaje_format = workbook.add_format({'num_format': '0.00%'})
            worksheet.set_column(1, matriz.shape[1], None, porcentaje_format)
            worksheet.set_column(0, 0, 10)
            worksheet.write(0, 0, f"Resultados de {tipo.capitalize()}", workbook.add_format({'bold': True, 'font_size': 14}))

    print(f"Resultados exportados a {archivo_excel} con formato de porcentaje.")

# Parámetros
imagen_path = "2023/colorimetria.JPG"  # Cambiar por la ruta de tu imagen
num_filas = 18
num_columnas = 25
umbral_longitud = 50  # Ajustar según la longitud mínima para considerar cobertura

# Cargar la imagen
imagen = cv2.imread(imagen_path)
if imagen is None:
    print("No se pudo cargar la imagen.")
else:
    resultados_vial_gris = analizar_cuadriculas_vial_gris(imagen, num_filas, num_columnas, umbral_longitud, diagnostico=True)

    resultados = {"vial_gris": resultados_vial_gris}
    exportar_a_excel_resultados(resultados, "resultados_vial_Alejo.xlsx")
