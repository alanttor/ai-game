"""
图形渲染系统 - Attack on Titan Fan Game
实现卡通渲染(Cel-Shading)和描边效果
Requirements: 8.1, 8.2, 8.3
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum
import os


@dataclass
class ShaderConfig:
    """着色器配置"""
    # Cel-shading参数
    cel_levels: float = 3.0  # 色阶数量
    ambient_color: Tuple[float, float, float, float] = (0.3, 0.3, 0.35, 1.0)
    diffuse_color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    
    # 边缘光参数
    rim_power: float = 3.0
    rim_color: Tuple[float, float, float, float] = (0.8, 0.8, 1.0, 1.0)
    
    # 描边参数
    outline_width: float = 0.02
    outline_color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)


class RenderMode(Enum):
    """渲染模式"""
    STANDARD = "standard"
    CEL_SHADING = "cel_shading"
    OUTLINE_ONLY = "outline_only"


class CelShadingRenderer:
    """
    卡通渲染器
    实现动漫风格的cel-shading效果
    """
    
    def __init__(self, shader_dir: str = "assets/shaders/"):
        """
        初始化卡通渲染器
        
        Args:
            shader_dir: 着色器文件目录
        """
        self.shader_dir = shader_dir
        self.config = ShaderConfig()
        self._shader_loaded = False
        self._cel_shader = None
        self._outline_shader = None
        self._entities_with_shaders: Dict[int, Any] = {}
    
    def load_shaders(self) -> bool:
        """
        加载着色器文件
        
        Returns:
            bool: 是否成功加载
        """
        cel_vert_path = os.path.join(self.shader_dir, "cel_shading.vert")
        cel_frag_path = os.path.join(self.shader_dir, "cel_shading.frag")
        outline_vert_path = os.path.join(self.shader_dir, "outline.vert")
        outline_frag_path = os.path.join(self.shader_dir, "outline.frag")
        
        # 检查着色器文件是否存在
        required_files = [cel_vert_path, cel_frag_path, outline_vert_path, outline_frag_path]
        for file_path in required_files:
            if not os.path.exists(file_path):
                print(f"警告: 着色器文件不存在: {file_path}")
                return False
        
        self._shader_loaded = True
        return True
    
    def apply_cel_shading(self, entity: Any) -> bool:
        """
        对实体应用卡通渲染效果
        
        Args:
            entity: 要应用着色器的实体
            
        Returns:
            bool: 是否成功应用
        """
        if not self._shader_loaded:
            if not self.load_shaders():
                return False
        
        entity_id = id(entity)
        self._entities_with_shaders[entity_id] = {
            'entity': entity,
            'mode': RenderMode.CEL_SHADING
        }
        return True
    
    def apply_outline(self, entity: Any, width: Optional[float] = None, 
                      color: Optional[Tuple[float, float, float, float]] = None) -> bool:
        """
        对实体应用描边效果
        
        Args:
            entity: 要应用描边的实体
            width: 描边宽度(可选)
            color: 描边颜色(可选)
            
        Returns:
            bool: 是否成功应用
        """
        if not self._shader_loaded:
            if not self.load_shaders():
                return False
        
        entity_id = id(entity)
        outline_config = {
            'width': width if width is not None else self.config.outline_width,
            'color': color if color is not None else self.config.outline_color
        }
        
        if entity_id in self._entities_with_shaders:
            self._entities_with_shaders[entity_id]['outline'] = outline_config
        else:
            self._entities_with_shaders[entity_id] = {
                'entity': entity,
                'mode': RenderMode.OUTLINE_ONLY,
                'outline': outline_config
            }
        return True
    
    def remove_shaders(self, entity: Any) -> bool:
        """
        移除实体的着色器效果
        
        Args:
            entity: 要移除着色器的实体
            
        Returns:
            bool: 是否成功移除
        """
        entity_id = id(entity)
        if entity_id in self._entities_with_shaders:
            del self._entities_with_shaders[entity_id]
            return True
        return False
    
    def set_cel_levels(self, levels: float) -> None:
        """设置色阶数量"""
        self.config.cel_levels = max(2.0, levels)
    
    def set_outline_width(self, width: float) -> None:
        """设置描边宽度"""
        self.config.outline_width = max(0.0, width)
    
    def set_outline_color(self, color: Tuple[float, float, float, float]) -> None:
        """设置描边颜色"""
        self.config.outline_color = color
    
    def set_rim_light(self, power: float, color: Tuple[float, float, float, float]) -> None:
        """设置边缘光参数"""
        self.config.rim_power = max(0.1, power)
        self.config.rim_color = color
    
    def get_shader_config(self) -> ShaderConfig:
        """获取当前着色器配置"""
        return self.config
    
    def is_shader_applied(self, entity: Any) -> bool:
        """检查实体是否已应用着色器"""
        return id(entity) in self._entities_with_shaders
    
    def get_applied_entities_count(self) -> int:
        """获取已应用着色器的实体数量"""
        return len(self._entities_with_shaders)


class OutlineRenderer:
    """
    描边渲染器
    实现动漫风格的黑色描边效果
    """
    
    def __init__(self):
        """初始化描边渲染器"""
        self.default_width = 0.02
        self.default_color = (0.0, 0.0, 0.0, 1.0)
        self._outline_entities: Dict[int, Dict[str, Any]] = {}
    
    def add_outline(self, entity: Any, width: Optional[float] = None,
                    color: Optional[Tuple[float, float, float, float]] = None) -> bool:
        """
        为实体添加描边
        
        Args:
            entity: 目标实体
            width: 描边宽度
            color: 描边颜色
            
        Returns:
            bool: 是否成功添加
        """
        entity_id = id(entity)
        self._outline_entities[entity_id] = {
            'entity': entity,
            'width': width if width is not None else self.default_width,
            'color': color if color is not None else self.default_color
        }
        return True
    
    def remove_outline(self, entity: Any) -> bool:
        """
        移除实体的描边
        
        Args:
            entity: 目标实体
            
        Returns:
            bool: 是否成功移除
        """
        entity_id = id(entity)
        if entity_id in self._outline_entities:
            del self._outline_entities[entity_id]
            return True
        return False
    
    def update_outline(self, entity: Any, width: Optional[float] = None,
                       color: Optional[Tuple[float, float, float, float]] = None) -> bool:
        """
        更新实体的描边参数
        
        Args:
            entity: 目标实体
            width: 新的描边宽度
            color: 新的描边颜色
            
        Returns:
            bool: 是否成功更新
        """
        entity_id = id(entity)
        if entity_id not in self._outline_entities:
            return False
        
        if width is not None:
            self._outline_entities[entity_id]['width'] = width
        if color is not None:
            self._outline_entities[entity_id]['color'] = color
        return True
    
    def has_outline(self, entity: Any) -> bool:
        """检查实体是否有描边"""
        return id(entity) in self._outline_entities
    
    def get_outline_count(self) -> int:
        """获取有描边的实体数量"""
        return len(self._outline_entities)


class GraphicsSystem:
    """
    图形系统
    管理所有图形渲染相关功能
    """
    
    def __init__(self, shader_dir: str = "assets/shaders/"):
        """
        初始化图形系统
        
        Args:
            shader_dir: 着色器目录
        """
        self.cel_renderer = CelShadingRenderer(shader_dir)
        self.outline_renderer = OutlineRenderer()
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        初始化图形系统
        
        Returns:
            bool: 是否成功初始化
        """
        if self._initialized:
            return True
        
        # 加载着色器
        shader_loaded = self.cel_renderer.load_shaders()
        self._initialized = True
        return shader_loaded
    
    def apply_anime_style(self, entity: Any, include_outline: bool = True) -> bool:
        """
        对实体应用完整的动漫风格渲染
        
        Args:
            entity: 目标实体
            include_outline: 是否包含描边
            
        Returns:
            bool: 是否成功应用
        """
        success = self.cel_renderer.apply_cel_shading(entity)
        if success and include_outline:
            self.outline_renderer.add_outline(entity)
        return success
    
    def remove_anime_style(self, entity: Any) -> bool:
        """
        移除实体的动漫风格渲染
        
        Args:
            entity: 目标实体
            
        Returns:
            bool: 是否成功移除
        """
        cel_removed = self.cel_renderer.remove_shaders(entity)
        outline_removed = self.outline_renderer.remove_outline(entity)
        return cel_removed or outline_removed
    
    def set_global_cel_levels(self, levels: float) -> None:
        """设置全局色阶数量"""
        self.cel_renderer.set_cel_levels(levels)
    
    def set_global_outline_width(self, width: float) -> None:
        """设置全局描边宽度"""
        self.cel_renderer.set_outline_width(width)
        self.outline_renderer.default_width = width
    
    def set_global_outline_color(self, color: Tuple[float, float, float, float]) -> None:
        """设置全局描边颜色"""
        self.cel_renderer.set_outline_color(color)
        self.outline_renderer.default_color = color
    
    def is_initialized(self) -> bool:
        """检查系统是否已初始化"""
        return self._initialized
    
    def get_stats(self) -> Dict[str, int]:
        """获取渲染统计信息"""
        return {
            'cel_shaded_entities': self.cel_renderer.get_applied_entities_count(),
            'outlined_entities': self.outline_renderer.get_outline_count()
        }
