import pygame
import math
import random
import os # 追加
from settings import *
from boss.boss_bullet import BossBullet

class Boss:
    """東方風ボスの基底クラス"""
    
    def __init__(self, x, y, boss_type="basic", font=None, base_dir=None):
        self.x = x
        self.y = y
        self.boss_type = boss_type
        self.width = 80
        self.height = 80
        self.rect = pygame.Rect(x - self.width//2, y - self.height//2, self.width, self.height)
        self.font = font # フォントをインスタンス変数として保持
        self.image = None
        self.base_dir = base_dir # base_dirをインスタンス変数として保持
        
        # ボスの基本ステータス
        self.max_health = 0 # 総体力はスペルカードの合計で計算
        self.health = 0
        self.speed = 1.0
        self.score_value = 5000

        # スペルカード体力管理
        self.current_spell_max_health = 0
        self.current_spell_health = 0
        
        # 移動パターン
        self.move_timer = 0
        self.move_pattern = 0
        self.move_direction = 1
        self.target_x = x
        self.target_y = y
        
        # 弾幕システム
        self.spell_cards = []
        self.current_spell = 0
        self.spell_timer = 0
        self.spell_phase = 0
        self.is_casting = False
        
        # アニメーション
        self.animation_timer = 0
        self.flash_timer = 0
        
        # 状態管理
        self.active = True
        self.invulnerable = False
        self.entrance_timer = 180  # 3秒間の登場演出
        
        # ボスタイプ別の初期化
        self.init_boss_type()
    
    def init_boss_type(self):
        """ボスタイプ別の初期化"""
        total_health = 0
        if self.boss_type == "fairy":
            self.score_value = 3000
            self.spell_cards = [
                {"name": "妖精の舞", "pattern": "fairy_dance", "duration": 5400, "spell_health": 100},
                {"name": "光の乱舞", "pattern": "light_burst", "duration": 5400, "spell_health": 150}
            ]
            try:
                # base_dirを使用して絶対パスを構築
                image_path = os.path.join(self.base_dir, "assets", "img", "faily.png")
                self.image = pygame.image.load(image_path).convert()
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
            except pygame.error as e:
                print(f"Error loading boss image: {e}")
                self.image = None
            
        elif self.boss_type == "witch":
            self.score_value = 8000
            self.spell_cards = [
                {"name": "魔法の嵐", "pattern": "magic_storm", "duration": 5400, "spell_health": 200},
                {"name": "星屑の雨", "pattern": "star_rain", "duration": 5400, "spell_health": 250},
                {"name": "螺旋の呪文", "pattern": "spiral_curse", "duration": 5400, "spell_health": 300}
            ]
            try:
                # base_dirを使用して絶対パスを構築
                image_path = os.path.join(self.base_dir, "assets", "img", "magichuman.png")
                self.image = pygame.image.load(image_path).convert()
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
            except pygame.error as e:
                print(f"Error loading boss image: {e}")
                self.image = None
            
        elif self.boss_type == "dragon":
            self.score_value = 12000
            self.spell_cards = [
                {"name": "竜の咆哮", "pattern": "dragon_roar", "duration": 5400, "spell_health": 300},
                {"name": "炎の渦", "pattern": "fire_spiral", "duration": 5400, "spell_health": 350},
                {"name": "雷光の槍", "pattern": "thunder_spear", "duration": 5400, "spell_health": 400},
                {"name": "究極竜破", "pattern": "ultimate_blast", "duration": 5400, "spell_health": 500}
            ]
            try:
                # base_dirを使用して絶対パスを構築
                image_path = os.path.join(self.base_dir, "assets", "img", "dragon.png")
                self.image = pygame.image.load(image_path).convert()
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
            except pygame.error as e:
                print(f"Error loading boss image: {e}")
                self.image = None

        # スペルカードの体力を合計してボスの総体力を設定
        for spell in self.spell_cards:
            total_health += spell["spell_health"]
        self.max_health = total_health
        self.health = total_health # 初期体力は総体力と同じ

        # 現在のスペルカードの体力を初期化
        if self.spell_cards:
            self.current_spell_max_health = self.spell_cards[self.current_spell]["spell_health"]
            self.current_spell_health = self.current_spell_max_health
    
    def update(self):
        """ボスの更新処理"""
        if not self.active:
            return []
        
        # 登場演出中は移動のみ
        if self.entrance_timer > 0:
            self.entrance_timer -= 1
            # 上から下に降りてくる演出
            if self.y < 120:
                self.y += 2
            self.update_rect()
            return []
        
        # 移動パターンの更新
        self.update_movement()
        
        # スペルカード（弾幕パターン）の更新
        bullets = self.update_spell_cards()
        
        # アニメーション更新
        self.animation_timer += 1
        if self.flash_timer > 0:
            self.flash_timer -= 1
        
        self.update_rect()
        return bullets
    
    def update_movement(self):
        """移動パターンの更新"""
        self.move_timer += 1
        
        if self.boss_type == "fairy":
            # 軽やかな左右移動
            if self.move_timer % 120 == 0:
                self.target_x = random.randint(100, SCREEN_WIDTH - 100)
            
            # 滑らかな移動
            dx = self.target_x - self.x
            if abs(dx) > 2:
                self.x += dx * 0.02
                
        elif self.boss_type == "witch":
            # 複雑な円運動
            center_x = SCREEN_WIDTH // 2
            center_y = 150
            radius = 80
            angle = self.move_timer * 0.02
            self.x = center_x + math.cos(angle) * radius
            self.y = center_y + math.sin(angle * 2) * 30
            
        elif self.boss_type == "dragon":
            # 威圧的な左右移動
            if self.move_timer % 180 == 0:
                self.move_direction *= -1
                self.target_x = SCREEN_WIDTH // 4 if self.move_direction < 0 else SCREEN_WIDTH * 3 // 4
            
            dx = self.target_x - self.x
            if abs(dx) > 3:
                self.x += dx * 0.015
    
    def update_spell_cards(self):
        """スペルカード（弾幕パターン）の更新"""
        if not self.spell_cards:
            return []
        
        bullets = []
        current_spell_data = self.spell_cards[self.current_spell]
        
        # スペルカード発動
        if not self.is_casting:
            self.is_casting = True
            self.spell_timer = 0
            self.spell_phase = 0
        
        self.spell_timer += 1
        
        # パターン別の弾幕生成
        pattern_bullets = self.execute_spell_pattern(current_spell_data["pattern"])
        bullets.extend(pattern_bullets)
        
        # スペルカード終了判定
        if self.spell_timer >= current_spell_data["duration"]:
            self.is_casting = False
            # スペルカードの体力が残っていても、時間切れで次のスペルカードへ移行
            if self.current_spell_health > 0 and self.current_spell < len(self.spell_cards) - 1:
                self.current_spell += 1
                self.current_spell_max_health = self.spell_cards[self.current_spell]["spell_health"]
                self.current_spell_health = self.current_spell_max_health
            self.spell_timer = 0
        
        return bullets
    
    def execute_spell_pattern(self, pattern):
        """弾幕パターンの実行"""
        bullets = []
        
        if pattern == "fairy_dance":
            # 妖精の舞：回転しながら弾を発射
            if self.spell_timer % 20 == 0:
                for i in range(8):
                    angle = (self.spell_timer * 0.1 + i * 45) * math.pi / 180
                    speed = 2.5
                    bullet = BossBullet(
                        self.x + math.cos(angle) * 30,
                        self.y + math.sin(angle) * 30,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed,
                        color=CYAN
                    )
                    bullets.append(bullet)
        
        elif pattern == "light_burst":
            # 光の乱舞：放射状の弾幕
            if self.spell_timer % 30 == 0:
                for i in range(12):
                    angle = i * 30 * math.pi / 180
                    speed = 3.0
                    bullet = BossBullet(
                        self.x,
                        self.y,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed,
                        color=YELLOW
                    )
                    bullets.append(bullet)
        
        elif pattern == "magic_storm":
            # 魔法の嵐：複雑な螺旋弾幕
            if self.spell_timer % 8 == 0:
                for layer in range(3):
                    angle = (self.spell_timer * 0.2 + layer * 120) * math.pi / 180
                    speed = 2.0 + layer * 0.5
                    bullet = BossBullet(
                        self.x,
                        self.y,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed,
                        color=MAGENTA
                    )
                    bullets.append(bullet)
        
        elif pattern == "star_rain":
            # 星屑の雨：上から降ってくる弾幕
            if self.spell_timer % 15 == 0:
                for i in range(5):
                    x = random.randint(50, SCREEN_WIDTH - 50)
                    bullet = BossBullet(x, -10, 0, 3.5, color=WHITE)
                    bullets.append(bullet)
        
        elif pattern == "spiral_curse":
            # 螺旋の呪文：螺旋状の弾幕
            if self.spell_timer % 5 == 0:
                angle = self.spell_timer * 0.3 * math.pi / 180
                radius = 50 + (self.spell_timer % 100) * 2
                for direction in [-1, 1]:
                    final_angle = angle * direction
                    speed = 2.5
                    bullet = BossBullet(
                        self.x + math.cos(final_angle) * 20,
                        self.y + math.sin(final_angle) * 20,
                        math.cos(final_angle) * speed,
                        math.sin(final_angle) * speed,
                        color=RED
                    )
                    bullets.append(bullet)
        
        elif pattern == "dragon_roar":
            # 竜の咆哮：扇状の強力な弾幕
            if self.spell_timer % 40 == 0:
                center_angle = math.atan2(400 - self.y, SCREEN_WIDTH//2 - self.x)  # プレイヤー方向
                for i in range(15):
                    angle = center_angle + (i - 7) * 0.2
                    speed = 4.0
                    bullet = BossBullet(
                        self.x,
                        self.y + 30,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed,
                        color=ORANGE
                    )
                    bullets.append(bullet)
        
        elif pattern == "fire_spiral":
            # 炎の渦：回転する炎弾
            if self.spell_timer % 12 == 0:
                for ring in range(2):
                    for i in range(6):
                        angle = (self.spell_timer * 0.15 + i * 60 + ring * 30) * math.pi / 180
                        speed = 2.0 + ring * 0.8
                        bullet = BossBullet(
                            self.x,
                            self.y,
                            math.cos(angle) * speed,
                            math.sin(angle) * speed,
                            color=RED
                        )
                        bullets.append(bullet)
        
        elif pattern == "thunder_spear":
            # 雷光の槍：直線的な高速弾
            if self.spell_timer % 60 == 0:
                for i in range(3):
                    target_x = random.randint(100, SCREEN_WIDTH - 100)
                    target_y = SCREEN_HEIGHT
                    angle = math.atan2(target_y - self.y, target_x - self.x)
                    speed = 6.0
                    bullet = BossBullet(
                        self.x,
                        self.y,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed,
                        color=BLUE
                    )
                    bullets.append(bullet)
        
        elif pattern == "ultimate_blast":
            # 究極竜破：全方位超弾幕
            if self.spell_timer % 6 == 0:
                for i in range(15):
                    angle = i * 24 * math.pi / 180
                    speed = 2.0 + random.random()
                    bullet = BossBullet(
                        self.x,
                        self.y,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed,
                        color=PURPLE
                    )
                    bullets.append(bullet)
        
        return bullets
    
    def take_damage(self, damage):
        """ダメージを受ける"""
        if self.invulnerable or self.entrance_timer > 0:
            return False
        
        # スペルカードの体力にダメージを適用
        self.current_spell_health -= damage
        self.health -= damage # ボス全体の体力も減らす
        self.flash_timer = 10  # 被弾フラッシュ効果
        
        # スペルカードの体力が0になったら次のスペルカードへ
        if self.current_spell_health <= 0:
            self.is_casting = False # 現在のスペルカードを終了
            self.current_spell += 1
            if self.current_spell < len(self.spell_cards):
                # 次のスペルカードの体力を初期化
                self.current_spell_max_health = self.spell_cards[self.current_spell]["spell_health"]
                self.current_spell_health = self.current_spell_max_health
            else:
                # 全てのスペルカードを撃破したらボス撃破
                self.active = False
                return True  # 撃破された
        
        if self.health <= 0:
            self.active = False
            return True  # 撃破された
        
        return False  # まだ生きている
    
    def update_rect(self):
        """矩形の更新"""
        self.rect = pygame.Rect(
            self.x - self.width//2,
            self.y - self.height//2,
            self.width,
            self.height
        )
    
    def draw(self, screen):
        """ボスの描画"""
        if not self.active:
            return
        
        # ボスの本体描画
        color = WHITE
        if self.flash_timer > 0:
            color = RED  # 被弾時は赤く光る
        elif self.entrance_timer > 0:
            # 登場演出中は透明度を上げる
            alpha = min(255, (180 - self.entrance_timer) * 3)
            color = (*WHITE[:3], alpha) if len(WHITE) == 4 else WHITE
        
        # ボスタイプ別の描画
        if self.boss_type == "fairy":
            if self.image:
                screen.blit(self.image, self.rect)
            else:
                # 妖精：円形で小さめ
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 30)
                pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), 30, 3)
            
        elif self.boss_type == "witch":
            if self.image:
                screen.blit(self.image, self.rect)
            else:
                # 魔女：複雑な形状
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 35)
                pygame.draw.circle(screen, MAGENTA, (int(self.x), int(self.y)), 35, 4)
                # 魔法陣エフェクト
                if self.is_casting:
                    angle = self.animation_timer * 0.1
                    for i in range(6):
                        x = self.x + math.cos(angle + i * 60 * math.pi / 180) * 45
                        y = self.y + math.sin(angle + i * 60 * math.pi / 180) * 45
                        pygame.draw.circle(screen, YELLOW, (int(x), int(y)), 3)
        
        elif self.boss_type == "dragon":
            if self.image:
                screen.blit(self.image, self.rect)
            else:
                # ドラゴン：大きく威圧的
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 40)
                pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), 40, 5)
                # 威圧オーラ
            if self.animation_timer % 60 < 30:
                pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 50, 2)

    def get_current_spell_data(self):
        """現在のスペルカードの体力と名前を取得"""
        if self.spell_cards and self.current_spell < len(self.spell_cards):
            return {
                "name": self.spell_cards[self.current_spell]["name"],
                "current_health": self.current_spell_health,
                "max_health": self.current_spell_max_health
            }
        return None

    def draw_outline(self, screen, color, width):
        """ボスの外枠を描画"""
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.width // 2 + width, width)

