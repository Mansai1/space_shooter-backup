import pygame
import json
import os
import settings # settingsモジュールをインポート
from utils import draw_text # draw_textをインポート

class UpgradeScreen:
    def __init__(self, screen, font_path):
        self.screen = screen
        self.font_path = font_path
        self.font = pygame.font.Font(font_path, 30)
        self.small_font = pygame.font.Font(font_path, 20)
        self.running = True
        self.upgrade_data = self.load_upgrade_data()
        
        self.upgrade_costs = {
            'attack': 500,
            'fire_rate': 700,
            'speed': 400,
            'option': 1000
        }
        self.weapon_costs = {
            'wide_shot': 1500,
            'laser_weapon': 2000
        }

        self.upgrade_buttons = self.create_upgrade_buttons()
        self.weapon_buttons = self.create_weapon_buttons()
        self.back_button = pygame.Rect(settings.SCREEN_WIDTH // 2 - 100, settings.SCREEN_HEIGHT - 70, 200, 50)
        self.reset_button = pygame.Rect(settings.SCREEN_WIDTH - 170, settings.SCREEN_HEIGHT - 70, 150, 50)

    def load_upgrade_data(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), 'upgrade_data.json'), 'r') as f:
                data = json.load(f)
                # 新しいキーのデフォルト値を追加
                data.setdefault("unlocked_weapons", ["normal"])
                data.setdefault("current_weapon", "normal")
                return data
        except FileNotFoundError:
            return {"points": 0, "attack_level": 1, "fire_rate_level": 1, "speed_level": 1, "option_level": 0, "unlocked_weapons": ["normal"], "current_weapon": "normal"}

    def save_upgrade_data(self):
        with open(os.path.join(os.path.dirname(__file__), 'upgrade_data.json'), 'w') as f:
            json.dump(self.upgrade_data, f, indent=4)

    def create_upgrade_buttons(self):
        buttons = {}
        y_start = 150
        for i, (key, cost) in enumerate(self.upgrade_costs.items()):
            buttons[key] = pygame.Rect(settings.SCREEN_WIDTH // 2 + 50, y_start + i * 60, 150, 40)
        return buttons

    def create_weapon_buttons(self):
        buttons = {}
        y_start = 150
        x_start = 50
        for i, weapon_type in enumerate(settings.WEAPON_TYPES):
            buttons[weapon_type] = pygame.Rect(x_start, y_start + i * 60, 150, 40)
        return buttons

    def run(self):
        while self.running:
            self.screen.fill(settings.BLACK)
            # タイトル
            draw_text(self.screen, f"Points: {self.upgrade_data['points']}", settings.SCREEN_WIDTH // 2, 40, self.font, settings.WHITE)
            draw_text(self.screen, "武器選択", 180, 100, self.font, settings.YELLOW)
            draw_text(self.screen, "アップグレード", settings.SCREEN_WIDTH // 2, 100, self.font, settings.YELLOW)
            self.draw_weapon_options()
            self.draw_upgrade_options()
            self.draw_buttons()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            pygame.display.flip()

    def draw_upgrade_options(self):
        # アップグレード欄を中央縦並びに
        y_start = 160
        x_center = settings.SCREEN_WIDTH // 2
        row_height = 80
        upgrade_names = {
            'attack': '攻撃力',
            'fire_rate': '連射速度',
            'speed': '移動速度',
            'option': '子機'
        }
        for i, (key, cost) in enumerate(self.upgrade_costs.items()):
            level = self.upgrade_data.get(f"{key}_level", 1)
            display_name = upgrade_names.get(key, key.replace('_', ' ').title())
            y = y_start + i * row_height
            # ラベル
            draw_text(self.screen, f"{display_name} (Lv: {level})", x_center, y, self.small_font, settings.WHITE)
            # コスト
            draw_text(self.screen, f"コスト: {cost * level}", x_center, y + 25, self.small_font, settings.GRAY)
            # ボタン
            rect = self.upgrade_buttons[key]
            rect.centerx = x_center
            rect.y = y + 40
            pygame.draw.rect(self.screen, settings.WHITE, rect, 2)
            draw_text(self.screen, "アップグレード", rect.centerx, rect.centery, self.small_font, settings.WHITE)

    def draw_weapon_options(self):
        # 武器選択欄を左側縦並びに
        y_start = 160
        x_center = 180
        row_height = 80
        weapon_names = {
            'normal': '通常弾',
            'wide_shot': 'ワイドショット',
            'laser_weapon': 'レーザー'
        }
        for i, weapon_type in enumerate(settings.WEAPON_TYPES):
            y = y_start + i * row_height
            is_unlocked = weapon_type in self.upgrade_data['unlocked_weapons']
            is_current = weapon_type == self.upgrade_data['current_weapon']
            cost = self.weapon_costs.get(weapon_type, 0)
            display_name = weapon_names.get(weapon_type, weapon_type.replace('_', ' ').title())
            text_color = settings.WHITE
            if is_current: text_color = settings.GREEN
            elif not is_unlocked: text_color = settings.GRAY
            draw_text(self.screen, display_name, x_center, y, self.small_font, text_color)
            if not is_unlocked and weapon_type != "normal":
                draw_text(self.screen, f"コスト: {cost}", x_center, y + 25, self.small_font, settings.GRAY)
            # ボタン
            rect = self.weapon_buttons[weapon_type]
            rect.centerx = x_center
            rect.y = y + 40
            button_text = "選択" if is_unlocked else "アンロック"
            button_color = settings.GREEN if is_unlocked else settings.RED
            if is_current: button_color = settings.BLUE
            pygame.draw.rect(self.screen, button_color, rect, 2)
            draw_text(self.screen, button_text, rect.centerx, rect.centery, self.small_font, settings.WHITE)

    def draw_buttons(self):
        # 戻る・リセットボタンを下部中央に配置
        screen_w, screen_h = self.screen.get_size()
        self.back_button.x = screen_w // 2 - 180
        self.back_button.y = screen_h - 80
        self.reset_button.x = screen_w // 2 + 30
        self.reset_button.y = screen_h - 80
        pygame.draw.rect(self.screen, settings.WHITE, self.back_button, 2)
        draw_text(self.screen, "メニューに戻る", self.back_button.centerx, self.back_button.centery, self.font, settings.WHITE)
        pygame.draw.rect(self.screen, settings.RED, self.reset_button, 2)
        draw_text(self.screen, "リセット", self.reset_button.centerx, self.reset_button.centery, self.small_font, settings.WHITE)

    def handle_click(self, pos):
        if self.back_button.collidepoint(pos):
            self.running = False
            self.save_upgrade_data()
            return

        for key, rect in self.upgrade_buttons.items():
            if rect.collidepoint(pos):
                self.upgrade(key)
                return

        for weapon_type, rect in self.weapon_buttons.items():
            if rect.collidepoint(pos):
                self.handle_weapon_action(weapon_type)
                return

        if self.reset_button.collidepoint(pos):
            self.reset_upgrades()
            return

    def upgrade(self, key):
        level_key = f"{key}_level"
        level = self.upgrade_data.get(level_key, 1)
        cost = self.upgrade_costs[key] * level
        if self.upgrade_data['points'] >= cost:
            self.upgrade_data['points'] -= cost
            self.upgrade_data[level_key] += 1
            self.save_upgrade_data()

    def handle_weapon_action(self, weapon_type):
        is_unlocked = weapon_type in self.upgrade_data['unlocked_weapons']
        is_current = weapon_type == self.upgrade_data['current_weapon']

        if is_unlocked:
            if not is_current:
                self.upgrade_data['current_weapon'] = weapon_type
                self.save_upgrade_data()
        else:
            cost = self.weapon_costs.get(weapon_type, 0)
            if self.upgrade_data['points'] >= cost:
                self.upgrade_data['points'] -= cost
                self.upgrade_data['unlocked_weapons'].append(weapon_type)
                self.upgrade_data['current_weapon'] = weapon_type # アンロックしたら自動的に選択
                self.save_upgrade_data()

    def reset_upgrades(self):
        total_refund = 0

        # 通常アップグレードのポイント返金
        for key, cost in self.upgrade_costs.items():
            level_key = f"{key}_level"
            level = self.upgrade_data.get(level_key, 1)
            for i in range(1, level):
                total_refund += cost * i
            self.upgrade_data[level_key] = 1

        # 武器アンロックのポイント返金
        for weapon, cost in self.weapon_costs.items():
            if weapon in self.upgrade_data['unlocked_weapons'] and weapon != 'normal':
                total_refund += cost
        
        self.upgrade_data['unlocked_weapons'] = ["normal"]
        self.upgrade_data['current_weapon'] = "normal"
        self.upgrade_data['option_level'] = 0

        self.upgrade_data['points'] += total_refund
        self.save_upgrade_data()

    
