import cv2
import numpy as np
import pandas as pd

def calcular_cobertura_por_cuadrante(mascara, umbral_porcentaje):
    """
    Calcula el porcentaje de cobertura en una cuadrícula basada en una máscara binaria,
    redondeando a 0, 25, 50, 75, o 100%.
    """
    pixeles_totales = mascara.size
    pixeles_detectados = cv2.countNonZero(mascara)
    porcentaje_cuadrante = (pixeles_detectados / pixeles_totales) * 100

    # Redondear al 25% más cercano
    if porcentaje_cuadrante >= umbral_porcentaje:
        if porcentaje_cuadrante <= 12.5:
            return 25
        elif porcentaje_cuadrante <= 37.5:
            return 50
        elif porcentaje_cuadrante <= 62.5:
            return 75
        else:
            return 100
    else:
        return 0
        

def analizar_cuadriculas(imagen, num_filas, num_columnas, tipo="vegetal"):
    """
    Divide la imagen en cuadrículas y analiza cada cuadrícula según el tipo especificado.
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
            
            if tipo == "vegetal":
                # Análisis de cobertura vegetal
                hsv = cv2.cvtColor(cuadricula, cv2.COLOR_BGR2HSV)
                verde_bajo = np.array([30, 20, 20])
                verde_alto = np.array([90, 255, 255])
                mascara = cv2.inRange(hsv, verde_bajo, verde_alto)
                umbral = 30  # Ajustar umbral para vegetación
            elif tipo == "urbanistico":
                # Análisis de cobertura urbanística
                gris = cv2.cvtColor(cuadricula, cv2.COLOR_BGR2GRAY)
                _, mascara = cv2.threshold(gris, 100, 255, cv2.THRESH_BINARY)
                umbral = 30  # Ajustar umbral para áreas urbanas
            elif tipo == "vial":
                # Análisis de cobertura vial
                gris = cv2.cvtColor(cuadricula, cv2.COLOR_BGR2GRAY)
                bordes = cv2.Canny(gris, 50, 150)  # Detección de bordes
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                mascara = cv2.dilate(bordes, kernel, iterations=1)
                umbral = 20  # Ajustar umbral para calles
            else:
                raise ValueError("Tipo no reconocido. Debe ser 'vegetal', 'urbanistico' o 'vial'.")
            
            cobertura_cuadrante = calcular_cobertura_por_cuadrante(mascara, umbral)
            matriz_resultados[fila, columna] = cobertura_cuadrante

    return matriz_resultados

def exportar_a_excel_resultados(resultados, archivo_excel="coberturaAlejo.xlsx"):
    """
    Exporta los resultados a diferentes hojas de un archivo Excel como porcentaje en formato numérico.
    """
    with pd.ExcelWriter(archivo_excel, engine='xlsxwriter') as writer:
        for tipo, matriz in resultados.items():
            # Convertir matriz a DataFrame y dividir entre 100 para porcentajes
            df = pd.DataFrame(matriz / 100)
            df.columns = [f"Columna {i+1}" for i in range(matriz.shape[1])]
            df.index.name = "Fila"
            
            # Escribir datos en el archivo Excel
            df.to_excel(writer, sheet_name=tipo.capitalize(), index=True)

            # Aplicar formato de porcentaje
            workbook = writer.book
            worksheet = writer.sheets[tipo.capitalize()]
            porcentaje_format = workbook.add_format({'num_format': '0.00%'})  # Formato porcentaje con dos decimales

            # Aplicar formato a todas las celdas del DataFrame
            worksheet.set_column(1, matriz.shape[1], None, porcentaje_format)  # Ajusta desde la columna 1
            worksheet.set_column(0, 0, 10)  # Ajusta ancho de la columna de filas

    print(f"Resultados exportados a {archivo_excel} con formato de porcentaje.")

# Parámetros
imagen_path = "2023/coberturaalejo2023.png"  # Reemplazar con tu imagen
num_filas = 18  # Número de filas para cuadrículas
num_columnas = 25  # Número de columnas para cuadrículas

# Cargar la imagen
imagen = cv2.imread(imagen_path)
if imagen is None:
    print("No se pudo cargar la imagen.")
else:
    # Realizar los análisis
    resultados = {
        "vegetal": analizar_cuadriculas(imagen, num_filas, num_columnas, tipo="vegetal"),
        "urbanistico": analizar_cuadriculas(imagen, num_filas, num_columnas, tipo="urbanistico"),
        "vial": analizar_cuadriculas(imagen, num_filas, num_columnas, tipo="vial")
    }
    
    # Exportar resultados
    exportar_a_excel_resultados(resultados)


    
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
imagen_path = "2023/coberturaalejo2023.png"  # Cambiar por la ruta de tu imagen
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

