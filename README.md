Introduccion
Propósito del Programa
El programa es un juego llamado "Mario Pygame" desarrollado en Python utilizando la biblioteca Pygame. El objetivo del juego es controlar un personaje para moverse a través de un mundo, enfrentarse a enemigos y superar obstáculos.
1.2 Requisitos
•	Python 3.x
•	Pygame
2. Estructura del Código
2.1 Importación de Bibliotecas
import os
import sys
import random
import math
import pygame
import numpy as np
import cv2
Estas importaciones permiten utilizar funcionalidades de Pygame, manejo del sistema, generación de números aleatorios, operaciones matemáticas avanzadas, manipulación de imágenes y procesamiento de video.
2.2 Inicialización y Configuración
pygame.init()
ANCHO, ALTO = 800, 600
GRIS = (50, 50, 50)
BLANCO = (255, 255, 255)
pygame.display.set_caption("Mario Pygame")
Estas líneas inicializan Pygame y definen constantes para el tamaño de la pantalla y los colores utilizados en el juego.
2.3 Configuración de la Pantalla y Recursos
ventana = pygame.display.set_mode((ANCHO, ALTO))
fondo_img = pygame.image.load(os.path.join("Assets", "Background", "blue.png")).convert()
Se configura la pantalla del juego y se carga la imagen de fondo.
2.4 Fuentes y Sonidos
No se mencionan específicamente fuentes y sonidos en el código proporcionado.
2.5 Variables de Estado del Juego
INICIO = 0
JUGANDO = 1
PAUSA = 2
estado = INICIO
Se definen los diferentes estados del juego y las variables que almacenan el estado actual del juego.
3. Funciones
3.1 Funciones de Utilidad
def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)
Esta función dibuja las vidas restantes en la pantalla utilizando una imagen de corazón.
4. Clases
4.1 Clase Enemy
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = self.load_enemy_image("Assets/MainCharacters/Mushroom", 16, 16)
        self.x_vel = 1
        self.y_vel = 0
        self.mask = pygame.mask.from_surface(self.image)

    def load_enemy_image(self, path, width, height):
        image = pygame.image.load(os.path.join(path, random.choice(os.listdir(path)))).convert_alpha()
        return pygame.transform.scale(image, (width, height))

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def update(self):
        self.move(self.x_vel, self.y_vel)
La clase Enemy representa un enemigo en el juego, incluyendo su movimiento y actualización de sprites.
5. Funciones Auxiliares
5.1 Manejo de Colisiones
def handle_vertical_collision_enemy(sprite, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(sprite, obj):
            if dy > 0:
                sprite.rect.bottom = obj.rect.top
                sprite.y_vel = 0
            elif dy < 0:
                sprite.rect.top = obj.rect.bottom
                sprite.y_vel = 0
            collided_objects.append(obj)
    return collided_objects
Esta función maneja las colisiones verticales de un enemigo con los objetos del juego.
6. Pantallas del Juego
6.1 Menú Principal
def main_menu():
    run = True
    while run:
        ventana.fill(GRIS)
        draw_text(ventana, "Mario Pygame", 100, BLANCO, ANCHO//2, ALTO//4)
        draw_buttons(ventana, "Play", 200, 50, ANCHO//2 - 100, ALTO//2, BLANCO, GRIS)
        draw_buttons(ventana, "Quit", 200, 50, ANCHO//2 - 100, ALTO//2 + 60, BLANCO, GRIS)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    run = False
                    main()
                if quit_button.collidepoint(event.pos):
                    run = False
        pygame.display.update()
    pygame.quit()
    sys.exit()
Esta función muestra el menú principal del juego, donde se puede iniciar el juego o salir.
7. Bucle Principal del Juego
El bucle principal del juego se encarga de gestionar el estado del juego, actualizar los sprites y gestionar los eventos del usuario.
def main():
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        ventana.fill(GRIS)
        # Actualizar y dibujar todos los sprites del juego
        pygame.display.flip()
        pygame.time.Clock().tick(60)
    pygame.quit()
    sys.exit()

main_menu()
8. Conclusión
El código del juego "Mario Pygame" está estructurado para manejar diferentes estados de juego y actualizar los elementos de la pantalla en consecuencia. La interacción del usuario se gestiona a través de eventos de teclado y ratón, proporcionando una experiencia de juego fluida y reactiva.
