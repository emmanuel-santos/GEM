from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from truco.models import *
from truco.constants import *

def carta_es_valida(carta):
    palos_validos = [ESPADA,BASTO,ORO,COPA]
    valores_validos = [1,2,3,4,5,6,7,10,11,12]
    return carta.palo in palos_validos and carta.valor in valores_validos

class CartaTests(TestCase):
    jerarquia_harcoded = [
        [Carta(palo=BASTO,valor=4),Carta(palo=ORO,valor=4),Carta(palo=COPA,valor=4),Carta(palo=ESPADA,valor=4)],
        [Carta(palo=BASTO,valor=5),Carta(palo=ORO,valor=5),Carta(palo=COPA,valor=5),Carta(palo=ESPADA,valor=5)],
        [Carta(palo=BASTO,valor=6),Carta(palo=ORO,valor=6),Carta(palo=COPA,valor=6),Carta(palo=ESPADA,valor=6)],
        [Carta(palo=COPA,valor=7),Carta(palo=BASTO,valor=7)],
        [Carta(palo=BASTO,valor=10),Carta(palo=ORO,valor=10),Carta(palo=COPA,valor=10),Carta(palo=ESPADA,valor=10)],
        [Carta(palo=BASTO,valor=11),Carta(palo=ORO,valor=11),Carta(palo=COPA,valor=11),Carta(palo=ESPADA,valor=11)],
        [Carta(palo=BASTO,valor=12),Carta(palo=ORO,valor=12),Carta(palo=COPA,valor=12),Carta(palo=ESPADA,valor=12)],
        [Carta(palo=ORO,valor=1),Carta(palo=COPA,valor=1)],
        [Carta(palo=BASTO,valor=2),Carta(palo=ORO,valor=2),Carta(palo=COPA,valor=2),Carta(palo=ESPADA,valor=2)],
        [Carta(palo=BASTO,valor=3),Carta(palo=ORO,valor=3),Carta(palo=COPA,valor=3),Carta(palo=ESPADA,valor=3)],
        [Carta(palo=ORO,valor=7)],
        [Carta(palo=ESPADA,valor=7)],
        [Carta(palo=BASTO,valor=1)],
        [Carta(palo=ESPADA,valor=1)]
    ]

    def test_carta_equidad(self):
        a = Carta(palo=BASTO,valor=3)
        b = Carta(palo=BASTO,valor=3)
        c = Carta(palo=ORO,valor=7)
        self.assertTrue(a==b, "No detecta igualdades")
        self.assertFalse(b==c, "Detecta igualdades que no son.")

    def test_carta_inequidad(self):
        a = Carta(palo=BASTO,valor=3)
        b = Carta(palo=BASTO,valor=3)
        c = Carta(palo=ORO,valor=7)
        self.assertFalse(a!=b, "Detecta desigualdades que no son")
        self.assertTrue(b!=c, "No detecta desigualdades")

    def test_carta_random_correctas(self):
        c = Carta()
        for i in range(0,200):
            c.randomize()
            self.assertTrue(carta_es_valida(c), "Genero la carta invalida " + str(c))

    def test_carta_jerarquia_pardas(self):
        for lista_iguales in self.jerarquia_harcoded:
            for carta in lista_iguales:
                for otra_carta in lista_iguales:
                    if carta != otra_carta:
                        self.assertEqual(carta.jerarquia(),otra_carta.jerarquia(), str(carta) + " y " + str(otra_carta) + " deberian tener la misma jerarquia")

    def test_carta_jerarquia_superiores(self):
        for i in range(0,len(self.jerarquia_harcoded)):
            carta = self.jerarquia_harcoded[i][0]
            for j in range(i+1,len(self.jerarquia_harcoded)):
                otra_carta = self.jerarquia_harcoded[j][0]
                self.assertTrue(carta.jerarquia()<otra_carta.jerarquia(), str(carta) + "deberia perder frente a " + str(otra_carta))

    def test_carta_puntos(self):
        self.assertEqual(Carta(palo=BASTO,valor=12).puntos(),0)
        self.assertEqual(Carta(palo=ORO,valor=11).puntos(),0)
        self.assertEqual(Carta(palo=ESPADA,valor=10).puntos(),0)
        for i in [1,2,3,4,5,6,7]:
            self.assertEqual(Carta(palo=ESPADA,valor=i).puntos(),i)


def hacer_mano(a,b,c):
    m = Mano()
    m.save()
    for carta in [a,b,c]:
        carta.mano = m
        carta.save()
    return m

