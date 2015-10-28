# -*- encoding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from truco.models import *
from truco.constants import *
from truco.tests import mano_jugador, carta_jugador

# Botones
btn_quiero = ['Quiero', 'No Quiero']
btn_truco = ['Truco']
btn_retruco = ['Quiero Retruco']
btn_envido = ['Envido','Real Envido','Falta Envido']
btn_envido_t = ['Envido esta primero','Real Envido','Falta Envido']
btn_mazo = ['Irse al Mazo']
btn_cont = ['Continuar']

class TurnosApi(TestCase):
    def actualizar(self):
        try:
            self.a = Jugador.objects.get(id=self.a.id)
            self.b = Jugador.objects.get(id=self.b.id)
            self.c = Jugador.objects.get(id=self.c.id)
            self.d = Jugador.objects.get(id=self.d.id)
            self.e = Jugador.objects.get(id=self.e.id)
            self.f = Jugador.objects.get(id=self.f.id)
        except AttributeError:
            pass
        self.r = Ronda.objects.get(id=self.r.id)
        self.p = Partida.objects.get(id=self.p.id)
        self.e0 = Equipo.objects.get(id=self.e0.id)
        self.e1 = Equipo.objects.get(id=self.e1.id)

    def accion_canto(self, jugador, input):
        if not jugador.partida.ultima_ronda.terminada:
            self.assertEqual(self.r.turno_de(), jugador.posicion_en_mesa)
        self.r.accion(jugador, input)
        self.actualizar()

    def assertOpciones(self, jugador, opciones):
        self.assertEqual(self.r.opciones(jugador).sort(), opciones.sort())

    def assertPuntaje(self, jugador, num):
        self.assertEqual(jugador.equipo.puntos_partida, num)

    def terminar_ronda(self):
        for j in self.p.jugadores.all():
            self.accion_canto(j,'continuar')
        self.p.mostrar_partida(self.a)
        self.actualizar()

    def accion_carta(self, jugador, num):
        self.accion_canto(jugador, carta_jugador(jugador, num))


class TurnosDosJugadores(TurnosApi):
    def setUp(self):
        p = Partida(nombre='test',puntos_max=15)
        p.save()
        self.p = p
        self.e0 = Equipo(partida=p,pares=True)
        self.e0.save()
        self.e1 = Equipo(partida=p,pares=False)
        self.e1.save()
        self.a = Jugador(user=User.objects.create_user('a','a','a'),partida=p,posicion_en_mesa=0,equipo=self.e0)
        self.a.save()
        self.b = Jugador(user=User.objects.create_user('b','b','b'),partida=p,posicion_en_mesa=1,equipo=self.e1)
        self.b.save()
        Ronda.crear(p,0)
        self.r = Ronda.objects.latest('id')

    def test_2_no_quiere_truco(self):
        mano_jugador([(4,ORO),(4,ORO),(4,ORO)],self.a)
        mano_jugador([(4,ESPADA),(4,ORO),(4,BASTO)],self.b)
        self.assertOpciones(self.a, btn_truco+btn_mazo+btn_envido)
        self.accion_canto(self.a,'truco')
        self.assertOpciones(self.a, btn_envido_t+btn_quiero+btn_retruco)
        self.accion_canto(self.b, 'no-quiero')
        self.assertOpciones(self.a,btn_cont)
        self.assertOpciones(self.b,btn_cont)
        self.assertPuntaje(self.a,1)

    def test_2_real_envido_esta_primero(self):
        mano_jugador([(4,ORO),(4,ORO),(4,ORO)],self.a)
        mano_jugador([(4,ESPADA),(4,ORO),(4,BASTO)],self.b)
        self.accion_carta(self.a, 0)  # El jugador a juega un 4 de ORO
        self.accion_canto(self.b, 'truco')
        self.accion_canto(self.a, 'real-envido-esta-primero')
        self.assertOpciones(self.b, btn_quiero+['Falta Envido'])
        self.accion_canto(self.b, 'no-quiero')  # b no quiere envido
        self.assertOpciones(self.a, btn_quiero+btn_retruco)
        self.accion_canto(self.a, 'no-quiero')  # a no quiere truco
        self.terminar_ronda()
        self.assertPuntaje(self.a, 1)
        self.assertPuntaje(self.b, 1)

