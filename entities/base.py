from enum import Enum

import pygame
from pygame.math import Vector2


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, position, image_dict, state=None, velocity: Vector2 = None):
        """
        Animated sprite object.

        Args:
            position: x, y coordinate on the screen to place the AnimatedSprite.
            image_dict: Images to use in the animation. It's a dictionary of state names as key and
                a list of images as values.
            state: An state for the state of the object

        """
        super(AnimatedSprite, self).__init__()

        if state is None:
            self._state = list(image_dict.keys())[0]
        elif isinstance(state, Enum):
            self._state = state.value
        else:
            self._state = state

        self.image_dict = image_dict
        self.images = image_dict[self.state]
        # self.images_left = [pygame.transform.flip(image, True, False) for image in
        #                     image_dict]  # Flipping every image.
        self.index = 0
        self.image = self.images[self.index]  # 'image' is the current image of the animation.
        self.rect = pygame.Rect(position, (self.image.get_width(), self.image.get_height()))

        if velocity is None:
            self.velocity = Vector2(0, 0)
        else:
            self.velocity = velocity

        self.animation_time = 0.1
        self.current_time = 0

        self.animation_frames = 6
        self.current_frame = 0

    def move(self):
        pass

    def destroy(self):
        pass

    def draw(self):
        pass

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if isinstance(value, Enum):
            value = value.value

        if value not in self.image_dict:
            raise ValueError("Provided state is not amongst the initialized images.")

        self._state = value
        self.images = self.image_dict[self._state]
        self.image = self.images[0]

    def next_frame(self):
        self.index += 1
        self.index %= len(self.images)
        self.image = self.images[self.index]