class ManoTests(TestCase):
    def setUp(self):
        self.m = Mano()
        self.m.save()
        self.a = Carta(palo=ESPADA,valor=3,mano=self.m)
        self.b = Carta(palo=ESPADA,valor=2,mano=self.m)
        self.c = Carta(palo=ESPADA,valor=1,mano=self.m)
        self.a.save()
        self.b.save()
        self.c.save()

    def tearDown(self):
        self.m.delete()

    def test_mano_puntos(self):
        # Caso ABC
        m = hacer_mano(Carta(palo=BASTO,valor=7),Carta(palo=ORO,valor=2),Carta(palo=COPA,valor=2))
        self.assertEqual(m.puntos_del_envido(),7)
        m = hacer_mano(Carta(palo=BASTO,valor=2),Carta(palo=ORO,valor=7),Carta(palo=COPA,valor=2))
        self.assertEqual(m.puntos_del_envido(),7)
        m = hacer_mano(Carta(palo=BASTO,valor=2),Carta(palo=ORO,valor=2),Carta(palo=COPA,valor=7))
        self.assertEqual(m.puntos_del_envido(),7)

        # Caso AAB ABA BAA
        m = hacer_mano(Carta(palo=BASTO,valor=7),Carta(palo=BASTO,valor=2),Carta(palo=ORO,valor=2))
        self.assertEqual(m.puntos_del_envido(),29)
        m = hacer_mano(Carta(palo=BASTO,valor=2),Carta(palo=ORO,valor=2),Carta(palo=BASTO,valor=7))
        self.assertEqual(m.puntos_del_envido(),29)
        m = hacer_mano(Carta(palo=ORO,valor=2),Carta(palo=BASTO,valor=2),Carta(palo=BASTO,valor=7))
        self.assertEqual(m.puntos_del_envido(),29)

        # Caso (AA)A (A)A(A) A(AA)
        m = hacer_mano(Carta(palo=BASTO,valor=7),Carta(palo=BASTO,valor=2),Carta(palo=BASTO,valor=1))
        self.assertEqual(m.puntos_del_envido(),29)
        m = hacer_mano(Carta(palo=BASTO,valor=2),Carta(palo=BASTO,valor=1),Carta(palo=BASTO,valor=7))
        self.assertEqual(m.puntos_del_envido(),29)
        m = hacer_mano(Carta(palo=BASTO,valor=1),Carta(palo=BASTO,valor=2),Carta(palo=BASTO,valor=7))
        self.assertEqual(m.puntos_del_envido(),29)

    def test_mano_jugar_carta(self):
        self.m.jugar_carta(self.a.id)
        aa = self.m.cartas.get(palo=ESPADA,valor=3)
        self.assertTrue(aa.jugada != None)
        self.assertEqual(aa.jugada,0)

    def test_mano_cartas_jugadas(self):
        # Despues de jugar una carta
        self.m.jugar_carta(self.a.id)
        c_ord = self.m.cartas_jugadas()
        self.assertTrue(self.a in c_ord)
        
        # Despues de jugar dos cartas
        self.m.jugar_carta(self.c.id)
        c_ord = self.m.cartas_jugadas()
        self.assertTrue(self.a in c_ord and self.c in c_ord)
        
        # Despues de jugar tres cartas
        self.m.jugar_carta(self.b.id)
        c_ord = self.m.cartas_jugadas()
        self.assertTrue(self.a in c_ord and self.c in c_ord and self.b in c_ord)

    def test_mano_cartas_jugables(self):
        self.m.jugar_carta(self.a.id)
        self.assertFalse(self.a in self.m.cartas_jugables())
        self.assertTrue(self.b in self.m.cartas_jugables())
        self.assertTrue(self.c in self.m.cartas_jugables())

    def test_mano_asignaciones(self):
        u = User.objects.create_user('a','a','a')
        p = Partida(nombre='a')
        p.save()
        e = Equipo(partida=p,pares=True)
        e.save()
        j = Jugador(user=u,posicion_en_mesa=0,partida=p,equipo=e)
        j.save()
        m = Mano()
        m.asignaciones(j,Carta(palo=ORO,valor=4),Carta(palo=ORO,valor=4),Carta(palo=ORO,valor=4))
        self.assertEqual(m.jugador,j)
        self.assertEqual(len(m.cartas.all()),3)

    def test_mano_comparar_jugada(self):
        m = hacer_mano(Carta(palo=BASTO,valor=1),Carta(palo=BASTO,valor=4),Carta(palo=COPA,valor=5))
        m2 = hacer_mano(Carta(palo=BASTO,valor=5),Carta(palo=ORO,valor=4),Carta(palo=ESPADA,valor=1))
        m.jugar_carta(m.cartas.get(valor=1).id)
        m.jugar_carta(m.cartas.get(valor=4).id)
        m.jugar_carta(m.cartas.get(valor=5).id)
        m2.jugar_carta(m2.cartas.get(valor=5).id)
        m2.jugar_carta(m2.cartas.get(valor=4).id)
        m2.jugar_carta(m2.cartas.get(valor=1).id)
        self.assertEqual(m.comparar_jugada(m2,0), True)
        self.assertEqual(m.comparar_jugada(m2,1), None)
        self.assertEqual(m.comparar_jugada(m2,2), False)


