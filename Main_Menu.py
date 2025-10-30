import pygame
import sys
from random import uniform
from panel_control import PanelControl

def main_menu():
    """Menú principal que ejecuta el juego al presionar 'Jugar'"""
    # Inicialización
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    W, H = screen.get_size()
    pygame.display.set_caption("TerraForm Main Menu")
    clock = pygame.time.Clock()
    
    # Colores
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    PURPLE = (83, 53, 227)
    RED = (209, 65, 38)
    PURPLE_DARK = (65, 44, 168)
    RED_DARK = (166, 49, 27)
    
    # Música
    try:
        pygame.mixer.music.load("Assets/Musica/space_suspense.ogg")
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play(-1)
    except:
        print("[AVISO] No se pudo cargar la música")
    
    # Estrellas
    stars = [[uniform(0, W), uniform(0, H)] for _ in range(90)]
    STAR_SPEED = H * 0.036
    STAR_SIZE = max(2, int(H * 0.004))
    
    # Título
    try:
        title_img = pygame.image.load("Assets/Titulo/TerraFormpl.png").convert_alpha()
        title_h = int(H * 0.65)
        title_w = int(title_h * title_img.get_width() / title_img.get_height())
        title_img = pygame.transform.smoothscale(title_img, (title_w, title_h))
        title_rect = title_img.get_rect(center=(W // 2, int(H * 0.28)))
    except:
        title_img = None
        print("[AVISO] No se pudo cargar el título")
    
    # Botones
    BTN_W = int(W * 0.20)
    BTN_H = int(H * 0.10)
    BTN_RADIUS = 15
    btn_play = pygame.Rect(W // 2 - BTN_W // 2, int(H * 0.64), BTN_W, BTN_H)
    btn_exit = pygame.Rect(W // 2 - BTN_W // 2, int(H * 0.80), BTN_W, BTN_H)
    font = pygame.font.SysFont(None, int(BTN_H * 0.55))
    
    def draw_button(rect, color, color_hover, text, mouse_pos):
        color_final = color_hover if rect.collidepoint(mouse_pos) else color
        pygame.draw.rect(screen, color_final, rect, border_radius=BTN_RADIUS)
        text_surf = font.render(text, True, BLACK)
        screen.blit(text_surf, text_surf.get_rect(center=rect.center))
    
    def update_stars(dt):
        for star in stars:
            star[1] += STAR_SPEED * dt
            if star[1] > H:
                star[1] = 0
                star[0] = uniform(0, W)
    
    def draw_stars():
        for x, y in stars:
            pygame.draw.rect(screen, WHITE, (int(x), int(y), STAR_SIZE, STAR_SIZE))
    
    # Loop principal del menú
    running = True
    start_cinematic = False
    fade_alpha = 255
    
    while running:
        dt = clock.tick(60) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_play.collidepoint(event.pos):
                    start_cinematic = True
                elif btn_exit.collidepoint(event.pos):
                    running = False
        
        # Actualizar estrellas
        update_stars(dt)
        
        # Dibujar
        screen.fill(BLACK)
        draw_stars()
        
        # Fade out del menú
        if start_cinematic:
            fade_alpha -= 200 * dt
            if fade_alpha <= 0:
                fade_alpha = 0
                running = False
        
        # Dibujar título y botones con fade
        if title_img and fade_alpha > 0:
            temp_title = title_img.copy()
            temp_title.set_alpha(int(fade_alpha))
            screen.blit(temp_title, title_rect)
        
        if fade_alpha > 0:
            # Crear superficies temporales para los botones con alpha
            btn_surface = pygame.Surface((W, H), pygame.SRCALPHA)
            
            # Dibujar botones en superficie temporal
            color_play = PURPLE_DARK if btn_play.collidepoint(mouse_pos) else PURPLE
            color_exit = RED_DARK if btn_exit.collidepoint(mouse_pos) else RED
            
            pygame.draw.rect(btn_surface, (*color_play, int(fade_alpha)), btn_play, border_radius=BTN_RADIUS)
            pygame.draw.rect(btn_surface, (*color_exit, int(fade_alpha)), btn_exit, border_radius=BTN_RADIUS)
            
            text_play = font.render("Jugar", True, (*BLACK, int(fade_alpha)))
            text_exit = font.render("Salir", True, (*BLACK, int(fade_alpha)))
            
            btn_surface.blit(text_play, text_play.get_rect(center=btn_play.center))
            btn_surface.blit(text_exit, text_exit.get_rect(center=btn_exit.center))
            
            screen.blit(btn_surface, (0, 0))
        
        pygame.display.flip()
    
    # Si se inició la cinemática, mostrarla
    if start_cinematic:
        show_cinematics(screen, W, H, stars, STAR_SPEED, STAR_SIZE, clock)
    else:
        pygame.quit()
        sys.exit()


def show_cinematics(screen, W, H, stars, STAR_SPEED, STAR_SIZE, clock):
    # Configuración de cinemáticas
    cinematics = [
        {"image": "Assets/Cinematicas/Cinematica1.png", "text": "Hace mucho tiempo, la humanidad habitó un mundo que parecía eterno. Un lugar donde la vida florecía sin límites, donde el cielo y la tierra respiraban al mismo ritmo. Aquel paraíso, origen de todo lo que somos, fue llamado… la Tierra."},
        {"image": "Assets/Cinematicas/Cinematica2.png", "text": "Pero el ser humano nunca conoció los límites. Su ambición desmedida lo llevó a devorar su propio paraíso, a consumir hasta el último aliento de la Tierra. Y con cada recurso perdido… también extinguió la vida y la belleza que alguna vez lo cobijaron."},
        {"image": "Assets/Cinematicas/Cinematica3.png", "text": "Como último intento por sobrevivir, la humanidad envió a siete astronautas en una misión desesperada: encontrar un nuevo hogar, un planeta capaz de proteger lo poco que quedaba de su especie."},
        {"image": "Assets/Cinematicas/Cinematica4.png", "text": "Después de doce años de viaje, los siete astronautas llegaron a su destino. Un planeta nuevo, lleno de potencial y riesgos. Lo llamaron Lazarus. Aquí comienza la nueva oportunidad de la humanidad… ¿podrá la humanidad salvarse esta vez?"}
    ]
    
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    
    # Cargar imágenes de cinemáticas
    cinematic_images = []
    for cin in cinematics:
        try:
            img = pygame.image.load(cin["image"]).convert_alpha()
            img_h = int(H * 0.6)
            img_w = int(img_h * img.get_width() / img.get_height())
            img = pygame.transform.smoothscale(img, (img_w, img_h))
            cinematic_images.append(img)
        except:
            print(f"[AVISO] No se pudo cargar {cin['image']}")
            cinematic_images.append(None)
    
    # Configuración del recuadro de texto
    text_box_height = int(H * 0.18)
    text_box_y = int(H * 0.73)
    text_box_rect = pygame.Rect(int(W * 0.1), text_box_y, int(W * 0.8), text_box_height)
    text_font = pygame.font.SysFont(None, int(H * 0.035))
    line_spacing = int(H * 0.042)
    
    def wrap_text(text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def update_stars(dt):
        for star in stars:
            star[1] += STAR_SPEED * dt
            if star[1] > H:
                star[1] = 0
                star[0] = uniform(0, W)
    
    def draw_stars():
        for x, y in stars:
            pygame.draw.rect(screen, WHITE, (int(x), int(y), STAR_SIZE, STAR_SIZE))
    
    # Loop de cinemáticas
    current_cinematic = 0
    fade_in_alpha = 0
    text_progress = 0
    text_speed = 30  # caracteres por segundo
    all_complete = False
    
    running = True
    while running and current_cinematic < len(cinematics):
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # Si las animaciones no han terminado, completarlas todas
                if not all_complete:
                    fade_in_alpha = 255
                    text_progress = len(cinematics[current_cinematic]["text"])
                    all_complete = True
                # Si todo está completo, pasar a la siguiente cinemática
                else:
                    current_cinematic += 1
                    # Verificar si hay más cinemáticas
                    if current_cinematic >= len(cinematics):
                        running = False
                    else:
                        fade_in_alpha = 0
                        text_progress = 0
                        all_complete = False
        
        # Procesar si aún hay cinemáticas por mostrar
        if current_cinematic < len(cinematics):
            # Actualizar estrellas
            update_stars(dt)
            
            # Fade in de la imagen
            if fade_in_alpha < 255:
                fade_in_alpha += 150 * dt
                if fade_in_alpha >= 255:
                    fade_in_alpha = 255
            
            # Progreso del texto
            if text_progress < len(cinematics[current_cinematic]["text"]):
                text_progress += text_speed * dt
                if text_progress >= len(cinematics[current_cinematic]["text"]):
                    text_progress = len(cinematics[current_cinematic]["text"])
            
            # Verificar si todo está completo
            if fade_in_alpha >= 255 and text_progress >= len(cinematics[current_cinematic]["text"]):
                all_complete = True
            
            # Dibujar
            screen.fill(BLACK)
            draw_stars()
            
            # Dibujar imagen de cinemática con fade in
            if cinematic_images[current_cinematic]:
                img = cinematic_images[current_cinematic].copy()
                img.set_alpha(int(fade_in_alpha))
                img_rect = img.get_rect(center=(W // 2, int(H * 0.35)))
                screen.blit(img, img_rect)
            
            # Dibujar recuadro de texto
            pygame.draw.rect(screen, BLACK, text_box_rect)
            pygame.draw.rect(screen, WHITE, text_box_rect, 2)
            
            # Obtener texto progresivo y dividirlo en líneas
            current_text = cinematics[current_cinematic]["text"][:int(text_progress)]
            max_text_width = text_box_rect.width - int(W * 0.04)
            lines = wrap_text(current_text, text_font, max_text_width)
            
            # Dibujar cada línea de texto
            y_offset = text_box_rect.y + int(H * 0.02)
            for line in lines:
                text_surf = text_font.render(line, True, WHITE)
                text_x = text_box_rect.x + int(W * 0.02)
                screen.blit(text_surf, (text_x, y_offset))
                y_offset += line_spacing
            
            pygame.display.flip()
    
    if running:
        pygame.mixer.music.stop()  # Detener música del menú
        iniciar_juego()
    else:
        iniciar_juego()


def iniciar_juego():
    """Inicia el juego principal"""
    print("🎮 Iniciando juego...")
    panel = PanelControl()
    panel.ejecutar()


if __name__ == "__main__":
    main_menu()
    


