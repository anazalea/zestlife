import pygame
from datetime import timedelta

from inventory import Order
import pricing
from entities.lemonadestand import (
    get_stand_downgrade, get_stand_upgrade, StandType, get_stand_config,
    UPGRADE_COST as stand_upgrade_cost,
    DOWNGRADE_REFUND as stand_downgrade_refund
)

#Constants
FONT_STYLE = './resources/joystix-monospace.ttf'
MENU_BG = pygame.image.load('./resources/menu_background.png')
RGB_WHITE = (255, 255, 255)
RGB_RED = (255, 0, 0)

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

def create_menu_background(screen):
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    color = (143, 181, 242)
    background.fill(color)
    return background

def update_straw_button_highlight(straw):
    if straw == 'no':
        return pygame.rect.Rect(13,298,204,34)
    if straw == 'paper':
        return pygame.rect.Rect(233,298,254,34)
    if straw == 'plastic':
        return pygame.rect.Rect(508,298,279,34)




def recipe_menu(lemonade_game):
    screen = lemonade_game.screen
    background = create_menu_background(screen)
    recipe = lemonade_game.recipe
    ingredients = {'lemon juice [mL]' : recipe.lemon_juice, 'sugar [g]' : recipe.sugar, 'water [mL]' : recipe.water,\
                         'ice [units]' : recipe.ice, 'straw': recipe.straw} #Get this from another class
    straw_highlight = update_straw_button_highlight(ingredients['straw'])
    ingredient_min, ingredient_max = 0, 500
    recipe_message = ''
    done = False
    click = False
    while not done:
        screen.blit(background, (0,0))
        screen.blit(MENU_BG, (0,0))

        font = pygame.font.Font(FONT_STYLE,25) #Edit fonts here
        draw_text('Set your recipe', font, (255, 255, 255), screen, 20, 20)

        #Try to make this into a loop through different ingredients
        buttons = [False]*2*len(ingredients)
        index = 0
        x_start, y_start = 20, 100
        button_dimension = 25
        for item, value in ingredients.items():
            if item != 'straw':
                item_name_x = x_start
                item_name_y = y_start + index*30 #Next line is 30 down
                button_coords = [(430,y_start + index*30, button_dimension, button_dimension), (480,y_start + index*30, button_dimension, button_dimension), (530,y_start + index*30, button_dimension, button_dimension)]
                draw_text(item, font, (255, 255, 255), screen , item_name_x, item_name_y)
                buttons[index*2] = button(screen, '-', (0,0,0,100), (0,0,0,255), button_coords[0], font, click)
                button(screen, str(value), (0,0,0,0), (0,0,0,0), button_coords[1], font, click)
                buttons[index*2+1] = button(screen, '+', (0,0,0,100), (0,0,0,255), button_coords[2], font, click)
                index +=1
        pygame.draw.rect(screen, (255,0,0), straw_highlight)
        no_straw = button(screen, "No Straw",(0,0,0,100), (0,0,0,255), (15,300,200,30), font, click)
        paper_straw = button(screen, "Paper Straw",(0,0,0,100), (0,0,0,255), (235,300,250,30), font, click)
        plastic_straw = button(screen, "Plastic Straw",(0,0,0,100), (0,0,0,255), (510,300,275,30), font, click)

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

            if no_straw:
                ingredients['straw'] = 'no'
                straw_highlight = update_straw_button_highlight(ingredients['straw'])
            if paper_straw:
                ingredients['straw'] = 'paper'
                straw_highlight = update_straw_button_highlight(ingredients['straw'])
            if plastic_straw:
                ingredients['straw'] = 'plastic'
                straw_highlight = update_straw_button_highlight(ingredients['straw'])

            if accept_recipe:

                recipe.update_ratios(ingredients['lemon juice [mL]'], ingredients['sugar [g]'], ingredients['water [mL]'], 
                                            ingredients['ice [units]'], ingredients['straw'])

                #Write something about the type of lemonade you're making
                recipe_message = 'The recipe sounds tasty'
            if return_to_game:
                done = True

        click = False
        screen.blit(font.render(recipe_message, 1, (0,0,0)), [10,380])
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

