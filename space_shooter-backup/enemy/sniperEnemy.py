import pygame
import math
from enemy.enemy_base import Enemy, TargetedBullet
from bullet import Bullet
from settings import *

class SniperEnemy(Enemy):
    """スナイパー敵 - 止まってプレイヤーを狙い撃ち"""
    def __init__(self, x, y, player, level_multipliers=None):
        health = 2
        speed = ENEMY_SPEED * 0.3
        
        if level_multipliers:
            health = max(1, int(health * level_multipliers.get('health', 1.0)))
            speed = speed * level_multipliers.get('speed', 1.0)
            
        super().__init__(x, y, player, health, speed, (128, 0, 128), ENEMY_SIZE)
        self.enemy_type = "sniper"
        self.score_value = ENEMY_SCORE * 2
        self.shoot_interval = 90
        
    def shoot(self):
        """プレイヤーを狙い撃ち"""
        if self.player is not None:
            # プレイヤーの方向を計算
            dx = self.player.x - self.x
            dy = self.player.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                # 正規化して速度を適用
                bullet_speed = BULLET_SPEED
                vx = (dx / distance) * bullet_speed
                vy = (dy / distance) * bullet_speed
                
                return TargetedBullet(self.x, self.y, vx, vy, RED)
        
        # 通常の弾を発射
        return super().shoot()
    
    def draw(self, screen):
        """スナイパー敵は六角形で描画"""
        # 六角形の頂点を計算
        points = []
        for i in range(6):
            angle = i * 60 * math.pi / 180
            px = self.x + (self.size//2) * math.cos(angle)
            py = self.y + (self.size//2) * math.sin(angle)
            points.append((px, py))
        
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, self.outline_color, points, 2)
        
        # 中央に照準マーク
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 3)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 6, 1)
        
        # 体力バー
        self.draw_health_bar(screen)