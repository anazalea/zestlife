import pygame


class Sound:
    def __init__(self):
        self.music_channel = pygame.mixer.Channel(0)
        self.music_channel.set_volume(0.2)
        self.sfx_channel = pygame.mixer.Channel(1)
        self.sfx_channel.set_volume(0.2)

        self.allowSFX = True

        # self.soundtrack = mixer.Sound("./sfx/main_theme.ogg")
        self.coin = pygame.mixer.Sound("./resources/coin.ogg")
        # self.bump = mixer.Sound("./sfx/bump.ogg")
        # self.stomp = mixer.Sound("./sfx/stomp.ogg")
        # self.jump = mixer.Sound("./sfx/small_jump.ogg")
        self.death = pygame.mixer.Sound("./resources/death.wav")
        # self.hit = pygame.mixer.Sound("./resources/hit.ogg")
        # self.kick = mixer.Sound("./sfx/kick.ogg")
        # self.brick_bump = mixer.Sound("./sfx/brick-bump.ogg")
        # self.powerup = mixer.Sound('./sfx/powerup.ogg')
        self.powerup_appear = pygame.mixer.Sound('./resources/powerup_appears.ogg')
        self.pipe = pygame.mixer.Sound('./resources/pipe.ogg')
        self.victory = pygame.mixer.Sound('./resources/stage_clear.ogg')

    def play_sfx(self, sfx):
        if self.allowSFX:
            self.sfx_channel.play(sfx)

    def play_music(self, music):
        self.music_channel.play(music)