import os
import sys
import random
import math
import pygame
import numpy as np
import cv2
from os import listdir
from os.path import isfile, join
from pygame.surfarray import array3d, pixels3d

pygame.init()


heart_image = pygame.image.load("assets/Menu/heart.png")
heart_image = pygame.transform.scale(heart_image, (30, 30))
font = pygame.font.Font(None, 36)

level1pass = False
level2pass = False
level3pass = False

pygame.display.set_caption("Mayti's Adventure")

WIDTH, HEIGHT = 1024, 720
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
# Cargar y reproducir música en bucle # Reemplaza con la ruta a tu archivo de música
pygame.mixer.music.set_volume(0.4) # Establecer el volumen al 10% # -1 para reproducir en bucle indefinidamente

def draw_lives(window, lives):
    for i in range(lives):
        window.blit(heart_image, (10 + i * 35, 10))  # Dibuja el texto en la esquina superior izquierda

def blur_surf(surface, radius):
    if radius < 1:
        return surface

    array = array3d(surface)
    array = array.astype(np.float32)

    kernel_size = 2 * radius + 1
    kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size * kernel_size)

    # Aplicar el kernel de desenfoque a cada canal
    for i in range(3):  # Canales RGB
        array[..., i] = cv2.filter2D(array[..., i], -1, kernel)

    array = np.clip(array, 0, 255).astype(np.uint8)

    blurred_surface = pygame.Surface(surface.get_size())
    pixels3d(blurred_surface)[:] = array

    return blurred_surface

def draw_buttons():
    # Cargar la imagen del logo
    logo_image = pygame.image.load("assets/Menu/maytilogo.png")
    logo_image = pygame.transform.scale(logo_image, (400, 250))
    logo_rect = logo_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 200))

    # Dibujar el logo
    window.blit(logo_image, logo_rect)
    # Cargar la imagen del botón "Play"
    play_button_image = pygame.image.load("assets\Menu\Buttons\Play.png")
    play_button_image = pygame.transform.scale(play_button_image, (100, 100))
    play_button_rect = play_button_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    
    # Dibujar el botón "Play"
    window.blit(play_button_image, play_button_rect)

    # Cargar la imagen del botón "Quit"
    quit_button_image = pygame.image.load("assets\Menu\Buttons\Close.png")
    quit_button_image = pygame.transform.scale(quit_button_image, (100, 100))
    quit_button_rect = quit_button_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

    # Dibujar el botón "Quit"
    window.blit(quit_button_image, quit_button_rect)

    return play_button_rect, quit_button_rect

def main_menu():
    pygame.mixer.music.load("assets/Music/ost/menu.mp3")
    pygame.mixer.music.play(-1)
    clock = pygame.time.Clock()
    run = True

    while run:
        window.fill(BLACK)
        play_button_rect, quit_button_rect = draw_buttons()
        
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if play_button_rect.collidepoint(mouse_pos):
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load("assets/Music/ost/level1.mp3")
                    pygame.mixer.music.play(-1)
                    main(window)
                elif quit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        clock.tick(FPS)

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

