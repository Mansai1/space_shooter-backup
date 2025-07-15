import pygame
from settings import *
from utils import draw_text # draw_textをインポート

def draw_level_info(screen, level_system, font, small_font, x, y_start):
    """レベル情報を画面に描画"""
    # レベル表示
    draw_text(screen, f"Level: {level_system.current_level}", x, y_start, font, WHITE)
    
    # 経験値バーの描画
    bar_width = 200
    bar_height = 10
    bar_x = x - bar_width // 2 + 10 # 中央寄せ
    bar_y = y_start + 30
    
    # 背景バー
    pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
    
    # 経験値バー
    progress = level_system.get_level_progress()
    fill_width = int(bar_width * progress)
    if fill_width > 0:
        pygame.draw.rect(screen, CYAN, (bar_x, bar_y, fill_width, bar_height))
    
    # バーの枠線
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
    
    # 経験値テキスト
    draw_text(screen, f"EXP: {level_system.experience}/{level_system.experience_to_next_level}", x, bar_y + bar_height + 15, small_font, WHITE)

def draw_level_up_notification(screen, font, notification_timer):
    """レベルアップ通知を表示"""
    if notification_timer > 0:
        # 通知の透明度を時間に応じて変更
        alpha = min(255, notification_timer * 8)
        
        # レベルアップテキスト
        level_up_text = font.render("LEVEL UP!", True, YELLOW)
        text_rect = level_up_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        
        # 背景を少し暗くする
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(alpha // 3)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # テキストに光る効果を追加
        glow_surf = pygame.Surface((text_rect.width + 20, text_rect.height + 20))
        glow_surf.set_alpha(alpha // 2)
        glow_surf.fill(YELLOW)
        screen.blit(glow_surf, (text_rect.x - 10, text_rect.y - 10))
        
        screen.blit(level_up_text, text_rect)

def draw_difficulty_info(screen, level_system, small_font, x, y_start):
    """現在の難易度情報を表示"""
    config = level_system.get_current_config()
    
    # 現在のレベル説明
    draw_text(screen, config['description'], x, y_start, small_font, WHITE)
    
    # 難易度指標
    y_offset = y_start + 20
    
    # 敵の強さ表示
    enemy_strength = f"Enemy Strength: x{config['enemy_speed_multiplier']:.1f}"
    strength_text = small_font.render(enemy_strength, True, RED if config['enemy_speed_multiplier'] > 1.5 else YELLOW if config['enemy_speed_multiplier'] > 1.2 else GREEN)
    screen.blit(strength_text, (x - strength_text.get_width() // 2, y_offset))
    
    # 敵の出現頻度表示
    spawn_rate = f"Spawn Rate: {60 // config['enemy_spawn_rate']:.1f}/sec"
    spawn_text = small_font.render(spawn_rate, True, RED if config['enemy_spawn_rate'] < 30 else YELLOW if config['enemy_spawn_rate'] < 45 else GREEN)
    screen.blit(spawn_text, (x - spawn_text.get_width() // 2, y_offset + 20))

def draw_level_transition(screen, font, small_font, level_system, transition_timer):
    """レベル移行時の画面表示"""
    if transition_timer > 0:
        # 背景を暗くする
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        config = level_system.get_current_config()
        
        # レベル情報表示
        level_title = font.render(f"LEVEL {level_system.current_level}", True, CYAN)
        title_rect = level_title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        screen.blit(level_title, title_rect)
        
        # レベル説明
        description = small_font.render(config['description'], True, WHITE)
        desc_rect = description.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        screen.blit(description, desc_rect)
        
        # 新要素の表示
        if level_system.current_level == 2:
            new_feature = small_font.render("NEW: Tank Enemies - High HP, slow movement", True, YELLOW)
        elif level_system.current_level == 3:
            new_feature = small_font.render("NEW: Zigzag Enemies - Unpredictable movement", True, YELLOW)
        elif level_system.current_level == 4:
            new_feature = small_font.render("NEW: Sniper Enemies - Accurate shots", True, YELLOW)
        elif level_system.current_level == 5:
            new_feature = small_font.render("NEW: Shield Enemies - Protected by barriers", True, YELLOW)
        elif level_system.current_level == 6:
            new_feature = small_font.render("NEW: Stopper Enemies - Stop and attack", True, YELLOW)
        else:
            new_feature = small_font.render("Difficulty Increased!", True, YELLOW)
        
        new_rect = new_feature.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(new_feature, new_rect)
        
        # 継続メッセージ
        continue_text = small_font.render("Press SPACE to continue", True, WHITE)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        screen.blit(continue_text, continue_rect)

def draw_stats_panel(screen, level_system, font, small_font, x, y_start):
    """統計パネルを表示（右上）"""
    panel_x = x - 100 # 中央寄せ
    panel_y = y_start
    panel_width = 210
    panel_height = 100
    
    # パネル背景
    panel_surf = pygame.Surface((panel_width, panel_height))
    panel_surf.set_alpha(150)
    panel_surf.fill((30, 30, 60))
    screen.blit(panel_surf, (panel_x, panel_y))
    
    # パネル枠線
    pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 2)
    
    # 統計情報
    y_offset = panel_y + 10
    
    draw_text(screen, f"Level: {level_system.current_level}", x, y_offset, small_font, WHITE)
    y_offset += 20
    draw_text(screen, f"Defeated: {level_system.total_enemies_defeated}", x, y_offset, small_font, WHITE)
    y_offset += 20
    score_mult = level_system.get_enemy_score_multiplier()
    draw_text(screen, f"Score Mult: x{score_mult:.1f}", x, y_offset, small_font, YELLOW)
    
    # 進行度バー（小）
    bar_width = 190
    bar_height = 6
    bar_x = panel_x + 10
    bar_y = y_offset + 15
    
    pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
    
    progress = level_system.get_level_progress()
    fill_width = int(bar_width * progress)
    if fill_width > 0:
        pygame.draw.rect(screen, CYAN, (bar_x, bar_y, fill_width, bar_height))
    
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

def draw_special_gauge(screen, player, font):
    # ゲージの背景
    gauge_bg_rect = pygame.Rect(10, SCREEN_HEIGHT - 40, 200, 20)
    pygame.draw.rect(screen, DARK_GRAY, gauge_bg_rect)

    # ゲージの現在の値
    gauge_width = (player.special_gauge / SPECIAL_GAUGE_MAX) * 200
    gauge_rect = pygame.Rect(10, SCREEN_HEIGHT - 40, gauge_width, 20)
    pygame.draw.rect(screen, YELLOW, gauge_rect)

    # ゲージの枠
    pygame.draw.rect(screen, WHITE, gauge_bg_rect, 2)

    # ストック数
    stock_text = font.render(f"SP: {player.special_stock}", True, WHITE)
    screen.blit(stock_text, (220, SCREEN_HEIGHT - 45))

def draw_stage_clear(screen, font):
    """ステージクリア画面を描画"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(150)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    clear_text = font.render("STAGE CLEAR", True, YELLOW)
    clear_rect = clear_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
    screen.blit(clear_text, clear_rect)

    continue_text = font.render("Click to Continue", True, WHITE)
    continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
    screen.blit(continue_text, continue_rect)