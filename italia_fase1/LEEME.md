# Compilador Italia — guía de entrega y explicación

## 1. Cómo iniciar

Extrae todo el ZIP y abre la carpeta `italia_fase1` en VS Code. En una terminal ubicada en esa carpeta ejecuta:

```bash
python main.py
```

En Windows también puedes usar `py main.py`. Se necesita Python 3.9 o posterior con Tkinter. El proyecto utiliza la biblioteca estándar; no necesita paquetes de pip.

La ventana inicia con el editor y ambas tablas vacíos. Escribe o pega tu código y pulsa **Analizar**. A la izquierda se muestra la tabla de símbolos y a la derecha la de errores semánticos. Si hay problemas de escritura o estructura, aparece una ventana con las observaciones correspondientes.

Las pruebas no se cargan ni se ejecutan al abrir el programa. Para probar manualmente un ejemplo, abre uno de los archivos de `pruebas/ejemplos/`, copia su contenido y pégalo en el editor.

## 2. Qué se hizo en esta revisión

Actualización de textos: todos los literales de texto se reconocen como `CADENA` y tienen tipo `delta`. Se actualizaron las reglas, la tabla de símbolos y las condiciones while.

1. Se conservan las reglas revisadas contra los PDF I, II y III. Las funciones ahora se declaran y llaman como `/<nombre>/()` por petición del equipo.
2. Se actualizaron los ejemplos y las pruebas. Las 79 pruebas pasaron, incluidas 4,000 entradas aleatorias reproducibles dentro de dos pruebas.
3. Se retiró el ejemplo del arranque. El texto original quedó en `pruebas/ejemplos/00_ejemplo_anterior.txt`.
4. Se reunieron todos los ejemplos y las pruebas en la carpeta `pruebas/`.
5. Se preparó un ZIP limpio, sin cachés de Python, versiones anteriores, herramientas de trabajo ni copias de los PDF.
6. Se sustituyó la documentación anterior por esta guía y un informe de verificación dentro de `pruebas/`.

Se actualizó el reconocimiento de funciones y sus filas en la tabla de símbolos. `/<dato>/` es variable y `/<dato>/()` es función. Las descripciones semánticas y las reglas de tipos se mantienen. La interfaz continúa vacía al abrirse.

La revisión confirma los casos comprobados; no constituye una garantía de que no pueda existir ningún fallo. Las protecciones que ya tenía el programa se conservaron y se probaron. La ventana no se volvió a inspeccionar en una sesión gráfica en este entorno; se revisaron su código y el arranque, y se comprobó que el programa es independiente de las pruebas.

## 3. Qué hace esta fase

El programa es un analizador de código fuente. Lee instrucciones, reconoce sus componentes y comprueba que los identificadores y los tipos se usen correctamente. Produce una tabla de símbolos, una tabla de errores y observaciones de entrada.

No calcula los resultados de las operaciones ni ejecuta los ciclos o las funciones del lenguaje. Por ejemplo, `while (1 == 1) {}` se analiza sin entrar en un ciclo infinito del programa fuente. Tampoco genera código máquina. Esto corresponde al alcance de esta primera fase.

## 4. Carpetas de la entrega

| Carpeta | Contenido y propósito |
|---|---|
| `italia_fase1/` | Los quince módulos necesarios para abrir la interfaz y realizar el análisis, junto con esta guía. |
| `italia_fase1/pruebas/` | Pruebas automáticas que se ejecutan solo mediante una orden manual, y el informe de revisión. |
| `italia_fase1/pruebas/ejemplos/` | Código fuente de ejemplo para copiar al editor y resultados esperados. |

La aplicación funciona aunque se retire la carpeta `pruebas/`. Los módulos `.py` de la carpeta principal deben permanecer juntos porque se importan entre sí.

## 5. Recorrido del código dentro del programa

