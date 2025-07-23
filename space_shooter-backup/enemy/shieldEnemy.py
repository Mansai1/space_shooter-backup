import pygame
import math
from enemy.enemy_base import Enemy
from settings import *
import os

class ShieldEnemy(Enemy):
    """シールド敵 - 一定ダメージまで無敵"""
    # 画像をクラス変数として一度だけロード
    image = None
    @classmethod
    def load_image(cls):
        if cls.image is None:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            img_path = os.path.join(base_dir, 'assets', 'img', 'shield.png')
            cls.image = pygame.image.load(img_path).convert_alpha()

    def __init__(self, x, y, player, level_multipliers=None, game=None):
        self.load_image()
        health = 1
        speed = ENEMY_SPEED * 0.9
        
        if level_multipliers:
            health = max(1, int(health * level_multipliers.get('health', 1.0)))
            speed = speed * level_multipliers.get('speed', 1.0)
            
        super().__init__(x, y, player, health, speed, (0, 191, 255), int(ENEMY_SIZE * 1.5), game=game)
        self.enemy_type = "shield"
        self.score_value = ENEMY_SCORE * 3
        self.shield_health = 5
        self.max_shield_health = 5
        self.shield_active = True

    def take_damage(self, damage=1):
        """シールドがある間はダメージを無効化"""
        if self.shield_active:
            self.shield_health -= damage
            if self.shield_health <= 0:
                self.shield_active = False
                self.color = (100, 100, 255)  # シールド破壊後は色が変わる
            return False  # シールドで防いだ
        else:
            # シールドがない場合は通常のダメージ処理
            return super().take_damage(damage)
    
    def draw(self, screen):
        """shield.png画像で描画し、シールドエフェクトや目も重ねる"""
        if self.image:
            img = pygame.transform.scale(self.image, (self.size, self.size))
            rect = img.get_rect(center=(self.x, self.y))
            screen.blit(img, rect)
        else:
            # 画像がない場合は円形で描画
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size//2)
            pygame.draw.circle(screen, self.outline_color, (int(self.x), int(self.y)), self.size//2, 2)
        
        # シールドエフェクト
        if self.shield_active:
            # シールドバー
            bar_width = self.size + 10
            bar_height = 4
            bar_x = self.x - bar_width // 2
            bar_y = self.y - self.size // 2 - 15
            
            pygame.draw.rect(screen, (0, 0, 255), (bar_x, bar_y, bar_width, bar_height))
            current_width = int(bar_width * (self.shield_health / self.max_shield_health))
            pygame.draw.rect(screen, CYAN, (bar_x, bar_y, current_width, bar_height))
            
            # シールドリング（点滅）
            if (self.move_timer // 10) % 2:
                pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), 
                                 self.size//2 + 8, 2)
        
        # 敵の目
        eye_size = 3
        pygame.draw.circle(screen, WHITE, 
                         (int(self.x - self.size//4), int(self.y - self.size//4)), eye_size)
        pygame.draw.circle(screen, WHITE, 
                         (int(self.x + self.size//4), int(self.y - self.size//4)), eye_size)
        
        # 通常の体力バー
        if not self.shield_active:
            self.draw_health_bar(screen)

    def move(self):
        self.y += self.speed