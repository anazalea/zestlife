import pygame
import pygame_menu
import pygbutton
import datetime
import time
import numpy as np
import math

from lemonadestand import LemonadeStand
from customer import Customer, CustomerArrivalTimeGenerator, CustomerPreferenceGenerator
from recipe import Recipe
from analog_clock import AnalogClock
from weather import Stars, Sun, Cloud
from employee import Employee

#Constants
#FONT_STYLE = './resources/dpcomic.ttf'
#FONT_STYLE = './resources/ARCADECLASSIC.ttf'
FONT_STYLE = './resources/joystix-monospace.ttf'

#Helper functions
def text_objects(text, font, color):
    text_surface = font.render(text, True, color)
    return text_surface, text_surface.get_rect()

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)

def button(surface, text, active_color, inactive_color, rect, font, click):
    mouse = pygame.mouse.get_pos()
    return_value = False
    if rect[0] < mouse[0] < rect[0] + rect[2] and rect[1] < mouse[1] < rect[1] + rect[3]:
        #Mouse is over the button
        draw_rect_alpha(surface, active_color, rect)
        #Did the user click
        if click and pygame.time.get_ticks() > 100:
            return_value = True
    else:
        draw_rect_alpha(surface, inactive_color, rect)
    text_surf, text_rect = text_objects(text, font, (255, 255, 255))
    text_rect.center = (int(rect[0] + rect[2] / 2), int(rect[1] + rect[3] / 2))
    surface.blit(text_surf, text_rect)
    return return_value

def menu_button(surface, active_color, inactive_color, rect, font, click):
    mouse = pygame.mouse.get_pos()
    return_value = False
    pass

def main_menu():
    pygame.init()
    pygame.mouse.set_visible(1)
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("LEMONADE")
    done = False
    click = False
    background = create_menu_background(screen)
    scenery = pygame.image.load('./resources/title.png')
    #stand = pygame.image.load('./resources/stand.png')

    while not done:
        screen.blit(background, (0,0))
        screen.blit(scenery, (0,0))
        #screen.blit(stand, (100,0))
        font = pygame.font.Font(FONT_STYLE,25) #Edit fonts here
        draw_text('main menu', font, (255, 255, 255), screen, 20, 20)
        buttons = [False]*2
        button_coords = [(290, 385, 250, 50),(290, 460, 250, 50)]
        buttons[0] = button(screen, 'Start Game', (0,0,0,100), (0,0,0,255), button_coords[0], font, click)
        buttons[1] = button(screen, 'Quit', (0,0,0,100), (0,0,0,255), button_coords[1], font, click)
        if click:
            if buttons[0]:
                play()
            if buttons[1]:
                done = True
        click = False
        pygame.display.update()

        #Events
        for event in pygame.event.get():
            # Close button clicked
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                #Clicked on start game
                if event.button == 1:
                    click = True
            if event.type == pygame.KEYDOWN:
                # Escape key pressed
                if event.key == pygame.K_ESCAPE:
                    done = True

def predict_demand(date):
    return 35

def create_menu_background(screen):
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    color = (143, 181, 242)
    background.fill(color)
    return background

def create_background(screen, current_time):
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    if current_time > datetime.time(20,0) or current_time < datetime.time(6,30):
        color = (28, 40, 61)
    else:
        color = (143, 181, 242)
    # color = (255, 255, 255)
    background.fill(color)
    return background

