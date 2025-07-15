import pygame
import math
from enemy.enemy_base import Enemy
from settings import *

class ShieldEnemy(Enemy):
    """シールド敵 - 一定ダメージまで無敵"""
    def __init__(self, x, y, player, level_multipliers=None):
        health = 1
        speed = ENEMY_SPEED * 0.9
        
        if level_multipliers:
            health = max(1, int(health * level_multipliers.get('health', 1.0)))
            speed = speed * level_multipliers.get('speed', 1.0)
            
        super().__init__(x, y, player, health, speed, (0, 191, 255), ENEMY_SIZE)
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
        """シールド敵は円形＋シールドエフェクトで描画"""
        # メイン部分（円形）
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