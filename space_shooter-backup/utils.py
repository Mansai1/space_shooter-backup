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

def draw_text_absolute(screen, text, x, y, font, color=WHITE, anchor="center"):
    """絶対座標でテキストを描画"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    
    if anchor == "topleft":
        text_rect.topleft = (x, y)
    elif anchor == "topright":
        text_rect.topright = (x, y)
    elif anchor == "midtop":
        text_rect.midtop = (x, y)
    elif anchor == "midleft":
        text_rect.midleft = (x, y)
    elif anchor == "center":
        text_rect.center = (x, y)
    elif anchor == "midright":
        text_rect.midright = (x, y)
    elif anchor == "bottomleft":
        text_rect.bottomleft = (x, y)
    elif anchor == "bottomright":
        text_rect.bottomright = (x, y)
    elif anchor == "midbottom":
        text_rect.midbottom = (x, y)
    else: # デフォルトは中央
        text_rect.center = (x, y)
        
    screen.blit(text_surface, text_rect)

def draw_text_relative(screen, text, x_percent, y_percent, font, color=WHITE, anchor="center"):
    """画面サイズに対する相対座標でテキストを描画"""
    screen_width, screen_height = screen.get_size()
    x_abs = int(screen_width * x_percent)
    y_abs = int(screen_height * y_percent)
    draw_text_absolute(screen, text, x_abs, y_abs, font, color, anchor)

def draw_text(screen, text, x, y, font, color=WHITE):
    """既存のdraw_textの呼び出しをdraw_text_absoluteにリダイレクト"""
    draw_text_absolute(screen, text, x, y, font, color, "center")

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


def draw_score(screen, score, font):
    """スコアを描画"""
    draw_text_relative(screen, f"スコア: {score}", 0.05, 0.05, font, WHITE, anchor="topleft")

def draw_lives(screen, lives, font):
    """残機を描画（アイコン＋数字）"""
    # 残機アイコンとしてプレイヤー画像を小さく表示
    import os
    img_path = os.path.join(os.path.dirname(__file__), 'assets', 'img', 'Image.png')
    try:
        icon = pygame.image.load(img_path).convert_alpha()
        icon_size = 24
        icon = pygame.transform.scale(icon, (icon_size, icon_size))
        for i in range(min(lives, 5)):
            screen.blit(icon, (20 + i * (icon_size + 6), 20))
        # 6機以上は「×n」表記
        if lives > 5:
            text = font.render(f"×{lives}", True, WHITE)
            screen.blit(text, (20 + 5 * (icon_size + 6), 20))
    except Exception:
        # 画像がない場合はテキストのみ
        pass
    # テキストで残機数も表示
    draw_text_relative(screen, f"残機: {lives}", 0.05, 0.1, font, WHITE, anchor="topleft")

def draw_powerups(screen, player, small_font):
    """プレイヤーのパワーアップ状態を表示"""
    draw_text_relative(screen, "パワーアップ:", 0.05, 0.15, small_font, YELLOW, anchor="topleft")
    
    # ライフアップアイテムの表示
    if "life_up" in player.powerups:
        draw_text_relative(screen, "残機アップ", 0.05, 0.18, small_font, GREEN, anchor="topleft")
    
    # パワーアップがない場合の表示
    if not player.powerups:
        draw_text_relative(screen, "なし", 0.05, 0.18, small_font, GRAY, anchor="topleft")

def draw_enemy_info(screen, enemies, small_font):
    """画面上の敵の種類と数を表示"""
    if not enemies:
        return
    
    enemy_counts = {}
    for enemy in enemies:
        enemy_type = type(enemy).__name__
        enemy_counts[enemy_type] = enemy_counts.get(enemy_type, 0) + 1
    
    y_offset_percent = 0.05
    draw_text_relative(screen, "敵情報:", 0.95, y_offset_percent, small_font, YELLOW, anchor="topright")
    y_offset_percent += 0.04
    
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
        
        draw_text_relative(screen, f"{display_name}: {count}", 0.95, y_offset_percent, small_font, color, anchor="topright")
        y_offset_percent += 0.03

def draw_sound_status(screen, sound_manager, small_font):
    """サウンド状態を表示"""
    if sound_manager:
        status = "BGM: ON" if sound_manager.music_playing else "BGM: OFF"
        color = GREEN if sound_manager.music_playing else RED
        draw_text_relative(screen, status, 0.95, 0.95, small_font, color, anchor="bottomright")

def draw_weapon_status(screen, player, small_font):
    """現在の武器状態を表示"""
    current_weapon = player.current_weapon.replace('_', ' ').title()
    weapon_color = WHITE
    
    if current_weapon == "Laser Weapon":
        weapon_color = CYAN
    elif current_weapon == "Wide Shot":
        weapon_color = GREEN
    
    draw_text_relative(screen, f"武器: {current_weapon}", 0.95, 0.9, small_font, weapon_color, anchor="bottomright")

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
    width, height = screen.get_size()
    draw_text(screen, "SPACE SHOOTER", width // 2, height // 2 - 100, font, WHITE)
    draw_text(screen, "Enemy Variety Edition", width // 2, height // 2 - 60, small_font, YELLOW)
    draw_text(screen, "スペースキーで開始", width // 2, height // 2, small_font, WHITE)
    draw_text(screen, "移動: WASD または 矢印キー", width // 2, height // 2 + 40, small_font, GRAY)
    draw_text(screen, "ショット: スペース", width // 2, height // 2 + 60, small_font, GRAY)
    draw_text(screen, "BGM切り替え: M", width // 2, height // 2 + 80, small_font, GRAY)
    draw_text(screen, "ポーズ: P", width // 2, height // 2 + 100, small_font, GRAY)
    
    # レーザーと爆弾の説明を追加
    draw_text(screen, "特殊武器: レーザー (貫通) & ボム (範囲攻撃)", width // 2, height // 2 + 140, small_font, CYAN)

def draw_game_over_screen(screen, score, font):
    """ゲームオーバー画面を描画"""
    # 半透明の黒いオーバーレイ
    overlay = pygame.Surface(screen.get_size())
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    draw_text_relative(screen, "GAME OVER", 0.5, 0.4, font, RED)
    draw_text_relative(screen, f"Final Score: {score}", 0.5, 0.5, font, WHITE)
    draw_text_relative(screen, "Press R to Retry", 0.5, 0.6, font, WHITE)
    draw_text_relative(screen, "Press Q to Quit", 0.5, 0.65, font, WHITE)

def draw_pause_screen(screen, font):
    """ポーズ画面を描画"""
    # 半透明の黒いオーバーレイ
    overlay = pygame.Surface(screen.get_size())
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    draw_text_relative(screen, "PAUSED", 0.5, 0.45, font, WHITE)
    draw_text_relative(screen, "Press P to Resume", 0.5, 0.55, font, WHITE)

def draw_sound_status(screen, sound_manager, small_font):
    """サウンド状態を表示"""
    if sound_manager:
        status = "BGM: ON" if sound_manager.music_playing else "BGM: OFF"
        color = GREEN if sound_manager.music_playing else RED
        draw_text_relative(screen, status, 0.95, 0.95, small_font, color, anchor="bottomright")

def draw_weapon_status(screen, player, small_font):
    """現在の武器状態を表示"""
    current_weapon = player.current_weapon.replace('_', ' ').title()
    weapon_color = WHITE
    
    if current_weapon == "Laser Weapon":
        weapon_color = CYAN
    elif current_weapon == "Wide Shot":
        weapon_color = GREEN
    
    draw_text_relative(screen, f"武器: {current_weapon}", 0.95, 0.9, small_font, weapon_color, anchor="bottomright")


def draw_special_gauge(screen, player, font):
    """必殺技ゲージを描画（画面比率対応版）"""
    # 画面サイズに応じてゲージの位置とサイズを調整
    screen_width, screen_height = screen.get_size()
    
    # ゲージのサイズと位置を画面比率に応じて調整
    gauge_width = int(screen_width * 0.15)  # 画面幅の15%
    gauge_height = int(screen_height * 0.03)  # 画面高さの3%
    x = int(screen_width * 0.05)  # 画面左端から5%
    y = int(screen_height * 0.85)  # 画面下端から15%
    
    # ゲージの背景
    bg_rect = pygame.Rect(x, y, gauge_width, gauge_height)
    pygame.draw.rect(screen, GRAY, bg_rect)
    
    # ゲージの充填部分
    fill_width = (player.special_gauge / player.max_special_gauge) * gauge_width
    fill_rect = pygame.Rect(x, y, fill_width, gauge_height)
    
    # ゲージの色を決定
    if player.special_gauge >= player.max_special_gauge:
        gauge_color = YELLOW  # 満タン
    else:
        gauge_color = BLUE
        
    pygame.draw.rect(screen, gauge_color, fill_rect)
    
    # ゲージの枠線
    pygame.draw.rect(screen, WHITE, bg_rect, 2)
    
    # テキスト（フォントサイズも画面比率に応じて調整）
    text_size = max(16, int(screen_height * 0.02))  # 最小16px、画面高さの2%
    try:
        text_font = pygame.font.Font(None, text_size)
    except:
        text_font = font  # フォールバック
    
    text_surf = text_font.render("SP", True, WHITE)
    text_rect = text_surf.get_rect()
    text_rect.midleft = (x + 10, y + gauge_height // 2)
    screen.blit(text_surf, text_rect)

def draw_adaptive_text(screen, text, x_percent, y_percent, base_font, color=WHITE, anchor="center", min_size=16):
    """画面比率に応じてフォントサイズを調整してテキストを描画"""
    screen_width, screen_height = screen.get_size()
    
    # 画面サイズに応じてフォントサイズを調整
    base_size = base_font.get_height()
    scale_factor = min(screen_width / 800, screen_height / 600)  # 800x600を基準とする
    new_size = max(min_size, int(base_size * scale_factor))
    
    try:
        # 新しいサイズでフォントを作成
        adaptive_font = pygame.font.Font(base_font.get_filename(), new_size)
    except:
        # フォールバック: 既存のフォントを使用
        adaptive_font = base_font
    
    # 相対座標を絶対座標に変換
    x_abs = int(screen_width * x_percent)
    y_abs = int(screen_height * y_percent)
    
    # テキストを描画
    draw_text_absolute(screen, text, x_abs, y_abs, adaptive_font, color, anchor)

def create_adaptive_button(screen, text, x_percent, y_percent, width_percent, height_percent, font, color=DARK_GRAY, text_color=WHITE):
    """画面比率に応じてボタンのサイズと位置を調整"""
    screen_width, screen_height = screen.get_size()
    
    x = int(screen_width * x_percent)
    y = int(screen_height * y_percent)
    width = int(screen_width * width_percent)
    height = int(screen_height * height_percent)
    
    button_rect = pygame.Rect(x, y, width, height)
    
    # ボタンの背景を描画
    pygame.draw.rect(screen, color, button_rect, border_radius=10)
    
    # テキストを中央に配置
    draw_text_absolute(screen, text, button_rect.centerx, button_rect.centery, font, text_color, anchor="center")
    
    return button_rect

def draw_adaptive_ui_panel(screen, x_percent, y_percent, width_percent, height_percent, color=DARK_GRAY, alpha=128):
    """画面比率に応じてUIパネルを描画"""
    screen_width, screen_height = screen.get_size()
    
    x = int(screen_width * x_percent)
    y = int(screen_height * y_percent)
    width = int(screen_width * width_percent)
    height = int(screen_height * height_percent)
    
    # 半透明のパネルを作成
    panel = pygame.Surface((width, height))
    panel.set_alpha(alpha)
    panel.fill(color)
    
    # パネルを描画
    screen.blit(panel, (x, y))
    
    return pygame.Rect(x, y, width, height)

def draw_fps_counter(screen, fps, font, position="topright", bg_alpha=180):
    """画面にFPSカウンターを表示（画面比率対応）"""
    try:
        # FPSの値に応じて色を変更
        if fps >= 55:  # 高FPS
            fps_color = GREEN
        elif fps >= 45:  # 中FPS
            fps_color = YELLOW
        else:  # 低FPS
            fps_color = RED
        
        # FPSテキストを作成
        fps_text = f"FPS: {fps}"
        
        # 画面サイズを取得
        screen_width, screen_height = screen.get_size()
        
        # 位置を計算
        if position == "topright":
            x = screen_width - 20
            y = 20
            anchor = "topright"
        elif position == "topleft":
            x = 20
            y = 20
            anchor = "topleft"
        elif position == "bottomright":
            x = screen_width - 20
            y = screen_height - 20
            anchor = "bottomright"
        elif position == "bottomleft":
            x = 20
            y = screen_height - 20
            anchor = "bottomleft"
        else:  # デフォルトは右上
            x = screen_width - 20
            y = 20
            anchor = "topright"
        
        # テキストを描画
        text_surface = font.render(fps_text, True, fps_color)
        text_rect = text_surface.get_rect()
        
        # アンカーに応じて位置を設定
        if anchor == "topright":
            text_rect.topright = (x, y)
        elif anchor == "topleft":
            text_rect.topleft = (x, y)
        elif anchor == "bottomright":
            text_rect.bottomright = (x, y)
        elif anchor == "bottomleft":
            text_rect.bottomleft = (x, y)
        
        # 背景の四角形を描画（半透明）
        bg_rect = text_rect.inflate(10, 4)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surface.set_alpha(bg_alpha)
        bg_surface.fill(BLACK)
        
        # 背景とテキストを描画
        screen.blit(bg_surface, bg_rect)
        screen.blit(text_surface, text_rect)
        
        return text_rect
        
    except Exception as e:
        # FPS表示でエラーが発生した場合は何もしない
        print(f"FPS表示エラー: {e}")
        return None