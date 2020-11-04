class GameEnvironment():

    def __init__(self, game_objects, screen_size):
        self._game_objects = game_objects
        self._screen_size = screen_size

    @property
    def game_objects(self):
        return self._game_objects

    @property
    def screen_size(self):
        return self._screen_size
