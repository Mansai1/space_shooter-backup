import pygame
import math
import random
from settings import *

class BossBullet:
    """ボス専用弾丸クラス - 複雑な動作パターンを持つ"""
    
    def __init__(self, x, y, vx, vy, bullet_type="normal", color=WHITE, size=8, damage=1):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.bullet_type = bullet_type
        self.color = color
        self.size = size
        self.damage = damage
        
        # 弾丸の状態
        self.active = True
        self.age = 0
        self.max_age = 600  # 10秒で自動消滅
        
        # 特殊効果用パラメータ
        self.angle = math.atan2(vy, vx)
        self.speed = math.sqrt(vx*vx + vy*vy)
        self.original_speed = self.speed
        self.rotation = 0
        self.scale = 1.0
        self.alpha = 255
        
        # タイプ別の特殊パラメータ
        self.init_bullet_type()
        
        # 当たり判定
        self.rect = pygame.Rect(x - size//2, y - size//2, size, size)
    
    def init_bullet_type(self):
        """弾丸タイプ別の初期化"""
        if self.bullet_type == "homing":
            # 誘導弾
            self.homing_strength = 0.02
            self.target_x = SCREEN_WIDTH // 2
            self.target_y = SCREEN_HEIGHT - 100
            
        elif self.bullet_type == "accelerating":
            # 加速弾
            self.acceleration = 0.05
            self.max_speed = self.speed * 3
            
        elif self.bullet_type == "decelerating":
            # 減速弾
            self.deceleration = 0.98
            self.min_speed = 0.5
            
        elif self.bullet_type == "spiral":
            # 螺旋弾
            self.spiral_radius = 20
            self.spiral_speed = 0.1
            self.center_vx = self.vx
            self.center_vy = self.vy
            
        elif self.bullet_type == "sine_wave":
            # サイン波弾
            self.wave_amplitude = 30
            self.wave_frequency = 0.05
            self.perpendicular_angle = self.angle + math.pi / 2
            
        elif self.bullet_type == "bouncing":
            # 跳ね返り弾
            self.bounce_count = 3
            self.bounce_decay = 0.8
            
        elif self.bullet_type == "splitting":
            # 分裂弾
            self.split_timer = 60
            self.has_split = False
            
        elif self.bullet_type == "laser":
            # レーザー弾（長い弾丸）
            self.length = 40
            self.width = 4
            
        elif self.bullet_type == "explosive":
            # 爆発弾
            self.explosion_timer = 120
            self.explosion_radius = 30
            
    def update(self, player_x=None, player_y=None):
        """弾丸の更新処理"""
        if not self.active:
            return []
        
        self.age += 1
        
        # 寿命チェック
        if self.age > self.max_age:
            self.active = False
            return []
        
        # タイプ別の更新処理
        new_bullets = []
        
        if self.bullet_type == "normal":
            self.update_normal()
            
        elif self.bullet_type == "homing":
            new_bullets = self.update_homing(player_x, player_y)
            
        elif self.bullet_type == "accelerating":
            self.update_accelerating()
            
        elif self.bullet_type == "decelerating":
            self.update_decelerating()
            
        elif self.bullet_type == "spiral":
            self.update_spiral()
            
        elif self.bullet_type == "sine_wave":
            self.update_sine_wave()
            
        elif self.bullet_type == "bouncing":
            self.update_bouncing()
            
        elif self.bullet_type == "splitting":
            new_bullets = self.update_splitting()
            
        elif self.bullet_type == "laser":
            self.update_laser()
            
        elif self.bullet_type == "explosive":
            new_bullets = self.update_explosive()
        
        # 画面外チェック
        margin = 50
        if (self.x < -margin or self.x > SCREEN_WIDTH + margin or
            self.y < -margin or self.y > SCREEN_HEIGHT + margin):
            if self.bullet_type != "bouncing":
                self.active = False
        
        # 当たり判定の更新
        self.update_rect()
        
        return new_bullets
    
    def update_normal(self):
        """通常弾の更新"""
        self.x += self.vx
        self.y += self.vy
    
    def update_homing(self, player_x, player_y):
        """誘導弾の更新"""
        if player_x is not None and player_y is not None:
            # プレイヤーへの方向を計算
            dx = player_x - self.x
            dy = player_y - self.y
            target_angle = math.atan2(dy, dx)
            
            # 現在の角度から目標角度への補正
            angle_diff = target_angle - self.angle
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            # 徐々に方向転換
            self.angle += angle_diff * self.homing_strength
            
            # 速度ベクトルを更新
            self.vx = math.cos(self.angle) * self.speed
            self.vy = math.sin(self.angle) * self.speed
        
        self.x += self.vx
        self.y += self.vy
        
        return []
    
    def update_accelerating(self):
        """加速弾の更新"""
        if self.speed < self.max_speed:
            self.speed += self.acceleration
            self.vx = math.cos(self.angle) * self.speed
            self.vy = math.sin(self.angle) * self.speed
        
        self.x += self.vx
        self.y += self.vy
    
    def update_decelerating(self):
        """減速弾の更新"""
        self.speed *= self.deceleration
        if self.speed < self.min_speed:
            self.speed = self.min_speed
        
        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed
        
        self.x += self.vx
        self.y += self.vy
    
    def update_spiral(self):
        """螺旋弾の更新"""
        # 中心の移動
        center_x = self.x + self.center_vx
        center_y = self.y + self.center_vy
        
        # 螺旋運動
        spiral_angle = self.age * self.spiral_speed
        offset_x = math.cos(spiral_angle) * self.spiral_radius
        offset_y = math.sin(spiral_angle) * self.spiral_radius
        
        self.x = center_x + offset_x
        self.y = center_y + offset_y
        
        # 中心座標を更新（実際には使わないが、一貫性のため）
        self.x += self.center_vx * 0.1
        self.y += self.center_vy * 0.1
    
    def update_sine_wave(self):
        """サイン波弾の更新"""
        # 基本的な前進
        self.x += self.vx
        self.y += self.vy
        
        # サイン波による横移動
        wave_offset = math.sin(self.age * self.wave_frequency) * self.wave_amplitude
        offset_x = math.cos(self.perpendicular_angle) * wave_offset * 0.1
        offset_y = math.sin(self.perpendicular_angle) * wave_offset * 0.1
        
        self.x += offset_x
        self.y += offset_y
    
    def update_bouncing(self):
        """跳ね返り弾の更新"""
        next_x = self.x + self.vx
        next_y = self.y + self.vy
        
        # 壁との衝突判定
        bounced = False
        
        if next_x <= 0 or next_x >= SCREEN_WIDTH:
            self.vx = -self.vx * self.bounce_decay
            self.bounce_count -= 1
            bounced = True
        
        if next_y <= 0 or next_y >= SCREEN_HEIGHT:
            self.vy = -self.vy * self.bounce_decay
            self.bounce_count -= 1
            bounced = True
        
        if bounced and self.bounce_count <= 0:
            self.active = False
            return
        
        self.x += self.vx
        self.y += self.vy
    
    def update_splitting(self):
        """分裂弾の更新"""
        self.x += self.vx
        self.y += self.vy
        
        self.split_timer -= 1
        
        # 分裂処理
        if self.split_timer <= 0 and not self.has_split:
            self.has_split = True
            self.active = False
            
            # 3つに分裂
            new_bullets = []
            for i in range(3):
                angle_offset = (i - 1) * 0.5  # -0.5, 0, 0.5 radians
                new_angle = self.angle + angle_offset
                new_vx = math.cos(new_angle) * self.speed * 0.7
                new_vy = math.sin(new_angle) * self.speed * 0.7
                
                new_bullet = BossBullet(
                    self.x, self.y, new_vx, new_vy,
                    bullet_type="normal",
                    color=self.color,
                    size=self.size - 2
                )
                new_bullets.append(new_bullet)
            
            return new_bullets
        
        return []
    
    def update_laser(self):
        """レーザー弾の更新"""
        self.x += self.vx
        self.y += self.vy
        self.rotation += 0.1  # 回転エフェクト
    
    def update_explosive(self):
        """爆発弾の更新"""
        self.x += self.vx
        self.y += self.vy
        
        self.explosion_timer -= 1
        
        # 爆発処理
        if self.explosion_timer <= 0:
            self.active = False
            
            # 爆発で放射状に弾を生成
            new_bullets = []
            for i in range(8):
                angle = i * 45 * math.pi / 180
                speed = 2.0
                new_vx = math.cos(angle) * speed
                new_vy = math.sin(angle) * speed
                
                new_bullet = BossBullet(
                    self.x, self.y, new_vx, new_vy,
                    bullet_type="normal",
                    color=ORANGE,
                    size=6
                )
                new_bullets.append(new_bullet)
            
            return new_bullets
        
        # 爆発前の点滅効果
        if self.explosion_timer < 30:
            self.alpha = 128 + int(127 * math.sin(self.age * 0.5))
        
        return []
    
    def update_rect(self):
        """当たり判定矩形の更新"""
        if self.bullet_type == "laser":
            # レーザーは長方形の当たり判定
            self.rect = pygame.Rect(
                self.x - self.length//2,
                self.y - self.width//2,
                self.length,
                self.width
            )
        else:
            # 通常は円形（正方形で近似）
            self.rect = pygame.Rect(
                self.x - self.size//2,
                self.y - self.size//2,
                self.size,
                self.size
            )
    
    def draw(self, screen):
        """弾丸の描画"""
        if not self.active:
            return
        
        if self.bullet_type == "laser":
            self.draw_laser(screen)
        elif self.bullet_type == "explosive":
            self.draw_explosive(screen)
        else:
            self.draw_normal(screen)
    
    def draw_normal(self, screen):
        """通常弾丸の描画"""
        # アルファ値を考慮した色
        if self.alpha < 255:
            # 半透明描画は複雑なので、単純化
            color = self.color
        else:
            color = self.color
        
        # 弾丸の形状（タイプ別）
        if self.bullet_type == "homing":
            # 誘導弾：三角形
            points = []
            for i in range(3):
                angle = self.angle + i * 120 * math.pi / 180
                px = self.x + math.cos(angle) * self.size
                py = self.y + math.sin(angle) * self.size
                points.append((int(px), int(py)))
            pygame.draw.polygon(screen, color, points)
            
        elif self.bullet_type == "spiral":
            # 螺旋弾：回転する四角形
            points = []
            for i in range(4):
                angle = self.rotation + i * 90 * math.pi / 180
                px = self.x + math.cos(angle) * self.size
                py = self.y + math.sin(angle) * self.size
                points.append((int(px), int(py)))
            pygame.draw.polygon(screen, color, points)
            
        elif self.bullet_type == "splitting":
            # 分裂弾：点滅する円
            if self.split_timer < 30 and self.split_timer % 6 < 3:
                color = RED
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size, 2)
            
        else:
            # 通常弾：円形
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
            
            # 光沢効果
            highlight_size = max(2, self.size - 3)
            highlight_color = tuple(min(255, c + 50) for c in color[:3])
            pygame.draw.circle(screen, highlight_color, 
                             (int(self.x - self.size//3), int(self.y - self.size//3)), 
                             highlight_size//2)
    
    def draw_laser(self, screen):
        """レーザー弾の描画"""
        # レーザーの向きを計算
        end_x = self.x + math.cos(self.angle) * self.length
        end_y = self.y + math.sin(self.angle) * self.length
        
        # レーザー本体
        pygame.draw.line(screen, self.color, 
                        (int(self.x), int(self.y)), 
                        (int(end_x), int(end_y)), 
                        self.width)
        
        # 中心線
        center_color = tuple(min(255, c + 100) for c in self.color[:3])
        pygame.draw.line(screen, center_color,
                        (int(self.x), int(self.y)), 
                        (int(end_x), int(end_y)), 
                        max(1, self.width//2))
    
    def draw_explosive(self, screen):
        """爆発弾の描画"""
        # 基本的な円
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        
        # 爆発前の警告エフェクト
        if self.explosion_timer < 60:
            warning_radius = self.explosion_radius + int(10 * math.sin(self.age * 0.3))
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), warning_radius, 2)
        
        # 中心の光
        core_color = tuple(min(255, c + 100) for c in self.color[:3])
        pygame.draw.circle(screen, core_color, (int(self.x), int(self.y)), self.size//2)


class BossBulletManager:
    """ボス弾丸管理クラス"""
    
    def __init__(self):
        self.bullets = []
        self.max_bullets = 500  # 最大弾丸数
    
    def add_bullet(self, bullet):
        """弾丸を追加"""
        if len(self.bullets) < self.max_bullets:
            self.bullets.append(bullet)
    
    def add_bullets(self, bullets):
        """複数の弾丸を追加"""
        for bullet in bullets:
            self.add_bullet(bullet)
    
    def update(self, player_x=None, player_y=None):
        """全弾丸の更新"""
        new_bullets = []
        active_bullets = []
        
        for bullet in self.bullets:
            if bullet.active:
                # 弾丸の更新処理
                generated_bullets = bullet.update(player_x, player_y)
                new_bullets.extend(generated_bullets)
                active_bullets.append(bullet)
        
        self.bullets = active_bullets
        self.add_bullets(new_bullets)
    
    def draw(self, screen):
        """全弾丸の描画"""
        for bullet in self.bullets:
            bullet.draw(screen)
    
    def get_bullets(self):
        """アクティブな弾丸リストを取得"""
        return [bullet for bullet in self.bullets if bullet.active]
    
    def clear(self):
        """全弾丸をクリア"""
        self.bullets.clear()
    
    def get_bullet_count(self):
        """現在の弾丸数を取得"""
        return len(self.bullets)


# 弾幕パターン生成用のヘルパー関数
class BulletPatterns:
    """弾幕パターン生成クラス"""
    
    @staticmethod
    def create_circle_pattern(center_x, center_y, bullet_count, speed, color=WHITE, bullet_type="normal"):
        """円形弾幕パターン"""
        bullets = []
        for i in range(bullet_count):
            angle = i * (360 / bullet_count) * math.pi / 180
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            bullet = BossBullet(center_x, center_y, vx, vy, bullet_type, color)
            bullets.append(bullet)
        return bullets
    
    @staticmethod
    def create_spiral_pattern(center_x, center_y, bullet_count, speed, spiral_factor, color=WHITE):
        """螺旋弾幕パターン"""
        bullets = []
        for i in range(bullet_count):
            angle = i * spiral_factor * math.pi / 180
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            bullet = BossBullet(center_x, center_y, vx, vy, "normal", color)
            bullets.append(bullet)
        return bullets
    
    @staticmethod
    def create_aimed_pattern(center_x, center_y, target_x, target_y, bullet_count, speed, spread, color=WHITE):
        """プレイヤー狙い弾幕パターン"""
        bullets = []
        base_angle = math.atan2(target_y - center_y, target_x - center_x)
        
        for i in range(bullet_count):
            angle_offset = (i - bullet_count//2) * spread
            angle = base_angle + angle_offset
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            bullet = BossBullet(center_x, center_y, vx, vy, "normal", color)
            bullets.append(bullet)
        return bullets
    
    @staticmethod
    def create_random_pattern(center_x, center_y, bullet_count, min_speed, max_speed, color=WHITE):
        """ランダム弾幕パターン"""
        bullets = []
        for i in range(bullet_count):
            angle = random.random() * 2 * math.pi
            speed = random.uniform(min_speed, max_speed)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            bullet = BossBullet(center_x, center_y, vx, vy, "normal", color)
            bullets.append(bullet)
        return bullets