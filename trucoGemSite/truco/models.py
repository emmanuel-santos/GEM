# -*- encoding: utf-8 -*-
from django.db import models
from django.db.models import Q, F, Count
from django.contrib.auth.models import User
from django.utils.text import slugify as slugify_unicode
from constants import *
import random

def slugify(word):
    return slugify_unicode(unicode(word))


class Carta(models.Model):
    """
    El valor representa el número de una carta. El palo es representado
    con un numero, descripto en constants.
    """
    palo = models.IntegerField()
    valor = models.IntegerField()
    mano = models.ForeignKey('Mano', related_name="cartas", null=True)
    jugada = models.IntegerField(null=True)

    def __unicode__(self):
        return str(self.valor) + " de " + dict_palos[self.palo]

    def __eq__(self, other):
        return self.valor == other.valor and self.palo == other.palo

    def __ne__(self, other):
        return self.valor != other.valor or self.palo != other.palo

    def randomize(self):
        """
        Asigna un palo y valor aleatorios para esta carta.
        """
        self.palo = random.randint(0,3)
        self.valor = random.randint(1,12)
        while self.valor == 8 or self.valor == 9:
            self.valor = random.randint(1,12)

    def jerarquia(self):
        """
        Retorna un valor que representa la jerarquia de esta carta.
        """
        # Los rangos corresponden de 4 a 6 y 10 a 12
        if self.valor in range(4,7) or self.valor in range(10,13):
            return self.valor
        if self.valor is 1:
            if self.palo is ORO or self.palo is COPA:
                return 15
            if self.palo is BASTO:
                return 30
            if self.palo is ESPADA:
                return 40
        if self.valor is 2:
            return 20
        if self.valor is 3:
            return 22
        if self.valor is 7:
            if self.palo is BASTO or self.palo is COPA:
                return 7
            if self.palo is ORO:
                return 25
            if self.palo is ESPADA:
                return 27

    def puntos(self):
        """
        Retorna el valor que corresponderia para el envido de esta carta.
        """
        if self.valor > 7:
            return 0
        else:
            return self.valor

    def puntos_envido(self, otra):
        valor_esta = 0 if self.valor > 7 else self.valor
        valor_otra = 0 if otra.valor > 7 else otra.valor
        if self.palo == otra.palo:
            return 20 + valor_otra + valor_esta
        else:
            return max(valor_esta, valor_otra)

    def image(self):
        """
        Retorna un string que contiene la direccion de la imagen de la carta 'self'.
        """
        d = {BASTO : 'B', ORO : 'O', COPA : 'C', ESPADA : 'E'}
        return "/static/truco/cartas/" + d[self.palo] + str(self.valor) + ".jpg"


class Mano(models.Model):
    jugador = models.ForeignKey('Jugador', related_name='manos', null=True)

    def __unicode__(self):
        return ", ".join([str(c) for c in self.cartas.all()])

    def __eq__(self,other):
        return all([carta in other.cartas.all() for carta in self.cartas.all()] )

    def asignaciones(self,jugador,a,b,c):
        """
        Le asigna a la mano 'self' el jugador 'jugador' y las cartas 'a','b' y 'c',
        encargandose de las llamadas a save() donde sea necesario.
        """
        self.jugador = jugador
        self.save()
        for carta in [a,b,c]:
            carta.mano = self
            carta.save()

    def puntos_de_envido_posibles(self):
        cartas = self.cartas.all()
        return [cartas[a].puntos_envido(cartas[b]) for a in range(3) for b in range(3) if a < b]

    def puntos_del_envido(self):
        return max(self.puntos_de_envido_posibles())

    def jugar_carta(self, id):
        """
        Toma la carta de esta mano con el id 'id' y le asigna un numero de jugada.
        Para la primer jugada, asignará un 0, luego 1, y luego 2.
        """
        c = self.cartas.get(id=id)
        c.jugada = self.cartas.exclude(jugada=None).count()
        c.save()

    def comparar_jugada(self, otra, ronda):
        """
        Devuelve True si la carta jugada en la vuelta i de self le gana a la de otra.
        False si la carta de other gana, None si son pardas.
        Se asume 0 <= ronda < 3.
        """
        c1 = self.cartas.get(jugada=ronda)
        c2 = otra.cartas.get(jugada=ronda)
        if c1.jerarquia() > c2.jerarquia():
            return True
        elif c1.jerarquia() < c2.jerarquia():
            return False
        else:
            return None

    def cartas_jugadas(self):
        return self.cartas.exclude(jugada=None)

    def cartas_jugables(self):
        return self.cartas.filter(jugada=None)


