import pygame
import pygame_menu
import pygbutton
import datetime
import time
import numpy as np
import math

from weather import Cloud

cloud_spawn_rate = 0.9
BACKGROUND_COLOR = (0,0,0)
BACKGROUND_SKY_MSG = 'BLAH'

def create_background(screen, current_time):
    global BACKGROUND_COLOR
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    if current_time > datetime.time(20,0) or current_time < datetime.time(6,30):
        color = BACKGROUND_COLOR
    else:
        color = BACKGROUND_COLOR
    background.fill(color)
    return background

def validate_sky_color(value):
    global BACKGROUND_SKY_MSG
    try:
        float(value)
        randomize_sky_color(value)
        BACKGROUND_SKY_MSG = 'BLOOOO'
    except:
        BACKGROUND_SKY_MSG = 'PICK A BETTER NUMBER'


def randomize_sky_color(value):
    global BACKGROUND_COLOR
    BACKGROUND_COLOR = np.ones(3) * float(value)

def set_cloud_spawn_rate(new_rate):
    global cloud_spawn_rate
    print('NEW!',cloud_spawn_rate)
    cloud_spawn_rate = float(new_rate)

def play():
    global cloud_spawn_rate
    pygame.init()
    pygame.mouse.set_visible(1)
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("LEMONADE")
    current_datetime = datetime.datetime(2020, 10, 4, 9, 00)
    background = create_background(screen, current_datetime.time())
    recipe_button = pygbutton.PygButton((16, 520, 64, 64), normal = './resources/lamp.png')
    lamp = pygame.image.load('./resources/lamp.png')
    game_speed = 0.25
    clouds = {}
    cloud_index = 0
    
    fps = 60
    done = False
    pause = False

    menu = pygame_menu.Menu(height = 300,
                            width = 400,
                            title = 'CLOUDS',
                            theme = pygame_menu.themes.THEME_BLUE,
                            onclose = pygame_menu.events.RESET)
    menu.add_text_input('Sky color :', default=0.9, onchange=validate_sky_color)
    menu.add_label(BACKGROUND_SKY_MSG, max_char=-1, font_size=20)
    menu.add_button('Close Menu', pygame_menu.events.CLOSE)




    while not done:
        background.fill(BACKGROUND_COLOR)
        screen.blit(background, (0,0))
        
        if not pause:
            current_datetime += datetime.timedelta(minutes = game_speed)
            if np.random.randn() > cloud_spawn_rate:
                    cloud_index += 1
                    clouds[cloud_index] = Cloud(screen)
            dead_clouds = []
            for cloud in clouds:
                clouds[cloud].move(game_speed)
                screen.blit(clouds[cloud].image, clouds[cloud].current_loc)
                if clouds[cloud].current_loc[0] < -200:
                    dead_clouds.append(cloud)
            [clouds.pop(dead_cloud) for dead_cloud in dead_clouds]
        recipe_button.draw(screen)
        pygame.display.update() 

        if menu.is_enabled():
            print('here')
            menu.mainloop(screen)
            print(menu.is_enabled())
            # menu.draw(screen)
        
        for event in pygame.event.get():
            # Close button clicked
            if event.type == pygame.QUIT:
                done = True

            buttonEvents = recipe_button.handleEvent(event)
            if 'click' in buttonEvents:
                print('Clicked')
                menu.enable()
                menu.mainloop(screen)
                # menu.mainloop(screen)
                # pause = True
                

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

                # elif event.key == pygame.K_r:
                #     recipe_menu.toggle()

if __name__ == '__main__':
  play()
