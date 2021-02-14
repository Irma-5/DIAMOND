import os
import sys

import pygame

FPS = 50
clock = pygame.time.Clock()
size = width, height = 800, 400
screen = pygame.display.set_mode(size)

def terminate():
    pygame.quit()
    sys.exit()

def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    text_coord = 50
    for line in intro_text:
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            # elif event.type == pygame.KEYDOWN or \
            #         event.type == pygame.MOUSEBUTTONDOWN:
            #     return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


start_screen()

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image