class TurnosCuatroJugadores(TurnosApi):
    def setUp(self):
        p = Partida(nombre='test',puntos_max=15,cantidad_jugadores=4)
        p.save()
        self.p = p
        self.e0 = Equipo(partida=p,pares=True)
        self.e0.save()
        self.e1 = Equipo(partida=p,pares=False)
        self.e1.save()
        self.a = Jugador(user=User.objects.create_user('a','a','a'),partida=p,posicion_en_mesa=0,equipo=self.e0)
        self.a.save()
        self.b = Jugador(user=User.objects.create_user('b','b','b'),partida=p,posicion_en_mesa=1,equipo=self.e1)
        self.b.save()
        self.c = Jugador(user=User.objects.create_user('c','c','c'),partida=p,posicion_en_mesa=2,equipo=self.e0)
        self.c.save()
        self.d = Jugador(user=User.objects.create_user('d','d','d'),partida=p,posicion_en_mesa=3,equipo=self.e1)
        self.d.save()
        Ronda.crear(p,0)
        self.r = Ronda.objects.latest('id')

    def test_4_ganar_ronda(self):
        mano_jugador([(4,ORO)   ,(1,ESPADA),(4,ORO)   ],self.a)
        mano_jugador([(1,ESPADA),(4,ORO)   ,(4,ORO)   ],self.b)
        mano_jugador([(4,ORO)   ,(4,ORO)   ,(4,ORO)   ],self.c)
        mano_jugador([(4,ORO)   ,(4,ORO)   ,(1,ESPADA)],self.d)
        # Primera vuelta
        self.accion_carta(self.a, 0)
        self.accion_carta(self.b, 0) # juega 1 espadas y gana.
        self.accion_carta(self.c, 0)
        self.accion_carta(self.d, 0)
        # Segunda vuelta
        self.accion_carta(self.b, 1)
        self.accion_carta(self.c, 1)
        self.accion_carta(self.d, 1)
        self.accion_carta(self.a, 1) # juega 1 espadas y gana.
        # Tercera vuelta
        self.accion_carta(self.a, 2)
        self.accion_carta(self.b, 2)
        self.accion_carta(self.c, 2)
        self.accion_carta(self.d, 2) # juega 1 espadas y gana.
        # Chequear que ganó el equipo b,d
        self.terminar_ronda()
        self.assertEqual(self.e1.puntos_partida,1)

    def test_4_envido_cantos(self):
        mano_jugador([(4,ORO),(4,ORO),(4,ORO)],self.a)
        mano_jugador([(5,ORO),(5,ORO),(5,ORO)],self.b)
        mano_jugador([(6,ORO),(6,ORO),(6,ORO)],self.c) # Pie de e0
        mano_jugador([(4,ORO),(4,ORO),(4,ORO)],self.d) # Pie de e1
        # Parte del quiero
        self.accion_carta(self.a, 0)
        self.accion_canto(self.b, 'envido')
        self.accion_canto(self.c, 'envido')
        self.accion_canto(self.d, 'real-envido')
        self.accion_canto(self.c, 'quiero')
        self.assertEqual(self.r.envido.puntosE,7)
        # Parte de cantos
        self.accion_canto(self.a, 'tengo-28')
        self.accion_canto(self.b, '30-son-mejores')
        self.accion_canto(self.c, '32-son-mejores')
        self.accion_canto(self.d, 'son-buenas')
        self.assertTrue(self.r.envido.terminado)

    def test_4_truco(self):
        mano_jugador([(4,ORO),(4,ORO),(4,ORO)],self.a)
        mano_jugador([(3,ORO),(4,ORO),(4,ORO)],self.b)
        mano_jugador([(4,ORO),(4,ORO),(4,ORO)],self.c) # Pie de e0
        mano_jugador([(4,ORO),(4,ORO),(4,ORO)],self.d) # Pie de e1
        # Parte del quiero
        self.accion_carta(self.a, 0)
        self.accion_canto(self.b, 'truco')
        self.accion_canto(self.c, 'quiero-retruco')
        self.accion_canto(self.d, 'quiero')
        self.accion_carta(self.b, 0)
        self.accion_carta(self.c, 0)
        self.accion_carta(self.d, 0)
        self.accion_canto(self.b, 'quiero-retruco')
        self.accion_canto(self.c, 'no-quiero')
        self.terminar_ronda()
        self.assertEqual(self.e1.puntos_partida,3)

