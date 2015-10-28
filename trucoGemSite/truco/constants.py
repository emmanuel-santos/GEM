# -*- encoding: utf-8 -*-
"""
Este documento es para definir constantes utilizadas en todo el
proyecto.
"""


# PALOS
ESPADA = 0
BASTO = 1
ORO = 2
COPA = 3

dict_palos = {
    ESPADA : "espadas",
    BASTO : "bastos",
    ORO : "oros",
    COPA : "copas",
}

PUNTOS = [(n,str(n)) for n in range(1,8) + range(20,34)]

cantos_truco = {
    2 : "TRUCO!",
    3 : "QUIERO RETRUCO!",
    4 : "QUIERO VALE CUATRO!",
}

cantos = {
    'quiero'                        : "QUIERO!",
    'no-quiero'                     : "NO QUIERO!",
    'truco'                         : "TRUCO!",
    'quiero-retruco'                : "QUIERO RETRUCO!",
    'quiero-vale-cuatro'            : "QUIERO VALE CUATRO!",
    'envido'                        : "ENVIDO!",
    'envido-esta-primero'           : "EL ENVIDO ESTÁ PRIMERO!",
    'real-envido'                   : "REAL ENVIDO!",
    'real-envido-esta-primero'      : "REAL ENVIDO ESTÁ PRIMERO!",
    'falta-envido'                  : "FALTA ENVIDO!",
    'falta-envido-esta-primero'     : "FALTA ENVIDO ESTÁ PRIMERO!",
    'mostrar-las-cartas'            : "MOSTRAME LAS CARTAS!",
    'irse-al-mazo'                  : "me voy al mazo...",
}
