# Algoritmo de detección y dimensionamiento de capsulas (ADDC)

Este programa integra distintas funciones descritas a continuación para lograr la detección 
de un corte transversal de una capsula, para después poder dimensionarla, encontrando la razón
entre el diámetro interior y el diámetro exterior de esta.

Se divide en tres partes fundamentales que se concentran en la función "pill_measuring" y se siguen los siguientes pasos para el procesado de la imagen:

1. Carga de la imagen.
2. Preprocesado de la imagen. Aproximación de la capsula a una elipse limpia. Se necesita aproximar 
la capsula a una elipse para poder determinar su ángulo de rotación.  
3. Rotación de la imagen. Este paso es necesario ya que la orientación de la capsula varía entre 
imágenes, y se requiere medir puntos equivalentes de cada perímetro de las elipses aproximadas
para una mejor precisión y la rotación de la capsula facilita este proceso. 
4. Detección de contornos. Se detectan los contornos de la imagen rotada, tomando solo los más 
grandes (debiendo corresponder estos a los de la capsula) para después aproximar las cajas de las cuales se extraen sus medidas de alto y ancho. 
5. Cálculo de la razón entre los diámetros mayores y diámetros menores de cada perímetro, debiendo corresponder estos diámetros a los altos y los anchos de cada caja.

En el estado actual del algoritmo con las imágenes de prueba se tiene un 66.66% de éxito (18/27 imágenes), siento posible una mejora en el proceso de remoción de ruido y realzamiento de bordes
en el algoritmo. 

Sin embargo, bajo las siguientes condiciones el algoritmo promete un funcionamiento adecuado. 

1. Imagen clara. Sin perturbaciones más grandes que la capsula, buena resolución (mayor a 300x300 px). Mientras mayor sea la resolución mayor será la precisión de la razón obtenida,
sin embargo, una resolución muy grande puede comprometer la remoción de ruido y el costo computacional. 
2. Buena iluminación, sin destellos, brillos o reflejos en la superficie de la capsula.
3. Imágenes bien enfocadas (sin zonas borrosas), sin efectos de blur o distorsión.
4. Imagen centrada. Que la cápsula esté centrada en la imagen y en caso de ser elíptica, tener sus ejes paralelos a los de la imagen. 
5. Sin sombras. Relacionándolo con la iluminación, que esta sea directa, de modo que no se causen sombras, las cuales comprometen de manera drástica la calidad de 
los resultados. 
6. Fondo sin ruido. El fondo debe ser liso y de un color que sea distinto al de las píldoras, de modo que estas puedan resaltar y distinguirse de manera fácil.
 Para las cápsulas transparentes servirá que este fondo sea liso y sin ruido, llámese ruido a todo desperfecto en la superficie (agujeros, hundimientos, rayones, pelusa etc.) que cause sombras, alteraciones en el perímetro de la cápsula etc. 
7. El algoritmo intenta que toda la cápsula se contenga en las cajas calculadas, de modo que toda irregularidad como protuberancias o bultos, 
serán captados por el algoritmo y se incluirán como parte de la cápsula, afectando así los resultados, se recomienda que las capsulas sean uniformes. 

Se explica el funcionamiento de las funciones principales a continuación. 

### Definición del ángulo de rotación automática 

Determina el ángulo de rotación para una imagen, de forma que la capsula quede lo más recta 
posible, en referencia a la orientación de la imagen absoluta.

Argumentos: 

- image (numpy.ndarray): imagen de entrada en el formato de un arreglo de numpy

*Ejemplo*:
 
```python
	ángulo = angle_rotation(imagen001)
```
Retorna:

- angle (float) = regresa el ángulo en el que la imagen desea ser rotada 

### Rotación de la imagen

Rota la imagen de entrada a partir de un ángulo especificado, corrigiendo los cortes que provoca 
la función por defecto de opencv y quitando el fondo que causa un mal funcionamiento en el 
algoritmo de detección de contornos.

Argumentos:

- image (numpy.ndarray): imagen original en el formato de un arreglo de numpy
- angle (float): ángulo en el que se rotará la imagen

*Ejemplo*:
```python
        imagerotation(image001,45.0)
```
Retorna:

- rotated (numpy.ndarray): imagen rotada en el ángulo especificado, sin cortes, en el formato de un arreglo de numpy arreglo

### Detección de la píldora y dimensionamiento 

A partir de los contornos de la píldora define cajas que contienen a los perímetros interior y 
exterior de la capsula, aproximándonos a elipses concéntricas, se determinan dos cajas rectangulares 
que contengan estas elipses, de forma que a través de las medidas de estas cajas (alto y ancho)
se pueda determinar la razón entre los diámetros mayores y los diámetros menores de cada 
perímetro.


Argumentos: 

- image (str): nombre (path) de la imagen de la capsula que se va a procesar, la imagen debe ser clara, con iluminación constante y con el menor ruido de fondo

*Ejemplo*:
```python
        pill_measuring("A:/IoT Sellos/WIN_20220913_16_42_57_Pro.jpg")
```
Return:

- ratios(dict): Diccionario de las razones entre los diámetros exteriores e interiores (respectivamente) y el promedio de estos, las especificaciones indican que este valor debe rondar entre 30% y 70%

## Uso de prueba

```python
	from función1 import pill_measuring
	ratio = pill_measuring(image)
```

##Consola
```console
 (Pillmeasuring) A:\Funciones RP>python función1.py -i "A:\Funciones RP\imagenes_prueba\Lote_1\5529D0A6A1814E1E8FF414AEC8F3A57E.png"
 
 (Pillmeasuring) A:\Funciones RP>python función1.py --image "A:\Funciones RP\imagenes_prueba\Lote_1\5529D0A6A1814E1E8FF414AEC8F3A57E.png"
```
Return:

![imagen de salida](https://github.com/giovannyTorres/CV_pills_diameter_control/blob/dev/img_output/Casos%20de%20exito/5529D0A6A1814E1E8FF414AEC8F3A57E_output.png)

Además de regresar la razón entre diámetros (relacionada con el grosor de la píldora) 
guarda la imagen procesada en la carpeta especificada.