class Jugador(models.Model):
    user = models.ForeignKey(User)
    equipo = models.ForeignKey('Equipo', related_name='jugadores')
    partida = models.ForeignKey('Partida', related_name="jugadores")
    posicion_en_mesa = models.IntegerField()
    visto = models.BooleanField(default=False)
    mostrar_cartas = models.BooleanField(default=False)
    puntos_cantados = models.IntegerField(null=True)

    @property
    def mano(self):
        return self.manos.latest('id')

    def toca_jugar(self):
        if self.partida.ultima_ronda.terminada:
            return not self.visto
        else:
            return self.posicion_en_mesa == self.partida.ultima_ronda.turno_de()

    def mano_desde_lista(self,lista):
        """
        Toma una lista de tres cartas y le asigna al jugador 'self' una mano
        con esas tres cartas.
        """
        m = Mano()
        m.asignaciones(self,lista[0],lista[1],lista[2])

    def comparar_manos(self,otro):
        """
        Toma dos jugadores y devuelve una lista, donde para cada jugada habrá una entrada
        en la lista. Si la jugada fue ganada por el jugador 'self', será True. Si ganó 'otro'
        es False. Si empardaron es None.x
        """
        return [self.mano.comparar_jugada(otro.mano,i) for i in range(len(self.mano.cartas_jugadas()))]

    def jugadas(self):
        m = self.manos.latest('id')
        return m.cartas_jugadas()

    def mostrar_mensajes(self):
        """
        Devuelve un string que es el resultado de todos los mensajes del jugador
        concatenados.
        """
        mensajes = filter(None, [m.mostrar() for m in self.mensajes.order_by('de_truco')])
        return ", ".join(mensajes)

    def es_mano(self):
        return self.posicion_en_mesa == self.partida.ultima_ronda.mano

class Truco(models.Model):
    ronda = models.OneToOneField('Ronda', related_name='truco')
    cantado = models.BooleanField(default=False)
    esperando_respuesta = models.BooleanField(default=False)
    puntos_truco = models.IntegerField(default=1)
    tiene_el_quiero = models.ForeignKey('Equipo',null=True)

    def opciones(self, jugador):
        botones = []
        if self.tiene_el_quiero and jugador == self.tiene_el_quiero.pie() and self.esperando_respuesta:
            botones.append('Quiero')
            botones.append('No quiero')
        if self.puntos_truco == 1:
            botones.append('Truco')
        elif self.puntos_truco == 2 and self.tiene_el_quiero and jugador == self.tiene_el_quiero.pie():
            botones.append('Quiero retruco')
        elif self.puntos_truco == 3 and self.tiene_el_quiero and jugador == self.tiene_el_quiero.pie():
            botones.append('Quiero vale cuatro')
        return botones

    def input(self, jugador, input):
        Mensaje.objects.filter(de_truco=True,
            emisor__partida__id=jugador.partida.id).delete()
        jugador.mensajes.filter(de_envido=True).delete()
        Mensaje.broadcast(jugador,cantos[input], de_truco=True)
        if input in ['truco','quiero-retruco','quiero-vale-cuatro']:
            self.cantado = True
            self.esperando_respuesta = True
            self.tiene_el_quiero = jugador.equipo.contrincante()
            self.puntos_truco += 1
        elif input == 'quiero':
            self.esperando_respuesta = False
        elif input == 'no-quiero':
            Mensaje.objects.exclude(de_truco=True).delete()
            self.esperando_respuesta = False
            self.puntos_truco -= 1
            self.ronda.sumar_al_otro(jugador,self.puntos_truco)
            self.ronda.terminada = True
            self.ronda.save()
        self.save()