class JugadorTests(TestCase):
    def setUp(self):
        self.us = User.objects.create_user('us',"mail",'us')
        self.us2 = User.objects.create_user('us2',"mail",'us2')
        self.p = Partida(nombre="test")
        self.p.save()
        self.e0 = Equipo(partida=self.p,pares=True)
        self.e0.save()
        self.e1 = Equipo(partida=self.p,pares=False)
        self.e1.save()
        self.j = Jugador(user=self.us,partida=self.p,posicion_en_mesa=0,equipo=self.e0)
        self.j2 = Jugador(user=self.us2,partida=self.p,posicion_en_mesa=0,equipo=self.e1)
        self.j.save()
        self.j2.save()

    def test_jugador_mano_desde_lista(self):
        m = hacer_mano(Carta(palo=BASTO,valor=1),Carta(palo=BASTO,valor=2),Carta(palo=BASTO,valor=3))
        self.j.mano_desde_lista([Carta(palo=BASTO,valor=1),Carta(palo=BASTO,valor=2),Carta(palo=BASTO,valor=3)])
        self.assertEqual(m,self.j.mano)

    def test_jugador_jugadas(self):
        self.j.mano_desde_lista([Carta(palo=BASTO,valor=1),Carta(palo=BASTO,valor=2),Carta(palo=BASTO,valor=3)])
        self.j.mano.jugar_carta(self.j.mano.cartas.get(valor=1).id)
        self.assertEqual(len(self.j.jugadas()),1)
        self.j.mano.jugar_carta(self.j.mano.cartas.get(valor=2).id)
        self.j.mano.jugar_carta(self.j.mano.cartas.get(valor=3).id)
        self.assertEqual(len(self.j.jugadas()),3)

    def test_jugador_comparar(self):
        m = hacer_mano(Carta(palo=BASTO,valor=1),Carta(palo=BASTO,valor=4),Carta(palo=COPA,valor=5))
        m2 = hacer_mano(Carta(palo=BASTO,valor=5),Carta(palo=ORO,valor=4),Carta(palo=ESPADA,valor=1))
        m.jugar_carta(m.cartas.get(valor=1).id)
        m.jugar_carta(m.cartas.get(valor=4).id)
        m.jugar_carta(m.cartas.get(valor=5).id)
        m2.jugar_carta(m2.cartas.get(valor=5).id)
        m2.jugar_carta(m2.cartas.get(valor=4).id)
        m2.jugar_carta(m2.cartas.get(valor=1).id)
        m.jugador = self.j
        m.save()
        m2.jugador = self.j2
        m2.save()
        self.assertEqual(self.j.comparar_manos(self.j2),[True,None,False])