def price_menu(lemonade_game):
    screen = lemonade_game.screen
    background = create_menu_background(screen)
    price_image = pygame.image.load('./resources/background.png') #Update with price image
    lemonade_stand = lemonade_game.lemonade_stand
    price = lemonade_stand.price
    price_min, price_max = 0, 50
    price_message = ''
    done = False
    click = False
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
        draw_text('Price [$]', font, (255, 255, 255), screen , item_name_x, item_name_y)
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
                price_message = 'The price seems reasonable'
            if return_to_game:
                done = True

        click = False
        screen.blit(font.render(price_message, 1, (0,0,0)), [10,380])
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

def inventory_menu(lemonade_game):
    screen = lemonade_game.screen
    background = create_menu_background(screen)
    inventory_image = pygame.image.load('./resources/background.png') #Update with recipe image
    lemonade_stand = lemonade_game.lemonade_stand
    stock_items = {'lemons [units]' : lemonade_stand.lemonstock.current_units, 'sugar [g]' : lemonade_stand.sugarstock.current_units, 'ice [units]' : lemonade_stand.icestock.current_units} #Get this from another class
    done = False
    click = False
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
            item_display = item + ' in stock:'+ str(round(value)) #+ ', quantity ordered:' + str(round(value))
            draw_text(item_display, font, (255, 255, 255), screen , item_name_x, item_name_y)
            buttons[index] = button(screen, 'Order', (0,0,0,100), (0,0,0,255), (item_name_x+590,item_name_y+25,button_h,button_w), font, click)
            index += 1
        #Buttons to accept recipe and return to game
        return_to_game = button(screen, 'Resume Game', (0,0,0,100), (0,0,0,255), (400,500,300,50), font, click)
        if click:
            if buttons[0]:
                #lemons
                lemon_order_menu(lemonade_game)
            if buttons[1]:
                #sugar
                sugar_order_menu(lemonade_game)
            if buttons[2]:
                #ice
                ice_order_menu(lemonade_game)
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

def lemon_order_menu(lemonade_game):
    screen = lemonade_game.screen
    background = create_menu_background(screen)
    order_lemon_image = pygame.image.load('./resources/background.png')
    order_message = ''
    #(amount, time(hrs))
    possible_orders = [(1,1),(5,2),(10,6),(100,24)]
    order_amounts = [0] * len(possible_orders)
    lemonade_stand = lemonade_game.lemonade_stand
    done = False
    click = False
    while not done:
        screen.blit(background, (0,0))
        screen.blit(order_lemon_image, (0,0))
        font = pygame.font.Font(FONT_STYLE,15)
        draw_text('Order Lemons', font, (255, 255, 255), screen, 20, 20)
        draw_text('Quantity [units]', font, (255, 255, 255), screen, 20, 70)
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
        prices = []
        for order in possible_orders:
            item_name_x = starting_x
            item_name_y = starting_y + index*50
            lemon_price = round(pricing.get_lemon_discountedprice(timedelta(hours=order[1]), order[0]),2)
            prices.append(lemon_price)
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
                #Calculate cost
                total_cost = 0
                for i in range(len(order_amounts)):
                    total_cost += order_amounts[i]*prices[i]
                print(total_cost)
                #Check for enough cash
                if total_cost <= lemonade_stand.account_balance:
                    order_message = 'Order Placed'
                    #Do the orders
                    index = 0
                    for order in possible_orders:
                        if order_amounts[index] != 0:
                            order_num = 0
                            while order_num < order_amounts[index]:
                                lemon_order = Order(order_dt=lemonade_game.current_datetime, delivery_dt=lemonade_game.current_datetime+timedelta(hours=order[1]), amount=order[0])
                                lemonade_stand.lemonstock.add_order(lemon_order)
                                order_num += 1
                        index += 1
                    #Pay
                    lemonade_stand.account_balance -= total_cost
                else:
                    order_message = 'Order too expensive'
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