1. `main.py` abre la interfaz.
2. El usuario escribe y pulsa **Analizar**.
3. `interfaz.py` entrega el texto a `analizar()`.
4. `entrada.py` transforma el texto en tokens.
5. `sintaxis.py` reconoce las instrucciones; `expresiones.py` comprueba sus expresiones.
6. `simbolos.py` prepara los lexemas y administra los nombres declarados.
7. `analizador.py` recorre las instrucciones y llama a las comprobaciones necesarias.
8. Los errores y observaciones se guardan en un `Resultado`.
9. `interfaz.py` utiliza ese resultado para llenar las tablas.

Un **lexema** es el texto concreto, por ejemplo `25.5` o `/<num1>/`. Un **token** es el registro que acompaña ese texto con su categoría, línea y columna. El tipo léxico `REAL` se traduce al tipo semántico `rho`.

## 6. Explicación de cada archivo

### `main.py`: punto de entrada

Importa `iniciar` desde la interfaz. La condición `if __name__ == '__main__':` permite abrir la ventana cuando ejecutas este archivo directamente. Si otro archivo lo importa, no abre la ventana automáticamente. Es pequeño porque su responsabilidad es iniciar la aplicación.

### `interfaz.py`: entrada y presentación de resultados

Utiliza Tkinter. `crear_tabla()` construye una tabla con sus columnas y barras de desplazamiento. `llenar()` elimina las filas del análisis anterior y agrega las nuevas. `iniciar()` crea la ventana, el editor, el botón y las dos tablas.

Dentro de `iniciar()` se define `ejecutar()`, la función asociada al botón. Obtiene el texto del editor, llama al analizador y presenta sus resultados. Si existen observaciones, abre una ventana adicional para mostrarlas. No decide qué tipo de dato es correcto: esa decisión corresponde a los módulos del análisis.

El editor no recibe ningún texto al construirse. Analizar una entrada vacía devuelve tablas vacías y cero errores.

### `modelos.py`: registros compartidos

Define tres clases sencillas mediante `@dataclass`:

- `Token`: guarda `clase`, `lexema`, `linea` y `columna`.
- `Instruccion`: guarda la clase de instrucción, su token inicial, nombres, tipo declarado, expresión y expresión postfija.
- `Resultado`: guarda las listas de símbolos, errores y observaciones.

Una dataclass genera automáticamente el constructor del registro. `field(default_factory=list)` crea una lista nueva para cada objeto, evitando compartir resultados entre análisis distintos.

`Resultado.error()` crea una fila con `Token`, `Lexema`, `Renglón` y `Descripción`. Los códigos se numeran `ErrSem1`, `ErrSem2`, etc. `Resultado.avisar()` agrega una observación con línea y columna.

### `reglas.py`: reglas y nombres comunes

Centraliza los tipos `phi`, `rho` y `delta`, las descripciones de error y los operadores. `TIPOS_ADMITIDOS` indica qué tipos puede recibir un destino. `OPERADORES_ADMITIDOS` indica qué operadores admite ese destino. `TIPOS_LITERAL` relaciona las categorías de los literales con sus tipos.

La condición `tipo in conjunto` permite consultar una regla sin escribir muchas comparaciones repetidas. Las descripciones se definen aquí para mantener la misma escritura en todos los errores.

### `entrada.py`: reconocimiento de tokens

`tokenizar()` recorre el texto con un índice y conserva la línea y columna. Reconoce identificadores, tipos, nombres de funciones, números, cadenas, operadores, llaves y separadores.

Reconoce `/<` antes de considerar `/` como división. Comprueba el identificador completo mediante una expresión regular. Un número como `12abc` o `1.2.3` se conserva como una unidad inválida: no se separa artificialmente en fragmentos válidos.

Dentro de comillas, los símbolos son parte del literal. Por eso `"while { /<x>/"` es una cadena y no varias instrucciones. Los comentarios empiezan con `#` fuera de las comillas. Se normalizan los saltos de línea de Windows.

