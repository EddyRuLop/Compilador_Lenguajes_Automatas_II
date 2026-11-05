# Resultados esperados de los ejemplos

Actualización: funciones con y sin parámetros, tipos phi/rho/delta/void y return.

07_funciones_parametros.txt: 0 errores semánticos y 0 observaciones; genera triplos sin avisos.

05_funciones_correctas.txt: 0 errores semánticos y 0 observaciones.

06_funciones_errores_pdf_III.txt: 11 errores semánticos y 0 observaciones.

| Token | Lexema | Renglón | Descripción |
|---|---|---:|---|
| ErrSem1 | /<x2>/ | 14 | Incompatibilidad de tipos, phi |
| ErrSem2 | /<Suma>/ | 16 | Declaración duplicada |
| ErrSem3 | /<NoExiste>/ | 19 | Función indefinida |
| ErrSem4 | /<Promedio>/ | 20 | Incompatibilidad de tipos, phi |
| ErrSem5 | /<Mostrar>/ | 21 | Incompatibilidad de tipos, phi |
| ErrSem6 | /<Otro>/ | 22 | Variable indefinida |
| ErrSem7 | /<C>/ | 22 | Variable indefinida |
| ErrSem8 | /<C2>/ | 22 | Función indefinida |
| ErrSem9 | /<C3>/ | 23 | Función indefinida |
| ErrSem10 | 25.5 | 23 | Incompatibilidad de tipos, phi |
| ErrSem11 | / | 23 | Incompatibilidad de tipos, phi |

01_correcto.txt: 0 errores semánticos, 0 observaciones de entrada.

02_actividad_con_errores.txt: 14 errores semánticos, 0 observaciones.

| Token | Lexema | Renglón | Descripción |
|---|---|---:|---|
| ErrSem1 | 1.5 | 4 | Incompatibilidad de tipos, phi |
| ErrSem2 | "dos" | 5 | Incompatibilidad de tipos, rho |
| ErrSem3 | 7 | 6 | Incompatibilidad de tipos, delta |
| ErrSem4 | 2.5 | 7 | Incompatibilidad de tipos, phi |
| ErrSem5 | "real" | 8 | Incompatibilidad de tipos, rho |
| ErrSem6 | 9 | 9 | Incompatibilidad de tipos, delta |
| ErrSem7 | /<sinA>/ | 10 | Variable indefinida |
| ErrSem8 | /<sinB>/ | 11 | Variable indefinida |
| ErrSem9 | /<sinC>/ | 12 | Variable indefinida |
| ErrSem10 | /<sinD>/ | 13 | Variable indefinida |
| ErrSem11 | /<sinE>/ | 14 | Variable indefinida |
| ErrSem12 | /<sinF>/ | 15 | Variable indefinida |
| ErrSem13 | /<num1>/ | 16 | Declaración duplicada |
| ErrSem14 | /<x2>/ | 17 | Declaración duplicada |

03_prioridades_pdf_III.txt:
- Renglón 4: /<Otro>/ — Variable indefinida.
- Renglón 4: 25.5 — Incompatibilidad de tipos, phi.
- Renglón 4: / — Incompatibilidad de tipos, phi.
- Renglón 5: /<Otro2>/ — Variable indefinida.
- Renglón 5: /<C>/ — Variable indefinida.
- Renglón 6: /<num1>/ — Declaración duplicada.
- Renglón 7: 1.5 — Incompatibilidad de tipos, phi.

04_entrada_mal_escrita.txt: las instrucciones mal escritas se señalan en el aviso de entrada. Las asignaciones de 2.5 y 3.14 sí se analizan y generan incompatibilidad con phi. No se informa que el programa sea válido.

07_textos_delta.txt: 0 errores semánticos y 0 observaciones.
Todos sus literales de texto, incluido 'A', tienen tipo delta.
