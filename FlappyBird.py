import os
import random

import pygame

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800

PIPE_IMAGE = pygame.transform.scale2x(
    pygame.image.load(os.path.join('images', 'pipe.png')))
GROUND_IMAGE = pygame.transform.scale2x(
    pygame.image.load(os.path.join('images', 'base.png')))
BACKGROUND_IMAGE = pygame.transform.scale2x(
    pygame.image.load(os.path.join('images', 'bg.png')))
BIRD_IMAGES = [
    pygame.transform.scale2x(pygame.image.load(
        os.path.join('images', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(
        os.path.join('images', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(
        os.path.join('images', 'bird3.png')))
]


pygame.font.init()
POINTS_FONT = pygame.font.SysFont('arial', 50)
