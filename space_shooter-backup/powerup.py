import pygame
import random
import math  
from settings import *

class PowerUp:
    def __init__(self, x, y, power_type, game=None):
        self.x = x
        self.y = y
        self.size = POWERUP_SIZE
        self.speed = POWERUP_SPEED
        self.power_type = power_type
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        self.active = True
        self.bob_offset = 0  # フワフワ動くエフェクト用
        self.bob_speed = 0.1
        self.game = game  # 追加: Gameインスタンス参照
        
    def update(self):
        self.y += self.speed
        self.bob_offset += self.bob_speed
        
        # フワフワ動くエフェクト
        float_y = self.y + math.sin(self.bob_offset) * 2
        self.rect.center = (self.x, float_y)
        
        # 画面外に出たら非アクティブに
        height = self.game.current_height if self.game else SCREEN_HEIGHT
        if self.y > height + self.size:
            self.active = False
    
    def draw(self, screen):
        float_y = self.y + math.sin(self.bob_offset) * 2
        
        if self.power_type == "triple_shot":
            # 三角形 - トリプルショット
            points = [
                (self.x, float_y - self.size//2),
                (self.x - self.size//2, float_y + self.size//2),
                (self.x + self.size//2, float_y + self.size//2)
            ]
            pygame.draw.polygon(screen, GREEN, points)
            pygame.draw.polygon(screen, WHITE, points, 2)
            # "T"マーク
            font = pygame.font.Font(None, 16)
            text = font.render("T", True, BLACK)
            text_rect = text.get_rect(center=(self.x, float_y))
            screen.blit(text, text_rect)
            
        elif self.power_type == "rapid_fire":
            # 円形 - ラピッドファイア
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(float_y)), self.size//2)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(float_y)), self.size//2, 2)
            # "R"マーク
            font = pygame.font.Font(None, 16)
            text = font.render("R", True, BLACK)
            text_rect = text.get_rect(center=(self.x, float_y))
            screen.blit(text, text_rect)
            
        elif self.power_type == "shield":
            # 六角形 - シールド
            points = []
            for i in range(6):
                angle = i * 60 * math.pi / 180
                px = self.x + (self.size//2) * math.cos(angle)
                py = float_y + (self.size//2) * math.sin(angle)
                points.append((px, py))
            pygame.draw.polygon(screen, BLUE, points)
            pygame.draw.polygon(screen, WHITE, points, 2)
            # "S"マーク
            font = pygame.font.Font(None, 16)
            text = font.render("S", True, WHITE)
            text_rect = text.get_rect(center=(self.x, float_y))
            screen.blit(text, text_rect)
            
        elif self.power_type == "speed_boost":
            # ダイヤモンド - スピードブースト
            points = [
                (self.x, float_y - self.size//2),
                (self.x + self.size//2, float_y),
                (self.x, float_y + self.size//2),
                (self.x - self.size//2, float_y)
            ]
            pygame.draw.polygon(screen, MAGENTA, points)
            pygame.draw.polygon(screen, WHITE, points, 2)
            # "+"マーク
            font = pygame.font.Font(None, 16)
            text = font.render("+", True, WHITE)
            text_rect = text.get_rect(center=(self.x, float_y))
            screen.blit(text, text_rect)
            
        elif self.power_type == "laser":
            # 長方形 - レーザー
            rect_width = self.size - 4
            rect_height = self.size + 4
            laser_rect = pygame.Rect(
                self.x - rect_width//2,
                float_y - rect_height//2,
                rect_width,
                rect_height
            )
            pygame.draw.rect(screen, CYAN, laser_rect)
            pygame.draw.rect(screen, WHITE, laser_rect, 2)
            
            # レーザー線エフェクト
            pygame.draw.line(screen, WHITE, 
                           (self.x, float_y - rect_height//2),
                           (self.x, float_y + rect_height//2), 2)
            
            # "L"マーク
            font = pygame.font.Font(None, 16)
            text = font.render("L", True, WHITE)
            text_rect = text.get_rect(center=(self.x, float_y))
            screen.blit(text, text_rect)
            
        elif self.power_type == "bomb":
            # 八角形 - 爆弾
            points = []
            for i in range(8):
                angle = i * 45 * math.pi / 180
                px = self.x + (self.size//2) * math.cos(angle)
                py = float_y + (self.size//2) * math.sin(angle)
                points.append((px, py))
            pygame.draw.polygon(screen, ORANGE, points)
            pygame.draw.polygon(screen, WHITE, points, 2)
            
            # 爆発マーク
            font = pygame.font.Font(None, 16)
            text = font.render("B", True, WHITE)
            text_rect = text.get_rect(center=(self.x, float_y))
            screen.blit(text, text_rect)
            
            # 点滅エフェクト
            if pygame.time.get_ticks() % 400 < 200:
                pygame.draw.circle(screen, RED, (int(self.x), int(float_y)), 3)

        elif self.power_type == "life_up":
            # 赤色のハート型＋白枠＋中央に「1UP」
            heart_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            cx, cy = self.size // 2, self.size // 2
            scale = self.size // 2

            # ハートの形状を計算
            points = []
            for t in range(0, 360, 5):
                rad = math.radians(t)
                x = cx + scale * 0.95 * math.sin(rad) ** 3
                y = cy - scale * (0.7 * math.cos(rad) - 0.3 * math.cos(2*rad) - 0.2 * math.cos(3*rad) - 0.1 * math.cos(4*rad))
                points.append((x, y))
            pygame.draw.polygon(heart_surface, RED, points)
            pygame.draw.polygon(heart_surface, WHITE, points, 2)
            screen.blit(heart_surface, (self.x - cx, float_y - cy))
            # "1UP"テキスト
            font = pygame.font.Font(None, 18)
            text = font.render("1UP", True, WHITE)
            text_rect = text.get_rect(center=(self.x, float_y))
            screen.blit(text, text_rect)