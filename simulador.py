import random
import pygame
import math
from collections import deque
from datetime import datetime
from estructuras import ListaEnlazada, Queue, MonticuloMinimo
from colonos import Colono, Ingeniero, Biologo, Explorador, Guardia
from acciones import Accion
from acciones import MINUTES_PER_CYCLE

class GeneradorEventos:
    EVENTOS = [
        {"nombre": "Lluvia de Meteoritos", "probabilidad": 0.1, "acciones": [], "dano_colonos": 15, "dano_structura": {"lab": 20, "hab": 15}, "mensaje": "Lluvia de meteoritos detectada! Dano estructural."},
        {"nombre": "Tormenta Electromagnetica", "probabilidad": 0.1, "acciones": [], "dano_colonos": 5, "dano_structura": {"lab": 10}, "mensaje": "Tormenta electromagnetica afecta sistemas."},
        {"nombre": "Llegada de Nuevos Colonos", "probabilidad": 0.1, "acciones": [], "dano_colonos": 0, "dano_structura": {}, "mensaje": "Capsula de colonos detectada!"},
        {"nombre": "Plaga en Cultivos", "probabilidad": 0.12, "acciones": [], "dano_colonos": 5, "dano_structura": {}, "mensaje": "Plaga detectada en los cultivos."},
        {"nombre": "Actividad Sismica", "probabilidad": 0.10, "acciones": [], "dano_colonos": 10, "dano_structura": {"hab": 25}, "mensaje": "Actividad sismica detectada."},
        {"nombre": "Caida de Temperatura", "probabilidad": 0.15, "acciones": [], "dano_colonos": 8, "dano_structura": {}, "mensaje": "Temperatura descendiendo peligrosamente."},
        {"nombre": "Descubrimiento de Artefacto Alienigena", "probabilidad": 0.08, "acciones": [], "dano_colonos": 0, "dano_structura": {}, "mensaje": "Artefacto alienigena encontrado. Oportunidad de investigacion!"},
        {"nombre": "Incendio en el Habitat", "probabilidad": 0.10, "acciones": [], "dano_colonos": 12, "dano_structura": {"hab": 30}, "mensaje": "Incendio detectado en el habitat!"}
    ]

    @staticmethod
    def generar_evento():
        if random.random() < 0.35:
            evento = random.choices(GeneradorEventos.EVENTOS, weights=[e["probabilidad"] for e in GeneradorEventos.EVENTOS])[0]
            return evento
        return None