class Envido(models.Model):
    ronda = models.OneToOneField('Ronda', related_name='envido')
    cantado = models.BooleanField(default=False)
    cantando_puntos = models.BooleanField(default=False)
    terminado = models.BooleanField(default=False)
    envido = models.PositiveSmallIntegerField(default=0)
    real_envido = models.BooleanField(default=False)
    falta_envido = models.BooleanField(default=False)
    tiene_el_quiero = models.ForeignKey('Equipo',null=True)
    querido = models.NullBooleanField(null=True)
    puntosE = models.IntegerField(default=0)
    toca_cantar = models.IntegerField(null=True)

    def opciones(self, jugador):
        if not self.disponible(jugador):
            if not self.esperando_respuesta():
                return []
        if self.ronda.truco.esperando_respuesta and self.ronda.truco.puntos_truco == 2:
            if not self.esperando_respuesta():
                return ['Envido esta primero', 'Real Envido esta primero', 'Falta Envido esta primero']
        botones = []
        # Si hay que cantar puntos
        if self.cantando_puntos and not self.terminado:
            return [self.cantar_puntos(jugador),'mentir']
        # Si se planta
        if jugador.equipo == self.tiene_el_quiero and self.cantado:
            botones.append('Quiero')
            botones.append('No quiero')
        # Si el jugador quiere 'subir de nivel'
        if self.envido < 2 and not (self.real_envido or self.falta_envido):
            botones.append('Envido')
        if not self.real_envido and not self.falta_envido:
            botones.append('Real Envido')
        if not self.falta_envido:
            botones.append('Falta Envido')
        return botones

    def input(self, jugador, input):
        jugador.mensajes.filter(de_envido=True).delete()
        try:
            Mensaje.broadcast(jugador,cantos[input], de_envido=True)
        except KeyError:
            # El jugador cantó puntos/mintió
            pass
        # Si se plantó
        if input == 'quiero':
            self.cantando_puntos = True
            self.puntosE = self.puntos_quiero()
            self.querido = True
            self.toca_cantar = self.ronda.mano
            self.save()
            return
        elif input == 'no-quiero':
            self.puntosE = self.puntos_no_quiero()
            self.terminado = True
            self.querido = False
            self.save()
            return
        # Si cantó puntos
        elif input == slugify(self.cantar_puntos(jugador)) or input == 'mentir':
            if jugador.puntos_cantados == None:
                jugador.puntos_cantados = jugador.mano.puntos_del_envido()
                jugador.save()
            self.toca_cantar = (self.toca_cantar + 1) % self.ronda.partida.cantidad_jugadores
            Mensaje.broadcast(jugador,self.cantar_puntos(jugador),de_envido=True)
            if all(j.puntos_cantados for j in self.ronda.partida.jugadores.all()):
                self.terminado = True
            self.save() 
            return
        # Si quiere avanzar más
        elif input in ['envido','envido-esta-primero']:
            self.envido += 1
        elif input in ['real-envido','real-envido-esta-primero']:
            self.real_envido = True
        elif input in ['falta-envido','falta-envido-esta-primero']:
            self.falta_envido = True
        self.cantado = True
        # turno del otro
        self.tiene_el_quiero = jugador.equipo.contrincante()
        self.save()

    def puntos_quiero(self):
        if self.falta_envido:
            equipos = self.ronda.partida.equipos.all()
            puntos_jugador = max(e.puntos_partida for e in equipos)
            if puntos_jugador < 15:
                return (15 - puntos_jugador)
            else:
                return (30 - puntos_jugador)
        puntos = 3 if self.real_envido else 0
        puntos += 2 * self.envido
        return puntos

    def puntos_no_quiero(self):
        if self.falta_envido:
            if not self.real_envido and self.envido == 0:
                return 1
            if not self.real_envido and self.envido == 2:
                return 5
            else:
                puntos = 3 if self.real_envido else 0
                puntos += 2 * self.envido
                return puntos
        if self.real_envido:
            return 1 if not self.envido else self.envido * 2
        return self.envido

    def cantar_puntos(self, jugador):
        if jugador.puntos_cantados == None:
            puntos_envido = jugador.mano.puntos_del_envido()
        else:
            puntos_envido = jugador.puntos_cantados
        if jugador.es_mano():
            return 'Tengo ' + str(puntos_envido)
        # Si no es mano
        otro = jugador.equipo.contrincante()
        if puntos_envido > otro.mejores_puntos_cantados():
            return str(puntos_envido) + ' son mejores!'
        else:
            return 'Son buenas'

    def esperando_respuesta(self):
        return self.cantado and not self.terminado

    def disponible(self, jugador):
        jugaron_una = jugador.mano.cartas_jugadas().count() == 0
        truco = self.ronda.truco
        acepto_truco = (not truco.esperando_respuesta) if truco.puntos_truco == 2 else truco.puntos_truco > 2
        return jugaron_una and not acepto_truco and not self.terminado

    def ganador_envido(self):
        """
        Devuelve el equipo ganador del envido para esta ronda.
        """
        if not self.querido:
            return
        [e0,e1] = self.ronda.partida.equipos.all()
        if e0.mejores_puntos_cantados() > e1.mejores_puntos_cantados():
            return e0
        elif e0.mejores_puntos_cantados() < e1.mejores_puntos_cantados():
            return e1
        else:
            jugadores = self.ronda.partida.jugadores
            return jugadores.get(posicion_en_mesa=self.ronda.mano).equipo

    def dar_puntos(self):
        if not self.cantado:
            return
        gana = self.ganador_envido()
        if self.querido:
            if any(j.mostrar_cartas for j in gana.jugadores.all()):
                p_cantados = gana.mejores_puntos_cantados()
                ganador = max(gana.jugadores.all(),key=lambda j:j.puntos_cantados)
                if not p_cantados in ganador.mano.puntos_de_envido_posibles():
                    otro = gana.contrincante()
                    otro.puntos_partida += self.puntosE
                    otro.save()
                    return
            gana.puntos_partida += self.puntosE
            gana.save()
        else:
            e = self.tiene_el_quiero.contrincante()
            e.puntos_partida += self.puntosE
            e.save()


