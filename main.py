import pygame
import pygame_menu
import pygbutton
import datetime
import numpy as np

from entities.lemonadegame import LemonadeGame
from sound import Sound

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

    # RECIPE STUFF
    recipe_theme = pygame_menu.themes.THEME_DEFAULT.copy()
    recipe_theme.background_color = (0, 0, 0, 100)  # Enable transparency
    recipe_menu = pygame_menu.Menu(
        theme=recipe_theme,
        height=400,
        width=600,
        onclose=pygame_menu.events.RESET,
        title='Recipe',
    )
    recipe_menu.add_text_input('Lemon Juice [ml] :', default=lemonade_game.recipe.lemon_juice,
                               onchange=lemonade_game.recipe.validate_lemonjuice, maxwidth=100,
                               maxwidth_dynamically_update=False)
    recipe_menu.add_text_input('Sugar [g] :', default=lemonade_game.recipe.sugar,
                               onchange=lemonade_game.recipe.validate_sugar)
    recipe_menu.add_text_input('Water [ml] :', default=lemonade_game.recipe.water,
                               onchange=lemonade_game.recipe.validate_water)
    recipe_menu.add_text_input('Ice [cubes] :', default=lemonade_game.recipe.ice,
                               onchange=lemonade_game.recipe.validate_ice)
    recipe_menu.add_selector('Straw Type ',
                             [('None', 'no'),
                              ('Plastic', 'plastic'),
                              ('Paper', 'paper')],
                             onchange=lemonade_game.recipe.validate_straw,
                             selector_id='select_straw')

    recipe_menu.add_button('CLOSE', pygame_menu.events.CLOSE)
    recipe_menu.disable()
    recipe_button = pygbutton.PygButton((800 - 80, 520, 64, 64), normal='./resources/flask.png')

    # PRICE
    price_theme = pygame_menu.themes.THEME_DEFAULT.copy()
    price_theme.background_color = (0, 0, 0, 100)  # Enable transparency
    price_menu = pygame_menu.Menu(
        theme=price_theme,
        height=400,
        width=600,
        onclose=pygame_menu.events.RESET,
        title='PRICING',
    )
    price_menu.add_text_input('Price/Cup [$] :',
                              default=str(np.round(lemonade_game.lemonade_stand.price + 0.001, 2)),
                              onchange=lemonade_game.lemonade_stand.validate_price)
    price_menu.add_button('CLOSE', pygame_menu.events.CLOSE)
    price_menu.disable()
    price_button = pygbutton.PygButton((800 - 80 - 8 - 64, 520, 64, 64),
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
            pygame.display.update()

        for event in pygame.event.get():

            # Close button clicked
            if event.type == pygame.QUIT:
                done = True

            buttonEvents = recipe_button.handleEvent(event)
            if 'click' in buttonEvents:
                recipe_menu.enable()
                recipe_menu.mainloop(lemonade_game.screen)

            buttonEvents = price_button.handleEvent(event)
            if 'click' in buttonEvents:
                price_menu.enable()
                price_menu.mainloop(lemonade_game.screen)

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
