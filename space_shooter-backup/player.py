import pygame
import math
import os
from settings import *
from option import OptionManager
from bullet import Bullet, Laser, Bomb # Bullet, Laser, Bombを直接インポート

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, upgrade_data=None):
        super().__init__()
        self.x = x
        self.y = y
        self.level = 1
        self.size = PLAYER_SIZE
        self.upgrade_data = upgrade_data if upgrade_data else self.load_default_upgrades()

        self.current_weapon = self.upgrade_data.get('current_weapon', 'normal') # 現在の武器

        # レベルアップで獲得する機能のフラグ
        self.has_triple_shot = False
        self.has_rapid_fire = False
        self.has_shield = False
        self.has_speed_boost = False
        self.has_laser = False
        self.has_bomb = False

        self.apply_upgrades()

        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        image_path = os.path.join(os.path.dirname(__file__), "assets", "img", "Image.png")
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        
        self.powerups = {}
        self.shield_active = False
        self.shield_hits = 0
        self.max_shield_hits = 5
        
        self.shoot_cooldown = 0
        self.fire_rate_multiplier = 1.0

        self.special_gauge = 0
        self.special_stock = 0
        self.invincible = False
        self.invincible_timer = 0
        
        self.option_manager = OptionManager(self)
        self.on_level_up(1) # 初期の子機を設定

    def load_default_upgrades(self):
        return {"points": 0, "attack_level": 1, "fire_rate_level": 1, "speed_level": 1, "option_level": 0, "unlocked_weapons": ["normal"], "current_weapon": "normal"}

    def apply_upgrades(self):
        # 基本攻撃力はアップグレードレベルと武器のダメージ倍率で決定
        base_attack = 1 + (self.upgrade_data.get('attack_level', 1) - 1) * 0.2
        weapon_damage_multiplier = WEAPON_STATS.get(self.current_weapon, {}).get('damage_multiplier', 1.0)
        self.attack_power = base_attack * weapon_damage_multiplier

        self.speed = PLAYER_SPEED + (self.upgrade_data.get('speed_level', 1) - 1) * 0.5
        self.base_speed = self.speed
        
        fire_rate_level = self.upgrade_data.get('fire_rate_level', 1)
        base_cooldown = 15 - (fire_rate_level - 1) # 連射アップグレードによる基本クールダウン短縮
        weapon_cooldown_multiplier = WEAPON_STATS.get(self.current_weapon, {}).get('cooldown_multiplier', 1.0)
        
        self.normal_cooldown = max(5, int(base_cooldown * weapon_cooldown_multiplier))
        self.rapid_fire_cooldown = max(2, int((base_cooldown / 3) * weapon_cooldown_multiplier)) # rapid_fireはnormalの1/3程度
        self.laser_cooldown = max(10, int(30 * weapon_cooldown_multiplier))
        self.bomb_cooldown = max(30, int(60 * weapon_cooldown_multiplier))

        self.option_count = self.upgrade_data.get('option_level', 0)

    def apply_runtime_upgrade(self, upgrade_option):
        """レベルアップ画面で選択されたアップグレードを適用"""
        upgrade_option.apply(self)

    def on_level_up(self, new_level):
        self.level = new_level # プレイヤーの現在のレベルを更新
        self.option_manager.update_options(self.option_count) # 子機はアップグレードレベルで管理

        # レベルに応じて機能を追加
        if new_level >= 2: self.has_triple_shot = True
        if new_level >= 4: self.has_rapid_fire = True
        if new_level >= 6:
            self.has_shield = True
            self.shield_active = True
        if new_level >= 8: self.has_speed_boost = True
        if new_level >= 10: self.has_laser = True
        if new_level >= 12: self.has_bomb = True
        
    def update(self):
        keys = pygame.key.get_pressed()
        
        current_speed = self.speed
        if self.has_speed_boost: # レベルアップによるスピードブースト
            current_speed *= 1.5

        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.x -= current_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.x += current_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: self.y -= current_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.y += current_speed
            
        self.x = max(self.size//2, min(SCREEN_WIDTH - self.size//2, self.x))
        self.y = max(self.size//2, min(SCREEN_HEIGHT - self.size//2, self.y))
        
        self.rect.center = (self.x, self.y)
        
        # パワーアップの時間管理（life_upは永続なので不要）
        # self.update_powerups()
        
        if self.shoot_cooldown > 0: self.shoot_cooldown -= 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0: self.invincible = False

        if self.special_stock < SPECIAL_STOCK_MAX:
            self.special_gauge += 1
            if self.special_gauge >= SPECIAL_GAUGE_MAX:
                self.special_gauge = 0
                self.special_stock += 1
            
        self.option_manager.update()
    
    def add_option(self):
        """オプションを追加する"""
        self.option_count += 1
        self.option_manager.update_options(self.option_count)

    def add_powerup(self, power_type):
        """パワーアップを追加"""
        if power_type == "life_up":
            return True # main.pyでライフを増やす
        return False # その他のパワーアップはここでは処理しない
    
    def can_shoot(self):
        return self.shoot_cooldown <= 0
    
    def shoot(self, enemies=None, boss=None):
        all_bullets = []
        player_bullets = self.shoot_player()
        all_bullets.extend(player_bullets)
        if boss:
            option_bullets = self.option_manager.shoot_all(enemies, self.level, boss)
            all_bullets.extend(option_bullets)
        elif enemies:
            option_bullets = self.option_manager.shoot_all(enemies, self.level)
            all_bullets.extend(option_bullets)
        return all_bullets
    
    def shoot_player(self):
        if not self.can_shoot(): return []
        bullets = []

        # レベルアップで獲得した機能による弾の発射
        if self.has_laser:
            bullets.append(Laser(self.x, self.y - self.size//2, direction_y=-1, damage=self.attack_power * 2))
            self.shoot_cooldown = self.laser_cooldown
        elif self.has_bomb:
            bullets.append(Bomb(self.x, self.y - self.size//2, direction_y=-1))
            self.shoot_cooldown = self.bomb_cooldown
        elif self.has_triple_shot:
            bullets.append(Bullet(self.x, self.y - self.size//2, direction_y=-1, damage=self.attack_power))
            bullets.append(Bullet(self.x - 10, self.y - self.size//2, direction_y=-1, angle=-15, damage=self.attack_power))
            bullets.append(Bullet(self.x + 10, self.y - self.size//2, direction_y=-1, angle=15, damage=self.attack_power))
            self.shoot_cooldown = self.normal_cooldown
        else:
            # 現在選択されている武器に応じて弾を発射
            if self.current_weapon == "normal":
                bullets.append(Bullet(self.x, self.y - self.size//2, direction_y=-1, damage=self.attack_power))
                self.shoot_cooldown = self.normal_cooldown
            elif self.current_weapon == "wide_shot":
                bullets.append(Bullet(self.x, self.y - self.size//2, direction_y=-1, damage=self.attack_power))
                bullets.append(Bullet(self.x - 10, self.y - self.size//2, direction_y=-1, angle=-15, damage=self.attack_power))
                bullets.append(Bullet(self.x + 10, self.y - self.size//2, direction_y=-1, angle=15, damage=self.attack_power))
                self.shoot_cooldown = self.normal_cooldown
            elif self.current_weapon == "laser_weapon":
                bullets.append(Laser(self.x, self.y - self.size//2, direction_y=-1, damage=self.attack_power * 2))
                self.shoot_cooldown = self.laser_cooldown
        
        # 連射パワーアップはクールダウンのみ短縮
        if self.has_rapid_fire:
            self.shoot_cooldown = self.rapid_fire_cooldown

        self.shoot_cooldown *= self.fire_rate_multiplier

        return bullets

    def shoot_special(self, boss=None):
        if self.special_stock > 0:
            from bullet import MasterSpark
            self.special_stock -= 1
            self.invincible = True
            self.invincible_timer = 300
            return MasterSpark(self, boss)
        return None
    
    def check_bomb_collision(self, bomb, enemies):
        if hasattr(bomb, 'exploded') and bomb.exploded: return False
        for enemy in enemies:
            if hasattr(bomb, 'rect') and hasattr(enemy, 'rect'):
                if bomb.rect.colliderect(enemy.rect):
                    if hasattr(bomb, 'explode'):
                        bomb.explode()
                        bomb.explosion_radius = BOMB_EXPLOSION_RADIUS
                    return True
        return False
    
    def take_damage(self):
        if self.invincible:
            return False

        if self.shield_active:
            self.shield_hits += 1
            if self.shield_hits >= self.max_shield_hits:
                self.shield_active = False
                self.shield_hits = 0
            self.invincible = True
            self.invincible_timer = 60  # シールドヒット時に1秒間の無敵
            return False  # ライフへのダメージはなし

        # シールドがない場合はダメージを受ける
        self.invincible = True
        self.invincible_timer = 120  # ライフ減少時に2秒間の無敵
        return True
    
    def get_all_collision_rects(self):
        rects = [self.rect]
        rects.extend(self.option_manager.get_option_rects())
        return rects
    
    def reset_level(self):
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100
        self.option_manager.reset()

    def reset_position(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 100

    def change_weapon(self, weapon_type):
        if weapon_type in self.upgrade_data.get('unlocked_weapons', []):
            self.current_weapon = weapon_type
            self.apply_upgrades() # 武器変更時に性能を再適用
            return True
        return False
    
    def draw(self, screen):
        if self.invincible and pygame.time.get_ticks() % 200 < 100:
            return  # Blink effect

        if self.has_shield: # レベルアップによるシールド表示
            shield_alpha = 100 + int(50 * math.sin(pygame.time.get_ticks() * 0.01))
            shield_color_base = BLUE[:3]
            shield_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            shield_color = (*shield_color_base, min(255, max(0, shield_alpha)))
            pygame.draw.circle(shield_surface, shield_color, (self.size, self.size), self.size)
            screen.blit(shield_surface, (self.x - self.size, self.y - self.size))
        
        img_rect = self.image.get_rect(center=(self.x, self.y))
        screen.blit(self.image, img_rect)
        
        # 武器タイプに応じたエフェクト（レベルアップ機能と重複しないように調整）
        # if self.current_weapon == "wide_shot":
        #     pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), self.size // 2 + 5, 2)
        # elif self.current_weapon == "laser_weapon":
        #     pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), self.size // 2 + 5, 2)

        if self.has_speed_boost: pygame.draw.circle(screen, MAGENTA, (int(self.x), int(self.y)), self.size // 2 + 5, 2)
        if self.has_laser: pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), self.size // 2 + 3, 2)
        if self.has_bomb: pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), self.size // 2 + 4, 2)
        
        self.option_manager.draw(screen)
        
        