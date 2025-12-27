"""
HUD (Heads-Up Display) - 游戏界面显示

显示玩家的资源状态、生命值、连击数和警告指示器。

Requirements:
    4.1 - 显示气体和刀刃资源
    4.2 - 低气体警告指示器
    4.3 - 低刀刃警告指示器
"""
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any
from enum import Enum


class WarningType(Enum):
    """警告类型枚举"""
    LOW_GAS = "low_gas"
    LOW_BLADE = "low_blade"
    CRITICAL_HEALTH = "critical_health"


@dataclass
class HUDData:
    """
    HUD显示数据
    
    包含所有需要在HUD上显示的信息
    """
    # 资源数据
    gas_level: float = 100.0
    max_gas: float = 100.0
    blade_count: int = 8
    max_blades: int = 8
    blade_durability: float = 100.0
    max_blade_durability: float = 100.0
    
    # 生命值数据
    health: float = 100.0
    max_health: float = 100.0
    
    # 战斗数据
    combo_count: int = 0
    total_score: int = 0
    
    # 警告状态
    low_gas_warning: bool = False
    low_blade_warning: bool = False
    
    @property
    def gas_percentage(self) -> float:
        """气体百分比 (0.0 - 1.0)"""
        if self.max_gas <= 0:
            return 0.0
        return self.gas_level / self.max_gas
    
    @property
    def health_percentage(self) -> float:
        """生命值百分比 (0.0 - 1.0)"""
        if self.max_health <= 0:
            return 0.0
        return self.health / self.max_health
    
    @property
    def blade_durability_percentage(self) -> float:
        """刀刃耐久度百分比 (0.0 - 1.0)"""
        if self.max_blade_durability <= 0:
            return 0.0
        return self.blade_durability / self.max_blade_durability


class HUDElement:
    """
    HUD元素基类
    
    所有HUD元素的抽象基类
    """
    
    def __init__(self, x: float = 0, y: float = 0, visible: bool = True):
        """
        初始化HUD元素
        
        Args:
            x: X坐标 (屏幕比例 -0.5 到 0.5)
            y: Y坐标 (屏幕比例 -0.5 到 0.5)
            visible: 是否可见
        """
        self.x = x
        self.y = y
        self.visible = visible
    
    def update(self, data: HUDData) -> None:
        """更新元素显示"""
        pass
    
    def render(self) -> Dict[str, Any]:
        """
        渲染元素（返回渲染数据）
        
        Returns:
            dict: 渲染数据
        """
        return {
            'x': self.x,
            'y': self.y,
            'visible': self.visible
        }


class ResourceBar(HUDElement):
    """
    资源条元素
    
    显示气体或刀刃耐久度的进度条
    """
    
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 0.2,
        height: float = 0.02,
        color: str = "#00FF00",
        background_color: str = "#333333",
        label: str = ""
    ):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.color = color
        self.background_color = background_color
        self.label = label
        self.fill_percentage = 1.0
        self.warning_active = False
        self.warning_color = "#FF0000"
    
    def set_fill(self, percentage: float) -> None:
        """设置填充百分比"""
        self.fill_percentage = max(0.0, min(1.0, percentage))
    
    def set_warning(self, active: bool) -> None:
        """设置警告状态"""
        self.warning_active = active
    
    def render(self) -> Dict[str, Any]:
        """渲染资源条"""
        base = super().render()
        base.update({
            'type': 'resource_bar',
            'width': self.width,
            'height': self.height,
            'color': self.warning_color if self.warning_active else self.color,
            'background_color': self.background_color,
            'label': self.label,
            'fill_percentage': self.fill_percentage,
            'warning_active': self.warning_active
        })
        return base