def sugar_order_menu(lemonade_game):
    screen = lemonade_game.screen
    background = create_menu_background(screen)
    order_sugar_image = pygame.image.load('./resources/background.png')
    order_message = ''
    #(amount, time(hrs))
    possible_orders = [(100,1),(250,2),(500,6),(1000,24)]
    order_amounts = [0] * len(possible_orders)
    lemonade_stand = lemonade_game.lemonade_stand
    done = False
    click = False
    while not done:
        screen.blit(background, (0,0))
        screen.blit(order_sugar_image, (0,0))
        font = pygame.font.Font(FONT_STYLE,15)
        draw_text('Order Sugar', font, (255, 255, 255), screen, 20, 20)
        draw_text('Quantity [g]', font, (255, 255, 255), screen, 20, 70)
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
        prices = []
        for order in possible_orders:
            item_name_x = starting_x
            item_name_y = starting_y + index*50
            #Convert amount ordered to kg so pricing makes sense
            sugar_price = round(pricing.get_sugar_discountedprice(timedelta(hours=order[1]), order[0]/1000),2)
            prices.append(sugar_price)
            button_coords = [(item_name_x+600, item_name_y, button_dimension, button_dimension),
                            (item_name_x+640, item_name_y, button_dimension, button_dimension),
                            (item_name_x+680, item_name_y, button_dimension, button_dimension)]

            draw_text(str(order[0]), font, (255, 255, 255), screen , item_name_x, item_name_y)
            draw_text(str(order[1])+' HR', font, (255, 255, 255), screen , item_name_x+200, item_name_y)
            draw_text(str(sugar_price), font, (255, 255, 255), screen , item_name_x+400, item_name_y)
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
                #Calculate cost
                total_cost = 0
                for i in range(len(order_amounts)):
                    total_cost += order_amounts[i]*prices[i]
                print(total_cost)
                #Check for enough cash
                if total_cost <= lemonade_stand.account_balance:
                    order_message = 'Order Placed'
                    #Do the orders
                    index = 0
                    for order in possible_orders:
                        if order_amounts[index] != 0:
                            order_num = 0
                            while order_num < order_amounts[index]:
                                sugar_order = Order(order_dt=lemonade_game.current_datetime, delivery_dt=lemonade_game.current_datetime+timedelta(hours=order[1]), amount=order[0])
                                lemonade_stand.sugarstock.add_order(sugar_order)
                                order_num += 1
                        index += 1
                    #Pay
                    lemonade_stand.account_balance -= total_cost
                else:
                    order_message = 'Order too expensive'
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

def ice_order_menu(lemonade_game):
    screen = lemonade_game.screen
    background = create_menu_background(screen)
    order_ice_image = pygame.image.load('./resources/background.png')
    order_message = ''
    #(amount, time(hrs))
    possible_orders = [(50,4),(100,8),(200,10),(500,12)]
    order_amounts = [0] * len(possible_orders)
    lemonade_stand = lemonade_game.lemonade_stand
    done = False
    click = False
    while not done:
        screen.blit(background, (0,0))
        screen.blit(order_ice_image, (0,0))
        font = pygame.font.Font(FONT_STYLE,15)
        draw_text('Order Ice', font, (255, 255, 255), screen, 20, 20)
        draw_text('Quantity [units]', font, (255, 255, 255), screen, 20, 70)
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
        prices = []
        for order in possible_orders:
            item_name_x = starting_x
            item_name_y = starting_y + index*50
            ice_price = 0
            prices.append(ice_price)
            button_coords = [(item_name_x+600, item_name_y, button_dimension, button_dimension),
                            (item_name_x+640, item_name_y, button_dimension, button_dimension),
                            (item_name_x+680, item_name_y, button_dimension, button_dimension)]

            draw_text(str(order[0]), font, (255, 255, 255), screen , item_name_x, item_name_y)
            draw_text(str(order[1])+' HR', font, (255, 255, 255), screen , item_name_x+200, item_name_y)
            draw_text(str(ice_price), font, (255, 255, 255), screen , item_name_x+400, item_name_y)
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
                #Calculate cost
                total_cost = 0
                for i in range(len(order_amounts)):
                    total_cost += order_amounts[i]*prices[i]
                print(total_cost)
                #Check for enough cash
                if total_cost <= lemonade_stand.account_balance:
                    order_message = 'Order Placed'
                    #Do the orders
                    index = 0
                    for order in possible_orders:
                        if order_amounts[index] != 0:
                            order_num = 0
                            while order_num < order_amounts[index]:
                                ice_order = Order(order_dt=lemonade_game.current_datetime, delivery_dt=lemonade_game.current_datetime+timedelta(hours=order[1]), amount=order[0])
                                lemonade_stand.icestock.add_order(ice_order)
                                order_num += 1
                        index += 1
                    #Pay
                    lemonade_stand.account_balance -= total_cost
                else:
                    order_message = 'Order too expensive'
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

