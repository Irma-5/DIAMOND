import os
import sys
import random

import pygame
from settings import *


def load_image(name, colorkey=None):
    image = pygame.image.load(name)
    return image

def loading_menu():
    image = load_image("menu.jpg")
    fon = pygame.transform.scale(image, (width, height))
    screen.blit(fon, (0, 0))
    all_sprites = pygame.sprite.Group()

    sprite = pygame.sprite.Sprite()
    diamond = pygame.transform.scale(load_image("diamond.png"), (width//3, height//25*10))
    sprite.image = diamond
    sprite.rect = sprite.image.get_rect()
    all_sprites.add(sprite)
    sprite.rect.x = width/2 - sprite.rect.width/2
    sprite.rect.y = height/3 - sprite.rect.height/2
    all_sprites.draw(screen)

    loading = True
    coord_of_load = 1
    while loading:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.draw.rect(screen, orange, (100, 450, coord_of_load, 10), 0)
        if coord_of_load <= 600: coord_of_load += 20
        else: loading = 0
        clock.tick(25 + random.randrange(-20, 20))
        pygame.display.flip()


def game_menu():
    image = load_image("menu.jpg")
    fon = pygame.transform.scale(image, (width, height))
    screen.blit(fon, (0, 0))
    all_sprites = pygame.sprite.Group()

    sprite = pygame.sprite.Sprite()
    diamond = pygame.transform.scale(load_image("diamond.png"), (width // 3, height // 25 * 10))
    sprite.image = diamond
    sprite.rect = sprite.image.get_rect()
    all_sprites.add(sprite)
    sprite.rect.x = width / 2 - sprite.rect.width / 2
    sprite.rect.y = height / 3 - sprite.rect.height / 2
    all_sprites.draw(screen)
    choose = 0
    while not choose:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.draw.rect(screen, sky_blue, (120, 300, 580, 100), 0)
        clock.tick(FPS)
        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('D')
    size = width, height = 800, 600
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    running = True
    loading_menu()
    clock.tick(FPS - 20)
    game_menu()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()