Cada recorrido consume caracteres o termina. Existen límites de 250,000 caracteres y 50,000 tokens; si se superan, se devuelve una observación en vez de intentar seguir procesando toda la entrada.

### `sintaxis.py`: reconocimiento de instrucciones

`separar()` agrupa los tokens en declaraciones, asignaciones, llamadas, funciones, retornos y bloques `while`. Mantiene una pila para recordar qué bloques están abiertos. Si faltan llaves, informa el problema y genera cierres internos para terminar el análisis de forma ordenada; no modifica el texto del usuario.

`construir()` valida una instrucción individual. Por ejemplo, una declaración debe contener identificadores separados por comas. Si la declaración está mal escrita, no registra parcialmente las primeras variables como si toda ella fuera válida.

`cabecera_funcion()` reconoce `tipo /<Nombre>/() {`. `siguiente_visible()` permite saltos de línea entre partes de una cabecera. Una función declarada dentro de otra función o de un `while` se rechaza y su cuerpo se aísla durante la recuperación.

El punto y coma o un salto de línea pueden terminar una instrucción. Dentro de paréntesis se admite continuar en otra línea. Una sentencia dañada se descarta o recupera hasta un límite seguro para intentar revisar las siguientes.

### `expresiones.py`: operandos, operadores y paréntesis

`reconocer_llamadas()` reconoce una secuencia como `/<Suma>/ ( )` y la representa internamente como un operando de clase `LLAMADA`. Los tokens originales conservan los paréntesis como signos separados. No se admiten argumentos.

`validar()` comprueba que los operandos y operadores estén colocados correctamente y que los paréntesis estén equilibrados. Por ejemplo, detecta `1 2`, `1 +` y `(1 + 2`.

Utiliza una lista de salida y una pila de operadores. La precedencia establece que la multiplicación se procesa antes que la suma. Una expresión como `1 + 2 * 3` se representa en postfija como `1 2 3 * +`. Esa representación sirve para comprobar el tipo de una condición de `while`; no evalúa valores numéricos.

No usa `eval` ni ejecuta el texto del usuario como Python. El reconocimiento es iterativo, por lo que no necesita una llamada recursiva por cada paréntesis.

### `simbolos.py`: tabla y ámbitos

La clase `Simbolos` realiza dos tareas: prepara las filas visibles y administra los nombres que están declarados en cada punto del programa.

En su construcción recorre los tokens y agrega los lexemas distintos en orden de aparición. Las constantes reciben su tipo; las palabras reservadas y los signos conservan el tipo vacío.

`entrar()` abre un ámbito y `salir()` lo cierra. `buscar()` busca una variable desde el ámbito más interno hacia el global. `duplicada()` comprueba solo el ámbito actual. Esto permite que dos funciones tengan una variable local con el mismo nombre, pero impide repetirla dentro del mismo ámbito.

`declarar()` registra el tipo de una variable. `fila_variable()` distingue internamente variables con el mismo nombre en ámbitos diferentes. La tabla visible conserva las dos columnas del PDF, por lo que puede mostrar el mismo nombre en más de una fila sin añadir una columna de ámbito.

`marcar_indefinida()` conserva una fila sin tipo cuando una variable no está declarada. `tipo()` consulta el tipo de una variable, literal o llamada. Las funciones declaradas se guardan en un diccionario propio y sus filas en `filas_funciones`. La tabla muestra `/<nombre>/` tanto para funciones como para variables, sin añadir paréntesis al lexema. En el código fuente, las funciones conservan los paréntesis obligatorios `()`; internamente se registran por separado. Declarar una no declara automáticamente la otra ni reemplaza su tipo.

La tabla visible puede contener todos los lexemas desde el inicio del análisis, pero eso no significa que todos estén declarados. Las declaraciones se activan en orden. Una declaración posterior no borra el error de un uso anterior.

### `indefinidas.py`: variables no declaradas