class RondaTests(TestCase):
    def setUp (self):
        for letra in "abc":
            u = User.objects.create_user(letra,"default@default.com",letra)
        self.us_a = User.objects.get(username='a')
        self.us_b = User.objects.get(username='b')
        self.us_c = User.objects.get(username='c')
        self.p = Partida(nombre="test")
        self.p.save()
        self.e0 = Equipo(partida=self.p,pares=True)
        self.e0.save()
        self.e1 = Equipo(partida=self.p,pares=False)
        self.e1.save()
        self.j_a = Jugador(user=self.us_a,partida=self.p,posicion_en_mesa=0,equipo=self.e0)
        self.j_a.save()
        Mano(jugador=self.j_a).save()
        self.j_b = Jugador(user=self.us_b,partida=self.p,posicion_en_mesa=1,equipo=self.e1)
        self.j_b.save()
        Mano(jugador=self.j_b).save()
        self.r = Ronda(partida=self.p,mano=0)
        self.r.save()
        Truco(ronda=self.r).save()
        Envido(ronda=self.r).save()

    def definir_jugadas(self, jugador, jugada1=None, jugada2=None, jugada3=None):
        jugador.mano.cartas.all().delete()
        if jugada1 != None:
            Carta(palo=jugada1[1],valor=jugada1[0],jugada=0,mano=jugador.mano).save()
        if jugada2 != None:
            Carta(palo=jugada2[1],valor=jugada2[0],jugada=1,mano=jugador.mano).save()
        if jugada3 != None:
            Carta(palo=jugada3[1],valor=jugada3[0],jugada=2,mano=jugador.mano).save()

    def test_ronda_gana_mano(self):
        # Repartir
        m = hacer_mano(Carta(palo=ORO,valor=4),Carta(palo=BASTO,valor=5),Carta(palo=ESPADA,valor=6))
        m.jugador = self.j_a
        m.save()
        m = hacer_mano(Carta(palo=BASTO,valor=4),Carta(palo=ORO,valor=5),Carta(palo=COPA,valor=6))
        m.jugador = self.j_b
        m.save()
        # Jugar
        self.r.accion(self.j_a,str(self.j_a.mano.cartas.get(valor=4).id))
        self.r.accion(self.j_b,str(self.j_b.mano.cartas.get(valor=4).id))
        self.r.accion(self.j_a,str(self.j_a.mano.cartas.get(valor=5).id))
        self.r.accion(self.j_b,str(self.j_b.mano.cartas.get(valor=5).id))
        self.r.accion(self.j_a,str(self.j_a.mano.cartas.get(valor=6).id))
        self.r.accion(self.j_b,str(self.j_b.mano.cartas.get(valor=6).id))
        j_a_actualizado = self.p.jugadores.get(id=self.j_a.id)
        self.assertEqual(j_a_actualizado.equipo.puntos_partida, 1)

    def test_ronda_buscar_ganador(self):
        # Una sola jugada
        self.definir_jugadas(self.j_a,(4, BASTO))
        self.definir_jugadas(self.j_b,(4, BASTO))
        self.assertRaises(IndexError, self.r.buscar_ganador)
        self.definir_jugadas(self.j_a,(1, BASTO))
        self.definir_jugadas(self.j_b,(4, BASTO))
        self.assertRaises(IndexError, self.r.buscar_ganador)
        self.definir_jugadas(self.j_a,(4, BASTO))
        self.definir_jugadas(self.j_b,(1, BASTO))
        self.assertRaises(IndexError, self.r.buscar_ganador)
        # Dos jugadas
        self.definir_jugadas(self.j_a,(1, BASTO),(4, BASTO))
        self.definir_jugadas(self.j_b,(4, BASTO),(4, BASTO))
        self.assertTrue(self.j_a in self.r.buscar_ganador().jugadores.all())
        self.definir_jugadas(self.j_a,(1, BASTO),(1, BASTO))
        self.definir_jugadas(self.j_b,(4, BASTO),(4, BASTO))
        self.assertTrue(self.j_a in self.r.buscar_ganador().jugadores.all())
        self.definir_jugadas(self.j_a,(1, BASTO),(4, BASTO))
        self.definir_jugadas(self.j_b,(4, BASTO),(1, BASTO))
        self.assertRaises(IndexError, self.r.buscar_ganador)
        self.definir_jugadas(self.j_a,(4, BASTO),(4, BASTO))
        self.definir_jugadas(self.j_b,(1, BASTO),(4, BASTO))
        self.assertTrue(self.j_b in self.r.buscar_ganador().jugadores.all())
        self.definir_jugadas(self.j_a,(4, BASTO),(4, BASTO))
        self.definir_jugadas(self.j_b,(1, BASTO),(1, BASTO))
        self.assertTrue(self.j_b in self.r.buscar_ganador().jugadores.all())
        self.definir_jugadas(self.j_a,(4, BASTO),(1, BASTO))
        self.definir_jugadas(self.j_b,(1, BASTO),(4, BASTO))
        self.assertRaises(IndexError, self.r.buscar_ganador)
        self.definir_jugadas(self.j_a,(4, BASTO),(1, BASTO))
        self.definir_jugadas(self.j_b,(4, BASTO),(4, BASTO))
        self.assertTrue(self.j_a in self.r.buscar_ganador().jugadores.all())
        self.definir_jugadas(self.j_a,(4, BASTO),(4, BASTO))
        self.definir_jugadas(self.j_b,(4, BASTO),(1, BASTO))
        self.assertTrue(self.j_b in self.r.buscar_ganador().jugadores.all())
        self.definir_jugadas(self.j_a,(4, BASTO),(4, BASTO))
        self.definir_jugadas(self.j_b,(4, BASTO),(4, BASTO))
        self.assertRaises(IndexError, self.r.buscar_ganador)
        # Tres jugadas
        self.definir_jugadas(self.j_a,(1, BASTO),(4, BASTO),(1, BASTO))
        self.definir_jugadas(self.j_b,(4, BASTO),(4, BASTO),(4, BASTO))
        self.assertTrue(self.j_a in self.r.buscar_ganador().jugadores.all())
        self.definir_jugadas(self.j_a,(1, BASTO),(4, BASTO),(4, BASTO))
        self.definir_jugadas(self.j_b,(4, BASTO),(1, BASTO),(1, BASTO))
        self.assertTrue(self.j_b in self.r.buscar_ganador().jugadores.all())
        self.definir_jugadas(self.j_a,(1, BASTO),(4, BASTO),(4, BASTO))
        self.definir_jugadas(self.j_b,(4, BASTO),(1, BASTO),(4, BASTO))
        self.assertTrue(self.j_a in self.r.buscar_ganador().jugadores.all())
        self.definir_jugadas(self.j_a,(4, BASTO),(1, BASTO),(1, BASTO))
        self.definir_jugadas(self.j_b,(1, BASTO),(4, BASTO),(4, BASTO))
        self.assertTrue(self.j_a in self.r.buscar_ganador().jugadores.all())
        self.definir_jugadas(self.j_a,(4, BASTO),(1, BASTO),(4, BASTO))
        self.definir_jugadas(self.j_b,(1, BASTO),(4, BASTO),(1, BASTO))
        self.assertTrue(self.j_b in self.r.buscar_ganador().jugadores.all())
        self.definir_jugadas(self.j_a,(4, BASTO),(1, BASTO),(4, BASTO))
        self.definir_jugadas(self.j_b,(1, BASTO),(4, BASTO),(4, BASTO))
        self.assertTrue(self.j_b in self.r.buscar_ganador().jugadores.all())
        self.definir_jugadas(self.j_a,(4, BASTO),(4, BASTO),(1, BASTO))
        self.definir_jugadas(self.j_b,(4, BASTO),(4, BASTO),(4, BASTO))
        self.assertTrue(self.j_a in self.r.buscar_ganador().jugadores.all())
        self.definir_jugadas(self.j_a,(4, BASTO),(4, BASTO),(4, BASTO))
        self.definir_jugadas(self.j_b,(4, BASTO),(4, BASTO),(1, BASTO))
        self.assertTrue(self.j_b in self.r.buscar_ganador().jugadores.all())
        self.definir_jugadas(self.j_a,(4, BASTO),(4, BASTO),(4, BASTO))
        self.definir_jugadas(self.j_b,(4, BASTO),(4, BASTO),(4, BASTO))
        self.assertRaises(IndexError, self.r.buscar_ganador)

    def test_ronda_ganar_ronda(self):
        # Repartir
        m = hacer_mano(Carta(palo=ORO,valor=7),Carta(palo=BASTO,valor=1),Carta(palo=ESPADA,valor=1))
        m.jugador = self.j_a
        m.save()
        m = hacer_mano(Carta(palo=ORO,valor=4),Carta(palo=COPA,valor=4),Carta(palo=ESPADA,valor=4))
        m.jugador = self.j_b
        m.save()
        # Jugar
        self.r.accion(self.j_a,str(self.j_a.mano.cartas.get(palo=ORO).id))
        self.r.accion(self.j_b,str(self.j_b.mano.cartas.get(palo=ORO).id))
        self.r.accion(self.j_a,str(self.j_a.mano.cartas.get(palo=ESPADA).id))
        self.r.accion(self.j_b,str(self.j_b.mano.cartas.get(palo=ESPADA).id))
        j_a_actualizado = self.p.jugadores.get(id=self.j_a.id)
        self.assertEqual(j_a_actualizado.equipo.puntos_partida, 1)

    def test_ronda_repartir(self):
        self.r.repartir()
        # Solo podemos chequear que es distinto de Vacio
        self.assertEqual(len(self.j_a.mano.cartas.all()),3)
        self.assertEqual(len(self.j_b.mano.cartas.all()),3)

    def test_ronda_tres_rondas(self):
        # Repartir
        m = hacer_mano(Carta(palo=ORO,valor=7),Carta(palo=BASTO,valor=4),Carta(palo=ESPADA,valor=4))
        m.jugador = self.j_a
        m.save()
        m = hacer_mano(Carta(palo=ORO,valor=4),Carta(palo=BASTO,valor=7),Carta(palo=ESPADA,valor=7))
        m.jugador = self.j_b
        m.save()
        # Jugar
        self.r.accion(self.j_a,str(self.j_a.mano.cartas.get(palo=ORO).id))
        self.r.accion(self.j_b,str(self.j_b.mano.cartas.get(palo=ORO).id))
        self.r.accion(self.j_a,str(self.j_a.mano.cartas.get(palo=BASTO).id))
        self.r.accion(self.j_b,str(self.j_b.mano.cartas.get(palo=BASTO).id))
        self.r.accion(self.j_a,str(self.j_a.mano.cartas.get(palo=ESPADA).id))
        self.r.accion(self.j_b,str(self.j_b.mano.cartas.get(palo=ESPADA).id))
        j_b_actualizado = self.p.jugadores.get(id=self.j_b.id)
        self.assertEqual(j_b_actualizado.equipo.puntos_partida, 1)

    def test_ronda_jugar_carta(self):
        self.r.repartir()
        self.r.save()
        self.r.accion(self.j_a,str(self.j_a.mano.cartas.latest('id').id))
        self.assertTrue(len(self.j_a.mano.cartas_jugadas())>0)
        self.assertTrue(self.j_a.mano.cartas_jugadas()[0],self.j_a.mano.cartas.latest('id').id)
        self.assertEqual(Ronda.objects.get(id=self.r.id).turno_de(),1)

    def test_ronda_ultimo_ganador(self):
        # Pardas
        self.definir_jugadas(self.j_a,(4, BASTO))
        self.definir_jugadas(self.j_b,(4, BASTO))
        self.assertEqual(self.r.ultimo_ganador(),self.j_a)
        # Uno
        self.definir_jugadas(self.j_a,(4, BASTO))
        self.definir_jugadas(self.j_b,(1, BASTO))
        self.assertEqual(self.r.ultimo_ganador(),self.j_b)
        # Dos
        self.definir_jugadas(self.j_a,(4, BASTO),(4, BASTO))
        self.definir_jugadas(self.j_b,(4, BASTO),(1, BASTO))
        self.assertEqual(self.r.ultimo_ganador(),self.j_b)
        # Desiguales
        self.definir_jugadas(self.j_a,(4, BASTO))
        self.definir_jugadas(self.j_b,(1, BASTO),(4, BASTO))
        self.assertEqual(self.r.ultimo_ganador(),self.j_b)


