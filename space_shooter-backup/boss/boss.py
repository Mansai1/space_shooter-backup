import pygame
import math
import random
import os
from settings import *
from boss.boss_bullet import BossBullet
from boss.environmental_boss import EnvironmentalBoss

class Boss:
    """東方風ボスの基底クラス"""
    
    def __init__(self, x, y, boss_type="basic", font=None, base_dir=None, player_level=1, game=None):
        self.x = x
        self.y = y
        self.boss_type = boss_type
        self.width = 80
        self.height = 80
        self.rect = pygame.Rect(x - self.width//2, y - self.height//2, self.width, self.height)
        self.font = font
        self.image = None
        self.base_dir = base_dir
        self.player_level = player_level
        self.game = game  # 追加: Gameインスタンス参照

        self.max_health = 0
        self.health = 0
        self.speed = 1.0
        self.score_value = 5000

        self.current_spell_max_health = 0
        self.current_spell_health = 0
        
        self.move_timer = 0
        self.move_pattern = 0
        self.move_direction = 1
        self.target_x = x
        self.target_y = y
        
        self.spell_cards = []
        self.current_spell = 0
        self.spell_timer = 0
        self.spell_phase = 0
        self.is_casting = False
        
        self.animation_timer = 0
        self.flash_timer = 0
        
        self.active = True
        self.invulnerable = False
        self.entrance_timer = 180
        
        self.init_boss_type()
    
    def init_boss_type(self):
        total_health = 0
        if self.boss_type == "fairy":
            self.score_value = 3000
            self.spell_cards = [
                {"name": "妖精の舞", "pattern": "fairy_dance", "duration": 5400, "spell_health": 100},
                {"name": "光の乱舞", "pattern": "light_burst", "duration": 5400, "spell_health": 150}
            ]
            try:
                image_path = os.path.join(self.base_dir, "assets", "img", "faily.png")
                self.image = pygame.image.load(image_path).convert_alpha()
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
                image_path = os.path.join(self.base_dir, "assets", "img", "magichuman.png")
                self.image = pygame.image.load(image_path).convert_alpha()
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
                image_path = os.path.join(self.base_dir, "assets", "img", "dragon.png")
                self.image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
            except pygame.error as e:
                print(f"Error loading boss image: {e}")
                self.image = None

        for spell in self.spell_cards:
            total_health += spell["spell_health"]
        self.max_health = total_health
        self.health = total_health

        if self.spell_cards:
            self.current_spell_max_health = self.spell_cards[self.current_spell]["spell_health"]
            self.current_spell_health = self.current_spell_max_health
    
    def update(self, player, all_sprites):
        if not self.active:
            return []
        
        if self.entrance_timer > 0:
            self.entrance_timer -= 1
            if self.y < 120:
                self.y += 2
            self.update_rect()
            return []
        
        self.update_movement()
        bullets = self.update_spell_cards()
        
        self.animation_timer += 1
        if self.flash_timer > 0:
            self.flash_timer -= 1
        
        self.update_rect()
        return bullets
    
    def update_movement(self):
        self.move_timer += 1
        width = self.game.current_width if self.game else SCREEN_WIDTH
        height = self.game.current_height if self.game else SCREEN_HEIGHT
        margin = int(width * 0.08)
        top_margin = 50
        bottom_margin = 100
        if self.boss_type == "fairy":
            if self.move_timer % 120 == 0:
                self.target_x = random.randint(margin, width - margin)
            dx = self.target_x - self.x
            if abs(dx) > 2:
                self.x += dx * 0.02
            # 画面内に制限
            self.x = max(margin, min(width - margin, self.x))
            self.y = max(top_margin, min(height - bottom_margin, self.y))
        elif self.boss_type == "witch":
            center_x = width // 2
            center_y = 150
            radius = 80
            angle = self.move_timer * 0.02
            self.x = center_x + math.cos(angle) * radius
            self.y = center_y + math.sin(angle * 2) * 30
            self.x = max(margin, min(width - margin, self.x))
            self.y = max(top_margin, min(height - bottom_margin, self.y))
        elif self.boss_type == "dragon":
            if self.move_timer % 180 == 0:
                self.move_direction *= -1
                self.target_x = width // 4 if self.move_direction < 0 else width * 3 // 4
            dx = self.target_x - self.x
            if abs(dx) > 3:
                self.x += dx * 0.015
            self.x = max(margin, min(width - margin, self.x))
            self.y = max(top_margin, min(height - bottom_margin, self.y))
    
    def update_spell_cards(self):
        if not self.spell_cards:
            return []
        
        bullets = []
        current_spell_data = self.spell_cards[self.current_spell]
        
        if not self.is_casting:
            self.is_casting = True
            self.spell_timer = 0
            self.spell_phase = 0
        
        self.spell_timer += 1
        
        pattern_bullets = self.execute_spell_pattern(current_spell_data["pattern"])
        bullets.extend(pattern_bullets)
        
        if self.spell_timer >= current_spell_data["duration"]:
            self.is_casting = False
            if self.current_spell_health > 0 and self.current_spell < len(self.spell_cards) - 1:
                self.current_spell += 1
                self.current_spell_max_health = self.spell_cards[self.current_spell]["spell_health"]
                self.current_spell_health = self.current_spell_max_health
            self.spell_timer = 0
        
        return bullets
    
    def execute_spell_pattern(self, pattern):
        bullets = []
        
        if pattern == "fairy_dance":
            if self.spell_timer % 20 == 0:
                for i in range(8):
                    angle = (self.spell_timer * 0.1 + i * 45) * math.pi / 180
                    speed = 2.5
                    bullets.append(BossBullet(self.x + math.cos(angle) * 30, self.y + math.sin(angle) * 30, math.cos(angle) * speed, math.sin(angle) * speed, color=CYAN, game=self.game))
        
        elif pattern == "light_burst":
            if self.spell_timer % 30 == 0:
                for i in range(12):
                    angle = i * 30 * math.pi / 180
                    speed = 3.0
                    bullets.append(BossBullet(self.x, self.y, math.cos(angle) * speed, math.sin(angle) * speed, color=YELLOW, game=self.game))
        
        elif pattern == "magic_storm":
            if self.spell_timer % 8 == 0:
                for layer in range(3):
                    angle = (self.spell_timer * 0.2 + layer * 120) * math.pi / 180
                    speed = 2.0 + layer * 0.5
                    bullets.append(BossBullet(self.x, self.y, math.cos(angle) * speed, math.sin(angle) * speed, color=MAGENTA, game=self.game))
        
        elif pattern == "star_rain":
            if self.spell_timer % 15 == 0:
                for i in range(5):
                    x = random.randint(50, self.game.current_width - 50) if self.game else random.randint(50, SCREEN_WIDTH - 50)
                    bullets.append(BossBullet(x, -10, 0, 3.5, color=WHITE, game=self.game))
        
        elif pattern == "spiral_curse":
            if self.spell_timer % 5 == 0:
                angle = self.spell_timer * 0.3 * math.pi / 180
                for direction in [-1, 1]:
                    final_angle = angle * direction
                    speed = 2.5
                    bullets.append(BossBullet(self.x + math.cos(final_angle) * 20, self.y + math.sin(final_angle) * 20, math.cos(final_angle) * speed, math.sin(final_angle) * speed, color=RED, game=self.game))
        
        elif pattern == "dragon_roar":
            if self.spell_timer % 40 == 0:
                width = self.game.current_width if self.game else SCREEN_WIDTH
                center_angle = math.atan2(400 - self.y, width//2 - self.x)
                for i in range(15):
                    angle = center_angle + (i - 7) * 0.2
                    speed = 4.0
                    bullets.append(BossBullet(self.x, self.y + 30, math.cos(angle) * speed, math.sin(angle) * speed, color=ORANGE, game=self.game))
        
        elif pattern == "fire_spiral":
            if self.spell_timer % 12 == 0:
                for ring in range(2):
                    for i in range(6):
                        angle = (self.spell_timer * 0.15 + i * 60 + ring * 30) * math.pi / 180
                        speed = 2.0 + ring * 0.8
                        bullets.append(BossBullet(self.x, self.y, math.cos(angle) * speed, math.sin(angle) * speed, color=RED, game=self.game))
        
        elif pattern == "thunder_spear":
            if self.spell_timer % 60 == 0:
                for i in range(3):
                    width = self.game.current_width if self.game else SCREEN_WIDTH
                    height = self.game.current_height if self.game else SCREEN_HEIGHT
                    target_x = random.randint(100, width - 100)
                    target_y = height
                    angle = math.atan2(target_y - self.y, target_x - self.x)
                    speed = 6.0
                    bullets.append(BossBullet(self.x, self.y, math.cos(angle) * speed, math.sin(angle) * speed, color=BLUE, game=self.game))
        
        elif pattern == "ultimate_blast":
            if self.spell_timer % 8 == 0: # 発射間隔を少し長く (6 -> 8)
                for i in range(12): # 同時発射数を減らす (15 -> 12)
                    angle = i * 30 * math.pi / 180 # 角度を調整 (360/12=30)
                    speed = 2.0 + random.random()
                    bullets.append(BossBullet(self.x, self.y, math.cos(angle) * speed, math.sin(angle) * speed, color=PURPLE, game=self.game))
        
        return bullets
    
    def take_damage(self, damage):
        if self.invulnerable or self.entrance_timer > 0:
            return False
        
        self.current_spell_health -= damage
        self.health -= damage
        self.flash_timer = 10
        
        if self.current_spell_health <= 0:
            self.is_casting = False
            self.current_spell += 1
            if self.current_spell < len(self.spell_cards):
                self.current_spell_max_health = self.spell_cards[self.current_spell]["spell_health"]
                self.current_spell_health = self.current_spell_max_health
            else:
                self.active = False
                return True
        
        if self.health <= 0:
            self.active = False
            return True
        
        return False
    
    def update_rect(self):
        self.rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)
    
    def draw(self, screen):
        if not self.active:
            return
        
        color = WHITE
        if self.flash_timer > 0:
            color = RED
        elif self.entrance_timer > 0:
            alpha = min(255, (180 - self.entrance_timer) * 3)
            color = (*WHITE[:3], alpha) if len(WHITE) == 4 else WHITE
        
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            if self.boss_type == "fairy":
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 30)
                pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), 30, 3)
            elif self.boss_type == "witch":
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 35)
                pygame.draw.circle(screen, MAGENTA, (int(self.x), int(self.y)), 35, 4)
                if self.is_casting:
                    angle = self.animation_timer * 0.1
                    for i in range(6):
                        x = self.x + math.cos(angle + i * 60 * math.pi / 180) * 45
                        y = self.y + math.sin(angle + i * 60 * math.pi / 180) * 45
                        pygame.draw.circle(screen, YELLOW, (int(x), int(y)), 3)
            elif self.boss_type == "dragon":
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 40)
                pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), 40, 5)
                if self.animation_timer % 60 < 30:
                    pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 50, 2)

    def get_current_spell_data(self):
        if self.spell_cards and self.current_spell < len(self.spell_cards):
            return {
                "name": self.spell_cards[self.current_spell]["name"],
                "current_health": self.current_spell_health,
                "max_health": self.current_spell_max_health
            }
        return None

    def draw_outline(self, screen, color, width):
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.width // 2 + width, width)