class Simulador:
    def __init__(self, callback_log=None, callback_visual=None):
        self.ciclo = 0
        self.colonos = []
        self.cola_acciones = Queue()
        self.heap_prioridades = MonticuloMinimo()
        self.historial = ListaEnlazada()
        self.recursos = {"energia": 100, "alimentos": 100, "materiales": 100}
        self.salud_laboratorio = 100
        self.salud_habitat = 100
        self.MAX_SALUD_ESTRUCTURA = 100
        self.callback_log = callback_log
        self.callback_visual = callback_visual
        self.año, self.mes, self.dia = 2157, 3, 15
        self.hora, self.minuto = 8, 0
        self.dia_actual = 0
        self.dia_semana = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
        self.meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        self.dias_sobrevividos = 0
        self.eventos_totales = 0
        self.tareas_completadas = 0
        self.colonos_perdidos = 0
        self.acciones_rutinarias_generadas_hoy = {"7:00": False, "16:00": False}
        self.horario_trabajo_activo = True
        self.acciones_pausadas = []
        self.alertas_enviadas = set()
        self.ultimo_dia_notificado = -1
        self.ancho_mapa = 235
        self.alto_mapa = 150
        self.zonas = {}
        self.sitios_construccion = {}
        self.mapa_terreno = None

        self.mapa_tareas_zonas = {
            "defenderse": "perimetro_norte", "proteger_colonos": "base",
            "reparar_laboratorio": "base", "reparar_habitat": "base",
            "generar_energia": "reactor", "recolectar_alimentos": "cultivos",
            "cultivar": "cultivos", "explorar_terreno": "exploracion_ne",
            "recolectar_recursos": "exploracion_ne", "construir": "base",
            "investigar_flora": "cultivos", "cartografiar": "exploracion_ne",
            "explorar_cavernas": "exploracion_ne", "patrullar": "perimetro_norte",
            "curar": "base"
        }

        self.inicializar_colonia()

    def _encontrar_punto_inicio_zona(self, mapa_terreno, tipo_terreno, min_dist=0, max_dist=1000, evitar_zonas=True):
        intentos = 0
        max_intentos = 200
        if not mapa_terreno or not mapa_terreno[0]:
            self.log("Error: mapa_terreno vacio o invalido en _encontrar_punto_inicio_zona", "peligro")
            raise ValueError("mapa_terreno invalido")
        ancho_m, alto_m = len(mapa_terreno[0]), len(mapa_terreno)

        while intentos < max_intentos:
            intentos += 1
            x = random.randint(10, ancho_m - 11)
            y = random.randint(10, alto_m - 11)

            if not (0 <= y < alto_m and 0 <= x < ancho_m): continue

            if mapa_terreno[y][x] != tipo_terreno: continue

            if "base" in self.zonas:
                base_x, base_y, _, _ = self.zonas["base"]
                dist_base = math.hypot(x - base_x, y - base_y)
                if not (min_dist <= dist_base <= max_dist):
                    continue

            if evitar_zonas:
                muy_cerca = False
                for zid, (zx, zy, _, _) in self.zonas.items():
                    if zid != "base":
                        dist_otra = math.hypot(x - zx, y - zy)
                        if dist_otra < 15:
                            muy_cerca = True; break
                if muy_cerca: continue

            return (x, y)

        self.log(f"Advertencia: No se encontro punto ideal para zona {tipo_terreno}. Usando aleatorio.", "advertencia")
        return (random.randint(10, ancho_m - 11), random.randint(10, alto_m - 11))


    def _generar_zona_blob(self, mapa_terreno, centro_x, centro_y, color, tamano_max):
        zona_tiles = set()
        cola = deque([(centro_x, centro_y)])
        prob_expansion = 0.75
        while cola and len(zona_tiles) < tamano_max:
            cx, cy = cola.popleft()
            if (cx, cy) in zona_tiles: continue
            if not (0 <= cx < self.ancho_mapa and 0 <= cy < self.alto_mapa): continue
            zona_tiles.add((cx, cy))
            vecinos = [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]
            random.shuffle(vecinos)
            for nx, ny in vecinos:
                if (nx, ny) not in zona_tiles and random.random() < prob_expansion:
                    cola.append((nx, ny))
        return (centro_x, centro_y, color, list(zona_tiles))


    def generar_zonas_aleatorias(self, mapa_terreno):
        self.mapa_terreno = mapa_terreno
        try:
            base_x, base_y = self._encontrar_punto_inicio_zona(mapa_terreno, tipo_terreno='pasto', max_dist=self.ancho_mapa*0.3)
            self.zonas["base"] = self._generar_zona_blob(mapa_terreno, base_x, base_y, (200, 200, 255), 40)
            cult_x, cult_y = self._encontrar_punto_inicio_zona(mapa_terreno, 'pasto', min_dist=5, max_dist=25)
            self.zonas["cultivos"] = self._generar_zona_blob(mapa_terreno, cult_x, cult_y, (100, 255, 100), 30)
            react_x, react_y = self._encontrar_punto_inicio_zona(mapa_terreno, random.choice(['pasto','desierto']), min_dist=5, max_dist=20)
            self.zonas["reactor"] = self._generar_zona_blob(mapa_terreno, react_x, react_y, (255, 220, 100), 25)
            try: expl_x, expl_y = self._encontrar_punto_inicio_zona(mapa_terreno, 'montaña', min_dist=70)
            except ValueError:
                self.log("Advertencia: No montanas. Usando desierto para exploracion.", "advertencia")
                expl_x, expl_y = self._encontrar_punto_inicio_zona(mapa_terreno, 'desierto', min_dist=60)
            self.zonas["exploracion_ne"] = self._generar_zona_blob(mapa_terreno, expl_x, expl_y, (255, 150, 50), 50)
            perim_x = (base_x + expl_x) // 2; perim_y = (base_y + expl_y) // 2
            terreno_perim = mapa_terreno[perim_y][perim_x] if 0<=perim_y<self.alto_mapa and 0<=perim_x<self.ancho_mapa else 'pasto'
            px, py = self._encontrar_punto_inicio_zona(mapa_terreno, terreno_perim, min_dist=30, max_dist=60)
            self.zonas["perimetro_norte"] = self._generar_zona_blob(mapa_terreno, px, py, (255, 100, 100), 35)
            self.log("Zonas aleatorias generadas", "exito")
        except Exception as e:
            self.log(f"Error critico generando zonas: {e}", "peligro"); return False
        if "base" in self.zonas:
            base_x, base_y = self.zonas["base"][:2]
            for colono in self.colonos:
                colono.posicion = [float(base_x+random.randint(-5,5)), float(base_y+random.randint(-5,5))]
            self.log("Colonos desplegados en base", "exito")
        else:
            self.log("Error: No se genero 'base'. Colonos en centro.", "peligro")
            for colono in self.colonos: colono.posicion = [self.ancho_mapa/2.0, self.alto_mapa/2.0]
        self.generar_sitios_construccion(mapa_terreno); return True


    def notificar(self, mensaje, tipo="info", duracion=4000):
        if self.callback_log: self.callback_log(mensaje, tipo, duracion)

    def avanzar_tiempo(self):
        self.minuto += MINUTES_PER_CYCLE
        if self.minuto >= 60:
            self.minuto = 0; self.hora += 1
            if self.hora == 6: self.notificar("Buenos dias...", "info", 3000)
            elif self.hora == 12: self.notificar("Mediodia...", "info", 3000)
            elif self.hora == 18: self.notificar("Atardecer...", "advertencia", 3000)
            elif self.hora == 22: self.notificar("Noche...", "info", 3000)

            if self.hora >= 24:
                self.hora = 0; self.dia += 1
                self.dia_actual = (self.dia_actual + 1) % 7
                self.dias_sobrevividos += 1
                self.mantenimiento_envejecimiento()
                self.mantenimiento_reproduccion()
                self.consumir_recursos()
                
                self.acciones_rutinarias_generadas_hoy = {"7:00": False, "16:00": False}
                
                if self.dias_sobrevividos != self.ultimo_dia_notificado:
                    self.ultimo_dia_notificado = self.dias_sobrevividos
                    self.notificar(f"Dia {self.dias_sobrevividos} - {self.obtener_fecha_formateada()}", "info", 4000)
                if self.dia > 30:
                    self.dia = 1; self.mes += 1
                    mes_idx = max(0, min(11, self.mes - 1))
                    self.notificar(f"Nuevo mes: {self.meses[mes_idx]}", "info", 3000)
                    if self.mes > 12:
                        self.mes = 1; self.año += 1
                        self.notificar(f"Ano nuevo: {self.año}", "exito", 5000)

    def obtener_fecha_formateada(self):
        mes_idx = max(0, min(11, self.mes - 1)); dia_idx = max(0, min(6, self.dia_actual))
        return f"{self.dia_semana[dia_idx]}, {self.dia} {self.meses[mes_idx]} {self.año}"

    def obtener_hora_formateada(self):
        return f"{self.hora:02d}:{self.minuto:02d}"

    def obtener_periodo_dia(self):
        if 6 <= self.hora < 12: return "Mañana"
        elif 12 <= self.hora < 18: return "Tarde"
        elif 18 <= self.hora < 22: return "Atardecer"
        else: return "Noche"

    def generar_nombre_aleatorio(self, genero):
        nombres_m = ["Marcus","Kai","Omar","Dmitri","Hassan","Jin","Akira","Chen","Leo","Ivan"]
        nombres_f = ["Elena","Sofia","Luna","Aria","Nova","Maya","Zara","Rina","Cora","Iris"]
        apellidos = ["Rodriguez","Chen","Petrov","Kim","Singh","Silva","Yamamoto","Ali","Mueller","Santos"]
        nombre = random.choice(nombres_m) if genero == "Hombre" else random.choice(nombres_f)
        return f"{nombre} {random.choice(apellidos)}"

    def inicializar_colonia(self):
        id_actual = 1; num_por_rol = 2; roles = [Ingeniero, Biologo, Explorador, Guardia]
        for Rol in roles:
            for _ in range(num_por_rol):
                genero = random.choice(["Hombre", "Mujer"]); nombre = self.generar_nombre_aleatorio(genero)
                self.colonos.append(Rol(nombre, id_actual, genero)); id_actual += 1
        self.log("Colonia Epsilon-3 establecida", "exito"); self.log(f"Colonos iniciales: {len(self.colonos)}", "info")

    def log(self, mensaje, tipo="info"):
        self.historial.agregar(f"[{tipo.upper()}] {mensaje}")

    def gestionar_horario_trabajo(self):
        if self.hora == 22 and self.minuto == 0 and self.horario_trabajo_activo:
            self.iniciar_periodo_descanso()
        
        elif self.hora == 6 and self.minuto == 0 and not self.horario_trabajo_activo:
            self.finalizar_periodo_descanso()

    def iniciar_periodo_descanso(self):
        self.horario_trabajo_activo = False
        self.acciones_pausadas = []
        
        if "base" in self.zonas:
            destino_dormir = self.zonas["base"][:2]
        else:
            destino_dormir = [self.ancho_mapa // 2, self.alto_mapa // 2]
        
        colonos_trabajando = 0
        
        for colono in self.colonos:
            if colono.lifestage == "Adulto" and colono.salud > 0:
                
                if colono.ocupado and colono.accion_actual:
                    self.acciones_pausadas.append({
                        'accion': colono.accion_actual,
                        'progreso': colono.progreso_accion,
                        'colono_id': colono.id
                    })
                    colonos_trabajando += 1
                
                colono.ocupado = False
                colono.accion_actual = None
                colono.progreso_accion = 0
                
                offset_x = random.uniform(-4.0, 4.0)
                offset_y = random.uniform(-4.0, 4.0)
                colono.destino = [
                    float(destino_dormir[0]) + offset_x,
                    float(destino_dormir[1]) + offset_y
                ]
                
                colono.energia = min(100, colono.energia + 5)
        
        self.log(f"Periodo de descanso iniciado. {colonos_trabajando} tareas pausadas.", "info")
        self.notificar("Hora de dormir (10 PM). Colonos regresan al hábitat.", "info", 5000)

    def finalizar_periodo_descanso(self):
        self.horario_trabajo_activo = True
        
        for colono in self.colonos:
            if colono.lifestage == "Adulto" and colono.salud > 0:
                colono.energia = 100
                colono.destino = None
        
        acciones_restauradas = 0
        for accion_data in self.acciones_pausadas:
            accion = accion_data['accion']
            self.heap_prioridades.insertar(accion.prioridad, accion)
            acciones_restauradas += 1
        
        self.acciones_pausadas = []
        
        self.log(f"Periodo laboral iniciado. {acciones_restauradas} tareas restauradas.", "info")
        self.notificar("Buenos días (6 AM). Colonos listos para trabajar.", "exito", 5000)

    def generar_acciones_rutinarias(self):
        
        momento_actual = None
        
        if self.hora == 7 and self.minuto < 30 and not self.acciones_rutinarias_generadas_hoy["7:00"]:
            momento_actual = "7:00"
        elif self.hora == 16 and self.minuto < 30 and not self.acciones_rutinarias_generadas_hoy["16:00"]:
            momento_actual = "16:00"
        else:
            return

        acciones_esenciales = [
            ("generar_energia", "Mantenimiento reactor", "reactor"),
            ("recolectar_alimentos", "Cosecha", "cultivos"),
            ("explorar_terreno", "Exploracion NE", "exploracion_ne")
        ]
        
        for tipo, desc, zona in acciones_esenciales:
            if zona in self.zonas:
                self.cola_acciones.encolar(Accion(tipo, f"Rutina {momento_actual}: {desc}", zona_id=zona, duracion=None, metadata=None))
            else:
                self.log(f"Advertencia: Zona '{zona}' para '{tipo}' no existe. Omitiendo rutina.", "advertencia")

        self.log(f"Rutinas esenciales generadas para {momento_actual}.", "info")
        self.acciones_rutinarias_generadas_hoy[momento_actual] = True

    def procesar_evento(self, evento):
        self.log(f"EVENTO: {evento['nombre']}", "advertencia")
        self.log(f"    {evento['mensaje']}", "info")
        dano_c = evento.get('dano_colonos', 0)
        dano_s = evento.get('dano_structura', {})
        tipo_notif = "peligro" if dano_c > 10 or dano_s else ("advertencia" if dano_c > 0 else "info")
        self.notificar(f"{evento['nombre']}", tipo_notif, 5000)
        
        if evento['nombre'] == "Lluvia de Meteoritos":
            if self.callback_visual:
                self.callback_visual("meteor_shower")
                
        if evento['nombre'] == "Actividad Sismica":
            if self.callback_visual:
                self.callback_visual("earthquake")
                
        if evento['nombre'] == "Caida de Temperatura":
            if self.callback_visual:
                self.callback_visual("temp_drop")
        
        if evento['nombre'] == "Llegada de Nuevos Colonos":
            if self.callback_visual:
                self.callback_visual("new_colonists")
        if evento["nombre"] == "Tormenta Electromagnetica":
        
            self.notificar(evento["mensaje"], "peligro", 6000)
            
            if self.callback_visual:
                self.callback_visual("electromagnetic_storm")
                
        if evento['nombre'] == "Descubrimiento de Artefacto Alienigena":
            
            if self.callback_visual:
                self.callback_visual("artifact_discovery")

        if dano_s:
            dano_lab = dano_s.get("lab", 0) + random.randint(-5, 5)
            dano_hab = dano_s.get("hab", 0) + random.randint(-5, 5)
            
            lab_existe = False
            for zona_id in self.zonas.keys():
                if "laboratorio" in zona_id:
                    lab_existe = True
                    break
            
            if not lab_existe:
                for sitio_id, datos in self.sitios_construccion.items():
                    if "laboratorio" in sitio_id and datos.get("en_progreso", False):
                        lab_existe = True; break
            
            if dano_lab > 0 and self.salud_laboratorio > 0 and lab_existe:
                salud_anterior = self.salud_laboratorio
                self.salud_laboratorio = max(0, self.salud_laboratorio - dano_lab)
                self.log(f"    Laboratorio danado! Salud: {self.salud_laboratorio}%", "peligro")
                if self.salud_laboratorio < salud_anterior:
                    self.notificar(f"Lab danado ({self.salud_laboratorio}%)!", "peligro", 4000)

            if dano_hab > 0 and self.salud_habitat > 0:
                salud_anterior = self.salud_habitat
                self.salud_habitat = max(0, self.salud_habitat - dano_hab)
                self.log(f"    Habitat danado! Salud: {self.salud_habitat}%", "peligro")
                if self.salud_habitat < salud_anterior:
                    self.notificar(f"Hab danado ({self.salud_habitat}%)!", "peligro", 4000)

        if evento['nombre'] == "Llegada de Nuevos Colonos":
            num_nuevos = 3
            self.log(f"    Llegan {num_nuevos} colonos.", "exito")
            
            base_pos = self.zonas.get("base", [self.ancho_mapa//2, self.alto_mapa//2])[:2]
            
            for i in range(num_nuevos):
                nuevo_id = max((c.id for c in self.colonos), default=0) + 1
                
                nuevo_genero = random.choice(["Hombre", "Mujer"])
                nuevo_nombre = self.generar_nombre_aleatorio(nuevo_genero)
                
                Rol = random.choice([Ingeniero, Biologo, Explorador, Guardia])
                
                nuevo_colono = Rol(nuevo_nombre, nuevo_id, nuevo_genero)
                
                offset_x = random.uniform(-3.0, 3.0)
                offset_y = random.uniform(-3.0, 3.0)
                nuevo_colono.posicion = [
                    float(base_pos[0]) + offset_x,
                    float(base_pos[1]) + offset_y
                ]
                
                nuevo_colono.ocupado = False
                nuevo_colono.accion_actual = None
                nuevo_colono.destino = None
                
                nuevo_colono.energia = 100
                nuevo_colono.salud = 100
                
                self.colonos.append(nuevo_colono)
                
                self.log(f"    + {nuevo_nombre} ({nuevo_colono.tipo}) ID:{nuevo_id} en [{nuevo_colono.posicion[0]:.1f}, {nuevo_colono.posicion[1]:.1f}]", "exito")
            
            self.notificar(f"¡Llegaron {num_nuevos} colonos!", "exito", 5000)
            return

        if dano_c > 0:
            colonos_vivos = [c for c in self.colonos if c.salud > 0]
            if colonos_vivos:
                afectados = random.sample(colonos_vivos, k=min(2, len(colonos_vivos)))
                for colono in afectados:
                    dano_real = dano_c + random.randint(-max(1,dano_c//3), max(1,dano_c//2))
                    colono.recibir_dano(dano_real)
                    if colono.salud <= 0:
                        self.log(f"    {colono.nombre} MUERTO por {evento['nombre']}", "peligro")
                        self.notificar(f"{colono.nombre} ha fallecido", "peligro", 6000); self.colonos_perdidos += 1
                    elif dano_real > 10:
                        self.log(f"    {colono.nombre} herido ({colono.salud}%)", "advertencia")
                        self.notificar(f"{colono.nombre} herido", "advertencia", 4000)

        for tipo_accion in evento.get('acciones', []):
            zona_id = self.mapa_tareas_zonas.get(tipo_accion)
            desc = f"URGENTE: {tipo_accion}"
            if zona_id in self.zonas or zona_id is None:
                self.cola_acciones.encolar(Accion(tipo_accion, desc, zona_id=zona_id))
            else: self.log(f"Advertencia: Zona '{zona_id}' para '{tipo_accion}' no existe.", "advertencia")

    def asignar_acciones(self):
        
        if not self.horario_trabajo_activo:
            return
        
        while not self.cola_acciones.esta_vacia():
            accion = self.cola_acciones.desencolar()
            self.heap_prioridades.insertar(accion.prioridad, accion)
        
        colonos_disponibles = [c for c in self.colonos
                              if c.lifestage == "Adulto"
                              and c.salud > 0
                              and not c.ocupado]
        
        if not colonos_disponibles or self.heap_prioridades.esta_vacio():
            return

        tareas_para_reinsertar = []

        while colonos_disponibles and not self.heap_prioridades.esta_vacio():
            accion = self.heap_prioridades.extraer_minimo()
            
            colono_elegido = self.encontrar_mejor_colono(accion, colonos_disponibles)
            
            if colono_elegido:
                destino = None
                
                if accion.tipo == "construir" and accion.metadata and "construir_sitio" in accion.metadata:
                    sid = accion.metadata["construir_sitio"]
                    if sid in self.sitios_construccion:
                        destino = self.sitios_construccion[sid]["centro"]
                elif accion.zona_id and accion.zona_id in self.zonas:
                    destino = self.zonas[accion.zona_id][:2]
                
                colono_elegido.asignar_accion(accion, destino_zona=destino)
                self.log(f"{colono_elegido.nombre} -> {accion.tipo} @ {accion.zona_id or '??'}", "info")
                colonos_disponibles.remove(colono_elegido)
                
            else:
                tareas_para_reinsertar.append(accion)
            
            if not colonos_disponibles:
                while not self.heap_prioridades.esta_vacio():
                    tareas_para_reinsertar.append(self.heap_prioridades.extraer_minimo())
                break
        
        for accion in tareas_para_reinsertar:
            self.heap_prioridades.insertar(accion.prioridad, accion)

    def encontrar_mejor_colono(self, accion, colonos_disponibles):
        mejores = []
        for c in colonos_disponibles:
            if c.puede_realizar(accion.tipo):
                ef = c.aptitudes.get(accion.tipo, 0.5); d_pen = 0; dest = None
                if accion.tipo=="construir" and accion.metadata and "construir_sitio" in accion.metadata:
                    sid = accion.metadata["construir_sitio"];
                    if sid in self.sitios_construccion: dest = self.sitios_construccion[sid]["centro"]
                elif accion.zona_id and accion.zona_id in self.zonas: dest = self.zonas[accion.zona_id][:2]
                if dest: d = math.hypot(c.posicion[0]-dest[0], c.posicion[1]-dest[1]); d_pen = d/10
                punt = (ef*100)-d_pen; mejores.append((punt, c))
        if mejores: mejores.sort(reverse=True, key=lambda i: i[0]); return mejores[0][1]
        return None

    def _procesar_accion_completada(self, accion, colono):
        resultado = {"accion": accion.tipo}
        efectividad = colono.aptitudes.get(accion.tipo, 0.5) * random.uniform(0.9, 1.1)
        self.tareas_completadas += 1

        if accion.tipo == "construir" and accion.metadata and "construir_sitio" in accion.metadata:
            sitio_id = accion.metadata["construir_sitio"]
            if sitio_id in self.sitios_construccion:
                sitio_data = self.sitios_construccion.pop(sitio_id)
                nuevo_id_zona = sitio_data["tipo_nuevo"]
                nuevo_color = (150,150,200)
                if "cultivos" in nuevo_id_zona: nuevo_color=(100,255,100); self.mapa_tareas_zonas["recolectar_alimentos"]=nuevo_id_zona; self.mapa_tareas_zonas["cultivar"]=nuevo_id_zona
                elif "laboratorio" in nuevo_id_zona: nuevo_color=(100,200,255)
                elif "habitat" in nuevo_id_zona: nuevo_color=(200,180,255)
                elif "geotermica" in nuevo_id_zona: nuevo_color=(255,100,0); self.mapa_tareas_zonas["generar_energia"]=nuevo_id_zona
                self.zonas[nuevo_id_zona] = (sitio_data["centro"][0], sitio_data["centro"][1], nuevo_color, sitio_data["tiles"])
                self.notificar(f"Construccion: {nuevo_id_zona}!", "exito"); resultado["construccion"]=nuevo_id_zona
            return resultado

        if accion.tipo == "curar":
            costo_alimentos = 20
            costo_energia = 15
            costo_materiales = 25
            
            if (self.recursos["alimentos"] >= costo_alimentos and
                self.recursos["energia"] >= costo_energia and
                self.recursos["materiales"] >= costo_materiales):
                
                self.recursos["alimentos"] -= costo_alimentos
                self.recursos["energia"] -= costo_energia
                self.recursos["materiales"] -= costo_materiales
                
                colonos_heridos = [c for c in self.colonos
                                   if c.salud > 0 and c.salud < 100
                                   and c.lifestage == "Adulto"]
                
                if colonos_heridos:
                    colonos_heridos.sort(key=lambda c: c.salud)
                    curados = 0
                    
                    for paciente in colonos_heridos[:3]:
                        cantidad_cura = int(random.randint(30, 50) * efectividad)
                        salud_anterior = paciente.salud
                        paciente.curar(cantidad_cura)
                        cura_real = paciente.salud - salud_anterior
                        
                        if cura_real > 0:
                            self.log(f"  {paciente.nombre} curado +{cura_real}HP (→{paciente.salud}%)", "exito")
                            curados += 1
                    
                    self.log(f"{colono.nombre} completó curación. {curados} colonos atendidos.", "exito")
                    self.notificar(
                        f"Curación: {curados} colonos (-{costo_alimentos} -{costo_energia} -{costo_materiales})",
                        "exito",
                        3500
                    )
                else:
                    self.log(f"{colono.nombre} completó curación pero no había heridos.", "info")
                    self.notificar("Curación: No había colonos heridos", "info", 2500)
            
            else:
                faltantes = []
                if self.recursos["alimentos"] < costo_alimentos:
                    faltantes.append(f"{costo_alimentos - self.recursos['alimentos']}")
                if self.recursos["energia"] < costo_energia:
                    faltantes.append(f"{costo_energia - self.recursos['energia']}")
                if self.recursos["materiales"] < costo_materiales:
                    faltantes.append(f"{costo_materiales - self.recursos['materiales']}")
                
                self.log(f"FALLO: Curación sin recursos. Faltan: {', '.join(faltantes)}", "peligro")
                self.notificar(
                    f" Curación fallida: Faltan {', '.join(faltantes)}",
                    "peligro",
                    4000
                )
            
            return resultado

        if accion.tipo == "reparar_laboratorio":
            if self.salud_laboratorio < self.MAX_SALUD_ESTRUCTURA:
                reparado = int(25 * efectividad); salud_ant = self.salud_laboratorio
                self.salud_laboratorio = min(self.MAX_SALUD_ESTRUCTURA, self.salud_laboratorio + reparado)
                if self.salud_laboratorio > salud_ant:
                    self.log(f"{colono.nombre} reparo lab (+{self.salud_laboratorio-salud_ant}). Salud: {self.salud_laboratorio}%", "exito")
                    self.notificar(f"Lab reparado (+{self.salud_laboratorio-salud_ant}%).", "exito", 3000)

        elif accion.tipo == "reparar_habitat":
            if self.salud_habitat < self.MAX_SALUD_ESTRUCTURA:
                reparado = int(30 * efectividad); salud_ant = self.salud_habitat
                self.salud_habitat = min(self.MAX_SALUD_ESTRUCTURA, self.salud_habitat + reparado)
                if self.salud_habitat > salud_ant:
                    self.log(f"{colono.nombre} reparo hab (+{self.salud_habitat-salud_ant}). Salud: {self.salud_habitat}%", "exito")
                    self.notificar(f"Hab reparado (+{self.salud_habitat-salud_ant}%).", "exito", 3000)

        elif accion.tipo == "generar_energia":
            ganancia = int(150 * efectividad); self.recursos["energia"] = min(200, self.recursos["energia"]+ganancia)
            if ganancia > 120: self.notificar(f"Energia +{ganancia} energia", "exito", 2500)
        elif accion.tipo == "recolectar_alimentos":
            ganancia = int(140 * efectividad); self.recursos["alimentos"] = min(200, self.recursos["alimentos"]+ganancia)
            if ganancia > 110: self.notificar(f"Alimentos +{ganancia} alimentos", "exito", 2500)
        elif accion.tipo in ["explorar_terreno", "recolectar_recursos", "explorar_cavernas"]:
            if accion.tipo == "explorar_cavernas": ganancia = int(100 * efectividad); prob_sitio = 0.40; tipo_pref="especial"
            else: ganancia = int(120 * efectividad); prob_sitio = 0.25; tipo_pref=None
            self.recursos["materiales"] = min(200, self.recursos["materiales"]+ganancia)
            if ganancia > (70 if accion.tipo=="explorar_cavernas" else 90): self.notificar(f"Recursos +{ganancia} mat.", "exito", 2500)
            if random.random() < prob_sitio:
                if self.mapa_terreno:
                    nuevo_sitio = self._generar_nuevo_sitio_construccion(self.mapa_terreno, tipo_preferido=tipo_pref)
                    if nuevo_sitio: resultado["descubrimiento"] = nuevo_sitio
        elif accion.tipo == "investigar_flora" and random.random() < efectividad:
            self.recursos["alimentos"] += 60; self.log("Descubrimiento flora!", "exito"); self.notificar("Descubrimiento!", "exito", 4000)

        return resultado

    def ejecutar_ciclo(self):
        self.ciclo += 1
        self.avanzar_tiempo()
        
        self.gestionar_horario_trabajo()
        
        if self.ciclo % 5 == 0 or self.ciclo == 1:
            self.log(f"CICLO {self.ciclo} - {self.obtener_hora_formateada()}", "info")
        
        evento = GeneradorEventos.generar_evento()
        if evento:
            self.eventos_totales += 1
            self.procesar_evento(evento)
        
        if self.horario_trabajo_activo:
            self.generar_acciones_rutinarias()
        
        resultados = self.actualizar_progreso_acciones()
        
        if self.horario_trabajo_activo:
            self.asignar_acciones()
        
        self.mantenimiento_colonos()
        return resultados

    def actualizar_progreso_acciones(self):
        
        if not self.horario_trabajo_activo:
            return {}
        
        resultados = {}
        for colono in self.colonos:
            if colono.ocupado and colono.accion_actual and colono.salud > 0:
                en_destino = True
                if colono.destino:
                    dist = math.hypot(colono.posicion[0]-colono.destino[0],
                                      colono.posicion[1]-colono.destino[1])
                    if dist > colono.velocidad * 1.5:
                        en_destino = False
                
                if en_destino:
                    colono.progreso_accion += 1
                    colono.energia = max(0, colono.energia - 0.5)
                    
                    if colono.progreso_accion >= colono.accion_actual.duracion:
                        accion_completada = colono.completar_accion()
                        if accion_completada:
                            res = self._procesar_accion_completada(accion_completada, colono)
                            resultados.update(res)
                        colono.progreso_accion = 0
        
        return resultados

    def mantenimiento_colonos(self):
        a_remover = []
        for colono in self.colonos:
            if colono.salud > 0:
                colono.actualizar_movimiento(self.ancho_mapa, self.alto_mapa)
                if colono.lifestage=="Adulto" and not colono.ocupado and colono.energia<50: colono.descansar()
                alerta_id=f"salud_{colono.nombre}"
                if colono.salud<30 and alerta_id not in self.alertas_enviadas: self.notificar(f"{colono.nombre} salud critica!", "peligro", 5000); self.alertas_enviadas.add(alerta_id)
                elif colono.salud>=50 and alerta_id in self.alertas_enviadas: self.alertas_enviadas.discard(alerta_id)
                dano_aleatorio = 1 if colono.lifestage=="Adulto" else 2
                if random.random()<0.02:
                    colono.recibir_dano(random.randint(1, dano_aleatorio*2))
                    if colono.salud<=0: self.colonos_perdidos+=1; self.log(f"{colono.nombre} ha fallecido.", "peligro"); self.notificar(f"{colono.nombre} ha fallecido", "peligro", 6000); a_remover.append(colono)
        for c in a_remover:
            if c in self.colonos: self.colonos.remove(c)

    def consumir_recursos(self):
        vivos = len([c for c in self.colonos if c.salud > 0]); consumo_base=5; consumo_por_colono=2
        consumo_alim = max(1, consumo_base + (vivos * consumo_por_colono)); consumo_ener = max(1, consumo_base + (vivos * consumo_por_colono))
        self.recursos["alimentos"] = max(0, self.recursos["alimentos"] - consumo_alim); self.recursos["energia"] = max(0, self.recursos["energia"] - consumo_ener)
        if self.recursos["alimentos"]<20:
            if "comida_baja" not in self.alertas_enviadas: tipo="peligro" if self.recursos["alimentos"]<10 else "advertencia"; self.notificar(f"Alimentos criticos: {self.recursos['alimentos']}", tipo, 4000); self.alertas_enviadas.add("comida_baja")
        elif self.recursos["alimentos"]>=50 and "comida_baja" in self.alertas_enviadas: self.alertas_enviadas.discard("comida_baja")
        if self.recursos["energia"]<30:
            if "energia_baja" not in self.alertas_enviadas: tipo="peligro" if self.recursos["energia"]<15 else "advertencia"; self.notificar(f"Energia critica: {self.recursos['energia']}", tipo, 4000); self.alertas_enviadas.add("energia_baja")
        elif self.recursos["energia"]>=60 and "energia_baja" in self.alertas_enviadas: self.alertas_enviadas.discard("energia_baja")

    def agregar_tarea_personalizada(self, tipo, descripcion):
        if tipo in Accion.PRIORIDADES:
            zona_id = self.mapa_tareas_zonas.get(tipo)
            if zona_id and zona_id not in self.zonas: self.log(f"Adv: Zona '{zona_id}' para '{tipo}' no existe.", "advertencia"); zona_id = None
            self.cola_acciones.encolar(Accion(tipo, descripcion, zona_id=zona_id))
            self.log(f"Tarea agregada: {tipo} @ {zona_id or 'Base'}", "exito")
            self.notificar(f"Nueva tarea: {descripcion}", "tarea", 3000); return True
        else: self.log(f"Error: Tarea desconocida '{tipo}'", "peligro"); self.notificar(f"Error: Tarea '{tipo}' no reconocida", "peligro", 4000); return False

    def generar_sitios_construccion(self, mapa_terreno):
        try:
            cx,cy=self._encontrar_punto_inicio_zona(mapa_terreno,'pasto',min_dist=15,max_dist=40); ctx,cty,col,tls=self._generar_zona_blob(mapa_terreno,cx,cy,(100,100,100),30)
            self.sitios_construccion["sitio_cultivo_1"]={"centro":(ctx,cty),"color":col,"tiles":tls,"tipo_nuevo":"cultivos_exp_1","costo":100,"en_progreso":False}
        except Exception as e: self.log(f"Error gen sitio cultivo: {e}", "peligro")
        try:
            lx,ly=self._encontrar_punto_inicio_zona(mapa_terreno,'pasto',min_dist=10,max_dist=30); ltx,lty,lcol,ltls=self._generar_zona_blob(mapa_terreno,lx,ly,(100,100,100),25)
            self.sitios_construccion["sitio_lab_1"]={"centro":(ltx,lty),"color":lcol,"tiles":ltls,"tipo_nuevo":"laboratorio_1","costo":150,"en_progreso":False}
        except Exception as e: self.log(f"Error gen sitio lab: {e}", "peligro")
        self.log(f"Sitios construccion iniciales: {len(self.sitios_construccion)}", "info")
        try:
            hx,hy=self._encontrar_punto_inicio_zona(mapa_terreno,'pasto',min_dist=10,max_dist=30)
            htx,hty,hcol,htls=self._generar_zona_blob(mapa_terreno,hx,hy,(100,100,100),35)
            self.sitios_construccion["sitio_habitat_1"]={"centro":(htx,hty),"color":hcol,"tiles":htls,"tipo_nuevo":"habitat_exp_1","costo":120,"en_progreso":False}
        except Exception as e: self.log(f"Error gen sitio habitat: {e}", "peligro")

    def _generar_nuevo_sitio_construccion(self, mapa_terreno, tipo_preferido=None):
        self.log("Exploracion: posible sitio detectado.", "exito")
        tipo_terr=random.choice(['pasto','desierto'])
        try: sx,sy=self._encontrar_punto_inicio_zona(mapa_terreno,tipo_terr,min_dist=50,evitar_zonas=True)
        except Exception as e: self.log(f"No ubicacion para sitio: {e}", "advertencia"); return None
        tam=random.randint(20,35); cx,cy,col,tls=self._generar_zona_blob(mapa_terreno,sx,sy,(120,120,120),tam)
        tipos_pos=["cultivos","laboratorio","habitat"]; costo_base=120
        if tipo_preferido=="especial": tipos_pos.append("geotermica"); costo_base=180
        tipo_nuevo=random.choice(tipos_pos); costo=costo_base+random.randint(-20,50); indice=1
        while f"sitio_{tipo_nuevo}_{indice}" in self.sitios_construccion: indice+=1
        nuevo_id=f"sitio_{tipo_nuevo}_{indice}"; zona_final=f"{tipo_nuevo}_exp_{indice}"
        self.sitios_construccion[nuevo_id]={"centro":(cx,cy),"color":col,"tiles":tls,"tipo_nuevo":zona_final,"costo":costo,"en_progreso":False}
        self.log(f"Nuevo sitio descubierto: {nuevo_id}!", "exito"); self.notificar(f"Sitio descubierto para {tipo_nuevo}!", "exito", 5000)
        return nuevo_id

    def iniciar_construccion(self, sitio_id):
        sitio = self.sitios_construccion.get(sitio_id)
        if not sitio: self.notificar(f"Error: Sitio {sitio_id} no existe", "peligro"); return
        if sitio["en_progreso"]: self.notificar(f"Construccion ya en progreso en {sitio_id}", "advertencia"); return
        costo = sitio["costo"]
        if self.recursos["materiales"] < costo: self.notificar(f"Materiales insuficientes ({self.recursos['materiales']}/{costo})", "peligro"); return
        self.recursos["materiales"] -= costo; sitio["en_progreso"] = True
        accion = Accion("construir", f"Construir {sitio['tipo_nuevo']}", metadata={"construir_sitio": sitio_id})
        self.heap_prioridades.insertar(accion.prioridad, accion)
        self.notificar(f"Construccion iniciada: {sitio['tipo_nuevo']} ({costo} mat.)", "exito")
        self.log(f"Construccion iniciada {sitio_id}, costo {costo} mat.", "info")

    def mantenimiento_envejecimiento(self):
        dias_año=120; convertir=[]
        for c in self.colonos:
            c.edad_dias+=1
            if c.edad_dias>=dias_año: c.edad+=1; c.edad_dias=0
            if c.lifestage=="Infante" and c.edad>=18: convertir.append(c)
        for c in convertir: self.convertir_a_adulto(c)

    def convertir_a_adulto(self, colono):
        colono.lifestage = "Adulto"
        tipo = random.choice(["Ingeniero", "Biologo", "Explorador", "Guardia"]); colono.tipo = tipo
        apt_base={k:0.6 for k in Accion.PRIORIDADES}
        if tipo=="Ingeniero": apt={"reparar_laboratorio":0.85,"generar_energia":0.8,"reparar_habitat":0.75,"construir":0.7}
        elif tipo=="Biologo": apt={"recolectar_alimentos":0.85,"cultivar":0.8,"investigar_flora":0.75,"curar":0.65}
        elif tipo=="Explorador": apt={"explorar_terreno":0.85,"recolectar_recursos":0.75,"cartografiar":0.7,"explorar_cavernas":0.65}
        elif tipo=="Guardia": apt={"defenderse":0.85,"patrullar":0.8,"proteger_colonos":0.75,"vigilar":0.7}
        apt_base.update(apt); colono.aptitudes=apt_base
        self.notificar(f"{colono.nombre} es ahora {tipo}!", "exito", 5000)

    def mantenimiento_reproduccion(self):
        prob=0.03;
        if random.random()>prob: return
        if "base" not in self.zonas: return
        bc=self.zonas["base"][:2]; mujeres=[]; hombres=[]
        for c in self.colonos:
            if c.lifestage!="Adulto" or c.salud<=0 or c.ocupado: continue
            dist=math.hypot(c.posicion[0]-bc[0], c.posicion[1]-bc[1])
            if dist>15: continue
            if c.genero=="Mujer" and 18<=c.edad<45: mujeres.append(c)
            elif c.genero=="Hombre" and 18<=c.edad<60: hombres.append(c)
        if mujeres and hombres: self.generar_nacimiento(random.choice(mujeres), random.choice(hombres))

    def generar_nacimiento(self, madre, padre):
        nid = max((c.id for c in self.colonos), default=0)+1
        ngen = random.choice(["Hombre", "Mujer"]); nnom = self.generar_nombre_aleatorio(ngen)
        nbebe = Colono(nnom, nid, ngen, edad_inicial=0)
        if "base" in self.zonas: bc=self.zonas["base"][:2]; nbebe.posicion=[float(bc[0]+random.randint(-2,2)), float(bc[1]+random.randint(-2,2))]
        self.colonos.append(nbebe)
        self.notificar(f"Ha nacido {nnom}!", "exito", 6000)
        
    def get_conteo_estructuras(self):
        conteo = {"laboratorio": 0, "habitat": 0, "cultivos": 0}
        
        for zona_id in self.zonas.keys():
            if "laboratorio" in zona_id:
                conteo["laboratorio"] += 1
            elif "habitat" in zona_id or "base" in zona_id:
                conteo["habitat"] += 1
            elif "cultivos" in zona_id:
                conteo["cultivos"] += 1
                
        return conteo