def play():
    pygame.init()
    pygame.mouse.set_visible(1)
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("LEMONADE")
    current_datetime = datetime.datetime(2020, 10, 4, 9, 00)
    current_date = current_datetime.date()
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
    recipe_menu(recipe)
    recipe_button = pygbutton.PygButton((800-80, 520, 64, 64), normal = './resources/flask.png')

    n_customers_today = predict_demand(current_datetime.date())
    customers = [Customer(screen, arrival_time_generator, preference_generator) for i in range(n_customers_today)]
    recent_customer_thought = ''

    # PRICE
    price_menu(lemonade_stand)
    price_button = pygbutton.PygButton((800-80-8-64, 520, 64, 64),
                                    normal = './resources/dollar-coin.png')

    fps = 60
    done = False
    pause = False


    while not done:
        screen.blit(background, (0,0))
        screen.blit(scenery, (0,0))
        time_passed_seconds = clock.tick(fps) / 1000.0

        font = pygame.font.Font(FONT_STYLE,15)
        if not pause:
            current_datetime += datetime.timedelta(minutes = game_speed)
            if np.random.randn() > 0.9:
                cloud_index += 1
                clouds[cloud_index] = Cloud(screen)
            if current_datetime.time() > datetime.time(18,0) or current_datetime.time() < datetime.time(6,30):
                color = (28, 40, 61)
                stars.twinkle()
                screen.blit(stars.image, (0,0))
            else:
                color = (143, 181, 242)
                sun.twinkle()
                screen.blit(sun.image, (500,0))
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
                customers = [Customer(screen, arrival_time_generator, preference_generator) for i in range(n_customers_today)]
                current_date = current_datetime.date()
            screen.blit(analog_clock.bg, analog_clock.loc)
            analog_clock.draw_hands(screen)

            # if the stand is open, update+draw employee
            if current_datetime.time() > lemonade_stand.opening_time \
                        and current_datetime.time() < lemonade_stand.closing_time:
                employee.update()
                screen.blit(employee.image, employee.loc)
            lemonade_stand.draw(current_datetime.time(),screen)

            # for each customer whose arrival time has passed
            for customer in customers:
                if customer.arrival_time < current_datetime.time():
                    customer.move(game_speed)
                    screen.blit(customer.sprite_im, customer.current_loc)
                    #if they're right in front of the stand see if they want to/can purchase
                    if customer.current_loc[0] > int(screen.get_width()/2)-50 and not customer.has_lemonade \
                                                    and customer.likes_recipe:
                        likes_it, reason = customer.customer_likes_recipe(recipe, lemonade_stand.price)
                        # print(likes_it, reason)

                        if not lemonade_stand.has_enough_stuff(recipe):
                            customer.likes_recipe = False
                            recent_customer_thought = 'This lemonade stand is horrifically mismanaged.'

                        elif not likes_it:
                            customer.likes_recipe = False
                            recent_customer_thought = reason

                        else:
                            recent_customer_thought = reason
                            lemonade_stand.lemons -= recipe.lemon_juice / lemonade_stand.juicing_efficiency
                            lemonade_stand.sugar -= recipe.sugar
                            lemonade_stand.account_balance += lemonade_stand.price
                            customer.has_lemonade = True

            analog_clock.current_time = current_datetime
            time_stamp = font.render(str(current_datetime),1,(214, 26, 13))
            current_price = font.render(str(lemonade_stand.price)+' $ / CUP', 1, (214, 26, 13))
            n_lemons = font.render(str(np.round(lemonade_stand.lemons,1))+' LEMONS ON HAND', 1, (214, 26, 13))
            g_sugar = font.render(str(lemonade_stand.sugar)+' g SUGAR ON HAND', 1, (214, 26, 13))
            juice_eff = font.render(f'JUICING EFFICIENCY {str(lemonade_stand.juicing_efficiency)} mL/lemon', 1, (214, 26, 13))
            money = font.render(str(lemonade_stand.account_balance)+' $', 1, (0,0,0))
            thoughts = font.render(recent_customer_thought, 1, (0,0,0))

            screen.blit(time_stamp,[20,20])
            screen.blit(current_price, [20,40])
            screen.blit(juice_eff, [20,60])
            screen.blit(n_lemons, [20,80])
            screen.blit(g_sugar, [20,100])
            screen.blit(money, [20,120])
            screen.blit(thoughts, [10,580])

            recipe_button.draw(screen)
            price_button.draw(screen)
            pygame.display.update()

        for event in pygame.event.get():

            # Close button clicked
            if event.type == pygame.QUIT:
                done = True

            buttonEvents = recipe_button.handleEvent(event)
            if 'click' in buttonEvents:
                recipe_menu(recipe)

            buttonEvents = price_button.handleEvent(event)
            if 'click' in buttonEvents:
                price_menu(lemonade_stand)

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

