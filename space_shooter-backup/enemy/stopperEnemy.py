import pygame
import math
import random
from enemy.enemy_base import Enemy
from settings import *

class StopperEnemy(Enemy):
    """ストッパー敵 - 画面中央で一時停止して集中攻撃"""
    def __init__(self, x, y, player, level_multipliers=None, game=None):
        health = 2
        speed = ENEMY_SPEED * 1.2
        
        if level_multipliers:
            health = max(1, int(health * level_multipliers.get('health', 1.0)))
            speed = speed * level_multipliers.get('speed', 1.0)
            
        super().__init__(x, y, player, health, speed, (255, 255, 0), ENEMY_SIZE, game=game)
        self.enemy_type = "stopper"
        self.score_value = ENEMY_SCORE * 2.5
        self.state = "moving"  # moving, stopping
        self.stop_timer = 0
        self.stop_duration = 180  # 3秒間停止
        self.attack_count = 0
        
    def move(self):
        """段階的な移動パターン"""
        height = self.game.current_height if self.game else SCREEN_HEIGHT
        
        if self.state == "moving":
            self.y += self.speed
            # 画面中央付近で停止
            if self.y >= height // 3:
                self.state = "stopping"
                self.stop_timer = 0
                
        elif self.state == "stopping":
            self.stop_timer += 1
            if self.stop_timer >= self.stop_duration:
                self.state = "moving"
                self.speed *= 0.8  # 停止後は少し遅くなる
    
    def should_shoot(self):
        """停止中は頻繁に射撃"""
        if self.state == "stopping":
            if self.shoot_timer >= 20:  # 高頻度
                self.shoot_timer = 0
                self.attack_count += 1
                return True
        else:
            # 通常の射撃判定
            if self.shoot_timer >= self.shoot_interval:
                self.shoot_timer = 0
                self.shoot_interval = random.randint(60, 120)
                return True
        return False
    
    def update(self):
        """基底クラスのupdateメソッドを呼び出し"""
        return super().update()
    
    def draw(self, screen):
        """ストッパー敵は八角形で描画"""
        # 八角形の頂点を計算
        points = []
        for i in range(8):
            angle = i * 45 * math.pi / 180
            px = self.x + (self.size//2) * math.cos(angle)
            py = self.y + (self.size//2) * math.sin(angle)
            points.append((px, py))
        
        # 停止中は色を変える
        color = (255, 255, 100) if self.state == "stopping" else self.color
        
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, self.outline_color, points, 2)
        
        # 停止中は警告マーク
        if self.state == "stopping":
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 8, 2)
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 3)
            
        # 体力バー
        self.draw_health_bar(screen)