class CounterDisplay(HUDElement):
    """
    计数器显示元素
    
    显示刀刃数量、连击数等数值
    """
    
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        label: str = "",
        font_size: float = 0.03,
        color: str = "#FFFFFF"
    ):
        super().__init__(x, y)
        self.label = label
        self.font_size = font_size
        self.color = color
        self.value: int = 0
        self.max_value: Optional[int] = None
        self.warning_active = False
        self.warning_color = "#FF0000"
    
    def set_value(self, value: int, max_value: Optional[int] = None) -> None:
        """设置显示值"""
        self.value = value
        self.max_value = max_value
    
    def set_warning(self, active: bool) -> None:
        """设置警告状态"""
        self.warning_active = active
    
    def get_display_text(self) -> str:
        """获取显示文本"""
        if self.max_value is not None:
            return f"{self.label}: {self.value}/{self.max_value}"
        return f"{self.label}: {self.value}"
    
    def render(self) -> Dict[str, Any]:
        """渲染计数器"""
        base = super().render()
        base.update({
            'type': 'counter',
            'label': self.label,
            'value': self.value,
            'max_value': self.max_value,
            'font_size': self.font_size,
            'color': self.warning_color if self.warning_active else self.color,
            'display_text': self.get_display_text(),
            'warning_active': self.warning_active
        })
        return base


class ComboDisplay(HUDElement):
    """
    连击显示元素
    
    显示当前连击数，带有动画效果标记
    """
    
    def __init__(
        self,
        x: float = 0,
        y: float = 0.3,
        font_size: float = 0.05
    ):
        super().__init__(x, y)
        self.font_size = font_size
        self.combo_count = 0
        self.show_animation = False
        self.animation_scale = 1.0
    
    def set_combo(self, count: int) -> None:
        """设置连击数"""
        if count > self.combo_count:
            self.show_animation = True
            self.animation_scale = 1.5
        self.combo_count = count
        if count == 0:
            self.visible = False
        else:
            self.visible = True
    
    def update_animation(self, dt: float) -> None:
        """更新动画"""
        if self.show_animation:
            self.animation_scale = max(1.0, self.animation_scale - dt * 2)
            if self.animation_scale <= 1.0:
                self.show_animation = False
    
    def render(self) -> Dict[str, Any]:
        """渲染连击显示"""
        base = super().render()
        base.update({
            'type': 'combo',
            'combo_count': self.combo_count,
            'font_size': self.font_size * self.animation_scale,
            'display_text': f"COMBO x{self.combo_count}" if self.combo_count > 0 else "",
            'animation_active': self.show_animation
        })
        return base


class WarningIndicator(HUDElement):
    """
    警告指示器元素
    
    显示低资源警告，带闪烁效果
    
    Requirements:
        4.2 - 低气体警告指示器
        4.3 - 低刀刃警告指示器
    """
    
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        warning_type: WarningType = WarningType.LOW_GAS,
        color: str = "#FF0000"
    ):
        super().__init__(x, y, visible=False)
        self.warning_type = warning_type
        self.color = color
        self.blink_timer = 0.0
        self.blink_interval = 0.5
        self.is_blinking = False
    
    def activate(self) -> None:
        """激活警告"""
        self.visible = True
        self.is_blinking = True
    
    def deactivate(self) -> None:
        """停用警告"""
        self.visible = False
        self.is_blinking = False
        self.blink_timer = 0.0
    
    def update_blink(self, dt: float) -> None:
        """更新闪烁效果"""
        if self.is_blinking:
            self.blink_timer += dt
            if self.blink_timer >= self.blink_interval:
                self.blink_timer = 0.0
                self.visible = not self.visible
    
    def get_warning_text(self) -> str:
        """获取警告文本"""
        texts = {
            WarningType.LOW_GAS: "⚠ 气体不足!",
            WarningType.LOW_BLADE: "⚠ 刀刃不足!",
            WarningType.CRITICAL_HEALTH: "⚠ 生命危险!"
        }
        return texts.get(self.warning_type, "⚠ 警告!")
    
    def render(self) -> Dict[str, Any]:
        """渲染警告指示器"""
        base = super().render()
        base.update({
            'type': 'warning',
            'warning_type': self.warning_type.value,
            'color': self.color,
            'text': self.get_warning_text(),
            'is_blinking': self.is_blinking
        })
        return base


