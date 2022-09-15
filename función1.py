#%%
from scipy.spatial import distance as dist
from imutils import perspective
import numpy as np
import imutils
import cv2

def midpoint(ptA, ptB): #calcular el punto medio 
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

def pill_measuring(image):
    # Cargar la imagen
    image = cv2.imread(image,0)
    
    mask = cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,19,5)
    cnts, __ = cv2.findContours(mask.copy(), cv2.RETR_CCOMP,    cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=lambda x: cv2.contourArea(x), reverse=True)

    Dimensiones = []
    # iterar a través de cada contorno
    for c in cnts[:]:
        D_d = {}
        # ignorar si el contorno no es sificientemente grande
        if cv2.contourArea(c) < 5000:
            continue
        orig = image.copy() #copia de la imagen
        ellipse = cv2.fitEllipse(c)
        x = np.zeros_like(image)
        cv2.ellipse(x,ellipse,(255,255,255),1)
        cont, __ = cv2.findContours(
        x.copy(),  cv2.RETR_CCOMP,    cv2.CHAIN_APPROX_NONE)
        cont = sorted(cnts, key=lambda x: cv2.contourArea(x), reverse=True)
        box = cv2.minAreaRect(cont[0]) 
        box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box) #puntos para dibujar el rectangulo
        box = np.array(box, dtype="int") 
        box = perspective.order_points(box)
        cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 1)

        for (x, y) in box:
            cv2.circle(orig, (int(x), int(y)), 2, (0, 0, 255), -1)

        (tl, tr, br, bl) = box
        (tltrX, tltrY) = midpoint(tl, tr)
        (blbrX, blbrY) = midpoint(bl, br)
    
        (tlblX, tlblY) = midpoint(tl, bl)
        (trbrX, trbrY) = midpoint(tr, br)

        cv2.circle(orig, (int(tltrX), int(tltrY)), 2, (255, 10, 0), -1)
        cv2.circle(orig, (int(blbrX), int(blbrY)), 2, (255, 10, 0), -1)
        cv2.circle(orig, (int(tlblX), int(tlblY)), 2, (255, 10, 0), -1)
        cv2.circle(orig, (int(trbrX), int(trbrY)), 2, (255, 10, 0), -1)

        cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
            (255, 0, 255), 2)
        cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
            (255, 0, 255), 2)

        dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
        dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
        
        if dA > dB : D_d['Diametro_mayor'],D_d['Diametro_menor'] = dA,dB 
        else:  D_d['Diametro_mayor'],D_d['Diametro_menor'] = dB,dA
        
        Dimensiones.append(D_d)
        

    Dimensiones = sorted(Dimensiones, key= lambda d:d['Diametro_mayor'],reverse=True)
    ratios = {}
    ratios['ratioD'] = Dimensiones[1]['Diametro_mayor']/Dimensiones[0]['Diametro_mayor']
    ratios['ratiod'] = Dimensiones[1]['Diametro_menor']/Dimensiones[0]['Diametro_menor']
    ratios['ratioAvg'] = (ratios['ratioD'] + ratios['ratiod'])/2
    
    data = {'Dimensiones': Dimensiones, 'Ratios':ratios}
    return data

# %%

def check_criteria(data):
    ratio_sup = 0.7
    ratio_inf = 0.3

    check = False
    if (data['Ratios']['ratioAvg'] > ratio_inf) and (data['Ratios']['ratioAvg'] < ratio_sup):
        check = True
    
    return check
#%%