class Ronda(models.Model):
    partida = models.ForeignKey('Partida',related_name='rondas')
    mano = models.IntegerField(default=0)
    terminada = models.BooleanField(default=False)

    @classmethod
    def crear(cls, partida, mano):
        """
        Toma una partida y un numero 'mano' y crea una ronda asociada a las mismas, donde
        el jugador en la posicion 'mano' es mano.
        Es un metodo de clase, por lo que debe ser llamado de la forma:
        Ronda(partida,0)
        """
        r = cls(partida=partida, mano=mano)
        r.save()
        Truco(ronda=r).save()
        Envido(ronda=r).save()
        Mensaje.objects.filter(emisor__partida__id=partida.id).delete()
        partida.jugadores.update(visto=False,puntos_cantados=None,mostrar_cartas=False)
        r.repartir()

    def opciones(self, jugador):
        """
        Toma un jugador y devuelve una lista de strings con las opciones
        que el jugador tiene para cantar.
        """
        opciones = []
        # Si terminó la partida:
        if self.terminada:
            if jugador.visto:
                return []
            else:
                if self.envido.terminado and self.envido.querido:
                    gano = self.envido.ganador_envido()
                    if not jugador in gano.jugadores.all() and not \
                    any([j.mostrar_cartas for j in self.partida.jugadores.all()]):
                        opciones += ['Mostrar las cartas']
                opciones += ['Continuar']
                return opciones
        # Si no es el turno del jugador:
        if not jugador.toca_jugar():
            return []
        # Opciones del jugador:
        if not self.envido.esperando_respuesta():
            opciones += self.truco.opciones(jugador)
        opciones += self.envido.opciones(jugador)
        if not self.truco.esperando_respuesta and not self.envido.esperando_respuesta():
            opciones += ['Irse al Mazo']
        return opciones

    def accion(self, jugador, input):
        """
        Toma un jugador y un string y ejecuta la accion asociada a ese string.
        """
        if input in [str(carta.id) for carta in jugador.mano.cartas_jugables()]:
            if not self.truco.esperando_respuesta and not self.envido.esperando_respuesta():
                jugador.mensajes.all().delete()
                jugador.mano.jugar_carta(input)
                una_jugada = self.partida.jugadores.all()[0].jugadas().count()
                if all(j.jugadas().count() == una_jugada for j in self.partida.jugadores.all()):
                    self.fin_de_ronda()
            else:
                return
        elif input in ['truco','quiero-retruco','quiero-vale-cuatro']:
            self.truco.input(jugador, input)
        elif input in ['envido','real-envido','falta-envido','envido-esta-primero', \
                'envido-esta-primero', 'real-envido-esta-primero','falta-envido-esta-primero']:
            self.envido.input(jugador, input)
        elif input == slugify(self.envido.cantar_puntos(jugador)) or input == 'mentir':
            self.envido.input(jugador, input)
        elif input in ['quiero','no-quiero']:
            if self.envido.esperando_respuesta():
                self.envido.input(jugador, input)
            else:
                self.truco.input(jugador, input)
        elif input == "irse-al-mazo":
            Mensaje.objects.filter(emisor__partida__id=self.partida.id).delete()
            Mensaje.broadcast(jugador,cantos[input], de_fin=True)
            self.terminada = True
            self.sumar_al_otro(jugador, self.truco.puntos_truco)
        elif input == "continuar":
            jugador.mensajes.filter(de_fin=True).delete()
            jugador.visto = True
            jugador.save()
        elif input == "mostrar-las-cartas" and not self.envido.ganador_envido().jugador_con_mas_puntos().mostrar_cartas:
            Mensaje.broadcast(jugador,cantos[input], de_fin=True)
            j = self.envido.ganador_envido().jugador_con_mas_puntos()
            j.mostrar_cartas = True
            j.save()
        else:
            return

        self.save()


    def sumar_al_otro(self, jugador, puntos):
        """
        Toma un jugador y un entero. Le suma al equipo opuesto al jugador
        los puntos contenidos en el entero.
        """
        otro = jugador.equipo.contrincante()
        otro.puntos_partida += puntos
        otro.save()

    def repartir(self):
        """
        Reparte una mano de cartas para cada jugador en la ronda.
        """
        # sacar cartas
        mazo = [Carta(palo=p,valor=v) for p in range(4) for v in [1,2,3,4,5,6,7,10,11,12]]
        l = random.sample(mazo, self.partida.jugadores.count()*3)

        # asignacion de cartas
        for n in range(self.partida.jugadores.count()):
            jugador = self.partida.jugadores.get(posicion_en_mesa=n)
            jugador.mano_desde_lista(l[n*3:n*3+3])

    def buscar_ganador(self):
        """
        Devuelve el equipo que ganó esta ronda o levanta
        la excepción IndexError si la ronda debe continuar.
        """
        [equipo1, equipo2] = self.partida.equipos.all()
        resultados1 = equipo1.mejores_jugadas()
        resultados2 = equipo2.mejores_jugadas()
        # Las reglas tienen que estar hardcodeadas en algún lado. Lo siento.
        if resultados1[0] == resultados2[0]:
            if resultados1[1] == resultados2[1]:
                if resultados1[2] == resultados2[2]:
                    raise IndexError
                else:
                    return equipo1 if resultados1[2] > resultados2[2] else equipo2
            else:
                return equipo1 if resultados1[1] > resultados2[1] else equipo2
        if resultados1[0] > resultados2[0]:
            if resultados1[1] == resultados2[1] or resultados1[1] > resultados2[1]:
                return equipo1
            else:
                if resultados1[2] == resultados2[2]:
                    return equipo1
                else:
                    return equipo1 if resultados1[2] > resultados2[2] else equipo2
        else:
            if resultados1[1] == resultados2[1] or resultados1[1] < resultados2[1]:
                return equipo2
            else:
                if resultados1[2] == resultados2[2]:
                    return equipo2
                else:
                    return equipo1 if resultados1[2] > resultados2[2] else equipo2

    def fin_de_ronda(self):
        """
        Chequea si según las cartas jugadas la ronda debería terminar o no. En
        caso de que sí, da los puntos al ganador y declara a la ronda como terminada.
        """
        try:
            equipo_ganador = self.buscar_ganador()
        except IndexError:
            if all([j.mano.cartas.filter(jugada=2).exists() for j in self.partida.jugadores.all()]):
                equipo_ganador = self.partida.jugadores.get(posicion_en_mesa=self.mano).equipo
            else:
                return
        equipo_ganador.puntos_partida += self.truco.puntos_truco
        equipo_ganador.save()
        self.terminada = True
        self.save()

    def turno_de(self):
        # Si se juega envido
        if self.envido.esperando_respuesta():
            if self.envido.cantando_puntos:
                return self.envido.toca_cantar
            else:
                return self.envido.tiene_el_quiero.pie().posicion_en_mesa
        # Si se juega truco
        if self.truco.esperando_respuesta:
            return self.truco.tiene_el_quiero.pie().posicion_en_mesa
        # Turno definido por cartas:
        jugadas = [(j.jugadas().count(), j) for j in \
                self.partida.jugadores.order_by('posicion_en_mesa')]
        menos_jugadas = min([a for (a, b) in jugadas])
        jugadas = (jugadas + jugadas)[(self.ultimo_ganador().posicion_en_mesa):]
        while len(jugadas):
            if jugadas[0][0] == menos_jugadas:
                return jugadas[0][1].posicion_en_mesa
            else:
                jugadas.pop(0)

    def ultimo_ganador(self):
        """
        Devuelve el jugador que ganó la última vuelta.
        """
        ultima_vuelta = min([j.jugadas().count() for j in self.partida.jugadores.all()]) - 1
        if ultima_vuelta == -1:
            return self.partida.jugadores.get(posicion_en_mesa=self.mano)
        jerarquias = []
        for j in self.partida.jugadores.all():
            carta = j.mano.cartas.get(jugada=ultima_vuelta)
            jerarquias.append((carta.jerarquia(), j))
        if jerarquias == []:
            return self.partida.jugadores.get(posicion_en_mesa=self.mano)
        max_jerarquia = max([jer for (jer, jug) in jerarquias])
        ganadores = [jug for (jer, jug) in jerarquias if jer == max_jerarquia]
        # Caso de pardas
        jugadores_pares = self.partida.equipos.get(pares=True).jugadores.all()
        jugadores_impares = self.partida.equipos.get(pares=False).jugadores.all()
        if any([g in jugadores_pares for g in ganadores]) and \
           any([g in jugadores_impares for g in ganadores]):
            return self.partida.jugadores.get(posicion_en_mesa=self.mano)
        # Caso en que ganan dos del mismo equipo
        ganadores.sort(key=lambda j: j.posicion_en_mesa)
        return ganadores[0]

