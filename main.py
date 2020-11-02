import glob

import pygame
import pygame_menu
import pygbutton
import datetime
import numpy as np

from entities.lemonadestand import LemonadeStand
from entities.customer import Customer, CustomerArrivalTimeGenerator, CustomerPreferenceGenerator
from recipe import Recipe
from entities.analog_clock import AnalogClock
from entities.weather import Stars, Sun, Cloud
from entities.employee import Employee


def predict_demand(date):
    return 35


def create_background(screen, current_time):
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    if current_time > datetime.time(20, 0) or current_time < datetime.time(6, 30):
        color = (28, 40, 61)
    else:
        color = (143, 181, 242)
    # color = (255, 255, 255)
    background.fill(color)
    return background


def initial_the_game(current_datetime):
    pygame.init()
    pygame.mouse.set_visible(1)
    pygame.display.set_caption("LEMONADE")
    customer_image_dict = {}
    for s in ['happy', 'sad', 'lemonade']:
        images_path = glob.glob(f'./resources/customer_{s}_*.png')
        customer_image_dict[s] = [pygame.image.load(img_path) for img_path in images_path]
        # TODO: do flipping for moving left

    arrival_time_generator = CustomerArrivalTimeGenerator()
    preference_generator = CustomerPreferenceGenerator()
    n_customers_today = predict_demand(current_datetime.date())
    customers = [
        Customer((0, 300), arrival_time_generator, preference_generator, customer_image_dict) for i
        in
        range(1)]
    return pygame.sprite.Group(customers), customers


