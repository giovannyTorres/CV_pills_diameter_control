
import numpy as np
import cv2 as cv
import re
import matplotlib.pyplot as plt
import os
import imutils
import argparse

def angle_rotation(image):
    """ Determina el angulo de rotación para una imagen, de forma que la capsula quede lo mas recta posible, en referencia a la orientación de la imagen absoluta

    Args: 
        image (numpy.ndarray): imagen de entrada en el formato de un arreglo de numpy

    Ejemplo: 
        angulo = angle_rotation(imagen001)

    Returns:
        angle (float) = regresa el angulo en el que la imagen desea ser rotada 
    """
    # imagen en escala de grises
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # La imagen se pasa a binaria de tal modo que los mayores valores adoptan un valor a 0 (generalmente cerca de los bordes de los objetos en la imagen) y el resto toma un valor de 0
    mask = cv.adaptiveThreshold(
        gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV, 19, 5)
    # A partir de la imagen bicromática se extraen los contornos de la píldora y se ordenan de mayor a menor area
    cnts, __ = cv.findContours(
        mask.copy(), cv.RETR_CCOMP,    cv.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=lambda x: cv.contourArea(x), reverse=True)
    # A partir de los contornos extraídos, se aproxima una elipse para el contorno exterior de la capsula y se aísla de los demás elementos de la imagen
    ellipse_ext = cv.fitEllipse(cnts[0])
    x = np.zeros_like(gray)
    clean_ellipse = cv.ellipse(x, ellipse_ext, (255, 255, 255), 1)
    # Con la elipse aislada se crean las coordenadas y se determina el angulo que necesita rotarse la imagen para que la elipse esté orientada en dirección de alguno de los ejes y se rota una copia de la imagen original en blanco y negro
    coords = np.column_stack(np.where(clean_ellipse > 0))
    angle = cv.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    elif angle < 0:
        angle = -angle
    return angle


def imagerotation(image, angle):
    """Rota la imagen de entrada a partir de un angulo especificado, corrigiendo los cortes que provoca la función por defecto de opencv y quitando el fondo que causa un mal funcionamiento en el algoritmo de detección de contornos

    Args:
        image (numpy.ndarray): imagen original en el formato de un arreglo de numpy
        angle (float): angulo en el que se rotará la imagen

    Ejemplo:
        imagerotation(image001,45.0)

    Return:
        rotated (numpy.ndarray): imagen rotada en el angulo especificado, sin cortes, en el formato de un arreglo de numpy arreglo
    """
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # La imagen se pasa a binaria de tal modo que los mayores valores adoptan un valor a 0 (generalmente cerca de los bordes de los objetos en la imagen) y el resto toma un valor de 0
    mask = cv.adaptiveThreshold(
        gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV, 19, 5)
    # A partir de la imagen bicromática se extraen los contornos de la píldora y se ordenan de mayor a menor area
    cnts, __ = cv.findContours(
        mask.copy(), cv.RETR_CCOMP,    cv.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=lambda x: cv.contourArea(x), reverse=True)
    if len(cnts) > 0:
        # se extrae el contorno más grande y se crea una mascara para la capsula
        c = max(cnts, key=cv.contourArea)
        mask = np.zeros(gray.shape, dtype="uint8")
        cv.drawContours(mask, [c], -1, 255, -1)
        # Se calcula una caja que contenga a la capsula, se extrae la ROI (region of interest) y se aplica la mascara
        (x, y, w, h) = cv.boundingRect(c)
        imageROI = image[y:y + h, x:x + w]
        maskROI = mask[y:y + h, x:x + w]
        imageROI = cv.bitwise_and(imageROI, imageROI,
                                  mask=maskROI)
        # finalmente se rota la imagen en el angulo deseado
        rotated = imutils.rotate_bound(imageROI, angle)
    return rotated