class ScoreDisplay(HUDElement):
    """
    分数显示元素
    """
    
    def __init__(
        self,
        x: float = 0.4,
        y: float = 0.45,
        font_size: float = 0.025
    ):
        super().__init__(x, y)
        self.font_size = font_size
        self.score = 0
    
    def set_score(self, score: int) -> None:
        """设置分数"""
        self.score = score
    
    def render(self) -> Dict[str, Any]:
        """渲染分数显示"""
        base = super().render()
        base.update({
            'type': 'score',
            'score': self.score,
            'font_size': self.font_size,
            'display_text': f"SCORE: {self.score:,}"
        })
        return base



class HUD:
    """
    游戏HUD管理器
    
    整合所有HUD元素，提供统一的更新和渲染接口。
    
    Requirements:
        4.1 - 显示气体和刀刃资源
        4.2 - 低气体警告指示器
        4.3 - 低刀刃警告指示器
    """
    
    def __init__(self):
        """初始化HUD"""
        # 资源条
        self.gas_bar = ResourceBar(
            x=-0.4, y=0.45,
            width=0.15, height=0.015,
            color="#00BFFF",  # 天蓝色
            label="GAS"
        )
        
        self.blade_durability_bar = ResourceBar(
            x=-0.4, y=0.42,
            width=0.15, height=0.015,
            color="#FFD700",  # 金色
            label="BLADE"
        )
        
        # 生命值条
        self.health_bar = ResourceBar(
            x=-0.4, y=0.39,
            width=0.15, height=0.02,
            color="#FF4444",  # 红色
            label="HP"
        )
        
        # 计数器
        self.blade_counter = CounterDisplay(
            x=-0.35, y=0.35,
            label="刀刃",
            font_size=0.02
        )
        
        # 连击显示
        self.combo_display = ComboDisplay(
            x=0, y=0.2,
            font_size=0.04
        )
        
        # 分数显示
        self.score_display = ScoreDisplay(
            x=0.35, y=0.45
        )
        
        # 警告指示器
        self.gas_warning = WarningIndicator(
            x=-0.2, y=0.3,
            warning_type=WarningType.LOW_GAS,
            color="#FF6600"
        )
        
        self.blade_warning = WarningIndicator(
            x=0.2, y=0.3,
            warning_type=WarningType.LOW_BLADE,
            color="#FFCC00"
        )
        
        self.health_warning = WarningIndicator(
            x=0, y=0.35,
            warning_type=WarningType.CRITICAL_HEALTH,
            color="#FF0000"
        )
        
        # 可见性
        self._visible = True
        
        # 当前数据
        self._current_data = HUDData()
    
    @property
    def visible(self) -> bool:
        """HUD是否可见"""
        return self._visible
    
    @visible.setter
    def visible(self, value: bool) -> None:
        """设置HUD可见性"""
        self._visible = value
    
    def update_from_player(self, player) -> None:
        """
        从玩家对象更新HUD数据
        
        Args:
            player: Player对象
        """
        if player is None:
            return
        
        # 获取资源系统数据
        resource_system = player.resource_system
        combat_system = player.combat_system
        
        # 更新数据
        self._current_data = HUDData(
            gas_level=resource_system.gas_level,
            max_gas=resource_system.max_gas,
            blade_count=resource_system.blade_count,
            max_blades=resource_system.max_blades,
            blade_durability=resource_system.blade_durability,
            max_blade_durability=resource_system.max_blade_durability,
            health=player.health,
            max_health=player.max_health,
            combo_count=combat_system.combo_count,
            total_score=combat_system.total_score,
            low_gas_warning=resource_system.is_low_gas(),
            low_blade_warning=resource_system.is_low_blades()
        )
        
        self.update(self._current_data)
    
    def update(self, data: HUDData) -> None:
        """
        更新HUD显示
        
        Args:
            data: HUD数据
        """
        self._current_data = data
        
        # 更新资源条
        self.gas_bar.set_fill(data.gas_percentage)
        self.gas_bar.set_warning(data.low_gas_warning)
        
        self.blade_durability_bar.set_fill(data.blade_durability_percentage)
        
        self.health_bar.set_fill(data.health_percentage)
        
        # 更新计数器
        self.blade_counter.set_value(data.blade_count, data.max_blades)
        self.blade_counter.set_warning(data.low_blade_warning)
        
        # 更新连击显示
        self.combo_display.set_combo(data.combo_count)
        
        # 更新分数
        self.score_display.set_score(data.total_score)
        
        # 更新警告指示器 (Requirement 4.2, 4.3)
        if data.low_gas_warning:
            self.gas_warning.activate()
        else:
            self.gas_warning.deactivate()
        
        if data.low_blade_warning:
            self.blade_warning.activate()
        else:
            self.blade_warning.deactivate()
        
        # 低生命值警告 (< 25%)
        if data.health_percentage < 0.25:
            self.health_warning.activate()
        else:
            self.health_warning.deactivate()
    
    def update_animations(self, dt: float) -> None:
        """
        更新动画效果
        
        Args:
            dt: 时间步长
        """
        self.combo_display.update_animation(dt)
        self.gas_warning.update_blink(dt)
        self.blade_warning.update_blink(dt)
        self.health_warning.update_blink(dt)
    
    def render(self) -> Dict[str, Any]:
        """
        渲染HUD（返回所有元素的渲染数据）
        
        Returns:
            dict: 包含所有HUD元素渲染数据的字典
        """
        if not self._visible:
            return {'visible': False, 'elements': []}
        
        elements = [
            self.gas_bar.render(),
            self.blade_durability_bar.render(),
            self.health_bar.render(),
            self.blade_counter.render(),
            self.combo_display.render(),
            self.score_display.render(),
            self.gas_warning.render(),
            self.blade_warning.render(),
            self.health_warning.render()
        ]
        
        return {
            'visible': True,
            'elements': elements,
            'data': {
                'gas_percentage': self._current_data.gas_percentage,
                'health_percentage': self._current_data.health_percentage,
                'blade_durability_percentage': self._current_data.blade_durability_percentage,
                'combo_count': self._current_data.combo_count,
                'score': self._current_data.total_score,
                'warnings': {
                    'low_gas': self._current_data.low_gas_warning,
                    'low_blade': self._current_data.low_blade_warning,
                    'critical_health': self._current_data.health_percentage < 0.25
                }
            }
        }
    
    def get_gas_display(self) -> str:
        """获取气体显示文本"""
        return f"GAS: {self._current_data.gas_level:.0f}/{self._current_data.max_gas:.0f}"
    
    def get_blade_display(self) -> str:
        """获取刀刃显示文本"""
        return f"BLADE: {self._current_data.blade_count}/{self._current_data.max_blades}"
    
    def get_health_display(self) -> str:
        """获取生命值显示文本"""
        return f"HP: {self._current_data.health:.0f}/{self._current_data.max_health:.0f}"
    
    def get_combo_display(self) -> str:
        """获取连击显示文本"""
        if self._current_data.combo_count > 0:
            return f"COMBO x{self._current_data.combo_count}"
        return ""
    
    def get_score_display(self) -> str:
        """获取分数显示文本"""
        return f"SCORE: {self._current_data.total_score:,}"
    
    def is_low_gas_warning_active(self) -> bool:
        """
        检查低气体警告是否激活
        
        Requirement 4.2: 低气体警告指示器
        """
        return self._current_data.low_gas_warning
    
    def is_low_blade_warning_active(self) -> bool:
        """
        检查低刀刃警告是否激活
        
        Requirement 4.3: 低刀刃警告指示器
        """
        return self._current_data.low_blade_warning
    
    def reset(self) -> None:
        """重置HUD到初始状态"""
        self._current_data = HUDData()
        self.update(self._current_data)
    
    def __repr__(self) -> str:
        return (
            f"HUD(gas={self._current_data.gas_percentage:.0%}, "
            f"health={self._current_data.health_percentage:.0%}, "
            f"combo={self._current_data.combo_count})"
        )
