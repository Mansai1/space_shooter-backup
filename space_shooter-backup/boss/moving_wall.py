import pygame
import random
from settings import *

class MovingWall(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 20
        self.height = 150
        self.speed = 3
        
        # 出現位置と移動方向をランダムに決定
        if random.random() > 0.5:
            # 左から出現
            self.x = -self.width
            self.direction = 1
        else:
            # 右から出現
            self.x = SCREEN_WIDTH
            self.direction = -1
            
        self.y = random.randint(0, SCREEN_HEIGHT - self.height)
        
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill((200, 200, 200)) # 壁の色
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

    def update(self):
        self.rect.x += self.speed * self.direction
        
        # 画面外に出たら消滅
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
