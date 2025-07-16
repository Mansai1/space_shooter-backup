import pygame
import random
from settings import *
from boss.moving_wall import MovingWall
from boss.gravity_field import GravityField

class EnvironmentalBoss:
    def __init__(self, x, y, player_level):
        self.name = "環境操作型中ボス"
        self.max_hp = player_level * 150 # HPを少し増加
        self.hp = self.max_hp
        self.phases = 3
        self.current_phase = 1
        self.x = x
        self.y = y
        self.size = (80, 80)
        self.rect = pygame.Rect(x - self.size[0] // 2, y - self.size[1] // 2, self.size[0], self.size[1])
        self.move_speed = 2
        self.active = True
        self.score_value = 7500
        self.flash_timer = 0
        self.moving_walls = pygame.sprite.Group()
        self.gravity_fields = []

        self.phase_transition_hp = {
            2: self.max_hp * 0.66,
            3: self.max_hp * 0.33,
        }

        self.wall_spawn_timer = 0
        self.wall_spawn_interval = 2.0 * 60 # 2.0秒 壁の出現間隔を短くする

        self.gravity_spawn_timer = 0
        self.gravity_spawn_interval = 4 * 60 # 4秒

        self.darkness_active = False
        self.darkness_start_time = 0
        self.darkness_duration = 7 * 60 # 7秒
        self.darkness_cooldown = 6 * 60 # 6秒
        self.darkness_last_end_time = 0
        self.vision_radius = 250
        self.entrance_timer = 180 # 3秒間の登場演出

    def update(self, player, all_sprites):
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

        if self.flash_timer > 0:
            self.flash_timer -= 1

        self.check_phase_transition()

        if self.current_phase >= 1:
            self.update_phase_1(all_sprites)
        if self.current_phase >= 2:
            self.update_phase_2()
        if self.current_phase >= 3:
            self.update_phase_3()
        
        self.update_rect()
        self.moving_walls.update()
        for field in self.gravity_fields:
            field.update()

        # 重力場が弾に影響を与える
        # for bullet in player_bullets: # 仮
        #     for field in self.gravity_fields:
        #         field.apply_force(bullet)

        return [] # このボスは弾を返さない

    def check_phase_transition(self):
        if self.current_phase == 1 and self.hp <= self.phase_transition_hp[2]:
            self.current_phase = 2
            print("ボス: フェーズ2に移行！重力場を生成！")
        elif self.current_phase == 2 and self.hp <= self.phase_transition_hp[3]:
            self.current_phase = 3
            print("ボス: フェーズ3に移行！視界が悪くなる！")
            self.darkness_active = True
            self.darkness_start_time = pygame.time.get_ticks()

    def update_phase_1(self, all_sprites):
        self.wall_spawn_timer += 1
        if self.wall_spawn_timer >= self.wall_spawn_interval:
            self.wall_spawn_timer = 0
            wall = MovingWall()
            self.moving_walls.add(wall)
            all_sprites.add(wall)

    def update_phase_2(self):
        self.gravity_spawn_timer += 1
        if len(self.gravity_fields) < 3 and self.gravity_spawn_timer > self.gravity_spawn_interval:
            self.gravity_spawn_timer = 0
            self.gravity_fields.append(GravityField())

    def update_phase_3(self):
        current_time = pygame.time.get_ticks()
        if self.darkness_active:
            if current_time - self.darkness_start_time > self.darkness_duration:
                self.darkness_active = False
                self.darkness_last_end_time = current_time
        else:
            if current_time - self.darkness_last_end_time > self.darkness_cooldown:
                self.darkness_active = True
                self.darkness_start_time = current_time

    def draw(self, screen):
        if self.active:
            color = (120, 0, 180)
            if self.flash_timer > 0:
                color = RED

            pygame.draw.rect(screen, color, self.rect)
            # self.draw_health_bar(screen) # 描画はmainループのUI関数に任せる
            self.moving_walls.draw(screen)
            for field in self.gravity_fields:
                field.draw(screen)

            if self.darkness_active:
                self.draw_darkness(screen)

    def draw_darkness(self, screen):
        dark_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dark_surface.fill((0, 0, 0, 200))
        
        # プレイヤー周辺を明るくする
        light_rect = pygame.Rect(0, 0, self.vision_radius * 2, self.vision_radius * 2)
        light_rect.center = self.rect.center # ボス中心に明るい円
        pygame.draw.circle(dark_surface, (0,0,0,0), light_rect.center, self.vision_radius)

        screen.blit(dark_surface, (0,0))

    def draw_health_bar(self, screen):
        bar_width = self.size[0] * 1.5
        bar_height = 12
        bar_x = self.rect.centerx - bar_width / 2
        bar_y = self.rect.top - 20

        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        health_ratio = self.hp / self.max_hp
        health_width = bar_width * health_ratio
        health_color = GREEN if health_ratio > 0.6 else YELLOW if health_ratio > 0.3 else RED
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))

    def take_damage(self, damage):
        if self.entrance_timer > 0:
            return False
        self.flash_timer = 10
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.active = False
            print("環境操作型中ボス撃破！")
        return self.hp <= 0

    def update_rect(self):
        self.rect.center = (self.x, self.y)

    def is_alive(self):
        return self.active

    def get_current_spell_data(self):
        """UI描画のために、通常のボスと同じ形式でHPデータを返す"""
        phase_name = f"フェーズ {self.current_phase}"
        return {
            "name": f"{self.name} - {phase_name}",
            "current_health": self.hp,
            "max_health": self.max_hp,
        }

    def draw_outline(self, screen, color, width):
        """必殺技が当たった時のアウトライン描画"""
        pygame.draw.rect(screen, color, self.rect.inflate(width*2, width*2), width)