def employee_menu(lemonade_game):
    screen = lemonade_game.screen
    background = create_menu_background(screen)
    employee_image = pygame.image.load('./resources/background.png')
    lemonade_stand = lemonade_game.lemonade_stand
    wages = [20, 30, 40]
    done = False
    click = False
    while not done:
        current_employees = lemonade_stand.get_current_employees() #Get employees
        employee_count = [0, 0, 0]
        for employee in current_employees:
            if employee.get_daily_wage() == wages[0]:
                employee_count[0] += 1
            elif employee.get_daily_wage() == wages[1]:
                employee_count[1] += 1
            else:
                employee_count[2] += 1
        screen.blit(background, (0,0))
        screen.blit(employee_image, (0,0))

        font = pygame.font.Font(FONT_STYLE,15) #Edit fonts here
        draw_text('Current Staff', font, (255, 255, 255), screen, 20, 20)

        #Try to make this into a loop through different employee wage
        buttons = [False]*len(wages)*2
        index = 0
        x_start, y_start = 20, 100
        button_h, button_w = 75, 25
        spacing = 100
        for i in range(len(wages)):
            item_name_x = x_start
            item_name_y = y_start + index*spacing #Next line is 30 down
            item_display = str(employee_count[i]) + ' employees paid at '+ str(wages[i]) + ' $/day'#+ ', quantity ordered:' + str(round(value))
            draw_text(item_display, font, (255, 255, 255), screen , item_name_x, item_name_y)
            buttons[index*2] = button(screen, 'Fire', (0,0,0,100), (0,0,0,255), (item_name_x+290,item_name_y+25,button_h,button_w), font, click)
            buttons[index*2+1] = button(screen, 'Hire', (0,0,0,100), (0,0,0,255), (item_name_x+390,item_name_y+25,button_h,button_w), font, click)
            index += 1
        #Buttons to accept recipe and return to game
        return_to_game = button(screen, 'Resume Game', (0,0,0,100), (0,0,0,255), (400,500,300,50), font, click)
        if click:
            for i in range(len(buttons)):
                if buttons[i]:
                    if i % 2 == 0:
                        lemonade_stand.fire_employee(lemonade_stand.employee_image_dict,lemonade_game.current_datetime.time(),wages[int(i/2)])
                    else:
                        lemonade_stand.hire_employee(lemonade_stand.opening_time,lemonade_stand.closing_time,lemonade_stand.employee_image_dict,lemonade_game.current_datetime.time(),wages[int((i-1)/2)])
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

# from entities.lemonadegame import LemonadeGame # circular import
# def upgrade_menu(lemonade_game: LemonadeGame):

