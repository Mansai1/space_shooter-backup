import pygame
from settings import *
from utils import draw_text_relative, draw_text_absolute

def draw_boss_health_bar(screen, boss, font):
    """ボスのHPバーを描画"""
    if not boss or boss.entrance_timer > 0: # 登場演出中は表示しない
        return

    screen_width, screen_height = screen.get_size()
    bar_width_percent = 0.8
    bar_height_percent = 0.03
    bar_x_percent = 0.5 - (bar_width_percent / 2)
    bar_y_percent = 0.03

    bar_width_abs = int(screen_width * bar_width_percent)
    bar_height_abs = int(screen_height * bar_height_percent)
    bar_x_abs = int(screen_width * bar_x_percent)
    bar_y_abs = int(screen_height * bar_y_percent)

    # 背景
    pygame.draw.rect(screen, DARK_GRAY, (bar_x_abs, bar_y_abs, bar_width_abs, bar_height_abs))

    # スペルカードHPバー
    spell_data = boss.get_current_spell_data()
    if spell_data and spell_data['max_health'] > 0:
        health_ratio = max(0, spell_data['current_health'] / spell_data['max_health'])
        health_width = int(bar_width_abs * health_ratio)
        
        # HPバーの色を残りHPで変化
        if health_ratio > 0.6:
            hp_color = GREEN
        elif health_ratio > 0.3:
            hp_color = YELLOW
        else:
            hp_color = RED
        
        if health_width > 0:
            pygame.draw.rect(screen, hp_color, (bar_x_abs, bar_y_abs, health_width, bar_height_abs))
    
    # 枠線
    pygame.draw.rect(screen, WHITE, (bar_x_abs, bar_y_abs, bar_width_abs, bar_height_abs), 2)

def draw_boss_spell_card_name(screen, boss, font):
    """ボスのスペルカード名とHPを表示"""
    if not boss or boss.entrance_timer > 0: # 登場演出中は表示しない
        return

    spell_data = boss.get_current_spell_data()
    if spell_data:
        spell_name = spell_data['name']
        current_hp = int(spell_data['current_health'])
        max_hp = spell_data['max_health']

        # スペルカード名
        draw_text_relative(screen, spell_name, 0.5, 0.08, font, YELLOW)

        # スペルカードHP
        draw_text_relative(screen, f"HP: {current_hp}/{max_hp}", 0.5, 0.13, font, WHITE)
