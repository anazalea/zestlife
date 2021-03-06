import pygame
import pygame_menu
import pygbutton
import datetime
import numpy as np

from entities.lemonadegame import LemonadeGame
from sound import Sound
import menus


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

    bt_top = 547
    bt_w = 48
    bt_mgin = 5  # button margin
    recipe_button = pygbutton.PygButton((800 - bt_w - bt_mgin, bt_top, 60, 60),
                                        normal='./resources/recipe_button_norm.png',
                                        highlight='./resources/recipe_button_hover.png')
    price_button = pygbutton.PygButton((800 - 2 * (bt_w+bt_mgin), bt_top, 60, 60),
                                       normal='./resources/price_button_norm.png',
                                       highlight='./resources/price_button_hover.png')
    employees_button = pygbutton.PygButton((800 - 3 * (bt_w+bt_mgin), bt_top, 60, 60),
                                       normal='./resources/employee_button_norm.png',
                                       highlight='./resources/employee_button_hover.png')
    upgrade_button = pygbutton.PygButton((800 - 4 * (bt_w+bt_mgin), bt_top, 60, 60),
                                           normal='./resources/upgrade_button_norm.png',
                                           highlight='./resources/upgrade_button_hover.png')

    order_button = pygbutton.PygButton((42*5, 535, 83, 23),
                                           normal='./resources/order_button_norm.png',  
                                           highlight='./resources/order_button_hover.png')

    # import ipdb; ipdb.set_trace()
    pause_button = pygbutton.PygButton((800-100, 1,  14, 19),
                                        normal = './resources/pause_black.png',
                                        highlight = './resources/pause_red.png')

    play_button = pygbutton.PygButton((800-100+14+6, 1,  13, 19),
                                        normal = './resources/play_black.png',
                                        highlight = './resources/play_red.png')

    ff_button = pygbutton.PygButton((800-100+14+6+13+6, 1,  22, 19),
                                        normal = './resources/ff_black.png',
                                        highlight = './resources/ff_red.png')

    fff_button = pygbutton.PygButton((800-100+14+6+13+6+22+6, 1,  29, 19),
                                        normal = './resources/fff_black.png',
                                        highlight = './resources/fff_red.png')
 

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
            lemonade_game.print_thought()
            recipe_button.draw(lemonade_game.screen)
            price_button.draw(lemonade_game.screen)
            order_button.draw(lemonade_game.screen)
            employees_button.draw(lemonade_game.screen)
            upgrade_button.draw(lemonade_game.screen)
            pause_button.draw(lemonade_game.screen)
            play_button.draw(lemonade_game.screen)
            ff_button.draw(lemonade_game.screen)
            fff_button.draw(lemonade_game.screen)
            pygame.display.update()
            

        for event in pygame.event.get():

            # Close button clicked
            if event.type == pygame.QUIT:
                done = True

            if 'click' in recipe_button.handleEvent(event):
                menus.recipe_menu(lemonade_game)

            if 'click' in price_button.handleEvent(event):
                menus.price_menu(lemonade_game)

            if 'click' in order_button.handleEvent(event):
                menus.inventory_menu(lemonade_game)

            if 'click' in employees_button.handleEvent(event):
                menus.employee_menu(lemonade_game)

            if 'click' in upgrade_button.handleEvent(event):
                menus.upgrade_menu(lemonade_game)
               
            if 'click' in pause_button.handleEvent(event):
                pause = not pause

            if 'click' in play_button.handleEvent(event):
                game_speed = 0.25
                pause = False

            if 'click' in ff_button.handleEvent(event):
                game_speed = 1
                pause = False

            if 'click' in fff_button.handleEvent(event):
                game_speed = 5
                pause = False

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


if __name__ == '__main__':
    play()
