import pygame
import random
from settings import *
import pygame
import random
from settings import *
from utils import draw_text_multiline, draw_text_relative, draw_text_absolute

LIGHT_BLUE = (173, 216, 230)

class UpgradeOption:
    """個々のアップグレード情報を保持するクラス"""
    def __init__(self, u_type, name, description, apply_func):
        self.type = u_type
        self.name = name
        self.description = description
        self.apply = apply_func # プレイヤーに適用するための関数

def get_available_upgrades(player=None):
    """利用可能な全アップグレードのリストを返す。playerを渡すとoption_addの説明を動的に変更"""
    option_desc = "追従するオプションが1機増える"
    option_func = lambda p: p.add_option()
    if player is not None and getattr(player, 'option_count', 0) >= 4:
        option_desc = "子機の攻撃力が上昇する"
        option_func = lambda p: setattr(p, 'attack_power', getattr(p, 'attack_power', 1) + 1)
    return [
        UpgradeOption("fire_rate", "連射速度強化", "射撃間隔が10%短縮される", 
                      lambda p: setattr(p, 'fire_rate_multiplier', p.fire_rate_multiplier * 0.9)),
        UpgradeOption("attack_power", "攻撃力強化", "弾のダメージが1増加する", 
                      lambda p: setattr(p, 'attack_power', p.attack_power + 1)),
        UpgradeOption("move_speed", "移動速度強化", "プレイヤーの移動速度が上昇する", 
                      lambda p: setattr(p, 'speed', p.speed + 0.5)),
        UpgradeOption("option_add", "オプション追加", option_desc, option_func),
        UpgradeOption("life_up", "残機アップ", "残機が1つ増える", 
                      lambda p: setattr(p.game, 'lives', p.game.lives + 1)),
        UpgradeOption("safety", "セーフティ", "次の被弾を無効化する（一度だけ有効）", 
                      lambda p: setattr(p, 'safety_flag', True)),
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
        self.player_ref = None  # プレイヤー参照

    def start_selection(self, player=None):
        """アップグレード選択画面を開始する。playerを渡すとoption_add説明を動的に変更"""
        self.is_active = True
        self.player_ref = player
        # プレイヤー情報に応じてアップグレードリストを再生成
        self.all_upgrades = get_available_upgrades(player)
        self.current_choices = random.sample(self.all_upgrades, min(3, len(self.all_upgrades)))
        
        # 選択肢のUI矩形を準備
        screen_width, screen_height = self.screen.get_size()
        self.choice_rects.clear()
        
        card_width_percent = 0.25
        card_height_percent = 0.45
        padding_percent = 0.02

        card_width_abs = int(screen_width * card_width_percent)
        card_height_abs = int(screen_height * card_height_percent)
        padding_abs = int(screen_width * padding_percent)

        total_width_abs = len(self.current_choices) * card_width_abs + (len(self.current_choices) - 1) * padding_abs
        start_x_abs = (screen_width - total_width_abs) // 2
        
        for i in range(len(self.current_choices)):
            x_abs = start_x_abs + i * (card_width_abs + padding_abs)
            y_abs = (screen_height - card_height_abs) // 2
            self.choice_rects.append(pygame.Rect(x_abs, y_abs, card_width_abs, card_height_abs))

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
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # タイトル
        draw_text_relative(self.screen, "LEVEL UP! CHOOSE YOUR POWER", 0.5, 0.15, self.font, YELLOW)

        # 各選択肢カードを描画
        for i, rect in enumerate(self.choice_rects):
            upgrade = self.current_choices[i]
            
            # カードの背景
            pygame.draw.rect(self.screen, (30, 30, 80), rect, border_radius=10)
            pygame.draw.rect(self.screen, LIGHT_BLUE, rect, 2, border_radius=10)
            
            # アップグレード名
            draw_text_absolute(self.screen, upgrade.name, rect.centerx, rect.y + 30, self.font, WHITE)

            # 説明文
            # draw_text_multilineはrectと絶対座標を直接受け取るため、そのまま使用
            draw_text_multiline(self.screen, upgrade.description, self.small_font, WHITE, rect.inflate(-40, -40), rect.x + 20, rect.y + 120)