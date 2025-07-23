import pygame
import random
from enemy.enemy_base import Enemy
from settings import *

class TankEnemy(Enemy):
    """タンク敵 - 大きくて遅い、体力が多い、連射してくる"""
    # 画像をクラス変数として一度だけロード
    image = None
    @classmethod
    def load_image(cls):
        if cls.image is None:
            import os
            base_dir = os.path.dirname(os.path.dirname(__file__))
            img_path = os.path.join(base_dir, 'assets', 'img', 'tank.png')
            cls.image = pygame.image.load(img_path).convert_alpha()

    def __init__(self, x, y, player, level_multipliers=None, game=None):
        self.load_image()
        health = 10
        speed = ENEMY_SPEED * 0.8
        
        if level_multipliers:
            health = max(1, int(health * level_multipliers.get('health', 1.0)))
            speed = speed * level_multipliers.get('speed', 1.0)
            
        super().__init__(x, y, player, health, speed, (139, 69, 19), int(ENEMY_SIZE * 2.0), game=game)
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
    
    def update(self):
        """基底クラスのupdateメソッドを呼び出し"""
        return super().update()
    
    def draw(self, screen):
        """tank.png画像で描画"""
        if self.image:
            img = pygame.transform.scale(self.image, (self.size, self.size))
            rect = img.get_rect(center=(self.x, self.y))
            screen.blit(img, rect)
        else:
            # 画像がロードできなかった場合は従来の描画
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, self.outline_color, self.rect, 3)
            turret_size = self.size // 3
            turret_rect = pygame.Rect(self.x - turret_size//2, self.y - turret_size//2, 
                                    turret_size, turret_size)
            pygame.draw.rect(screen, (100, 50, 0), turret_rect)
            pygame.draw.rect(screen, self.outline_color, turret_rect, 2)
            pygame.draw.rect(screen, (80, 40, 0), 
                            (self.x - 2, self.y, 4, self.size//2))
        # 体力バー
        self.draw_health_bar(screen)

    def move(self):
        self.y += self.speed