class Mensaje(models.Model):
    mensaje = models.CharField(max_length=50)
    emisor = models.ForeignKey('Jugador')
    receptor = models.ForeignKey('Jugador',related_name='mensajes')
    de_envido = models.BooleanField(default=False)
    de_truco = models.BooleanField(default=False)
    de_fin = models.BooleanField(default=False)

    def __unicode__(self):
        return self.emisor.user.username + " dice '" + self.mensaje + \
                "' a " + self.receptor.user.username

    @classmethod
    def broadcast(cls, emisor, mensaje, de_envido=False, de_truco=False, de_fin=False):
        """
        Toma un jugador y un mensaje, y envía el mensaje a todos los otros jugadores
        en la partida.
        Opcionalmente se puede especificar si el mensaje es de envido, de truco o
        del final de la partida
        """
        for j in emisor.partida.jugadores.exclude(id=emisor.id):
            cls(emisor=emisor,mensaje=mensaje,receptor=j, \
                de_envido=de_envido,de_truco=de_truco,de_fin=de_fin).save()

    def mostrar(self):
        """
        Devuelve el mensaje, o nada, dependiendo del estado de la partida.
        """
        ronda = self.emisor.partida.ultima_ronda
        if self.de_truco and ronda.envido.esperando_respuesta():
            return None
        else:
            return self.mensaje


