import pygame
import math
from enemy.enemy_base import Enemy
from settings import *

class ZigzagEnemy(Enemy):
    """ジグザグ敵 - 左右に蛇行しながら降下"""
    def __init__(self, x, y, player, level_multipliers=None, game=None):
        health = 1
        speed = ENEMY_SPEED * 0.8
        
        if level_multipliers:
            health = max(1, int(health * level_multipliers.get('health', 1.0)))
            speed = speed * level_multipliers.get('speed', 1.0)
            
        super().__init__(x, y, player, health, speed, (0, 255, 0), ENEMY_SIZE, game=game)
        self.enemy_type = "zigzag"
        self.score_value = ENEMY_SCORE * 1.5
        self.zigzag_amplitude = 80
        
    def move(self):
        """ジグザグ移動"""
        self.y += self.speed
        # サイン波で左右に移動
        zigzag_offset = math.sin(self.move_timer * 0.1) * self.zigzag_amplitude
        self.x = self.start_x + zigzag_offset
        # 画面端での制限
        width = self.game.current_width if self.game else SCREEN_WIDTH
        self.x = max(self.size//2, min(width - self.size//2, self.x))