def recipe_menu(recipe):
    pygame.init()
    pygame.mouse.set_visible(1)
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("LEMONADE")
    done = False
    click = False
    background = create_menu_background(screen)
    recipe_image = pygame.image.load('./resources/background.png') #Update with recipe image
    ingredients = {'lemon juice' : recipe.lemon_juice, 'sugar' : recipe.sugar, 'water' : recipe.water, 'ice' : recipe.ice} #Get this from another class
    ingredient_min, ingredient_max = 0, 500
    recipe_style = ''
    while not done:
        screen.blit(background, (0,0))
        screen.blit(recipe_image, (0,0))

        font = pygame.font.Font(FONT_STYLE,25) #Edit fonts here
        draw_text('Set your recipe', font, (255, 255, 255), screen, 20, 20)

        #Try to make this into a loop through different ingredients
        buttons = [False]*2*len(ingredients)
        index = 0
        x_start, y_start = 20, 100
        button_dimension = 25
        for item, value in ingredients.items():
            item_name_x = x_start
            item_name_y = y_start + index*30 #Next line is 30 down
            button_coords = [(430,y_start + index*30, button_dimension, button_dimension), (480,y_start + index*30, button_dimension, button_dimension), (530,y_start + index*30, button_dimension, button_dimension)]
            draw_text(item, font, (255, 255, 255), screen , item_name_x, item_name_y)
            buttons[index*2] = button(screen, '-', (0,0,0,100), (0,0,0,255), button_coords[0], font, click)
            button(screen, str(value), (0,0,0,0), (0,0,0,0), button_coords[1], font, click)
            buttons[index*2+1] = button(screen, '+', (0,0,0,100), (0,0,0,255), button_coords[2], font, click)
            index +=1
        #Buttons to accept recipe and return to game
        accept_recipe = button(screen, 'Accept Recipe', (0,0,0,100), (0,0,0,255), (50,500,300,50), font, click)
        return_to_game = button(screen, 'Resume Game', (0,0,0,100), (0,0,0,255), (400,500,300,50), font, click)

        if click:
            for i in range(len(buttons)):
                if buttons[i]:
                    if i % 2 != 0:
                        if ingredients[list(ingredients.keys())[int(i/2)]] == ingredient_max:
                            pass
                        else:
                            ingredients[list(ingredients.keys())[int(i/2)]] +=1
                    else:
                        if ingredients[list(ingredients.keys())[int((i+1)/2)]] == ingredient_min:
                            pass
                        else:
                            ingredients[list(ingredients.keys())[int((i+1)/2)]] -=1
            if accept_recipe:
                recipe.update_ratios(ingredients['lemon juice'], ingredients['sugar'], ingredients['water'], ingredients['ice'])
                #Write something about the type of lemonade you're making
                recipe_style = 'The recipe sounds tasty'
            if return_to_game:
                done = True

        click = False
        recipe_message = font.render(recipe_style, 1, (0,0,0))
        screen.blit(recipe_message, [10,380])
        pygame.display.update()

        #Events
        for event in pygame.event.get():
            # Close button clicked
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                #Clicked on start game
                if event.button == 1:
                    click = True
            if event.type == pygame.KEYDOWN:
                # Escape key pressed
                if event.key == pygame.K_ESCAPE:
                    done = True

