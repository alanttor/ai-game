"""
音频系统 - AudioSystem
实现音效播放、背景音乐播放和音量控制
Requirements: 9.1, 9.2, 9.3, 9.4
"""
import os
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PATH_CONFIG

logger = logging.getLogger(__name__)


class SoundCategory(Enum):
    """音效类别"""
    ODM = "odm"           # 立体机动装置音效
    COMBAT = "combat"     # 战斗音效
    TITAN = "titan"       # 巨人音效
    UI = "ui"             # UI音效
    AMBIENT = "ambient"   # 环境音效


class MusicMood(Enum):
    """背景音乐情绪类型"""
    CALM = "calm"           # 平静
    TENSE = "tense"         # 紧张
    BATTLE = "battle"       # 战斗
    VICTORY = "victory"     # 胜利
    DEFEAT = "defeat"       # 失败
    CUTSCENE = "cutscene"   # 过场


@dataclass
class AudioConfig:
    """音频配置"""
    master_volume: float = 1.0      # 主音量 (0.0 - 1.0)
    sfx_volume: float = 1.0         # 音效音量
    music_volume: float = 0.7       # 音乐音量
    voice_volume: float = 1.0       # 语音音量
    
    # 威胁音效配置
    threat_distance_near: float = 20.0    # 近距离威胁阈值
    threat_distance_far: float = 50.0     # 远距离威胁阈值
    
    def get_effective_sfx_volume(self) -> float:
        """获取实际音效音量"""
        return self.master_volume * self.sfx_volume
    
    def get_effective_music_volume(self) -> float:
        """获取实际音乐音量"""
        return self.master_volume * self.music_volume
    
    def get_effective_voice_volume(self) -> float:
        """获取实际语音音量"""
        return self.master_volume * self.voice_volume


@dataclass
class SoundEffect:
    """音效定义"""
    name: str
    path: str
    category: SoundCategory
    volume: float = 1.0
    pitch: float = 1.0
    loop: bool = False
    _audio_instance: Any = field(default=None, repr=False)



