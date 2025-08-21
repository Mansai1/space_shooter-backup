import pygame
import math
import random
from settings import *

class Bullet:
    def __init__(self, x, y, direction_y=-1, angle=0, player_bullet=None, angle_override=None, bullet_type="normal", damage=1, game=None):
        self.x = x
        self.y = y
        self.size = BULLET_SIZE
        self.speed = BULLET_SPEED
        self.direction_y = direction_y  # -1で上向き、1で下向き
        self.bullet_type = bullet_type  # "normal", "option", "homing", "boss" など
        self.game = game  # 追加: Gameインスタンス参照
        
        # angle_overrideが指定されている場合はそれを優先
        if angle_override is not None:
            self.angle = math.radians(angle_override) # 角度は度で受け取り、ラジアンに変換
        else:
            self.angle = math.radians(angle)
        
        # player_bulletが指定されていない場合はdirection_yから判定
        if player_bullet is None:
            self.player_bullet = (direction_y == -1)
        else:
            self.player_bullet = player_bullet
            
        # player_bulletがFalseの場合はdirection_yを1（下向き）に設定
        if not self.player_bullet and direction_y == -1:
            self.direction_y = 1
        
        # 弾種別による設定調整
        self._setup_bullet_properties()
        
        # 角度指定がある場合は角度を優先した移動
        if angle_override is not None:
            self.vel_x = self.speed * math.cos(self.angle)
            self.vel_y = self.speed * math.sin(self.angle)
        else:
            # 従来の角度を考慮した速度成分
            self.vel_x = self.speed * math.sin(self.angle)
            self.vel_y = self.speed * self.direction_y * math.cos(self.angle)
        
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size*2, self.size*2)
        self.active = True
        
        # ダメージ設定
        self.damage = damage
        
    def _setup_bullet_properties(self):
        """弾種別による属性設定"""
        if self.bullet_type == "option":
            self.is_option_bullet = True
            self.damage = 2  # 子機の弾は威力が高い
            self.speed = BULLET_SPEED * 1.1  # 子機の弾は少し速い
        elif self.bullet_type == "boss":
            self.is_option_bullet = False
            self.size = BOSS_BULLET_SIZE
            self.damage = BOSS_BULLET_DAMAGE
            self.speed = BULLET_SPEED * 0.8  # ボスの弾は少し遅い
        else:
            self.is_option_bullet = False
        
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.rect.center = (self.x, self.y)
        width = self.game.current_width if self.game else SCREEN_WIDTH
        height = self.game.current_height if self.game else SCREEN_HEIGHT
        if (self.y < -10 or self.y > height + 10 or 
            self.x < -10 or self.x > width + 10):
            self.active = False
    
    def draw(self, screen):
        if self.bullet_type == "option":
            # 子機の弾は特別な見た目
            pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), self.size + 1)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), self.size - 2)
        elif self.bullet_type == "boss":
            # ボスの弾は特別な見た目
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.size + 1)
            pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), max(1, self.size - 2))
        else:
            # 通常の弾
            color = YELLOW if self.player_bullet else RED
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size, 1)

