import random
import math

class Colono:
    def __init__(self, nombre, id_colono, genero, edad_inicial=0):
        self.nombre = nombre
        self.id = id_colono
        self.tipo = "Colono" 
        self.energia = 100
        self.salud = 100
        self.ocupado = False
        self.accion_actual = None
        self.progreso_accion = 0
        self.aptitudes = {}
        
        self.genero = genero
        self.edad = edad_inicial
        self.edad_dias = 0
        
        if self.edad < 18:
            self.lifestage = "Infante"
            self.tipo = "Infante"
        else:
            self.lifestage = "Adulto"

        self.posicion = [0.0, 0.0]
        self.destino = None
        self.velocidad = 10.0
        self.velocidad_actual = [0.0, 0.0]
        self.aceleracion = 0.9
        self.friccion = 0.95  
        self.velocidad_maxima = 10.0  
        self.tiempo_deambular = 0
        self.dx_deambular = 0
        self.dy_deambular = 0

    def actualizar_movimiento(self, ancho_mapa, alto_mapa):
        
        if self.salud <= 0:
            return

        if self.lifestage == "Infante":
            return

        if self.energia <= 0:
            velocidad_efectiva = 0
        elif self.energia < 30:
            velocidad_efectiva = self.velocidad * 0.4
        elif self.energia < 60:
            velocidad_efectiva = self.velocidad * 0.7
        else:
            velocidad_efectiva = self.velocidad

        if self.destino:
            dx = self.destino[0] - self.posicion[0]
            dy = self.destino[1] - self.posicion[1]
            distancia = math.sqrt(dx**2 + dy**2)
            
            
            if distancia < 0.8:
                self.posicion = list(self.destino)
                self.destino = None
                self.velocidad_actual[0] *= 0.8
                self.velocidad_actual[1] *= 0.8
            elif velocidad_efectiva > 0:
                dir_x = dx / distancia
                dir_y = dy / distancia
                accel_x = dir_x * self.aceleracion * velocidad_efectiva
                accel_y = dir_y * self.aceleracion * velocidad_efectiva
                
                self.velocidad_actual[0] += accel_x
                self.velocidad_actual[1] += accel_y
                
                vel_magnitud = math.sqrt(self.velocidad_actual[0]**2 + self.velocidad_actual[1]**2)
                if vel_magnitud > velocidad_efectiva * self.velocidad_maxima:
                    factor = (velocidad_efectiva * self.velocidad_maxima) / vel_magnitud
                    self.velocidad_actual[0] *= factor
                    self.velocidad_actual[1] *= factor
                
                if distancia < 5.0:
                    factor_frenado = distancia / 5.0
                    self.velocidad_actual[0] *= factor_frenado
                    self.velocidad_actual[1] *= factor_frenado
                
                self.posicion[0] += self.velocidad_actual[0]
                self.posicion[1] += self.velocidad_actual[1]
        
        else:
            self.velocidad_actual[0] *= self.friccion
            self.velocidad_actual[1] *= self.friccion
            
            self.posicion[0] += self.velocidad_actual[0]
            self.posicion[1] += self.velocidad_actual[1]
            
            if not self.ocupado and velocidad_efectiva > 0:
                self.tiempo_deambular += 1
                
                if self.tiempo_deambular > random.randint(60, 120):
                    self.tiempo_deambular = 0
                    
                    if random.random() < 0.3:  
                        angulo = random.uniform(0, 2 * math.pi)
                        velocidad_deambular = velocidad_efectiva * 0.3
                        
                        self.dx_deambular = math.cos(angulo) * velocidad_deambular
                        self.dy_deambular = math.sin(angulo) * velocidad_deambular
                    else:
                        self.dx_deambular = 0
                        self.dy_deambular = 0
                
                
                if abs(self.dx_deambular) > 0.01 or abs(self.dy_deambular) > 0.01:
                    self.velocidad_actual[0] += self.dx_deambular * 0.1
                    self.velocidad_actual[1] += self.dy_deambular * 0.1
                    
                    
                    self.dx_deambular *= 0.98
                    self.dy_deambular *= 0.98

       
        self.posicion[0] = max(1.0, min(ancho_mapa - 1.0, self.posicion[0]))
        self.posicion[1] = max(1.0, min(alto_mapa - 1.0, self.posicion[1]))
        
        
        if self.posicion[0] <= 1.0 or self.posicion[0] >= ancho_mapa - 1.0:
            self.velocidad_actual[0] = 0
        if self.posicion[1] <= 1.0 or self.posicion[1] >= alto_mapa - 1.0:
            self.velocidad_actual[1] = 0
    
    def puede_realizar(self, accion):
        if self.ocupado or self.energia < 20 or self.salud < 30 or self.lifestage != "Adulto":
            return False
        return accion in self.aptitudes
    
    def asignar_accion(self, accion, destino_zona=None):
        self.ocupado = True
        self.accion_actual = accion
        self.progreso_accion = 0
        self.energia -= 15
        if destino_zona:
            
            offset_x = random.uniform(-3.0, 3.0)
            offset_y = random.uniform(-3.0, 3.0)
            self.destino = [
                float(destino_zona[0]) + offset_x,
                float(destino_zona[1]) + offset_y
            ]
    
    def completar_accion(self):
        accion = self.accion_actual
        self.ocupado = False
        self.accion_actual = None
        self.destino = None
        return accion
    
    def descansar(self):
        self.energia = min(100, self.energia + 25)
    
    def recibir_dano(self, cantidad):
        self.salud = max(0, self.salud - cantidad)
    
    def curar(self, cantidad):
        self.salud = min(100, self.salud + cantidad)


class Ingeniero(Colono):
    def __init__(self, nombre, id_colono, genero):
        super().__init__(nombre, id_colono, genero, edad_inicial=random.randint(20, 35))
        self.tipo = "Ingeniero"
        self.velocidad = 10.0  
        self.aptitudes = {
            "reparar_laboratorio": 0.95, "generar_energia": 0.90,
            "reparar_habitat": 0.85, "construir": 0.80
        }

class Biologo(Colono):
    def __init__(self, nombre, id_colono, genero):
        super().__init__(nombre, id_colono, genero, edad_inicial=random.randint(20, 35))
        self.tipo = "Biólogo"
        self.velocidad = 10.0  
        self.aptitudes = {
            "recolectar_alimentos": 0.95, "cultivar": 0.90,
            "investigar_flora": 0.85, "curar": 0.75
        }

class Explorador(Colono):
    def __init__(self, nombre, id_colono, genero):
        super().__init__(nombre, id_colono, genero, edad_inicial=random.randint(20, 35))
        self.tipo = "Explorador"
        self.velocidad = 10.0  
        self.velocidad_maxima = 2.5 
        self.aptitudes = {
            "explorar_terreno": 0.95, "recolectar_recursos": 0.85,
            "cartografiar": 0.80, "explorar_cavernas": 0.75
        }

class Guardia(Colono):
    def __init__(self, nombre, id_colono, genero):
        super().__init__(nombre, id_colono, genero, edad_inicial=random.randint(20, 35))
        self.tipo = "Guardia"
        self.velocidad = 10.0 
        self.aptitudes = {
            "defenderse": 0.95, "patrullar": 0.90,
            "proteger_colonos": 0.85, "vigilar": 0.80
        }