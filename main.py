import pygame
import sys
import random

# Inicialización de Pygame
pygame.init()

# Configuración de pantalla
ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Rana vs Polis")

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE = (0, 255, 0)
ORO = (255,191,0)

# Carga de imágenes
fondo = pygame.image.load("assets/carretera.jpeg")
rana = pygame.image.load("assets/rana.png")
coche = pygame.image.load("assets/cochepolicia.png")
moneda = pygame.image.load("assets/bitcoin.png")


# Escalado de imágenes
rana = pygame.transform.scale(rana, (50, 50))
coche = pygame.transform.scale(coche, (100, 70))
moneda = pygame.transform.scale(moneda, (30, 30))
fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

# Carga de sonidos
pygame.mixer.music.load("assets/musica_fondo.mp3")  # Música de fondo
sonido_perder = pygame.mixer.Sound("assets/perder.wav")  # Sonido al perder
sonido_ganar = pygame.mixer.Sound("assets/ganar.wav")  # Sonido al ganar
sonido_moneda = pygame.mixer.Sound("assets/getCoin.wav")
sonido_mascoches = pygame.mixer.Sound("assets/newLevel.wav")
sonido_startgame = pygame.mixer.Sound("assets/startgame.wav")  # Sonido de inicio

# Fuente
fuente_arcade = pygame.font.Font("assets/PressStart2P.ttf", 23)
fuente_arcade_small = pygame.font.Font("assets/PressStart2P.ttf", 15)

# FPS
reloj = pygame.time.Clock()
FPS = 60

# Función para mostrar texto en pantalla
def mostrar_texto(texto, x, y, color=BLANCO):
    render = fuente_arcade.render(texto, True, color)
    pantalla.blit(render, (x, y))

