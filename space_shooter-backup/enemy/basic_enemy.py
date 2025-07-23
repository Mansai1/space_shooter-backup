import pygame
from enemy.enemy_base import Enemy
from settings import *

class BasicEnemy(Enemy):
    """基本的な敵"""
    # 画像をクラス変数として一度だけロード
    image = None
    @classmethod
    def load_image(cls):
        if cls.image is None:
            import os
            base_dir = os.path.dirname(os.path.dirname(__file__))
            img_path = os.path.join(base_dir, 'assets', 'img', 'basic.png')
            cls.image = pygame.image.load(img_path).convert_alpha()

    def __init__(self, x, y, player, level_multipliers=None, game=None):
        self.load_image()
        health = 1
        speed = ENEMY_SPEED
        
        if level_multipliers:
            health = max(1, int(health * level_multipliers.get('health', 1.0)))
            speed = speed * level_multipliers.get('speed', 1.0)
            
        super().__init__(x, y, player, health, speed, RED, int(ENEMY_SIZE * 1.5), game=game)
        self.enemy_type = "basic"
        self.score_value = ENEMY_SCORE

    def draw(self, screen):
        """basic.png画像で描画"""
        if self.image:
            img = pygame.transform.scale(self.image, (self.size, self.size))
            rect = img.get_rect(center=(self.x, self.y))
            screen.blit(img, rect)
        else:
            # 画像がロードできなかった場合は四角で描画
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, self.outline_color, self.rect, 2)
        # 体力バー
        self.draw_health_bar(screen)