class BossManager:
    """ボス管理クラス"""
    
    def __init__(self, base_dir=None):
        self.current_boss = None
        self.boss_queue = []
        self.boss_defeated_count = 0
        self.base_dir = base_dir # base_dirをインスタンス変数として保持
        
        # ボス出現スケジュール
        self.boss_schedule = [
            {"level": 3, "type": "fairy"},
            {"level": 6, "type": "witch"},
            {"level": 10, "type": "dragon"},
            # レベル10以降は5レベルごとにボスが出現
        ]
    
    def should_spawn_boss(self, level, enemies_defeated):
        """ボス出現判定"""
        # スケジュールされたボス
        for boss_data in self.boss_schedule:
            if level == boss_data["level"] and not self.current_boss:
                return boss_data["type"]
        
        # レベル10以降は5レベルごと
        if level >= 10 and level % 5 == 0 and not self.current_boss:
            boss_types = ["fairy", "witch", "dragon"]
            return random.choice(boss_types)
        
        return None
    
    def spawn_boss(self, boss_type, font): # font引数を追加
        """ボスを生成"""
        if self.current_boss:
            return None
        
        x = SCREEN_WIDTH // 2
        y = -50  # 画面上から登場
        self.current_boss = Boss(x, y, boss_type, font, self.base_dir) # fontとbase_dirをBossコンストラクタに渡す
        return self.current_boss
    
    def update(self):
        """ボス管理の更新"""
        if not self.current_boss:
            return []
        
        bullets = self.current_boss.update()
        
        # ボスが撃破された場合
        if not self.current_boss.active:
            self.boss_defeated_count += 1
            self.current_boss = None
        
        return bullets
    
    def get_current_boss(self):
        """現在のボスを取得"""
        return self.current_boss
    
    def has_active_boss(self):
        """アクティブなボスがいるかチェック"""
        return self.current_boss is not None and self.current_boss.active