import math
from settings import *

class LevelSystem:
    def __init__(self):
        self.current_level = 1
        self.experience = 0
        self.experience_to_next_level = 100
        self.total_enemies_defeated = 0
        self.level_start_time = 0
        
        # レベル別設定
        self.level_configs = {
            1: {
                'enemy_spawn_rate': 60,
                'enemy_speed_multiplier': 1.0,
                'enemy_health_multiplier': 1.0,
                'powerup_spawn_rate': 600,
                'wave_spawn_interval': 300,
                'enemy_types': ['basic', 'fast'],
                'max_enemies_on_screen': 8,
                'experience_multiplier': 1.0,  # レベル1の経験値倍率
                'description': 'チュートリアル - ノーマルエネミーのみ'
            },
            2: {
                'enemy_spawn_rate': 55,
                'enemy_speed_multiplier': 1.1,
                'enemy_health_multiplier': 1.0,
                'powerup_spawn_rate': 550,
                'wave_spawn_interval': 280,
                'enemy_types': ['basic', 'fast', 'tank'],
                'max_enemies_on_screen': 10,
                'experience_multiplier': 1.1,  # レベル2の経験値倍率
                'description': 'タンクエネミーが登場'
            },
            3: {
                'enemy_spawn_rate': 50,
                'enemy_speed_multiplier': 1.2,
                'enemy_health_multiplier': 1.1,
                'powerup_spawn_rate': 500,
                'wave_spawn_interval': 260,
                'enemy_types': ['basic', 'fast', 'tank', 'zigzag', 'kamikaze'],
                'max_enemies_on_screen': 12,
                'experience_multiplier': 1.2,  # レベル3の経験値倍率
                'description': 'ジグザグエネミー＆イノシシエネミーが登場'
            },
            4: {
                'enemy_spawn_rate': 45,
                'enemy_speed_multiplier': 1.3,
                'enemy_health_multiplier': 1.2,
                'powerup_spawn_rate': 450,
                'wave_spawn_interval': 240,
                'enemy_types': ['basic', 'fast', 'tank', 'zigzag', 'kamikaze', 'sniper', 'barrage'],
                'max_enemies_on_screen': 14,
                'experience_multiplier': 1.3,  # レベル4の経験値倍率
                'description': 'スナイパー＆弾幕エネミーが登場'
            },
            5: {
                'enemy_spawn_rate': 40,
                'enemy_speed_multiplier': 1.4,
                'enemy_health_multiplier': 1.3,
                'powerup_spawn_rate': 400,
                'wave_spawn_interval': 220,
                'enemy_types': ['basic', 'fast', 'tank', 'zigzag', 'kamikaze', 'sniper', 'shield', 'barrage'],
                'max_enemies_on_screen': 16,
                'experience_multiplier': 1.4,  # レベル5の経験値倍率
                'description': 'シールドエネミーが登場'
            },
            6: {
                'enemy_spawn_rate': 35,
                'enemy_speed_multiplier': 1.5,
                'enemy_health_multiplier': 1.4,
                'powerup_spawn_rate': 350,
                'wave_spawn_interval': 200,
                'enemy_types': ['basic', 'fast', 'tank', 'zigzag', 'kamikaze', 'sniper', 'shield', 'stopper', 'barrage'],
                'max_enemies_on_screen': 18,
                'experience_multiplier': 1.5,  # レベル6の経験値倍率
                'description': 'ストッパーエネミーが登場'
            }
        }
        
        # レベル6以降の無限レベル設定
        self.infinite_level_base = {
            'enemy_spawn_rate': 30,
            'enemy_speed_multiplier': 1.6,
            'enemy_health_multiplier': 1.5,
            'powerup_spawn_rate': 300,
            'wave_spawn_interval': 180,
            'enemy_types': ['basic', 'fast', 'tank', 'zigzag', 'kamikaze', 'sniper', 'shield', 'stopper', 'barrage'],
            'max_enemies_on_screen': 20,
            'experience_multiplier': 1.6,  # レベル7以降のベース経験値倍率
            'description': 'エンドレスモード'
        }
    
    def add_experience(self, base_exp_points):
        """経験値を追加（レベル倍率適用）"""
        if base_exp_points > 0:
            # 現在のレベル設定から経験値倍率を取得
            current_config = self.get_current_config()
            multiplier = current_config.get('experience_multiplier', 1.0)
            
            # 倍率を適用した経験値を計算
            actual_exp = int(base_exp_points * multiplier)
            self.experience += actual_exp
            
            # デバッグ用（必要に応じてコメントアウト）
            print(f"Base EXP: {base_exp_points}, Multiplier: {multiplier:.1f}, Actual EXP: {actual_exp}")
        
        # レベルアップチェック
        leveled_up = False
        while self.experience >= self.experience_to_next_level:
            self.level_up()
            leveled_up = True
        
        return leveled_up
    
    def level_up(self):
        """レベルアップ処理"""
        self.experience -= self.experience_to_next_level
        self.current_level += 1
        
        # 次のレベルに必要な経験値を計算（指数関数的に増加）
        self.experience_to_next_level = int(100 * (1.5 ** (self.current_level - 1)))
        
        print(f"Level Up! New Level: {self.current_level}")  # デバッグ用
        return True  # レベルアップが発生したことを通知
    
    def get_current_config(self):
        """現在のレベル設定を取得"""
        if self.current_level <= 6:
            return self.level_configs[self.current_level].copy()
        else:
            # レベル6以降は無限レベル設定をベースに難易度を上げる
            config = self.infinite_level_base.copy()
            extra_levels = self.current_level - 6
            
            # 追加レベルに応じて難易度を上げる
            config['enemy_spawn_rate'] = max(15, config['enemy_spawn_rate'] - extra_levels * 2)
            config['enemy_speed_multiplier'] += extra_levels * 0.1
            config['enemy_health_multiplier'] += extra_levels * 0.1
            config['powerup_spawn_rate'] = max(180, config['powerup_spawn_rate'] - extra_levels * 10)
            config['wave_spawn_interval'] = max(120, config['wave_spawn_interval'] - extra_levels * 5)
            config['max_enemies_on_screen'] = min(30, config['max_enemies_on_screen'] + extra_levels)
            
            # レベルが上がるほど経験値倍率も増加（最大3.0倍まで）
            config['experience_multiplier'] = min(5.0, config['experience_multiplier'] + extra_levels * 0.1)
            config['description'] = f'エンドレスモード - レベル {self.current_level} (EXP x{config["experience_multiplier"]:.1f})'
            
            return config
    
    def get_enemy_score_multiplier(self):
        """レベルに応じたスコア倍率を取得"""
        return 1.0 + (self.current_level - 1) * 0.2
    
    def get_experience_multiplier(self):
        """現在の経験値倍率を取得"""
        current_config = self.get_current_config()
        return current_config.get('experience_multiplier', 1.0)
    
    def calculate_experience_gain(self, base_experience, enemy_type='basic'):
        """敵タイプとレベルに応じた経験値を計算"""
        # 敵タイプ別の経験値補正
        enemy_exp_multipliers = {
            'basic': 1.0,
            'fast': 1.1,
            'tank': 1.3,
            'zigzag': 1.2,
            'kamikaze': 1.4,
            'sniper': 1.5,
            'shield': 1.6,
            'stopper': 1.8,
            'boss': 10.0  # ボスは大幅に高い経験値
        }
        
        # 基本経験値 × 敵タイプ補正 × レベル倍率
        enemy_multiplier = enemy_exp_multipliers.get(enemy_type, 1.0)
        level_multiplier = self.get_experience_multiplier()
        
        return int(base_experience * enemy_multiplier * level_multiplier)
    
    def should_spawn_boss(self):
        """ボス出現判定（将来の拡張用）"""
        # 5レベルごとにボス出現の可能性
        return self.current_level % 5 == 0 and self.total_enemies_defeated % 50 == 0
    
    def get_level_progress(self):
        """レベル進行度を0-1で取得"""
        return self.experience / self.experience_to_next_level
    
    def get_experience_info(self):
        """経験値情報を取得（UI表示用）"""
        return {
            'current_exp': self.experience,
            'next_level_exp': self.experience_to_next_level,
            'progress': self.get_level_progress(),
            'multiplier': self.get_experience_multiplier()
        }
    
    def reset(self):
        """レベルシステムをリセット"""
        self.current_level = 1
        self.experience = 0
        self.experience_to_next_level = 100
        self.total_enemies_defeated = 0
        self.level_start_time = 0

    def next_level(self):
        self.current_level += 1
        self.experience = 0
        self.experience_to_next_level = int(100 * (1.5 ** (self.current_level - 1)))

class DifficultyManager:
    """難易度調整マネージャー"""
    
    @staticmethod
    def apply_level_config(game_objects, level_config):
        """レベル設定をゲームオブジェクトに適用"""
        # 敵の生成頻度を調整
        if hasattr(game_objects, 'enemy_spawn_rate'):
            game_objects.enemy_spawn_rate = level_config['enemy_spawn_rate']
        
        # 編隊出現間隔を調整
        if hasattr(game_objects, 'wave_spawn_interval'):
            game_objects.wave_spawn_interval = level_config['wave_spawn_interval']
        
        # パワーアップ出現頻度を調整
        if hasattr(game_objects, 'powerup_spawn_rate'):
            game_objects.powerup_spawn_rate = level_config['powerup_spawn_rate']
    
    @staticmethod
    def get_scaled_enemy_stats(base_health, base_speed, level_config):
        """レベルに応じて敵のステータスをスケール"""
        health = int(base_health * level_config['enemy_health_multiplier'])
        speed = base_speed * level_config['enemy_speed_multiplier']
        return health, speed
    
    @staticmethod
    def should_limit_enemies(current_enemy_count, level_config):
        """敵の数制限チェック"""
        return current_enemy_count >= level_config['max_enemies_on_screen']