def price_menu(lemonade_stand):
    pygame.init()
    pygame.mouse.set_visible(1)
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("LEMONADE")
    done = False
    click = False
    background = create_menu_background(screen)
    price_image = pygame.image.load('./resources/background.png') #Update with price image
    price = lemonade_stand.price
    price_min, price_max = 0, 50
    price_style = ''
    while not done:
        screen.blit(background, (0,0))
        screen.blit(price_image, (0,0))

        font = pygame.font.Font(FONT_STYLE,25) #Edit fonts here
        draw_text('Set your price', font, (255, 255, 255), screen, 20, 20)

        x_start, y_start = 20, 100
        button_dimension = 25
        item_name_x = x_start
        item_name_y = y_start
        button_coords = [(430,y_start, button_dimension, button_dimension), (490,y_start, button_dimension, button_dimension), (550,y_start, button_dimension, button_dimension)]
        draw_text('Price', font, (255, 255, 255), screen , item_name_x, item_name_y)
        button_1 = button(screen, '-', (0,0,0,100), (0,0,0,255), button_coords[0], font, click)
        button(screen, str(price), (0,0,0,0), (0,0,0,0), button_coords[1], font, click)
        button_2 = button(screen, '+', (0,0,0,100), (0,0,0,255), button_coords[2], font, click)
        #Buttons to accept recipe and return to game
        accept_price = button(screen, 'Accept Price', (0,0,0,100), (0,0,0,255), (50,500,300,50), font, click)
        return_to_game = button(screen, 'Resume Game', (0,0,0,100), (0,0,0,255), (400,500,300,50), font, click)

        if click:
            if button_1:
                price = round(price - 0.01, 2)
            if button_2:
                price = round(price + 0.01, 2)
            if accept_price:
                lemonade_stand.price = price
                #Write something about the type of lemonade you're making
                price_style = 'The price seems reasonable'
            if return_to_game:
                done = True

        click = False
        price_message = font.render(price_style, 1, (0,0,0))
        screen.blit(price_message, [10,380])
        pygame.display.update()

        #Events
        for event in pygame.event.get():
            # Close button clicked
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                #Clicked on start game
                if event.button == 1:
                    click = True
            if event.type == pygame.KEYDOWN:
                # Escape key pressed
                if event.key == pygame.K_ESCAPE:
                    done = True

def pending_orders():
    pygame.init()
    pygame.mouse.set_visible(1)
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("LEMONADE")
    done = False
    click = False
    background = create_menu_background(screen)
    order_image = pygame.image.load('./resources/background.png') #Update with price image
    while not done:
        screen.blit(background, (0,0))
        screen.blit(order_image, (0,0))

        font = pygame.font.Font(FONT_STYLE,15) #Edit fonts here
        draw_text('Purchase(d) Orders', font, (255, 255, 255), screen, 20, 20)

        draw_text('Pending:', font, (255, 255, 255), screen , 20, 60)
        #Fill in pending orders
        draw_rect_alpha(screen, (0,0,0,100), (10,80,700,100))
        draw_text('item', font, (255, 255, 255), screen , 20, 80)
        draw_text('arrives in', font, (255, 255, 255), screen , 220, 80)
        draw_text('quantity', font, (255, 255, 255), screen , 490, 80)
        #Implement logic to loop through orders and write them to the rectangle

def inventory_menu():
    pygame.init()
    pygame.mouse.set_visible(1)
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("LEMONADE")
    done = False
    click = False
    background = create_menu_background(screen)
    inventory_image = pygame.image.load('./resources/background.png') #Update with recipe image
    lemonadestand = LemonadeStand(screen)
    stock_items = {'lemon juice' : lemonadestand.lemons, 'sugar' : lemonadestand.sugar, 'ice' : lemonadestand.ice} #Get this from another class
    while not done:
        screen.blit(background, (0,0))
        screen.blit(inventory_image, (0,0))

        font = pygame.font.Font(FONT_STYLE,15) #Edit fonts here
        draw_text('Current Inventory', font, (255, 255, 255), screen, 20, 20)

        #Try to make this into a loop through different ingredients
        buttons = [False]*len(stock_items)
        index = 0
        x_start, y_start = 20, 100
        button_h, button_w = 100, 25
        spacing = 100
        for item, value in stock_items.items():
            item_name_x = x_start
            item_name_y = y_start + index*spacing #Next line is 30 down
            item_display = item + ' in stock:'+ str(value) + ', quantity ordered: 100'
            draw_text(item_display, font, (255, 255, 255), screen , item_name_x, item_name_y)
            buttons[index] = button(screen, 'Order', (0,0,0,100), (0,0,0,255), (item_name_x+590,item_name_y+25,button_h,button_w), font, click)
            index += 1
        #Buttons to accept recipe and return to game
        return_to_game = button(screen, 'Resume Game', (0,0,0,100), (0,0,0,255), (400,500,300,50), font, click)
        if click:
            if buttons[0]:
                #lemons
                lemon_order_menu(lemonadestand)
            if buttons[1]:
                #sugar
                pass
            if buttons[2]:
                #ice
                pass
            if return_to_game:
                done = True

        click = False
        pygame.display.update()

        #Events
        for event in pygame.event.get():
            # Close button clicked
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                #Clicked on start game
                if event.button == 1:
                    click = True
            if event.type == pygame.KEYDOWN:
                # Escape key pressed
                if event.key == pygame.K_ESCAPE:
                    done = True

