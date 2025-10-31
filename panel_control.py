import pygame
import sys
import random
import math
from simulador import Simulador
from componentes import Boton, BotonDesplegable, Mapa
from colores import *
from sistema_notifcaciones import SistemaNotificaciones

class ArtifactDisplay:
    def __init__(self, image, map_rect):
        self.image = image
        self.map_rect = map_rect
        self.rect = self.image.get_rect()

        self.rect.centerx = random.randint(map_rect.left + self.rect.width // 2,
                                             map_rect.right - self.rect.width // 2)
        self.rect.centery = random.randint(map_rect.top + self.rect.height // 2,
                                             map_rect.bottom - self.rect.height // 2)

        self.start_time = pygame.time.get_ticks()
        self.duration = 4000

    def update(self):
        return pygame.time.get_ticks() - self.start_time > self.duration

    def draw(self, pantalla):
        alpha = 255
        time_elapsed = pygame.time.get_ticks() - self.start_time
        if time_elapsed < 500:
            alpha = int((time_elapsed / 500) * 255)
        elif self.duration - time_elapsed < 500:
            alpha = int(((self.duration - time_elapsed) / 500) * 255)

        temp_image = self.image.copy()
        temp_image.set_alpha(alpha)

        pantalla.blit(temp_image, self.rect)


class LightningBolt:
    def __init__(self, image, window_size, screen_rect):
        self.image = image
        self.rect = self.image.get_rect()

        self.rect.centerx = random.randint(screen_rect.left, screen_rect.right)
        self.rect.centery = random.randint(screen_rect.top, screen_rect.bottom)

        self.start_time = pygame.time.get_ticks()
        self.duration = 800

    def update(self):
        return pygame.time.get_ticks() - self.start_time > self.duration

    def draw(self, pantalla):
        pantalla.blit(self.image, self.rect)

class Rocket:
    def __init__(self, image, window_size):
        self.original_image = image
        self.image = image
        self.window_size = window_size

        self.image = pygame.transform.rotate(self.original_image, 10)
        self.rect = self.image.get_rect()

        self.pos = pygame.Vector2(-self.rect.width, -self.rect.height)
        self.rect.topleft = self.pos

        self.speed = 25

        self.vel = pygame.Vector2(1, 1).normalize() * self.speed

    def update(self):
        self.pos += self.vel
        self.rect.topleft = self.pos

        if self.rect.left > self.window_size[0] or self.rect.top > self.window_size[1]:
            return False
        return True

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Snowflake:
    def __init__(self, image, map_rect):
        self.image = image
        self.map_rect = map_rect

        start_x = random.uniform(map_rect.left, map_rect.right)
        start_y = map_rect.top - random.uniform(5, image.get_height())
        self.pos = pygame.Vector2(start_x, start_y)

        self.speed_y = random.uniform(5, 10)

        self.drift_magnitude = random.uniform(0.2, 0.7)
        self.drift_offset = random.uniform(0, 2 * math.pi)
        self.start_time = pygame.time.get_ticks()

        self.rect = self.image.get_rect(center=self.pos)

    def update(self, current_time):
        self.pos.y += self.speed_y

        time_factor = (current_time - self.start_time) / 1000.0
        self.pos.x += math.sin(time_factor + self.drift_offset) * self.drift_magnitude

        self.rect.center = self.pos

        if self.rect.top > self.map_rect.bottom:
            return False
        return True

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Meteor:
    def __init__(self, image, map_rect):
        self.original_image = image
        self.image = image
        self.map_rect = map_rect

        start_x = random.uniform(map_rect.left, map_rect.right)
        start_y = map_rect.top - random.uniform(20, image.get_height() * 2)
        self.pos = pygame.Vector2(start_x, start_y)

        angle = random.uniform(math.pi * 0.4, math.pi * 0.6)
        speed = random.uniform(3, 7)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed

        self.start_time = pygame.time.get_ticks() + random.randint(0, 1)
        self.active = False

        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-2, 2)
        self.rect = self.image.get_rect(center=self.pos)


    def update(self, current_time):
        if not self.active:
            if current_time >= self.start_time:
                self.active = True
            else:
                return

        self.pos += self.vel

        self.rect.center = self.pos

        if self.rect.top > self.map_rect.bottom:
            return False
        return True

    def draw(self, surface):
        if self.active:
            surface.blit(self.image, self.rect)


def ejecutar_juego():
    
    pygame.init()
    ancho_ventana, alto_ventana = 1200, 700
    
    try:
        pantalla = pygame.display.set_mode((ancho_ventana, alto_ventana), pygame.RESIZABLE)
        pygame.display.set_caption("TerraForm")
    except pygame.error as e:
        print(f"Error display: {e}")
        sys.exit()

    reloj = pygame.time.Clock()
    ejecutando = True
    notificaciones = SistemaNotificaciones(0, 0)

    active_meteors = []
    active_snowflakes = []
    active_rockets = []
    active_artifacts = []
    active_lightning = []

    colono_scroll_offset = 0
    altura_linea_colono = 42
    lineas_visibles_colonos = 1
    heal_buttons = {}

    simulacion_activa = True
    velocidad = 1
    frames_por_ciclo = 60
    contador_frames = 0

    # Cargar imágenes
    meteor_image = None
    try:
        original_meteor = pygame.image.load("Assets/Meteorito.png").convert_alpha()
        meteor_image = pygame.transform.scale(original_meteor, (100, 100))
    except pygame.error as e:
        print(f"Error cargando Meteorito.png: {e}")

    snowflake_image = None
    try:
        original_snow = pygame.image.load("Assets/copo.png").convert_alpha()
        snowflake_image = pygame.transform.scale(original_snow, (20, 20))
    except pygame.error as e:
        print(f"Error cargando copo.png: {e}")

    rocket_image = None
    try:
        original_rocket = pygame.image.load("Assets/cohete.png").convert_alpha()
        rocket_image = pygame.transform.scale(original_rocket, (500, 500))
    except pygame.error as e:
        print(f"Error cargando cohete.png: {e}")

    artifact_images = []
    artifact_files = ["Assets/2.png", "Assets/3.png", "Assets/4.png"]
    #for file in artifact_files:
        #try:
            #original_artifact = pygame.image.load(file).convert_alpha()
            #scaled_artifact = pygame.transform.scale(original_artifact, (300, 300))
            #artifact_images.append(scaled_artifact)
            #print(f"{file} cargado")
        #except pygame.error as e:
            #print(f"Error cargando {file}: {e}")

    lightning_image = None
    try:
        original_lightning = pygame.image.load("Assets/rayo.png").convert_alpha()
        lightning_image = pygame.transform.scale(original_lightning, (500, 500))
        print("rayo.png cargado correctamente.")
    except pygame.error as e:
        print(f"Error cargando rayo.png: {e}")

    shake_active = False
    shake_duration = 0
    shake_start_time = 0
    shake_magnitude = 5

    cold_effect_active = False
    cold_effect_end_cycle = 0

    # Función para manejar eventos visuales
    def handle_visual_event(event_type):
        nonlocal active_meteors, active_snowflakes, active_rockets, active_artifacts, active_lightning
        nonlocal shake_active, shake_duration, shake_start_time
        nonlocal cold_effect_active, cold_effect_end_cycle
        
        if event_type == "meteor_shower" and meteor_image and mapa:
            num_meteors = random.randint(5, 8)
            for _ in range(num_meteors):
                active_meteors.append(Meteor(meteor_image, mapa.rect))
            print(f"Visual event: Triggered {num_meteors} meteors.")

        elif event_type == "earthquake":
            shake_active = True
            shake_duration = 1200
            shake_start_time = pygame.time.get_ticks()
            print(f"Visual event: Triggered earthquake shake.")

        elif event_type == "temp_drop":
            if snowflake_image and mapa:
                cold_effect_active = True
                cold_effect_end_cycle = simulador.ciclo + 3
                print(f"Visual event: Triggered temp drop. Ends on cycle {cold_effect_end_cycle}.")

        elif event_type == "new_colonists" and rocket_image:
            print("Visual event: Triggered new rocket arrival.")
            active_rockets.append(Rocket(rocket_image, (ancho_ventana, alto_ventana)))

        elif event_type == "electromagnetic_storm" and lightning_image:
            for i in range(3):
                active_lightning.append(LightningBolt(lightning_image,
                                                        (ancho_ventana, alto_ventana),
                                                        mapa.rect))
            print(f"Visual event: Triggered 3 lightning bolts for storm.")

        elif event_type == "artifact_discovery" and artifact_images and mapa:
            if not active_artifacts:
                chosen_image = random.choice(artifact_images)
                new_artifact = ArtifactDisplay(chosen_image, mapa.rect)
                active_artifacts.append(new_artifact)
                print(f"Visual event: Triggered artifact discovery.")

    # Inicializar simulador
    simulador = Simulador(
        callback_log=notificaciones.agregar,
        callback_visual=handle_visual_event
    )

    # Función para actualizar botones
    def actualizar_botones():
        nonlocal botones_control, menu_construccion, menus_desplegables
        
        panel_ancho = max(250, min(350, int(ancho_ventana * 0.25)))
        ancho_cont = panel_ancho - 40
        y_inicio = 20
        
        botones_control = [
            Boton(20, y_inicio, ancho_cont, 40, 
                  "PAUSAR" if simulacion_activa else "REANUDAR",
                  toggle_pausa,
                  COLOR_ADVERTENCIA if simulacion_activa else COLOR_EXITO),
            Boton(20, y_inicio + 50, (ancho_cont - 10) // 3, 35, "1x",
                  lambda: cambiar_velocidad(1),
                  COLOR_BOTON if velocidad != 1 else COLOR_EXITO),
            Boton(20 + (ancho_cont - 10) // 3 + 5, y_inicio + 50, (ancho_cont - 10) // 3, 35, "2x",
                  lambda: cambiar_velocidad(2),
                  COLOR_BOTON if velocidad != 2 else COLOR_EXITO),
            Boton(20 + 2 * ((ancho_cont - 10) // 3) + 10, y_inicio + 50, (ancho_cont - 10) // 3, 35, "3x",
                  lambda: cambiar_velocidad(3),
                  COLOR_BOTON if velocidad != 3 else COLOR_EXITO)
        ]
        
        y_constr = y_inicio + 95
        menu_construccion = BotonDesplegable(20, y_constr, ancho_cont, 35, "CONSTRUIR", [], (80, 180, 80))
        actualizar_menu_construccion()
        
        menu_y = 25
        menu_ancho = 150
        menu_espacio = 10
        num_menus = 4
        x_start = ancho_ventana - (num_menus * (menu_ancho + menu_espacio)) + menu_espacio - 10
        
        menu_data = [
            ("MANTENIMIENTO", [
                ("Rep. Lab", "reparar_laboratorio", "Rep. lab", (50, 100, 180)),
                ("Rep. Hab", "reparar_habitat", "Rep. hab", (50, 120, 180)),
                ("+ Energía", "generar_energia", "Reactor", (200, 150, 50))
            ], (30, 60, 120)),
            ("RECURSOS", [
                ("+ Comida", "recolectar_alimentos", "Cosecha", (50, 180, 50)),
                ("Cultivar", "cultivar", "Cultivo", (80, 180, 50)),
                ("+ Material", "recolectar_recursos", "Minería", (150, 100, 50))
            ], (40, 120, 40)),
            ("EXPLORACIÓN", [
                ("Expl. Terreno", "explorar_terreno", "Recon.", (255, 200, 100)),
                ("Expl. Caverna", "explorar_cavernas", "Caverna", (200, 150, 80)),
                ("Cartografiar", "cartografiar", "Mapeo", (180, 130, 60))
            ], (180, 120, 40))
        ]
        
        menus_desplegables = []
        cur_x = x_start
        for tit, tareas_info, col in menu_data:
            tareas = [(txt, lambda t=tipo, d=desc: agregar_tarea(t, d), tcol) 
                     for txt, tipo, desc, tcol in tareas_info]
            menu = BotonDesplegable(cur_x, menu_y, menu_ancho, 40, tit, tareas, col)
            menus_desplegables.append(menu)
            cur_x += menu_ancho + menu_espacio

    # Función para actualizar layout
    def actualizar_layout():
        nonlocal ancho_ventana, alto_ventana, pantalla, tiempo_rect, info_rect
        nonlocal lineas_visibles_colonos, mapa
        
        ancho_ventana = max(1000, ancho_ventana)
        alto_ventana = max(600, alto_ventana)
        
        try:
            pantalla = pygame.display.set_mode((ancho_ventana, alto_ventana), pygame.RESIZABLE)
        except pygame.error as e:
            print(f"Error resize: {e}")
            return
        
        panel_ancho = max(250, min(350, int(ancho_ventana * 0.25)))
        ancho_cont = panel_ancho - 40
        
        tiempo_y = 150
        tiempo_rect = pygame.Rect(20, tiempo_y, ancho_cont, 85)
        
        info_y = tiempo_rect.bottom + 10
        info_alto = alto_ventana - info_y - 20
        info_rect = pygame.Rect(20, info_y, ancho_cont, info_alto)
        
        header_h = 40
        if altura_linea_colono > 0:
            lineas_visibles_colonos = max(1, (info_alto - header_h) // altura_linea_colono)
        else:
            lineas_visibles_colonos = 1
        
        mapa_x = panel_ancho
        mapa_ancho = ancho_ventana - mapa_x - 20
        mapa_alto = alto_ventana - 40
        mapa_y = 20
        
        if mapa:
            mapa.rect.topleft = (mapa_x, mapa_y)
            mapa.rect.size = (mapa_ancho, mapa_alto)
            mapa.calcular_tile_size()
        else:
            mapa = Mapa(mapa_x, mapa_y, mapa_ancho, mapa_alto)
        
        if hasattr(mapa, 'mapa_terreno') and mapa.mapa_terreno:
            mapa.arbol_manager.generar_arboles(
                mapa.mapa_terreno,
                mapa.ancho_mapa,
                mapa.alto_mapa
            )
            print("Árboles generados en el mapa")
        
        if mapa:
            pad = 10
            rec_alto = 190
            nx = mapa.rect.left + pad
            ny = mapa.rect.top + pad + rec_alto + pad + 10
            notificaciones.x = nx
            notificaciones.y = ny
        
        actualizar_botones()

    def actualizar_menu_construccion():
        opciones = []
        if simulador:
            try:
                items = sorted(simulador.sitios_construccion.items())
            except AttributeError:
                items = []
            
            for sid, datos in items:
                if datos and not datos.get("en_progreso", True):
                    txt = f"{datos.get('tipo_nuevo', '?')} ({datos.get('costo', '?')})"
                    cb = lambda s=sid: simulador.iniciar_construccion(s)
                    opciones.append((txt, cb, (80, 180, 80)))
        
        if menu_construccion:
            menu_construccion.tareas = opciones
            if hasattr(menu_construccion, 'rect'):
                menu_construccion.crear_botones(10, 140, 200)

    def agregar_tarea(tipo, descripcion):
        simulador.agregar_tarea_personalizada(tipo, descripcion)

    def toggle_pausa():
        nonlocal simulacion_activa
        simulacion_activa = not simulacion_activa
        actualizar_botones()

    def cambiar_velocidad(v):
        nonlocal velocidad, frames_por_ciclo
        velocidad = v
        frames_por_ciclo = {1: 45, 2: 22, 3: 10, 4: 5}.get(v, 45)
        actualizar_botones()

    def ejecutar_ciclo():
        res = simulador.ejecutar_ciclo()
        if isinstance(res, dict) and ("construccion" in res or "descubrimiento" in res):
            actualizar_menu_construccion()
        return res

    def curar_colono(cid):
        costo_alimentos = 15
        costo_energia = 10
        costo_materiales = 20

        if (simulador.recursos["alimentos"] < costo_alimentos or
            simulador.recursos["energia"] < costo_energia or
            simulador.recursos["materiales"] < costo_materiales):

            faltantes = []
            if simulador.recursos["alimentos"] < costo_alimentos:
                faltantes.append(f"{costo_alimentos}")
            if simulador.recursos["energia"] < costo_energia:
                faltantes.append(f"{costo_energia}")
            if simulador.recursos["materiales"] < costo_materiales:
                faltantes.append(f"{costo_materiales}")

            notificaciones.agregar(
                f"Curación: Faltan {', '.join(faltantes)}",
                "peligro",
                3000
            )
            return

        c = next((co for co in simulador.colonos if co.id == cid), None)

        if c and c.salud < 100:
            simulador.recursos["alimentos"] -= costo_alimentos
            simulador.recursos["energia"] -= costo_energia
            simulador.recursos["materiales"] -= costo_materiales

            cura = random.randint(25, 50)
            sa = c.salud
            c.curar(cura)
            cr = c.salud - sa

            simulador.log(
                f"Curado {c.nombre}(+{cr}). Salud:{c.salud}%. Recursos: -{costo_alimentos} -{costo_energia} -{costo_materiales}",
                "exito"
            )
            notificaciones.agregar(
                f"{c.nombre} +{cr}HP (-{costo_alimentos} -{costo_energia} -{costo_materiales})",
                "exito",
                3000
            )
        elif c:
            notificaciones.agregar(f"{c.nombre} ya está sano", "info", 2000)

    def dibujar_info_colonos():
        nonlocal colono_scroll_offset, heal_buttons
        
        pygame.draw.rect(pantalla, COLOR_PANEL, info_rect, border_radius=8)
        pygame.draw.rect(pantalla, COLOR_BORDE, info_rect, 2, border_radius=8)
        
        tit_txt = "ESTADO COLONOS"
        tit_rend = FUENTE_NORMAL.render(tit_txt, True, COLOR_ADVERTENCIA)
        tit_rect = tit_rend.get_rect(left=info_rect.x + 10, top=info_rect.y + 10)
        pantalla.blit(tit_rend, tit_rect)
        
        cvl = [c for c in simulador.colonos if c.salud > 0]
        nv = len(cvl)
        np = simulador.colonos_perdidos
        
        cnt_txt = f"(V:{nv}/P:{np})"
        cnt_rend = FUENTE_PEQUENA.render(cnt_txt, True, COLOR_TEXTO_SECUNDARIO)
        cnt_rect = cnt_rend.get_rect(left=tit_rect.right + 10, centery=tit_rect.centery)
        if cnt_rect.right > info_rect.right - 10:
            cnt_rect.right = info_rect.right - 10
        pantalla.blit(cnt_rend, cnt_rect)
        
        pygame.draw.line(pantalla, COLOR_BORDE, 
                        (info_rect.x + 10, info_rect.y + 35),
                        (info_rect.right - 10, info_rect.y + 35), 1)
        
        cvl.sort(key=lambda c: c.edad)
        tc = nv
        y_col = info_rect.y + 45
        alt_lin = altura_linea_colono
        
        max_off = max(0, tc - lineas_visibles_colonos)
        colono_scroll_offset = max(0, min(colono_scroll_offset, max_off))
        
        c_mostrar = cvl[colono_scroll_offset:colono_scroll_offset + lineas_visibles_colonos]
        vis_ids = set()

        for c in c_mostrar:
            vis_ids.add(c.id)
            btn_w = 50
            btn_h = 18
            btn_x = info_rect.right - btn_w - 5
            btn_y = y_col
            
            hb = heal_buttons.get(c.id)
            if hb is None or hb.rect.topleft != (btn_x, btn_y):
                hb = Boton(btn_x, btn_y, btn_w, btn_h, "Curar",
                          lambda cid=c.id: curar_colono(cid), COLOR_EXITO)
                heal_buttons[c.id] = hb
            
            if c.salud < 100:
                hb.dibujar(pantalla)

            nom = f"{c.nombre[:8]}({c.tipo[:3]},{c.edad})"
            txt = FUENTE_PEQUENA.render(nom, True, COLOR_TEXTO)
            max_nx = btn_x - 10
            
            if txt.get_width() > max_nx - (info_rect.x + 15):
                ratio = (max_nx - (info_rect.x + 15)) / txt.get_width()
                cv = max(5, int(len(nom) * ratio) - 2)
                nom = nom[:cv] + ".."
                txt = FUENTE_PEQUENA.render(nom, True, COLOR_TEXTO)
            
            pantalla.blit(txt, (info_rect.x + 15, y_col))

            bar_y = y_col + 22
            bar_wt = info_rect.width - 30
            bar_wi = (bar_wt - 10) // 2
            bar_h = 8
            bar_sx = info_rect.x + 15
            
            pygame.draw.rect(pantalla, (30, 30, 40), (bar_sx, bar_y, bar_wi, bar_h), border_radius=3)
            
            sw = int((c.salud / 100) * bar_wi)
            scol = COLOR_EXITO if c.salud > 60 else (COLOR_ADVERTENCIA if c.salud > 30 else COLOR_PELIGRO)
            pygame.draw.rect(pantalla, scol, (bar_sx, bar_y, sw, bar_h), border_radius=3)

            if c.lifestage == "Adulto" and c.ocupado and c.accion_actual and c.accion_actual.duracion > 0:
                acc = c.accion_actual

                tarea_desc = str(acc.descripcion).split(':')[0].strip()[:10]
                if acc.zona_id:
                    tarea_desc = f"{tarea_desc} @ {acc.zona_id[:3]}"

                tarea_rend = FUENTE_PEQUENA.render(f"Tarea: {tarea_desc}", True, COLOR_TEXTO_SECUNDARIO)
                pantalla.blit(tarea_rend, (bar_sx + bar_wi + 10, y_col))

                prog = 0
                if acc.duracion > 0:
                    prog = c.progreso_accion / acc.duracion
                prog = min(1.0, max(0.0, prog))
                bar_px = bar_sx + bar_wi + 10
                
                pygame.draw.rect(pantalla, (40, 40, 30), (bar_px, bar_y, bar_wi, bar_h), border_radius=3)
                pygame.draw.rect(pantalla, COLOR_ADVERTENCIA, (bar_px, bar_y, int(bar_wi * prog), bar_h), border_radius=3)

            y_col += alt_lin

        ids_borrar = set(heal_buttons.keys()) - vis_ids
        for cid in ids_borrar:
            del heal_buttons[cid]
        
        if tc > lineas_visibles_colonos:
            scr_h = info_rect.height - 40
            scr_x = info_rect.right + 5
            scr_y = info_rect.y + 35
            ind_h = max(15, int(scr_h * (lineas_visibles_colonos / tc)))
            ind_y = scr_y
            scroll_range = tc - lineas_visibles_colonos
            
            if scroll_range > 0:
                ind_y += int((scr_h - ind_h) * (colono_scroll_offset / scroll_range))
            
            pygame.draw.rect(pantalla, (30, 30, 40), (scr_x, scr_y, 8, scr_h), border_radius=4)
            pygame.draw.rect(pantalla, COLOR_BORDE, (scr_x, ind_y, 8, ind_h), border_radius=4)

    def dibujar_barra_recurso(superficie, y, etiqueta, valor, valor_max, color):
        texto_val = f"{valor}/{valor_max}"
        texto = FUENTE_PEQUENA.render(f"{etiqueta}: {texto_val}", True, COLOR_TEXTO)
        superficie.blit(texto, (15, y))
        
        bx = 15
        by = y + 18
        bw = superficie.get_width() - 30
        bh = 10
        
        pygame.draw.rect(superficie, (30, 30, 40, 200), (bx, by, bw, bh), border_radius=3)
        
        porc = 0
        if valor_max > 0:
            porc = min(1.0, valor / valor_max)
        
        vw = int(porc * bw)
        col_fin = color
        umbral = 0.3 * valor_max
        
        if valor <= umbral:
            col_fin = COLOR_PELIGRO
        elif valor <= umbral * 2:
            col_fin = COLOR_ADVERTENCIA
        
        col_alpha = (*col_fin[:3], 220)
        pygame.draw.rect(superficie, col_alpha, (bx, by, vw, bh), border_radius=3)

    def dibujar_recursos():
        pan_w = 200
        pan_h = 190
        pad = 10
        
        if not mapa:
            return
        
        x = mapa.rect.left + pad
        y = mapa.rect.top + pad
        
        try:
            sf = pygame.Surface((pan_w, pan_h), pygame.SRCALPHA)
        except pygame.error:
            sf = pygame.Surface((pan_w, pan_h))
            sf.set_alpha(220)
        
        cf = (*COLOR_PANEL[:3], 180)
        pygame.draw.rect(sf, cf, (0, 0, pan_w, pan_h), border_radius=8)
        
        cb = (*COLOR_BORDE[:3], 200)
        pygame.draw.rect(sf, cb, (0, 0, pan_w, pan_h), 2, border_radius=8)

        try:
            conteo = simulador.get_conteo_estructuras()
        except AttributeError:
            conteo = {"laboratorio": 0, "habitat": 0, "cultivos": 0}

        rec = simulador.recursos
        slab = simulador.salud_laboratorio
        shab = simulador.salud_habitat
        max_s = simulador.MAX_SALUD_ESTRUCTURA
        max_r = 200

        y_ini = 10
        esp = 30

        dibujar_barra_recurso(sf, y_ini, "Alim", rec.get("alimentos", 0), max_r, COLOR_EXITO)
        dibujar_barra_recurso(sf, y_ini + esp, "Energ", rec.get("energia", 0), max_r, COLOR_ADVERTENCIA)
        dibujar_barra_recurso(sf, y_ini + 2 * esp, "Mater", rec.get("materiales", 0), max_r, (150, 150, 150))

        lab_label = f"Lab (x{conteo.get('laboratorio', 0)})"
        hab_label = f"Hab (x{conteo.get('habitat', 0)})"

        dibujar_barra_recurso(sf, y_ini + 3 * esp, lab_label, slab, max_s, (100, 150, 255))
        dibujar_barra_recurso(sf, y_ini + 4 * esp, hab_label, shab, max_s, (200, 180, 255))

        cult_label = f"Cultivos: x{conteo.get('cultivos', 0)}"
        cult_texto = FUENTE_PEQUENA.render(cult_label, True, COLOR_TEXTO)
        sf.blit(cult_texto, (15, y_ini + 5 * esp + 5))

        pantalla.blit(sf, (x, y))

    def dibujar_cola_prioridad():
        pan_w = 280
        pan_h = 220
        pad = 10
        
        if not mapa:
            return
        
        x = mapa.rect.right - pan_w - pad
        y = mapa.rect.bottom - pan_h - pad
        pr = pygame.Rect(x, y, pan_w, pan_h)
        
        try:
            sf = pygame.Surface((pan_w, pan_h), pygame.SRCALPHA)
        except pygame.error:
            sf = pygame.Surface((pan_w, pan_h))
            sf.set_alpha(220)
        
        cf = (*COLOR_PANEL[:3], 220)
        pygame.draw.rect(sf, cf, (0, 0, pan_w, pan_h), border_radius=8)
        
        cb = (*COLOR_BORDE[:3], 255)
        pygame.draw.rect(sf, cb, (0, 0, pan_w, pan_h), 2, border_radius=8)
        
        tit = FUENTE_NORMAL.render("COLA DE TAREAS", True, COLOR_ADVERTENCIA)
        sf.blit(tit, (10, 10))
        
        pygame.draw.line(sf, cb, (10, 35), (pan_w - 10, 35), 1)
        
        try:
            tareas = sorted(simulador.heap_prioridades.heap, key=lambda i: i[0])
        except Exception as e:
            tareas = []
            print(f"Err heap sort: {e}")
        
        yt = 45
        lh = 20
        lv = max(1, (pr.height - 55) // lh)
        
        for i, (prio, acc) in enumerate(tareas[:lv]):
            try:
                txt = str(acc)
                rend = FUENTE_PEQUENA.render(txt, True, COLOR_TEXTO)
                tw = rend.get_width()
                max_w = pr.width - 20
                
                if tw > max_w:
                    nc = len(txt)
                    ce = 0
                    if tw > 0:
                        ce = int(nc * (max_w / tw)) - 3
                    if ce > 0:
                        txt = txt[:ce] + ".."
                        rend = FUENTE_PEQUENA.render(txt, True, COLOR_TEXTO)
                
                sf.blit(rend, (15, yt))
                yt += lh
            except Exception as e:
                print(f"Err draw task: {e},{acc}")
        
        pantalla.blit(sf, (x, y))

    def dibujar_panel_lateral():
        pan_w_tot = max(250, min(350, int(ancho_ventana * 0.25)))
        pan_rect_f = pygame.Rect(10, 10, pan_w_tot - 20, alto_ventana - 20)
        
        pygame.draw.rect(pantalla, COLOR_PANEL, pan_rect_f, border_radius=8)
        pygame.draw.rect(pantalla, COLOR_BORDE, pan_rect_f, 2, border_radius=8)
        
        pygame.draw.rect(pantalla, (20, 20, 35), tiempo_rect, border_radius=6)
        pygame.draw.rect(pantalla, COLOR_BORDE, tiempo_rect, 1, border_radius=6)
        
        ft = FUENTE_PEQUENA.render(simulador.obtener_fecha_formateada(), True, COLOR_TEXTO)
        pantalla.blit(ft, (tiempo_rect.x + 10, tiempo_rect.y + 8))
        
        ht = FUENTE_TITULO.render(simulador.obtener_hora_formateada(), True, COLOR_ADVERTENCIA)
        pantalla.blit(ht, (tiempo_rect.x + 10, tiempo_rect.y + 30))
        
        pt = FUENTE_PEQUENA.render(simulador.obtener_periodo_dia(), True, COLOR_TEXTO_SECUNDARIO)
        pantalla.blit(pt, (tiempo_rect.x + 10, tiempo_rect.y + 65))
        
        vt = FUENTE_PEQUENA.render(f"Vel: {velocidad}x", True, COLOR_EXITO)
        vr = vt.get_rect(right=tiempo_rect.right - 10, bottom=tiempo_rect.bottom - 5)
        pantalla.blit(vt, vr)

    # Inicializar variables para el layout
    tiempo_rect = None
    info_rect = None
    mapa = None
    botones_control = []
    menu_construccion = None
    menus_desplegables = []
    
    actualizar_layout()

    if mapa and mapa.mapa_terreno:
        if not simulador.generar_zonas_aleatorias(mapa.mapa_terreno):
            print("Error generando zonas.")
            ejecutando = False
    else:
        print("Error: Mapa no disponible.")
        ejecutando = False

    # Loop principal del juego
    while ejecutando:
        mouse_pos = pygame.mouse.get_pos()
        eventos = pygame.event.get()
        
        for ev in eventos:
            if ev.type == pygame.QUIT:
                ejecutando = False
            
            if ev.type == pygame.VIDEORESIZE:
                ancho_ventana = ev.w
                alto_ventana = ev.h
                actualizar_layout()
            
            if ev.type == pygame.MOUSEWHEEL:
                if info_rect.collidepoint(mouse_pos):
                    if ev.y > 0:
                        colono_scroll_offset = max(0, colono_scroll_offset - 1)
                    elif ev.y < 0:
                        tc = len([c for c in simulador.colonos if c.salud > 0])
                        mo = max(0, tc - lineas_visibles_colonos)
                        colono_scroll_offset = min(mo, colono_scroll_offset + 1)
                    continue
                elif mapa and mapa.manejar_evento(ev, mouse_pos):
                    continue
            
            if ev.type == pygame.KEYDOWN:
                if mapa and mapa.manejar_teclado(ev.key):
                    continue
            
            ev_widget = False
            for btn in botones_control:
                if btn.manejar_evento(ev, mouse_pos):
                    ev_widget = True
                    break
            
            if ev_widget:
                continue
            
            for heal_btn in list(heal_buttons.values()):
                if heal_btn.manejar_evento(ev, mouse_pos):
                    ev_widget = True
                    break
            
            if ev_widget:
                continue
            
            if menu_construccion and menu_construccion.manejar_evento(ev, mouse_pos):
                ev_widget = True
                continue
            
            for menu in menus_desplegables:
                if menu.manejar_evento(ev, mouse_pos):
                    ev_widget = True
                    break
            
            if ev_widget:
                continue

        res_ciclo = None
        if simulacion_activa:
            contador_frames += 1
            if contador_frames >= frames_por_ciclo:
                res_ciclo = ejecutar_ciclo()
                contador_frames = 0
                
                if isinstance(res_ciclo, dict) and ("construccion" in res_ciclo or "descubrimiento" in res_ciclo):
                    actualizar_menu_construccion()

        current_time = pygame.time.get_ticks()
        active_meteors = [m for m in active_meteors if m.update(current_time)]

        shake_offset_x = 0
        shake_offset_y = 0
        
        if shake_active:
            time_elapsed = current_time - shake_start_time

            if time_elapsed < shake_duration:
                shake_offset_x = random.randint(-shake_magnitude, shake_magnitude)
                shake_offset_y = random.randint(-shake_magnitude, shake_magnitude)
            else:
                shake_active = False

        if cold_effect_active:
            if simulador.ciclo > cold_effect_end_cycle:
                cold_effect_active = False
            elif snowflake_image and mapa and random.random() < 0.25:
                active_snowflakes.append(Snowflake(snowflake_image, mapa.rect))

        active_snowflakes = [s for s in active_snowflakes if s.update(current_time)]
        active_rockets = [r for r in active_rockets if r.update()]
        active_lightning = [l for l in active_lightning if not l.update()]
        active_artifacts = [a for a in active_artifacts if not a.update()]

        notificaciones.actualizar()
        pantalla.fill(COLOR_FONDO)

        if mapa:
            original_offset_x = mapa.offset_x
            original_offset_y = mapa.offset_y

            if shake_active:
                mapa.offset_x += shake_offset_x
                mapa.offset_y += shake_offset_y

            mapa.dibujar(pantalla, simulador.colonos, simulador.hora, 
                        simulador.zonas, simulador.sitios_construccion)

            if shake_active:
                mapa.offset_x = original_offset_x
                mapa.offset_y = original_offset_y

            if cold_effect_active:
                cold_filter = pygame.Surface(mapa.rect.size, pygame.SRCALPHA)
                cold_filter.fill((170, 200, 255, 60))
                pantalla.blit(cold_filter, mapa.rect.topleft)

            for flake in active_snowflakes:
                flake.draw(pantalla)

        for rocket in active_rockets:
            rocket.draw(pantalla)

        for meteor in active_meteors:
            meteor.draw(pantalla)
        
        for bolt in active_lightning:
            bolt.draw(pantalla)
        
        for artifact in active_artifacts:
            artifact.draw(pantalla)

        dibujar_panel_lateral()
        dibujar_info_colonos()
        dibujar_recursos()
        dibujar_cola_prioridad()

        for btn in botones_control:
            btn.dibujar(pantalla)
        
        if menu_construccion:
            menu_construccion.dibujar(pantalla)
        
        for menu in menus_desplegables:
            menu.dibujar(pantalla)

        notificaciones.dibujar(pantalla)

        pygame.display.flip()
        reloj.tick(60)

    pygame.quit()
    sys.exit()


# Mantener compatibilidad con código antiguo
class PanelControl:
    def __init__(self):
        pass
    
    def ejecutar(self):
        ejecutar_juego()
