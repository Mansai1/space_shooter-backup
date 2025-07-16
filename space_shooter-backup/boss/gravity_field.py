import pygame
import math
import random
from settings import *

class GravityField:
    def __init__(self):
        self.x = random.randint(100, SCREEN_WIDTH - 100)
        self.y = random.randint(100, SCREEN_HEIGHT - 100)
        self.radius = 80
        self.strength = 0.5
        self.move_speed = 1.5 # 重力場の移動速度を上げる
        self.direction = random.uniform(0, 2 * math.pi)
        self.color = (150, 150, 255, 100) # 半透明の青
        self.surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.surface, self.color, (self.radius, self.radius), self.radius)

    def update(self):
        # ゆっくり移動
        self.x += self.move_speed * math.cos(self.direction)
        self.y += self.move_speed * math.sin(self.direction)

        # 画面端で反射
        if self.x - self.radius < 0 or self.x + self.radius > SCREEN_WIDTH:
            self.direction = math.pi - self.direction
        if self.y - self.radius < 0 or self.y + self.radius > SCREEN_HEIGHT:
            self.direction = -self.direction

    def draw(self, screen):
        screen.blit(self.surface, (self.x - self.radius, self.y - self.radius))

    def apply_force(self, bullet):
        dx = self.x - bullet.x
        dy = self.y - bullet.y
        distance_sq = dx*dx + dy*dy

        if distance_sq < self.radius*self.radius:
            distance = math.sqrt(distance_sq)
            if distance == 0: return

            # 重力の影響を計算
            force = self.strength * (1 - distance / self.radius)
            force_x = force * (dx / distance)
            force_y = force * (dy / distance)

            # 弾の速度に影響を与える
            bullet.vx += force_x
            bullet.vy += force_y
