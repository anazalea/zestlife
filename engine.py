from entities.environment import GameEnvironment


class Engine():

    def draw_background():
        """draw any non-interactive object"""
        pass


    def tick(e: GameEnvironment):
        """Update the state every entity in the game"""
        for o in e.game_objects:
            o.update()
            o.move()
