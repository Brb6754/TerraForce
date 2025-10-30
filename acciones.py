import random 
import math 

MINUTES_PER_CYCLE = 30

class Accion:
    PRIORIDADES = {
        "reparar_laboratorio": 2,
        "reparar_habitat": 2, "generar_energia": 3, "recolectar_alimentos": 4,
        "cultivar": 4, "explorar_terreno": 5, "recolectar_recursos": 5,
        "construir": 5, "investigar_flora": 6, "cartografiar": 6,
        "explorar_cavernas": 6, "curar": 2
    }
    
    DURACIONES_BASE_CYCLES = {
         "reparar_laboratorio": 2,
        "reparar_habitat": 2, "generar_energia": 3, "recolectar_alimentos": 3,
        "cultivar": 1, 
        "explorar_terreno": 8,
        "recolectar_recursos": 8,
        "construir": 5,
        "investigar_flora": 8,
        "cartografiar": 8,
        "explorar_cavernas": 8,
        "curar": 3
    }
    
    
    DURACIONES_BASE_MINUTES = {k: v * MINUTES_PER_CYCLE for k, v in DURACIONES_BASE_CYCLES.items()}
    
    
    
    def __init__(self, tipo, descripcion, duracion=None, zona_id=None, metadata=None, prioridad=None):
        self.tipo = tipo
        self.descripcion = descripcion
        self.prioridad = prioridad if prioridad is not None else self.PRIORIDADES.get(tipo, 10)
        
        min_base = self.DURACIONES_BASE_MINUTES.get(tipo, 5 * MINUTES_PER_CYCLE) 

        if duracion is not None:
            min_duracion = duracion 
        else:
            min_variacion = random.randint(-1, 2) * MINUTES_PER_CYCLE
            min_duracion = max(MINUTES_PER_CYCLE, min_base + min_variacion) 

        self.duracion_minutos = min_duracion
        self.duracion = max(1, math.ceil(min_duracion / MINUTES_PER_CYCLE)) 
        
        self.completada = False
        self.zona_id = zona_id
        self.metadata = metadata
    
    def __str__(self):
        zona_str = f" @ {self.zona_id}" if self.zona_id else ""
        meta_str = f" ({self.metadata})" if self.metadata else ""
        return f"[P{self.prioridad} / {self.duracion_minutos} min ({self.duracion} c)] {self.tipo}{zona_str}{meta_str}"