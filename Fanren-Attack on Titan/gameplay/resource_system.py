"""
资源管理系统 - 管理气体和刀刃资源
"""
from dataclasses import dataclass, field
from typing import Tuple
import sys
import os

# 添加父目录到路径以便导入config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GAME_CONFIG


@dataclass
class ResourceState:
    """资源状态数据类"""
    gas_level: float = field(default_factory=lambda: GAME_CONFIG.MAX_GAS)
    blade_count: int = field(default_factory=lambda: GAME_CONFIG.MAX_BLADES)
    blade_durability: float = field(default_factory=lambda: GAME_CONFIG.MAX_BLADE_DURABILITY)


class ResourceSystem:
    """
    资源管理系统
    
    管理玩家的气体和刀刃资源，包括消耗、补充和警告检测。
    
    Attributes:
        gas_level: 当前气体量 (0 - max_gas)
        blade_count: 当前刀刃数量 (0 - max_blades)
        blade_durability: 当前刀刃耐久度 (0 - max_durability)
    """
    
    def __init__(
        self,
        max_gas: float = None,
        max_blades: int = None,
        max_blade_durability: float = None,
        low_gas_threshold: float = None,
        low_blade_threshold: int = None
    ):
        """
        初始化资源系统
        
        Args:
            max_gas: 最大气体量，默认使用配置值
            max_blades: 最大刀刃数量，默认使用配置值
            max_blade_durability: 最大刀刃耐久度，默认使用配置值
            low_gas_threshold: 低气体警告阈值(百分比)，默认使用配置值
            low_blade_threshold: 低刀刃警告阈值，默认使用配置值
        """
        # 配置值
        self._max_gas = max_gas if max_gas is not None else GAME_CONFIG.MAX_GAS
        self._max_blades = max_blades if max_blades is not None else GAME_CONFIG.MAX_BLADES
        self._max_blade_durability = max_blade_durability if max_blade_durability is not None else GAME_CONFIG.MAX_BLADE_DURABILITY
        self._low_gas_threshold = low_gas_threshold if low_gas_threshold is not None else GAME_CONFIG.LOW_GAS_THRESHOLD
        self._low_blade_threshold = low_blade_threshold if low_blade_threshold is not None else GAME_CONFIG.LOW_BLADE_THRESHOLD

        # 当前资源状态
        self._gas_level = self._max_gas
        self._blade_count = self._max_blades
        self._blade_durability = self._max_blade_durability
    
    # ==================== 属性访问器 ====================
    
    @property
    def gas_level(self) -> float:
        """当前气体量"""
        return self._gas_level
    
    @property
    def blade_count(self) -> int:
        """当前刀刃数量"""
        return self._blade_count
    
    @property
    def blade_durability(self) -> float:
        """当前刀刃耐久度"""
        return self._blade_durability
    
    @property
    def max_gas(self) -> float:
        """最大气体量"""
        return self._max_gas
    
    @property
    def max_blades(self) -> int:
        """最大刀刃数量"""
        return self._max_blades
    
    @property
    def max_blade_durability(self) -> float:
        """最大刀刃耐久度"""
        return self._max_blade_durability
    
    # ==================== 气体管理 ====================
    
    def consume_gas(self, amount: float) -> bool:
        """
        消耗气体
        
        Args:
            amount: 消耗量
            
        Returns:
            bool: 是否成功消耗（气体足够）
        """
        if amount < 0:
            return False
        
        if self._gas_level >= amount:
            self._gas_level -= amount
            return True
        return False
    
    def refill_gas(self) -> None:
        """补充气体至最大值"""
        self._gas_level = self._max_gas
    
    def get_gas_percentage(self) -> float:
        """
        获取气体百分比
        
        Returns:
            float: 气体百分比 (0.0 - 1.0)
        """
        if self._max_gas <= 0:
            return 0.0
        return self._gas_level / self._max_gas
    
    # ==================== 刀刃管理 ====================
    
    def switch_blade(self) -> bool:
        """
        切换刀刃（消耗一把刀刃，恢复耐久度）
        
        Returns:
            bool: 是否成功切换（有备用刀刃）
        """
        if self._blade_count > 0:
            self._blade_count -= 1
            self._blade_durability = self._max_blade_durability
            return True
        return False
    
    def consume_blade_durability(self, amount: float) -> bool:
        """
        消耗刀刃耐久度
        
        Args:
            amount: 消耗量
            
        Returns:
            bool: 是否成功消耗（耐久度足够）
        """
        if amount < 0:
            return False
        
        if self._blade_durability >= amount:
            self._blade_durability -= amount
            return True
        return False
    
    def refill_blades(self) -> None:
        """补充刀刃至最大数量，并恢复耐久度"""
        self._blade_count = self._max_blades
        self._blade_durability = self._max_blade_durability
    
    def get_blade_durability_percentage(self) -> float:
        """
        获取刀刃耐久度百分比
        
        Returns:
            float: 耐久度百分比 (0.0 - 1.0)
        """
        if self._max_blade_durability <= 0:
            return 0.0
        return self._blade_durability / self._max_blade_durability
    
    # ==================== 警告检测 ====================
    
    def is_low_gas(self) -> bool:
        """
        检测是否低气体
        
        Returns:
            bool: 气体是否低于警告阈值 (< 20%)
        """
        return self.get_gas_percentage() < self._low_gas_threshold
    
    def is_low_blades(self) -> bool:
        """
        检测是否低刀刃
        
        Returns:
            bool: 刀刃数量是否低于警告阈值 (< 2)
        """
        return self._blade_count < self._low_blade_threshold
    
    def get_warnings(self) -> Tuple[bool, bool]:
        """
        获取所有警告状态
        
        Returns:
            Tuple[bool, bool]: (低气体警告, 低刀刃警告)
        """
        return (self.is_low_gas(), self.is_low_blades())
    
    # ==================== 补给站交互 ====================
    
    def interact_with_supply_station(self) -> None:
        """
        与补给站交互，补充所有资源
        
        Requirements: 4.4 - 补给站补充气体和刀刃至最大值
        """
        self.refill_gas()
        self.refill_blades()
    
    # ==================== 状态获取 ====================
    
    def get_state(self) -> ResourceState:
        """
        获取当前资源状态
        
        Returns:
            ResourceState: 当前资源状态数据
        """
        return ResourceState(
            gas_level=self._gas_level,
            blade_count=self._blade_count,
            blade_durability=self._blade_durability
        )
    
    def set_state(self, state: ResourceState) -> None:
        """
        设置资源状态（用于存档恢复）
        
        Args:
            state: 资源状态数据
        """
        self._gas_level = max(0, min(state.gas_level, self._max_gas))
        self._blade_count = max(0, min(state.blade_count, self._max_blades))
        self._blade_durability = max(0, min(state.blade_durability, self._max_blade_durability))
    
    def __repr__(self) -> str:
        return (
            f"ResourceSystem(gas={self._gas_level:.1f}/{self._max_gas}, "
            f"blades={self._blade_count}/{self._max_blades}, "
            f"durability={self._blade_durability:.1f}/{self._max_blade_durability})"
        )
