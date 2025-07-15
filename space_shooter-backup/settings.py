import pygame

# 画面設定
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 色定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GOLD = (255, 215, 0)
DARK_GRAY = (64, 64, 64)
GRAY = (128, 128, 128)

# プレイヤー設定
PLAYER_SPEED = 5
PLAYER_SIZE = 40

# 必殺技設定
SPECIAL_GAUGE_MAX = 1800  # 30秒でゲージMAX
SPECIAL_STOCK_MAX = 3
MASTER_SPARK_DURATION = 300  # 5秒間持続
MASTER_SPARK_WIDTH = SCREEN_WIDTH // 2  # 画面の半分の幅
MASTER_SPARK_DAMAGE = 0.5  # フレームごとのダメージ
MASTER_SPARK_BOSS_DAMAGE_PERCENTAGE = 0.3 # ボスに与える総ダメージ割合

# 弾の設定
BULLET_SPEED = 7
BULLET_SIZE = 5

# レーザー設定
LASER_WIDTH = 8
LASER_LENGTH = 200
LASER_SPEED = 20
LASER_DAMAGE = 5  # 貫通ダメージ

# 爆弾設定
BOMB_SIZE = 10
BOMB_SPEED = 4
BOMB_EXPLOSION_RADIUS = 80
BOMB_EXPLOSION_DURATION = 30  # フレーム数

# 子機設定
OPTION_SIZE = PLAYER_SIZE // 2
OPTION_FOLLOW_DELAY = 10
OPTION_ORBIT_SPEED = 2
OPTION_SHOOT_INTERVAL = 20

# 敵の設定
ENEMY_SPEED = 2
ENEMY_SIZE = 30
ENEMY_SPAWN_RATE = 60  # フレーム数

# ボス設定
BOSS_WARNING_DURATION = 180  # 3秒間の警告表示
BOSS_ENTRANCE_DURATION = 180  # 3秒間の登場演出
BOSS_DEFEAT_EFFECT_DURATION = 120  # 2秒間の撃破演出

# ボスタイプ別設定
BOSS_STATS = {
    "fairy": {
        "max_health": 300,
        "score_value": 3000,
        "size": 30,
        "speed": 1.5,
        "name": "妖精の女王",
        "color": CYAN
    },
    "witch": {
        "max_health": 800,
        "score_value": 8000,
        "size": 35,
        "speed": 1.0,
        "name": "魔導師エリス",
        "color": MAGENTA
    },
    "dragon": {
        "max_health": 1200,
        "score_value": 12000,
        "size": 40,
        "speed": 0.8,
        "name": "炎竜アグニ",
        "color": ORANGE
    }
}

# スペルカード設定
SPELL_CARD_PATTERNS = {
    "fairy_dance": {
        "duration": 600,
        "difficulty": 1,
        "bullet_color": CYAN,
        "bullet_speed": 2.5
    },
    "light_burst": {
        "duration": 480,
        "difficulty": 2,
        "bullet_color": YELLOW,
        "bullet_speed": 3.0
    },
    "magic_storm": {
        "duration": 720,
        "difficulty": 3,
        "bullet_color": MAGENTA,
        "bullet_speed": 2.0
    },
    "star_rain": {
        "duration": 600,
        "difficulty": 2,
        "bullet_color": WHITE,
        "bullet_speed": 3.5
    },
    "spiral_curse": {
        "duration": 540,
        "difficulty": 4,
        "bullet_color": RED,
        "bullet_speed": 2.5
    },
    "dragon_roar": {
        "duration": 480,
        "difficulty": 3,
        "bullet_color": ORANGE,
        "bullet_speed": 4.0
    },
    "fire_spiral": {
        "duration": 600,
        "difficulty": 4,
        "bullet_color": RED,
        "bullet_speed": 2.0
    },
    "thunder_spear": {
        "duration": 720,
        "difficulty": 5,
        "bullet_color": BLUE,
        "bullet_speed": 6.0
    },
    "ultimate_blast": {
        "duration": 900,
        "difficulty": 6,
        "bullet_color": PURPLE,
        "bullet_speed": 3.5
    }
}

# ボス出現スケジュール
BOSS_SPAWN_SCHEDULE = {
    3: "fairy",     # レベル3で妖精ボス
    6: "witch",     # レベル6で魔女ボス
    10: "dragon",   # レベル10でドラゴンボス
    # レベル10以降は5レベルごとにランダムボス
}

# ボス弾幕の基本設定
BOSS_BULLET_SIZE = 8
BOSS_BULLET_DAMAGE = 1
BOSS_INVULNERABLE_TIME = 10  # 被弾後の無敵時間（フレーム）

# パワーアップ設定
POWERUP_SIZE = 25
POWERUP_SPEED = 3
POWERUP_SPAWN_RATE = 600  # フレーム数（10秒）
POWERUP_TYPES = ["life_up"]
POWERUP_DURATION = 600  # 10秒間持続

# 武器設定
WEAPON_TYPES = ["normal", "wide_shot", "laser_weapon"]
WEAPON_STATS = {
    "normal": {
        "damage_multiplier": 1.0,
        "cooldown_multiplier": 1.0,
        "bullet_count": 1
    },
    "wide_shot": {
        "damage_multiplier": 0.8,
        "cooldown_multiplier": 1.2,
        "bullet_count": 3
    },
    "laser_weapon": {
        "damage_multiplier": 1.5,
        "cooldown_multiplier": 2.0,
        "bullet_count": 1
    }
}

# レベルシステム設定
LEVEL_UP_NOTIFICATION_DURATION = 180  # 3秒間表示
LEVEL_TRANSITION_DURATION = 300  # 5秒間表示
BASE_EXPERIENCE_GAIN = 10  # 基本経験値

# レベルアップ時のボーナス経験値（敵タイプ別）
ENEMY_EXP_VALUES = {
    'basic': 10,
    'fast': 15,
    'tank': 25,
    'zigzag': 20,
    'sniper': 30,
    'shield': 35,
    'stopper': 40
}

# ボス撃破時の経験値
BOSS_EXP_VALUES = {
    'fairy': 200,
    'witch': 500,
    'dragon': 1000
}

# スコア設定
ENEMY_SCORE = 10

# ダメージ数値表示設定
DAMAGE_NUMBER_DURATION = 60  # 1秒間表示
DAMAGE_NUMBER_RISE_SPEED = 2  # 上昇速度

# UI設定
BOSS_HP_BAR_WIDTH = SCREEN_WIDTH - 100
BOSS_HP_BAR_HEIGHT = 20
BOSS_HP_BAR_Y = 20

# エフェクト設定
PARTICLE_LIFETIME = 60  # パーティクルの生存時間
EXPLOSION_PARTICLE_COUNT = 20  # 爆発時のパーティクル数
AURA_PARTICLE_COUNT = 8  # オーラエフェクトのパーティクル数

# サウンド設定
SOUND_ENABLED = True
MUSIC_VOLUME = 0.7
SOUND_VOLUME = 0.5

# サウンドファイルパス
SOUND_PATHS = {
    'shoot': 'assets/sounds/shoot.wav',
    'explosion': 'assets/sounds/explosion.wav',
    'powerup': 'assets/sounds/powerup.wav',
    'enemy_hit': 'assets/sounds/enemy_hit.wav',
    'player_hit': 'assets/sounds/player_hit.wav',
    'bgm': 'assets/sounds/bgm.mp3',
    'masupa': 'assets/sounds/masupa.wav'
}