def pill_measuring(image):
    """ A partir de los contornos de la píldora define cajas que contienen a los perímetros interior y exterior de la capsula, aproximándonos a elipses concéntricas determina la razón entre los diámetros mayores y los diámetros menores de cada perímetro

    Args: 
        image (str): nombre (path) de la imagen de la capsula que se va a procesar, la imagen debe ser clara, con iluminación constante y con el menor ruido de fondo

    Ejemplo:
        pill_measuring("A:/IoT Sellos/WIN_20220913_16_42_57_Pro.jpg")

    Return:
        ratio_average (float): Promedio de de las razones entre los diámetros exteriores e interiores (respectivamente), las especificaciones indican que este valor debe rondar entre 30% y 70%
    """
    # En caso de tener un path como image, esta parte del código extrae el nombre de la imagen para poder identificar la imagen de salida, en caso de que se remueva la parte del guardado de imágenes del código, esta parte tampoco es necesaria
    name = re.split(r'[\\,.,/]', image)[-2]
    # Se carga la imagen
    image = cv.imread(image)
    # Se define el angulo de rotación
    angle = angle_rotation(image)
    # Se rota la imagen el angulo especificado
    rotated = imagerotation(image, angle)
    # Con el Canny edge detector de opencv se detectan todos los bordes de la imagen rotada dependiendo de los limites especificados, a través de los dos operadores morfologicos, dilate y erode se afinan estos contornos para cerrar algunos que estén abiertos y  remover  ruido.
    rotated_gray = cv.cvtColor(rotated, cv.COLOR_BGR2GRAY)
    edged = cv.Canny(rotated_gray, 50, 120)
    edged = cv.dilate(edged, None, iterations=1)
    edged = cv.erode(edged, None, iterations=1)
    # Se encuentran los contornos de esta imagen en el formato de opencv y se ordenan de mayor a menor area
    cnts, hierarchy = cv.findContours(
        edged.copy(), cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=lambda x: cv.contourArea(x), reverse=True)
    # A partir de los contornos encontrados, se definen dos rectangulos que contengan a los dos contornos más grandes (respectivamente)
    x1, y1, w1, h1 = cv.boundingRect(cnts[0])
    x2, y2, w2, h2 = cv.boundingRect(cnts[1])
    # Con estos rectángulos se obtienen el ancho y el alto de cada caja y se interpretan como los diámetros mayor y menor de cada elipse y se gurdan en un diccionario dependiendo de a que contorno pertenecen
    diametros = {}
    diametros['contorno exterior'] = [w1, h1]
    diametros['contorno interior'] = [w2, h2]
    # Se ordenan los elementos de cada lista de diametros
    diametros['contorno exterior'].sort(reverse=True)
    diametros['contorno interior'].sort(reverse=True)
    # Se calculan los radios superior (del diametros mayores), inferior (diametros menores) y el average (promedio de los últimos dos)
    ratio_sup = diametros['contorno interior'][0] / \
        diametros['contorno exterior'][0]
    ratio_inf = diametros['contorno interior'][1] / \
        diametros['contorno exterior'][1]
    ratio_avg = (ratio_sup+ratio_inf)/2
    # Se almacenan en un diccionario
    ratios = {'ratio_average': ratio_avg,
              'ratio_D': ratio_sup, 'ratio_d': ratio_inf}
    # visualización de imágenes, se crea una copia de la imagen original rotada y se dibujan las cajas en ella para después guardar esta imagen
    img_copy = rotated.copy()
    plt.rcParams['figure.dpi'] = 150
    ax = plt.gca()
    ax.axes.xaxis.set_ticks([])  # quita labels/ticks de la imagen ploteada
    ax.axes.yaxis.set_ticks([])
    plt.imshow(cv.drawContours(img_copy, cnts, 0, (255, 0, 0), 1))
    plt.imshow(cv.drawContours(img_copy, cnts, 1, (255, 0, 0), 1))
    plt.imshow(cv.rectangle(img_copy, (x1, y1),
                            (x1+w1, y1+h1), (51, 255, 57), 2))
    plt.imshow(cv.rectangle(img_copy, (x2, y2),
                            (x2+w2, y2+h2), (51, 255, 57), 2))
    plt.title(f'{name}')
    # path donde se guarda la imagen de salida
    plt.savefig(os.path.join("..", "Funciones RP",
                "img_output", f"{name}_output.png"))
    cv.imshow("Cápsula dimensionada", img_copy)
    cv.waitKey(0)
    cv.destroyAllWindows()

    return ratios

def main():
    '''Método de entrada de la imagen para la ejecución del script
    '''
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True,
                    help="path to the input image")
    args = vars(ap.parse_args())
    pill_measuring(args["image"])
    
if __name__ == "__main__":
    main()