class BossManager:
    def __init__(self, base_dir=None, game=None):
        self.current_boss = None
        self.base_dir = base_dir
        self.game = game
        self.spawned_bosses_for_level = set()
        
        self.boss_schedule = [
            {"level": 3, "type": "fairy"},
            {"level": 5, "type": "environmental"},
            {"level": 8, "type": "witch"},
            {"level": 12, "type": "dragon"},
        ]
    
    def should_spawn_boss(self, level, enemies_defeated):
        print(f"[BossManager] Checking spawn for level {level}, current_boss: {self.current_boss is not None}, spawned_bosses_for_level: {self.spawned_bosses_for_level}")
        if self.current_boss:
            print("[BossManager] Boss already active.")
            return None

        for boss_data in self.boss_schedule:
            print(f"[BossManager] Checking scheduled boss: {boss_data['type']} at level {boss_data['level']}")
            if level == boss_data["level"] and boss_data["type"] not in self.spawned_bosses_for_level:
                print(f"[BossManager] Scheduled boss {boss_data['type']} should spawn.")
                return boss_data["type"]

        if level >= 10 and level % 5 == 0:
            print("[BossManager] Checking random boss spawn for level >= 10.")
            available_bosses = [b_type for b_type in ["fairy", "witch", "dragon", "environmental"] if b_type not in self.spawned_bosses_for_level]
            if available_bosses:
                chosen_boss = random.choice(available_bosses)
                print(f"[BossManager] Random boss {chosen_boss} chosen.")
                return chosen_boss
            print("[BossManager] No available random bosses to spawn.")
        
        print("[BossManager] No boss to spawn.")
        return None
    
    def spawn_boss(self, boss_type, font, player_level):
        if self.current_boss:
            return None
        width = self.game.current_width if self.game else SCREEN_WIDTH
        x = width // 2
        y = -50
        
        if boss_type == "environmental":
            self.current_boss = EnvironmentalBoss(x, y, player_level, game=self.game)
        else:
            self.current_boss = Boss(x, y, boss_type, font, self.base_dir, player_level, game=self.game)
        
        # スポーンしたボスタイプを記録
        self.spawned_bosses_for_level.add(boss_type)
        return self.current_boss
    
    def update(self, player, all_sprites):
        if not self.current_boss:
            return []
        
        bullets = self.current_boss.update(player, all_sprites)
        
        if not self.current_boss.active:
            self.current_boss = None
        
        return bullets
    
    def get_current_boss(self):
        return self.current_boss
    
    def has_active_boss(self):
        return self.current_boss is not None and self.current_boss.active
