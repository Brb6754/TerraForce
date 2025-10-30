from __future__ import annotations
import pygame
import random
import math
from colores import *
from sprite_manager import SpriteManager


class ArbolManager:

    def __init__(self):
        self.tree_images_original = []
        self.tree_images = []
        self.arboles = []

        try:
            tree1_original = pygame.image.load("Assets/tree.png").convert_alpha()
            self.tree_images_original.append(tree1_original)
            self.tree_images.append(pygame.transform.scale(tree1_original, (10, 10)))
            print("tree.png cargado")
        except pygame.error as e:
            print(f"No se pudo cargar tree.png: {e}")

        try:
            tree2_original = pygame.image.load("Assets/tree1.png").convert_alpha()
            self.tree_images_original.append(tree2_original)
            self.tree_images.append(pygame.transform.scale(tree2_original, (8, 8)))
            print("tree1.png cargado")
        except pygame.error as e:
            print(f"No se pudo cargar tree1.png: {e}")

    def generar_arboles(self, mapa_terreno, ancho_mapa, alto_mapa):
        if not self.tree_images:
            print("No hay imágenes de árboles cargadas")
            return

        self.arboles = []

        for y in range(alto_mapa):
            for x in range(ancho_mapa):
                terreno = mapa_terreno[y][x]

                if terreno == 'bosque':
                    probabilidad = 0.015
                elif terreno == 'pasto':
                    probabilidad = 0.003
                else:
                    continue

                if random.random() < probabilidad:
                    tipo_arbol = random.randint(0, len(self.tree_images) - 1)
                    self.arboles.append((x, y, tipo_arbol))

        print(f"Generados {len(self.arboles)} árboles en el mapa")

    def dibujar_arboles(self, pantalla, mapa_rect, offset_x, offset_y, tile_size, zoom):
        if not self.tree_images_original or not self.arboles:
            return

        for x, y, tipo in self.arboles:
            screen_x = mapa_rect.x + x * tile_size + offset_x + 20
            screen_y = mapa_rect.y + y * tile_size + offset_y + 20

            if not mapa_rect.collidepoint(screen_x, screen_y):
                continue

            tree_img_original = self.tree_images_original[tipo]

            tamaño_arbol = max(16, int(32 * zoom))
            tree_img = pygame.transform.scale(tree_img_original, (tamaño_arbol, tamaño_arbol))

            tree_rect = tree_img.get_rect(center=(screen_x + tile_size // 2, screen_y + tile_size // 2))

            pantalla.blit(tree_img, tree_rect)


class Boton:
    def __init__(self, x, y, ancho, alto, texto, callback=None, color=COLOR_BOTON):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color_base = color
        self.color_actual = color
        self.callback = callback
        self.hover = False

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color_actual, self.rect, border_radius=6)
        pygame.draw.rect(pantalla, COLOR_BORDE, self.rect, 2, border_radius=6)
        texto_render = FUENTE_PEQUENA.render(self.texto, True, COLOR_TEXTO)
        texto_rect = texto_render.get_rect(center=self.rect.center)
        pantalla.blit(texto_render, texto_rect)

    def manejar_evento(self, evento, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.color_actual = COLOR_BOTON_HOVER
            if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                if self.callback:
                    self.callback()
                return True
        else:
            self.color_actual = self.color_base
        return False

class BotonDesplegable:
    def __init__(self, x, y, ancho, alto, titulo, tareas, color_titulo):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.titulo = titulo
        self.tareas = tareas
        self.color_titulo = color_titulo
        self.expandido = False
        self.alto_expandido = alto + len(tareas) * 35 + 10
        self.botones = []
        self.crear_botones(x, y + alto + 5, ancho)

    def crear_botones(self, x, y, ancho):
        self.botones = []
        for i, (texto, callback, color) in enumerate(self.tareas):
            boton = Boton(x, y + i * 35, ancho, 32, texto, callback, color)
            self.botones.append(boton)

    def toggle(self):
        self.expandido = not self.expandido

    def manejar_evento(self, evento, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
                self.toggle()
                return True
        if self.expandido:
            for boton in self.botones:
                if boton.manejar_evento(evento, mouse_pos):
                    return True
        return False

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color_titulo, self.rect, border_radius=6)
        pygame.draw.rect(pantalla, COLOR_BORDE, self.rect, 2, border_radius=6)
        flecha = " " if not self.expandido else " "
        texto_titulo = FUENTE_NORMAL.render(f"{self.titulo}{flecha}", True, COLOR_TEXTO)
        pantalla.blit(texto_titulo, (self.rect.x + 10, self.rect.y + 6))
        if self.expandido:
            for boton in self.botones:
                boton.dibujar(pantalla)

class Terminal:
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.lineas = []
        self.max_lineas = 100
        self.scroll_offset = 0
        self.lineas_visibles = (alto - 40) // 18

    def agregar(self, texto, tipo="info"):
        color_map = {"info": COLOR_TERMINAL_TEXTO, "exito": COLOR_EXITO, "advertencia": COLOR_ADVERTENCIA, "peligro": COLOR_PELIGRO}
        color = color_map.get(tipo, COLOR_TERMINAL_TEXTO)
        timestamp = pygame.time.get_ticks() // 1000
        mins, secs = divmod(timestamp, 60)
        hrs, mins = divmod(mins, 60)
        timestamp = f"{hrs%24:02d}:{mins:02d}:{secs:02d}"
        self.lineas.append((f"[{timestamp}] {texto}", color))
        if len(self.lineas) > self.max_lineas:
            self.lineas.pop(0)
        self.scroll_offset = max(0, len(self.lineas) - self.lineas_visibles)

    def scroll(self, direccion):
        self.scroll_offset = max(0, min(len(self.lineas) - self.lineas_visibles, self.scroll_offset + direccion))

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, COLOR_TERMINAL, self.rect, border_radius=8)
        pygame.draw.rect(pantalla, COLOR_BORDE, self.rect, 2, border_radius=8)
        header = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 30)
        pygame.draw.rect(pantalla, COLOR_PANEL, header, border_radius=8)
        header_texto = FUENTE_NORMAL.render("TERMINAL", True, COLOR_TEXTO)
        pantalla.blit(header_texto, (self.rect.x + 10, self.rect.y + 5))
        y = self.rect.y + 38
        inicio = max(0, self.scroll_offset)
        fin = min(len(self.lineas), inicio + self.lineas_visibles)
        for i in range(inicio, fin):
            texto, color = self.lineas[i]
            texto_render = FUENTE_TERMINAL.render(texto, True, color)
            pantalla.blit(texto_render, (self.rect.x + 8, y))
            y += 18


