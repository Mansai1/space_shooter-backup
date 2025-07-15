import pygame
import random
import math
import os
from settings import *


def init_font():
    """メインフォントの初期化"""
    font_path = os.path.join(os.path.dirname(__file__), "NotoSansJP-VariableFont_wght.ttf")
    try:
        return pygame.font.Font(font_path, 36)
    except Exception as e:
        print(f"Error loading font {font_path}: {e}")
        # フォントの初期化に失敗した場合はエラーを発生させる
        raise

def init_small_font():
    """小さいフォントの初期化"""
    font_path = os.path.join(os.path.dirname(__file__), "NotoSansJP-VariableFont_wght.ttf")
    try:
        return pygame.font.Font(font_path, 20)
    except Exception as e:
        print(f"Error loading font {font_path}: {e}")
        # フォントの初期化に失敗した場合はエラーを発生させる
        raise

def draw_text(screen, text, x, y, font, color=WHITE):
    """テキストを描画"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.centery = y
    screen.blit(text_surface, text_rect)

def draw_text_multiline(screen, text, font, color, rect, start_x, start_y):
    """指定された矩形内にテキストを折り返して描画"""
    lines = text.splitlines()
    y = start_y
    for line in lines:
        words = line.split(' ')
        space = font.size(' ')[0]  # 幅 of a space.
        x = start_x
        for word in words:
            word_surface = font.render(word, True, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= rect.right:
                x = start_x  # Reset the x.
                y += word_height  # Start on new row.
            screen.blit(word_surface, (x, y))
            x += word_width + space
        y += font.get_linesize()


def draw_score(screen, score, font, x, y):
    """スコアを描画"""
    draw_text(screen, f"スコア: {score}", x, y, font, WHITE)

def draw_lives(screen, lives, font, x, y):
    """ライフを描画"""
    draw_text(screen, f"HP: {lives}", x, y, font, WHITE)

def draw_powerups(screen, player, small_font, x, y_start):
    """プレイヤーのパワーアップ状態を表示"""
    y_offset = y_start
    draw_text(screen, "パワーアップ:", x, y_offset, small_font, YELLOW)
    y_offset += 25
    
    # ライフアップアイテムの表示
    if "life_up" in player.powerups:
        draw_text(screen, "残機アップ", x, y_offset, small_font, GREEN)
        y_offset += 20
    
    # パワーアップがない場合の表示
    if not player.powerups:
        draw_text(screen, "なし", x, y_offset, small_font, GRAY)
        y_offset += 20

def draw_enemy_info(screen, enemies, small_font, x, y_start):
    """画面上の敵の種類と数を表示"""
    if not enemies:
        return
    
    enemy_counts = {}
    for enemy in enemies:
        enemy_type = type(enemy).__name__
        enemy_counts[enemy_type] = enemy_counts.get(enemy_type, 0) + 1
    
    y_offset = y_start
    draw_text(screen, "敵情報:", x, y_offset, small_font, YELLOW)
    y_offset += 25
    
    enemy_colors = {
        'BasicEnemy': RED,
        'SpeedEnemy': (255, 165, 0),
        'ZigzagEnemy': GREEN,
        'KamikazeEnemy': MAGENTA,
        'SniperEnemy': (128, 0, 128),
        'ShieldEnemy': BLUE,
        'TankEnemy': GRAY,
        'StopperEnemy': CYAN
    }
    
    for enemy_type, count in enemy_counts.items():
        type_names = {
            'BasicEnemy': 'ノーマル',
            'SpeedEnemy': 'スピーダー',
            'ZigzagEnemy': 'ジグザグ',
            'KamikazeEnemy': 'カミカゼ',
            'SniperEnemy': 'スナイパー',
            'ShieldEnemy': 'シールド',
            'TankEnemy': 'タンク',
            'StopperEnemy': 'ストッパー'
        }
        
        display_name = type_names.get(enemy_type, enemy_type)
        color = enemy_colors.get(enemy_type, WHITE)
        
        draw_text(screen, f"{display_name}: {count}", x, y_offset, small_font, color)
        y_offset += 20

def draw_sound_status(screen, sound_manager, small_font, x, y):
    """サウンド状態を表示"""
    if sound_manager:
        status = "BGM: ON" if sound_manager.music_playing else "BGM: OFF"
        color = GREEN if sound_manager.music_playing else RED
        draw_text(screen, status, x, y, small_font, color)

def draw_weapon_status(screen, player, small_font, x, y):
    """現在の武器状態を表示"""
    current_weapon = player.current_weapon.replace('_', ' ').title()
    weapon_color = WHITE
    
    if current_weapon == "Laser Weapon":
        weapon_color = CYAN
    elif current_weapon == "Wide Shot":
        weapon_color = GREEN
    
    draw_text(screen, f"武器: {current_weapon}", x, y, small_font, weapon_color)

def check_collision(rect1, rect2):
    """矩形の当たり判定"""
    return rect1.colliderect(rect2)

def check_circle_collision(x1, y1, r1, x2, y2, r2):
    """円形の当たり判定"""
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance < (r1 + r2)

def check_laser_collision(laser, enemy):
    """レーザーと敵の当たり判定"""
    if not hasattr(laser, 'rect') or not hasattr(enemy, 'rect'):
        return False
    return laser.rect.colliderect(enemy.rect)

def check_bomb_explosion_collision(bomb, enemy):
    """爆弾の爆発範囲と敵の当たり判定"""
    if not bomb.exploded or bomb.explosion_radius <= 0:
        return False
    
    # 円形の当たり判定
    distance = math.sqrt((enemy.x - bomb.x) ** 2 + (enemy.y - bomb.y) ** 2)
    return distance <= bomb.explosion_radius

# パーティクル関連の関数
def create_explosion_effect():
    """爆発エフェクトのパーティクルを生成"""
    particles = []
    for _ in range(15):  # パーティクル数を増加
        particle = {
            'x': 0,  # 後で設定
            'y': 0,  # 後で設定
            'vx': random.uniform(-4, 4),
            'vy': random.uniform(-4, 4),
            'life': 40,
            'max_life': 40,
            'color': random.choice([RED, YELLOW, ORANGE, WHITE])
        }
        particles.append(particle)
    return particles

def create_laser_hit_effect():
    """レーザーヒットエフェクトのパーティクルを生成"""
    particles = []
    for _ in range(8):
        particle = {
            'x': 0,  # 後で設定
            'y': 0,  # 後で設定
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-2, 2),
            'life': 15,
            'max_life': 15,
            'color': random.choice([CYAN, WHITE, BLUE])
        }
        particles.append(particle)
    return particles

def create_bomb_explosion_effect():
    """爆弾爆発エフェクトのパーティクルを生成"""
    particles = []
    for _ in range(25):  # より多くのパーティクル
        particle = {
            'x': 0,  # 後で設定
            'y': 0,  # 後で設定
            'vx': random.uniform(-6, 6),
            'vy': random.uniform(-6, 6),
            'life': 60,
            'max_life': 60,
            'color': random.choice([ORANGE, RED, YELLOW, WHITE])
        }
        particles.append(particle)
    return particles

def create_powerup_effect():
    """パワーアップエフェクトのパーティクルを生成"""
    particles = []
    for _ in range(12):
        particle = {
            'x': 0,  # 後で設定
            'y': 0,  # 後で設定
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-2, 2),
            'life': 30,
            'max_life': 30,
            'color': random.choice([CYAN, GREEN, BLUE, MAGENTA])
        }
        particles.append(particle)
    return particles

def update_particles(particles):
    """パーティクルの更新"""
    for particle in particles[:]:
        particle['x'] += particle['vx']
        particle['y'] += particle['vy']
        particle['life'] -= 1
        
        # 重力効果
        particle['vy'] += 0.1
        
        # 空気抵抗
        particle['vx'] *= 0.98
        particle['vy'] *= 0.98
        
        if particle['life'] <= 0:
            particles.remove(particle)

def draw_particles(screen, particles):
    """パーティクルの描画"""
    for particle in particles:
        # 寿命に応じて透明度を計算
        alpha = int(255 * (particle['life'] / particle['max_life']))
        alpha = max(0, min(255, alpha))
        
        # パーティクルのサイズを計算
        size = max(1, int(4 * (particle['life'] / particle['max_life'])))
        
        # 色にアルファ値を適用（簡易版）
        color = particle['color']
        if alpha < 255:
            # 背景色と混合して透明度を表現
            bg_color = BLACK
            r = int(color[0] * alpha / 255 + bg_color[0] * (255 - alpha) / 255)
            g = int(color[1] * alpha / 255 + bg_color[1] * (255 - alpha) / 255)
            b = int(color[2] * alpha / 255 + bg_color[2] * (255 - alpha) / 255)
            color = (r, g, b)
        
        # パーティクルを描画
        pygame.draw.circle(screen, color, (int(particle['x']), int(particle['y'])), size)

def draw_title_screen(screen, font, small_font):
    """タイトル画面を描画"""
    draw_text(screen, "SPACE SHOOTER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100, font, WHITE)
    draw_text(screen, "Enemy Variety Edition", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60, small_font, YELLOW)
    draw_text(screen, "スペースキーで開始", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, small_font, WHITE)
    draw_text(screen, "移動: WASD または 矢印キー", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40, small_font, GRAY)
    draw_text(screen, "ショット: スペース", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60, small_font, GRAY)
    draw_text(screen, "BGM切り替え: M", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, small_font, GRAY)
    draw_text(screen, "ポーズ: P", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100, small_font, GRAY)
    
    # レーザーと爆弾の説明を追加
    draw_text(screen, "特殊武器: レーザー (貫通) & ボム (範囲攻撃)", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 140, small_font, CYAN)

def draw_game_over_screen(screen, score, font):
    """ゲームオーバー画面を描画"""
    # 半透明の黒いオーバーレイ
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    draw_text(screen, "GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, font, RED)
    draw_text(screen, f"Final Score: {score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, font, WHITE)
    draw_text(screen, "Press R to Retry", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, font, WHITE)
    draw_text(screen, "Press Q to Quit", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, font, WHITE)

def draw_pause_screen(screen, font):
    """ポーズ画面を描画"""
    # 半透明の黒いオーバーレイ
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    draw_text(screen, "PAUSED", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, font, WHITE)
    draw_text(screen, "Press P to Resume", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, font, WHITE)

def draw_sound_status(screen, sound_manager, small_font, x, y):
    """サウンド状態を表示"""
    if sound_manager:
        status = "BGM: ON" if sound_manager.music_playing else "BGM: OFF"
        color = GREEN if sound_manager.music_playing else RED
        draw_text(screen, status, x, y, small_font, color)

def draw_weapon_status(screen, player, small_font, x, y):
    """現在の武器状態を表示"""
    current_weapon = player.current_weapon.replace('_', ' ').title()
    weapon_color = WHITE
    
    if current_weapon == "Laser Weapon":
        weapon_color = CYAN
    elif current_weapon == "Wide Shot":
        weapon_color = GREEN
    
    draw_text(screen, f"武器: {current_weapon}", x, y, small_font, weapon_color)


def draw_special_gauge(screen, player, x, y, width, height):
    """必殺技ゲージを描画"""
    # ゲージの背景
    bg_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, GRAY, bg_rect)
    
    # ゲージの充填部分
    fill_width = (player.special_gauge / player.max_special_gauge) * width
    fill_rect = pygame.Rect(x, y, fill_width, height)
    
    # ゲージの色を決定
    if player.special_gauge >= player.max_special_gauge:
        gauge_color = YELLOW  # 満タン
    else:
        gauge_color = BLUE
        
    pygame.draw.rect(screen, gauge_color, fill_rect)
    
    # ゲージの枠線
    pygame.draw.rect(screen, WHITE, bg_rect, 2)
    
    # テキスト
    font = pygame.font.Font(None, 20)
    text_surf = font.render("SP", True, WHITE)
    screen.blit(text_surf, (x + 5, y + 2))