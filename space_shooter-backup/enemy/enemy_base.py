import pygame
import random
import math
from settings import *
from bullet import Bullet

class Enemy:
    """敵の基底クラス"""
    def __init__(self, x, y, player, health=1, speed=ENEMY_SPEED, color=RED, size=ENEMY_SIZE):
        self.x = x
        self.y = y
        self.player = player
        self.start_x = x  # 初期位置を記録
        self.max_health = health
        self.health = health
        self.speed = speed
        self.color = color
        self.size = size
        self.active = True
        self.rect = pygame.Rect(x - size//2, y - size//2, size, size)
        self.enemy_type = "basic"
        self.score_value = ENEMY_SCORE
        self.outline_color = WHITE
        
        # 射撃関連
        self.shoot_cooldown = 0
        self.shoot_timer = 0
        self.shoot_interval = random.randint(60, 180)
        
        # 移動関連
        self.move_timer = 0
        
    def update(self):
        """基本的な更新処理"""
        self.move_timer += 1
        self.move()
        self.update_rect()
        
        # 画面外で非アクティブ化
        if self.y > SCREEN_HEIGHT + self.size or self.y < -self.size:
            self.active = False
        
        # 射撃処理
        if self.should_shoot():
            return self.shoot()
        return None
            
    def move(self):
        """移動処理（サブクラスでオーバーライド）"""
        self.y += self.speed
        
    def update_rect(self):
        """矩形の位置を更新"""
        self.rect.center = (self.x, self.y)
        
    def update_shooting(self):
        """射撃タイマーの更新"""
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.shoot_timer < self.shoot_interval:
            self.shoot_timer += 1
            
    def draw(self, screen):
        """敵を描画"""
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, self.outline_color, self.rect, 2)
        
        # 体力バーの描画
        self.draw_health_bar(screen)

    def draw_outline(self, screen, color, width):
        """敵のアウトラインを描画"""
        pygame.draw.rect(screen, color, self.rect, width)
        
    def draw_health_bar(self, screen):
        """体力バーを描画"""
        if self.health < self.max_health and self.max_health > 1:
            bar_width = self.size
            bar_height = 4
            bar_x = self.x - bar_width // 2
            bar_y = self.y - self.size // 2 - 8
            
            # 背景バー
            pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            
            # 体力バー
            health_ratio = self.health / self.max_health
            health_width = int(bar_width * health_ratio)
            health_color = GREEN if health_ratio > 0.6 else YELLOW if health_ratio > 0.3 else RED
            pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))
            
    def take_damage(self, damage=1):
        """ダメージを受ける"""
        self.health -= damage
        if self.health <= 0:
            self.active = False
            return True  # 撃破された
        return False  # まだ生きている
        
    def should_shoot(self):
        """射撃するかどうか判定"""
        if self.shoot_cooldown <= 0 and self.shoot_timer >= self.shoot_interval:
            self.shoot_cooldown = random.randint(60, 120)
            self.shoot_timer = 0
            self.shoot_interval = random.randint(60, 180)
            return True
        return False
        
    def shoot(self):
        """弾を発射"""
        # 下向きに発射（direction_y=1）
        return Bullet(self.x, self.y + self.size//2, direction_y=1, angle=0, player_bullet=False)

class TargetedBullet(Bullet):
    """狙い撃ち弾"""
    def __init__(self, x, y, vx, vy, color):
        super().__init__(x, y, direction_y=1, angle=0, player_bullet=False)
        self.vx = vx
        self.vy = vy
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
        
        if (self.x < 0 or self.x > SCREEN_WIDTH or 
            self.y < 0 or self.y > SCREEN_HEIGHT):
            self.active = False