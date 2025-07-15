import pygame
import math
import os
from settings import *

class Option:
    """プレイヤーの子機クラス"""
    def __init__(self, option_id, player, offset_angle=0, distance=60):
        self.option_id = option_id
        self.player = player
        self.x = player.x
        self.y = player.y
        self.size = PLAYER_SIZE // 2  # プレイヤーの半分のサイズ
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        
        # 追従関連
        self.follow_positions = []  # プレイヤーの過去の位置を記録
        self.follow_delay = 10  # 追従の遅延フレーム数
        self.max_follow_positions = 30  # 記録する位置の最大数
        
        # 軌道運動関連
        self.orbit_mode = False
        self.orbit_angle = offset_angle
        self.orbit_distance = distance
        self.orbit_speed = 2  # 軌道運動の速度
        
        # 射撃関連
        self.shoot_cooldown = 0
        self.shoot_interval = 20  # 子機の射撃間隔
        
        # ビジュアル
        image_path = os.path.join(os.path.dirname(__file__), "assets", "img", "Image.png")
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.pulse_timer = 0
        self.color = CYAN
        
    def update(self):
        """子機の位置と状態を更新"""
        # プレイヤーの位置を記録
        self.follow_positions.append((self.player.x, self.player.y))
        if len(self.follow_positions) > self.max_follow_positions:
            self.follow_positions.pop(0)
        
        if self.orbit_mode:
            # 軌道運動モード
            self.orbit_angle += self.orbit_speed
            self.x = self.player.x + math.cos(math.radians(self.orbit_angle)) * self.orbit_distance
            self.y = self.player.y + math.sin(math.radians(self.orbit_angle)) * self.orbit_distance
        else:
            # 追従モード
            if len(self.follow_positions) > self.follow_delay:
                target_pos = self.follow_positions[-self.follow_delay]
                self.x, self.y = target_pos
            else:
                # 追従位置が不足している場合は現在位置
                self.x, self.y = self.player.x, self.player.y
        
        # 矩形の位置を更新
        self.rect.center = (int(self.x), int(self.y))
        
        # 射撃クールダウン
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        # パルスエフェクト
        self.pulse_timer += 0.2
    
    def can_shoot(self):
        """射撃可能かチェック"""
        return self.shoot_cooldown <= 0
    
    def shoot(self, target_enemies=None, level=1, boss=None):
        """子機が弾を発射（レベルに応じて弾種変更）"""
        if not self.can_shoot():
            return []
        
        from bullet import OptionBulletManager
        
        # 最も近い敵を取得
        target = None
        if boss: # ボスがいる場合はボスを優先
            target = boss
        elif target_enemies and len(target_enemies) > 0:
            target = min(target_enemies, 
                            key=lambda e: math.sqrt((e.x - self.x)**2 + (e.y - self.y)**2))
        
        # ターゲットが存在する場合のみ弾を生成
        if target:
            # レベルに応じた弾を生成
            bullets = OptionBulletManager.create_level_appropriate_bullets(
                self.x, self.y - self.size//2, level, target
            )
            
            self.shoot_cooldown = self.shoot_interval
            return bullets
        return []
    
    def set_orbit_mode(self, enabled, distance=60):
        """軌道運動モードの設定"""
        self.orbit_mode = enabled
        self.orbit_distance = distance
    
    def draw(self, screen):
        """子機を描画"""
        # パルスエフェクト
        pulse_alpha = int(50 + 30 * math.sin(self.pulse_timer))
        pulse_radius = int(self.size//2 + 5 * math.sin(self.pulse_timer * 2))
        
        # 外側のパルス
        pulse_surface = pygame.Surface((pulse_radius * 2, pulse_radius * 2), pygame.SRCALPHA)
        pulse_color = (*self.color[:3], pulse_alpha)
        pygame.draw.circle(pulse_surface, pulse_color, 
                         (pulse_radius, pulse_radius), pulse_radius)
        screen.blit(pulse_surface, (self.x - pulse_radius, self.y - pulse_radius))
        
        # 子機画像の描画
        img_rect = self.image.get_rect(center=(self.x, self.y))
        screen.blit(self.image, img_rect)
        
        # 軌道運動モードの場合、軌道線を表示
        if self.orbit_mode:
            pygame.draw.circle(screen, (100, 100, 100), 
                             (int(self.player.x), int(self.player.y)), 
                             int(self.orbit_distance), 1)

class OptionManager:
    """子機管理クラス"""
    def __init__(self, player):
        self.player = player
        self.options = []
        self.max_options = 4  # 最大子機数
        
    def update_options(self, option_count):
        """子機の数を指定された数に更新"""
        current_count = len(self.options)
        
        if option_count > current_count:
            for _ in range(option_count - current_count):
                self.add_option()
        elif option_count < current_count:
            for _ in range(current_count - option_count):
                self.remove_option()
        
        # 子機の振る舞いはプレイヤーレベルに依存させる
        self.update_option_behavior(self.player.level)
    
    def get_option_count_for_level(self, level):
        """レベルに応じた子機数を取得"""
        if level >= 8:
            return 4  # レベル8以降は最大4機
        elif level >= 6:
            return 3  # レベル6-7は3機
        elif level >= 4:
            return 2  # レベル4-5は2機
        elif level >= 2:
            return 1  # レベル2-3は1機
        else:
            return 0  # レベル1は子機なし
    
    def update_option_behavior(self, level):
        """レベルに応じて子機の動作を変更"""
        num_options = len(self.options)
        for i, option in enumerate(self.options):
            if level >= 10:
                # レベル10以降は軌道運動モード
                option.set_orbit_mode(True, 60)  # 軌道半径を60に統一
                option.orbit_angle = i * (360 / num_options) if num_options > 0 else 0
                option.color = MAGENTA
                option.shoot_interval = 15  # 射撃間隔短縮
            elif level >= 7:
                # レベル7以降は高速追従（子機ごとに遅延を変更）
                option.set_orbit_mode(False)
                option.follow_delay = 5 + i * 3  # 子機ごとに遅延を変える
                option.color = YELLOW
                option.shoot_interval = 18
            else:
                # 通常の追従モード
                option.set_orbit_mode(False)
                option.follow_delay = 10 + i * 5
                option.color = CYAN
                option.shoot_interval = 20
    
    def add_option(self):
        """子機を追加"""
        if len(self.options) < self.max_options:
            option_id = len(self.options)
            # 子機ごとに初期角度を設定して重なりを防ぐ
            offset_angle = (360 / (len(self.options) + 1)) * option_id
            new_option = Option(option_id, self.player, offset_angle=offset_angle)
            self.options.append(new_option)
    
    def remove_option(self):
        """子機を削除"""
        if self.options:
            self.options.pop()
    
    def update(self):
        """全ての子機を更新"""
        for option in self.options:
            option.update()
    
    def shoot_all(self, enemies=None, level=1, boss=None):
        """全ての子機から射撃"""
        all_bullets = []
        for option in self.options:
            bullets = option.shoot(enemies, level, boss)  # level と boss を渡す
            all_bullets.extend(bullets)
        return all_bullets
    
    def draw(self, screen):
        """全ての子機を描画"""
        for option in self.options:
            option.draw(screen)
    
    def get_option_rects(self):
        """全ての子機の矩形を取得（衝突判定用）"""
        return [option.rect for option in self.options]
    
    def reset(self):
        """子機をリセット"""
        self.options.clear()