class EnvidoTests(TestCase):
    def setUp(self):
        p = Partida(nombre='test',puntos_max=15)
        p.save()
        self.eq0 = Equipo(partida=p,pares=True)
        self.eq0.save()
        self.eq1 = Equipo(partida=p,pares=False)
        self.eq1.save()
        self.j_a = Jugador(user=User.objects.create_user('a','a','a'),partida=p,posicion_en_mesa=0,equipo=self.eq0)
        self.j_a.save()
        self.j_b = Jugador(user=User.objects.create_user('b','b','b'),partida=p,posicion_en_mesa=1,equipo=self.eq1)
        self.j_b.save()
        Ronda.crear(p,0)
        r = Ronda.objects.latest('id')
        self.e = r.envido

    def test_envido_puntos_quiero(self):
        self.assertEqual(self.e.puntos_quiero(),0)
        self.e.input(self.j_a, 'envido')
        self.assertEqual(self.e.puntos_quiero(),2)
        self.e.input(self.j_a, 'envido')
        self.assertEqual(self.e.puntos_quiero(),4)
        self.e.input(self.j_a, 'real-envido')
        self.assertEqual(self.e.puntos_quiero(),7)
        self.e.input(self.j_a, 'falta-envido')
        self.assertEqual(self.e.puntos_quiero(),15)

    def test_envido_botones(self):
        self.assertEqual(self.e.opciones(self.j_a).sort(),['Envido','Real Envido','Falta Envido'].sort())
        self.e.input(self.j_a, 'envido')
        self.assertEqual(self.e.opciones(self.j_b).sort(),['Envido','Real Envido','Falta Envido','Quiero','No Quiero'].sort())
        self.e.input(self.j_b, 'envido')
        self.assertEqual(self.e.opciones(self.j_a).sort(),['Real Envido','Falta Envido','Quiero','No Quiero'].sort())
        self.e.input(self.j_a, 'real-envido')
        self.assertEqual(self.e.opciones(self.j_b).sort(),['Falta Envido','Quiero','No Quiero'].sort())
        self.e.input(self.j_b, 'falta-envido')
        self.assertEqual(self.e.opciones(self.j_a).sort(),['Quiero','No Quiero'].sort())

    def test_envido_puntos_no_quiero(self):
        r = Ronda.objects.latest('id')
        e = Envido(ronda=r,envido=1,real_envido=False,falta_envido=False)
        self.assertEqual(e.puntos_no_quiero(),1)
        e = Envido(ronda=r,envido=0,real_envido=True,falta_envido=False)
        self.assertEqual(e.puntos_no_quiero(),1)
        e = Envido(ronda=r,envido=0,real_envido=False,falta_envido=True)
        self.assertEqual(e.puntos_no_quiero(),1)
        e = Envido(ronda=r,envido=2,real_envido=False,falta_envido=False)
        self.assertEqual(e.puntos_no_quiero(),2)
        e = Envido(ronda=r,envido=1,real_envido=True,falta_envido=False)
        self.assertEqual(e.puntos_no_quiero(),2)
        e = Envido(ronda=r,envido=1,real_envido=False,falta_envido=True)
        self.assertEqual(e.puntos_no_quiero(),2)
        e = Envido(ronda=r,envido=0,real_envido=True,falta_envido=True)
        self.assertEqual(e.puntos_no_quiero(),3)
        e = Envido(ronda=r,envido=2,real_envido=False,falta_envido=True)
        self.assertEqual(e.puntos_no_quiero(),5)
        e = Envido(ronda=r,envido=2,real_envido=True,falta_envido=False)
        self.assertEqual(e.puntos_no_quiero(),4)
        e = Envido(ronda=r,envido=1,real_envido=True,falta_envido=True)
        self.assertEqual(e.puntos_no_quiero(),5)
        e = Envido(ronda=r,envido=2,real_envido=True,falta_envido=True)
        self.assertEqual(e.puntos_no_quiero(),7)

