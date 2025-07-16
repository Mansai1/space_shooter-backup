import pygame
from settings import *

class DamageNumber:
    """ダメージ数値を表示するためのクラス"""
    def __init__(self, x, y, damage, font, color=WHITE):
        self.x = x
        self.y = y
        self.damage = str(damage)
        self.font = font
        self.color = color
        
        # ライフサイクルと動き
        self.lifetime = 60  # 60フレーム（1秒）で消える
        self.speed_y = -1   # 上昇速度
        self.alpha = 255    # 初期透明度
        self.active = True

    def update(self):
        """位置と透明度を更新"""
        self.y += self.speed_y
        self.lifetime -= 1
        
        # 徐々に透明にする
        if self.lifetime < 30:
            self.alpha = max(0, int(255 * (self.lifetime / 30)))
            
        if self.lifetime <= 0:
            self.active = False

    def draw(self, screen):
        """ダメージ数値を描画"""
        if not self.active:
            return
            
        text_surface = self.font.render(self.damage, True, self.color)
        text_surface.set_alpha(self.alpha)
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        screen.blit(text_surface, text_rect)