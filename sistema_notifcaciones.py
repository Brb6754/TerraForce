import pygame
from colores import *
import time

class Notificacion:
    def __init__(self, mensaje, tipo="info", duracion=4000):
        self.mensaje = mensaje
        self.tipo = tipo
        self.duracion = duracion
        self.tiempo_creacion = pygame.time.get_ticks()
        self.alpha = 255
        self.offset_y = -80
        self.objetivo_y = 0
        self.eliminando = False

        self.colores = {
            "info": (50, 120, 200),
            "exito": COLOR_EXITO,
            "advertencia": COLOR_ADVERTENCIA,
            "peligro": COLOR_PELIGRO,
            "tarea": (100, 150, 255)
        }
        self.color = self.colores.get(tipo, self.colores["info"])

        self.iconos = {
            "info": " ",
            "exito": " ",
            "advertencia": " ",
            "peligro": " ",
            "tarea": " "
        }
        self.icono = self.iconos.get(tipo, self.iconos["info"])

    def actualizar(self):
        tiempo_actual = pygame.time.get_ticks()
        tiempo_vida = tiempo_actual - self.tiempo_creacion

        if self.offset_y < self.objetivo_y:
            self.offset_y += 3
            if self.offset_y > self.objetivo_y:
                self.offset_y = self.objetivo_y

        if tiempo_vida > self.duracion - 500:
            self.eliminando = True
            fade_progress = (tiempo_vida - (self.duracion - 500)) / 500
            self.alpha = int(255 * (1 - fade_progress))

        return tiempo_vida < self.duracion

    def dibujar(self, pantalla, x, y):
        y_final = y + self.offset_y

        ancho, alto = 320, 70
        superficie = pygame.Surface((ancho, alto), pygame.SRCALPHA)

        color_fondo = (*self.color, int(self.alpha * 0.9))
        pygame.draw.rect(superficie, color_fondo, (0, 0, ancho, alto), border_radius=10)

        color_borde = (*self.color, self.alpha)
        pygame.draw.rect(superficie, color_borde, (0, 0, ancho, alto), 3, border_radius=10)

        pygame.draw.rect(superficie, color_borde, (0, 0, 6, alto), border_radius=10)


        palabras = self.mensaje.split()
        lineas = []
        linea_actual = ""

        for palabra in palabras:
            test_linea = linea_actual + " " + palabra if linea_actual else palabra
            if FUENTE_PEQUENA.size(test_linea)[0] < 240:
                linea_actual = test_linea
            else:
                if linea_actual:
                    lineas.append(linea_actual)
                linea_actual = palabra

        if linea_actual:
            lineas.append(linea_actual)

        y_texto = 15 if len(lineas) > 1 else 25
        for i, linea in enumerate(lineas[:2]):
            texto_render = FUENTE_PEQUENA.render(linea, True, (255, 255, 255, self.alpha))
            superficie.blit(texto_render, (55, y_texto + i * 20))

        if not self.eliminando:
            tiempo_actual = pygame.time.get_ticks()
            progreso = (tiempo_actual - self.tiempo_creacion) / self.duracion
            ancho_barra = int((ancho - 20) * (1 - progreso))
            pygame.draw.rect(superficie, (255, 255, 255, int(self.alpha * 0.6)),
                           (10, alto - 8, ancho_barra, 4), border_radius=2)

        pantalla.blit(superficie, (x, y_final))


class SistemaNotificaciones:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.notificaciones = []
        self.max_notificaciones = 5
        self.separacion = 80

    def agregar(self, mensaje, tipo="info", duracion=4000):
        notificacion = Notificacion(mensaje, tipo, duracion)

        for i, notif in enumerate(self.notificaciones):
            notif.objetivo_y = (i + 1) * self.separacion

        self.notificaciones.insert(0, notificacion)

        if len(self.notificaciones) > self.max_notificaciones:
            self.notificaciones = self.notificaciones[:self.max_notificaciones]

    def actualizar(self):
        self.notificaciones = [n for n in self.notificaciones if n.actualizar()]

        for i, notif in enumerate(self.notificaciones):
            notif.objetivo_y = i * self.separacion

    def dibujar(self, pantalla):
        for notif in self.notificaciones:
            notif.dibujar(pantalla, self.x, self.y)

    def actualizar_posicion(self, ancho_ventana, alto_ventana):
        self.x = ancho_ventana - 340
        self.y = 80