class AudioSystem:
    """
    音频系统
    负责管理游戏中所有音效和背景音乐的播放
    
    Requirements:
    - 9.1: ODM Gear音效 (钩锁发射、钢索张力、气体释放)
    - 9.2: 战斗音效 (刀刃斩击、巨人撞击)
    - 9.3: 背景音乐 (根据任务情绪播放)
    - 9.4: 威胁音效 (巨人接近时调整音频提示)
    """
    
    # 预定义音效路径
    SOUND_PATHS = {
        # ODM音效 (Requirement 9.1)
        'hook_fire': 'odm/hook_fire.wav',
        'hook_attach': 'odm/hook_attach.wav',
        'hook_release': 'odm/hook_release.wav',
        'cable_tension': 'odm/cable_tension.wav',
        'gas_release': 'odm/gas_release.wav',
        'gas_boost': 'odm/gas_boost.wav',
        'gas_low': 'odm/gas_low.wav',
        
        # 战斗音效 (Requirement 9.2)
        'blade_slash': 'combat/blade_slash.wav',
        'blade_hit': 'combat/blade_hit.wav',
        'blade_break': 'combat/blade_break.wav',
        'blade_switch': 'combat/blade_switch.wav',
        'nape_cut': 'combat/nape_cut.wav',
        'titan_impact': 'combat/titan_impact.wav',
        'combo_hit': 'combat/combo_hit.wav',
        
        # 巨人音效 (Requirement 9.4)
        'titan_roar': 'titan/titan_roar.wav',
        'titan_footstep': 'titan/titan_footstep.wav',
        'titan_grab': 'titan/titan_grab.wav',
        'titan_death': 'titan/titan_death.wav',
        'titan_steam': 'titan/titan_steam.wav',
        
        # UI音效
        'menu_select': 'ui/menu_select.wav',
        'menu_confirm': 'ui/menu_confirm.wav',
        'menu_cancel': 'ui/menu_cancel.wav',
        
        # 环境音效
        'wind': 'ambient/wind.wav',
        'city_ambient': 'ambient/city_ambient.wav',
    }
    
    # 预定义音乐路径
    MUSIC_PATHS = {
        MusicMood.CALM: 'bgm/calm.mp3',
        MusicMood.TENSE: 'bgm/tense.mp3',
        MusicMood.BATTLE: 'bgm/battle.mp3',
        MusicMood.VICTORY: 'bgm/victory.mp3',
        MusicMood.DEFEAT: 'bgm/defeat.mp3',
        MusicMood.CUTSCENE: 'bgm/cutscene.mp3',
    }
    
    def __init__(self, config: AudioConfig = None):
        """
        初始化音频系统
        
        Args:
            config: 音频配置，默认使用默认配置
        """
        self.config = config or AudioConfig()
        
        # 音效缓存
        self._sound_cache: Dict[str, SoundEffect] = {}
        
        # 当前播放的背景音乐
        self._current_music: Optional[Any] = None
        self._current_music_mood: Optional[MusicMood] = None
        
        # 当前播放的循环音效
        self._looping_sounds: Dict[str, Any] = {}
        
        # 威胁音效状态
        self._threat_level: float = 0.0
        self._threat_sound_playing: bool = False
        
        # Ursina引擎可用性
        self._ursina_available = False
        self._check_ursina()
        
        # 初始化音效定义
        self._init_sound_definitions()
    
    def _check_ursina(self) -> None:
        """检查Ursina引擎是否可用"""
        try:
            from ursina import Audio
            self._ursina_available = True
        except ImportError:
            self._ursina_available = False
            logger.warning("Ursina引擎不可用，音频系统将使用模拟模式")
    
    def _init_sound_definitions(self) -> None:
        """初始化音效定义"""
        # ODM音效
        self._register_sound('hook_fire', SoundCategory.ODM)
        self._register_sound('hook_attach', SoundCategory.ODM)
        self._register_sound('hook_release', SoundCategory.ODM)
        self._register_sound('cable_tension', SoundCategory.ODM, loop=True)
        self._register_sound('gas_release', SoundCategory.ODM)
        self._register_sound('gas_boost', SoundCategory.ODM)
        self._register_sound('gas_low', SoundCategory.ODM)
        
        # 战斗音效
        self._register_sound('blade_slash', SoundCategory.COMBAT)
        self._register_sound('blade_hit', SoundCategory.COMBAT)
        self._register_sound('blade_break', SoundCategory.COMBAT)
        self._register_sound('blade_switch', SoundCategory.COMBAT)
        self._register_sound('nape_cut', SoundCategory.COMBAT)
        self._register_sound('titan_impact', SoundCategory.COMBAT)
        self._register_sound('combo_hit', SoundCategory.COMBAT)
        
        # 巨人音效
        self._register_sound('titan_roar', SoundCategory.TITAN)
        self._register_sound('titan_footstep', SoundCategory.TITAN)
        self._register_sound('titan_grab', SoundCategory.TITAN)
        self._register_sound('titan_death', SoundCategory.TITAN)
        self._register_sound('titan_steam', SoundCategory.TITAN)
        
        # UI音效
        self._register_sound('menu_select', SoundCategory.UI)
        self._register_sound('menu_confirm', SoundCategory.UI)
        self._register_sound('menu_cancel', SoundCategory.UI)
        
        # 环境音效
        self._register_sound('wind', SoundCategory.AMBIENT, loop=True)
        self._register_sound('city_ambient', SoundCategory.AMBIENT, loop=True)
    
    def _register_sound(self, name: str, category: SoundCategory, 
                        volume: float = 1.0, loop: bool = False) -> None:
        """注册音效定义"""
        if name in self.SOUND_PATHS:
            self._sound_cache[name] = SoundEffect(
                name=name,
                path=self.SOUND_PATHS[name],
                category=category,
                volume=volume,
                loop=loop
            )

    
    def _get_full_sound_path(self, relative_path: str) -> str:
        """获取音效完整路径"""
        return os.path.join(PATH_CONFIG.SOUNDS_DIR, relative_path)
    
    def _get_full_music_path(self, relative_path: str) -> str:
        """获取音乐完整路径"""
        return os.path.join(PATH_CONFIG.MUSIC_DIR, relative_path)
    
    # ==================== 音效播放 (Requirements 9.1, 9.2) ====================
    
    def play_sound(self, sound_name: str, volume_multiplier: float = 1.0, 
                   pitch: float = 1.0) -> bool:
        """
        播放音效
        
        Args:
            sound_name: 音效名称
            volume_multiplier: 音量倍数
            pitch: 音调
            
        Returns:
            是否成功播放
        """
        if sound_name not in self._sound_cache:
            logger.warning(f"音效未找到: {sound_name}")
            return False
        
        sound_def = self._sound_cache[sound_name]
        effective_volume = (self.config.get_effective_sfx_volume() * 
                          sound_def.volume * volume_multiplier)
        
        if self._ursina_available:
            try:
                from ursina import Audio
                full_path = self._get_full_sound_path(sound_def.path)
                audio = Audio(
                    full_path,
                    volume=effective_volume,
                    pitch=pitch,
                    autoplay=True,
                    loop=sound_def.loop
                )
                
                if sound_def.loop:
                    self._looping_sounds[sound_name] = audio
                
                return True
            except Exception as e:
                logger.warning(f"播放音效失败 {sound_name}: {e}")
                return False
        else:
            # 模拟模式 - 记录播放请求
            logger.debug(f"[模拟] 播放音效: {sound_name}, 音量: {effective_volume}")
            return True
    
    def stop_sound(self, sound_name: str) -> bool:
        """
        停止循环音效
        
        Args:
            sound_name: 音效名称
            
        Returns:
            是否成功停止
        """
        if sound_name in self._looping_sounds:
            if self._ursina_available:
                try:
                    self._looping_sounds[sound_name].stop()
                except:
                    pass
            del self._looping_sounds[sound_name]
            return True
        return False
    
    def stop_all_sounds(self) -> None:
        """停止所有音效"""
        for sound_name in list(self._looping_sounds.keys()):
            self.stop_sound(sound_name)
    
    # ==================== ODM音效 (Requirement 9.1) ====================
    
    def play_hook_fire(self) -> bool:
        """播放钩锁发射音效"""
        return self.play_sound('hook_fire')
    
    def play_hook_attach(self) -> bool:
        """播放钩锁附着音效"""
        return self.play_sound('hook_attach')
    
    def play_hook_release(self) -> bool:
        """播放钩锁释放音效"""
        return self.play_sound('hook_release')
    
    def start_cable_tension(self) -> bool:
        """开始播放钢索张力音效（循环）"""
        return self.play_sound('cable_tension')
    
    def stop_cable_tension(self) -> bool:
        """停止钢索张力音效"""
        return self.stop_sound('cable_tension')
    
    def play_gas_release(self) -> bool:
        """播放气体释放音效"""
        return self.play_sound('gas_release')
    
    def play_gas_boost(self) -> bool:
        """播放气体推进音效"""
        return self.play_sound('gas_boost')
    
    def play_gas_low_warning(self) -> bool:
        """播放气体不足警告音效"""
        return self.play_sound('gas_low')
    
    # ==================== 战斗音效 (Requirement 9.2) ====================
    
    def play_blade_slash(self) -> bool:
        """播放刀刃斩击音效"""
        return self.play_sound('blade_slash')
    
    def play_blade_hit(self) -> bool:
        """播放刀刃命中音效"""
        return self.play_sound('blade_hit')
    
    def play_blade_break(self) -> bool:
        """播放刀刃断裂音效"""
        return self.play_sound('blade_break')
    
    def play_blade_switch(self) -> bool:
        """播放刀刃切换音效"""
        return self.play_sound('blade_switch')
    
    def play_nape_cut(self) -> bool:
        """播放后颈斩击音效"""
        return self.play_sound('nape_cut')
    
    def play_titan_impact(self) -> bool:
        """播放巨人撞击音效"""
        return self.play_sound('titan_impact')
    
    def play_combo_hit(self, combo_count: int) -> bool:
        """
        播放连击音效
        
        Args:
            combo_count: 当前连击数，影响音调
        """
        # 连击数越高，音调越高
        pitch = min(1.0 + (combo_count - 1) * 0.1, 2.0)
        return self.play_sound('combo_hit', pitch=pitch)

    
    # ==================== 背景音乐 (Requirement 9.3) ====================
    
    def play_music(self, mood: MusicMood, fade_in: float = 1.0) -> bool:
        """
        播放背景音乐
        
        Args:
            mood: 音乐情绪类型
            fade_in: 淡入时间（秒）
            
        Returns:
            是否成功播放
        """
        # 如果已经在播放相同情绪的音乐，不重复播放
        if self._current_music_mood == mood and self._current_music is not None:
            return True
        
        # 停止当前音乐
        self.stop_music()
        
        if mood not in self.MUSIC_PATHS:
            logger.warning(f"未找到音乐: {mood}")
            return False
        
        music_path = self.MUSIC_PATHS[mood]
        effective_volume = self.config.get_effective_music_volume()
        
        if self._ursina_available:
            try:
                from ursina import Audio
                full_path = self._get_full_music_path(music_path)
                self._current_music = Audio(
                    full_path,
                    volume=effective_volume,
                    autoplay=True,
                    loop=True
                )
                self._current_music_mood = mood
                return True
            except Exception as e:
                logger.warning(f"播放音乐失败 {mood}: {e}")
                return False
        else:
            # 模拟模式
            logger.debug(f"[模拟] 播放背景音乐: {mood.value}")
            self._current_music_mood = mood
            self._current_music = {'mood': mood, 'path': music_path}
            return True
    
    def stop_music(self, fade_out: float = 0.5) -> None:
        """
        停止背景音乐
        
        Args:
            fade_out: 淡出时间（秒）
        """
        if self._current_music is not None:
            if self._ursina_available:
                try:
                    self._current_music.stop()
                except:
                    pass
            self._current_music = None
            self._current_music_mood = None
    
    def set_music_mood(self, mood: MusicMood) -> bool:
        """
        设置音乐情绪（切换背景音乐）
        
        Args:
            mood: 目标情绪
            
        Returns:
            是否成功切换
        """
        return self.play_music(mood)
    
    def get_current_music_mood(self) -> Optional[MusicMood]:
        """获取当前音乐情绪"""
        return self._current_music_mood
    
    def is_music_playing(self) -> bool:
        """检查是否正在播放音乐"""
        return self._current_music is not None
    
    # ==================== 威胁音效 (Requirement 9.4) ====================
    
    def update_threat_level(self, distance_to_nearest_titan: float) -> None:
        """
        更新威胁等级，根据巨人距离调整音效
        
        Args:
            distance_to_nearest_titan: 到最近巨人的距离
        """
        if distance_to_nearest_titan < 0:
            # 无巨人
            self._threat_level = 0.0
            self._stop_threat_audio()
            return
        
        near = self.config.threat_distance_near
        far = self.config.threat_distance_far
        
        if distance_to_nearest_titan <= near:
            # 近距离 - 高威胁
            self._threat_level = 1.0
        elif distance_to_nearest_titan >= far:
            # 远距离 - 无威胁
            self._threat_level = 0.0
        else:
            # 中等距离 - 线性插值
            self._threat_level = 1.0 - (distance_to_nearest_titan - near) / (far - near)
        
        self._update_threat_audio()
    
    def _update_threat_audio(self) -> None:
        """根据威胁等级更新音效"""
        if self._threat_level > 0.5 and not self._threat_sound_playing:
            # 高威胁时播放警告音效
            self._start_threat_audio()
        elif self._threat_level <= 0.3 and self._threat_sound_playing:
            # 低威胁时停止警告音效
            self._stop_threat_audio()
        
        # 调整音乐紧张度
        if self._threat_level > 0.7:
            if self._current_music_mood != MusicMood.BATTLE:
                self.set_music_mood(MusicMood.BATTLE)
        elif self._threat_level > 0.3:
            if self._current_music_mood not in [MusicMood.TENSE, MusicMood.BATTLE]:
                self.set_music_mood(MusicMood.TENSE)
    
    def _start_threat_audio(self) -> None:
        """开始播放威胁音效"""
        self._threat_sound_playing = True
        # 可以播放心跳声或紧张音效
        logger.debug("开始播放威胁音效")
    
    def _stop_threat_audio(self) -> None:
        """停止威胁音效"""
        self._threat_sound_playing = False
        logger.debug("停止威胁音效")
    
    def get_threat_level(self) -> float:
        """获取当前威胁等级 (0.0 - 1.0)"""
        return self._threat_level
    
    # ==================== 巨人音效 ====================
    
    def play_titan_roar(self, distance: float = 0.0) -> bool:
        """
        播放巨人咆哮音效
        
        Args:
            distance: 巨人距离，影响音量
        """
        volume = self._calculate_distance_volume(distance)
        return self.play_sound('titan_roar', volume_multiplier=volume)
    
    def play_titan_footstep(self, distance: float = 0.0) -> bool:
        """播放巨人脚步声"""
        volume = self._calculate_distance_volume(distance)
        return self.play_sound('titan_footstep', volume_multiplier=volume)
    
    def play_titan_grab(self) -> bool:
        """播放巨人抓取音效"""
        return self.play_sound('titan_grab')
    
    def play_titan_death(self) -> bool:
        """播放巨人死亡音效"""
        return self.play_sound('titan_death')
    
    def play_titan_steam(self) -> bool:
        """播放巨人蒸汽消散音效"""
        return self.play_sound('titan_steam')
    
    def _calculate_distance_volume(self, distance: float) -> float:
        """
        根据距离计算音量
        
        Args:
            distance: 距离
            
        Returns:
            音量倍数 (0.0 - 1.0)
        """
        if distance <= 0:
            return 1.0
        
        max_distance = self.config.threat_distance_far
        if distance >= max_distance:
            return 0.1  # 最小音量
        
        return 1.0 - (distance / max_distance) * 0.9

    
    # ==================== 音量控制 ====================
    
    def set_master_volume(self, volume: float) -> None:
        """
        设置主音量
        
        Args:
            volume: 音量值 (0.0 - 1.0)
        """
        self.config.master_volume = max(0.0, min(1.0, volume))
        self._update_all_volumes()
    
    def set_sfx_volume(self, volume: float) -> None:
        """
        设置音效音量
        
        Args:
            volume: 音量值 (0.0 - 1.0)
        """
        self.config.sfx_volume = max(0.0, min(1.0, volume))
        self._update_all_volumes()
    
    def set_music_volume(self, volume: float) -> None:
        """
        设置音乐音量
        
        Args:
            volume: 音量值 (0.0 - 1.0)
        """
        self.config.music_volume = max(0.0, min(1.0, volume))
        self._update_music_volume()
    
    def set_voice_volume(self, volume: float) -> None:
        """
        设置语音音量
        
        Args:
            volume: 音量值 (0.0 - 1.0)
        """
        self.config.voice_volume = max(0.0, min(1.0, volume))
    
    def get_master_volume(self) -> float:
        """获取主音量"""
        return self.config.master_volume
    
    def get_sfx_volume(self) -> float:
        """获取音效音量"""
        return self.config.sfx_volume
    
    def get_music_volume(self) -> float:
        """获取音乐音量"""
        return self.config.music_volume
    
    def get_voice_volume(self) -> float:
        """获取语音音量"""
        return self.config.voice_volume
    
    def _update_all_volumes(self) -> None:
        """更新所有音频音量"""
        self._update_music_volume()
        # 循环音效的音量更新
        if self._ursina_available:
            for sound_name, audio in self._looping_sounds.items():
                if sound_name in self._sound_cache:
                    sound_def = self._sound_cache[sound_name]
                    try:
                        audio.volume = (self.config.get_effective_sfx_volume() * 
                                       sound_def.volume)
                    except:
                        pass
    
    def _update_music_volume(self) -> None:
        """更新音乐音量"""
        if self._current_music is not None and self._ursina_available:
            try:
                self._current_music.volume = self.config.get_effective_music_volume()
            except:
                pass
    
    # ==================== UI音效 ====================
    
    def play_menu_select(self) -> bool:
        """播放菜单选择音效"""
        return self.play_sound('menu_select')
    
    def play_menu_confirm(self) -> bool:
        """播放菜单确认音效"""
        return self.play_sound('menu_confirm')
    
    def play_menu_cancel(self) -> bool:
        """播放菜单取消音效"""
        return self.play_sound('menu_cancel')
    
    # ==================== 环境音效 ====================
    
    def start_ambient_wind(self) -> bool:
        """开始播放风声环境音效"""
        return self.play_sound('wind')
    
    def stop_ambient_wind(self) -> bool:
        """停止风声环境音效"""
        return self.stop_sound('wind')
    
    def start_city_ambient(self) -> bool:
        """开始播放城市环境音效"""
        return self.play_sound('city_ambient')
    
    def stop_city_ambient(self) -> bool:
        """停止城市环境音效"""
        return self.stop_sound('city_ambient')
    
    # ==================== 配置管理 ====================
    
    def get_config(self) -> AudioConfig:
        """获取音频配置"""
        return self.config
    
    def set_config(self, config: AudioConfig) -> None:
        """设置音频配置"""
        self.config = config
        self._update_all_volumes()
    
    def get_config_dict(self) -> Dict[str, float]:
        """获取配置字典（用于存档）"""
        return {
            'master_volume': self.config.master_volume,
            'sfx_volume': self.config.sfx_volume,
            'music_volume': self.config.music_volume,
            'voice_volume': self.config.voice_volume,
        }
    
    def load_config_dict(self, config_dict: Dict[str, float]) -> None:
        """从字典加载配置（用于读档）"""
        if 'master_volume' in config_dict:
            self.config.master_volume = config_dict['master_volume']
        if 'sfx_volume' in config_dict:
            self.config.sfx_volume = config_dict['sfx_volume']
        if 'music_volume' in config_dict:
            self.config.music_volume = config_dict['music_volume']
        if 'voice_volume' in config_dict:
            self.config.voice_volume = config_dict['voice_volume']
        self._update_all_volumes()
    
    # ==================== 清理 ====================
    
    def cleanup(self) -> None:
        """清理音频资源"""
        self.stop_all_sounds()
        self.stop_music()
        self._sound_cache.clear()
        logger.info("音频系统已清理")
