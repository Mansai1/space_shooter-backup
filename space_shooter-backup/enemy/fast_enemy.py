import pygame
from enemy.enemy_base import Enemy
from settings import *

class FastEnemy(Enemy):
    """高速敵"""
    def __init__(self, x, y, player, level_multipliers=None):
        health = 1
        speed = ENEMY_SPEED * 2.5
        
        if level_multipliers:
            health = max(1, int(health * level_multipliers.get('health', 1.0)))
            speed = speed * level_multipliers.get('speed', 1.0)
            
        super().__init__(x, y, player, health, speed, (255, 165, 0), ENEMY_SIZE - 5)
        self.enemy_type = "fast"
        self.score_value = ENEMY_SCORE * 2
        
    def should_shoot(self):
        """高速敵は弾を撃たない（突進重視）"""
        return False