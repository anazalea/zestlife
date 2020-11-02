
import pygame



class Recipe():
    def __init__(self, lemon_juice, sugar, water, ice, straw=None):
        self.image = pygame.image.load('./resources/recipe.png')
        self.lemon_juice = lemon_juice # ml
        self.sugar = sugar # g
        self.water = water # ml
        self.ice = ice # cubes
        self.straw = straw # ['no', 'plastic', 'paper']
        self.update_ratios()

    def update_ratios(self, lemon_juice=None, sugar=None, water=None, ice=None, straw=None):
        if lemon_juice:
            self.lemon_juice = lemon_juice
        if sugar:
            self.sugar = sugar
        if water:
            self.water = water
        if ice:
            self.ice = ice
        if straw:
            self.straw = straw
        self.total_volume = self.water + self.lemon_juice
        if self.total_volume == 0:
            self.total_volume = 1
        self.sugar_concentration = self.sugar / self.total_volume
        self.lemon_concentration = self.lemon_juice / self.total_volume
        self.ice_concentration = self.ice / self.total_volume
        print(self.total_volume, self.sugar_concentration, self.ice_concentration, self.lemon_concentration)

    def update_lemonjuice(self, value):
        self.lemon_juice = value
        self.update_ratios()

    def validate_lemonjuice(self, value):
        try:
            float(value)
            self.update_lemonjuice(float(value))
            self.update_ratios()
        except:
            print('INVALID LEMON JUICE QUANTITY')

    def update_sugar(self, value):
        self.sugar = value
        self.update_ratios()

    def validate_sugar(self, value):
        try:
            float(value)
            self.update_sugar(float(value))
            self.update_ratios()
        except:
            print('INVALID SUGAR QUANTITY')

    def update_water(self, value):
        self.water = value
        self.update_ratios()

    def validate_water(self, value):
        try:
            float(value)
            self.update_water(float(value))
            self.update_ratios()
        except:
            print('INVALID WATER QUANTITY')

    def update_ice(self, value):
        self.ice = value
        self.update_ratios()

    def validate_ice(self, value):
        try:
            int(value)
            self.update_ice(int(value))
            self.update_ratios()
        except:
            print('INVALID ICE CUBE QUANTITY')

    def update_straw(self, value):
        self.straw = value
        self.update_ratios()

    def validate_straw(self, value, straw):
        try:
            ['no', 'plastic', 'paper'].index(straw)
            self.update_straw(straw)
        except:
            print('INVALID STRAW TYPE')

    def __str__(self):
        pass
        
    
