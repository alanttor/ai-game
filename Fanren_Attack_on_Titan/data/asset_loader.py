"""
资源加载器 - AssetLoader
实现模型、贴图、音频的加载和缓存机制
"""
import os
from typing import Dict, Any, Optional, TypeVar, Generic
from dataclasses import dataclass, field
import logging

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PATH_CONFIG

# 设置日志
logger = logging.getLogger(__name__)

T = TypeVar('T')


class AssetNotFoundError(Exception):
    """资源未找到异常"""
    pass


class AssetLoadError(Exception):
    """资源加载失败异常"""
    pass


@dataclass
class CachedAsset(Generic[T]):
    """缓存的资源项"""
    asset: T
    path: str
    load_time: float = 0.0
    access_count: int = 0


class AssetCache:
    """资源缓存管理"""
    
    def __init__(self, max_size: int = 100):
        """
        初始化缓存
        
        Args:
            max_size: 最大缓存数量
        """
        self._cache: Dict[str, CachedAsset] = {}
        self._max_size = max_size
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存的资源"""
        if key in self._cache:
            self._cache[key].access_count += 1
            return self._cache[key].asset
        return None
    
    def put(self, key: str, asset: Any, path: str) -> None:
        """添加资源到缓存"""
        if len(self._cache) >= self._max_size:
            self._evict_least_used()
        
        self._cache[key] = CachedAsset(
            asset=asset,
            path=path,
            access_count=1
        )

    
    def remove(self, key: str) -> bool:
        """从缓存移除资源"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
    
    def _evict_least_used(self) -> None:
        """移除最少使用的资源"""
        if not self._cache:
            return
        
        least_used_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].access_count
        )
        del self._cache[least_used_key]
    
    def contains(self, key: str) -> bool:
        """检查缓存中是否存在资源"""
        return key in self._cache
    
    @property
    def size(self) -> int:
        """当前缓存大小"""
        return len(self._cache)


