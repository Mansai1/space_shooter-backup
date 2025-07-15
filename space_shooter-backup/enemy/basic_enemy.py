import pygame
from enemy.enemy_base import Enemy
from settings import *

class BasicEnemy(Enemy):
    """基本的な敵"""
    def __init__(self, x, y, player, level_multipliers=None):
        health = 1
        speed = ENEMY_SPEED
        
        if level_multipliers:
            health = max(1, int(health * level_multipliers.get('health', 1.0)))
            speed = speed * level_multipliers.get('speed', 1.0)
            
        super().__init__(x, y, player, health, speed, RED, ENEMY_SIZE)
        self.enemy_type = "basic"
        self.score_value = ENEMY_SCORE