import pygame
from settings import *
from utils import draw_text # draw_textをインポート

from utils import draw_text_relative, draw_text_absolute # draw_textをインポート

def draw_level_info(screen, level_system, font, small_font):
    """レベル情報を画面に描画"""
    # レベル表示
    draw_text_relative(screen, f"Level: {level_system.current_level}", 0.05, 0.75, font, WHITE, anchor="topleft")
    
    # 経験値バーの描画
    screen_width, screen_height = screen.get_size()
    bar_width_percent = 0.25
    bar_height_percent = 0.015
    bar_x_percent = 0.05
    bar_y_percent = 0.8
    
    bar_width_abs = int(screen_width * bar_width_percent)
    bar_height_abs = int(screen_height * bar_height_percent)
    bar_x_abs = int(screen_width * bar_x_percent)
    bar_y_abs = int(screen_height * bar_y_percent)
    
    # 背景バー
    pygame.draw.rect(screen, (50, 50, 50), (bar_x_abs, bar_y_abs, bar_width_abs, bar_height_abs))
    
    # 経験値バー
    progress = level_system.get_level_progress()
    fill_width_abs = int(bar_width_abs * progress)
    if fill_width_abs > 0:
        pygame.draw.rect(screen, CYAN, (bar_x_abs, bar_y_abs, fill_width_abs, bar_height_abs))
    
    # バーの枠線
    pygame.draw.rect(screen, WHITE, (bar_x_abs, bar_y_abs, bar_width_abs, bar_height_abs), 2)
    
    # 経験値テキスト
    draw_text_relative(screen, f"EXP: {level_system.experience}/{level_system.experience_to_next_level}", 0.05 + bar_width_percent / 2, bar_y_percent + bar_height_percent + 0.02, small_font, WHITE, anchor="midtop")

def draw_difficulty_info(screen, level_system, small_font):
    """現在の難易度情報を表示"""
    config = level_system.get_current_config()
    
    # 現在のレベル説明
    draw_text_relative(screen, config['description'], 0.05, 0.9, small_font, WHITE, anchor="topleft")
    
    # 難易度指標
    # 敵の強さ表示
    enemy_strength = f"Enemy Strength: x{config['enemy_speed_multiplier']:.1f}"
    draw_text_relative(screen, enemy_strength, 0.05, 0.93, small_font, RED if config['enemy_speed_multiplier'] > 1.5 else YELLOW if config['enemy_speed_multiplier'] > 1.2 else GREEN, anchor="topleft")
    
    # 敵の出現頻度表示
    spawn_rate = f"Spawn Rate: {60 // config['enemy_spawn_rate']:.1f}/sec"
    draw_text_relative(screen, spawn_rate, 0.05, 0.96, small_font, RED if config['enemy_spawn_rate'] < 30 else YELLOW if config['enemy_spawn_rate'] < 45 else GREEN, anchor="topleft")

def draw_stats_panel(screen, level_system, font, small_font):
    """統計パネルを表示（右上）"""
    screen_width, screen_height = screen.get_size()
    panel_width_percent = 0.25
    panel_height_percent = 0.18
    panel_x_percent = 0.95 - panel_width_percent # 右寄せ
    panel_y_percent = 0.75
    
    panel_x_abs = int(screen_width * panel_x_percent)
    panel_y_abs = int(screen_height * panel_y_percent)
    panel_width_abs = int(screen_width * panel_width_percent)
    panel_height_abs = int(screen_height * panel_height_percent)
    
    # パネル背景
    panel_surf = pygame.Surface((panel_width_abs, panel_height_abs))
    panel_surf.set_alpha(150)
    panel_surf.fill((30, 30, 60))
    screen.blit(panel_surf, (panel_x_abs, panel_y_abs))
    
    # パネル枠線
    pygame.draw.rect(screen, WHITE, (panel_x_abs, panel_y_abs, panel_width_abs, panel_height_abs), 2)
    
    # ��計情報
    y_offset_percent = panel_y_percent + 0.02
    
    draw_text_relative(screen, f"Level: {level_system.current_level}", 0.95 - 0.01, y_offset_percent, small_font, WHITE, anchor="topright")
    y_offset_percent += 0.03
    draw_text_relative(screen, f"Defeated: {level_system.total_enemies_defeated}", 0.95 - 0.01, y_offset_percent, small_font, WHITE, anchor="topright")
    y_offset_percent += 0.03
    score_mult = level_system.get_enemy_score_multiplier()
    draw_text_relative(screen, f"Score Mult: x{score_mult:.1f}", 0.95 - 0.01, y_offset_percent, small_font, YELLOW, anchor="topright")
    
    # 進行度バー（小）
    bar_width_percent = panel_width_percent - 0.025
    bar_height_percent = 0.01
    bar_x_percent = panel_x_percent + 0.01
    bar_y_percent = y_offset_percent + 0.025
    
    bar_width_abs = int(screen_width * bar_width_percent)
    bar_height_abs = int(screen_height * bar_height_percent)
    bar_x_abs = int(screen_width * bar_x_percent)
    bar_y_abs = int(screen_height * bar_y_percent)
    
    pygame.draw.rect(screen, (50, 50, 50), (bar_x_abs, bar_y_abs, bar_width_abs, bar_height_abs))
    
    progress = level_system.get_level_progress()
    fill_width_abs = int(bar_width_abs * progress)
    if fill_width_abs > 0:
        pygame.draw.rect(screen, CYAN, (bar_x_abs, bar_y_abs, fill_width_abs, bar_height_abs))
    
    pygame.draw.rect(screen, WHITE, (bar_x_abs, bar_y_abs, bar_width_abs, bar_height_abs), 1)