`revisar()` recorre los tokens de una instrucción y consulta los identificadores de variable. Si no encuentra uno en los ámbitos disponibles, conserva su símbolo sin tipo. La tabla muestra un solo error `Variable indefinida` por lexema, en el primer renglón detectado.

### `duplicadas.py`: declaraciones repetidas

`declarar()` revisa cada nombre de una declaración. Si ya existe en el mismo ámbito, agrega `Declaración duplicada`. Si no existe, lo registra.

Una declaración duplicada no reemplaza el tipo original. Si primero se declara una variable `phi` y luego se intenta declararla `rho` en el mismo ámbito, continúa teniendo tipo `phi`.

### `asignaciones.py`: tipos de los operandos

`revisar()` recibe el tipo del destino y consulta el de cada operando. Un destino `phi` admite enteros; uno `rho` admite enteros y reales; uno `delta` admite textos entre comillas simples o dobles.

Si encuentra un tipo conocido que no está permitido, señala el lexema con `Incompatibilidad de tipos, ` seguido del tipo del destino. También revisa el tipo de retorno de las funciones utilizadas como operandos.

Si el destino está indefinido, no comprueba incompatibilidades. Si un operando está indefinido, no inventa su tipo: ese identificador ya tiene su error específico.

### `aritmetica.py`: operadores admitidos

`revisar()` comprueba los operadores contra las reglas del tipo de destino. Para `phi` se permiten `+`, `-` y `*`; para `rho`, también `/`; para `delta`, `+` y `-`.

Una división con destino `phi` se reporta aunque `4 / 2` pudiera dar un entero. Se está aplicando la regla del PDF, sin calcular el resultado. `%` se reconoce como operador, pero no está incluido entre los operadores permitidos de estas reglas.

Esta capa complementa a `asignaciones.py`: una comprueba los operadores y la otra los tipos de los operandos.

### `ciclos.py`: condición de while

`revisar()` recorre la expresión postfija y utiliza una pila de tipos. Una comparación válida produce el tipo interno `booleano`. Los operadores lógicos combinan booleanos. Al final comprueba que la condición produzca un booleano.

Por ejemplo, `while (/<num1>/ < 3)` tiene una comparación; `while (3)` no produce un booleano según estas reglas. Las incompatibilidades de condición se explican mediante observaciones porque los PDF I–III no fijan una descripción exacta de tabla para esos casos.

El cuerpo del ciclo se analiza como código fuente una vez. El analizador no repite sus instrucciones según el valor de la condición.

### `funciones.py`: declaración, llamada y retorno

`declarar()` registra el nombre y su tipo de retorno. Si ya existe, agrega `Declaración duplicada` y conserva la primera firma. Devuelve un contexto que recuerda qué función se está revisando, su tipo y si contiene un retorno con valor.

`revisar_llamadas()` comprueba que cada función haya sido declarada antes de usarse. Cuando no existe, agrega `Función indefinida`. En la tabla de errores, el lexema conserva los delimitadores, por ejemplo `/<Suma>/`; la descripción distingue la función de la variable. En la tabla de símbolos la función se representa con `()`.

`revisar_retorno()` comprueba que `return` esté dentro de una función. Para funciones con tipo `phi`, `rho` o `delta`, reutiliza las comprobaciones de asignación y aritmética tomando el tipo de la función como destino. En una función `void`, se admite `return;`, pero no un retorno con valor.

`cerrar()` comprueba que una función con tipo de retorno contenga al menos un `return` con valor. No analiza si todos los caminos de ejecución garantizan un retorno. Por ejemplo, un retorno dentro de un `while` cuenta como presente aunque el ciclo pudiera no ejecutarse.

### `analizador.py`: coordinación

`analizar(codigo)` crea un `Resultado` nuevo, obtiene los tokens, separa las instrucciones y prepara los símbolos. Recorre las instrucciones con `while` y llama a las capas anteriores según corresponda.

