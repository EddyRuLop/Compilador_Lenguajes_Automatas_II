"""Datos compartidos. No contiene reglas del lenguaje ni componentes gráficos."""
from dataclasses import dataclass, field


@dataclass
class Token:
    clase: str
    lexema: str
    linea: int
    columna: int


@dataclass
class Instruccion:
    clase: str
    inicio: Token
    nombres: list = field(default_factory=list)
    tipo: str = ''
    expresion: list = field(default_factory=list)
    postfija: list = field(default_factory=list)


@dataclass
class Resultado:
    simbolos: list = field(default_factory=list)
    errores: list = field(default_factory=list)
    observaciones: list = field(default_factory=list)

    def avisar(self, token, detalle):
        # Estos avisos NO se presentan como errores semánticos de la maestra.
        self.observaciones.append(
            f'Línea {token.linea}, columna {token.columna}: {detalle}'
        )

    def error(self, token, descripcion):
        # Opción 2 del PDF II, página 13: una fila por lexema infractor.
        self.errores.append({
            'Token': f'ErrSem{len(self.errores) + 1}',
            'Lexema': token.lexema,
            'Renglón': token.linea,
            'Descripción': descripcion,
        })