class TrucoTests(TestCase):
    def setUp(self):
        p = Partida(nombre='test',puntos_max=15)
        p.save()
        self.e0 = Equipo(partida=p,pares=True)
        self.e0.save()
        self.e1 = Equipo(partida=p,pares=False)
        self.e1.save()
        self.j_a = Jugador(user=User.objects.create_user('a','a','a'),partida=p,posicion_en_mesa=0,equipo=self.e0)
        self.j_a.save()
        self.j_b = Jugador(user=User.objects.create_user('b','b','b'),partida=p,posicion_en_mesa=1,equipo=self.e1)
        self.j_b.save()
        Ronda.crear(p,0)
        r = Ronda.objects.latest('id')
        self.t = r.truco

    def test_truco_botones(self):
        self.assertEqual(self.t.opciones(self.j_a).sort(),['Truco'].sort())
        self.t.input(self.j_a, 'truco')
        self.assertEqual(self.t.opciones(self.j_b).sort(),['Quiero Retruco','Quiero','No Quiero'].sort())
        self.t.input(self.j_a, 'quiero-retruco')
        self.assertEqual(self.t.opciones(self.j_a).sort(),['Quiero Vale Cuatro','Quiero','No Quiero'].sort())
        self.t.input(self.j_a, 'quiero-vale-cuatro')
        self.assertEqual(self.t.opciones(self.j_b).sort(),['Quiero','No Quiero'].sort())


def mano_jugador(tuplas, jugador):
    m = hacer_mano(Carta(valor=tuplas[0][0],palo=tuplas[0][1]),Carta(valor=tuplas[1][0],palo=tuplas[1][1]),Carta(valor=tuplas[2][0],palo=tuplas[2][1]))
    m.jugador = jugador
    m.save()

def carta_jugador(jugador, num):
    return str(jugador.mano.cartas.all()[num].id)

