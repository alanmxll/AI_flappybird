import os
import random

import neat
import pygame

ai_playing = True
generation = 0

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
SCORE_FONT = pygame.font.SysFont('arial', 50)


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
        center_image_position = self.image.get_rect(
            topleft=(self.x_axis, self.y_axis)).center
        rectangle = routated_image.get_rect(center=center_image_position)
        screen.blit(routated_image, rectangle)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


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


class Ground:
    SPEED = 5
    WIDTH = GROUND_IMAGE.get_width()
    IMAGE = GROUND_IMAGE

    def __init__(self, y_axis):
        self.y_axis = y_axis
        self.x_axis_ground_0 = 0
        self.x_axis_ground_1 = self.WIDTH

    def move(self):
        self.x_axis_ground_0 -= self.SPEED
        self.x_axis_ground_1 -= self.SPEED

        if self.x_axis_ground_0 + self.WIDTH < 0:
            self.x_axis_ground_0 = self.x_axis_ground_1 + self.WIDTH

        if self.x_axis_ground_1 + self.WIDTH < 0:
            self.x_axis_ground_1 = self.x_axis_ground_0 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMAGE, (self.x_axis_ground_0, self.y_axis))
        screen.blit(self.IMAGE, (self.x_axis_ground_1, self.y_axis))


def draw_screen(screen, birds, pipes, ground, score):
    screen.blit(BACKGROUND_IMAGE, (0, 0))

    for bird in birds:
        bird.draw(screen)

    for pipe in pipes:
        pipe.draw(screen)

    score_text = SCORE_FONT.render(f"Score: {score}", 1, (255, 255, 255))
    screen.blit(score_text, (SCREEN_WIDTH - 10 - score_text.get_width(), 10))

    if(ai_playing):
        score_text = SCORE_FONT.render(
            f"Generation: {generation}", 1, (255, 255, 255))
        screen.blit(score_text, (10, 10))

    ground.draw(screen)

    pygame.display.update()


def main(genomes, settings):  # fitness function
    global generation
    generation += 1

    if ai_playing:
        networks = []
        genome_list = []
        birds = []

        for _, genome in genomes:
            network = neat.nn.FeedForwardNetwork.create(genome, settings)
            networks.append(network)
            genome.fitness = 0
            genome_list.append(genome)
            birds.append(Bird(230, 350))
    else:
        birds = [Bird(230, 350)]

    ground = Ground(730)
    pipes = [Pipe(700)]
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    scores = 0
    clock = pygame.time.Clock()

    is_running = True
    while is_running:
        clock.tick(30)

        # User interaction
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
                pygame.quit()
                quit()

            if not ai_playing:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        for bird in birds:
                            bird.jump()

        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x_axis > (pipes[0].x_axis + pipes[0].TOP_PIPE.get_width()):
                pipe_index = 1
        else:
            is_running = False
            break

        # Move elements
        for i, bird in enumerate(birds):
            bird.move()
            # Up bird fitness
            genome_list[i].fitness += 0.1
            output = networks[i].activate(
                (bird.y_axis,
                 abs(bird.y_axis - pipes[pipe_index].height),
                    abs(bird.y_axis - pipes[pipe_index].base_position))
            )
            # -1 and 1 -> if the output is > 0.5 so the bird jump
            if output[0] > 0.5:
                bird.jump()

        ground.move()

        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    birds.pop(i)
                    if ai_playing:
                        genome_list[i].fitness -= 1
                        genome_list.pop(i)
                        networks.pop(i)

                if not pipe.passed and bird.x_axis > pipe.x_axis:
                    pipe.passed = True
                    add_pipe = True

            pipe.move()
            if pipe.x_axis + pipe.TOP_PIPE.get_width() < 0:
                remove_pipes.append(pipe)

        if add_pipe:
            scores += 1
            pipes.append(Pipe(600))
            for genome in genome_list:
                genome.fitness += 5

        for pipe in remove_pipes:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y_axis + bird.image.get_height()) > ground.y_axis or bird.y_axis < 0:
                birds.pop(i)
                if ai_playing:
                    genome_list.pop(i)
                    networks.pop(i)

        draw_screen(screen, birds, pipes, ground, scores)


def run(settings_path):
    settings = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                           neat.DefaultSpeciesSet, neat.DefaultStagnation, settings_path)

    birds_population = neat.Population(settings)
    birds_population.add_reporter(neat.StdOutReporter(True))
    birds_population.add_reporter(neat.StatisticsReporter())

    if ai_playing:
        birds_population.run(main, 50)
    else:
        main(None, None)


if __name__ == '__main__':
    path = os.path.dirname(__file__)
    settings_path = os.path.join(path, 'settings.txt')
    run(settings_path)
