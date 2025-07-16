import pygame
import random
import sys
import os # 追加
import json # 追加
from settings import *
from player import Player
from bullet import Bullet, Bomb, MasterSpark
# from enemy import Enemy
from enemy.enemy_factory import EnemyFactory
from enemy.sniperEnemy import SniperEnemy
from powerup import PowerUp
from utils import *
from sound_manager import init_sound_system, play_sound
from level_system import LevelSystem, DifficultyManager
from level_ui import draw_level_info, draw_level_up_notification, draw_level_transition, draw_stats_panel, draw_difficulty_info, draw_stage_clear, draw_special_gauge
from boss.boss import BossManager  # ボス管理クラスをインポート
from boss.environmental_boss import EnvironmentalBoss
from boss.boss_ui import draw_boss_health_bar, draw_boss_spell_card_name # 追加
from level_up_upgrade_screen import LevelUpUpgradeScreen # レベルアップ時アップグレード画面
from damage_number import DamageNumber # 追加

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Shooter - Enemy Variety Edition")
        self.clock = pygame.time.Clock()
        self.font = init_font()
        self.small_font = init_small_font()
        self.level_system = LevelSystem()
        self.difficulty_manager = DifficultyManager()  # 難易度管理を追加
        
        # スクリプトのディレクトリパスを取得
        self.base_dir = os.path.dirname(__file__)
        self.boss_manager = BossManager(self.base_dir)  # ボス管理を追加し、base_dirを渡す

        # 背景画像の読み込みと設定
        background_path = os.path.join(self.base_dir, "assets", "img", "game_back.png")
        self.background_image = pygame.image.load(background_path).convert()
        self.bg_height = self.background_image.get_height()
        self.scroll_y = 0
        self.scroll_speed = 1
        
        self.level_up_notification_timer = 0
        self.level_transition_timer = 0
        
        # サウンドシステムの初期化
        self.sound_manager = init_sound_system()

        # アップグレードデータをロード
        self.upgrade_data = self.load_upgrade_data()

        self.game_state = "TITLE"  # TITLE, PLAYING, PAUSED, GAME_OVER, UPGRADE, LEVEL_UP_CHOICE
        self.is_paused = False

        # タイトル画面のボタン
        self.start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50)
        self.upgrade_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 20, 200, 50)
        self.quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 90, 200, 50)
        
        # レベルアップ選択画面の初期化
        self.level_up_upgrade_screen = LevelUpUpgradeScreen(self.screen, self.font, self.small_font)

        # self.reset_game() # タイトル画面から開始するため、ここでは呼ばない

    def load_upgrade_data(self):
        try:
            with open(os.path.join(self.base_dir, 'upgrade_data.json'), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # デフォルト設定を返す
            return {"points": 0, "attack_level": 1, "fire_rate_level": 1, "speed_level": 1, "option_level": 0}

    def save_upgrade_data(self):
        with open(os.path.join(self.base_dir, 'upgrade_data.json'), 'w') as f:
            json.dump(self.upgrade_data, f, indent=4)
        
    def reset_game(self):
        """ゲームの初期化"""
        # アップグレードデータをプレイヤーに渡す
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100, self.upgrade_data)
        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.boss_bullets = []
        self.special_attacks = []
        self.powerups = []
        self.particles = []
        self.damage_numbers = [] # ダメージ数値管理リストを追加
        self.score = 0
        self.lives = 3 # ライフ制に変更

        self.enemy_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.wave_spawn_timer = 0
        self.wave_spawn_interval = 300  # 5秒間隔で編隊出現

        self.level_system = LevelSystem()
        self.difficulty_manager = DifficultyManager()
        self.boss_manager = BossManager(self.base_dir)
        self.game_state = "PLAYING"
        
    def get_current_level_config(self):
        """現在のレベル設定を取得"""
        return self.level_system.get_current_config()
        
    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.game_state == "TITLE":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_button.collidepoint(event.pos):
                        self.reset_game()
                        if self.sound_manager:
                            self.sound_manager.play_music()
                    elif self.upgrade_button.collidepoint(event.pos):
                        self.game_state = "UPGRADE"
                    elif self.quit_button.collidepoint(event.pos):
                        return False
            
            if event.type == pygame.KEYDOWN:
                if self.game_state == "TITLE":
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                        if self.sound_manager:
                            self.sound_manager.play_music()

                elif self.game_state == "PLAYING":
                    if event.key == pygame.K_p:
                        self.is_paused = not self.is_paused
                    elif not self.is_paused:
                        if event.key == pygame.K_SPACE:
                            if self.level_transition_timer > 0:
                                self.level_transition_timer = 0
                            new_bullets = self.player.shoot(self.enemies, self.boss_manager.get_current_boss())
                            if new_bullets:
                                self.bullets.extend(new_bullets)
                                play_sound('shoot')
                        elif event.key == pygame.K_b:
                            special_attack = self.player.shoot_special(self.boss_manager.get_current_boss())
                            if special_attack:
                                self.special_attacks.append(special_attack)
                                play_sound('masupa')
                        elif event.key == pygame.K_m:
                            if self.sound_manager.music_playing:
                                self.sound_manager.stop_music()
                            else:
                                self.sound_manager.play_music()

                elif self.game_state == "GAME_OVER":
                    if event.key == pygame.K_r:
                        self.game_state = "TITLE"
                    elif event.key == pygame.K_q:
                        return False

            elif self.game_state == "LEVEL_UP_CHOICE":
                chosen_upgrade = self.level_up_upgrade_screen.handle_event(event)
                if chosen_upgrade:
                    # プレイヤーにアップグレードを適用
                    self.player.apply_runtime_upgrade(chosen_upgrade)
                    # ゲームを再開
                    self.game_state = "PLAYING"

            if event.type == pygame.MOUSEBUTTONDOWN and self.game_state == "STAGE_CLEAR":
                self.next_stage()
        
        # 連続射撃のための処理
        if self.game_state == "PLAYING":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                new_bullets = self.player.shoot(self.enemies, self.boss_manager.get_current_boss())
                if new_bullets:  # 弾が発射された場合
                    self.bullets.extend(new_bullets)
                    play_sound('shoot')  # 射撃音再生
                        
        return True
    
    def update_game(self):
        """ゲームロジックの更新"""
        if self.game_state != "PLAYING" or self.is_paused or self.level_up_upgrade_screen.is_active:
            return
            
        # 背景スクロール（ボス戦以外）
        if not self.boss_manager.get_current_boss():
            self.scroll_y += self.scroll_speed
            if self.scroll_y >= self.bg_height:
                self.scroll_y = 0

        # 現在のレベル設定を取得
        current_level_config = self.get_current_level_config()
        
        # レベルアップ通知
        if self.level_up_notification_timer > 0:
            draw_level_up_notification(self.screen, self.font, self.level_up_notification_timer)
            self.level_up_notification_timer -= 1

        # ボス出現チェック
        boss_type = self.boss_manager.should_spawn_boss(
            self.level_system.current_level, 
            self.level_system.total_enemies_defeated
        )
        if boss_type:
            boss = self.boss_manager.spawn_boss(boss_type, self.font, self.level_system.current_level)
            if boss:
                print(f"Boss spawned: {boss_type}")
        
        # ボスの更新
        enemy_sprites = pygame.sprite.Group(*self.enemies)
        all_sprites = pygame.sprite.Group(self.player, enemy_sprites)
        boss_bullets = self.boss_manager.update(self.player, all_sprites)
        if boss_bullets:
            self.boss_bullets.extend(boss_bullets)
        
        # プレイヤーの更新
        self.player.update()
        
        # 弾の更新
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)
                
        # 敵の弾の更新
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if not bullet.active:
                self.enemy_bullets.remove(bullet)
        
        # ボス弾の更新
        for bullet in self.boss_bullets[:]:
            bullet.update()
            if not bullet.active:
                self.boss_bullets.remove(bullet)

        for attack in self.special_attacks[:]:
            attack.update()
            if not attack.active:
                self.special_attacks.remove(attack)
        
        # パワーアップの更新
        for powerup in self.powerups[:]:
            powerup.update()
            if not powerup.active:
                self.powerups.remove(powerup)
        
        # ボスがいる場合は通常敵の出現を制限
        current_boss = self.boss_manager.get_current_boss()
        if not current_boss:
            # 単体敵の生成（レベル設定を適用）
            spawn_rate = max(30, ENEMY_SPAWN_RATE - (self.level_system.current_level * 5))
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= spawn_rate:
                self.enemy_spawn_timer = 0
                enemy_x = random.randint(ENEMY_SIZE, SCREEN_WIDTH - ENEMY_SIZE)
                
                # レベル設定を敵生成に渡す
                enemy = EnemyFactory.create_random_enemy(enemy_x, -ENEMY_SIZE, self.player, current_level_config)
                self.enemies.append(enemy)
            
            # 敵の編隊生成（レベル設定を適用）
            self.wave_spawn_timer += 1
            if self.wave_spawn_timer >= self.wave_spawn_interval:
                self.wave_spawn_timer = 0
                self.spawn_enemy_wave(current_level_config)
        
        # パワーアップの生成
        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer >= POWERUP_SPAWN_RATE:
            self.powerup_spawn_timer = 0
            powerup_x = random.randint(POWERUP_SIZE, SCREEN_WIDTH - POWERUP_SIZE)
            powerup_type = random.choice(POWERUP_TYPES)
            powerup = PowerUp(powerup_x, -POWERUP_SIZE, powerup_type)
            self.powerups.append(powerup)
        
        # 敵の更新
        for enemy in self.enemies[:]:
            new_bullets = enemy.update()  # 戻り値を修正
            if new_bullets:  # 弾が生成された場合
                self.enemy_bullets.extend(new_bullets)  # 弾幕を追加
            
            # 敵が画面外に出たら削除
            if not enemy.active:
                self.enemies.remove(enemy)
            elif enemy.should_shoot() and random.random() < 0.3:  # 既存の処理も残す
                # スナイパー敵の場合は狙い撃ち
                if isinstance(enemy, SniperEnemy):
                    enemy_bullet = enemy.shoot(self.player.x, self.player.y)
                else:
                    enemy_bullet = enemy.shoot()
                self.enemy_bullets.append(enemy_bullet)
        
        # 当たり判定
        self.check_collisions()
        
        # パーティクルの更新
        update_particles(self.particles)

        # ダメージ数値の更新
        for dn in self.damage_numbers[:]:
            dn.update()
            if not dn.active:
                self.damage_numbers.remove(dn)
        
        # ゲームオーバー判定
        if self.lives <= 0:
            self.game_state = "GAME_OVER"
            points_earned = self.score // 10
            self.upgrade_data['points'] += points_earned
            self.save_upgrade_data()
            print(f"Game Over. Earned {points_earned} points.")
            if self.sound_manager:
                self.sound_manager.stop_music()
    
    def spawn_enemy_wave(self, level_config=None):
        """敵の編隊を生成（レベル設定適用）"""
        # レベルに応じて使用可能な編隊タイプを決定
        wave_types = EnemyFactory.get_wave_types_for_level(level_config)
        
        wave_type = random.choice(wave_types)
        
        start_x = random.randint(100, SCREEN_WIDTH - 100)
        start_y = -50
        
        # レベル設定を編隊生成に渡す
        wave_enemies = EnemyFactory.create_enemy_wave(wave_type, start_x, start_y, self.player, level_config)
        self.enemies.extend(wave_enemies)
    
    def check_collisions(self):
        """当たり判定の処理"""
        # プレイヤーの弾と敵の当たり判定
        for bullet in self.bullets[:]:
            hit_enemy = False
            
            # 爆弾の場合は特別な処理
            if isinstance(bullet, Bomb):
                # 爆弾が敵に直撃したかチェック
                if self.player.check_bomb_collision(bullet, self.enemies):
                    # 爆弾爆発エフェクト
                    explosion_particles = create_bomb_explosion_effect()
                    for particle in explosion_particles:
                        particle['x'] = bullet.x
                        particle['y'] = bullet.y
                    self.particles.extend(explosion_particles)
                    
                    # 爆弾爆発音
                    # play_sound('bomb_explode')
                    
                    # 爆発範囲内の敵にダメージ
                    for enemy in self.enemies[:]:
                        if check_bomb_explosion_collision(bullet, enemy):
                            was_destroyed = enemy.take_damage(10)  # 爆発ダメージ
                            
                            if was_destroyed:
                                self.enemies.remove(enemy)
                                # スコア加算
                                score_value = getattr(enemy, 'score_value', ENEMY_SCORE)
                                self.score += score_value
                                
                                # 経験値とレベルアップ処理（新システム）
                                old_level = self.level_system.current_level
                                # 敵のタイプを取得（可能であれば）
                                enemy_type = getattr(enemy, 'enemy_type', 'basic')
                                # 計算された経験値を追加
                                calculated_exp = self.level_system.calculate_experience_gain(BASE_EXPERIENCE_GAIN, enemy_type)
                                self.level_system.add_experience(calculated_exp)
                                self.level_system.total_enemies_defeated += 1
                                
                                # レベルアップチェック
                                if self.level_system.current_level > old_level:
                                    self.level_up_notification_timer = LEVEL_UP_NOTIFICATION_DURATION
                                
                                # 敵撃破エフェクト
                                enemy_explosion_particles = create_explosion_effect()
                                for particle in enemy_explosion_particles:
                                    particle['x'] = enemy.x
                                    particle['y'] = enemy.y
                                self.particles.extend(enemy_explosion_particles)
                    
                    # 爆弾を削除
                    self.bullets.remove(bullet)
                    hit_enemy = True
                    
            else:
                # 通常弾・レーザーの処理
                for enemy in self.enemies[:]:
                    if check_collision(bullet.rect, enemy.rect):
                        # レーザーでない場合は弾を削除
                        if not hasattr(bullet, 'penetrating') or not bullet.penetrating:
                            self.bullets.remove(bullet)
                        
                        # 敵にダメージを与える
                        damage = getattr(bullet, 'damage', 1)
                        was_destroyed = enemy.take_damage(damage)

                        # ダメージ数値を生成
                        self.damage_numbers.append(DamageNumber(enemy.x, enemy.y, damage, self.small_font, YELLOW))
                        
                        if was_destroyed:
                            # 敵が撃破された場合のみ削除
                            self.enemies.remove(enemy)
                            # 敵のタイプに応じてスコア加算
                            score_value = getattr(enemy, 'score_value', ENEMY_SCORE)
                            self.score += score_value    

                            # 経験値とレベルアップ処理（新システム）
                            enemy_type = getattr(enemy, 'enemy_type', 'basic')
                            exp_gain = self.level_system.calculate_experience_gain(BASE_EXPERIENCE_GAIN, enemy_type)
                            # レベルアップしたかどうかをチェック
                            if self.level_system.add_experience(exp_gain):
                                self.game_state = "LEVEL_UP_CHOICE"
                                self.level_up_upgrade_screen.start_selection()
                                self.player.on_level_up(self.level_system.current_level) # プレイヤーのレベルアップ処理を呼び出す

                            self.level_system.total_enemies_defeated += 1

                            # サウンド再生
                            play_sound('enemy_hit')
                            
                            # 爆発エフェクト
                            explosion_particles = create_explosion_effect()
                            for particle in explosion_particles:
                                particle['x'] = enemy.x
                                particle['y'] = enemy.y
                            self.particles.extend(explosion_particles)
                        else:
                            # シールドで防がれた場合のサウンド（あれば）
                            # play_sound('shield_hit')  # 必要に応じて追加
                            pass
                        
                        hit_enemy = True
                        # レーザーでない場合はループを抜ける
                        if not hasattr(bullet, 'penetrating') or not bullet.penetrating:
                            break
            
            if hit_enemy:
                continue
        
        # プレイヤーの弾とボスの当たり判定
        current_boss = self.boss_manager.get_current_boss()
        if current_boss:
            for bullet in self.bullets[:]:
                if check_collision(bullet.rect, current_boss.rect):
                    # レーザーでない場合は弾を削除
                    if not hasattr(bullet, 'penetrating') or not bullet.penetrating:
                        self.bullets.remove(bullet)
                    
                    # ボスにダメージを与える
                    damage = getattr(bullet, 'damage', 1)
                    was_destroyed = current_boss.take_damage(damage)

                    # ダメージ数値を生成
                    self.damage_numbers.append(DamageNumber(current_boss.x, current_boss.y, damage, self.small_font, RED))
                    
                    if was_destroyed:
                        # ボス撃破時の処理
                        self.score += current_boss.score_value
                        
                        # 大量の経験値獲得（新システム）
                        old_level = self.level_system.current_level
                        # ボス撃破の経験値（基本値の10倍、さらに倍率適用）
                        boss_base_exp = BASE_EXPERIENCE_GAIN * 10
                        self.level_system.add_experience(boss_base_exp)
                        self.level_system.total_enemies_defeated += 1
                        
                        # レベルアップチェック
                        if self.level_system.current_level > old_level:
                            self.level_up_notification_timer = LEVEL_UP_NOTIFICATION_DURATION
                        
                        # ボス撃破エフェクト
                        boss_explosion_particles = create_explosion_effect()
                        for i in range(5):  # 複数の爆発エフェクト
                            for particle in boss_explosion_particles:
                                particle['x'] = current_boss.x + random.randint(-30, 30)
                                particle['y'] = current_boss.y + random.randint(-30, 30)
                            self.particles.extend(boss_explosion_particles)
                        
                        # ボス撃破音
                        # play_sound('enemy_hit')  # ボス撃破音（適切な音があれば変更）
                        self.game_state = "STAGE_CLEAR"
                        print(f"Boss defeated! Score: {current_boss.score_value}")  # デバッグ用
                    
                    # レーザーでない場合はループを抜ける
                    if not hasattr(bullet, 'penetrating') or not bullet.penetrating:
                        break
            
        # プレイヤーとパワーアップの当たり判定
        for powerup in self.powerups[:]:
            if check_collision(powerup.rect, self.player.rect):
                self.powerups.remove(powerup)
                if powerup.power_type == "life_up":
                    self.lives += 1 # ライフを1増やす
                    play_sound('powerup') # サウンド再生
                # 他のパワーアップはレベルアップで機能追加されるため、ここでは処理しない
                break
        
        # 敵の弾とプレイヤーの当たり判定
        for bullet in self.enemy_bullets[:]:
            if check_collision(bullet.rect, self.player.rect):
                self.enemy_bullets.remove(bullet)
                if self.player.take_damage():  # シールドで防げなかった場合
                    self.lives -= 1
                    
                    # サウンド再生
                    play_sound('player_hit')
                    
                    # プレイヤー被弾エフェクト
                    explosion_particles = create_explosion_effect()
                    for particle in explosion_particles:
                        particle['x'] = self.player.x
                        particle['y'] = self.player.y
                    self.particles.extend(explosion_particles)
                break
        
        # ボス弾とプレイヤーの当たり判定
        for bullet in self.boss_bullets[:]:
            if check_collision(bullet.rect, self.player.rect):
                self.boss_bullets.remove(bullet)
                if self.player.take_damage():  # シールドで防げなかった場合
                    self.lives -= 1
                    
                    # サウンド再生
                    play_sound('player_hit')
                    
                    # プレイヤー被弾エフェクト
                    explosion_particles = create_explosion_effect()
                    for particle in explosion_particles:
                        particle['x'] = self.player.x
                        particle['y'] = self.player.y
                    self.particles.extend(explosion_particles)
                break
        
        # 敵とプレイヤーの当たり判定
        for enemy in self.enemies[:]:
            if check_collision(enemy.rect, self.player.rect):
                # 敵にダメージを与える（衝突時は大ダメージ）
                was_destroyed = enemy.take_damage(3)  # 衝突時は3ダメージ
                
                if was_destroyed:
                    self.enemies.remove(enemy)
                
                if self.player.take_damage():  # シールドで防げなかった場合
                    self.lives -= 1
                    
                    # サウンド再生
                    play_sound('player_hit')
                
                # 衝突エフェクト
                explosion_particles = create_explosion_effect()
                for particle in explosion_particles:
                    particle['x'] = enemy.x
                    particle['y'] = enemy.y
                self.particles.extend(explosion_particles)
                break
        
        # プレイヤーと環境ボス移動壁の当たり判定
        current_boss = self.boss_manager.get_current_boss()
        if current_boss and isinstance(current_boss, EnvironmentalBoss):
            for wall in current_boss.moving_walls:
                if check_collision(self.player.rect, wall.rect):
                    if self.player.take_damage():  # シールドで防げなかった場合
                        self.lives -= 1
                        
                        # サウンド再生
                        play_sound('player_hit')
                    
                        # プレイヤー被弾エフェクト
                        explosion_particles = create_explosion_effect()
                        for particle in explosion_particles:
                            particle['x'] = self.player.x
                            particle['y'] = self.player.y
                        self.particles.extend(explosion_particles)
                    break
        
        # ボスとプレイヤーの当たり判定
        current_boss = self.boss_manager.get_current_boss()
        if current_boss and check_collision(current_boss.rect, self.player.rect):
            if self.player.take_damage():  # シールドで防げなかった場合
                self.lives -= 2  # ボスとの衝突は2ダメージ
                
                # サウンド再生
                play_sound('player_hit')
                
                # 衝突エフェクト
                explosion_particles = create_explosion_effect()
                for particle in explosion_particles:
                    particle['x'] = self.player.x
                    particle['y'] = self.player.y
                self.particles.extend(explosion_particles)

        # 必殺技と敵の当たり判定
        for attack in self.special_attacks:
            for enemy in self.enemies[:]:
                if check_collision(attack.rect, enemy.rect):
                    if enemy.take_damage(attack.damage):
                        self.enemies.remove(enemy)
                        self.score += getattr(enemy, 'score_value', ENEMY_SCORE)

            if current_boss:
                if check_collision(attack.rect, current_boss.rect):
                    if current_boss.take_damage(attack.damage):
                        self.score += current_boss.score_value
                        self.game_state = "STAGE_CLEAR"

    def next_stage(self):
        self.level_system.next_level()
        self.player.reset_position()
        self.enemies.clear()
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.boss_bullets.clear()
        self.powerups.clear()
        self.game_state = "PLAYING"
    
    def draw(self):
        """描画処理"""
        # 背景画像のスクロール描画
        y1 = self.scroll_y
        y2 = self.scroll_y - self.bg_height
        self.screen.blit(self.background_image, (0, y1))
        self.screen.blit(self.background_image, (0, y2))

        if self.game_state == "TITLE":
            draw_text(self.screen, "Space Shooter", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, self.font, WHITE)
            pygame.draw.rect(self.screen, DARK_GRAY, self.start_button)
            draw_text(self.screen, "Start", self.start_button.centerx, self.start_button.centery, self.font, WHITE)
            pygame.draw.rect(self.screen, DARK_GRAY, self.upgrade_button)
            draw_text(self.screen, "Upgrade", self.upgrade_button.centerx, self.upgrade_button.centery, self.font, WHITE)
            pygame.draw.rect(self.screen, DARK_GRAY, self.quit_button)
            draw_text(self.screen, "Quit", self.quit_button.centerx, self.quit_button.centery, self.font, WHITE)

        elif self.game_state == "PLAYING" or self.is_paused:
            # --- ゲーム要素の描画 ---
            self.player.draw(self.screen)

            for bullet in self.bullets:
                bullet.draw(self.screen)

            for bullet in self.enemy_bullets:
                bullet.draw(self.screen)

            # ボス弾の描画
            for bullet in self.boss_bullets:
                bullet.draw(self.screen)

            for enemy in self.enemies:
                enemy.draw(self.screen)

            # ボスの描画
            current_boss = self.boss_manager.get_current_boss()
            if current_boss:
                current_boss.draw(self.screen)
                # ボスのHPバーとスペルカード名を描画
                draw_boss_health_bar(self.screen, current_boss, self.font)
                draw_boss_spell_card_name(self.screen, current_boss, self.font)

            for powerup in self.powerups:
                powerup.draw(self.screen)

            for attack in self.special_attacks:
                attack.draw(self.screen)

            # マスタースパークがアクティブな場合、敵にアウトラインを描画
            for attack in self.special_attacks:
                if isinstance(attack, MasterSpark):
                    for enemy in self.enemies:
                        if check_collision(attack.rect, enemy.rect):
                            enemy.draw_outline(self.screen, YELLOW, 2) # 黄色いアウトライン
                    current_boss = self.boss_manager.get_current_boss()
                    if current_boss and check_collision(attack.rect, current_boss.rect):
                        current_boss.draw_outline(self.screen, YELLOW, 3) # ボスには太いアウトライン

            # パーティクルの描画
            draw_particles(self.screen, self.particles)

            # ダメージ数値の描画
            for dn in self.damage_numbers:
                dn.draw(self.screen)

            # --- UI の描画 ---
            draw_score(self.screen, self.score, self.font, x=50, y=30)
            draw_lives(self.screen, self.lives, self.font, x=50, y=60)
            draw_powerups(self.screen, self.player, self.small_font, x=50, y_start=90)
            draw_enemy_info(self.screen, self.enemies, self.small_font, x=SCREEN_WIDTH - 50, y_start=30)

            # レベルシステムUI の追加
            draw_level_info(self.screen, self.level_system, self.font, self.small_font, x=50, y_start=SCREEN_HEIGHT - 150)
            draw_stats_panel(self.screen, self.level_system, self.font, self.small_font, x=50, y_start=SCREEN_HEIGHT - 100)
            draw_difficulty_info(self.screen, self.level_system, self.small_font, x=50, y_start=SCREEN_HEIGHT - 50)

            # 必殺技ゲージの描画
            draw_special_gauge(self.screen, self.player, self.font)

            # サウンド状態表示と武器情報
            draw_sound_status(self.screen, self.sound_manager, self.small_font, x=SCREEN_WIDTH - 50, y=SCREEN_HEIGHT - 30)
            draw_weapon_status(self.screen, self.player, self.small_font, x=SCREEN_WIDTH - 50, y=SCREEN_HEIGHT - 60)

            if self.is_paused:
                draw_pause_screen(self.screen, self.font)
        
        elif self.game_state == "LEVEL_UP_CHOICE":
            # --- ゲーム画面を背景として描画 ---
            self.player.draw(self.screen)
            for bullet in self.bullets: bullet.draw(self.screen)
            for bullet in self.enemy_bullets: bullet.draw(self.screen)
            for bullet in self.boss_bullets: bullet.draw(self.screen)
            for enemy in self.enemies: enemy.draw(self.screen)
            current_boss = self.boss_manager.get_current_boss()
            if current_boss:
                current_boss.draw(self.screen)
                draw_boss_health_bar(self.screen, current_boss, self.font)
                draw_boss_spell_card_name(self.screen, current_boss, self.font)
            for powerup in self.powerups: powerup.draw(self.screen)
            for attack in self.special_attacks: attack.draw(self.screen)
            draw_particles(self.screen, self.particles)
            for dn in self.damage_numbers:
                dn.draw(self.screen)

            # --- UIも背景として描画 ---
            draw_score(self.screen, self.score, self.font, x=50, y=30)
            draw_lives(self.screen, self.lives, self.font, x=50, y=60)
            draw_powerups(self.screen, self.player, self.small_font, x=50, y_start=90)
            draw_enemy_info(self.screen, self.enemies, self.small_font, x=SCREEN_WIDTH - 50, y_start=30)
            draw_level_info(self.screen, self.level_system, self.font, self.small_font, x=50, y_start=SCREEN_HEIGHT - 150)
            draw_stats_panel(self.screen, self.level_system, self.font, self.small_font, x=50, y_start=SCREEN_HEIGHT - 100)
            draw_difficulty_info(self.screen, self.level_system, self.small_font, x=50, y_start=SCREEN_HEIGHT - 50)
            draw_special_gauge(self.screen, self.player, self.font)
            draw_sound_status(self.screen, self.sound_manager, self.small_font, x=SCREEN_WIDTH - 50, y=SCREEN_HEIGHT - 30)
            draw_weapon_status(self.screen, self.player, self.small_font, x=SCREEN_WIDTH - 50, y=SCREEN_HEIGHT - 60)

            # --- アップグレード選択画面を最前面に描画 ---
            self.level_up_upgrade_screen.draw()

        elif self.game_state == "GAME_OVER":
            # ゲームオーバー画面
            draw_game_over_screen(self.screen, self.score, self.font)

        elif self.game_state == "STAGE_CLEAR":
            draw_stage_clear(self.screen, self.font)

        pygame.display.flip()
    
    def run(self):
        """メインゲームループ"""
        running = True
        while running:
            if self.game_state == "UPGRADE":
                from upgrade_screen import UpgradeScreen
                upgrade_screen = UpgradeScreen(self.screen, os.path.join(self.base_dir, 'NotoSansJP-VariableFont_wght.ttf'))
                upgrade_screen.run()
                self.upgrade_data = self.load_upgrade_data() # データを再読み込み
                self.game_state = "TITLE"
            
            running = self.handle_events()
            if self.game_state == "PLAYING":
                self.update_game()
            
            self.draw()
            self.clock.tick(FPS)
        
        self.save_upgrade_data()
        # クリーンアップ
        if self.sound_manager:
            self.sound_manager.stop_music()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()