import pygame
import os
from settings import *

class SoundManager:
    def __init__(self):
        if not SOUND_ENABLED:
            return
            
        pygame.mixer.init()
        self.sounds = {}
        self.music_playing = False
        
        # サウンドファイルの読み込み
        self.load_sounds()
        
    def load_sounds(self):
        """サウンドファイルを読み込む"""
        for sound_name, sound_path in SOUND_PATHS.items():
            if sound_name == 'bgm':
                continue  # BGMは別途処理

            full_path = os.path.join(os.path.dirname(__file__), sound_path)

            if os.path.exists(full_path):
                try:
                    sound = pygame.mixer.Sound(full_path)
                    sound.set_volume(SOUND_VOLUME)
                    self.sounds[sound_name] = sound
                    print(f"Loaded sound: {sound_name}")
                except pygame.error as e:
                    print(f"Could not load sound {sound_name}: {e}")
                    # デフォルトサウンドを生成
                    self.sounds[sound_name] = self.create_default_sound(sound_name)
            else:
                print(f"Sound file not found: {full_path}")
                # デフォルトサウンドを生成
                self.sounds[sound_name] = self.create_default_sound(sound_name)
    
    def create_default_sound(self, sound_name):
        """サウンドファイルがない場合のデフォルトサウンド生成"""
        try:
            # 簡単な波形を生成してサウンドを作る
            import numpy as np
            
            sample_rate = 22050
            
            if sound_name == 'shoot':
                # 射撃音：短い高音
                duration = 0.1
                frequency = 800
            elif sound_name == 'explosion':
                # 爆発音：低音のノイズ
                duration = 0.3
                frequency = 200
            elif sound_name == 'powerup':
                # パワーアップ音：上昇音
                duration = 0.5
                frequency = 400
            elif sound_name == 'enemy_hit':
                # 敵撃破音：中音
                duration = 0.2
                frequency = 600
            elif sound_name == 'player_hit':
                # プレイヤー被弾音：下降音
                duration = 0.4
                frequency = 300
            else:
                duration = 0.1
                frequency = 440
                
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2))
            
            for i in range(frames):
                time = float(i) / sample_rate
                if sound_name == 'powerup':
                    # 上昇音
                    freq = frequency + (frequency * 0.5 * time / duration)
                elif sound_name == 'player_hit':
                    # 下降音
                    freq = frequency - (frequency * 0.3 * time / duration)
                else:
                    freq = frequency
                    
                wave = np.sin(2 * np.pi * freq * time)
                
                # エンベロープ（音量の変化）
                envelope = max(0, 1 - time / duration)
                wave *= envelope * 0.3  # 音量調整
                
                arr[i] = [wave, wave]
            
            # numpy配列をpygameサウンドに変換
            sound_array = (arr * 32767).astype(np.int16)
            sound = pygame.sndarray.make_sound(sound_array)
            sound.set_volume(SOUND_VOLUME)
            return sound
        except ImportError:
            print("Warning: numpy is not installed. Cannot create default sounds.")
            return None
    
    def play_sound(self, sound_name):
        """サウンドを再生"""
        if not SOUND_ENABLED:
            return
            
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def play_music(self):
        """BGMを再生"""
        if not SOUND_ENABLED or self.music_playing:
            return
            
        bgm_path = SOUND_PATHS['bgm']
        full_path = os.path.join(os.path.dirname(__file__), bgm_path)
        if os.path.exists(full_path):
            try:
                pygame.mixer.music.load(full_path)
                pygame.mixer.music.set_volume(MUSIC_VOLUME)
                pygame.mixer.music.play(-1)  # ループ再生
                self.music_playing = True
                print("BGM started")
            except pygame.error as e:
                print(f"Could not load BGM: {e}")
        else:
            print(f"BGM file not found: {full_path}")
    
    def stop_music(self):
        """BGMを停止"""
        if SOUND_ENABLED and self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False
    
    def set_sound_volume(self, volume):
        """効果音の音量設定"""
        global SOUND_VOLUME
        SOUND_VOLUME = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(SOUND_VOLUME)
    
    def set_music_volume(self, volume):
        """BGMの音量設定"""
        global MUSIC_VOLUME
        MUSIC_VOLUME = max(0.0, min(1.0, volume))
        if self.music_playing:
            pygame.mixer.music.set_volume(MUSIC_VOLUME)

# グローバルなサウンドマネージャーインスタンス
sound_manager = None

def init_sound_system():
    """サウンドシステムの初期化"""
    global sound_manager
    sound_manager = SoundManager()
    return sound_manager

def play_sound(sound_name):
    """サウンド再生のショートカット関数"""
    if sound_manager:
        sound_manager.play_sound(sound_name)