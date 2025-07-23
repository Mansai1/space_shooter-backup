import random
from settings import *
from enemy.basic_enemy import BasicEnemy
from enemy.fast_enemy import FastEnemy
from enemy.tankEnemy import TankEnemy
from enemy.zigzagEnemy import ZigzagEnemy
from enemy.sniperEnemy import SniperEnemy
from enemy.shieldEnemy import ShieldEnemy
from enemy.stopperEnemy import StopperEnemy
from enemy.kamikazeEnemy import KamikazeEnemy
from enemy.barrage_enemy import BarrageEnemy

class EnemyFactory:
    """敵生成のファクトリークラス"""
    
    # 敵タイプとクラスのマッピング
    ENEMY_CLASSES = {
        'basic': BasicEnemy,
        'fast': FastEnemy,
        'tank': TankEnemy,
        'zigzag': ZigzagEnemy,
        'sniper': SniperEnemy,
        'shield': ShieldEnemy,
        'stopper': StopperEnemy,
        'kamikaze': KamikazeEnemy,
        'barrage': BarrageEnemy
    }
    
    @classmethod
    def create_enemy(cls, enemy_type, x, y, player, level_config=None, game=None, **kwargs):
        """指定されたタイプの敵を生成"""
        # レベル設定から倍率を取得
        level_multipliers = None
        if level_config:
            level_multipliers = {
                'health': level_config.get('enemy_health_multiplier', 1.0),
                'speed': level_config.get('enemy_speed_multiplier', 1.0)
            }
        
        enemy_class = cls.ENEMY_CLASSES.get(enemy_type, BasicEnemy)
        
        return enemy_class(x, y, player, level_multipliers=level_multipliers, game=game, **kwargs)
    
    @classmethod
    def create_random_enemy(cls, x, y, player, level_config=None, game=None):
        """レベル設定に基づいてランダムな敵を生成"""
        if level_config:
            available_types = level_config.get('enemy_types', ['basic'])
        else:
            available_types = ['basic']
        
        enemy_type = random.choice(available_types)
        
        return cls.create_enemy(enemy_type, x, y, player, level_config, game=game)
    
    @classmethod
    def create_enemy_wave(cls, wave_type, start_x, start_y, player, level_config=None, game=None):
        """レベル設定に基づいて敵の編隊を生成"""
        enemies = []
        width = game.current_width if game else SCREEN_WIDTH
        
        if wave_type == "basic_line":
            # 基本的な一列編隊
            for i in range(5):
                x = start_x + (i - 2) * 60
                if 0 <= x <= width:
                    enemy = cls.create_enemy('basic', x, start_y, player, level_config, game=game)
                    enemies.append(enemy)
                    
        elif wave_type == "speed_rush":
            # 高速敵の突撃
            for i in range(3):
                x = start_x + (i - 1) * 80
                if 0 <= x <= width:
                    enemy = cls.create_enemy('fast', x, start_y - i * 30, player, level_config, game=game)
                    enemies.append(enemy)
                    
        elif wave_type == "zigzag_formation":
            # ジグザグ敵の編隊
            if level_config and 'zigzag' in level_config.get('enemy_types', []):
                for i in range(4):
                    x = start_x + (i - 1.5) * 70
                    if 0 <= x <= width:
                        enemy = cls.create_enemy('zigzag', x, start_y - i * 20, player, level_config, game=game)
                        enemies.append(enemy)
                        
        elif wave_type == "mixed_assault":
            # 混合編隊
            if level_config:
                available_types = level_config.get('enemy_types', ['basic'])
                for i in range(6):
                    x = start_x + (i - 2.5) * 50
                    if 0 <= x <= width:
                        enemy_type = random.choice(available_types)
                        enemy = cls.create_enemy(enemy_type, x, start_y - (i % 2) * 25, player, level_config, game=game)
                        enemies.append(enemy)
                        
        elif wave_type == "tank_formation":
            # タンク編隊
            if level_config and 'tank' in level_config.get('enemy_types', []):
                for i in range(3):
                    x = start_x + (i - 1) * 100
                    if 0 <= x <= width:
                        enemy = cls.create_enemy('tank', x, start_y, player, level_config, game=game)
                        enemies.append(enemy)
                        
        elif wave_type == "shield_wall":
            # シールド敵の壁
            if level_config and 'shield' in level_config.get('enemy_types', []):
                for i in range(4):
                    x = start_x + (i - 1.5) * 60
                    if 0 <= x <= width:
                        enemy = cls.create_enemy('shield', x, start_y, player, level_config, game=game)
                        enemies.append(enemy)
                        
        elif wave_type == "stopper_ambush":
            # ストッパー敵の待ち伏せ
            if level_config and 'stopper' in level_config.get('enemy_types', []):
                positions = [start_x - 80, start_x, start_x + 80]
                for i, x in enumerate(positions):
                    if 0 <= x <= width:
                        enemy = cls.create_enemy('stopper', x, start_y - i * 40, player, level_config, game=game)
                        enemies.append(enemy)
                        
        elif wave_type == "sniper_overwatch":
            # スナイパー敵の狙撃陣形
            if level_config and 'sniper' in level_config.get('enemy_types', []):
                positions = [start_x - 120, start_x + 120]
                for x in positions:
                    if 0 <= x <= width:
                        enemy = cls.create_enemy('sniper', x, start_y, player, level_config, game=game)
                        enemies.append(enemy)
                        
        elif wave_type == "kamikaze_rush":
            # カミカゼ敵の突撃
            if level_config and 'kamikaze' in level_config.get('enemy_types', []):
                for i in range(5):
                    x = start_x + (i - 2) * 40
                    if 0 <= x <= width:
                        enemy = cls.create_enemy('kamikaze', x, start_y - i * 15, player, level_config, game=game)
                        enemies.append(enemy)
                        
        elif wave_type == "barrage_assault":
            # 弾幕敵の攻撃
            if level_config and 'barrage' in level_config.get('enemy_types', []):
                # 弾幕敵は単体で出現（強力なため）
                enemy = cls.create_enemy('barrage', start_x, start_y, player, level_config, game=game)
                enemies.append(enemy)
                        
        elif wave_type == "fortress_formation":
            # 要塞編隊（タンクを中心にシールドで守る）
            if (level_config and 'tank' in level_config.get('enemy_types', []) 
                and 'shield' in level_config.get('enemy_types', [])):
                # 中央にタンク
                tank = cls.create_enemy('tank', start_x, start_y, player, level_config, game=game)
                enemies.append(tank)
                
                # 周囲にシールド敵
                shield_positions = [
                    (start_x - 60, start_y - 30),
                    (start_x + 60, start_y - 30),
                    (start_x - 60, start_y + 30),
                    (start_x + 60, start_y + 30)
                ]
                for x, y in shield_positions:
                    if 0 <= x <= width:
                        enemy = cls.create_enemy('shield', x, y, player, level_config, game=game)
                        enemies.append(enemy)
                        
        elif wave_type == "pincer_attack":
            # 挟み撃ち編隊
            if level_config:
                available_types = level_config.get('enemy_types', ['basic'])
                
                # 左右から攻撃
                left_x = max(50, start_x - 200)
                right_x = min(width - 50, start_x + 200)
                
                for i in range(3):
                    enemy_type = random.choice(available_types)
                    
                    # 左側編隊
                    enemy_left = cls.create_enemy(enemy_type, left_x, start_y - i * 40, player, level_config, game=game)
                    enemies.append(enemy_left)
                    
                    # 右側編隊
                    enemy_type = random.choice(available_types)
                    enemy_right = cls.create_enemy(enemy_type, right_x, start_y - i * 40, player, level_config, game=game)
                    enemies.append(enemy_right)
        
        return enemies
    
    @classmethod
    def get_wave_types_for_level(cls, level_config):
        """レベル設定に基づいて使用可能な編隊タイプを取得"""
        if not level_config:
            return ["basic_line"]
        
        available_types = level_config.get('enemy_types', ['basic'])
        wave_types = ["basic_line", "mixed_assault"]
        
        # 敵タイプに応じて編隊を追加
        if 'fast' in available_types:
            wave_types.append("speed_rush")
        if 'zigzag' in available_types:
            wave_types.append("zigzag_formation")
        if 'tank' in available_types:
            wave_types.append("tank_formation")
        if 'shield' in available_types:
            wave_types.append("shield_wall")
        if 'stopper' in available_types:
            wave_types.append("stopper_ambush")
        if 'sniper' in available_types:
            wave_types.append("sniper_overwatch")
        if 'kamikaze' in available_types:
            wave_types.append("kamikaze_rush")
        if 'barrage' in available_types:
            wave_types.append("barrage_assault")
        if 'tank' in available_types and 'shield' in available_types:
            wave_types.append("fortress_formation")
        if len(available_types) >= 3:
            wave_types.append("pincer_attack")
            
        return wave_types