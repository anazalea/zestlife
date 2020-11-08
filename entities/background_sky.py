from datetime import datetime

import pygame

class BackgroundSky():
    def __init__(self, current_time, screen):
        self.background = pygame.Surface(screen.get_size())
        self.background = self.background.convert()
        self._sky_color_img = pygame.image.load('./resources/sky_color.png')
        self._sun_img = pygame.image.load('./resources/sun.png')
        self.update_color(current_time)

    def update_color(self, current_time: datetime):
        self.background.fill(
            self._sky_color_img.get_at((current_time.hour * 4 + current_time.minute // 15, 0))
        )

        if 4 <= current_time.hour <= 20:
            x = current_time.hour + current_time.minute / 60
            y = -(x/2 - 6) ** 2 + 16  # 0 to 16 curve
            self.background.blit(self._sun_img, (650 - (x - 4) * 43, 200 - y * 20))
