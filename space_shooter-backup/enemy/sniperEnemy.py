import pygame
import math
from enemy.enemy_base import Enemy, TargetedBullet
from bullet import Bullet
from settings import *

class SniperEnemy(Enemy):
    """スナイパー敵 - 止まってプレイヤーを狙い撃ち"""
    # 画像をクラス変数として一度だけロード
    image = None
    @classmethod
    def load_image(cls):
        if cls.image is None:
            import os
            base_dir = os.path.dirname(os.path.dirname(__file__))
            img_path = os.path.join(base_dir, 'assets', 'img', 'sniper.png')
            cls.image = pygame.image.load(img_path).convert_alpha()

    def __init__(self, x, y, player, level_multipliers=None, game=None):
        self.load_image()
        health = 2
        speed = ENEMY_SPEED * 0.3
        
        if level_multipliers:
            health = max(1, int(health * level_multipliers.get('health', 1.0)))
            speed = speed * level_multipliers.get('speed', 1.0)
            
        super().__init__(x, y, player, health, speed, (128, 0, 128), int(ENEMY_SIZE * 2.0), game=game)
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
                
                return TargetedBullet(self.x, self.y, vx, vy, RED, game=self.game)
        
        # 通常の弾を発射
        return super().shoot()
    
    def update(self):
        """基底クラスのupdateメソッドを呼び出し"""
        return super().update()
    
    def draw(self, screen):
        """sniper.png画像で描画"""
        if self.image:
            img = pygame.transform.scale(self.image, (self.size, self.size))
            rect = img.get_rect(center=(self.x, self.y))
            screen.blit(img, rect)
        else:
            # 画像がロードできなかった場合は六角形で描画
            points = []
            for i in range(6):
                angle = i * 60 * math.pi / 180
                px = self.x + (self.size//2) * math.cos(angle)
                py = self.y + (self.size//2) * math.sin(angle)
                points.append((px, py))
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, self.outline_color, points, 2)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 3)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 6, 1)
        # 体力バー
        self.draw_health_bar(screen)