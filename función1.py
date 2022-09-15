# %% importar paquetes
from scipy.spatial import distance as dist
from imutils import perspective
import numpy as np
import imutils
import cv2 as cv

#%% definir funciones 
def midpoint(ptA, ptB):  # calcular el punto medio
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

def Modifiedrotation(rotateImage, angle):
   
    
    imgHeight, imgWidth = rotateImage.shape[0], rotateImage.shape[1]
 
    
    
    centreY, centreX = imgHeight//2, imgWidth//2
 
    
    rotationMatrix = cv.getRotationMatrix2D((centreY, centreX), angle, 1.0)
 
    
    
    cosofRotationMatrix = np.abs(rotationMatrix[0][0])
    sinofRotationMatrix = np.abs(rotationMatrix[0][1])
 
    
    
    
    newImageHeight = int((imgHeight * sinofRotationMatrix) +
                         (imgWidth * cosofRotationMatrix))
    newImageWidth = int((imgHeight * cosofRotationMatrix) +
                        (imgWidth * sinofRotationMatrix))
 
    
    
    rotationMatrix[0][2] += (newImageWidth/2) - centreX
    rotationMatrix[1][2] += (newImageHeight/2) - centreY
 
    
    rotatingimage = cv.warpAffine(
        rotateImage, rotationMatrix,(newImageWidth, newImageHeight))
 
    return rotatingimage
# %%
def pill_measuring(image):
    # Cargar la imagen
    image = cv.imread(image, 0)
    mask = cv.adaptiveThreshold(
        image, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV, 19, 5)

    cnts, __ = cv.findContours(
        mask.copy(), cv.RETR_CCOMP,    cv.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=lambda x: cv.contourArea(x), reverse=True)
    ellipse_ext = cv.fitEllipse(cnts[0])
    x = np.zeros_like(image)
    clean_ellipse = cv.ellipse(x, ellipse_ext, (255, 255, 255), 1)

    coords = np.column_stack(np.where(clean_ellipse > 0))
    angle = cv.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
        # otherwise, just take the inverse of the angle to make
        # it positive
    else:
        angle = -angle

    # rotate the image to deskew it
    rotated = Modifiedrotation(image,angle) 
    edged = cv.Canny(rotated, 50, 120)
    edged = cv.dilate(edged, None, iterations=1)
    edged = cv.erode(edged, None, iterations=1)
    cnts, hierarchy = cv.findContours(edged.copy(), cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=lambda x: cv.contourArea(x), reverse=True)
    x1, y1, w1, h1 = cv.boundingRect(cnts[0])
    x2, y2, w2, h2 = cv.boundingRect(cnts[1])
    diametros = {}
    diametros['contorno exterior'] = [w1,h1]
    diametros['contorno interior'] = [w2,h2]
    
    diametros['contorno exterior'].sort(reverse=True)
    diametros['contorno interior'].sort(reverse=True)

    ratio_sup = diametros['contorno interior'][0]/diametros['contorno exterior'][0]
    ratio_inf = diametros['contorno interior'][1]/diametros['contorno exterior'][1]

    ratio_avg = (ratio_sup+ratio_inf)/2

    ratios = {'ratio_average':ratio_avg,'ratio_D':ratio_sup,'ratio_d':ratio_inf}
    #visualización de imágenes
    
    return ratios 
# %%
