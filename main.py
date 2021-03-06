import pygame

from FlappyBird import (SCREEN_HEIGHT, SCREEN_WIDTH, Bird, Ground, Pipe,
                        draw_screen)


def main():
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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for bird in birds:
                        bird.jump()

        # Move elements
        for bird in birds:
            bird.move()

        ground.move()

        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    birds.pop(i)

                if not pipe.passed and bird.x_axis > pipe.x_axis:
                    pipe.passed = True
                    add_pipe = True

            pipe.move()
            if pipe.x_axis + pipe.TOP_PIPE.get_width() < 0:
                remove_pipes.append(pipe)

        if add_pipe:
            scores += 1
            pipes.append(Pipe(600))

        for pipe in remove_pipes:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y_axis + bird.image.get_height()) > ground.y_axis or bird.y_axis < 0:
                birds.pop(i)

        draw_screen(screen, birds, pipes, ground, scores)


if __name__ == '__main__':
    main()
