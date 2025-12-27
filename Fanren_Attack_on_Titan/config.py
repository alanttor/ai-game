"""
全局配置文件 - Attack on Titan Fan Game
"""
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class GameConfig:
    """游戏全局配置"""
    # 窗口设置
    WINDOW_TITLE: str = "进击的巨人 - 同人游戏"
    WINDOW_WIDTH: int = 1280
    WINDOW_HEIGHT: int = 720
    FULLSCREEN: bool = False
    
    # 游戏设置
    TARGET_FPS: int = 60
    PHYSICS_TIMESTEP: float = 1.0 / 60.0
    
    # ODM系统设置
    HOOK_RANGE: float = 50.0
    MAX_GAS: float = 100.0
    BOOST_COST: float = 5.0
    BOOST_POWER: float = 20.0
    
    # 战斗系统设置
    MAX_BLADES: int = 8
    MAX_BLADE_DURABILITY: float = 100.0
    DURABILITY_COST_PER_ATTACK: float = 10.0
    BASE_ATTACK_DAMAGE: float = 50.0
    COMBO_TIMEOUT: float = 3.0
    
    # 资源警告阈值
    LOW_GAS_THRESHOLD: float = 0.2  # 20%
    LOW_BLADE_THRESHOLD: int = 2
    
    # 存档设置
    SAVE_DIR: str = "saves/"
    MAX_SAVE_SLOTS: int = 3
    SAVE_VERSION: str = "1.0.0"


@dataclass
class PathConfig:
    """路径配置"""
    ASSETS_DIR: str = "assets/"
    MODELS_DIR: str = "assets/models/"
    TEXTURES_DIR: str = "assets/textures/"
    SOUNDS_DIR: str = "assets/sounds/"
    MUSIC_DIR: str = "assets/music/"
    SHADERS_DIR: str = "assets/shaders/"
    DATA_DIR: str = "data_files/"
    CHARACTERS_FILE: str = "data_files/characters.json"
    STORIES_FILE: str = "data_files/stories.json"
    LEVELS_FILE: str = "data_files/levels.json"
    TITANS_FILE: str = "data_files/titans.json"


# 全局配置实例
GAME_CONFIG = GameConfig()
PATH_CONFIG = PathConfig()
