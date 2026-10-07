import pygame

from game.game_engine import GameEngine, WIDTH, HEIGHT, FPS

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic Escape")

clock = pygame.time.Clock()

engine = GameEngine(screen)

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                engine.reset()

    keys = pygame.key.get_pressed()

    engine.update(keys)
    engine.draw()

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()