class TurnosSeisJugadores(TurnosApi):
    def setUp(self):
        p = Partida(nombre='test',puntos_max=15,cantidad_jugadores=6)
        p.save()
        self.p = p
        self.e0 = Equipo(partida=p,pares=True)
        self.e0.save()
        self.e1 = Equipo(partida=p,pares=False)
        self.e1.save()
        self.a = Jugador(user=User.objects.create_user('a','a','a'),partida=p,posicion_en_mesa=0,equipo=self.e0)
        self.a.save()
        self.b = Jugador(user=User.objects.create_user('b','b','b'),partida=p,posicion_en_mesa=1,equipo=self.e1)
        self.b.save()
        self.c = Jugador(user=User.objects.create_user('c','c','c'),partida=p,posicion_en_mesa=2,equipo=self.e0)
        self.c.save()
        self.d = Jugador(user=User.objects.create_user('d','d','d'),partida=p,posicion_en_mesa=3,equipo=self.e1)
        self.d.save()
        self.e = Jugador(user=User.objects.create_user('e','e','e'),partida=p,posicion_en_mesa=4,equipo=self.e0)
        self.e.save()
        self.f = Jugador(user=User.objects.create_user('f','f','f'),partida=p,posicion_en_mesa=5,equipo=self.e1)
        self.f.save()
        Ronda.crear(p,0)
        self.r = Ronda.objects.latest('id')

    def test_6_ganar_ronda(self):
        mano_jugador([(4,ORO)   ,(4,ORO)   ,(4,ORO)   ],self.a)
        mano_jugador([(1,ESPADA),(4,ORO)   ,(4,ORO)   ],self.b)
        mano_jugador([(4,ORO)   ,(4,ORO)   ,(4,ORO)   ],self.c)
        mano_jugador([(4,ORO)   ,(4,ORO)   ,(4,ORO)   ],self.d)
        mano_jugador([(4,ORO)   ,(1,ESPADA),(4,ORO)   ],self.e)
        mano_jugador([(4,ORO)   ,(4,ORO)   ,(1,ESPADA)],self.f)
        # Primera vuelta
        self.accion_carta(self.a, 0)
        self.accion_carta(self.b, 0) # Gana
        self.accion_carta(self.c, 0)
        self.accion_carta(self.d, 0)
        self.accion_carta(self.e, 0)
        self.accion_carta(self.f, 0)
        # Segunda vuelta
        self.accion_carta(self.b, 1)
        self.accion_carta(self.c, 1)
        self.accion_carta(self.d, 1)
        self.accion_carta(self.e, 1) # Gana
        self.accion_carta(self.f, 1)
        self.accion_carta(self.a, 1)
        # Tercera vuelta
        self.accion_carta(self.e, 2)
        self.accion_carta(self.f, 2) # Gana
        self.accion_carta(self.a, 2)
        self.accion_carta(self.b, 2)
        self.accion_carta(self.c, 2)
        self.accion_carta(self.d, 2)
        # Chequear que ganó el equipo b, d, f
        self.terminar_ronda()
        self.assertEqual(self.e1.puntos_partida,1)

    def test_6_envido_cantos(self):
        mano_jugador([(10,ORO),(4,ORO),(4,ESPADA)],self.a)
        mano_jugador([(10,ORO),(1,ORO),(4,ESPADA)],self.b)
        mano_jugador([(10,ORO),(6,ORO),(4,ESPADA)],self.c)
        mano_jugador([(10,ORO),(5,ORO),(4,ESPADA)],self.d)
        mano_jugador([(10,ORO),(4,ORO),(4,ESPADA)],self.e) # Pie de e0
        mano_jugador([(3,ORO) ,(7,ORO),(4,ESPADA)],self.f) # Pie de e1
        # Parte del quiero
        self.accion_carta(self.a, 0)
        self.accion_carta(self.b, 0)
        self.accion_canto(self.c, 'envido')
        self.accion_canto(self.f, 'envido')
        self.accion_canto(self.e, 'quiero')
        self.assertEqual(self.r.envido.puntosE,4)
        # Parte de cantos
        self.accion_canto(self.a, 'tengo-24')
        self.accion_canto(self.b, 'son-buenas')
        self.accion_canto(self.d, '25-son-mejores')
        self.accion_canto(self.c, '26-son-mejores')
        self.accion_canto(self.f, '30-son-mejores')
        self.accion_canto(self.e, 'son-buenas')
        self.assertTrue(self.r.envido.terminado)