class Equipo(models.Model):
    partida = models.ForeignKey('Partida', related_name='equipos')
    puntos_partida = models.IntegerField(default=0)
    pares = models.BooleanField(default=0)

    def mejores_jugadas(self):
        """
        Retorna una lista con la mayor jerarquía 
        jugada por el equipo en cada vuelta
        """
        result = []
        try:
            for vuelta in range(3):
                result.append(max(j.mano.cartas.get(jugada=vuelta).jerarquia() \
                              for j in self.jugadores.all()))
        except Carta.DoesNotExist:
            pass
        return result

    def pie(self):
        """
        Devuelve el jugador pie de este equipo
        """
        jugadores = list(self.partida.jugadores.order_by('posicion_en_mesa'))
        pos_mano = self.partida.ultima_ronda.mano
        jugadores = jugadores[pos_mano:] + jugadores[:pos_mano]
        jugadores = filter(lambda j:(j.posicion_en_mesa%2==0)==self.pares,jugadores)
        return jugadores[-1]

    def sin_cantar(self):
        """
        Devuelve el primer jugador del equipo (ordenados por la posición en mesa)
        que no haya cantado aún sus puntos de envido. Si todos cantaron,
        devuelve None.
        """
        try:
            jugadores = self.jugadores.order_by('posicion_en_mesa')
            return jugadores.filter(puntos_cantados=None)[0]
        except IndexError:
            return None

    def mejores_puntos_cantados(self):
        """
        Devuelve un número correspondiente a los mejores puntos cantados para
        todos los miembros de este equipo.
        """
        return max([j.puntos_cantados for j in self.jugadores.all()])

    def jugador_con_mas_puntos(self):
        """
        Devuelve el jugador de este equipo que cantó la mayor cantidad de puntos.
        """
        return max(self.jugadores.all(),key=lambda j:j.puntos_cantados)

    def contrincante(self):
        """
        Devuelve el equipo opuesto a este.
        """
        return self.partida.equipos.exclude(id=self.id)[0]


