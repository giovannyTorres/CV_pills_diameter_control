# Descripción de lo que hace el programa
# %% importar paquetes
import numpy as np
import cv2 as cv
import imutils
import re
import matplotlib.pyplot as plt
import os
# %%


def pill_measuring(image):
    """ A partir de los contornos de la píldora define cajas que contienen a los perímetros interior y exterior de la capsula, aproximándonos a elipses concéntricas determina la razón entre los diámetros mayores y los diámetros menores de cada perímetro

    Args: 
        image (str): nombre (path) de la imagen de la pildora que se va a procesar, la imagen debe ser clara, con iluminación constante y con el menor ruido de fondo. 

    Ejemplo:
        pill_measuring(A:/IoT Sellos/WIN_20220913_16_42_57_Pro.jpg)
     A:\Funciones RP\dummy img\IoT Sellos\Muestras sellos\WIN_20220913_16_08_37_Pro.jpg
    Return:
        ratios(dict): Diccionario de las razones entre los diámetros exteriores e interiores (respectivamente) y el promedio de estos, las especificaciones indican que este valor debe rondar entre 30% y 70%.
    """
    # En caso de tener un path como image, esta parte del código extrae el nombre de la imagen para poder identificar la imagen de salida, en caso de que se remueva la parte del guardado de imágenes del código, esta parte tampoco es necesaria
    #name = re.sub(r'[\]', '/', image)
    name = re.split(r'[\\,.,]', image)[-2]
    # Se carga la imagen en blanco y negro
    image = cv.imread(image, 0)
    # La imagen se pasa a binaria de tal modo que los mayores valores adoptan un valor a 0 (generalmente cerca de los bordes de los objetos en la imagen) y el resto toma un valor de 0
    mask = cv.adaptiveThreshold(
        image, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV, 19, 5)
    # A partir de la imagen bicromática se extraen los contornos de la píldora y se ordenan de mayor a menor area
    cnts, __ = cv.findContours(
        mask.copy(), cv.RETR_CCOMP,    cv.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=lambda x: cv.contourArea(x), reverse=True)
    # A partir de los contornos extraídos, se aproxima una elipse para el contorno exterior de la capsula y se aísla de los demás elementos de la imagen
    ellipse_ext = cv.fitEllipse(cnts[0])
    x = np.zeros_like(image)
    clean_ellipse = cv.ellipse(x, ellipse_ext, (255, 255, 255), 1)
    # Con la elipse aislada se crean las coordenadas y se determina el angulo que necesita rotarse la imagen para que la elipse esté orientada en dirección de alguno de los ejes y se rota una copia de la imagen original en blanco y negro
    coords = np.column_stack(np.where(clean_ellipse > 0))
    angle = cv.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    rotated = imutils.rotate_bound(image.copy(), angle)
    # Con el Canny edge detector de opencv se detectan todos los bordes de la imagen rotada dependiendo de los limites especificados, a través de los dos operadores morfologicos, dilate y erode se afinan estos contornos para cerrar algunos que estén abiertos y  remover  ruido.
    edged = cv.Canny(rotated, 50, 120)
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
    ax = plt.gca()
    ax.axes.xaxis.set_ticks([]) #quita labels/ticks de la imagen ploteada
    ax.axes.yaxis.set_ticks([])
    plt.imshow(cv.rectangle(img_copy, (x1, y1),
                            (x1+w1, y1+h1), (255, 0, 100), 1))
    plt.imshow(cv.rectangle(img_copy, (x2, y2),
                            (x2+w2, y2+h2), (255, 0, 100), 1))
    plt.savefig(os.path.join("..","Funciones RP", "img_output",f"{name}_output.png")) #path donde se guarda la imagen de salida
    return ratios
# %%
