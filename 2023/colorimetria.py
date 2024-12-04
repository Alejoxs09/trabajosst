import cv2
import numpy as np
import matplotlib.pyplot as plt

# Cargar la imagen
imagen = cv2.imread("2023/colorimetria.JPG")
if imagen is None:
    print("No se pudo cargar la imagen.")
    exit()

# Convertir la imagen al espacio de color HSV
imagen_hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

# Mostrar la imagen original
plt.figure(figsize=(10, 6))
plt.title("Imagen Original")
plt.imshow(cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB))
plt.axis("off")
plt.show()

# Usar la función de OpenCV para seleccionar colores en la imagen
def seleccionar_color(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # Obtener el color HSV del píxel seleccionado
        pixel = imagen_hsv[y, x]
        print(f"Pixel seleccionado en (x={x}, y={y}): HSV = {pixel}")

# Crear una ventana para seleccionar el color
cv2.namedWindow("Selecciona un color")
cv2.setMouseCallback("Selecciona un color", seleccionar_color)

while True:
    cv2.imshow("Selecciona un color", imagen)
    if cv2.waitKey(1) & 0xFF == 27:  # Presiona 'Esc' para salir
        break

cv2.destroyAllWindows()
