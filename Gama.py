import pygame
import random
import sys  # Agregado para cerrar el programa limpiamente si hay error
import Constantes
from Personaje1 import Personaje
from Mustang import Mustang


def escalar_img(image, scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, (int(w * scale), int(h * scale)))


def cargar_imagenes(paths, size=None):
    imgs = []
    for p in paths:
        try:
            img = pygame.image.load(p).convert_alpha()
            if size:
                img = pygame.transform.scale(img, size)
            imgs.append(img)
        except Exception as e:
            print(f"ERROR: No se pudo cargar la imagen {p}. Detalle: {e}")
            continue
    return imgs

def pantalla_muerte(ventana):
    fuente_grande = pygame.font.SysFont(None, 72)
    fuente_peq = pygame.font.SysFont(None, 30)
    reloj_muerte = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    return False
 
        ventana.fill(Constantes.COLOR_BG)
        texto = fuente_grande.render("¡Has muerto!", True, (255, 0, 0))
        subt = fuente_peq.render("Presiona R para reiniciar  Q o ESC para salir", True, (255, 255, 255))
        ventana.blit(texto, texto.get_rect(center=(Constantes.ANCHO//2, Constantes.ALTO//2 - 30)))
        ventana.blit(subt, subt.get_rect(center=(Constantes.ANCHO//2, Constantes.ALTO//2 + 30)))
        pygame.display.update()
        reloj_muerte.tick(30)

def pantalla_inicio():
    ventana = pygame.display.set_mode((Constantes.ANCHO, Constantes.ALTO))
    pygame.display.set_caption("RunPy - Pantalla de Inicio")
    fuente_titulo = pygame.font.SysFont(None, 100)
    fuente_boton = pygame.font.SysFont(None, 50)
    fuente_peq = pygame.font.SysFont(None, 32)
    clock = pygame.time.Clock()
    botones = []
    # Definir botones de nivel y salir
    for i in range(5):
        rect = pygame.Rect(Constantes.ANCHO//2 - 120, 220 + i*90, 240, 60)
        botones.append((rect, f"Nivel {i+1}"))
    boton_salir = pygame.Rect(Constantes.ANCHO//2 - 120, 220 + 5*90, 240, 60)
    mensaje_no_disp = "Nivel no disponible"
    mostrar_mensaje = False
    mensaje_timer = 0
    while True:
        ventana.fill((30, 30, 60))
        # Título
        texto = fuente_titulo.render("RunPy", True, (255, 255, 0))
        ventana.blit(texto, texto.get_rect(center=(Constantes.ANCHO//2, 120)))
        # Botones de nivel
        for variable, (rect, label) in enumerate(botones):
            color = (0, 180, 0) if variable == 0 else (80, 80, 80)
            pygame.draw.rect(ventana, color, rect, border_radius=12)
            txt = fuente_boton.render(label, True, (255,255,255))
            ventana.blit(txt, txt.get_rect(center=rect.center))
        # Botón salir
        pygame.draw.rect(ventana, (180,0,0), boton_salir, border_radius=12)
        txt_salir = fuente_boton.render("Salir", True, (255,255,255))
        ventana.blit(txt_salir, txt_salir.get_rect(center=boton_salir.center))
        # Mensaje de nivel no disponible
        if mostrar_mensaje:
            msg = fuente_peq.render(mensaje_no_disp, True, (255,80,80))
            ventana.blit(msg, msg.get_rect(center=(Constantes.ANCHO//2, Constantes.ALTO-80)))
            if pygame.time.get_ticks() - mensaje_timer > 1200:
                mostrar_mensaje = False
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "salir"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for variable, (rect, _) in enumerate(botones):
                    if rect.collidepoint(mx, my):
                        if variable == 0:
                            return "nivel1"
                        else:
                            mostrar_mensaje = True
                            mensaje_timer = pygame.time.get_ticks()
                if boton_salir.collidepoint(mx, my):
                    return "salir"
        clock.tick(60)

# --- BUCLE PRINCIPAL DEL JUEGO ---
def game_loop():
    ventana = pygame.display.set_mode((Constantes.ANCHO, Constantes.ALTO))
    pygame.display.set_caption("RunPy")

    ruta_musica = "assets/Musica.mp3" 
    try:
        pygame.mixer.music.load(ruta_musica)
        pygame.mixer.music.set_volume(0.5) # Volumen al 50%
        pygame.mixer.music.play(-1) # -1 significa loop infinito
    except Exception as e:
        print(f"AVISO: No se pudo cargar la música en '{ruta_musica}'. Error: {e}")

    # Cargar Fondo
    try:
        imagen_fondo = pygame.image.load("assets/images/calle.PNG")
        imagen_fondo = pygame.transform.scale(imagen_fondo, (Constantes.ANCHO, Constantes.ALTO))
    except Exception as e:
        print(f"ERROR CRÍTICO: No se encontró el fondo. {e}")
        return False # Salir si no hay fondo

    # Cargar Corazones
    img_corazon_lleno = None
    img_corazon_vacio = None
    try:
        raw_lleno = pygame.image.load("assets/Corazon.png")
        raw_vacio = pygame.image.load("assets/Sinvida.png")
        img_corazon_lleno = pygame.transform.scale(raw_lleno, (70, 70))
        img_corazon_vacio = pygame.transform.scale(raw_vacio, (70, 70))
    except Exception as e:
        print(f"ADVERTENCIA: No se cargaron corazones. {e}")

    # Cargar frames de coches (sprites)
    car_images = [
        "assets/images/Carro0.png",
        "assets/images/Carro1.png",
        "assets/images/Carro2.png",
        "assets/images/Carro3.png",
    ]
    car_w, car_h = 180, 160
    car_frames = cargar_imagenes(car_images, size=(car_w, car_h))

    # Cargar Personaje 
    animaciones = []
    try:
        for i in range(6):
            ruta_personaje = f"assets/images/characters/sprite{i}.png"
            img = pygame.image.load(ruta_personaje)
            img = escalar_img(img, Constantes.SCALA_PERSONAJE)
            animaciones.append(img)
    except Exception as e:
        print(f"ERROR CRÍTICO: Falló la carga del personaje. Detalle: {e}")
        return False 

    # VERIFICACIÓN DE SEGURIDAD
    if len(animaciones) == 0:
        print("ERROR FATAL: La lista de animaciones está vacía.")
        return False

    suelo_inicial_y = 680
    # Calcular offsets para la hitbox
    if animaciones and len(animaciones) > 0:
        sprite_h = animaciones[0].get_height()
        offset_bottom = sprite_h // 4
    else:
        offset_bottom = 0
        
    jugador = Personaje(50, suelo_inicial_y, animaciones, hitbox_offset_x=0, hitbox_offset_bottom=offset_bottom)

    lista_mustangs = []         
    tiempo_ultimo_spawn = 0     
    frecuencia_spawn = 700     

    mover_arriba = False
    mover_abajo = False
    mover_izquierda = False
    mover_derecha = False
    saltar = False

    max_vidas = 3
    vidas = max_vidas
    hit_cooldown_ms = 1000  
    last_hit_time = -hit_cooldown_ms


    tiempo_limite = 15 # Segundos que dura el nivel
    tiempo_inicio = pygame.time.get_ticks()
    fuente_timer = pygame.font.SysFont(None, 40)
    tiempo_agotado = False # Bandera para saber si salimos por tiempo

    reloj = pygame.time.Clock()
    run = True

    while run:
        reloj.tick(Constantes.FPS)

        # 1. Lógica de Scroll del Fondo
        if mover_derecha:
            Constantes.scroll_x -= Constantes.scroll_speed
        if abs(Constantes.scroll_x) > Constantes.ANCHO:
            Constantes.scroll_x = 0

        # 2. Dibujar Fondo
        if imagen_fondo:
            ventana.blit(imagen_fondo, (Constantes.scroll_x, 0))
            ventana.blit(imagen_fondo, (Constantes.scroll_x + Constantes.ANCHO, 0))
        else:
            ventana.fill(Constantes.COLOR_BG)

        ahora = pygame.time.get_ticks()
        
        # 3. Movimiento del Jugador
        delta_x = 0
        delta_y = 0

        if not jugador.en_el_aire:
            if mover_arriba: delta_y = -5
            if mover_abajo: delta_y = 5

        if saltar:
            jugador.salto()

        if ahora - tiempo_ultimo_spawn > frecuencia_spawn:
            carril = random.choice(["arriba", "abajo"])
            if carril == "arriba":
                nuevo_obs = Mustang(Constantes.ANCHO, 400, -10, ancho=car_w, alto=car_h, frames=car_frames)
            else:
                nuevo_obs = Mustang(-50, 450, 5, ancho=car_w, alto=car_h, frames=car_frames)
            lista_mustangs.append(nuevo_obs)
            tiempo_ultimo_spawn = ahora

        for obs in lista_mustangs[:]:
            obs.dibujar(ventana)
            obs.movimiento()
            if obs.velocidad < 0 and obs.x + obs.ancho < 0:
                lista_mustangs.remove(obs)
            elif obs.velocidad > 0 and obs.x > Constantes.ANCHO:
                lista_mustangs.remove(obs)

        jugador.corriendo = mover_izquierda or mover_derecha
        jugador.movimiento(delta_x, delta_y)
        jugador.update()
        jugador.dibujar(ventana)

        # Condición de Muerte por Altura
        if jugador.forma.y <= 450 and not jugador.en_el_aire:

            run = False  

        # 6. Eventos de Teclado
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d: mover_derecha = True
                if event.key == pygame.K_w: mover_arriba = True
                if event.key == pygame.K_s: mover_abajo = True
                if event.key == pygame.K_SPACE: saltar = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d: mover_derecha = False
                if event.key == pygame.K_w: mover_arriba = False
                if event.key == pygame.K_s: mover_abajo = False
                if event.key == pygame.K_SPACE: saltar = False
        
        # 7. HUD Vidas
        for i in range(max_vidas):
            x = 10 + i * 80
            y = 10
            imagen_a_dibujar = img_corazon_lleno if i < vidas else img_corazon_vacio
            if imagen_a_dibujar:
                ventana.blit(imagen_a_dibujar, (x, y))
            else:
                color = (255, 0, 0) if i < vidas else (100, 100, 100)
                pygame.draw.rect(ventana, color, (x, y, 40, 40))

        # --- NUEVO: HUD Temporizador y Lógica de Fin de Tiempo ---
        segundos_transcurridos = (ahora - tiempo_inicio) / 1000
        tiempo_restante = max(0, tiempo_limite - int(segundos_transcurridos))
        
        txt_timer = fuente_timer.render(f"Tiempo: {tiempo_restante}s", True, (255, 255, 255))
        ventana.blit(txt_timer, (Constantes.ANCHO - 200, 20))

        if tiempo_restante <= 0:
            tiempo_agotado = True
            run = False

        pygame.display.update()

    pygame.mixer.music.stop() # Detener música al salir

    if tiempo_agotado:
        # Si se acabó el tiempo, regresamos False para volver al menú de inicio
        return False
    else:
        # Si murió (por altura u otra razón), mostramos pantalla de muerte
        return pantalla_muerte(ventana)

if __name__ == "__main__":
    try:
        pygame.init()
        # Inicializar mixer explícitamente por si acaso
        pygame.mixer.init()
        while True:
            accion = pantalla_inicio()
            if accion == "nivel1":
                while True:
                    reiniciar = game_loop()
                    if not reiniciar:
                        break
                    Constantes.scroll_x = 0
            elif accion == "salir":
                break
    finally:
        pygame.quit()