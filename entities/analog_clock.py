import pygame
import math
import datetime

class AnalogClock():
    def __init__(self, current_time, screen):
        self.bg = pygame.image.load('./resources/clcock2.png')
        self.current_time = current_time
        self.height = self.bg.get_height()
        self.width = self.bg.get_width()
        self.radius_m = int(self.height * 0.3)
        self.radius_h = int(self.height * 0.2)
        self.center = [screen.get_width() - int(self.width/2), int(self.height/2)]
        self.loc = [screen.get_width() - self.width, 0]


    def draw(self, screen):
        screen.blit(self.bg, self.loc)
        h = self.current_time.hour % 12
        hour_hand_X = math.cos(math.radians(h*30+270)) * self.radius_h + self.center[0]
        hour_hand_Y = math.sin(math.radians(h*30+270)) * self.radius_h + self.center[1]
        m = self.current_time.minute
        minute_hand_X = math.cos(math.radians(m*6+270)) * self.radius_m + self.center[0]
        minute_hand_Y = math.sin(math.radians(m*6+270)) * self.radius_m + self.center[1]
        pygame.draw.line(screen,[0,0,0],self.center,(hour_hand_X, hour_hand_Y), 2)
        pygame.draw.line(screen,[0,0,0],self.center,(minute_hand_X, minute_hand_Y), 2)