def get_block2(size):
    path = join("assets", "Terrain", "Terrain2.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

def get_block3(size):
    path = join("assets", "Terrain", "Terrain3.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

class Enemy(pygame.sprite.Sprite):
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Enemy", "NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height, move_range=(0, WIDTH)):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 2
        self.y_vel = 0
        self.mask = None
        self.direction = "right"
        self.animation_count = 0
        self.fall_count = 0
        self.sprite = self.SPRITES["idle_right"][0]  # Inicializar sprite
        self.mask = pygame.mask.from_surface(self.sprite)  # Inicializar máscara
        self.update()  # Asegurarse de que la máscara se actualice al inicio

        # Define the movement range for the enemy
        self.move_range = move_range
        self.initial_x = x  # Store the initial x position

    def loop(self, fps, objects):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(objects)
        self.update_sprite()
        self.fall_count += 1

    def move(self, objects):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel

        # Check if the enemy has moved beyond the defined range
        if self.rect.left < self.initial_x + self.move_range[0] or self.rect.right > self.initial_x + self.move_range[1]:
            self.x_vel = -self.x_vel
            self.direction = "left" if self.x_vel < 0 else "right"

        vertical_collide = handle_vertical_collision_enemy(self, objects, self.y_vel)
        if vertical_collide:
            self.fall_count = 0
            self.y_vel = 0

    def update_sprite(self):
        sprite_sheet = "run" if self.x_vel != 0 else "idle"
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

def handle_vertical_collision_enemy(sprite, objects, dy):
    collided_objects = []
    for obj in objects:
        if obj and obj.mask and sprite.mask and pygame.sprite.collide_mask(sprite, obj):
            if isinstance(obj, Block):
                if dy > 0:
                    sprite.rect.bottom = obj.rect.top
                elif dy < 0:
                    sprite.rect.top = obj.rect.bottom
                collided_objects.append(obj)
            
            if isinstance(obj, Block2):
                if dy > 0:
                    sprite.rect.bottom = obj.rect.top
                elif dy < 0:
                    sprite.rect.top = obj.rect.bottom
                collided_objects.append(obj)

            if isinstance(obj, Block3):
                if dy > 0:
                    sprite.rect.bottom = obj.rect.top
                elif dy < 0:
                    sprite.rect.top = obj.rect.bottom
                collided_objects.append(obj)
    return collided_objects


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "Mayti", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "right"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.lives = 3
        self.hiteffect = pygame.mixer.Sound('assets/Music/sfx/hit.mp3')
        self.jumpeffect = pygame.mixer.Sound('assets/Music/sfx/jump.mp3')

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        self.jumpeffect.play()
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        if not self.hit:
            self.hit = True
            self.hit_count = 0
            self.lives -= 1
            self.hiteffect.play()
            if self.lives <= 0:
                game_over_screen(window, True)  # Mostrar pantalla de Game Over y esperar a reiniciar

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
            if self.hit_count > fps * 0.5:
                self.hit = False
                self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Block2(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block2(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Block3(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block3(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class InvisibleBlock(Block):
    def __init__(self, x, y, size):
        super().__init__(x, y, size)
        self.image.fill((0, 0, 0, 0))  # Fill the image with transparency

    def draw(self, win, offset_x):
        # Override the draw method to avoid rendering the block
        pass # Fill the image with transparency


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

    def check_collision(self, player):
        if pygame.sprite.collide_mask(player, self):
            player.make_hit()

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image, enemies, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    for enemy in enemies:  # Dibujar cada enemigo
        enemy.draw(window, offset_x)

    player.draw(window, offset_x)

    # Dibujar las vidas del jugador
    draw_lives(window, player.lives)

    pygame.display.update()

def handle_vertical_collision(sprite, objects, dy):
    collided_objects = []
    for obj in objects:
        if obj and pygame.sprite.collide_mask(sprite, obj):
            if isinstance(obj, Block):
                if dy > 0:
                    sprite.rect.bottom = obj.rect.top
                    sprite.landed()
                elif dy < 0:
                    sprite.rect.top = obj.rect.bottom
                    sprite.hit_head()
                collided_objects.append(obj)
            
            if isinstance(obj, Block2):
                if dy > 0:
                    sprite.rect.bottom = obj.rect.top
                    sprite.landed()
                elif dy < 0:
                    sprite.rect.top = obj.rect.bottom
                    sprite.hit_head()
                collided_objects.append(obj)
            
            if isinstance(obj, Block3):
                if dy > 0:
                    sprite.rect.bottom = obj.rect.top
                    sprite.landed()
                elif dy < 0:
                    sprite.rect.top = obj.rect.bottom
                    sprite.hit_head()
                collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()

def reset_game():
    main(window)



def level1(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Brown.png")

    block_size = 96

    player_x = -1000
    player_y = HEIGHT - block_size - 50  # 50 es la altura del jugador

    player = Player(player_x, player_y, 50, 50)
    enemy_x = -800  # Centrado horizontalmente en la pantalla
    enemy_y = HEIGHT - block_size - 70  # A 70 píxeles por encima del borde inferior
    enemy = Enemy(enemy_x, enemy_y, 50, 50, move_range=(-80,70 ))

    enemy2_x = -400
    enemy2_y = HEIGHT - block_size - 70
    enemy2 = Enemy(enemy2_x, enemy2_y, 50, 50, move_range=(-100, 65))

    enemy3_x = -100
    enemy3_y = HEIGHT - block_size - 70
    enemy3 = Enemy(enemy3_x, enemy3_y, 50, 50, move_range=(-100, 65))

    # Enemigos
    enemies = [enemy, enemy2,enemy3]  # Añadir ambos enemigos a una lista
    
    # fuegos que estan encendidos
    fire1 = Fire(700, HEIGHT - block_size - 63, 16, 32)
    fire2 = Fire(300, HEIGHT - block_size - 63, 16, 32)
    fire3 = Fire(1100, HEIGHT - block_size - 63, 16, 32)
    fire4 = Fire(700, HEIGHT - block_size - 542, 16, 32)
    fire5 = Fire(300, HEIGHT - block_size - 350, 16, 32)
    fire6 = Fire(1100, HEIGHT - block_size - 350, 16, 32)
    fire20 = Fire(1960, HEIGHT - block_size - 63, 16, 32)
    fire22 = Fire(2340, HEIGHT - block_size - 350, 16, 32)
    fire23 = Fire(2720, HEIGHT - block_size - 350, 16, 32)
    
    # codigo para mostrar encendido el fuego, mostrar solo encendido los fuegos que se veran en pantalla
    fire1.on()
    fire2.on()
    fire3.on()
    fire4.on()
    fire5.on()
    fire6.on()
    fire20.on()
    fire22.on()
    fire23.on()

    floor = [
        Block(i * block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)
        if i not in [1, 5, 6, 9, 10, 13, 14, 15, 16, 17, 18, 19]
    ]

    objects = [*floor,
               # diseño de las plataformas iniciales
               Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 2, HEIGHT - block_size * 4, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size),
               Block(block_size * 4, HEIGHT - block_size * 4, block_size),
               Block(block_size * 5, HEIGHT - block_size * 5, block_size),
               Block(block_size * 6, HEIGHT - block_size * 6, block_size),
               Block(block_size * 7, HEIGHT - block_size * 6, block_size),
               Block(block_size * 8, HEIGHT - block_size * 6, block_size),
               Block(block_size * 11, HEIGHT - block_size * 4, block_size),
               Block(block_size * 12, HEIGHT - block_size * 4, block_size),
               Block(block_size * 14, HEIGHT - block_size * 2, block_size),

               # diseño parte tryhard
               Block(block_size * 17, HEIGHT - block_size * 4, block_size),
               Block(block_size * 21, HEIGHT - block_size * 4, block_size),
               Block(block_size * 24, HEIGHT - block_size * 4, block_size),
               Block(block_size * 25, HEIGHT - block_size * 4, block_size),
               Block(block_size * 28, HEIGHT - block_size * 4, block_size),
               Block(block_size * 29, HEIGHT - block_size * 4, block_size),

               # codigo para la columna del inicio
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 1, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 2, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 3, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 4, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 5, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 6, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 7, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 8, block_size),
               # colocacion de los fuegos en el mapa
               fire1, fire2, fire3, fire4, fire5, fire6, 
               fire20, fire22, fire23]

    offset_x = -1500
    scroll_area_width = 450

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()  # Cambiado: Salir del programa si se cierra la ventana
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)

        for enemy in enemies:
            enemy.loop(FPS, objects)  # Actualizar el estado de cada enemigo

        if player.rect.y > 800:
            game_over_screen(window, True)

        # Mostrar en loop solo los fuegos encendidos
        for fire in [fire1, fire2, fire3, fire4, fire5, fire6, fire20, fire22, fire23]:
            fire.loop()

        handle_move(player, objects)
        draw(window, background, bg_image, enemies, player, objects, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

        specific_y = HEIGHT - block_size * 4  # Ajusta este valor según sea necesario

        pygame.display.update()

        # loop para el chequeo de colisiones
        for firecheck in [fire1, fire2, fire3, fire4, fire5, fire6]:
            firecheck.check_collision(player)

        for enemy in enemies:
            if pygame.sprite.collide_mask(player, enemy):
                player.make_hit()

        if player.rect.x >= block_size * 29 and player.rect.y <= specific_y:
            victory_screen(window)
            return True

def draw(window, background, bg_image, enemies, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    for enemy in enemies:  # Dibujar cada enemigo
        enemy.draw(window, offset_x)

    player.draw(window, offset_x)

    # Dibujar las vidas del jugador
    draw_lives(window, player.lives)

    pygame.display.update()

    
def level2(window):
    global level2pass
    clock = pygame.time.Clock()
    background, bg_image = get_background("Gray.png")

    block_size = 96

    player_x = -1000
    player_y = HEIGHT - block_size - 50  # 50 es la altura del jugador

    player = Player(player_x, player_y, 50, 50)
    enemy_x = -800  # Centrado horizontalmente en la pantalla
    enemy_y = HEIGHT - block_size - 70  # A 70 píxeles por encima del borde inferior
    enemy = Enemy(enemy_x, enemy_y, 50, 50, move_range=(-100, 300))
    
    #Enemigos
    
    #fuegos que estan encendidos
    fire1 = Fire(700, HEIGHT - block_size - 63, 16, 32)
    fire2 = Fire(300, HEIGHT - block_size - 63, 16, 32)
    fire3 = Fire(1100, HEIGHT - block_size - 63, 16, 32)
    fire4 = Fire(700, HEIGHT - block_size - 542, 16, 32)
    fire5 = Fire(300, HEIGHT - block_size - 350, 16, 32)
    fire6 = Fire(1100, HEIGHT - block_size - 350, 16, 32)
    fire20 = Fire(1960, HEIGHT - block_size - 63, 16, 32)
    fire22 = Fire(2340, HEIGHT - block_size - 350, 16, 32)
    fire23 = Fire(2720, HEIGHT - block_size - 350, 16, 32)
    
    #codigo para mostrar encendido el fuego, mostrar solo encendido los fuegos que se veran en pantalla
    fire1.on()
    fire2.on()
    fire3.on()
    fire4.on()
    fire5.on()
    fire6.on()
    fire20.on()
    fire22.on()
    fire23.on()

    floor = [
        Block2(i * block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)
        if i not in [1, 5, 6, 9,10, 13,14,15, 16, 17,18,19]
    ]

    objects = [*floor,
               #diseño de las plataformas iniciales
               Block2(0, HEIGHT - block_size * 2, block_size),
               Block2(block_size * 2, HEIGHT - block_size * 4, block_size),
               Block2(block_size * 3, HEIGHT - block_size * 4, block_size),
               Block2(block_size * 4, HEIGHT - block_size * 4, block_size),
               Block2(block_size * 5, HEIGHT - block_size * 5, block_size),
               Block2(block_size * 6, HEIGHT - block_size * 6, block_size),
               Block2(block_size * 7, HEIGHT - block_size * 6, block_size),
               Block2(block_size * 8, HEIGHT - block_size * 6, block_size),
               Block2(block_size * 11, HEIGHT - block_size * 4, block_size),
               Block2(block_size * 12, HEIGHT - block_size * 4, block_size),
               Block2(block_size * 14, HEIGHT - block_size * 2, block_size),

               #diseño parte tryhard
               Block2(block_size * 17, HEIGHT - block_size * 4, block_size),
               Block2(block_size * 21, HEIGHT - block_size * 4, block_size),
               Block2(block_size * 24, HEIGHT - block_size * 4, block_size),
               Block2(block_size * 25, HEIGHT - block_size * 4, block_size),
               Block2(block_size * 28, HEIGHT - block_size * 4, block_size),
               Block2(block_size * 29, HEIGHT - block_size * 4, block_size),

               #codigo para la columna del inicio
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 1, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 2, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 3, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 4, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 5, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 6, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 7, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 8, block_size),
               #colocacion de los fuegos en el mapa
               fire1, fire2, fire3, fire4, fire5, fire6, 
               fire20,fire22,fire23]

    offset_x = -1500
    scroll_area_width = 450

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()  # Cambiado: Salir del programa si se cierra la ventana
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        enemy.loop(FPS, objects)  # Pasa los objetos al loop del enemigo


        if player.rect.y > 800:
            game_over_screen(window, True)
            
        # Mostrar en loop solo los fuegos encendidos
        for fire in [fire1, fire2, fire3, fire4, fire5, fire6, fire20, fire22, fire23]:
            fire.loop()

        handle_move(player, objects)
        draw(window, background, bg_image, enemy, player, objects, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

        specific_y = HEIGHT - block_size * 4  # Ajusta este valor según sea necesario

        pygame.display.update()
 #loop para el chequeo de colisiones
        for firecheck in [fire1, fire2, fire3, fire4, fire5, fire6]:
            firecheck.check_collision(player)

        if pygame.sprite.collide_mask(player, enemy):
            player.make_hit()
        if player.rect.x >= block_size * 29 and player.rect.y <= specific_y:
                victory_screen(window)
                return True
    
def level3(window):
    global level3pass
    clock = pygame.time.Clock()
    background, bg_image = get_background("Pink.png")

    block_size = 96

    player_x = -1000
    player_y = HEIGHT - block_size - 50  # 50 es la altura del jugador

    player = Player(player_x, player_y, 50, 50)
    enemy_x = -800  # Centrado horizontalmente en la pantalla
    enemy_y = HEIGHT - block_size - 70  # A 70 píxeles por encima del borde inferior
    enemy = Enemy(enemy_x, enemy_y, 50, 50, move_range=(-100, 300))
    
    #Enemigos
    
    #fuegos que estan encendidos
    fire1 = Fire(700, HEIGHT - block_size - 63, 16, 32)
    fire2 = Fire(300, HEIGHT - block_size - 63, 16, 32)
    fire3 = Fire(1100, HEIGHT - block_size - 63, 16, 32)
    fire4 = Fire(700, HEIGHT - block_size - 542, 16, 32)
    fire5 = Fire(300, HEIGHT - block_size - 350, 16, 32)
    fire6 = Fire(1100, HEIGHT - block_size - 350, 16, 32)
    fire20 = Fire(1960, HEIGHT - block_size - 63, 16, 32)
    fire22 = Fire(2340, HEIGHT - block_size - 350, 16, 32)
    fire23 = Fire(2720, HEIGHT - block_size - 350, 16, 32)
    
    #codigo para mostrar encendido el fuego, mostrar solo encendido los fuegos que se veran en pantalla
    fire1.on()
    fire2.on()
    fire3.on()
    fire4.on()
    fire5.on()
    fire6.on()
    fire20.on()
    fire22.on()
    fire23.on()

    floor = [
        Block3(i * block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)
        if i not in [1, 5, 6, 9,10, 13,14,15, 16, 17,18,19]
    ]

    objects = [*floor,
               #diseño de las plataformas iniciales
               Block3(0, HEIGHT - block_size * 2, block_size),
               Block3(block_size * 2, HEIGHT - block_size * 4, block_size),
               Block3(block_size * 3, HEIGHT - block_size * 4, block_size),
               Block3(block_size * 4, HEIGHT - block_size * 4, block_size),
               Block3(block_size * 5, HEIGHT - block_size * 5, block_size),
               Block3(block_size * 6, HEIGHT - block_size * 6, block_size),
               Block3(block_size * 7, HEIGHT - block_size * 6, block_size),
               Block3(block_size * 8, HEIGHT - block_size * 6, block_size),
               Block3(block_size * 11, HEIGHT - block_size * 4, block_size),
               Block3(block_size * 12, HEIGHT - block_size * 4, block_size),
               Block3(block_size * 14, HEIGHT - block_size * 2, block_size),

               #diseño parte tryhard
               Block3(block_size * 17, HEIGHT - block_size * 4, block_size),
               Block3(block_size * 21, HEIGHT - block_size * 4, block_size),
               Block3(block_size * 24, HEIGHT - block_size * 4, block_size),
               Block3(block_size * 25, HEIGHT - block_size * 4, block_size),
               Block3(block_size * 28, HEIGHT - block_size * 4, block_size),
               Block3(block_size * 29, HEIGHT - block_size * 4, block_size),

               #codigo para la columna del inicio
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 1, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 2, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 3, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 4, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 5, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 6, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 7, block_size),
               InvisibleBlock(block_size * -12, HEIGHT - block_size * 8, block_size),
               #colocacion de los fuegos en el mapa
               fire1, fire2, fire3, fire4, fire5, fire6, 
               fire20,fire22,fire23]

    offset_x = -1500
    scroll_area_width = 450

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()  # Cambiado: Salir del programa si se cierra la ventana
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        enemy.loop(FPS, objects)  # Pasa los objetos al loop del enemigo


        if player.rect.y > 800:
            game_over_screen(window, True)
            
        # Mostrar en loop solo los fuegos encendidos
        for fire in [fire1, fire2, fire3, fire4, fire5, fire6, fire20, fire22, fire23]:
            fire.loop()

        handle_move(player, objects)
        draw(window, background, bg_image, enemy, player, objects, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

        specific_y = HEIGHT - block_size * 4  # Ajusta este valor según sea necesario

        pygame.display.update()
 #loop para el chequeo de colisiones
        for firecheck in [fire1, fire2, fire3, fire4, fire5, fire6]:
            firecheck.check_collision(player)

        if pygame.sprite.collide_mask(player, enemy):
            player.make_hit()
        if player.rect.x >= block_size * 29 and player.rect.y <= specific_y:
                victory_screen(window)
                return True

def load_music(track):
    pygame.mixer.music.load(os.path.join("assets/Music/ost", track))
    pygame.mixer.music.play(-1)


# Código de la pantalla principal
def main(window):
    global level1pass, level2pass, level3pass
    while True:
        if not level1pass:
            load_music("level1.mp3")
            level1pass = level1(window)
        elif not level2pass:
            load_music("level2.mp3")
            level2pass = level2(window)
        elif not level3pass:
            load_music("level2.mp3")
            level3pass = level3(window)
        else:
            break
    pygame.quit()
    sys.exit()


def victory_screen(window):
    global level1pass, level2pass
    pygame.mixer.music.stop()
    font = pygame.font.Font(None, 36)

    background_surface = window.copy()
    blurred_background = blur_surf(background_surface, radius=10)

    window.blit(blurred_background, (0, 0))

    win_text = font.render("¡Has ganado!", True, (0, 255, 0))
    text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    restart_text = font.render("Presione Enter para continuar", True, (255, 255, 255))
    restart_text_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

    exit_text = font.render("Presione ESC para salir", True, (255, 255, 255))
    exit_text_rect = exit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

    window.blit(win_text, text_rect)
    window.blit(restart_text, restart_text_rect)
    window.blit(exit_text, exit_text_rect)
    pygame.display.flip()

    level_completed = False
    while not level_completed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    level_completed = True
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def game_over_screen(window, waiting=False):
    pygame.mixer.music.stop()
    font = pygame.font.Font(None, 36)

        # Obtener una copia de la ventana actual y aplicar el desenfoque
    background_surface = window.copy()
    blurred_background = blur_surf(background_surface, radius=10)

    # Dibujar la superficie desenfocada en la ventana
    window.blit(blurred_background, (0, 0))
    
    # Texto de "Game Over"
    game_over_text = font.render("Game Over", True, (255, 0, 0))
    text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    # Texto de "Presione Enter para reiniciar"
    restart_text = font.render("Presione Enter para reiniciar", True, (255, 255, 255))
    restart_text_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

    exit_text = font.render("Presione ESC para salir", True, (255,255,255))
    exit_text_rect = exit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

     # Limpiar la pantalla con negro
    window.blit(game_over_text, text_rect)
    window.blit(restart_text, restart_text_rect)
    window.blit(exit_text, exit_text_rect)
    pygame.display.flip()

    if waiting:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Esperar a que se presione Enter para reiniciar
                        pygame.mixer.music.load("assets/Music/ost/level1.mp3")
                        pygame.mixer.music.play(-1)
                        main(window)  # Reiniciar el juego
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

if __name__ == "__main__":
    pygame.mixer.music.load("assets/Music/ost/level1.mp3")
    main_menu()
    pygame.mixer.music.stop()
    pygame.init()
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Juego de Niveles")
    main(window)