class TurnosTests(TestCase):
    def setUp(self):
        p = Partida(nombre='test',puntos_max=15)
        p.save()
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

    def actualizar(self):
        self.a = Jugador.objects.get(id=self.a.id)
        self.b = Jugador.objects.get(id=self.b.id)
        self.r = Ronda.objects.get(id=self.r.id)

    def test_turnos_envido_esta_primero(self):
        self.assertEqual(self.r.opciones(self.a).sort(),['Truco','Envido','Real Envido','Falta Envido'].sort())
        self.r.accion(self.a, 'truco')
        self.assertEqual(self.r.opciones(self.b).sort(),['Quiero Retruco','Quiero','No Quiero','Envido Esta Primero'].sort())
        self.r.accion(self.b, 'envido-esta-primero')
        self.assertEqual(self.r.opciones(self.a).sort(),['Envido','Real Envido','Falta Envido','Quiero','No Quiero'].sort())

    def test_turnos_truco(self):
        mano_jugador([(1,ESPADA),(6,ORO),(5,BASTO)],self.a)
        mano_jugador([(7,ESPADA),(4,ORO),(4,BASTO)],self.b); self.actualizar()
        # El turno del jugador a. Canta truco.
        self.assertEqual(self.r.turno_de(),self.a.posicion_en_mesa)
        self.assertEqual(self.r.opciones(self.a).sort(), ['Truco','Envido','Real Envido','Falta Envido','Irse al Mazo'].sort())
        self.r.accion(self.a, 'truco'); self.actualizar()
        # El turno del jugador b. Dice Quiero.
        self.assertEqual(self.r.turno_de(),self.b.posicion_en_mesa)
        self.assertEqual(self.r.opciones(self.b).sort(), ['Quiero', 'No Quiero','Envido esta primero','Quiero Retruco'].sort())
        self.r.accion(self.b, 'quiero'); self.actualizar()
        # El turno del jugador a. Juega una carta. 7 espadas.
        self.assertEqual(self.r.turno_de(),self.a.posicion_en_mesa)
        self.assertEqual(self.r.opciones(self.a).sort(), ['Irse al Mazo'].sort())
        self.r.accion(self.a, carta_jugador(self.a,0)); self.actualizar()
        # El turno del jugador b. Retruca.
        self.assertEqual(self.r.turno_de(),self.b.posicion_en_mesa)
        self.assertEqual(self.r.opciones(self.b).sort(), ['Irse al Mazo', 'Quiero Retruco'].sort())
        self.r.accion(self.b, 'quiero-retruco'); self.actualizar()
        # El turno del jugador a. Acepta.
        self.assertEqual(self.r.turno_de(),self.a.posicion_en_mesa)
        self.assertEqual(self.r.opciones(self.a).sort(), ['Quiero','No Quiero','Quiero Vale Cuatro'].sort())
        self.r.accion(self.a, 'quiero'); self.actualizar()
        # El turno del jugador b. Juega una carta. 1 espadas.
        self.assertEqual(self.r.turno_de(),self.b.posicion_en_mesa)
        self.assertEqual(self.r.opciones(self.b).sort(), ['Irse al Mazo'].sort())
        self.r.accion(self.b, carta_jugador(self.b,0)); self.actualizar()
        # El turno del jugador a. Pide vale cuatro.
        self.assertEqual(self.r.turno_de(),self.a.posicion_en_mesa)
        self.assertEqual(self.r.opciones(self.a).sort(), ['Irse al Mazo','Quiero Vale Cuatro'].sort())
        self.r.accion(self.a, 'quiero-vale-cuatro'); self.actualizar()
        # El turno del jugador b. No acepta. Gana a.
        self.assertEqual(self.r.turno_de(),self.b.posicion_en_mesa)
        self.assertEqual(self.r.opciones(self.b).sort(), ['Quiero','No Quiero'].sort())
        self.r.accion(self.b, 'no-quiero'); self.actualizar()
        self.assertEqual(self.r.opciones(self.a).sort(), ['Continuar'].sort())
        self.assertEqual(self.r.opciones(self.b).sort(), ['Continuar'].sort())
        self.r.accion(self.b, 'continuar'); self.actualizar()
        self.assertEqual(self.r.opciones(self.b), [])
        self.assertEqual(self.a.equipo.puntos_partida,3)


class PartidaTests(TestCase):
    def setUp(self):
        for letra in ["a","b","c"]:
            u = User.objects.create_user(letra,"default@default.com",letra)
        self.us_a = User.objects.get(username='a')
        self.us_b = User.objects.get(username='b')
        self.us_c = User.objects.get(username='c')
        self.p = Partida(nombre="test")
        self.p.save()
        self.e0 = Equipo(partida=self.p,pares=True)
        self.e0.save()
        self.e1 = Equipo(partida=self.p,pares=False)
        self.e1.save()
        self.j_a = Jugador(user=self.us_a,partida=self.p,posicion_en_mesa=0,equipo=self.e0)
        self.j_a.save()
        self.j_b = Jugador(user=self.us_b,partida=self.p,posicion_en_mesa=1,equipo=self.e1)
        self.j_b.save()
        Ronda.crear(self.p,0)

    def tearDown(self):
        for obj in [self.p,self.j_a,self.j_b]:
            obj.delete()

    def test_partida_sumar_jugador(self):
        p = Partida(nombre="test2")
        p.save()
        self.assertEqual(len(p.jugadores.all()), 0)
        x = User.objects.create_user('x',"test@test.com",'x')
        p.sumar_jugador(x)
        self.assertEqual(len(p.jugadores.all()), 1)
        self.assertEqual(p.jugadores.latest('id').posicion_en_mesa, 0)
        y = User.objects.create_user('y',"test@test.com",'y')
        p.sumar_jugador(y)
        self.assertEqual(len(p.jugadores.all()), 2)
        self.assertEqual(p.jugadores.latest('id').posicion_en_mesa, 1)

    def test_partida_esta_llena(self):
        p = Partida(nombre="test2")
        p.save()
        self.assertFalse(p.esta_llena())
        p.sumar_jugador(User.objects.create_user('rer'))
        self.assertFalse(p.esta_llena())
        p.sumar_jugador(User.objects.create_user('rer2'))
        self.assertTrue(p.esta_llena())

    def test_partida_jugador(self):
        self.assertEqual(self.j_a, self.p.jugador(self.us_a))
        self.assertEqual(None, self.p.jugador(self.us_c))

    def test_partida_mostrar(self):
        self.p.ultima_ronda.repartir()
        dic = self.p.mostrar_partida(self.j_a)
        self.assertEqual(dic['mi_mano'],self.j_a.mano)
        self.assertEqual(dic['otro_mano'], self.j_b.mano)


