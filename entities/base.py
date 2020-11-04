from enum import Enum

import pygame
from pygame.math import Vector2


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, position, image_dict, hold_for_n_frames=1, state=None):
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
        self.switch_frames = hold_for_n_frames
        self.frames_at_image = 0
        self.index = 0
        self.image = self.images[self.index]  # 'image' is the current image of the animation.
        self.rect = pygame.Rect(position, (self.image.get_width(), self.image.get_height()))
        self.real_position = Vector2(position)

    def move(self, vector):
        self.real_position += vector
        self.rect[:2] = self.real_position[:2]

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
        self.image = self.images[self.index]

    def next_frame(self):
        self.frames_at_image += 1
        if self.frames_at_image > self.switch_frames:
            self.frames_at_image = 0
            self.index += 1
            self.index %= len(self.images)
            self.image = self.images[self.index]
