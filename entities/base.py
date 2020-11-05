from enum import Enum
from typing import List, Optional, Dict

import pygame
from pygame.math import Vector2
from pygame.surface import Surface


def get_flipped_version(image: Surface, flip: bool = False) -> Surface:
    return image if not flip else pygame.transform.flip(image, True, False)


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, position, image_dict, hold_for_n_frames=1, state=None,
                 flip: bool = False,
                 accessory_images=None,
                 visible_accessories=None):
        """
        Animated sprite object.

        Args:
            position: x, y coordinate on the screen to place the AnimatedSprite.
            image_dict: Images to use in the animation. It's a dictionary of state names as key and
                a list of images as values.
            state: An state for the state of the object
            accessory_images(dict): a dict with name of the accessory as the key and a tuple
                (p, im) containing the relative position (p) and the image (im)
            visible_accessories(set): a subset of accessory_images keys that will be visible

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
        self.flip = flip

        self._accessory_images = accessory_images if accessory_images else {}
        self._visible_accessories = visible_accessories if visible_accessories else set()
        if any(v not in self._accessory_images for v in self._visible_accessories):
            raise ValueError("visible_accessories must be a subset of accessory_images.keys()")
        self.update_images_with_accessories()

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
        self.update_images_with_accessories()
        self.image = self.images[self.index]

    def next_frame(self):
        self.frames_at_image += 1
        if self.frames_at_image > self.switch_frames:
            self.frames_at_image = 0
            self.index += 1
            self.index %= len(self.images)
            self.image = get_flipped_version(self.images[self.index], self.flip)

    def check_acc_key(self, ac_key):
        if ac_key not in self._accessory_images:
            raise ValueError("ac_key must be a member of accessory_images.keys()")

    def show_accessory(self, ac_key):
        self.check_acc_key(ac_key)

        self._visible_accessories.add(ac_key)
        self.update_images_with_accessories()

    def hide_accessory(self, ac_key):
        self._visible_accessories.remove(ac_key)
        self.update_images_with_accessories()

    def clear_accessories(self):
        self._visible_accessories = set()

    def update_images_with_accessories(self):
        """More like modifies self.images with appended accessories."""
        images = []
        for m in self.image_dict[self.state]:
            m = m.copy()
            for ac in self._visible_accessories:
                ac_pos, ac_img = self._accessory_images[ac]
                m.blit(ac_img, ac_pos)
            images.append(m)
        self.images = images
