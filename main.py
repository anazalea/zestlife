import pygame
import pygame_menu
import pygbutton
import datetime
import numpy as np

from entities.lemonadegame import LemonadeGame
<<<<<<< HEAD
from sound import Sound
=======
import menus

>>>>>>> inventory-menu

def play():
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.init()
    sound = Sound()
    pygame.mouse.set_visible(1)
    pygame.display.set_caption("LEMONADE")
    clock = pygame.time.Clock()
    game_speed = 0.25
    lemonade_game = LemonadeGame(sound, config=None)

    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################

    recipe_button = pygbutton.PygButton((800 - 80, 520, 64, 64), normal='./resources/flask.png')
    price_button = pygbutton.PygButton((800 - 80 - 8 - 64, 520, 64, 64),
                                       normal='./resources/dollar-coin.png')
    inventory_button = pygbutton.PygButton((800 - 80 - 8 - 64 - 8 - 64, 520, 64, 64),
                                       normal='./resources/dollar-coin.png')

    ##############################################################################################
    ##############################################################################################
    ##############################################################################################
    ##############################################################################################

    fps = 60
    done = False
    pause = False
    while not done:
        clock.tick(fps)
        if not pause:
            lemonade_game.update_world(game_speed)
            lemonade_game.draw()
            lemonade_game.print_stats()
            recipe_button.draw(lemonade_game.screen)
            price_button.draw(lemonade_game.screen)
            inventory_button.draw(lemonade_game.screen)
            pygame.display.update()

        for event in pygame.event.get():

            # Close button clicked
            if event.type == pygame.QUIT:
                done = True

            buttonEvents = recipe_button.handleEvent(event)
            if 'click' in buttonEvents:
                menus.recipe_menu(lemonade_game) #Needs recipe

            buttonEvents = price_button.handleEvent(event)
            if 'click' in buttonEvents:
                menus.price_menu(lemonade_game) #Needs lemonade stand

            buttonEvents = inventory_button.handleEvent(event)
            if 'click' in buttonEvents:
                menus.inventory_menu(lemonade_game) #Needs lemonade stand

            elif event.type == pygame.KEYDOWN:
                # Escape key pressed
                if event.key == pygame.K_ESCAPE:
                    done = True

                elif event.key == pygame.K_SPACE:
                    pause = not pause

                elif event.key == pygame.K_1:
                    game_speed = 0.25

                elif event.key == pygame.K_2:
                    game_speed = 1

                elif event.key == pygame.K_3:
                    game_speed = 5

                elif event.key == pygame.K_r:
                    recipe_menu.toggle()


if __name__ == '__main__':
    play()
