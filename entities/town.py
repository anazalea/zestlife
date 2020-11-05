import datetime
import pygame

class Town():
    def __init__(self, current_time):
        self.image_day = pygame.image.load('./resources/Background_day.png')
        self.image_night = pygame.image.load('./resources/Background_night.png')
        self.update_town_time(current_time)

    def update_town_time(self, current_time):
        if current_time > datetime.time(20) or current_time < datetime.time(6):
            self.image = self.image_night
        else:
            self.image = self.image_day

    def draw(self, screen):
        screen.blit(self.image, (0,0))

        