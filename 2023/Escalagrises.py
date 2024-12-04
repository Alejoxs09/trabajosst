import cv2
import numpy as np

# Función para detectar grises en el rango HSV
def detectar_grises_hsv(imagen):
    """
    Detecta los tonos grises en la imagen utilizando el espacio HSV.
    """
    # Convertir la imagen a HSV
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

    # Definir el rango de grises en HSV
    gris_bajo = np.array([0, 0, 50])  # Bajo: Tonos bajos de saturación y brillo
    gris_alto = np.array([180, 50, 220])  # Alto: Tonos bajos de saturación y brillo, hasta blanco

    # Crear una máscara para los tonos grises
    mascara_gris = cv2.inRange(hsv, gris_bajo, gris_alto)

    # Aplicar la máscara a la imagen original para ver solo las áreas grises
    imagen_gris = cv2.bitwise_and(imagen, imagen, mask=mascara_gris)

    return imagen_gris, mascara_gris

# Cargar la imagen
imagen_path = "2023/colorimetria.jpg"  # Reemplaza con la ruta de tu imagen
imagen = cv2.imread(imagen_path)

# Verifica si la imagen fue cargada correctamente
if imagen is None:
    print("No se pudo cargar la imagen.")
else:
    # Detectar los tonos grises
    imagen_gris, mascara_gris = detectar_grises_hsv(imagen)

    # Mostrar la imagen con los tonos grises detectados
    cv2.imshow("Imagen con tonos grises", imagen_gris)
    cv2.imshow("Máscara de grises", mascara_gris)

    # Espera hasta que se presione una tecla para cerrar
    cv2.waitKey(0)
    cv2.destroyAllWindows()