COLORES_TERRENO = {
    'agua': (0, 151, 245),
    'agua_profunda': (2, 116, 186),
    'agua_orilla': (0, 151, 245),
    'pasto': (107, 161, 45),
    'bosque': (6, 110, 2),
    'montaña': (49, 54, 49),
    'nieve': (255, 250, 250),
    'desierto': (125, 120, 106),
    'desierto_arena': (92, 88, 77)
}

class MapaGenerador:
    @staticmethod
    def ruido_suave(x, y, semilla):
        n = x + y * 57 + semilla * 131
        n = (n << 13) ^ n
        return (1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0)

    @staticmethod
    def interpolar(a, b, x):
        ft = x * 3.1415927
        f = (1 - math.cos(ft)) * 0.5
        return a * (1 - f) + b * f

    @staticmethod
    def ruido_interpolado(x, y, semilla):
        entero_x = int(x)
        fraccion_x = x - entero_x
        entero_y = int(y)
        fraccion_y = y - entero_y
        v1 = MapaGenerador.ruido_suave(entero_x, entero_y, semilla)
        v2 = MapaGenerador.ruido_suave(entero_x + 1, entero_y, semilla)
        v3 = MapaGenerador.ruido_suave(entero_x, entero_y + 1, semilla)
        v4 = MapaGenerador.ruido_suave(entero_x + 1, entero_y + 1, semilla)
        i1 = MapaGenerador.interpolar(v1, v2, fraccion_x)
        i2 = MapaGenerador.interpolar(v3, v4, fraccion_x)
        return MapaGenerador.interpolar(i1, i2, fraccion_y)

    @staticmethod
    def generar_ruido_perlin(x, y, semilla, octavas=4):
        total = 0
        frecuencia = 1
        amplitud = 1
        max_valor = 0
        for i in range(octavas):
            total += MapaGenerador.ruido_interpolado(x * frecuencia, y * frecuencia, semilla + i) * amplitud
            max_valor += amplitud
            amplitud *= 0.5
            frecuencia *= 2
        return total / max_valor

    @staticmethod
    def generar_mapa(ancho=500, alto=300):
        mapa = []
        colores_mapa = []
        semilla = random.randint(0, 10000)
        semilla_humedad = random.randint(0, 10000)
        escala_principal = 0.08
        escala_detalle = 0.15

        for y in range(alto):
            fila = []
            fila_colores = []
            for x in range(ancho):
                elevacion = MapaGenerador.generar_ruido_perlin(x * escala_principal, y * escala_principal, semilla, octavas=5)
                humedad = MapaGenerador.generar_ruido_perlin(x * escala_principal, y * escala_principal, semilla_humedad, octavas=4)
                detalle = MapaGenerador.generar_ruido_perlin(x * escala_detalle, y * escala_detalle, semilla + 1000, octavas=2)
                valor_final = (elevacion * 0.7 + detalle * 0.3)
                elevacion = (elevacion + 1) / 2
                humedad = (humedad + 1) / 2
                valor_final = (valor_final + 1) / 2

                if humedad < 0.35 and 0.30 <= valor_final < 0.65:
                    tipo = 'desierto' if valor_final < 0.48 else 'desierto_arena'
                elif valor_final < 0.55:
                    tipo = 'pasto'
                elif valor_final < 0.72:
                    tipo = 'bosque' if humedad > 0.5 else 'pasto'
                elif valor_final < 0.85:
                    tipo = 'montaña'
                else:
                    tipo = 'nieve'

                color = COLORES_TERRENO[tipo]
                variacion = random.randint(-8, 8)
                color_variado = tuple(max(0, min(255, c + variacion)) for c in color)
                fila.append(tipo)
                fila_colores.append(color_variado)
            mapa.append(fila)
            colores_mapa.append(fila_colores)

        mapa, colores_mapa = MapaGenerador.suavizar_mapa(mapa, colores_mapa, ancho, alto)
        posiciones_rio = MapaGenerador.generar_rio(mapa, colores_mapa, ancho, alto)
        MapaGenerador.generar_lagos(mapa, colores_mapa, 3, posiciones_rio, ancho, alto)
        return mapa, colores_mapa

    @staticmethod
    def generar_rio(mapa, colores_mapa, ancho, alto):
        posiciones_rio = set()
        x = random.randint(ancho // 4, 3 * ancho // 4)
        y = 0
        semilla_rio = random.randint(0, 10000)

        ancho_rio = random.randint(8, 12)
        offset_curva = 0

        while y < alto:
            ruido_curva = MapaGenerador.generar_ruido_perlin(y * 0.15, 0, semilla_rio, octavas=3)
            offset_curva += ruido_curva * 0.8
            x_centro = x + int(offset_curva)
            x_centro = max(ancho_rio, min(ancho - ancho_rio - 1, x_centro))

            ancho_actual = ancho_rio + int(MapaGenerador.ruido_suave(y, 0, semilla_rio + 500) * 3)

            for dx in range(-ancho_actual // 2, ancho_actual // 2 + 1):
                nx = x_centro + dx
                if 0 <= nx < ancho and 0 <= y < alto:
                    distancia_normalizada = abs(dx) / (ancho_actual / 2)

                    if distancia_normalizada < 0.3:
                        tipo_agua = 'agua_profunda'
                        color_base = COLORES_TERRENO['agua_profunda']
                    elif distancia_normalizada < 0.7:
                        tipo_agua = 'agua'
                        color_base = COLORES_TERRENO['agua']
                    else:
                        tipo_agua = 'agua_orilla'
                        color_base = COLORES_TERRENO['agua_orilla']

                    mapa[y][nx] = tipo_agua

                    variacion = random.randint(-5, 5)
                    colores_mapa[y][nx] = tuple(max(0, min(255, c + variacion)) for c in color_base)
                    posiciones_rio.add((nx, y))
            y += 1
        return posiciones_rio

    @staticmethod
    def generar_lagos(mapa, colores_mapa, num_lagos, posiciones_rio, ancho, alto):
        lagos_creados = 0
        intentos = 0
        while lagos_creados < num_lagos and intentos < 50:
            intentos += 1
            centro_x = random.randint(ancho // 6, 5 * ancho // 6)
            centro_y = random.randint(alto // 6, 5 * alto // 6)
            muy_cerca = any(math.sqrt((centro_x - rx) ** 2 + (centro_y - ry) ** 2) < 15 for rx, ry in posiciones_rio)
            if muy_cerca:
                continue

            radio_base = random.randint(4, 8)
            semilla_lago = random.randint(0, 10000)
            tiles_lago = []

            for dy in range(-radio_base, radio_base + 1):
                for dx in range(-radio_base, radio_base + 1):
                    x = centro_x + dx
                    y = centro_y + dy
                    if 0 <= x < ancho and 0 <= y < alto:
                        distancia = math.sqrt(dx * dx + dy * dy)
                        ruido_borde = MapaGenerador.generar_ruido_perlin(dx * 0.25, dy * 0.25, semilla_lago, octavas=3)
                        radio_modificado = radio_base + ruido_borde * 2.5
                        if distancia < radio_modificado - 0.5:
                            tiles_lago.append((x, y))

            for x, y in tiles_lago:
                mapa[y][x] = 'agua'
                color = COLORES_TERRENO['agua']
                variacion = random.randint(-8, 8)
                colores_mapa[y][x] = tuple(max(0, min(255, c + variacion)) for c in color)

            MapaGenerador.limpiar_tiles_aislados_agua(mapa, colores_mapa, centro_x, centro_y, radio_base + 5, ancho, alto)
            lagos_creados += 1

    @staticmethod
    def limpiar_tiles_aislados_agua(mapa, colores_mapa, centro_x, centro_y, radio_limpieza, ancho, alto):
        for dy in range(-radio_limpieza, radio_limpieza + 1):
            for dx in range(-radio_limpieza, radio_limpieza + 1):
                x = centro_x + dx
                y = centro_y + dy
                if 0 < x < ancho - 1 and 0 < y < alto - 1:
                    if mapa[y][x] in ['agua', 'agua_profunda', 'agua_orilla']:
                        vecinos_agua = sum([
                            mapa[y-1][x] in ['agua', 'agua_profunda', 'agua_orilla'],
                            mapa[y+1][x] in ['agua', 'agua_profunda', 'agua_orilla'],
                            mapa[y][x-1] in ['agua', 'agua_profunda', 'agua_orilla'],
                            mapa[y][x+1] in ['agua', 'agua_profunda', 'agua_orilla']
                        ])
                        if vecinos_agua < 2:
                            mapa[y][x] = 'pasto'
                            color = COLORES_TERRENO['pasto']
                            variacion = random.randint(-8, 8)
                            colores_mapa[y][x] = tuple(max(0, min(255, c + variacion)) for c in color)

    @staticmethod
    def suavizar_mapa(mapa, colores_mapa, ancho, alto):
        nuevo_mapa = [fila[:] for fila in mapa]
        nuevos_colores = [fila[:] for fila in colores_mapa]
        for y in range(1, alto - 1):
            for x in range(1, ancho - 1):
                tipo_actual = mapa[y][x]
                vecinos = [mapa[y-1][x], mapa[y+1][x], mapa[y][x-1], mapa[y][x+1],
                            mapa[y-1][x-1], mapa[y-1][x+1], mapa[y+1][x-1], mapa[y+1][x+1]]
                contador = {}
                for vecino in vecinos:
                    contador[vecino] = contador.get(vecino, 0) + 1
                if contador.get(tipo_actual, 0) < 2:
                    tipo_mas_comun = max(contador, key=contador.get)
                    nuevo_mapa[y][x] = tipo_mas_comun
                    color = COLORES_TERRENO[tipo_mas_comun]
                    variacion = random.randint(-8, 8)
                    nuevos_colores[y][x] = tuple(max(0, min(255, c + variacion)) for c in color)
        return nuevo_mapa, nuevos_colores


class Mapa:
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.ancho_mapa = 235
        self.alto_mapa = 150
        self.mapa_terreno, self.colores_mapa = MapaGenerador.generar_mapa(self.ancho_mapa, self.alto_mapa)
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = 1.0
        self.zoom_min = 0.5
        self.zoom_max = 5.0
        self.tile_size_base = 2
        self.tile_size = 2
        self.calcular_tile_size()
        self.pan_velocidad = 20

        self.sprite_manager = SpriteManager()
        self.ciclo_animacion = 0

        self.arbol_manager = ArbolManager()

    def calcular_tile_size(self):
        self.tile_size_base = max(2, min(
            (self.rect.width - 40) // self.ancho_mapa,
            (self.rect.height - 40) // self.alto_mapa
        ))
        self.tile_size = int(self.tile_size_base * self.zoom)

    def manejar_teclado(self, tecla):
        tecla_presionada = False

        if tecla == pygame.K_LEFT:
            self.offset_x += self.pan_velocidad
            tecla_presionada = True
        elif tecla == pygame.K_RIGHT:
            self.offset_x -= self.pan_velocidad
            tecla_presionada = True
        elif tecla == pygame.K_UP:
            self.offset_y += self.pan_velocidad
            tecla_presionada = True
        elif tecla == pygame.K_DOWN:
            self.offset_y -= self.pan_velocidad
            tecla_presionada = True

        if tecla_presionada:
            self.limitar_offset()
            return True

        return False

    def manejar_evento(self, evento, mouse_pos):
        if evento.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(mouse_pos):
                mouse_x_rel = mouse_pos[0] - self.rect.x - self.offset_x
                mouse_y_rel = mouse_pos[1] - self.rect.y - self.offset_y
                zoom_anterior = self.zoom

                if evento.y > 0:
                    self.zoom = min(self.zoom_max, self.zoom * 1.1)
                else:
                    self.zoom = max(self.zoom_min, self.zoom / 1.1)

                self.tile_size = int(self.tile_size_base * self.zoom)
                factor = self.zoom / zoom_anterior
                self.offset_x = int(mouse_x_rel - (mouse_x_rel * factor))
                self.offset_y = int(mouse_y_rel - (mouse_y_rel * factor))
                self.limitar_offset()

                return True

        return False

    def limitar_offset(self):
        max_offset_x = 20
        min_offset_x = -(self.ancho_mapa * self.tile_size - self.rect.width + 20)
        max_offset_y = 20
        min_offset_y = -(self.alto_mapa * self.tile_size - self.rect.height + 20)

        self.offset_x = max(min_offset_x, min(max_offset_x, self.offset_x))
        self.offset_y = max(min_offset_y, min(max_offset_y, self.offset_y))

    def dibujar(self, pantalla, colonos, hora_dia, zonas_activas, sitios_construccion):
        pygame.draw.rect(pantalla, COLOR_MAPA_BG, self.rect, border_radius=8)

        inicio_x = max(0, -self.offset_x // self.tile_size)
        fin_x = min(self.ancho_mapa, (self.rect.width - self.offset_x) // self.tile_size + 2)
        inicio_y = max(0, -self.offset_y // self.tile_size)
        fin_y = min(self.alto_mapa, (self.rect.height - self.offset_y) // self.tile_size + 2)

        for y in range(inicio_y, fin_y):
            for x in range(inicio_x, fin_x):
                screen_x = self.rect.x + x * self.tile_size + self.offset_x + 20
                screen_y = self.rect.y + y * self.tile_size + self.offset_y + 20
                if self.rect.collidepoint(screen_x, screen_y):
                    color_original = self.colores_mapa[y][x]
                    color_tinteado = self._aplicar_tinte_dia(color_original, hora_dia)
                    pygame.draw.rect(pantalla, color_tinteado, (screen_x, screen_y, self.tile_size, self.tile_size))

        self.arbol_manager.dibujar_arboles(
            pantalla,
            self.rect,
            self.offset_x,
            self.offset_y,
            self.tile_size,
            self.zoom
        )

        for zona_id, (centro_x, centro_y, color_zona, tiles_zona) in zonas_activas.items():
            for tx, ty in tiles_zona:
                screen_x = self.rect.x + tx * self.tile_size + self.offset_x + 20
                screen_y = self.rect.y + ty * self.tile_size + self.offset_y + 20
                tile_rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)

                if self.rect.colliderect(tile_rect):
                    pygame.draw.rect(pantalla, color_zona, tile_rect, 1)

        for sitio_id, datos_sitio in sitios_construccion.items():
            color_zona = datos_sitio["color"]
            tiles_zona = datos_sitio["tiles"]

            if datos_sitio["en_progreso"]:
                color_zona = (255, 255, 0)

            for tx, ty in tiles_zona:
                screen_x = self.rect.x + tx * self.tile_size + self.offset_x + 20
                screen_y = self.rect.y + ty * self.tile_size + self.offset_y + 20
                tile_rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)

                if self.rect.colliderect(tile_rect):
                    pygame.draw.rect(pantalla, color_zona, tile_rect, 1)

        self.ciclo_animacion += 1

        for colono in colonos:
            if colono.salud > 0:
                map_x = int(colono.posicion[0])
                map_y = int(colono.posicion[1])

                px = self.rect.x + map_x * self.tile_size + self.offset_x + 20
                py = self.rect.y + map_y * self.tile_size + self.offset_y + 20

                if self.rect.collidepoint(px, py):
                    sprite_dibujado = self.sprite_manager.dibujar_colono_sprite(
                        pantalla, colono, (int(px), int(py)),
                        self.zoom, self.ciclo_animacion
                    )

                    if not sprite_dibujado:
                        color_map = {"Ingeniero": COLOR_INGENIERO, "Biólogo": COLOR_BIOLOGO,
                                        "Explorador": COLOR_EXPLORADOR, "Guardia": COLOR_GUARDIA}

                        color_original_colono = color_map.get(colono.tipo, (255, 255, 255))
                        color_tinteado = self._aplicar_tinte_dia(color_original_colono, hora_dia)

                        radio = max(3, int(self.tile_size * 1.5))
                        pygame.draw.circle(pantalla, color_tinteado, (int(px), int(py)), radio)
                        pygame.draw.circle(pantalla, (0, 0, 0), (int(px), int(py)), radio, 1)

        pygame.draw.rect(pantalla, COLOR_BORDE, self.rect, 2, border_radius=8)
        self.dibujar_leyenda(pantalla)
        self.dibujar_info_zoom(pantalla)

    def dibujar_info_zoom(self, pantalla):
        zoom_texto = FUENTE_PEQUENA.render(f"Zoom: {self.zoom:.1f}x", True, COLOR_TEXTO_SECUNDARIO)
        pantalla.blit(zoom_texto, (self.rect.right - 80, self.rect.y + 10))

    def dibujar_leyenda(self, pantalla):
        leyenda_y_zonas = self.rect.bottom - 50
        leyenda_x_zonas = self.rect.x + 10

        zonas = [
            ("Hábitat/Base", (200, 180, 255)),
            ("Laboratorio", (100, 200, 255)),
            ("Cultivos", (100, 255, 100)),
            ("Reactor", (255, 220, 100)),
        ]

        for i, (nombre, color) in enumerate(zonas):
            x = leyenda_x_zonas + i * 120
            pygame.draw.rect(pantalla, color, (x, leyenda_y_zonas, 15, 15), 2)
            texto = FUENTE_PEQUENA.render(nombre, True, COLOR_TEXTO_SECUNDARIO)
            pantalla.blit(texto, (x + 20, leyenda_y_zonas + 2))

        leyenda_y_terreno = self.rect.bottom - 25
        leyenda_x_terreno = self.rect.x + 10

        terrenos = [
            ("Agua", COLORES_TERRENO['agua']),
            ("Pasto", COLORES_TERRENO['pasto']),
            ("Bosque", COLORES_TERRENO['bosque']),
            ("Desierto", COLORES_TERRENO['desierto']),
        ]

        for i, (nombre, color) in enumerate(terrenos):
            x = leyenda_x_terreno + i * 120
            pygame.draw.rect(pantalla, color, (x, leyenda_y_terreno, 15, 15))
            pygame.draw.rect(pantalla, COLOR_BORDE, (x, leyenda_y_terreno, 15, 15), 1)
            texto = FUENTE_PEQUENA.render(nombre, True, COLOR_TEXTO_SECUNDARIO)
            pantalla.blit(texto, (x + 20, leyenda_y_terreno + 2))

    def _aplicar_tinte_dia(self, color_original, hora):
        """Aplica un tinte al color basado en la hora del día."""
        r, g, b = color_original

        if 18 <= hora <= 20:
            r = min(255, int(r * 1.1 + 20))
            g = max(0, int(g * 0.9))
            b = max(0, int(b * 0.8))
        elif hora >= 21 or hora < 6:
            factor = 0.4
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor + 15)

        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        return (r, g, b)