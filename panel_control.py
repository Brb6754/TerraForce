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

        map_width = screen_rect.width
        map_height = screen_rect.height

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

class PanelControl:
    def __init__(self):
        pygame.init()
        self.ancho_ventana, self.alto_ventana = 1200, 700
        try:
            self.pantalla = pygame.display.set_mode((self.ancho_ventana, self.alto_ventana), pygame.RESIZABLE)
            pygame.display.set_caption("Colonia Epsilon-3 - Mapa Procedural")
        except pygame.error as e:
            print(f"Error display: {e}")
            sys.exit()

        self.reloj = pygame.time.Clock()
        self.ejecutando = True
        self.notificaciones = SistemaNotificaciones(0, 0)

        self.active_meteors = []
        self.active_snowflakes = []
        self.active_rockets = []
        self.active_artifacts = []

        self.simulador = Simulador(
            callback_log=self.notificaciones.agregar,
            callback_visual=self.handle_visual_event
        )

        self.colono_scroll_offset = 0
        self.altura_linea_colono = 42
        self.lineas_visibles_colonos = 1
        self.heal_buttons = {}

        self.simulacion_activa = True
        self.velocidad = 1
        self.frames_por_ciclo = 60
        self.contador_frames = 0

        self.meteor_image = None
        try:
            original_meteor = pygame.image.load("Assets/Meteorito.png").convert_alpha()
            self.meteor_image = pygame.transform.scale(original_meteor, (100, 100))
        except pygame.error as e:
            print(f"Error cargando Meteorito.png: {e}")
            self.meteor_image = None

        self.snowflake_image = None
        try:
            original_snow = pygame.image.load("Assets/copo.png").convert_alpha()
            self.snowflake_image = pygame.transform.scale(original_snow, (20, 20))
        except pygame.error as e:
            print(f"Error cargando copo.png: {e}")
            self.snowflake_image = None

        self.rocket_image = None
        try:
            original_rocket = pygame.image.load("Assets/cohete.png").convert_alpha()
            self.rocket_image = pygame.transform.scale(original_rocket, (500, 500))
        except pygame.error as e:
            print(f"Error cargando cohete.png: {e}")
            self.rocket_image = None

        self.artifact_images = []
        artifact_files = ["Assets/2.png",
                          "Assets/3.png",
                          "Assets/4.png"]
        for file in artifact_files:
            try:
                original_artifact = pygame.image.load(file).convert_alpha()
                scaled_artifact = pygame.transform.scale(original_artifact, (300, 300))
                self.artifact_images.append(scaled_artifact)
                print(f"{file} cargado")
            except pygame.error as e:
                print(f"Error cargando {file}: {e}")

        self.shake_active = False
        self.shake_duration = 0
        self.shake_start_time = 0
        self.shake_magnitude = 5

        self.cold_effect_active = False
        self.cold_effect_end_cycle = 0

        self.actualizar_layout()

        if hasattr(self, 'mapa') and self.mapa.mapa_terreno:
            if not self.simulador.generar_zonas_aleatorias(self.mapa.mapa_terreno):
                print("Error generando zonas.")
                self.ejecutando = False
        else:
            print("Error: Mapa no disponible.")
            self.ejecutando = False

        self.lightning_image = None
        self.active_meteors = []
        self.active_lightning = []

        try:
            original_lightning = pygame.image.load("Assets/rayo.png").convert_alpha()
            self.lightning_image = pygame.transform.scale(original_lightning, (500, 500))
            print("rayo.png cargado correctamente.")
        except pygame.error as e:
            print(f"Error cargando rayo.png: {e}")
            self.lightning_image = None

    def handle_visual_event(self, event_type):
        if event_type == "meteor_shower" and self.meteor_image and hasattr(self, 'mapa'):
            num_meteors = random.randint(5, 8)
            for _ in range(num_meteors):
                self.active_meteors.append(Meteor(self.meteor_image, self.mapa.rect))
            print(f"Visual event: Triggered {num_meteors} meteors.")

        elif event_type == "earthquake":
            self.shake_active = True
            self.shake_duration = 1200
            self.shake_start_time = pygame.time.get_ticks()
            print(f"Visual event: Triggered earthquake shake.")

        elif event_type == "temp_drop":
            if self.snowflake_image and hasattr(self, 'mapa'):
                self.cold_effect_active = True
                self.cold_effect_end_cycle = self.simulador.ciclo + 3
                print(f"Visual event: Triggered temp drop. Ends on cycle {self.cold_effect_end_cycle}.")

        elif event_type == "new_colonists" and self.rocket_image:
            print("Visual event: Triggered new rocket arrival.")
            self.active_rockets.append(Rocket(self.rocket_image,(self.ancho_ventana, self.alto_ventana)))

        elif event_type == "electromagnetic_storm" and self.lightning_image:
            for i in range(3):
                self.active_lightning.append(LightningBolt(self.lightning_image,
                                                             (self.ancho_ventana, self.alto_ventana),
                                                             self.mapa.rect))
            print(f"Visual event: Triggered 3 lightning bolts for storm.")

        elif event_type == "artifact_discovery" and self.artifact_images and hasattr(self, 'mapa'):
            if not self.active_artifacts:
                chosen_image = random.choice(self.artifact_images)
                new_artifact = ArtifactDisplay(chosen_image, self.mapa.rect)
                self.active_artifacts.append(new_artifact)
                print(f"Visual event: Triggered artifact discovery.")


    def actualizar_botones(self):
        panel_ancho=max(250,min(350,int(self.ancho_ventana*0.25))); ancho_cont=panel_ancho-40; y_inicio=20
        self.botones_control=[Boton(20,y_inicio,ancho_cont,40,"PAUSAR" if self.simulacion_activa else "REANUDAR",self.toggle_pausa,COLOR_ADVERTENCIA if self.simulacion_activa else COLOR_EXITO), Boton(20+(ancho_cont-10)//3+5,y_inicio+50,(ancho_cont-10)//3,35,"2x",lambda: self.cambiar_velocidad(2),COLOR_BOTON if self.velocidad!=2 else COLOR_EXITO), Boton(20,y_inicio+50,(ancho_cont-10)//3,35,"1x",lambda: self.cambiar_velocidad(1),COLOR_BOTON if self.velocidad!=1 else COLOR_EXITO), Boton(20+2*((ancho_cont-10)//3)+10,y_inicio+50,(ancho_cont-10)//3,35,"3x",lambda: self.cambiar_velocidad(3),COLOR_BOTON if self.velocidad!=3 else COLOR_EXITO)]
        y_constr=y_inicio+95
        if not hasattr(self,'menu_construccion'): self.menu_construccion=BotonDesplegable(20,y_constr,ancho_cont,35,"CONSTRUIR",[],(80,180,80))
        else: self.menu_construccion.rect.topleft=(20,y_constr); self.menu_construccion.rect.width=ancho_cont
        self.actualizar_menu_construccion()
        menu_y=25; menu_ancho=150; menu_espacio=10; num_menus=4; x_start=self.ancho_ventana-(num_menus*(menu_ancho+menu_espacio))+menu_espacio-10
        menu_data=[("MANTENIMIENTO",[("Rep. Lab","reparar_laboratorio","Rep. lab",(50,100,180)),("Rep. Hab","reparar_habitat","Rep. hab",(50,120,180)),("+ Energía","generar_energia","Reactor",(200,150,50))],(30,60,120)), ("RECURSOS",[("+ Comida","recolectar_alimentos","Cosecha",(50,180,50)),("Cultivar","cultivar","Cultivo",(80,180,50)),("+ Material","recolectar_recursos","Minería",(150,100,50))],(40,120,40)), ("EXPLORACIÓN",[("Expl. Terreno","explorar_terreno","Recon.",(255,200,100)),("Expl. Caverna","explorar_cavernas","Caverna",(200,150,80)),("Cartografiar","cartografiar","Mapeo",(180,130,60))],(180,120,40))]
        self.menus_desplegables=[]; cur_x=x_start
        for tit, tareas_info, col in menu_data:
             tareas=[(txt, lambda t=tipo, d=desc: self.agregar_tarea(t,d), tcol) for txt, tipo, desc, tcol in tareas_info]
             menu=BotonDesplegable(cur_x,menu_y,menu_ancho,40,tit,tareas,col); self.menus_desplegables.append(menu); cur_x+=menu_ancho+menu_espacio

    def actualizar_layout(self):
        self.ancho_ventana=max(1000,self.ancho_ventana); self.alto_ventana=max(600,self.alto_ventana)
        try: self.pantalla=pygame.display.set_mode((self.ancho_ventana,self.alto_ventana),pygame.RESIZABLE)
        except pygame.error as e: print(f"Error resize: {e}"); return
        panel_ancho=max(250,min(350,int(self.ancho_ventana*0.25))); ancho_cont=panel_ancho-40
        tiempo_y=150; self.tiempo_rect=pygame.Rect(20,tiempo_y,ancho_cont,85)
        info_y=self.tiempo_rect.bottom+10; info_alto=self.alto_ventana-info_y-20; self.info_rect=pygame.Rect(20,info_y,ancho_cont,info_alto)
        header_h=40
        if self.altura_linea_colono>0: self.lineas_visibles_colonos=max(1,(info_alto-header_h)//self.altura_linea_colono)
        else: self.lineas_visibles_colonos=1
        mapa_x=panel_ancho; mapa_ancho=self.ancho_ventana-mapa_x-20; mapa_alto=self.alto_ventana-40; mapa_y=20
        if hasattr(self,'mapa') and self.mapa: self.mapa.rect.topleft=(mapa_x,mapa_y); self.mapa.rect.size=(mapa_ancho,mapa_alto); self.mapa.calcular_tile_size()
        else: self.mapa=Mapa(mapa_x,mapa_y,mapa_ancho,mapa_alto)
        if hasattr(self.mapa, 'mapa_terreno') and self.mapa.mapa_terreno:
            self.mapa.arbol_manager.generar_arboles(
                self.mapa.mapa_terreno,
                self.mapa.ancho_mapa,
                self.mapa.alto_mapa
            )
            print("Árboles generados en el mapa")
        if hasattr(self,'mapa') and self.mapa:
            pad=10; rec_alto=190
            nx=self.mapa.rect.left+pad; ny=self.mapa.rect.top+pad+rec_alto+pad + 10
            if hasattr(self,'notificaciones'): self.notificaciones.x=nx; self.notificaciones.y=ny
        self.actualizar_botones()

    def actualizar_menu_construccion(self):
        opciones=[]
        if hasattr(self,'simulador') and self.simulador:
             try: items=sorted(self.simulador.sitios_construccion.items())
             except AttributeError: items=[]
             for sid, datos in items:
                 if datos and not datos.get("en_progreso",True): txt=f"{datos.get('tipo_nuevo','?')} ({datos.get('costo','?')})"; cb=lambda s=sid: self.simulador.iniciar_construccion(s); opciones.append((txt,cb,(80,180,80)))
        if hasattr(self,'menu_construccion'):
            self.menu_construccion.tareas=opciones
            if hasattr(self.menu_construccion,'rect'): self.menu_construccion.crear_botones(10,140,200)


    def agregar_tarea(self, tipo, descripcion): self.simulador.agregar_tarea_personalizada(tipo, descripcion)
    def toggle_pausa(self): self.simulacion_activa = not self.simulacion_activa; self.actualizar_botones()
    def cambiar_velocidad(self, v): self.velocidad=v; self.frames_por_ciclo={1:45,2:22,3:10,4:5}.get(v,45); self.actualizar_botones()

    def ejecutar_ciclo(self):
        res=self.simulador.ejecutar_ciclo()
        if isinstance(res, dict) and ("construccion" in res or "descubrimiento" in res): self.actualizar_menu_construccion()
        return res

    def _curar_colono(self, cid):
        costo_alimentos = 15
        costo_energia = 10
        costo_materiales = 20

        if (self.simulador.recursos["alimentos"] < costo_alimentos or
            self.simulador.recursos["energia"] < costo_energia or
            self.simulador.recursos["materiales"] < costo_materiales):

            faltantes = []
            if self.simulador.recursos["alimentos"] < costo_alimentos:
                faltantes.append(f"{costo_alimentos}")
            if self.simulador.recursos["energia"] < costo_energia:
                faltantes.append(f"{costo_energia}")
            if self.simulador.recursos["materiales"] < costo_materiales:
                faltantes.append(f"{costo_materiales}")

            self.notificaciones.agregar(
                f"Curación: Faltan {', '.join(faltantes)}",
                "peligro",
                3000
            )
            return

        c = next((co for co in self.simulador.colonos if co.id == cid), None)

        if c and c.salud < 100:
            self.simulador.recursos["alimentos"] -= costo_alimentos
            self.simulador.recursos["energia"] -= costo_energia
            self.simulador.recursos["materiales"] -= costo_materiales

            cura = random.randint(25, 50)
            sa = c.salud
            c.curar(cura)
            cr = c.salud - sa

            self.simulador.log(
                f"Curado {c.nombre}(+{cr}). Salud:{c.salud}%. Recursos: -{costo_alimentos} -{costo_energia} -{costo_materiales}",
                "exito"
            )
            self.notificaciones.agregar(
                f"{c.nombre} +{cr}HP (-{costo_alimentos} -{costo_energia} -{costo_materiales})",
                "exito",
                3000
            )
        elif c:
            self.notificaciones.agregar(f"{c.nombre} ya está sano", "info", 2000)

    def dibujar_info_colonos(self):
        pygame.draw.rect(self.pantalla,COLOR_PANEL,self.info_rect,border_radius=8); pygame.draw.rect(self.pantalla,COLOR_BORDE,self.info_rect,2,border_radius=8)
        tit_txt="ESTADO COLONOS"; tit_rend=FUENTE_NORMAL.render(tit_txt,True,COLOR_ADVERTENCIA); tit_rect=tit_rend.get_rect(left=self.info_rect.x+10,top=self.info_rect.y+10); self.pantalla.blit(tit_rend,tit_rect)
        cvl=[c for c in self.simulador.colonos if c.salud>0]; nv=len(cvl); np=self.simulador.colonos_perdidos
        cnt_txt=f"(V:{nv}/P:{np})"; cnt_rend=FUENTE_PEQUENA.render(cnt_txt,True,COLOR_TEXTO_SECUNDARIO); cnt_rect=cnt_rend.get_rect(left=tit_rect.right+10,centery=tit_rect.centery)
        if cnt_rect.right > self.info_rect.right-10: cnt_rect.right=self.info_rect.right-10
        self.pantalla.blit(cnt_rend,cnt_rect); pygame.draw.line(self.pantalla,COLOR_BORDE,(self.info_rect.x+10,self.info_rect.y+35),(self.info_rect.right-10,self.info_rect.y+35),1)
        cvl.sort(key=lambda c: c.edad); tc=nv; y_col=self.info_rect.y+45; alt_lin=self.altura_linea_colono
        max_off=max(0,tc-self.lineas_visibles_colonos); self.colono_scroll_offset=max(0,min(self.colono_scroll_offset,max_off))
        c_mostrar=cvl[self.colono_scroll_offset:self.colono_scroll_offset+self.lineas_visibles_colonos]; vis_ids=set()

        for c in c_mostrar:
            vis_ids.add(c.id); btn_w=50; btn_h=18; btn_x=self.info_rect.right-btn_w-5; btn_y=y_col
            hb=self.heal_buttons.get(c.id)
            if hb is None or hb.rect.topleft!=(btn_x,btn_y): hb=Boton(btn_x,btn_y,btn_w,btn_h,"Curar",lambda cid=c.id:self._curar_colono(cid),COLOR_EXITO); self.heal_buttons[c.id]=hb
            if c.salud<100: hb.dibujar(self.pantalla)

            nom=f"{c.nombre[:8]}({c.tipo[:3]},{c.edad})"; txt=FUENTE_PEQUENA.render(nom,True,COLOR_TEXTO); max_nx=btn_x-10
            if txt.get_width() > max_nx-(self.info_rect.x+15): ratio=(max_nx-(self.info_rect.x+15))/txt.get_width(); cv=max(5,int(len(nom)*ratio)-2); nom=nom[:cv]+".."; txt=FUENTE_PEQUENA.render(nom,True,COLOR_TEXTO)
            self.pantalla.blit(txt,(self.info_rect.x+15,y_col))

            bar_y=y_col+22; bar_wt=self.info_rect.width-30; bar_wi=(bar_wt-10)//2; bar_h=8; bar_sx=self.info_rect.x+15
            pygame.draw.rect(self.pantalla,(30,30,40),(bar_sx,bar_y,bar_wi,bar_h),border_radius=3)
            sw=int((c.salud/100)*bar_wi); scol=COLOR_EXITO if c.salud>60 else(COLOR_ADVERTENCIA if c.salud>30 else COLOR_PELIGRO)
            pygame.draw.rect(self.pantalla,scol,(bar_sx,bar_y,sw,bar_h),border_radius=3)

            if c.lifestage=="Adulto" and c.ocupado and c.accion_actual and c.accion_actual.duracion>0:
                acc=c.accion_actual

                tarea_desc = str(acc.descripcion).split(':')[0].strip()[:10]
                if acc.zona_id:
                    tarea_desc = f"{tarea_desc} @ {acc.zona_id[:3]}"

                tarea_rend = FUENTE_PEQUENA.render(f"Tarea: {tarea_desc}", True, COLOR_TEXTO_SECUNDARIO)
                self.pantalla.blit(tarea_rend, (bar_sx + bar_wi + 10, y_col))

                prog=0
                if acc.duracion>0: prog=c.progreso_accion/acc.duracion
                prog=min(1.0,max(0.0,prog)); bar_px=bar_sx+bar_wi+10
                pygame.draw.rect(self.pantalla,(40,40,30),(bar_px,bar_y,bar_wi,bar_h),border_radius=3)
                pygame.draw.rect(self.pantalla,COLOR_ADVERTENCIA,(bar_px,bar_y,int(bar_wi*prog),bar_h),border_radius=3)

            y_col+=alt_lin

        ids_borrar=set(self.heal_buttons.keys())-vis_ids
        for cid in ids_borrar: del self.heal_buttons[cid]
        if tc>self.lineas_visibles_colonos:
            scr_h=self.info_rect.height-40; scr_x=self.info_rect.right+5; scr_y=self.info_rect.y+35
            ind_h=max(15,int(scr_h*(self.lineas_visibles_colonos/tc))); ind_y=scr_y; scroll_range=tc-self.lineas_visibles_colonos
            if scroll_range>0: ind_y+=int((scr_h-ind_h)*(self.colono_scroll_offset/scroll_range))
            pygame.draw.rect(self.pantalla,(30,30,40),(scr_x,scr_y,8,scr_h),border_radius=4); pygame.draw.rect(self.pantalla,COLOR_BORDE,(scr_x,ind_y,8,ind_h),border_radius=4)

    def _dibujar_barra_recurso(self, superficie, y, etiqueta, valor, valor_max, color):
        texto_val=f"{valor}/{valor_max}"; texto=FUENTE_PEQUENA.render(f"{etiqueta}: {texto_val}",True,COLOR_TEXTO); superficie.blit(texto,(15,y))
        bx=15; by=y+18; bw=superficie.get_width()-30; bh=10
        pygame.draw.rect(superficie,(30,30,40,200),(bx,by,bw,bh),border_radius=3); porc=0
        if valor_max>0: porc=min(1.0,valor/valor_max)
        vw=int(porc*bw); col_fin=color; umbral=0.3*valor_max
        if valor<=umbral: col_fin=COLOR_PELIGRO;
        elif valor<=umbral*2: col_fin=COLOR_ADVERTENCIA;
        col_alpha=(*col_fin[:3],220); pygame.draw.rect(superficie,col_alpha,(bx,by,vw,bh),border_radius=3)


    def dibujar_recursos(self):
        pan_w=200; pan_h=190; pad=10;
        if not hasattr(self,'mapa'): return
        x=self.mapa.rect.left+pad; y=self.mapa.rect.top+pad
        try: sf=pygame.Surface((pan_w,pan_h),pygame.SRCALPHA)
        except pygame.error: sf=pygame.Surface((pan_w,pan_h)); sf.set_alpha(220)
        cf=(*COLOR_PANEL[:3],180); pygame.draw.rect(sf,cf,(0,0,pan_w,pan_h),border_radius=8)
        cb=(*COLOR_BORDE[:3],200); pygame.draw.rect(sf,cb,(0,0,pan_w,pan_h),2,border_radius=8)

        try:
            conteo = self.simulador.get_conteo_estructuras()
        except AttributeError:
            conteo = {"laboratorio": 0, "habitat": 0, "cultivos": 0}

        rec=self.simulador.recursos; slab=self.simulador.salud_laboratorio; shab=self.simulador.salud_habitat; max_s=self.simulador.MAX_SALUD_ESTRUCTURA; max_r=200

        y_ini=10; esp=30

        self._dibujar_barra_recurso(sf,y_ini,"Alim",rec.get("alimentos",0),max_r,COLOR_EXITO)
        self._dibujar_barra_recurso(sf,y_ini+esp,"Energ",rec.get("energia",0),max_r,COLOR_ADVERTENCIA)
        self._dibujar_barra_recurso(sf,y_ini+2*esp,"Mater",rec.get("materiales",0),max_r,(150,150,150))

        lab_label = f"Lab (x{conteo.get('laboratorio', 0)})"
        hab_label = f"Hab (x{conteo.get('habitat', 0)})"

        self._dibujar_barra_recurso(sf,y_ini+3*esp, lab_label, slab,max_s,(100,150,255))
        self._dibujar_barra_recurso(sf,y_ini+4*esp, hab_label, shab,max_s,(200,180,255))

        cult_label = f"Cultivos: x{conteo.get('cultivos', 0)}"
        cult_texto = FUENTE_PEQUENA.render(cult_label, True, COLOR_TEXTO)
        sf.blit(cult_texto, (15, y_ini + 5 * esp + 5))

        self.pantalla.blit(sf,(x,y))


    def dibujar_cola_prioridad(self):
        pan_w=280; pan_h=220; pad=10
        if not hasattr(self,'mapa'): return
        x=self.mapa.rect.right-pan_w-pad; y=self.mapa.rect.bottom-pan_h-pad; pr=pygame.Rect(x,y,pan_w,pan_h)
        try: sf=pygame.Surface((pan_w,pan_h),pygame.SRCALPHA)
        except pygame.error: sf=pygame.Surface((pan_w,pan_h)); sf.set_alpha(220)
        cf=(*COLOR_PANEL[:3],220); pygame.draw.rect(sf,cf,(0,0,pan_w,pan_h),border_radius=8)
        cb=(*COLOR_BORDE[:3],255); pygame.draw.rect(sf,cb,(0,0,pan_w,pan_h),2,border_radius=8)
        tit=FUENTE_NORMAL.render("COLA DE TAREAS",True,COLOR_ADVERTENCIA); sf.blit(tit,(10,10))
        pygame.draw.line(sf,cb,(10,35),(pan_w-10,35),1)
        try: tareas=sorted(self.simulador.heap_prioridades.heap,key=lambda i:i[0])
        except Exception as e: tareas=[]; print(f"Err heap sort: {e}")
        yt=45; lh=20; lv=max(1,(pr.height-55)//lh)
        for i,(prio,acc) in enumerate(tareas[:lv]):
            try:
                txt=str(acc); rend=FUENTE_PEQUENA.render(txt,True,COLOR_TEXTO); tw=rend.get_width(); max_w=pr.width-20
                if tw > max_w:
                    nc = len(txt); ce = 0
                    if tw > 0: ce = int(nc * (max_w / tw)) - 3
                    if ce > 0: txt=txt[:ce]+".."; rend=FUENTE_PEQUENA.render(txt,True,COLOR_TEXTO)
                sf.blit(rend,(15,yt)); yt+=lh
            except Exception as e: print(f"Err draw task: {e},{acc}")
        self.pantalla.blit(sf,(x,y))


    def dibujar_panel_lateral(self):
        pan_w_tot=max(250,min(350,int(self.ancho_ventana*0.25)))
        pan_rect_f=pygame.Rect(10,10,pan_w_tot-20,self.alto_ventana-20)
        pygame.draw.rect(self.pantalla,COLOR_PANEL,pan_rect_f,border_radius=8)
        pygame.draw.rect(self.pantalla,COLOR_BORDE,pan_rect_f,2,border_radius=8)
        if hasattr(self,'tiempo_rect'):
            pygame.draw.rect(self.pantalla,(20,20,35),self.tiempo_rect,border_radius=6)
            pygame.draw.rect(self.pantalla,COLOR_BORDE,self.tiempo_rect,1,border_radius=6)
            ft=FUENTE_PEQUENA.render(self.simulador.obtener_fecha_formateada(),True,COLOR_TEXTO); self.pantalla.blit(ft,(self.tiempo_rect.x+10,self.tiempo_rect.y+8))
            ht=FUENTE_TITULO.render(self.simulador.obtener_hora_formateada(),True,COLOR_ADVERTENCIA); self.pantalla.blit(ht,(self.tiempo_rect.x+10,self.tiempo_rect.y+30))
            pt=FUENTE_PEQUENA.render(self.simulador.obtener_periodo_dia(),True,COLOR_TEXTO_SECUNDARIO); self.pantalla.blit(pt,(self.tiempo_rect.x+10,self.tiempo_rect.y+65))
            vt=FUENTE_PEQUENA.render(f"Vel: {self.velocidad}x",True,COLOR_EXITO); vr=vt.get_rect(right=self.tiempo_rect.right-10,bottom=self.tiempo_rect.bottom-5); self.pantalla.blit(vt,vr)


    def ejecutar(self):
        while self.ejecutando:
            mouse_pos = pygame.mouse.get_pos(); eventos = pygame.event.get()
            for ev in eventos:
                if ev.type==pygame.QUIT: self.ejecutando=False
                if ev.type==pygame.VIDEORESIZE: self.ancho_ventana=ev.w; self.alto_ventana=ev.h; self.actualizar_layout()
                if ev.type==pygame.MOUSEWHEEL:
                    if self.info_rect.collidepoint(mouse_pos):
                        if ev.y>0: self.colono_scroll_offset=max(0,self.colono_scroll_offset-1)
                        elif ev.y<0: tc=len([c for c in self.simulador.colonos if c.salud>0]); mo=max(0,tc-self.lineas_visibles_colonos); self.colono_scroll_offset=min(mo,self.colono_scroll_offset+1)
                        continue
                    elif hasattr(self,'mapa') and self.mapa.manejar_evento(ev,mouse_pos): continue
                if ev.type==pygame.KEYDOWN:
                    if hasattr(self,'mapa') and self.mapa.manejar_teclado(ev.key): continue
                ev_widget=False
                for btn in self.botones_control:
                    if btn.manejar_evento(ev,mouse_pos): ev_widget=True; break
                if ev_widget: continue
                for heal_btn in list(self.heal_buttons.values()):
                    if heal_btn.manejar_evento(ev,mouse_pos): ev_widget=True; break
                if ev_widget: continue
                if hasattr(self,'menu_construccion') and self.menu_construccion.manejar_evento(ev,mouse_pos): ev_widget=True; continue
                for menu in self.menus_desplegables:
                    if menu.manejar_evento(ev,mouse_pos): ev_widget=True; break
                if ev_widget: continue

            res_ciclo = None
            if self.simulacion_activa:
                self.contador_frames+=1
                if self.contador_frames>=self.frames_por_ciclo:
                    res_ciclo=self.ejecutar_ciclo(); self.contador_frames=0
                    if isinstance(res_ciclo, dict) and ("construccion" in res_ciclo or "descubrimiento" in res_ciclo):
                          self.actualizar_menu_construccion()

            current_time = pygame.time.get_ticks()
            self.active_meteors = [m for m in self.active_meteors if m.update(current_time)]

            shake_offset_x = 0
            shake_offset_y = 0
            if self.shake_active:
                time_elapsed = current_time - self.shake_start_time

                if time_elapsed < self.shake_duration:
                    shake_offset_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
                    shake_offset_y = random.randint(-self.shake_magnitude, self.shake_magnitude)
                else:
                    self.shake_active = False

            if self.cold_effect_active:
                if self.simulador.ciclo > self.cold_effect_end_cycle:
                    self.cold_effect_active = False

                elif self.snowflake_image and hasattr(self, 'mapa') and random.random() < 0.25:
                    self.active_snowflakes.append(Snowflake(self.snowflake_image, self.mapa.rect))

            self.active_snowflakes = [s for s in self.active_snowflakes if s.update(current_time)]

            self.active_rockets = [r for r in self.active_rockets if r.update()]


            self.notificaciones.actualizar(); self.pantalla.fill(COLOR_FONDO)


            self.active_lightning = [l for l in self.active_lightning if not l.update()]

            self.active_artifacts = [a for a in self.active_artifacts if not a.update()]

            if hasattr(self,'mapa'):

                original_offset_x = self.mapa.offset_x
                original_offset_y = self.mapa.offset_y

                if self.shake_active:
                    self.mapa.offset_x += shake_offset_x
                    self.mapa.offset_y += shake_offset_y

                self.mapa.dibujar(self.pantalla,self.simulador.colonos,self.simulador.hora,self.simulador.zonas,self.simulador.sitios_construccion)

                if self.shake_active:
                    self.mapa.offset_x = original_offset_x
                    self.mapa.offset_y = original_offset_y

                if self.cold_effect_active:
                    cold_filter = pygame.Surface(self.mapa.rect.size, pygame.SRCALPHA)
                    cold_filter.fill((170, 200, 255, 60))
                    self.pantalla.blit(cold_filter, self.mapa.rect.topleft)

                for flake in self.active_snowflakes:
                    flake.draw(self.pantalla)

            for rocket in self.active_rockets:
                rocket.draw(self.pantalla)

            for meteor in self.active_meteors:
                meteor.draw(self.pantalla)
            for bolt in self.active_lightning:
                bolt.draw(self.pantalla)
            for artifact in self.active_artifacts:
                artifact.draw(self.pantalla)

            self.dibujar_panel_lateral()
            self.dibujar_info_colonos()

            self.dibujar_recursos()
            self.dibujar_cola_prioridad()

            for btn in self.botones_control: btn.dibujar(self.pantalla)
            if hasattr(self,'menu_construccion'): self.menu_construccion.dibujar(self.pantalla)
            for menu in self.menus_desplegables: menu.dibujar(self.pantalla)

            self.notificaciones.dibujar(self.pantalla)

            pygame.display.flip(); self.reloj.tick(60)

        pygame.quit(); sys.exit()
if __name__ == "__main__":
    panel = PanelControl()
    panel.ejecutar()