class Partida(models.Model):
    nombre = models.CharField(max_length=50)
    esperando = models.BooleanField(default=True)
    terminada = models.BooleanField(default=False)
    cantidad_jugadores = models.IntegerField(default=2)
    puntos_max = models.IntegerField(default=30)

    def __unicode__(self):
        return self.nombre

    @property
    def ultima_ronda(self):
        return self.rondas.latest('id')

    def mostrar_partida(self, jugador):
        """
        Toma un jugador y devuelve un diccionario con la información necesaria para
        mostrar la partida en el template correspondiente.
        """
        result = {
            "error_message" : "no_error", 
            "ident" : self.id,
            "nombre" : self.nombre,
            "template" : self.template(),
        }
        if jugador == None:
            result["error_message"] = "La sala esta llena, no se permiten observadores"
            return result
        if not self.esta_llena():
            result["error_message"] = "Esperando contrincante"
            return result
        if self.terminada:
            gana = max(self.equipos.all(),key=lambda e:e.puntos_partida).jugadores.all()
            res = "" 
            for j in gana:
                res += str(j.user) + " "
            if self.cantidad_jugadores == 2:
                result["error_message"] = "Esta partida terminó. Ganó " + res
            else: 
                result["error_message"] = "Esta partida terminó. Ganaron " + res
            return result

        # Maquina de estados
        if self.esperando:
            if self.rondas.count() == 0:
                Ronda.crear(partida=self,mano=0)
            elif not self.jugadores.filter(visto=False).exists():
                self.ultima_ronda.envido.dar_puntos()
                ultima = self.rondas.filter(terminada=True).last()
                Ronda.crear(partida=self,mano=(ultima.mano+1)%self.cantidad_jugadores)
            self.esperando = False
            self.save()

        result.update({
        "opciones"       : self.ultima_ronda.opciones(jugador),
        "mensaje"        : jugador.mostrar_mensajes(),
        "ronda"          : self.ultima_ronda,
        "jugadores"      : self.ordenar_jugadores(jugador),
        "toca_jugar"     : jugador.toca_jugar(),
        })
        return result

    def procesar_entrada(self, jugador, input):
        """
        Toma un jugador y un string. Ejecuta la acción input y luego chequea
        si la ronda ha terminado.
        """
        # Asegurarnos de que estamos esperando input de este jugador
        if jugador not in self.jugadores.all():
            return
        if self.ultima_ronda.terminada:
            if input in ['continuar','mostrar-las-cartas']:
                self.ultima_ronda.accion(jugador,input)
            else:
                return
        elif self.ultima_ronda.turno_de() != jugador.posicion_en_mesa:
            return

        self.ultima_ronda.accion(jugador,input)

        # Si se termino la ronda, ver si hay un ganador
        if self.ultima_ronda.terminada:
            if any([j.equipo.puntos_partida>=self.puntos_max for j in self.jugadores.all()]):
                self.terminada = True
            else:
                self.esperando = True
            self.save()

    def esta_llena(self):
        return self.jugadores.count() == self.cantidad_jugadores

    def ordenar_jugadores(self, jugador):
        """
        Devuelve una lista ordenada de los jugadores para el jugador especificado 
        según el orden esperado por los templates.
        """
        jugadores = list(self.jugadores.all())
        pos = jugador.posicion_en_mesa
        jugadores = jugadores[pos:] + jugadores[:pos]
        return jugadores

    def template(self):
        return "componentes_mesa/mesa_para_" + str(self.cantidad_jugadores)

    def sumar_jugador(self, usuario):
        """
        Añade un jugador a la partida.
        """
        # Se asume que hay espacio para otro jugador.
        if self.equipos.count() == 0:
            Equipo(partida=self,pares=True).save()
            Equipo(partida=self,pares=False).save()
        e = self.equipos.get(pares=self.jugadores.count()%2==0)
        Jugador(user=usuario,partida=self,posicion_en_mesa=self.jugadores.count(), \
            equipo=e).save()

    def jugador(self, usuario):
        """
        Retorna el jugador de esta partida asignado al usuario dado.
        Si no juega, devuelve None
        """
        try:
            return self.jugadores.get(user__id=usuario.id)
        except Jugador.DoesNotExist:
            return None

