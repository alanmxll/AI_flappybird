import os

import neat
import pygame

from FlappyBird import (SCREEN_HEIGHT, SCREEN_WIDTH, Bird, Ground, Pipe,
                        ai_playing, draw_screen, generation)


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