class HomingBullet(Bullet):
    """追尾弾クラス"""
    def __init__(self, x, y, target=None, player_bullet=True):
        super().__init__(x, y, direction_y=-1, player_bullet=player_bullet, bullet_type="homing")
        self.target = target
        self.homing_strength = 0.1  # 追尾の強さ
        self.max_turn_rate = 5  # 最大旋回角度（度）
        self.speed = BULLET_SPEED * 0.8  # 追尾弾は少し遅い
        
    def update(self):
        if self.target and hasattr(self.target, 'x') and hasattr(self.target, 'y'):
            # ターゲットへの角度を計算
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            target_angle = math.atan2(dy, dx)
            
            # 現在の進行角度
            current_angle = math.atan2(self.vel_y, self.vel_x)
            
            # 角度差を計算
            angle_diff = target_angle - current_angle
            
            # 角度を-π～πの範囲に正規化
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            # 最大旋回角度で制限
            max_turn_rad = math.radians(self.max_turn_rate)
            if abs(angle_diff) > max_turn_rad:
                angle_diff = max_turn_rad if angle_diff > 0 else -max_turn_rad
            
            # 新しい角度を計算
            new_angle = current_angle + angle_diff * self.homing_strength
            
            # 速度ベクトルを更新
            self.vel_x = self.speed * math.cos(new_angle)
            self.vel_y = self.speed * math.sin(new_angle)
        
        # 基本の更新処理
        super().update()
    
    def draw(self, screen):
        # 追尾弾は特別な見た目
        pygame.draw.circle(screen, MAGENTA, (int(self.x), int(self.y)), self.size + 2)
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size - 1)
        
        # 追尾エフェクト
        if self.target:
            # ターゲットへの線を薄く描画
            pygame.draw.line(screen, (100, 100, 100), 
                           (int(self.x), int(self.y)), 
                           (int(self.target.x), int(self.target.y)), 1)

