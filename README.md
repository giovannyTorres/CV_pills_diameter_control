# Algoritmo de detección y dimensionamiento de capsulas (ADDC)

Este programa integra distintas funciones descritas a continuación para lograr la detección 
de un corte transversal de una capsula, para después poder dimensionarla, encontrando la razón
entre el diametro interior y el diametro exterior de esta.

## Uso de prueba

```python
	from función1 import pill_measuring
	
	ratio = pill_measuring(image)
```
Ademas de regresar la razon entre diametros (relacionada con el grosor de la pildora) 
guarda la imagen procesada en la carpeta especificada