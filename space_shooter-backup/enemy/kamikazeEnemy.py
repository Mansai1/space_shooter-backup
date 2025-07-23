import pygame
import math
from enemy.enemy_base import Enemy
from settings import *

class KamikazeEnemy(Enemy):
    """カミカゼ敵 - プレイヤーに向かって突進"""
    # 画像をクラス変数として一度だけロード
    image = None
    @classmethod
    def load_image(cls):
        if cls.image is None:
            import os
            base_dir = os.path.dirname(os.path.dirname(__file__))
            img_path = os.path.join(base_dir, 'assets', 'img', 'kamikaze.png')
            cls.image = pygame.image.load(img_path).convert_alpha()

    def __init__(self, x, y, player, level_multipliers=None, game=None):
        self.load_image()
        health = 1
        speed = ENEMY_SPEED * 4
        
        if level_multipliers:
            health = max(1, int(health * level_multipliers.get('health', 1.0)))
            speed = speed * level_multipliers.get('speed', 1.0)
            
        super().__init__(x, y, player, health, speed, (255, 0, 255), int(ENEMY_SIZE * 2.0), game=game)
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
        """kamikaze.png画像で描画"""
        if self.image:
            img = pygame.transform.scale(self.image, (self.size, self.size))
            rect = img.get_rect(center=(self.x, self.y))
            screen.blit(img, rect)
        else:
            # 画像がロードできなかった場合は三角形で描画
            points = [
                (self.x, self.y - self.size//2),
                (self.x - self.size//2, self.y + self.size//2),
                (self.x + self.size//2, self.y + self.size//2)
            ]
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, self.outline_color, points, 2)
        # 敵の目は画像に含まれるため省略