class Laser:
    def __init__(self, x, y, direction_y=-1, damage=LASER_DAMAGE):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.width = LASER_WIDTH
        self.length = LASER_LENGTH
        self.speed = LASER_SPEED
        self.direction_y = direction_y
        self.damage = damage
        self.active = True
        self.player_bullet = True
        self.penetrating = True  # 貫通属性
        self.hits = 0  # ヒット回数
        self.max_hits = 5  # 最大ヒット回数
        self.hit_boss = False  # ボスに当たったかどうか
        # レーザーの矩形を作成
        if direction_y == -1:  # 上向き
            self.rect = pygame.Rect(x - self.width//2, y - self.length, self.width, self.length)
        else:  # 下向き
            self.rect = pygame.Rect(x - self.width//2, y, self.width, self.length)

    def update(self):
        self.y += self.speed * self.direction_y
        # レーザーの矩形を更新
        if self.direction_y == -1:  # 上向き
            self.rect = pygame.Rect(self.x - self.width//2, self.y - self.length, self.width, self.length)
        else:  # 下向き
            self.rect = pygame.Rect(self.x - self.width//2, self.y, self.width, self.length)
        # 画面外に出たら非アクティブに
        height = SCREEN_HEIGHT  # Laserクラスにはgameパラメータがないため、固定値を使用
        if (self.y < -self.length or self.y > height + self.length):
            self.active = False
        # 最大ヒット数に達したら非アクティブに
        if self.hits >= self.max_hits or self.hit_boss:
            self.active = False

    def draw(self, screen):
        if self.direction_y == -1:  # 上向き
            start_pos = (self.x, self.y)
            end_pos = (self.x, self.y - self.length)
        else:  # 下向き
            start_pos = (self.x, self.y)
            end_pos = (self.x, self.y + self.length)
        # --- ビームらしいグラデーションと発光 ---
        for i in range(6):
            width = self.width + i * 6
            alpha = max(30, 180 - i * 30)
            color = (100 + i*25, 255, 255, alpha)  # 外側ほど薄いシアン
            surf = pygame.Surface((width, abs(end_pos[1] - start_pos[1])), pygame.SRCALPHA)
            pygame.draw.rect(surf, color, (0, 0, width, abs(end_pos[1] - start_pos[1])))
            if self.direction_y == -1:
                screen.blit(surf, (self.x - width//2, end_pos[1]))
            else:
                screen.blit(surf, (self.x - width//2, start_pos[1]))
        # 中心の明るい線
        pygame.draw.line(screen, (255,255,255), start_pos, end_pos, 4)
        pygame.draw.line(screen, (200,255,255), start_pos, end_pos, 2)

    def hit_enemy(self):
        self.hits += 1
    def hit_boss_once(self):
        self.hit_boss = True

class Bomb:
    def __init__(self, x, y, direction_y=-1):
        self.x = x
        self.y = y
        self.size = BOMB_SIZE
        self.speed = BOMB_SPEED
        self.direction_y = direction_y
        self.active = True
        self.player_bullet = True
        self.exploded = False
        self.explosion_timer = 0
        self.explosion_radius = 0
        self.max_explosion_radius = BOMB_EXPLOSION_RADIUS
        self.explosion_duration = BOMB_EXPLOSION_DURATION
        
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
    
    def update(self):
        if not self.exploded:
            # 爆弾の移動
            self.y += self.speed * self.direction_y
            self.rect.center = (self.x, self.y)
            
            # 画面外に出たら爆発
            height = SCREEN_HEIGHT  # Bombクラスにはgameパラメータがないため、固定値を使用
            if (self.y < -10 or self.y > height + 10):
                self.explode()
        else:
            # 爆発エフェクトの更新
            self.explosion_timer += 1
            self.explosion_radius = (self.explosion_timer / self.explosion_duration) * self.max_explosion_radius
            
            if self.explosion_timer >= self.explosion_duration:
                self.active = False
    
    def explode(self):
        """爆弾を爆発させる"""
        if not self.exploded:
            self.exploded = True
            self.explosion_timer = 0
            # 爆発範囲の矩形を作成
            self.rect = pygame.Rect(
                self.x - self.max_explosion_radius,
                self.y - self.max_explosion_radius,
                self.max_explosion_radius * 2,
                self.max_explosion_radius * 2
            )
    
    def draw(self, screen):
        if not self.exploded:
            # 爆弾本体を描画
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size - 2)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size, 2)
            
            # 点滅エフェクト
            if pygame.time.get_ticks() % 200 < 100:
                pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size // 2)
        else:
            # 爆発エフェクトを描画
            if self.explosion_radius > 0:
                # 外側の爆発
                pygame.draw.circle(screen, ORANGE, 
                                 (int(self.x), int(self.y)), 
                                 int(self.explosion_radius), 3)
                
                # 内側の爆発
                inner_radius = int(self.explosion_radius * 0.7)
                if inner_radius > 0:
                    pygame.draw.circle(screen, YELLOW, 
                                     (int(self.x), int(self.y)), 
                                     inner_radius, 2)
                
                # 中心の爆発
                center_radius = int(self.explosion_radius * 0.4)
                if center_radius > 0:
                    pygame.draw.circle(screen, WHITE, 
                                     (int(self.x), int(self.y)), 
                                     center_radius)
    
    def get_explosion_rect(self):
        """爆発範囲の矩形を取得"""
        if self.exploded and self.explosion_radius > 0:
            return pygame.Rect(
                self.x - self.explosion_radius,
                self.y - self.explosion_radius,
                self.explosion_radius * 2,
                self.explosion_radius * 2
            )
        return None

class SpreadBullet:
    """拡散弾クラス - 複数の弾を一度に生成"""
    @staticmethod
    def create_spread(x, y, num_bullets=3, spread_angle=30, bullet_type="normal", game=None):
        """拡散弾を生成"""
        bullets = []
        center_angle = 0  # 中央は真上
        
        if num_bullets == 1:
            bullets.append(Bullet(x, y, direction_y=-1, bullet_type=bullet_type, game=game))
        else:
            for i in range(num_bullets):
                # 角度を計算（中央から左右に分散）
                if num_bullets % 2 == 1:
                    # 奇数の場合、中央に1発
                    angle_offset = (i - num_bullets // 2) * (spread_angle / (num_bullets - 1))
                else:
                    # 偶数の場合、中央をずらして配置
                    angle_offset = (i - num_bullets / 2 + 0.5) * (spread_angle / num_bullets)
                
                angle = center_angle + angle_offset
                bullets.append(Bullet(x, y, angle_override=angle - 90, bullet_type=bullet_type, game=game))  # -90で上向きに調整
        
        return bullets

class WideShotBullet:
    """ワイドショットの弾を生成するクラス"""
    @staticmethod
    def create_bullets(x, y, damage):
        bullets = []
        # 中央の弾
        bullets.append(Bullet(x, y - PLAYER_SIZE//2, direction_y=-1, damage=damage))
        # 左の弾
        bullets.append(Bullet(x - 10, y - PLAYER_SIZE//2, direction_y=-1, angle=-15, damage=damage))
        # 右の弾
        bullets.append(Bullet(x + 10, y - PLAYER_SIZE//2, direction_y=-1, angle=15, damage=damage))
        return bullets

class OptionBulletManager:
    """子機専用の弾管理クラス"""
    
    @staticmethod
    def create_level_appropriate_bullets(x, y, level, target_enemy=None, game=None):
        """レベルに応じた子機の弾を生成"""
        bullets = []
        
        if level >= 12:
            # レベル12以降：追尾弾
            if target_enemy:
                bullets.append(HomingBullet(x, y, target=target_enemy, game=game))
            else:
                bullets.append(Bullet(x, y, bullet_type="option", game=game))
        elif level >= 8:
            # レベル8-11：3方向拡散弾
            bullets = SpreadBullet.create_spread(x, y, num_bullets=3, spread_angle=20, bullet_type="option", game=game)
        elif level >= 5:
            # レベル5-7：強化弾（ダメージ3）
            bullet = Bullet(x, y, bullet_type="option", damage=3, game=game)
            bullets.append(bullet)
        else:
            # レベル2-4：通常の子機弾
            bullets.append(Bullet(x, y, bullet_type="option", game=game))
        
        return bullets
    
    @staticmethod
    def create_orbital_pattern(center_x, center_y, num_bullets=8, radius=60, rotation_angle=0):
        """軌道運動時の全方位弾幕パターン"""
        bullets = []
        angle_step = 360 / num_bullets
        
        for i in range(num_bullets):
            angle = i * angle_step + rotation_angle
            start_x = center_x + math.cos(math.radians(angle)) * 20
            start_y = center_y + math.sin(math.radians(angle)) * 20
            
            bullets.append(Bullet(start_x, start_y, angle_override=angle, bullet_type="option"))
        
        return bullets

class MasterSpark:
    def __init__(self, player, boss=None):
        self.player = player
        self.boss = boss # ボスオブジェクトを保持
        self.x = player.x  # プレイヤーのX座標を初期位置とする
        self.y = player.y  # プレイヤーのY座標を初期位置とする
        self.duration = MASTER_SPARK_DURATION
        self.width = MASTER_SPARK_WIDTH
        self.active = True
        # プレイヤーのY座標から画面上部までをカバーする矩形
        self.rect = pygame.Rect(self.x - self.width // 2, 0, self.width, self.y)
        self.pulse_timer = 0
        self.spark_particles = []

        # ボスがいる場合、現在のスペルカードの体力の30%を削るようにダメージを計算
        if self.boss and hasattr(self.boss, 'current_spell_max_health'):
            total_damage_to_deal = self.boss.current_spell_max_health * MASTER_SPARK_BOSS_DAMAGE_PERCENTAGE
            self.damage = total_damage_to_deal / self.duration
        else:
            self.damage = MASTER_SPARK_DAMAGE # 通常の敵へのダメージ

    def update(self):
        self.duration -= 1
        if self.duration <= 0:
            self.active = False

        # プレイヤーのX座標に合わせて必殺技を移動
        self.x = self.player.x
        self.rect.x = self.x - self.width // 2
        # プレイヤーのY座標に合わせて必殺技の高さを調整
        self.y = self.player.y
        self.rect.height = self.y
        self.rect.y = 0

        self.pulse_timer += 0.1 # 脈動タイマーを更新

        # パーティクル生成
        if random.random() < 0.3: # 発生頻度
            particle_x = random.randint(int(self.x - self.width / 2), int(self.x + self.width / 2))
            particle_y = random.randint(0, int(self.y))
            self.spark_particles.append({'x': particle_x, 'y': particle_y, 'life': 30, 'vx': random.uniform(-1, 1), 'vy': random.uniform(-1, 1)})

        # パーティクル更新
        for p in self.spark_particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.spark_particles.remove(p)

    def draw(self, screen):
        # 発射口の楕円部分の高さ
        ellipse_base_height = 30 # 楕円の縦のサイズ
        overlap_height = 10 # 楕円と四角の重なり部分の高さ

        # レーザーの本体
        # 複数の半透明な矩形と楕円を重ねて描画し、グラデーションを表現
        for i in range(5):
            current_width = self.width - i * (self.width // 5)
            alpha = 200 - i * 40  # 外側ほど透明に
            color = (255, 255, 100, alpha)  # 黄色っぽい色

            # 四角形部分
            # 矩形は画面上部から楕円の開始位置まで、少し重なるように
            rect_part = pygame.Rect(self.x - current_width // 2, 0, current_width, self.y - ellipse_base_height + overlap_height)
            if rect_part.height > 0:
                overlay_rect = pygame.Surface(rect_part.size, pygame.SRCALPHA)
                overlay_rect.fill(color)
                screen.blit(overlay_rect, rect_part.topleft)

            # 楕円部分
            # 楕円はplayer.yを底辺として、ellipse_base_heightの高さを持つ
            # 楕円の描画範囲を少し広げて、四角形部分と重なるようにする
            ellipse_draw_rect = pygame.Rect(self.x - current_width // 2, self.y - ellipse_base_height, current_width, ellipse_base_height + overlap_height)
            overlay_ellipse = pygame.Surface(ellipse_draw_rect.size, pygame.SRCALPHA)
            pygame.draw.ellipse(overlay_ellipse, color, overlay_ellipse.get_rect())
            screen.blit(overlay_ellipse, ellipse_draw_rect.topleft)

        # 最も内側の明るい部分（脈動）
        pulse_factor = (math.sin(self.pulse_timer) + 1) / 2 # 0から1の間で脈動
        inner_width = self.width // 3 + (self.width // 6 * pulse_factor)

        # 内側の四角形部分
        inner_rect_part = pygame.Rect(self.x - inner_width // 2, 0, inner_width, self.y - ellipse_base_height + overlap_height)
        if inner_rect_part.height > 0:
            inner_overlay_rect = pygame.Surface(inner_rect_part.size, pygame.SRCALPHA)
            inner_overlay_rect.fill((255, 255, 200, 255))  # より明るい黄色
            screen.blit(inner_overlay_rect, inner_rect_part.topleft)

        # 内側の楕円部分
        inner_ellipse_draw_rect = pygame.Rect(self.x - inner_width // 2, self.y - ellipse_base_height, inner_width, ellipse_base_height + overlap_height)
        inner_overlay_ellipse = pygame.Surface(inner_ellipse_draw_rect.size, pygame.SRCALPHA)
        pygame.draw.ellipse(inner_overlay_ellipse, (255, 255, 200, 255), inner_overlay_ellipse.get_rect())  # より明るい黄色
        screen.blit(inner_overlay_ellipse, inner_ellipse_draw_rect.topleft)

        # 中心線
        pygame.draw.line(screen, WHITE, (self.x, 0), (self.x, self.y), 4)

        # パーティクルの描画
        for p in self.spark_particles:
            particle_alpha = int(255 * (p['life'] / 30))
            particle_color = (255, 255, 255, particle_alpha)
            pygame.draw.circle(screen, particle_color, (int(p['x']), int(p['y'])), 2)
    
    def is_point_in_range(self, x, y):
        """指定された座標がMasterSparkの範囲内にあるかチェック"""
        try:
            # プレイヤーのX座標を中心とした範囲内かチェック
            half_width = self.width // 2
            left_edge = self.x - half_width
            right_edge = self.x + half_width
            
            # X座標が範囲内で、Y座標が画面上部からプレイヤー位置まで
            return (left_edge <= x <= right_edge and 0 <= y <= self.y)
        except Exception as e:
            print(f"MasterSpark範囲チェックエラー: {e}")
            return False
    
    def get_range_rect(self):
        """MasterSparkの範囲を表す矩形を取得"""
        try:
            return pygame.Rect(self.x - self.width // 2, 0, self.width, self.y)
        except Exception as e:
            print(f"MasterSpark範囲矩形取得エラー: {e}")
            return None