En una asignación revisa variables indefinidas, funciones indefinidas, tipos de operandos y operadores. En una declaración comprueba primero su inicializador, si existe, y después registra los nombres. Por ello, una variable no se considera declarada anticipadamente dentro de su propia inicialización.

La lista `bloques` recuerda si cada bloque corresponde a una función o a un `while`. `contexto` conserva la función activa. El contador `omitir` permite saltar los cuerpos de bloques rechazados sin publicar sus declaraciones como válidas.

Al terminar devuelve el resultado. Cada llamada comienza con listas y ámbitos nuevos, de modo que analizar un segundo programa no reutiliza las variables del primero.

## 7. Reglas de tu lenguaje

| Tipo de destino | Tipos de operandos admitidos | Operadores aritméticos admitidos |
|---|---|---|
| `phi` | `phi` | `+`, `-`, `*` |
| `rho` | `phi`, `rho` | `+`, `-`, `*`, `/` |
| `delta` | `delta` | `+`, `-` |

Los identificadores de variable cumplen `/<[a-zA-Z0-9]+>/`. Se aceptan letras y números ASCII, incluso números al inicio. No se aceptan espacios, guiones bajos ni acentos dentro del nombre. Las mayúsculas distinguen nombres.

Las funciones usan el mismo formato que las variables y obligatoriamente los paréntesis: `phi /<Suma>/() { return 2 + 3; }`. También se admite `/<123>/()` porque la expresión regular del equipo permite dígitos al inicio. `void` indica que una función no devuelve un valor: `void /<Mostrar>/() { return; }`. Se admiten parámetros tipados, por ejemplo `phi /<Suma>/(phi /<a>/, phi /<b>/) { return /<a>/ + /<b>/; }`, y argumentos como `/<Suma>/(2, 3 + 4)`. Los parámetros son variables locales del cuerpo; se comprueban su duplicación y la cantidad y los tipos de los argumentos. El cuerpo puede contener declaraciones, asignaciones, llamadas, `while` y `return`. Las funciones se declaran en el ámbito global. Las formas antiguas `Suma()` y `phi Suma()` se rechazan.

Al terminar de reconocer los tokens, `entrada.py` clasifica como nombre de función al identificador seguido de `(`, incluso si hay espacios, saltos o comentarios entre ambos. Después se comprueban los paréntesis completos y los parámetros o argumentos de su interior, que también pueden estar vacíos. Sin paréntesis se interpreta como variable.

Todos los textos entre comillas simples o dobles tienen tipo `delta`, incluidos `'A'`, `'Hola'`, `''` y `"Hola"`. También se admiten comillas tipográficas emparejadas. Se eliminó el tipo interno de carácter y la restricción de un solo carácter entre comillas simples. Los números reales requieren dígitos a ambos lados del punto, como `12.5`.

`while` es la única estructura de control del lenguaje admitida en esta fase. Los recorridos explícitos de los módulos de la aplicación también utilizan `while`; los `if` de Python eligen qué comprobación aplicar. Los archivos de pruebas anteriores contienen algunos recorridos `for`: pertenecen a las herramientas de comprobación y no al lenguaje que acepta el compilador ni a la aplicación.

## 8. Correspondencia con los tres PDF

| Comprobación | Referencia | Estado en esta revisión |
|---|---|---|
| Reglas de operandos y operadores por tipo del destino | PDF I, pp. 9–20 | Cubiertas para `phi`, `rho` y `delta`. |
| Tabla de lexemas y tipos, incluidas constantes | PDF I, pp. 21–24 | Cubierta. |
| Ejercicio de tipos adaptado a los lexemas del equipo | PDF I, p. 61 | Nueva prueba: 8 errores esperados. |
| Token, Lexema, Renglón y Descripción | PDF II, pp. 3–4 | Cubiertos. |
| Una fila por lexema infractor | PDF II, p. 13, opción 2 | Es el formato utilizado. |
| Variables y funciones declaradas antes de usarse | PDF III, pp. 5–15 | Cubiertas. |
| Función en la tabla con su tipo de retorno | PDF III, pp. 6–7 | Cubierta, incluido `void`. |
| Retorno incompatible | PDF III, p. 15 | Cubierto. |
| Duplicadas en el mismo ámbito | PDF III, pp. 16–23 | Cubiertas. |
| Indefinida e incompatibilidad con destino conocido | PDF III, p. 26 | Se reportan ambos tipos de error. |
| Destino indefinido: reportar únicamente el destino y omitir los demás errores semánticos de esa asignación | PDF III, pp. 29–33 | Cubierto. |

