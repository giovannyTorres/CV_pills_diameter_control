#%%
from scipy.spatial import distance as dist
from imutils import perspective
import numpy as np
import imutils
import cv2

def midpoint(ptA, ptB): #calcular el punto medio 
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

def pill_measuring(image,time,ID):

    # Cargar la imagen
    image = cv2.imread(image,0)
    #img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #ret, thresh = cv2.threshold(image, 155, 255, 0)
    #gray = cv2.GaussianBlur(image, (5, 5), 0) #Blur Gaussiano para filtrado de ruido y cerrado de bordes
    mask = cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,19,5)
    #edged = cv2.Canny(gray, 0, 255) #Detectar bordes
    #edged = cv2.dilate(edged, None, iterations=1) #dilatar
    #edged = cv2.erode(edged, None, iterations=1) #erosionar
    # find contours in the edge map
    cnts, __ = cv2.findContours(mask.copy(), cv2.RETR_CCOMP,    cv2.CHAIN_APPROX_SIMPLE)
        #(cnts, _) = contours.sort_contours(cnts)
    cnts = sorted(cnts,key=len,reverse=True)

    D_lst = []
    # iterar a través de cada contorno
    for c in cnts[:]:
        # ignorar si el contorno no es sificientemente grande
        if cv2.contourArea(c) < 5000:
            continue
        # Calcular la caja del contorno
        orig = image.copy() #copia de la imagen
        ellipse = cv2.fitEllipse(c)
        x = np.zeros_like(orig)
        cv2.ellipse(x,ellipse,(255,255,255),1)
        cont, __ = cv2.findContours(
        x.copy(),  cv2.RETR_CCOMP,    cv2.CHAIN_APPROX_NONE)
        #(cnts, _) = contours.sort_contours(cnts)
        cont = sorted(cont, key=len, reverse=True)
        box = cv2.minAreaRect(cont[0])  #rectangulo rotado en la dirección del objeto
        box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box) #puntos para dibujar el rectangulo
        box = np.array(box, dtype="int") 
        # order the points in the contour such that they appear
        # in top-left, top-right, bottom-right, and bottom-left
        # order, then draw the outline of the rotated bounding
        # box
        box = perspective.order_points(box)
        cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)
        # loop over the original points and draw them
        for (x, y) in box:
            cv2.circle(orig, (int(x), int(y)), 2, (0, 0, 255), -1)

        # unpack the ordered bounding box, then compute the midpoint
        # between the top-left and top-right coordinates, followed by
        # the midpoint between bottom-left and bottom-right coordinates
        (tl, tr, br, bl) = box
        (tltrX, tltrY) = midpoint(tl, tr)
        (blbrX, blbrY) = midpoint(bl, br)
        # compute the midpoint between the top-left and top-right points,
        # followed by the midpoint between the top-righ and bottom-right
        (tlblX, tlblY) = midpoint(tl, bl)
        (trbrX, trbrY) = midpoint(tr, br)
        # draw the midpoints on the image
        cv2.circle(orig, (int(tltrX), int(tltrY)), 2, (255, 10, 0), -1)
        cv2.circle(orig, (int(blbrX), int(blbrY)), 2, (255, 10, 0), -1)
        cv2.circle(orig, (int(tlblX), int(tlblY)), 2, (255, 10, 0), -1)
        cv2.circle(orig, (int(trbrX), int(trbrY)), 2, (255, 10, 0), -1)
        # draw lines between the midpoints
        cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
            (255, 0, 255), 2)
        cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
            (255, 0, 255), 2)
        # compute the Euclidean distance between the midpoints
        dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
        dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
        
        D_lst.append(dA)
        D_lst.append(dB)
        # draw the object sizes on the image

        cv2.putText(orig, "{:.2f}pix".format(dA),
            (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
            0.65, (255, 255, 255), 2)
        cv2.putText(orig, "{:.2f}pix".format(dB),
            (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
            0.65, (255, 255, 255), 2)
        # show the output image
        cv2.imshow("Image", orig)
        cv2.waitKey(0)

    D_lst.sort(reverse=True)
    ratio1 = 100*D_lst[1]/D_lst[0]
    ratio2 = 100*D_lst[3]/D_lst[2]
    ratio_prom = (ratio1+ratio2)/2
    return D_lst,ratio1,ratio2,ratio_prom

# %%
