import pygame
from settings import *
from utils import draw_text

def draw_boss_health_bar(screen, boss, font):
    """ボスのHPバーを描画"""
    if not boss or boss.entrance_timer > 0: # 登場演出中は表示しない
        return

    bar_width = SCREEN_WIDTH - 200
    bar_height = 20
    bar_x = (SCREEN_WIDTH - bar_width) // 2
    bar_y = 20

    # 背景
    pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))

    # スペルカードHPバー
    spell_data = boss.get_current_spell_data()
    if spell_data and spell_data['max_health'] > 0:
        health_ratio = max(0, spell_data['current_health'] / spell_data['max_health'])
        health_width = int(bar_width * health_ratio)
        
        # HPバーの色を残りHPで変化
        if health_ratio > 0.6:
            hp_color = GREEN
        elif health_ratio > 0.3:
            hp_color = YELLOW
        else:
            hp_color = RED
        
        if health_width > 0:
            pygame.draw.rect(screen, hp_color, (bar_x, bar_y, health_width, bar_height))
    
    # 枠線
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

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
        draw_text(screen, spell_name, SCREEN_WIDTH // 2, 50, font, YELLOW)

        # スペルカードHP
        draw_text(screen, f"HP: {current_hp}/{max_hp}", SCREEN_WIDTH // 2, 80, font, WHITE)