Las referencias son páginas del archivo PDF. Los nombres `int`, `float` y `string` se adaptan a `phi`, `rho` y `delta`. Las descripciones semánticas son `Variable indefinida`, `Función indefinida`, `Declaración duplicada` e `Incompatibilidad de tipos, <tipo>`.

Los PDF no son completamente uniformes en sus tablas: algunas muestran solo el error que se está explicando y hay diferencias en mayúsculas, numeración o puntuación. En la página 15 del PDF III, por ejemplo, el código también asigna una cadena a una variable real, aunque la tabla se centra en el retorno. El compilador conserva esa incompatibilidad conforme a la regla del PDF I. No sería correcto afirmar que reproduce exactamente cada fila y cada número de todas las diapositivas.

En los PDF I–III no hay un catálogo completo de descripciones léxicas y sintácticas. Los números mal escritos, identificadores inválidos y llaves faltantes se presentan como observaciones de entrada. **Cero errores semánticos no significa que el programa sea válido si tiene observaciones.**

El PDF I también menciona conceptos generales como argumentos de funciones y otras estructuras de control. Se admiten funciones con parámetros y argumentos; la estructura de control de esta fase sigue siendo `while`. La revisión confirma las reglas de esta fase, no la implementación de todo lo que se menciona teóricamente en los PDF.

La actividad de las páginas 34–37 del PDF III pide además un documento PDF de evidencias. El código de prueba de esa actividad está incluido; este ZIP no sustituye ese documento académico si la maestra lo solicita como entrega adicional.

## 9. Protecciones y límites comprobados

- Entradas vacías y reinicio del estado entre análisis.
- Identificadores y números mal escritos.
- Comillas, llaves y paréntesis incompletos.
- Recuperación para revisar instrucciones posteriores a una entrada dañada.
- Conservación del tipo original frente a declaraciones duplicadas.
- Separación de ámbitos locales y globales.
- Rechazo de funciones anidadas y llamadas con argumentos.
- Prioridad de errores cuando el destino está indefinido.
- Entradas extensas, anidación profunda y límites de caracteres y tokens.
- Independencia de la aplicación respecto de la carpeta de pruebas.

Estas comprobaciones no incluyen ejecución del código fuente, cálculo de valores, detección de división por cero ni análisis completo de caminos de retorno. No se añadieron estas funcionalidades durante la limpieza.

## 10. Estructuras de datos que utiliza realmente

| Estructura | Uso |
|---|---|
| Listas | Tokens, instrucciones, filas de símbolos, errores y observaciones. |
| Diccionarios | Consultar tipos por nombre, funciones declaradas y campos de las filas. |
| Listas utilizadas como pilas | Bloques abiertos, ámbitos, operadores y tipos de expresiones. |
| Conjuntos | Tipos, operadores y categorías permitidos, sin elementos repetidos. |
| Dataclasses | Registros `Token`, `Instruccion` y `Resultado`. |

Una pila es una lista que agrega al final con `append()` y retira el último elemento con `pop()`: lo último que entra es lo primero que sale. Esto coincide con los bloques anidados: primero debe cerrarse el bloque interior.

La recomendación previa de simplificar a listas y diccionarios no se aplicó como una reescritura en esta entrega, porque se pidió conservar el código y las funcionalidades. La implementación actual sigue utilizando las estructuras de esta tabla.

