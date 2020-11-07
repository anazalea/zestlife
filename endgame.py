import pygame
import menus


def check_victory_condition(lemonade_game):
    if lemonade_game.lemonade_stand.account_balance > 0:
        menus.victory_menu(lemonade_game)
        return True
    else:
        return False
