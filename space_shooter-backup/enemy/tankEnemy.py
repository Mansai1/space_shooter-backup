import pygame
import random
from enemy.enemy_base import Enemy
from settings import *

class TankEnemy(Enemy):
    """タンク敵 - 大きくて遅い、体力が多い、連射してくる"""
    def __init__(self, x, y, player, level_multipliers=None):
        health = 10
        speed = ENEMY_SPEED * 0.4
        
        if level_multipliers:
            health = max(1, int(health * level_multipliers.get('health', 1.0)))
            speed = speed * level_multipliers.get('speed', 1.0)
            
        super().__init__(x, y, player, health, speed, (139, 69, 19), int(ENEMY_SIZE * 1.5))
        self.enemy_type = "tank"
        self.score_value = ENEMY_SCORE * 4
        self.shoot_interval = 30
        self.burst_count = 0
        self.burst_max = 3
        
    def should_shoot(self):
        """連射パターンで射撃"""
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0
            self.burst_count += 1
            if self.burst_count >= self.burst_max:
                self.burst_count = 0
                self.shoot_interval = random.randint(90, 150)
            else:
                self.shoot_interval = 15
            return True
        return False
    
    def draw(self, screen):
        """タンク敵は正方形＋砲塔で描画"""
        # メイン部分
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, self.outline_color, self.rect, 3)
        
        # 砲塔
        turret_size = self.size // 3
        turret_rect = pygame.Rect(self.x - turret_size//2, self.y - turret_size//2, 
                                turret_size, turret_size)
        pygame.draw.rect(screen, (100, 50, 0), turret_rect)
        pygame.draw.rect(screen, self.outline_color, turret_rect, 2)
        
        # 砲身
        pygame.draw.rect(screen, (80, 40, 0), 
                        (self.x - 2, self.y, 4, self.size//2))
        
        # 体力バー
        self.draw_health_bar(screen)