## 11. Pruebas y archivos de ejemplo

Desde `italia_fase1`, ejecuta manualmente:

```bash
python -B -m unittest discover -s pruebas -v
```

`-B` evita generar archivos de caché durante las pruebas. Los archivos son:

- `pruebas/test_analizador.py`: reglas de tipos, símbolos, duplicadas, ámbitos, while y entradas difíciles.
- `pruebas/test_funciones.py`: declaraciones, llamadas, retornos y recuperación frente a funciones mal escritas.
- `pruebas/test_revision_pdf.py`: ejemplos adicionales de los PDF, resultados de los archivos de ejemplo, límites exactos e independencia de las pruebas.
- `pruebas/test_parentesis_funciones.py`: nuevo formato, nombres homónimos, espacios, sintaxis antigua rechazada y texto de cadenas que parece una llamada.
- `pruebas/test_textos_delta.py`: clasificación de textos, comillas, funciones, while y errores de tipos.
- `pruebas/REVISION.md`: evidencia y alcance de la revisión.
- `pruebas/ejemplos/RESULTADOS.md`: resultados esperados de los ejemplos anteriores.

| Ejemplo | Para qué sirve |
|---|---|
| `00_ejemplo_anterior.txt` | Conserva el texto que antes aparecía al iniciar; ahora solo es un archivo manual. |
| `01_correcto.txt` | Probar un programa sin errores. |
| `02_actividad_con_errores.txt` | Probar las 14 incidencias de la actividad. |
| `03_prioridades_pdf_III.txt` | Ver qué ocurre cuando coinciden distintos errores. |
| `04_entrada_mal_escrita.txt` | Comprobar observaciones de escritura y recuperación. |
| `05_funciones_correctas.txt` | Probar funciones con los tipos admitidos y llamadas válidas. |
| `07_textos_delta.txt` | Probar textos entre comillas simples y dobles, todos de tipo delta. |
| `06_funciones_errores_pdf_III.txt` | Probar errores de funciones, retornos y prioridad. |

## 12. Texto para explicarlo en una exposición

El proyecto implementa la primera fase de nuestro compilador, enfocada en el análisis semántico. Utiliza los tipos phi para enteros, rho para reales y delta para cadenas. Tanto variables como funciones usan el formato /<nombre>/. Los paréntesis distinguen a las funciones: /<nombre>/() es función y /<nombre>/ sin paréntesis es variable.

Dividimos el programa en módulos para que cada archivo tenga una responsabilidad. El archivo main abre la interfaz. La interfaz recibe el código y llama al analizador. Primero se reconocen los tokens, luego las instrucciones y finalmente se aplican las comprobaciones semánticas. Las reglas de variables indefinidas, declaraciones duplicadas, asignaciones, aritmética, funciones y while están separadas para que sea fácil localizar cada revisión.

La tabla de símbolos conserva los lexemas y sus tipos. Los ámbitos permiten distinguir las variables globales de las locales. La tabla de errores muestra el token del error, el lexema que lo provoca, el renglón y la descripción. Se utiliza una fila por lexema incorrecto, conforme a la opción dos del segundo PDF.

Una regla importante es que, cuando la variable que recibe una asignación no está declarada, se reporta únicamente «Variable indefinida» para ese destino. Se omiten los demás errores semánticos de esa asignación y se continúa con las instrucciones siguientes. Cuando el destino sí está declarado, pueden aparecer tanto errores de identificadores indefinidos como incompatibilidades de tipos.

El programa revisa el código sin ejecutarlo. Por eso puede analizar un while sin quedarse repitiendo su cuerpo. Cada análisis comienza desde cero. Los ejemplos y las pruebas están en una carpeta separada, y la interfaz comienza vacía. La revisión aprobó 79 pruebas, que incluyen los casos de los PDF, entradas mal formadas y el formato actualizado de las funciones.
