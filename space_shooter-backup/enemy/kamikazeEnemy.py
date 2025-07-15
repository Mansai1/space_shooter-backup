import pygame
import math
from enemy.enemy_base import Enemy
from settings import *

class KamikazeEnemy(Enemy):
    """カミカゼ敵 - プレイヤーに向かって突進"""
    def __init__(self, x, y, player, level_multipliers=None):
        health = 1
        speed = ENEMY_SPEED * 4
        
        if level_multipliers:
            health = max(1, int(health * level_multipliers.get('health', 1.0)))
            speed = speed * level_multipliers.get('speed', 1.0)
            
        super().__init__(x, y, player, health, speed, (255, 0, 255), ENEMY_SIZE)
        self.enemy_type = "kamikaze"
        self.score_value = ENEMY_SCORE * 3
        
        # ターゲット方向の計算
        if player is not None:
            dx = player.x - x
            dy = player.y - y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                self.vel_x = (dx / distance) * self.speed
                self.vel_y = (dy / distance) * self.speed
            else:
                self.vel_x = 0
                self.vel_y = self.speed
        else:
            self.vel_x = 0
            self.vel_y = self.speed
            
    def move(self):
        """プレイヤー方向に突進"""
        self.x += self.vel_x
        self.y += self.vel_y
        
    def should_shoot(self):
        """カミカゼは弾を撃たない（体当たり重視）"""
        return False
    
    def draw(self, screen):
        """カミカゼ敵は三角形で描画"""
        # 三角形の頂点を計算
        points = [
            (self.x, self.y - self.size//2),
            (self.x - self.size//2, self.y + self.size//2),
            (self.x + self.size//2, self.y + self.size//2)
        ]
        
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, self.outline_color, points, 2)
        
        # 敵の目を描画
        eye_size = 2
        pygame.draw.circle(screen, WHITE, 
                         (int(self.x - self.size//6), int(self.y - self.size//6)), eye_size)
        pygame.draw.circle(screen, WHITE, 
                         (int(self.x + self.size//6), int(self.y - self.size//6)), eye_size)