def draw_special_gauge(screen, player, font):
    screen_width, screen_height = screen.get_size()
    gauge_width_percent = 0.25
    gauge_height_percent = 0.03
    gauge_x_percent = 0.05
    gauge_y_percent = 0.95

    gauge_x_abs = int(screen_width * gauge_x_percent)
    gauge_y_abs = int(screen_height * gauge_y_percent)
    gauge_width_abs = int(screen_width * gauge_width_percent)
    gauge_height_abs = int(screen_height * gauge_height_percent)

    # ゲージの背景
    gauge_bg_rect = pygame.Rect(gauge_x_abs, gauge_y_abs, gauge_width_abs, gauge_height_abs)
    pygame.draw.rect(screen, DARK_GRAY, gauge_bg_rect)

    # ゲージの現在の値
    gauge_fill_width = (player.special_gauge / SPECIAL_GAUGE_MAX) * gauge_width_abs
    gauge_rect = pygame.Rect(gauge_x_abs, gauge_y_abs, gauge_fill_width, gauge_height_abs)
    pygame.draw.rect(screen, YELLOW, gauge_rect)

    # ゲージの枠
    pygame.draw.rect(screen, WHITE, gauge_bg_rect, 2)

    # ストック数
    draw_text_relative(screen, f"SP: {player.special_stock}", gauge_x_percent + gauge_width_percent + 0.02, gauge_y_percent + gauge_height_percent / 2, font, WHITE, anchor="midleft")

