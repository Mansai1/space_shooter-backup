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
        # pygameの初期化を安全に行う
        try:
            pygame.init()
            # ディスプレイモジュールの初期化を確認
            if not pygame.display.get_init():
                pygame.display.init()
        except Exception as e:
            print(f"pygame初期化エラー: {e}")
            sys.exit(1)
        
        # デスクトップの解像度を取得
        try:
            info = pygame.display.Info()
            desktop_width = info.current_w
            desktop_height = info.current_h
        except Exception as e:
            print(f"ディスプレイ情報取得エラー: {e}")
            # デフォルト値を設定
            desktop_width = SCREEN_WIDTH
            desktop_height = SCREEN_HEIGHT

        # 元のアスペクト比を維持しつつ、デスクトップサイズに収まるように調整
        aspect_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
        
        try:
            # 幅を基準に高さを計算
            new_width = desktop_width
            new_height = int(new_width / aspect_ratio)

            # 計算された高さがデスクトップの高さを超える場合、高さを基準に幅を再計算
            if new_height > desktop_height:
                new_height = desktop_height
                new_width = int(new_height * aspect_ratio)
            
            # 最小・最大サイズの制限を適用
            new_width = max(MIN_SCREEN_WIDTH, min(new_width, MAX_SCREEN_WIDTH))
            new_height = max(MIN_SCREEN_HEIGHT, min(new_height, MAX_SCREEN_HEIGHT))
            
        except Exception as e:
            print(f"画面サイズ計算エラー: {e}")
            # エラーが発生した場合はデフォルトサイズを使用
            new_width = SCREEN_WIDTH
            new_height = SCREEN_HEIGHT
        
        self.fullscreen = False  # 追加: 全画面状態フラグ
        self.desktop_width = desktop_width
        self.desktop_height = desktop_height
        self.original_aspect_ratio = aspect_ratio  # 元のアスペクト比を保存
        
        # 画面設定を試行
        try:
            self.set_screen(new_width, new_height, fullscreen=False)
        except Exception as e:
            print(f"初期画面設定エラー: {e}")
            # エラーが発生した場合はデフォルト設定を使用
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.game_viewport = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
            self.screen_scale_x = 1.0
            self.screen_scale_y = 1.0
            self.current_width = SCREEN_WIDTH
            self.current_height = SCREEN_HEIGHT
        pygame.display.set_caption("Space Shooter - Enemy Variety Edition")
        self.clock = pygame.time.Clock()
        self.font = init_font()
        self.small_font = init_small_font()
        
        # FPS制御の初期化
        self.last_frame_time = pygame.time.get_ticks()
        self.frame_count = 0
        self.fps_start_time = pygame.time.get_ticks()
        self.level_system = LevelSystem()
        self.difficulty_manager = DifficultyManager()  # 難易度管理を追加
        
        # スクリプトのディレクトリパスを取得
        self.base_dir = os.path.dirname(__file__)
        self.boss_manager = BossManager(self.base_dir, game=self)  # ボス管理を追加し、base_dirを渡す

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
        
        # システムFPS情報を表示
        if FIXED_FPS:
            from utils import get_system_fps_info
            fps_info = get_system_fps_info()
            print(f"システムFPS情報: 最大={fps_info['max_fps']}, 60FPS維持可能={fps_info['can_maintain_60fps']}")
            if not fps_info['can_maintain_60fps']:
                print("警告: システムが60FPSを維持できない可能性があります")

        self.game_state = "TITLE"  # TITLE, PLAYING, PAUSED, GAME_OVER, UPGRADE, LEVEL_UP_CHOICE
        self.is_paused = False

        # タイトル画面のボタン（描画時に動的に作成されるため、初期化は不要）
        self.start_button = None
        self.upgrade_button = None
        self.quit_button = None
        
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
        # 既存リストをクリア
        if hasattr(self, 'enemies'): self.enemies.clear()
        if hasattr(self, 'bullets'): self.bullets.clear()
        if hasattr(self, 'enemy_bullets'): self.enemy_bullets.clear()
        if hasattr(self, 'boss_bullets'): self.boss_bullets.clear()
        if hasattr(self, 'special_attacks'): self.special_attacks.clear()
        if hasattr(self, 'powerups'): self.powerups.clear()
        if hasattr(self, 'particles'): self.particles.clear()
        if hasattr(self, 'damage_numbers'): self.damage_numbers.clear()
        # アップグレードデータをプレイヤーに渡す
        self.player = Player(self.current_width // 2, self.current_height - 100, self.upgrade_data, game=self)
        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.boss_bullets = []
        self.special_attacks = []
        self.powerups = []
        self.particles = []
        self.damage_numbers = [] # ダメージ数値管理リストを追加
        self.score = 0
        # self.lives = 3 # ライフ制に変更
        self.lives = 100 #デバック用
        self.enemy_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.wave_spawn_timer = 0
        self.wave_spawn_interval = 300  # 5秒間隔で編隊出現
        self.level_system = LevelSystem()
        self.difficulty_manager = DifficultyManager()
        self.boss_manager = BossManager(self.base_dir, game=self)
        self.game_state = "PLAYING"
        
    def get_current_level_config(self):
        """現在のレベル設定を取得"""
        return self.level_system.get_current_config()
        
    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                # F11で全画面/ウィンドウ切り替え
                if event.key == pygame.K_F11:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        # デスクトップ解像度で全画面（アスペクト比維持せず黒帯なし）
                        new_width = self.desktop_width
                        new_height = self.desktop_height
                        self.set_screen(new_width, new_height, fullscreen=True)
                    else:
                        # ウィンドウモード（アスペクト比維持）
                        aspect_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
                        new_width = self.desktop_width
                        new_height = int(new_width / aspect_ratio)
                        if new_height > self.desktop_height:
                            new_height = self.desktop_height
                            new_width = int(new_height * aspect_ratio)
                        self.set_screen(new_width, new_height, fullscreen=False)
                    # UI再描画用にアップグレード画面のscreenも更新
                    self.level_up_upgrade_screen.screen = self.screen

            if self.game_state == "TITLE":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_button and self.start_button.collidepoint(event.pos):
                        self.reset_game()
                        if self.sound_manager:
                            self.sound_manager.play_music()
                    elif self.upgrade_button and self.upgrade_button.collidepoint(event.pos):
                        self.game_state = "UPGRADE"
                    elif self.quit_button and self.quit_button.collidepoint(event.pos):
                        return False
            
            if event.type == pygame.KEYDOWN:
                if self.game_state == "TITLE":
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                        if self.sound_manager:
                            self.sound_manager.play_music()

                elif self.game_state == "PLAYING":
                    if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        self.is_paused = not self.is_paused
                    elif event.key == pygame.K_q and self.is_paused:
                        # 一時停止中にQキーでタイトル画面に戻る
                        self.game_state = "TITLE"
                        self.is_paused = False
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
                                # 必殺技発動時の全消去は削除（範囲内の弾のみ消去）
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
        
        # デバッグ: レベル4以降で弾幕敵の利用可能性をチェック
        if self.level_system.current_level >= 4:
            available_enemies = current_level_config.get('enemy_types', [])
            if 'barrage' in available_enemies:
                print(f"Level {self.level_system.current_level}: Barrage enemy is available in {available_enemies}")
            else:
                print(f"Level {self.level_system.current_level}: Barrage enemy NOT available in {available_enemies}")
        
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
                # ボス戦突入時に道中の敵を全て消滅させる
                self.enemies.clear()
        
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
        
        # デバッグ: 敵の弾の数を表示（必要に応じて）
        # print(f"Enemy bullets: {len(self.enemy_bullets)}")
        
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
                enemy_x = random.randint(ENEMY_SIZE, self.current_width - ENEMY_SIZE)
                
                # レベル設定を敵生成に渡す
                enemy = EnemyFactory.create_random_enemy(enemy_x, -ENEMY_SIZE, self.player, current_level_config, game=self)
                self.enemies.append(enemy)
                
                # デバッグ: 弾幕敵が生成されたかチェック
                if hasattr(enemy, 'enemy_type') and enemy.enemy_type == "barrage":
                    print(f"Barrage enemy spawned at level {self.level_system.current_level}")
            
            # 敵の編隊生成（レベル設定を適用）
            self.wave_spawn_timer += 1
            if self.wave_spawn_timer >= self.wave_spawn_interval:
                self.wave_spawn_timer = 0
                self.spawn_enemy_wave(current_level_config)
        
        # パワーアップの生成
        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer >= POWERUP_SPAWN_RATE:
            self.powerup_spawn_timer = 0
            powerup_x = random.randint(POWERUP_SIZE, self.current_width - POWERUP_SIZE)
            powerup_type = random.choice(POWERUP_TYPES)
            powerup = PowerUp(powerup_x, -POWERUP_SIZE, powerup_type, game=self)
            self.powerups.append(powerup)
        
        # 敵の更新
        for enemy in self.enemies[:]:
            new_bullets = enemy.update()  # 戻り値を修正
            if new_bullets:  # 弾が生成された場合
                # 単一のBulletオブジェクトかリストかをチェック
                if isinstance(new_bullets, list):
                    self.enemy_bullets.extend(new_bullets)  # リストの場合
                else:
                    self.enemy_bullets.append(new_bullets)  # 単一オブジェクトの場合
                # デバッグ: 敵が弾を撃ったかチェック
                if hasattr(enemy, 'enemy_type'):
                    print(f"{enemy.enemy_type} enemy fired bullets")
            
            # 敵が画面外に出たら削除
            if not enemy.active:
                self.enemies.remove(enemy)
                # デバッグ: 弾幕敵が削除されたかチェック
                if hasattr(enemy, 'enemy_type') and enemy.enemy_type == "barrage":
                    print(f"Barrage enemy removed at y={enemy.y}")
            elif enemy.should_shoot() and random.random() < 0.3:  # 既存の処理も残す
                # スナイパー敵の場合は狙い撃ち
                if isinstance(enemy, SniperEnemy):
                    enemy_bullet = enemy.shoot(self.player.x, self.player.y)
                else:
                    enemy_bullet = enemy.shoot()
                self.enemy_bullets.append(enemy_bullet)
                # デバッグ: 既存の射撃処理で弾が生成されたかチェック
                if hasattr(enemy, 'enemy_type'):
                    print(f"{enemy.enemy_type} enemy fired bullet (legacy method)")
        
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
        
        start_x = random.randint(100, self.current_width - 100)
        start_y = -50
        
        # レベル設定を編隊生成に渡す
        wave_enemies = EnemyFactory.create_enemy_wave(wave_type, start_x, start_y, self.player, level_config, game=self)
        self.enemies.extend(wave_enemies)
        
        # デバッグ: 編隊内の弾幕敵をチェック
        for enemy in wave_enemies:
            if hasattr(enemy, 'enemy_type') and enemy.enemy_type == "barrage":
                print(f"Barrage enemy spawned in wave '{wave_type}' at level {self.level_system.current_level}")
    
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
                                self.level_up_upgrade_screen.start_selection(self.player)
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
                    if hasattr(bullet, 'penetrating') and bullet.penetrating:
                        # レーザーの場合はボスに当たったら1ヒットで消す
                        if hasattr(bullet, 'hit_boss_once'):
                            bullet.hit_boss_once()
                    else:
                        self.bullets.remove(bullet)
                    # ボスにダメージを与える
                    damage = getattr(bullet, 'damage', 1)
                    was_destroyed = current_boss.take_damage(damage)
                    # ダメージ数値を生成
                    self.damage_numbers.append(DamageNumber(current_boss.x, current_boss.y, damage, self.small_font, RED))
                    if was_destroyed:
                        # ボス撃破時の処理
                        self.score += current_boss.score_value
                        self.lives += 1  # ボス撃破で残機を1つ増やす
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
            if bullet.active and check_collision(bullet.rect, self.player.rect):
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
            if bullet.active and check_collision(bullet.rect, self.player.rect):
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

            # MasterSparkのビーム範囲に当たっている敵弾・ボス弾だけを消す
            if hasattr(attack, 'rect') and isinstance(attack, MasterSpark):
                # MasterSparkの範囲内の弾のみを消去
                self.clear_bullets_in_master_spark_range(attack)

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
        # 全画面時は黒い背景で塗りつぶし
        if self.fullscreen:
            self.screen.fill(BLACK)
        
        # 背景画像のスクロール描画（ゲームビューポート内に制限）
        bg_scaled = pygame.transform.scale(self.background_image, (self.current_width, self.current_height))
        for x in range(0, self.current_width, bg_scaled.get_width()):
            y1 = self.scroll_y
            y2 = self.scroll_y - self.current_height
            # ゲームビューポート内に描画
            self.screen.blit(bg_scaled, (x + self.game_viewport.x, y1 + self.game_viewport.y))
            self.screen.blit(bg_scaled, (x + self.game_viewport.x, y2 + self.game_viewport.y))

        if self.game_state == "TITLE":
            # タイトルとボタンを画面比率に応じて配置
            # タイトル
            draw_text_relative(self.screen, "Space Shooter", 0.5, 0.22, self.font, WHITE, anchor="center")
            
            # ボタン配置（画面比率に応じてサイズと位置を調整）
            button_width_percent = 0.3  # 画面幅の30%
            button_height_percent = 0.1  # 画面高さの10%
            button_gap_percent = 0.05    # 画面高さの5%
            
            # ボタンの位置を計算
            start_y_percent = 0.45
            upgrade_y_percent = start_y_percent + button_height_percent + button_gap_percent
            quit_y_percent = upgrade_y_percent + button_height_percent + button_gap_percent
            
            # ボタンを作成
            self.start_button = create_adaptive_button(
                self.screen, "Start", 0.35, start_y_percent, 
                button_width_percent, button_height_percent, self.font
            )
            self.upgrade_button = create_adaptive_button(
                self.screen, "Upgrade", 0.35, upgrade_y_percent, 
                button_width_percent, button_height_percent, self.font
            )
            self.quit_button = create_adaptive_button(
                self.screen, "Quit", 0.35, quit_y_percent, 
                button_width_percent, button_height_percent, self.font
            )

        elif self.game_state == "PLAYING" or self.is_paused:
            # --- ゲーム要素の描画 ---
            # ゲームビューポート内に描画するため、一時的なサブサーフェスを作成
            if self.fullscreen:
                game_surface = pygame.Surface((self.current_width, self.current_height))
                game_surface.set_colorkey((0, 0, 0))  # 透明色を設定
            else:
                game_surface = self.screen
            
            self.player.draw(game_surface)

            for bullet in self.bullets:
                bullet.draw(game_surface)

            for bullet in self.enemy_bullets:
                if bullet.active:
                    bullet.draw(game_surface)

            # ボス弾の描画
            for bullet in self.boss_bullets:
                if bullet.active:
                    bullet.draw(game_surface)

            for enemy in self.enemies:
                enemy.draw(game_surface)

            # ボスの描画
            current_boss = self.boss_manager.get_current_boss()
            if current_boss:
                current_boss.draw(game_surface)
                # ボスのHPバーとスペルカード名を描画
                draw_boss_health_bar(game_surface, current_boss, self.font)
                draw_boss_spell_card_name(game_surface, current_boss, self.font)

            for powerup in self.powerups:
                powerup.draw(game_surface)

            for attack in self.special_attacks:
                attack.draw(game_surface)

            # マスタースパークがアクティブな場合、敵にアウトラインを描画
            for attack in self.special_attacks:
                if isinstance(attack, MasterSpark):
                    for enemy in self.enemies:
                        if check_collision(attack.rect, enemy.rect):
                            enemy.draw_outline(game_surface, YELLOW, 2) # 黄色いアウトライン
                    current_boss = self.boss_manager.get_current_boss()
                    if current_boss and check_collision(attack.rect, current_boss.rect):
                        current_boss.draw_outline(game_surface, YELLOW, 3) # ボスには太いアウトライン

            # パーティクルの描画
            draw_particles(game_surface, self.particles)

            # ダメージ数値の描画
            for dn in self.damage_numbers:
                dn.draw(game_surface)
            
            # 全画面時はゲームサーフェスをメインスクリーンに描画
            if self.fullscreen:
                self.screen.blit(game_surface, self.game_viewport)

            # --- UI の描画 ---
            # UI要素は全画面時でもメインスクリーンに直接描画（ビューポート外でも表示）
            draw_score(self.screen, self.score, self.font)
            draw_lives(self.screen, self.lives, self.font)
            draw_powerups(self.screen, self.player, self.small_font)
            # draw_enemy_info(self.screen, self.enemies, self.small_font)
            draw_level_info(self.screen, self.level_system, self.font, self.small_font)
            # draw_stats_panel(self.screen, self.level_system, self.font, self.small_font)
            # draw_difficulty_info(self.screen, self.level_system, self.font, self.small_font)

            # 必殺技ゲージの描画
            draw_special_gauge(self.screen, self.player, self.font)

            # サウンド状態表示と武器情報
            draw_sound_status(self.screen, self.sound_manager, self.small_font)
            draw_weapon_status(self.screen, self.player, self.small_font)

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
            draw_score(self.screen, self.score, self.font)
            draw_lives(self.screen, self.lives, self.font)
            draw_powerups(self.screen, self.player, self.small_font)
            # draw_enemy_info(self.screen, self.enemies, self.small_font)
            draw_level_info(self.screen, self.level_system, self.font, self.small_font)
            # draw_stats_panel(self.screen, self.level_system, self.font, self.small_font)
            # draw_difficulty_info(self.screen, self.level_system, self.small_font)
            draw_special_gauge(self.screen, self.player, self.font)
            draw_sound_status(self.screen, self.sound_manager, self.small_font)
            draw_weapon_status(self.screen, self.player, self.small_font)

            # --- アップグレード選択画面を最前面に描画 ---
            self.level_up_upgrade_screen.draw()

        elif self.game_state == "GAME_OVER":
            # ゲームオーバー画面
            draw_game_over_screen(self.screen, self.score, self.font)

        elif self.game_state == "STAGE_CLEAR":
            draw_stage_clear(self.screen, self.font)

        # FPS表示（画面右上に目立つように表示）
        self.draw_fps_display()
        
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
            
            # FPS固定制御
            self.maintain_fixed_fps()
            
            # 従来のFPS制御（フォールバック）
            if not FIXED_FPS:
                self.clock.tick(FPS)
        
        self.save_upgrade_data()
        # クリーンアップ
        if self.sound_manager:
            self.sound_manager.stop_music()
        pygame.quit()
        sys.exit()

    def set_screen(self, width, height, fullscreen):
        """画面サイズ・スケール・ボタンを再計算（アスペクト比維持と黒帯処理）"""
        try:
            # 基本的なフラグを設定
            flags = pygame.DOUBLEBUF
            
            # 全画面モードの設定
            if fullscreen:
                # 全画面フラグを設定（SCALEDは使用しない）
                flags |= pygame.FULLSCREEN
                
                # アスペクト比を維持した画面サイズを計算
                target_aspect = self.original_aspect_ratio
                if width / height > target_aspect:
                    # 幅が広い場合、高さに合わせて幅を調整
                    new_height = height
                    new_width = int(height * target_aspect)
                    offset_x = (width - new_width) // 2
                    offset_y = 0
                else:
                    # 高さが高い場合、幅に合わせて高さを調整
                    new_width = width
                    new_height = int(width / target_aspect)
                    offset_x = 0
                    offset_y = (height - new_height) // 2
                
                self.game_viewport = pygame.Rect(offset_x, offset_y, new_width, new_height)
                self.screen_scale_x = new_width / SCREEN_WIDTH
                self.screen_scale_y = new_height / SCREEN_HEIGHT
                self.current_width = new_width
                self.current_height = new_height
            else:
                # ウィンドウモード時は通常通り
                self.game_viewport = pygame.Rect(0, 0, width, height)
                self.screen_scale_x = width / SCREEN_WIDTH
                self.screen_scale_y = height / SCREEN_HEIGHT
                self.current_width = width
                self.current_height = height
            
            # 画面モードを設定（エラーハンドリング付き）
            try:
                self.screen = pygame.display.set_mode((width, height), flags)
            except pygame.error as e:
                print(f"画面設定エラー: {e}")
                # フォールバック: 基本的な設定で再試行
                fallback_flags = pygame.DOUBLEBUF
                if fullscreen:
                    fallback_flags |= pygame.FULLSCREEN
                
                try:
                    self.screen = pygame.display.set_mode((width, height), fallback_flags)
                except pygame.error as e2:
                    print(f"フォールバック画面設定も失敗: {e2}")
                    # 最後の手段: デフォルトサイズでウィンドウモード
                    self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    self.game_viewport = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
                    self.screen_scale_x = 1.0
                    self.screen_scale_y = 1.0
                    self.current_width = SCREEN_WIDTH
                    self.current_height = SCREEN_HEIGHT
                    self.fullscreen = False
            
            # プレイヤーとボタンの更新
            if hasattr(self, 'player') and self.player:
                self.player.game = self
            if hasattr(self, 'create_buttons'):
                self.create_buttons()
                
        except Exception as e:
            print(f"画面設定で予期しないエラー: {e}")
            # エラーが発生した場合はデフォルト設定を使用
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.game_viewport = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
            self.screen_scale_x = 1.0
            self.screen_scale_y = 1.0
            self.current_width = SCREEN_WIDTH
            self.current_height = SCREEN_HEIGHT
            self.fullscreen = False

    def create_buttons(self):
        """画面比率に応じたボタンRectを再計算"""
        # ボタンは描画時に動的に作成されるため、ここでは何もしない
        # 画面サイズ変更時は次回の描画で自動的に再計算される
        pass
    
    def draw_fps_display(self):
        """画面右上にFPSを表示"""
        try:
            # FPS固定が有効な場合は実際のFPSを取得、そうでなければ従来の方法
            if FIXED_FPS:
                fps = int(self.get_actual_fps())
            else:
                fps = int(self.clock.get_fps())
            
            # utils.pyのdraw_fps_counter関数を使用してFPSを表示
            from utils import draw_fps_counter
            draw_fps_counter(self.screen, fps, self.small_font, position="topright")
            
        except Exception as e:
            # FPS表示でエラーが発生した場合は何もしない
            pass

    def clear_bullets_in_master_spark_range(self, master_spark):
        """MasterSparkの範囲内の弾のみを消去"""
        try:
            # MasterSparkの範囲を取得
            spark_rect = master_spark.rect
            
            # 敵弾の範囲内チェック
            bullets_to_remove = []
            for bullet in self.enemy_bullets:
                if bullet.active and self.is_bullet_in_master_spark_range(bullet, master_spark):
                    bullets_to_remove.append(bullet)
            
            # 範囲内の敵弾を削除し、エフェクトを追加
            for bullet in bullets_to_remove:
                if bullet in self.enemy_bullets:
                    # 弾消去エフェクトを生成
                    from utils import create_bullet_clear_effect
                    clear_effect = create_bullet_clear_effect(bullet.x, bullet.y, color=YELLOW)
                    self.particles.extend(clear_effect)
                    self.enemy_bullets.remove(bullet)
            
            # ボス弾の範囲内チェック
            boss_bullets_to_remove = []
            for bullet in self.boss_bullets:
                if bullet.active and self.is_bullet_in_master_spark_range(bullet, master_spark):
                    boss_bullets_to_remove.append(bullet)
            
            # 範囲内のボス弾を削除し、エフェクトを追加
            for bullet in boss_bullets_to_remove:
                if bullet in self.boss_bullets:
                    # 弾消去エフェクトを生成
                    from utils import create_bullet_clear_effect
                    clear_effect = create_bullet_clear_effect(bullet.x, bullet.y, color=RED)
                    self.particles.extend(clear_effect)
                    self.boss_bullets.remove(bullet)
                    
        except Exception as e:
            print(f"MasterSpark範囲内弾消去エラー: {e}")
    
    def is_bullet_in_master_spark_range(self, bullet, master_spark):
        """弾がMasterSparkの範囲内にあるかチェック"""
        try:
            # MasterSparkの範囲判定メソッドを使用
            if hasattr(master_spark, 'is_point_in_range'):
                # 弾の中心座標が範囲内かチェック
                return master_spark.is_point_in_range(bullet.x, bullet.y)
            else:
                # フォールバック: 矩形での判定
                spark_rect = master_spark.rect
                if hasattr(bullet, 'rect'):
                    return check_collision(bullet.rect, spark_rect)
                else:
                    return (spark_rect.left <= bullet.x <= spark_rect.right and 
                           0 <= bullet.y <= spark_rect.bottom)
                
        except Exception as e:
            print(f"弾範囲チェックエラー: {e}")
            return False
    
    def maintain_fixed_fps(self):
        """FPSを60に固定する"""
        if not FIXED_FPS:
            return
        
        try:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.last_frame_time
            
            # 目標フレーム時間（60FPS = 約16.67ms）
            target_frame_time = MIN_FRAME_TIME * 1000  # ミリ秒に変換
            
            # フレーム時間が短すぎる場合は待機
            if elapsed_time < target_frame_time:
                sleep_time = target_frame_time - elapsed_time
                pygame.time.wait(int(sleep_time))
            
            # フレーム時間を更新
            self.last_frame_time = pygame.time.get_ticks()
            
            # FPS計測（1秒ごと）
            self.frame_count += 1
            if current_time - self.fps_start_time >= 1000:  # 1秒経過
                actual_fps = self.frame_count
                self.frame_count = 0
                self.fps_start_time = current_time
                
                # FPSが目標値から大きく外れている場合は警告
                if abs(actual_fps - FPS) > FPS_TOLERANCE:
                    print(f"FPS警告: 目標={FPS}, 実際={actual_fps}")
                    
        except Exception as e:
            print(f"FPS制御エラー: {e}")
    
    def get_actual_fps(self):
        """現在の実際のFPSを取得"""
        try:
            if self.frame_count > 0:
                current_time = pygame.time.get_ticks()
                elapsed_time = (current_time - self.fps_start_time) / 1000.0  # 秒に変換
                if elapsed_time > 0:
                    return self.frame_count / elapsed_time
            return 0
        except Exception as e:
            print(f"FPS取得エラー: {e}")
            return 0

if __name__ == "__main__":
    try:
        # pygameの初期化を確認
        if not pygame.get_init():
            pygame.init()
        
        # ディスプレイモジュールの初期化を確認
        if not pygame.display.get_init():
            pygame.display.init()
        
        # ゲームを開始
        game = Game()
        game.run()
        
    except Exception as e:
        print(f"ゲーム起動エラー: {e}")
        import traceback
        traceback.print_exc()
        
        # pygameのクリーンアップ
        try:
            pygame.quit()
        except:
            pass
        
        sys.exit(1)