def play():

    current_datetime = datetime.datetime(2020, 10, 4, 9, 00)
    current_date = current_datetime.date()
    screen = pygame.display.set_mode((800, 600))
    group, customers = initial_the_game(current_datetime)
    game_speed = 0.25
    # Prepare Game Objects

    clock = pygame.time.Clock()
    arrival_time_generator = CustomerArrivalTimeGenerator()
    preference_generator = CustomerPreferenceGenerator()
    analog_clock = AnalogClock(current_datetime, screen)
    background = create_background(screen, current_datetime.time())
    scenery = pygame.image.load('./resources/background.png')
    stars = Stars()
    sun = Sun()
    clouds = {}
    cloud_index = 0
    employee = Employee()
    lemonade_stand = LemonadeStand(screen)

    # RECIPE STUFF
    recipe = Recipe(lemon_juice=40, sugar=35, water=300, ice=5, straw='no')
    recipe_theme = pygame_menu.themes.THEME_DEFAULT.copy()
    recipe_theme.background_color = (0, 0, 0, 100)  # Enable transparency
    recipe_menu = pygame_menu.Menu(
        theme=recipe_theme,
        height=400,
        width=600,
        onclose=pygame_menu.events.RESET,
        title='Recipe',
    )
    recipe_menu.add_text_input('Lemon Juice [ml] :', default=recipe.lemon_juice,
                               onchange=recipe.validate_lemonjuice, maxwidth=100,
                               maxwidth_dynamically_update=False)
    recipe_menu.add_text_input('Sugar [g] :', default=recipe.sugar,
                               onchange=recipe.validate_sugar)
    recipe_menu.add_text_input('Water [ml] :', default=recipe.water,
                               onchange=recipe.validate_water)
    recipe_menu.add_text_input('Ice [cubes] :', default=recipe.ice,
                               onchange=recipe.validate_ice)
    recipe_menu.add_selector('Straw Type ',
                             [('None', 'no'),
                              ('Plastic', 'plastic'),
                              ('Paper', 'paper')],
                             onchange=recipe.validate_straw,
                             selector_id='select_straw')

    recipe_menu.add_button('CLOSE', pygame_menu.events.CLOSE)
    recipe_menu.disable()
    recipe_button = pygbutton.PygButton((800 - 80, 520, 64, 64), normal='./resources/flask.png')

    n_customers_today = predict_demand(current_datetime.date())
    recent_customer_thought = ''

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
                              default=str(np.round(lemonade_stand.price + 0.001, 2)),
                              onchange=lemonade_stand.validate_price)
    price_menu.add_button('CLOSE', pygame_menu.events.CLOSE)
    price_menu.disable()
    price_button = pygbutton.PygButton((800 - 80 - 8 - 64, 520, 64, 64),
                                       normal='./resources/dollar-coin.png')

    fps = 60
    done = False
    pause = False

    # inital game
    # environment = GameEnvironment() # collection
    # environment.background =
    # ...

    while not done:
        screen.blit(background, (0, 0))
        screen.blit(scenery, (0, 0))
        time_passed_seconds = clock.tick(fps) / 1000.0

        font = pygame.font.Font(None, 25)
        if not pause:

            current_datetime += datetime.timedelta(minutes=game_speed)
            # for o in environment:
            #     o.move()

            if np.random.randn() > 0.9:
                cloud_index += 1
                clouds[cloud_index] = Cloud(screen)
            if current_datetime.time() > datetime.time(18,
                                                       0) or current_datetime.time() < datetime.time(
                    6, 30):
                color = (28, 40, 61)
                stars.twinkle()
                screen.blit(stars.image, (0, 0))
            else:
                color = (143, 181, 242)
                sun.twinkle()
                screen.blit(sun.image, (500, 0))
            background.fill(color)
            dead_clouds = []
            for cloud in clouds:
                clouds[cloud].move(game_speed)
                screen.blit(clouds[cloud].image, clouds[cloud].current_loc)
                if clouds[cloud].current_loc[0] < -200:
                    dead_clouds.append(cloud)
            [clouds.pop(dead_cloud) for dead_cloud in dead_clouds]

            # if it's a new day, generate new customers
            if current_datetime.date() != current_date:
                # NEW DAY
                n_customers_today = predict_demand(current_datetime.date())
                customers = [Customer(screen, arrival_time_generator, preference_generator) for i in
                             range(n_customers_today)]
                current_date = current_datetime.date()
            screen.blit(analog_clock.bg, analog_clock.loc)
            analog_clock.draw_hands(screen)

            # if the stand is open, update+draw employee
            if current_datetime.time() > lemonade_stand.opening_time \
                    and current_datetime.time() < lemonade_stand.closing_time:
                employee.update()
                screen.blit(employee.image, employee.loc)
            lemonade_stand.draw(current_datetime.time(), screen)

            group.draw(screen)
            group.update()

            # for each customer whose arrival time has passed
            for customer in customers:
                if customer.arrival_time < current_datetime.time():
                    customer.move(game_speed)
                    # screen.blit(customer.sprite_im, customer.current_loc)
                    # if they're right in front of the stand see if they want to/can purchase
                    if customer.current_loc[0] > int(
                            screen.get_width() / 2) - 50 and not customer.has_lemonade \
                            and customer.likes_recipe:
                        likes_it, reason = customer.customer_likes_recipe(recipe,
                                                                          lemonade_stand.price)
                        # print(likes_it, reason)

                        if not lemonade_stand.has_enough_stuff(recipe):
                            customer.state = Customer.CustomerState.SAD
                            recent_customer_thought = 'This lemonade stand is horrifically mismanaged.'

                        elif not likes_it:
                            customer.state = Customer.CustomerState.SAD
                            recent_customer_thought = reason

                        else:
                            recent_customer_thought = reason
                            lemonade_stand.lemons -= recipe.lemon_juice / lemonade_stand.juicing_efficiency
                            lemonade_stand.sugar -= recipe.sugar
                            lemonade_stand.account_balance += lemonade_stand.price
                            customer.state = Customer.CustomerState.LEMONADE

            analog_clock.current_time = current_datetime
            time_stamp = font.render(str(current_datetime), 1, (214, 26, 13))
            current_price = font.render(str(lemonade_stand.price) + ' $ / CUP', 1, (214, 26, 13))
            n_lemons = font.render(str(np.round(lemonade_stand.lemons, 1)) + ' LEMONS ON HAND', 1,
                                   (214, 26, 13))
            g_sugar = font.render(str(lemonade_stand.sugar) + ' g SUGAR ON HAND', 1, (214, 26, 13))
            juice_eff = font.render(
                f'JUICING EFFICIENCY {str(lemonade_stand.juicing_efficiency)} mL/lemon', 1,
                (214, 26, 13))
            money = font.render(str(lemonade_stand.account_balance) + ' $', 1, (0, 0, 0))
            thoughts = font.render(recent_customer_thought, 1, (0, 0, 0))

            screen.blit(time_stamp, [20, 20])
            screen.blit(current_price, [20, 40])
            screen.blit(juice_eff, [20, 60])
            screen.blit(n_lemons, [20, 80])
            screen.blit(g_sugar, [20, 100])
            screen.blit(money, [20, 120])
            screen.blit(thoughts, [10, 580])

            recipe_button.draw(screen)
            price_button.draw(screen)
            pygame.display.update()

        if recipe_menu.is_enabled():
            recipe_menu.mainloop(screen)

        for event in pygame.event.get():

            # Close button clicked
            if event.type == pygame.QUIT:
                done = True

            buttonEvents = recipe_button.handleEvent(event)
            if 'click' in buttonEvents:
                recipe_menu.enable()
                recipe_menu.mainloop(screen)

            buttonEvents = price_button.handleEvent(event)
            if 'click' in buttonEvents:
                price_menu.enable()
                price_menu.mainloop(screen)

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
