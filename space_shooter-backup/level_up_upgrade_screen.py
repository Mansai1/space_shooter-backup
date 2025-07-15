import pygame
import random
from settings import *
from utils import draw_text_multiline

LIGHT_BLUE = (173, 216, 230)

class UpgradeOption:
    """個々のアップグレード情報を保持するクラス"""
    def __init__(self, u_type, name, description, apply_func):
        self.type = u_type
        self.name = name
        self.description = description
        self.apply = apply_func # プレイヤーに適用するための関数

def get_available_upgrades():
    """利用可能な全アップグレードのリストを返す"""
    return [
        UpgradeOption("fire_rate", "連射速度強化", "射撃間隔が10%短縮される", 
                      lambda p: setattr(p, 'fire_rate_multiplier', p.fire_rate_multiplier * 0.9)),
        UpgradeOption("attack_power", "攻撃力強化", "弾のダメージが1増加する", 
                      lambda p: setattr(p, 'attack_power', p.attack_power + 1)),
        UpgradeOption("move_speed", "移動速度強化", "プレイヤーの移動速度が上昇する", 
                      lambda p: setattr(p, 'speed', p.speed + 0.5)),
        UpgradeOption("option_add", "オプション追加", "追従するオプションが1機増える", 
                      lambda p: p.add_option()),
        UpgradeOption("shield_max", "シールド最大値UP", "シールドの最大値が1増加する", 
                      lambda p: setattr(p, 'max_shield_hits', p.max_shield_hits + 1)),
        UpgradeOption("shield_recover", "シールド回復", "シールドが2回復する", 
                      lambda p: setattr(p, 'shield_hits', min(p.max_shield_hits, p.shield_hits + 2))),
        UpgradeOption("special_charge", "SPゲージチャージ", "必殺技ゲージが50%チャージされる", 
                      lambda p: setattr(p, 'special_gauge', min(SPECIAL_GAUGE_MAX, p.special_gauge + SPECIAL_GAUGE_MAX * 0.5))),
    ]

class LevelUpUpgradeScreen:
    def __init__(self, screen, font, small_font):
        self.screen = screen
        self.font = font
        self.small_font = small_font
        self.all_upgrades = get_available_upgrades()
        self.current_choices = []
        self.choice_rects = []
        self.is_active = False

    def start_selection(self):
        """アップグレード選択画面を開始する"""
        self.is_active = True
        # 重複しないようにランダムに3つ選ぶ
        self.current_choices = random.sample(self.all_upgrades, min(3, len(self.all_upgrades)))
        
        # 選択肢のUI矩形を準備
        self.choice_rects.clear()
        card_width, card_height = 220, 280
        total_width = len(self.current_choices) * card_width + (len(self.current_choices) - 1) * 20
        start_x = (SCREEN_WIDTH - total_width) / 2
        
        for i in range(len(self.current_choices)):
            x = start_x + i * (card_width + 20)
            y = (SCREEN_HEIGHT - card_height) / 2
            self.choice_rects.append(pygame.Rect(x, y, card_width, card_height))

    def handle_event(self, event):
        """マウスクリックを処理し、選択されたアップグレードを返す"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.choice_rects):
                if rect.collidepoint(event.pos):
                    self.is_active = False
                    return self.current_choices[i]
        return None

    def draw(self):
        """アップグレード選択画面を描画する"""
        if not self.is_active:
            return

        # 半透明のオーバーレイ
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # タイトル
        title_surf = self.font.render("LEVEL UP! CHOOSE YOUR POWER", True, YELLOW)
        self.screen.blit(title_surf, (SCREEN_WIDTH / 2 - title_surf.get_width() / 2, 100))

        # 各選択肢カードを描画
        for i, rect in enumerate(self.choice_rects):
            upgrade = self.current_choices[i]
            
            # カードの背景
            pygame.draw.rect(self.screen, (30, 30, 80), rect, border_radius=10)
            pygame.draw.rect(self.screen, LIGHT_BLUE, rect, 2, border_radius=10)
            
            # アップグレード名
            name_surf = self.font.render(upgrade.name, True, WHITE)
            self.screen.blit(name_surf, (rect.centerx - name_surf.get_width() / 2, rect.y + 30))

            # 説明文
            draw_text_multiline(self.screen, upgrade.description, self.small_font, WHITE, rect.inflate(-40, -40), rect.x + 20, rect.y + 120)