# Pantalla de inicio
def pantalla_inicio():
    # Cargar imagen de inicio
    imagen_inicio = pygame.image.load("assets/startgame.png")
    imagen_inicio = pygame.transform.scale(imagen_inicio, (ANCHO, ALTO))
    pantalla.blit(imagen_inicio, (0, 0))

    # Mensaje de inicio
    texto_inicio = fuente_arcade.render("PRESIONA UNA TECLA PARA COMENZAR", True, BLANCO)
    texto_rect = texto_inicio.get_rect(center=(ANCHO // 2, ALTO - 50))
    pantalla.blit(texto_inicio, texto_rect)

    pygame.display.flip()

    # Reproducir el sonido de inicio
    sonido_startgame.play()

    esperar_tecla()

# Función para la pantalla final
def pantalla_final(resultado, puntos):
    # Determinar imagen y texto según el resultado
    if resultado == "ganar":
        imagen_final = pygame.image.load("assets/winner.png")
        mensaje = "¡HAS GANADO!"
    else:
        imagen_final = pygame.image.load("assets/gameover.png")
        mensaje = "GAME OVER"
        puntos = 0 # Se pierde todo si es game over

    imagen_final = pygame.transform.scale(imagen_final, (ANCHO, ALTO))
    pantalla.blit(imagen_final, (0, 0))

    # Mostrar mensaje final
    texto_final = fuente_arcade.render(mensaje, True, BLANCO)
    texto_rect = texto_final.get_rect(center=(ANCHO // 2, ALTO - 100))
    pantalla.blit(texto_final, texto_rect)

    # Mostrar puntos solo si el resultado es "ganar"
    if resultado == "ganar":
        texto_puntos = fuente_arcade.render(f"Puntos: {puntos}", True, ORO)
        texto_puntos_rect = texto_puntos.get_rect(center=(ANCHO // 2, ALTO - 80))
        pantalla.blit(texto_puntos, texto_puntos_rect)

    # Mostrar mensaje de salida
    texto_salida = fuente_arcade_small.render("PRESIONA R PARA REINICIAR O ESC PARA SALIR", True, BLANCO)
    texto_salida_rect = texto_salida.get_rect(center=(ANCHO // 2, ALTO - 50))
    pantalla.blit(texto_salida, texto_salida_rect)

    pygame.display.flip()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    juego()  # Reiniciar el juego
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

# Esperar a que el jugador pulse una tecla
def esperar_tecla():
    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                esperando = False

# Función para crear un coche
def crear_coche_sin_solapamiento(obstaculos):
    max_intentos = 10
    for _ in range(max_intentos):
        x = random.randint(-100, -50) # Fuera de la pantalla por la izquierda
        y = random.randint(100, 300) # Solo dentro del área de la carretera
        nuevo_coche = pygame.Rect(x, y, 100, 70)

        # Verificar que no se solape con los coches existentes
        if not any(nuevo_coche.colliderect(coche) for coche in obstaculos):
            return nuevo_coche

    # Si no encuentra espacio después de varios intentos, devolver None
    return None

# Función para crear una moneda en posición aleatoria
def crear_moneda():
    x = random.randint(0, ANCHO - 30)
    y = random.randint(50, ALTO - 100)  # Dentro de un rango visible
    return pygame.Rect(x, y, 30, 30)

# Juego principal
def juego():
    # Coordenadas iniciales de la rana
    rana_x, rana_y = ANCHO // 2, ALTO - 60
    velocidad_rana = 5

    # Lista de obstáculos (coches) y monedas
    obstaculos = []
    monedas = []
    velocidad_coche = 3
    spawn_rate_coche = 60 # Valor inicial (más grande = menos coches)
    spawn_rate_moneda = 150 # Reducimos la frecuencia de aparición

    # Contador de puntos
    puntos = 0
    dificultad_mostrada = False  # Para controlar el mensaje de dificultad


    # Reproducir música de fondo
    pygame.mixer.music.play(-1)  # -1 para repetir indefinidamente

    juego_activo = True
    while juego_activo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Controles de la rana
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_UP] and rana_y > 0:
            rana_y -= velocidad_rana
        if teclas[pygame.K_DOWN] and rana_y < ALTO - 50:
            rana_y += velocidad_rana
        if teclas[pygame.K_LEFT] and rana_x > 0:
            rana_x -= velocidad_rana
        if teclas[pygame.K_RIGHT] and rana_x < ANCHO - 50:
            rana_x += velocidad_rana

        # Generar coches
        if random.randint(1, spawn_rate_coche) == 1:
            nuevo_coche = crear_coche_sin_solapamiento(obstaculos)
            if nuevo_coche:  # Solo añadir si no es None
                obstaculos.append(nuevo_coche)

        # Generar monedas
        if random.randint(1, spawn_rate_moneda) == 1:
            monedas.append(crear_moneda())

        # Movimiento de coches
        for coche_rect in obstaculos:
            coche_rect.x += velocidad_coche

        # Eliminar coches fuera de pantalla
        obstaculos = [c for c in obstaculos if c.x < ANCHO]

        # Detectar colisiones
        rana_rect = pygame.Rect(rana_x, rana_y, 50, 50).inflate(-10,-10) # inflate(width, height) reduce o amplía el tamaño del rectángulo. -10 para colisiones mas suaves
        for coche_rect in obstaculos:
            coche_rect_reducido = coche_rect.inflate(-10, -10) # reducimos el cuadrado para hacer colisiones mas permisivas
            if rana_rect.colliderect(coche_rect_reducido):
                pygame.mixer.music.stop()
                sonido_perder.play()
                pantalla_final("perder", puntos)
                return # Salir del juego tras perder

        # Detectar colisiones con monedas
        nuevas_monedas = []
        for moneda_rect in monedas:
           if rana_rect.colliderect(moneda_rect):
             puntos += 10
             sonido_moneda.play()  # Reproducir sonido al recoger una moneda
           else:
             nuevas_monedas.append(moneda_rect)
        monedas = nuevas_monedas

        # Incrementar dificultad según puntos
        if puntos % 100 == 0 and puntos > 0:
            if not dificultad_mostrada:
                spawn_rate_coche = max(10, spawn_rate_coche - 5)  # Reducir spawn rate
                velocidad_coche += 0.5  # Incrementar velocidad de los coches
                dificultad_mostrada = True

                # Fuente más grande para el mensaje
                fuente_grande = pygame.font.Font("assets/PressStart2P.ttf", 30)
                texto = fuente_grande.render("¡Más polis en camino!", True, BLANCO)

                # Centrar el texto
                texto_rect = texto.get_rect(center=(ANCHO // 2, ALTO // 2))

                # Mostrar mensaje temporal
                pantalla.blit(fondo, (0, 0)) # Redibujar fondo
                pantalla.blit(rana, (rana_x, rana_y))  # Redibujar la rana

                for coche_rect in obstaculos:
                    pantalla.blit(coche, coche_rect) # Redibujar coches
                for moneda_rect in monedas:
                    pantalla.blit(moneda, moneda_rect) # Redibujar monedas

                pantalla.blit(texto, texto_rect)  # Mostrar mensaje centrado
                sonido_mascoches.play()
                pygame.display.flip()

                # Usar un temporizador en lugar de delay
                tiempo_inicio = pygame.time.get_ticks()
                while pygame.time.get_ticks() - tiempo_inicio < 1000:  # 1000 ms = 1 segundo
                    for evento in pygame.event.get():
                        if evento.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()


        if puntos % 100 != 0:
            dificultad_mostrada = False

        # Condición de victoria
        if rana_y <= 0:
            pygame.mixer.music.stop()
            sonido_ganar.play()
            pantalla_final("ganar", puntos)
            return

        # Dibujar todo
        pantalla.blit(fondo, (0, 0))
        pantalla.blit(rana, (rana_x, rana_y))

        for coche_rect in obstaculos:
            pantalla.blit(coche, coche_rect)
        for moneda_rect in monedas:
            pantalla.blit(moneda, moneda_rect)

        # Mostrar el contador de puntos
        mostrar_texto(f"Puntos: {puntos}", 10, 10)

        # Actualizar pantalla
        pygame.display.flip()
        reloj.tick(FPS)

# Ejecución
pantalla_inicio()
juego()
pygame.quit()
