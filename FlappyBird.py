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


class Bird:
    IMAGES = BIRD_IMAGES
    # Rotation animations
    MAX_ROTATION = 25
    SPEED_ROTATION = 20
    ANIMATION_TIME = 5

    def __init__(self, x_axis, y_axis):
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.angle = 0
        self.speed = 0
        self.height = self.y_axis
        self.time = 0
        self.image_count = 0
        self.image = BIRD_IMAGES[0]

    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.height = self.y_axis

    def move(self):
        # Calculate the displacement
        self.time += 1

        # s = s0 + v0 * t + (at² / 2)
        displacement = 1.5 * (self.time**2) + self.speed * self.time

        # Restrict the displacement
        if displacement > 16:
            displacement = 16
        elif displacement < 0:
            displacement -= 2

        self.y_axis += displacement

        # The angle of the bird
        if displacement < 0 or self.y_axis < (self.height + 50):
            if self.angle < self.MAX_ROTATION:
                self.angle = self.MAX_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.SPEED_ROTATION

    def draw(self, screen):
        # Define what bird image use
        self.image_count += 1

        if self.image_count < self.ANIMATION_TIME:
            self.image = self.IMAGES[0]
        elif self.image_count < self.ANIMATION_TIME*2:
            self.image = self.IMAGES[1]
        elif self.image_count < self.ANIMATION_TIME*3:
            self.image = self.IMAGES[2]
        elif self.image_count < self.ANIMATION_TIME*4:
            self.image = self.IMAGES[1]
        elif self.image_count >= self.ANIMATION_TIME*4 + 1:
            self.image = self.IMAGES[0]
            self.image_count = 0

        # Let a fix image when bird go down
        if self.angle <= -80:
            self.image = self.IMAGES[1]
            self.image_count = self.ANIMATION_TIME*2

        # Draw the image
        routated_image = pygame.transform.rotate(self.image, self.angle)
        center_image_position = self.image.get_react(
            topleft=(self.x_axis, self.y_axis)).center
        rectangle = routated_image.get_rect(center=center_image_position)
        screen.blit(routated_image, rectangle)

    def get_mask(self):
        pygame.mask.from_surface(self.image)


class Pipe:
    DISTANCE = 200
    SPEED = 5

    def __init__(self, x_axis):
        self.x_axis = x_axis
        self.height = 0
        self.top_position = 0
        self.base_position = 0
        self.TOP_PIPE = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.BASE_PIPE = PIPE_IMAGE
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top_position = self.height - self.TOP_PIPE.get_height()
        self.base_position = self.height + self.DISTANCE

    def move(self):
        self.x_axis -= self.SPEED

    def draw(self, screen):
        screen.blit(self.TOP_PIPE, (self.x_axis, self.top_position))
        screen.blit(self.BASE_PIPE, (self.x_axis, self.base_position))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.TOP_PIPE)
        base_mask = pygame.mask.from_surface(self.BASE_PIPE)

        top_distance = (self.x_axis - bird.x_axis,
                        self.top_position - round(bird.y_axis))
        base_distance = (self.x_axis - bird.x_axis,
                         self.base_position - round(bird.y_axis))

        top_point = bird_mask.overlap(top_mask, top_distance)
        base_point = bird_mask.overlap(base_mask, base_distance)

        if base_point or top_point:
            return True
        else:
            return False