class AssetLoader:
    """
    资源加载器
    负责加载和缓存游戏资源（模型、贴图、音频）
    """
    
    def __init__(self, base_path: str = None):
        """
        初始化资源加载器
        
        Args:
            base_path: 资源根目录，默认使用配置中的路径
        """
        self.base_path = base_path or PATH_CONFIG.ASSETS_DIR
        
        # 各类型资源的缓存
        self._model_cache = AssetCache(max_size=50)
        self._texture_cache = AssetCache(max_size=100)
        self._sound_cache = AssetCache(max_size=50)
        self._music_cache = AssetCache(max_size=10)
        
        # Ursina引擎引用（延迟初始化）
        self._ursina_available = False
        self._check_ursina()
    
    def _check_ursina(self) -> None:
        """检查Ursina引擎是否可用"""
        try:
            from ursina import load_model, load_texture, Audio
            self._ursina_available = True
        except ImportError:
            self._ursina_available = False
            logger.warning("Ursina引擎不可用，资源加载将使用占位符模式")
    
    def _resolve_path(self, relative_path: str, asset_type: str) -> str:
        """
        解析资源完整路径
        
        Args:
            relative_path: 相对路径
            asset_type: 资源类型 (model, texture, sound, music)
            
        Returns:
            完整路径
        """
        type_dirs = {
            'model': PATH_CONFIG.MODELS_DIR,
            'texture': PATH_CONFIG.TEXTURES_DIR,
            'sound': PATH_CONFIG.SOUNDS_DIR,
            'music': PATH_CONFIG.MUSIC_DIR,
            'shader': PATH_CONFIG.SHADERS_DIR
        }
        
        base_dir = type_dirs.get(asset_type, self.base_path)
        
        # 如果已经是完整路径，直接返回
        if os.path.isabs(relative_path):
            return relative_path
        
        # 如果路径已包含资源目录前缀，直接使用
        if relative_path.startswith(base_dir):
            return relative_path
        
        return os.path.join(base_dir, relative_path)
    
    def _file_exists(self, path: str) -> bool:
        """检查文件是否存在"""
        return os.path.exists(path)
    
    def load_model(self, model_path: str, use_cache: bool = True) -> Any:
        """
        加载3D模型
        
        Args:
            model_path: 模型文件路径
            use_cache: 是否使用缓存
            
        Returns:
            加载的模型对象，或占位符
            
        Raises:
            AssetNotFoundError: 当模型文件不存在且无法使用占位符时
        """
        cache_key = f"model:{model_path}"
        
        # 检查缓存
        if use_cache:
            cached = self._model_cache.get(cache_key)
            if cached is not None:
                return cached
        
        full_path = self._resolve_path(model_path, 'model')
        
        if self._ursina_available:
            try:
                from ursina import load_model
                model = load_model(full_path)
                if model and use_cache:
                    self._model_cache.put(cache_key, model, full_path)
                return model
            except Exception as e:
                logger.warning(f"加载模型失败 {model_path}: {e}，使用占位符")
                return self._get_placeholder_model()
        else:
            # 非Ursina环境，返回路径信息作为占位符
            placeholder = {'type': 'model', 'path': full_path, 'placeholder': True}
            if use_cache:
                self._model_cache.put(cache_key, placeholder, full_path)
            return placeholder
    
    def load_texture(self, texture_path: str, use_cache: bool = True) -> Any:
        """
        加载贴图
        
        Args:
            texture_path: 贴图文件路径
            use_cache: 是否使用缓存
            
        Returns:
            加载的贴图对象，或占位符
        """
        cache_key = f"texture:{texture_path}"
        
        if use_cache:
            cached = self._texture_cache.get(cache_key)
            if cached is not None:
                return cached
        
        full_path = self._resolve_path(texture_path, 'texture')
        
        if self._ursina_available:
            try:
                from ursina import load_texture
                texture = load_texture(full_path)
                if texture and use_cache:
                    self._texture_cache.put(cache_key, texture, full_path)
                return texture
            except Exception as e:
                logger.warning(f"加载贴图失败 {texture_path}: {e}，使用默认贴图")
                return self._get_placeholder_texture()
        else:
            placeholder = {'type': 'texture', 'path': full_path, 'placeholder': True}
            if use_cache:
                self._texture_cache.put(cache_key, placeholder, full_path)
            return placeholder
    
    def load_sound(self, sound_path: str, use_cache: bool = True) -> Any:
        """
        加载音效
        
        Args:
            sound_path: 音效文件路径
            use_cache: 是否使用缓存
            
        Returns:
            加载的音效对象，或占位符
        """
        cache_key = f"sound:{sound_path}"
        
        if use_cache:
            cached = self._sound_cache.get(cache_key)
            if cached is not None:
                return cached
        
        full_path = self._resolve_path(sound_path, 'sound')
        
        if self._ursina_available:
            try:
                from ursina import Audio
                sound = Audio(full_path, autoplay=False)
                if sound and use_cache:
                    self._sound_cache.put(cache_key, sound, full_path)
                return sound
            except Exception as e:
                logger.warning(f"加载音效失败 {sound_path}: {e}")
                return None
        else:
            placeholder = {'type': 'sound', 'path': full_path, 'placeholder': True}
            if use_cache:
                self._sound_cache.put(cache_key, placeholder, full_path)
            return placeholder
    
    def load_music(self, music_path: str, use_cache: bool = True) -> Any:
        """
        加载背景音乐
        
        Args:
            music_path: 音乐文件路径
            use_cache: 是否使用缓存
            
        Returns:
            加载的音乐对象，或占位符
        """
        cache_key = f"music:{music_path}"
        
        if use_cache:
            cached = self._music_cache.get(cache_key)
            if cached is not None:
                return cached
        
        full_path = self._resolve_path(music_path, 'music')
        
        if self._ursina_available:
            try:
                from ursina import Audio
                music = Audio(full_path, autoplay=False, loop=True)
                if music and use_cache:
                    self._music_cache.put(cache_key, music, full_path)
                return music
            except Exception as e:
                logger.warning(f"加载音乐失败 {music_path}: {e}")
                return None
        else:
            placeholder = {'type': 'music', 'path': full_path, 'placeholder': True}
            if use_cache:
                self._music_cache.put(cache_key, placeholder, full_path)
            return placeholder
    
    def _get_placeholder_model(self) -> Any:
        """获取占位符模型"""
        if self._ursina_available:
            try:
                from ursina import load_model
                return load_model('cube')  # Ursina内置立方体
            except:
                pass
        return {'type': 'model', 'placeholder': True, 'shape': 'cube'}
    
    def _get_placeholder_texture(self) -> Any:
        """获取占位符贴图"""
        if self._ursina_available:
            try:
                from ursina import color
                return color.white  # 默认白色
            except:
                pass
        return {'type': 'texture', 'placeholder': True, 'color': 'white'}
    
    def preload_assets(self, asset_list: Dict[str, list]) -> Dict[str, int]:
        """
        预加载资源列表
        
        Args:
            asset_list: 资源列表，格式为 {'models': [...], 'textures': [...], ...}
            
        Returns:
            加载结果统计
        """
        results = {'models': 0, 'textures': 0, 'sounds': 0, 'music': 0}
        
        for model_path in asset_list.get('models', []):
            if self.load_model(model_path):
                results['models'] += 1
        
        for texture_path in asset_list.get('textures', []):
            if self.load_texture(texture_path):
                results['textures'] += 1
        
        for sound_path in asset_list.get('sounds', []):
            if self.load_sound(sound_path):
                results['sounds'] += 1
        
        for music_path in asset_list.get('music', []):
            if self.load_music(music_path):
                results['music'] += 1
        
        return results
    
    def clear_cache(self, asset_type: str = None) -> None:
        """
        清空缓存
        
        Args:
            asset_type: 要清空的资源类型，None表示全部清空
        """
        if asset_type is None or asset_type == 'model':
            self._model_cache.clear()
        if asset_type is None or asset_type == 'texture':
            self._texture_cache.clear()
        if asset_type is None or asset_type == 'sound':
            self._sound_cache.clear()
        if asset_type is None or asset_type == 'music':
            self._music_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """获取缓存统计信息"""
        return {
            'models': self._model_cache.size,
            'textures': self._texture_cache.size,
            'sounds': self._sound_cache.size,
            'music': self._music_cache.size
        }
