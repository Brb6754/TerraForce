import pygame
import math

class SpriteManager:
    def __init__(self):
        self.sprite_sheet = None
        self.sprite_loaded = False
        self.sprite_width_original = 512
        self.sprite_height_original = 512
        self.sprite_width = 32
        self.sprite_height = 32
        self.num_frames = 16

        self.color_map = {
            "Ingeniero": (50, 180, 255),
            "Biólogo": (100, 255, 150),
            "Explorador": (255, 180, 50),
            "Guardia": (255, 50, 100),
            "Infante": (255, 200, 255)
        }

        self.sprite_cache = {}

        self.cargar_sprites()

    def cargar_sprites(self):
        try:
            original_sheet = pygame.image.load("Assets/1.png").convert_alpha()
            print(f"Sprite sheet cargado: {original_sheet.get_width()}x{original_sheet.get_height()}")

            sheet_width = original_sheet.get_width()
            sheet_height = original_sheet.get_height()

            if sheet_width > sheet_height:
                self.sprite_width_original = sheet_width // self.num_frames
                self.sprite_height_original = sheet_height
            else:
                self.sprite_width_original = sheet_width
                self.sprite_height_original = sheet_height // self.num_frames

            print(f"Tamaño por frame original: {self.sprite_width_original}x{self.sprite_height_original}")

            nuevo_ancho = self.sprite_width * self.num_frames
            nuevo_alto = self.sprite_height

            self.sprite_sheet = pygame.transform.scale(original_sheet, (nuevo_ancho, nuevo_alto))
            self.sprite_loaded = True
            print(f"Redimensionado a: {nuevo_ancho}x{nuevo_alto} ({self.sprite_width}x{self.sprite_height} por frame)")

        except pygame.error as e:
            print(f"No se pudo cargar colono_sprite.png: {e}")
            self.sprite_loaded = False

    def get_frame(self, frame_index, escala=1.0, flip_x=False):
        if not self.sprite_loaded:
            return None

        frame_index = frame_index % self.num_frames
        cache_key = (frame_index, escala, flip_x)

        if cache_key in self.sprite_cache:
            return self.sprite_cache[cache_key]

        x = frame_index * self.sprite_width
        y = 0

        frame = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
        frame.blit(self.sprite_sheet, (0, 0), (x, y, self.sprite_width, self.sprite_height))

        if flip_x:
            frame = pygame.transform.flip(frame, True, False)

        if escala != 1.0:
            nuevo_ancho = max(8, int(self.sprite_width * escala))
            nuevo_alto = max(8, int(self.sprite_height * escala))
            frame = pygame.transform.scale(frame, (nuevo_ancho, nuevo_alto))

        self.sprite_cache[cache_key] = frame
        return frame

    def aplicar_color(self, surface, color, intensidad=0.5):
        colored = surface.copy()
        color_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        alpha = int(255 * intensidad)
        color_surface.fill((*color, alpha))
        colored.blit(color_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return colored

    def dibujar_colono_sprite(self, pantalla, colono, posicion, zoom=1.0, ciclo_animacion=0):
        if not self.sprite_loaded:
            return False

        esta_moviendose = False
        flip_x = False

        if hasattr(colono, 'velocidad_actual'):
            vel_x = colono.velocidad_actual[0]
            vel_y = colono.velocidad_actual[1]
            magnitud = math.sqrt(vel_x**2 + vel_y**2)
            esta_moviendose = magnitud > 0.5

            if vel_x < -0.1:
                flip_x = True
            elif vel_x > 0.1:
                flip_x = False

        if esta_moviendose:
            velocidad_anim = max(2, int(5 - magnitud * 0.2)) if hasattr(colono, 'velocidad_actual') else 4
            frame_index = (ciclo_animacion // velocidad_anim) % 8
        else:
            frame_index = 0

        escala = max(0.4, min(2.5, zoom * 0.7))

        frame = self.get_frame(frame_index, escala, flip_x)

        if frame is None:
            return False

        color = self.color_map.get(colono.tipo, (255, 255, 255))
        frame_colored = self.aplicar_color(frame, color, intensidad=0.6)

        if colono.salud < 50:
            intensidad_rojo = (1 - colono.salud / 50) * 0.4
            red_tint = pygame.Surface(frame_colored.get_size(), pygame.SRCALPHA)
            red_alpha = int(255 * intensidad_rojo)
            red_tint.fill((255, 0, 0, red_alpha))
            frame_colored.blit(red_tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        rect = frame_colored.get_rect(center=posicion)
        pantalla.blit(frame_colored, rect)

        if colono.salud < 100:
            self._dibujar_barra_salud(pantalla, colono, rect, zoom)

        if colono.ocupado and colono.accion_actual:
            self._dibujar_indicador_trabajo(pantalla, rect, zoom)

        return True

    def _dibujar_barra_salud(self, pantalla, colono, rect, zoom):
        barra_ancho = max(12, int(rect.width * 0.9))
        barra_alto = max(2, int(4 * zoom))
        barra_x = rect.centerx - barra_ancho // 2
        barra_y = rect.top - barra_alto - 3

        fondo = pygame.Surface((barra_ancho, barra_alto), pygame.SRCALPHA)
        fondo.fill((0, 0, 0, 180))
        pantalla.blit(fondo, (barra_x, barra_y))

        salud_ancho = int(barra_ancho * (colono.salud / 100))

        if colono.salud > 70:
            color_salud = (100, 255, 100)
        elif colono.salud > 40:
            color_salud = (255, 200, 50)
        else:
            color_salud = (255, 50, 50)

        barra_salud = pygame.Surface((salud_ancho, barra_alto), pygame.SRCALPHA)
        barra_salud.fill((*color_salud, 220))
        pantalla.blit(barra_salud, (barra_x, barra_y))

    def _dibujar_indicador_trabajo(self, pantalla, rect, zoom):
        radio = max(2, int(4 * zoom))
        pos_x = rect.right - radio - 2
        pos_y = rect.top + radio + 2

        tiempo = pygame.time.get_ticks()
        alpha = int(abs(math.sin(tiempo / 200)) * 150 + 105)

        circulo = pygame.Surface((radio * 2 + 2, radio * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(circulo, (255, 200, 0, alpha), (radio + 1, radio + 1), radio)
        pantalla.blit(circulo, (pos_x - radio - 1, pos_y - radio - 1))