def lemon_order_menu(lemonade_stand):
    pygame.init()
    pygame.mouse.set_visible(1)
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("LEMONADE")
    done = False
    click = False
    background = create_menu_background(screen)
    order_lemon_image = pygame.image.load('./resources/background.png')
    order_message = ''
    possible_orders = [(1,1),(5,2),(10,6),(100,24)]
    order_amounts = [0] * len(possible_orders)
    while not done:
        screen.blit(background, (0,0))
        screen.blit(order_lemon_image, (0,0))
        font = pygame.font.Font(FONT_STYLE,15)
        draw_text('Order Lemons', font, (255, 255, 255), screen, 20, 20)
        draw_text('Quantity', font, (255, 255, 255), screen, 20, 70)
        draw_text('Arrives In', font, (255, 255, 255), screen, 20+200, 70)
        draw_text('Price', font, (255, 255, 255), screen, 20+400, 70)
        draw_text('Order', font, (255, 255, 255), screen, 20+600, 70)

        #Implement menu to order from, times in hours
        amounts_min = 0
        amounts_max = 10
        index = 0
        starting_x = 20
        starting_y = 100
        button_dimension = 25
        buttons = [False] *2*len(possible_orders)
        for order in possible_orders:
            item_name_x = starting_x
            item_name_y = starting_y + index*50
            lemon_price = 2.0 #lemon_discounted_price()
            button_coords = [(item_name_x+600, item_name_y, button_dimension, button_dimension),
                            (item_name_x+640, item_name_y, button_dimension, button_dimension),
                            (item_name_x+680, item_name_y, button_dimension, button_dimension)]

            draw_text(str(order[0]), font, (255, 255, 255), screen , item_name_x, item_name_y)
            draw_text(str(order[1])+' HR', font, (255, 255, 255), screen , item_name_x+200, item_name_y)
            draw_text(str(lemon_price), font, (255, 255, 255), screen , item_name_x+400, item_name_y)
            buttons[index*2] = button(screen, '-', (0,0,0,100), (0,0,0,255), button_coords[0], font, click)
            button(screen, str(order_amounts[index]), (0,0,0,0), (0,0,0,0), button_coords[1], font, click)
            buttons[index*2+1] = button(screen, '+', (0,0,0,100), (0,0,0,255), button_coords[2], font, click)
            index += 1

        place_order = button(screen, 'Place Order', (0,0,0,100), (0,0,0,255), (50,500,300,50), font, click)
        return_to_inventory = button(screen, 'Back', (0,0,0,100), (0,0,0,255), (400,500,300,50), font, click)

        if click:
            for i in range(len(buttons)):
                if buttons[i]:
                    if i % 2 != 0:
                        if order_amounts[int(i/2)] == amounts_max:
                            pass
                        else:
                            order_amounts[int(i/2)] +=1
                    else:
                        if order_amounts[int((i+1)/2)] == amounts_min:
                            pass
                        else:
                            order_amounts[int((i+1)/2)] -=1
            if place_order:
                #Check for enough cash
                
                order_message = 'Order Placed'
            if return_to_inventory:
                done = True
        click = False
        screen.blit(font.render(order_message, 1, (0,0,0)), [10,380])
        pygame.display.update()

        #Events
        for event in pygame.event.get():
            # Close button clicked
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                #Clicked on start game
                if event.button == 1:
                    click = True
            if event.type == pygame.KEYDOWN:
                # Escape key pressed
                if event.key == pygame.K_ESCAPE:
                    done = True

if __name__ == '__main__':
    #main_menu()
    #recipe_menu()
    inventory_menu()