class ViewTests(TestCase):
    def setUp(self):
        for letra in ["a","b","c"]:
            u = User.objects.create_user(letra,"default@default.com",letra)
        self.client_a = Client()
        self.client_a.login(username='a', password='a')
        self.client_b = Client()
        self.client_b.login(username='b', password='b')

    def test_view_sala_create(self):
        self.client_a.post('/nueva_sala', {'Nombre':'sasa','Puntos':15,'num_jug':2})
        self.assertTrue(Partida.objects.get(nombre='sasa'))

    def test_view_sala_join(self):
        p = Partida(nombre="sasasa")
        p.save()
        self.client_a.get('/sala/' + str(p.id))
        self.client_b.get('/sala/' + str(p.id))
        self.assertEqual(len(p.jugadores.all()),2)

    def test_view_carta_tirar(self):
        p = Partida(nombre="abab")
        p.save()
        self.client_a.get('/sala/' + str(p.id))
        self.client_b.get('/sala/' + str(p.id))
        j0 = p.jugadores.get(posicion_en_mesa=0)
        # Una carta, jugador A
        self.client_a.get('/sala/' + str(p.id) + '/' + str(j0.mano.cartas.latest('id').id))
        self.assertEqual(len(j0.mano.cartas_jugadas()),1)
        p_actualizada = Partida.objects.get(nombre="abab")
        self.assertEqual(p_actualizada.ultima_ronda.turno_de(),1)
        # Una carta, jugador B
        j1 = p.jugadores.get(posicion_en_mesa=1)
        self.client_b.get('/sala/' + str(p.id) + '/' + str(j1.mano.cartas.latest('id').id))
        self.assertEqual(len(j1.mano.cartas_jugadas()),1)
        p_actualizada = Partida.objects.get(nombre="abab")
        # self.assertEqual(p_actualizada.ultima_ronda.turno_de(),0)
        # Dos cartas, jugador A
        self.client_a.get('/sala/' + str(p.id) + '/' + str(j0.mano.cartas.all()[1].id))
        # self.assertEqual(len(j0.mano.cartas_jugadas()),2)
        p_actualizada = Partida.objects.get(nombre="abab")
        # self.assertEqual(p_actualizada.ultima_ronda.turno_de(),1)

    def test_view_envido(self):
        p = Partida(nombre="abab")
        p.save()
        self.client_a.get('/sala/' + str(p.id))
        self.client_b.get('/sala/' + str(p.id))
        self.client_a.get('/sala/' + str(p.id) + '/envido')
        self.assertTrue(p.ultima_ronda.envido.cantado)
        self.client_b.get('/sala/' + str(p.id) + '/quiero')
        self.assertFalse(p.ultima_ronda.terminada)
        # self.assertEqual(Jugador.objects.get(user=client_a.user).,)
        p = Partida(nombre="abab")
        p.save()
        self.client_a.get('/sala/' + str(p.id))
        self.client_b.get('/sala/' + str(p.id))
        self.client_a.get('/sala/' + str(p.id) + '/envido')
        self.assertTrue(p.ultima_ronda.envido.cantado)
        self.client_b.get('/sala/' + str(p.id) + '/no-quiero')
        self.assertTrue(p.ultima_ronda.envido.terminado)

    def test_view_truco(self):
        p = Partida(nombre="abab")
        p.save()
        self.client_a.get('/sala/' + str(p.id))
        self.client_b.get('/sala/' + str(p.id))
        self.client_a.get('/sala/' + str(p.id) + '/truco')
        self.assertTrue(p.ultima_ronda.truco.cantado)
        self.client_b.get('/sala/' + str(p.id) + '/quiero')
        self.assertFalse(p.ultima_ronda.terminada)
        # self.assertEqual(Jugador.objects.get(user=client_a.user).,)
        p = Partida(nombre="abab")
        p.save()
        self.client_a.get('/sala/' + str(p.id))
        self.client_b.get('/sala/' + str(p.id))
        self.client_a.get('/sala/' + str(p.id) + '/truco')
        self.assertTrue(p.ultima_ronda.truco.cantado)
        self.client_b.get('/sala/' + str(p.id) + '/no-quiero')
        self.assertTrue(p.ultima_ronda.terminada)