def draw_level_up_notification(screen, font, notification_timer):
    """レベルアップ通知を表示"""
    if notification_timer > 0:
        # 通知の透明度を時間に応じて変更
        alpha = min(255, notification_timer * 8)
        
        # 背景を少し暗くする
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(alpha // 3)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # レベルアップテキスト
        draw_text_relative(screen, "LEVEL UP!", 0.5, 0.45, font, YELLOW)

def draw_difficulty_info(screen, level_system, small_font):
    """現在の難易度情報を表示"""
    config = level_system.get_current_config()
    
    # 現在のレベル説明
    draw_text_relative(screen, config['description'], 0.05, 0.9, small_font, WHITE, anchor="topleft")
    
    # 難易度指標
    # 敵の強さ表示
    enemy_strength = f"Enemy Strength: x{config['enemy_speed_multiplier']:.1f}"
    draw_text_relative(screen, enemy_strength, 0.05, 0.93, small_font, RED if config['enemy_speed_multiplier'] > 1.5 else YELLOW if config['enemy_speed_multiplier'] > 1.2 else GREEN, anchor="topleft")
    
    # 敵の出現頻度表示
    spawn_rate = f"Spawn Rate: {60 // config['enemy_spawn_rate']:.1f}/sec"
    draw_text_relative(screen, spawn_rate, 0.05, 0.96, small_font, RED if config['enemy_spawn_rate'] < 30 else YELLOW if config['enemy_spawn_rate'] < 45 else GREEN, anchor="topleft")

def draw_level_transition(screen, font, small_font, level_system, transition_timer):
    """レベル移行時の画面表示"""
    if transition_timer > 0:
        # 背景を暗くする
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        config = level_system.get_current_config()
        
        # レベル情報表示
        draw_text_relative(screen, f"LEVEL {level_system.current_level}", 0.5, 0.4, font, CYAN)
        
        # レベル説明
        draw_text_relative(screen, config['description'], 0.5, 0.45, small_font, WHITE)
        
        # 新要素の表示
        new_feature_text = ""
        if level_system.current_level == 2:
            new_feature_text = "NEW: Tank Enemies - High HP, slow movement"
        elif level_system.current_level == 3:
            new_feature_text = "NEW: Zigzag Enemies - Unpredictable movement"
        elif level_system.current_level == 4:
            new_feature_text = "NEW: Sniper Enemies - Accurate shots"
        elif level_system.current_level == 5:
            new_feature_text = "NEW: Shield Enemies - Protected by barriers"
        elif level_system.current_level == 6:
            new_feature_text = "NEW: Stopper Enemies - Stop and attack"
        else:
            new_feature_text = "Difficulty Increased!"
        
        draw_text_relative(screen, new_feature_text, 0.5, 0.5, small_font, YELLOW)
        
        # 継続メッセージ
        draw_text_relative(screen, "Press SPACE to continue", 0.5, 0.6, small_font, WHITE)

def draw_stats_panel(screen, level_system, font, small_font):
    """統計パネルを表示（右上）"""
    screen_width, screen_height = screen.get_size()
    panel_width_percent = 0.25
    panel_height_percent = 0.18
    panel_x_percent = 0.95 - panel_width_percent # 右寄せ
    panel_y_percent = 0.75
    
    panel_x_abs = int(screen_width * panel_x_percent)
    panel_y_abs = int(screen_height * panel_y_percent)
    panel_width_abs = int(screen_width * panel_width_percent)
    panel_height_abs = int(screen_height * panel_height_percent)
    
    # パネル背景
    panel_surf = pygame.Surface((panel_width_abs, panel_height_abs))
    panel_surf.set_alpha(150)
    panel_surf.fill((30, 30, 60))
    screen.blit(panel_surf, (panel_x_abs, panel_y_abs))
    
    # パネル枠線
    pygame.draw.rect(screen, WHITE, (panel_x_abs, panel_y_abs, panel_width_abs, panel_height_abs), 2)
    
    # 統計情報
    y_offset_percent = panel_y_percent + 0.02
    
    draw_text_relative(screen, f"Level: {level_system.current_level}", 0.95 - 0.01, y_offset_percent, small_font, WHITE, anchor="topright")
    y_offset_percent += 0.03
    draw_text_relative(screen, f"Defeated: {level_system.total_enemies_defeated}", 0.95 - 0.01, y_offset_percent, small_font, WHITE, anchor="topright")
    y_offset_percent += 0.03
    score_mult = level_system.get_enemy_score_multiplier()
    draw_text_relative(screen, f"Score Mult: x{score_mult:.1f}", 0.95 - 0.01, y_offset_percent, small_font, YELLOW, anchor="topright")
    
    # 進行度バー（小）
    bar_width_percent = panel_width_percent - 0.025
    bar_height_percent = 0.01
    bar_x_percent = panel_x_percent + 0.01
    bar_y_percent = y_offset_percent + 0.025
    
    bar_width_abs = int(screen_width * bar_width_percent)
    bar_height_abs = int(screen_height * bar_height_percent)
    bar_x_abs = int(screen_width * bar_x_percent)
    bar_y_abs = int(screen_height * bar_y_percent)
    
    pygame.draw.rect(screen, (50, 50, 50), (bar_x_abs, bar_y_abs, bar_width_abs, bar_height_abs))
    
    progress = level_system.get_level_progress()
    fill_width_abs = int(bar_width_abs * progress)
    if fill_width_abs > 0:
        pygame.draw.rect(screen, CYAN, (bar_x_abs, bar_y_abs, fill_width_abs, bar_height_abs))
    
    pygame.draw.rect(screen, WHITE, (bar_x_abs, bar_y_abs, bar_width_abs, bar_height_abs), 1)

def draw_special_gauge(screen, player, font):
    screen_width, screen_height = screen.get_size()
    gauge_width_percent = 0.25
    gauge_height_percent = 0.03
    gauge_x_percent = 0.05
    gauge_y_percent = 0.95

    gauge_x_abs = int(screen_width * gauge_x_percent)
    gauge_y_abs = int(screen_height * gauge_y_percent)
    gauge_width_abs = int(screen_width * gauge_width_percent)
    gauge_height_abs = int(screen_height * gauge_height_percent)

    # ゲージの背景
    gauge_bg_rect = pygame.Rect(gauge_x_abs, gauge_y_abs, gauge_width_abs, gauge_height_abs)
    pygame.draw.rect(screen, DARK_GRAY, gauge_bg_rect)

    # ゲージの現在の値
    gauge_fill_width = (player.special_gauge / SPECIAL_GAUGE_MAX) * gauge_width_abs
    gauge_rect = pygame.Rect(gauge_x_abs, gauge_y_abs, gauge_fill_width, gauge_height_abs)
    pygame.draw.rect(screen, YELLOW, gauge_rect)

    # ゲージの枠
    pygame.draw.rect(screen, WHITE, gauge_bg_rect, 2)

    # ストック数
    draw_text_relative(screen, f"SP: {player.special_stock}", gauge_x_percent + gauge_width_percent + 0.02, gauge_y_percent + gauge_height_percent / 2, font, WHITE, anchor="midleft")

def draw_stage_clear(screen, font):
    """ステージクリア画面を描画"""
    overlay = pygame.Surface(screen.get_size())
    overlay.set_alpha(150)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    draw_text_relative(screen, "STAGE CLEAR", 0.5, 0.45, font, YELLOW)
    draw_text_relative(screen, "Click to Continue", 0.5, 0.55, font, WHITE)