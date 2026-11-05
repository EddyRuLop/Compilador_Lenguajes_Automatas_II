# Revisión: funciones con delimitadores

Actualización del 5 de noviembre de 2026.

Las declaraciones y llamadas usan `/<nombre>/()`. Los identificadores siguen
la misma expresión regular que las variables. Sin paréntesis, `/<nombre>/`
se considera una variable. La sintaxis anterior, como `Suma()`, se rechaza.
Las funciones admiten parámetros tipados y llamadas con argumentos, incluidas
expresiones y llamadas anidadas. Los parámetros se declaran en el ámbito local
del cuerpo, que admite instrucciones y ciclos `while`.

## Implementación

- entrada.py distingue el identificador seguido de apertura de paréntesis y
  rechaza nombres sin delimitadores.
- sintaxis.py y expresiones.py conservan las comprobaciones de cabeceras y
  llamadas; sus mensajes explican el formato nuevo.
- simbolos.py separa las filas de variables y funciones. La tabla muestra
  `/<nombre>/` para variables y `/<nombre>/()` para funciones.
- funciones.py actualiza el tipo de la fila específica de función.
- Los ejemplos, resultados esperados y guía utilizan el nuevo formato.

La interfaz continúa vacía al iniciar y las pruebas permanecen separadas.
Se conservan las descripciones semánticas y las reglas de los PDF I–III
revisados en la entrega anterior.

## Verificación

Desde la carpeta del proyecto:

```bash
python -B -m unittest discover -s pruebas -q
```

Resultado: 79 pruebas aprobadas. Dos de ellas incluyen 4,000 entradas aleatorias
reproducibles en total. Las 67 pruebas anteriores se adaptaron al nuevo formato.
Se añadieron 7 pruebas de nombres homónimos con tipos distintos, independencia
entre variables y funciones, nombres numéricos, espacios y saltos, rechazo de
la sintaxis antigua y cadenas que contienen texto parecido a llamadas.

También pasan los casos anteriores de retornos, while, ámbitos, duplicadas,
indefinidas, incompatibilidades, límites y recuperación de entrada.

## Alcance

El programa analiza el código sin ejecutarlo. Comprueba la presencia de return,
no el retorno garantizado en todos los caminos. Los errores de escritura y
estructura se presentan como observaciones. Las pruebas respaldan los casos
ejecutados, no demuestran ausencia absoluta de defectos. La ventana no se
inspeccionó en una sesión gráfica en este entorno.

## Actualización: textos de tipo delta

Se eliminó el tipo interno de carácter. Todos los textos con comillas simples,
dobles o tipográficas se reconocen como CADENA y tienen tipo delta. Se admiten
textos vacíos o de varias letras también entre comillas simples.

Se añadieron cinco pruebas de clasificación, longitudes, funciones y while,
rechazo de texto en destinos numéricos y recuperación de comillas incompletas.
El ejemplo 07_textos_delta.txt produce cero errores y cero observaciones.