def upgrade_menu(lemonade_game):
    screen = lemonade_game.screen
    background = create_menu_background(screen)
    stand_image = pygame.image.load('./resources/background_upgrade_stand_menu.png')
    lemonade_stand = lemonade_game.lemonade_stand

    # current and upgrade/downgrade paths
    current_stand_type = lemonade_stand.stand_type
    upgrade_stand_type = get_stand_upgrade(current_stand_type)
    downgrade_stand_type = get_stand_downgrade(current_stand_type)
    can_upgrade = upgrade_stand_type != current_stand_type
    can_downgrade = downgrade_stand_type != current_stand_type
    can_pay_for_upgrade = stand_upgrade_cost <= lemonade_stand.account_balance
    print ('{} <- {} -> {}'.format(downgrade_stand_type, current_stand_type, upgrade_stand_type))
    print ('can_pay_for_upgrade: {}'.format(can_pay_for_upgrade))
    # get current and upgrad/downgrade details
    current_stand_config = get_stand_config(current_stand_type)
    upgrade_stand_config = get_stand_config(upgrade_stand_type)
    downgrade_stand_config = get_stand_config(downgrade_stand_type)


    done = False
    click = False
    fontsize = 20
    font = pygame.font.Font(FONT_STYLE, fontsize)
    while not done:
        screen.blit(background, (0,0))
        screen.blit(stand_image, (0,0))

        left_margin = 20
        top_margin = 20

        draw_text('Upgrade your stand', font, RGB_WHITE, screen, left_margin, top_margin)
        button_w, button_h = 15*fontsize, fontsize
        active_color, inactive_color = (0, 0, 0, 100), (0, 0, 0, 255)
        mid_x = 400

        # buttons
        downgrade_button = button(screen, 'Downgrade (+${})'.format(stand_downgrade_refund if can_downgrade else 0),
                                  active_color, inactive_color,
                                  (left_margin, 50, button_w, button_h),
                                  font, click)
        upgrade_button = button(screen, 'Upgrade (-${})'.format(stand_upgrade_cost if can_upgrade else 0),
                                active_color if can_pay_for_upgrade else RGB_RED,
                                inactive_color if can_pay_for_upgrade else RGB_RED,
                                (mid_x, 50, button_w, button_h),
                                font, click)
        draw_text(
            'Juicing Efficiency: {} <- {} -> {}'.format(
                downgrade_stand_config.juicing_efficiency,
                current_stand_config.juicing_efficiency,
                upgrade_stand_config.juicing_efficiency,
            ),
            font, RGB_WHITE, screen , left_margin, 100
        )
        draw_text(
            'Lemon Capacity:     {} <- {} -> {}'.format(
                downgrade_stand_config.lemon_capacity,
                current_stand_config.lemon_capacity,
                upgrade_stand_config.lemon_capacity,
            ),
            font, RGB_WHITE, screen , left_margin, 120
        )
        draw_text(
            'Sugar Capacity:     {} <- {} -> {}'.format(
                downgrade_stand_config.sugar_capacity,
                current_stand_config.sugar_capacity,
                upgrade_stand_config.sugar_capacity,
            ),
            font, RGB_WHITE, screen , left_margin, 140
        )
        draw_text(
            'Ice Capacity:       {} <- {} -> {}'.format(
                downgrade_stand_config.ice_capacity,
                current_stand_config.ice_capacity,
                upgrade_stand_config.ice_capacity,
            ),
            font, RGB_WHITE, screen , left_margin, 160
        )
        return_to_game = button(screen, 'Resume Game',
                                active_color, inactive_color,
                                (400,500,300,50),
                                font, click)
        if click:
            if downgrade_button:
                lemonade_stand.downgrade_stand(dt=lemonade_game.current_datetime)
                done = True
            if upgrade_button:
                if can_pay_for_upgrade:
                    lemonade_stand.upgrade_stand(dt=lemonade_game.current_datetime)
            if any([return_to_game, downgrade_button, upgrade_button]):
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

def daily_report_menu(lemonade_game):
    screen = lemonade_game.screen
    done = False
    font = pygame.font.Font(FONT_STYLE, 15)
    title_font = pygame.font.Font(FONT_STYLE, 30)
    days_operating = str((lemonade_game.current_datetime - lemonade_game.start_datetime).days)
    while not done:
        screen.blit(MENU_BG, (0, 0))
        draw_text("DAILY REPORT", title_font, (255, 255, 0), screen, 250, 20)
        top_margin = 80
        line_space = 20
        for i, line in enumerate(lemonade_game.daily_report):
            draw_text(line, font, (255, 255, 255), screen, 40, top_margin + i * line_space)
        draw_text(f'{days_operating} days in operation', font, (255, 255, 255), screen, 40, top_margin + (i+2) * line_space)
        draw_text("Press any key to continue.", font, (0, 0, 0), screen, 250, 560)

        pygame.display.update()

        # Events
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN or  event.type == pygame.KEYDOWN:
                done = True
