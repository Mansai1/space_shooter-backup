import pygame
import math
import random
from enemy.enemy_base import Enemy
from bullet import Bullet
from settings import *

class BarrageEnemy(Enemy):
    """弾幕を放つ特殊な敵"""
    def __init__(self, x, y, player, level_multipliers=None):
        health = 5 # 少しタフにする
        speed = ENEMY_SPEED * 0.8 # 少し遅め
        
        if level_multipliers:
            health = max(1, int(health * level_multipliers.get('health', 1.0)))
            speed = speed * level_multipliers.get('speed', 1.0)
            
        super().__init__(x, y, player, health, speed, PURPLE, ENEMY_SIZE * 1.2) # 紫色で少し大きく
        self.enemy_type = "barrage"
        self.score_value = ENEMY_SCORE * 3
        
        # 弾幕用のタイマー
        self.barrage_cooldown = random.randint(180, 240) # 3〜4秒に1回
        self.barrage_timer = self.barrage_cooldown
        
        # 移動パターン
        self.state = "descending" # descending, holding
        self.hold_y = random.randint(SCREEN_HEIGHT // 5, SCREEN_HEIGHT // 3)

    def move(self):
        """移動ロジック"""
        if self.state == "descending":
            self.y += self.speed
            if self.y >= self.hold_y:
                self.state = "holding" # 指定位置で停止
        elif self.state == "holding":
            # 左右にゆっくり揺れる
            self.x += math.sin(self.y / 20 + self.barrage_timer * 0.1) * 0.5
    
    def update(self):
        """敵の更新処理をオーバーライド"""
        self.move()

        # 弾幕の発射判定
        bullets = []
        if self.state == "holding":
            self.barrage_timer -= 1
            if self.barrage_timer <= 0:
                bullets = self.shoot_barrage()
                self.barrage_timer = self.barrage_cooldown # タイマーリセット
        
        return bullets # 弾幕リストを返す (空の場合もある)

    def should_shoot(self):
        """この敵は通常弾を撃たないのでFalseを返す"""
        return False

    def shoot_barrage(self):
        """円形の弾幕を生成"""
        bullets = []
        num_bullets = 16
        for i in range(num_bullets):
            angle_deg = i * (360 / num_bullets) # 角度を度数法で計算
            bullets.append(Bullet(self.x, self.y, player_bullet=False, angle_override=angle_deg, bullet_type="boss"))
        return bullets

    def draw(self, screen):
        """弾幕敵の描画（菱形）"""
        points = [(self.x, self.y - self.size//2), (self.x + self.size//2, self.y),
                  (self.x, self.y + self.size//2), (self.x - self.size//2, self.y)]
        pygame.draw.polygon(screen, self.color, points)
        if hasattr(self, 'outline_color'):
            pygame.draw.polygon(screen, self.outline_color, points, 2)
        
        if self.state == "holding" and self.barrage_timer < 60:
            charge_ratio = (60 - self.barrage_timer) / 60.0
            radius = int((self.size//2) * charge_ratio)
            alpha = int(150 * charge_ratio)
            surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*WHITE[:3], alpha), (radius, radius), radius)
            screen.blit(surface, (self.x - radius, self.y - radius))
            
        if hasattr(self, 'draw_health_bar'):
            self.draw_health_bar(screen)