"""
立体机动装置系统 (ODM System) - 3D Maneuver Gear
实现钩锁发射、摆荡物理和气体推进功能

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6
"""
from dataclasses import dataclass, field
from typing import Optional, Tuple, List
from enum import Enum
import math
import sys
import os

# 添加父目录到路径以便导入config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GAME_CONFIG


class HookSide(Enum):
    """钩锁侧面枚举"""
    LEFT = "left"
    RIGHT = "right"


@dataclass
class Vec3:
    """简单的3D向量类"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other: 'Vec3') -> 'Vec3':
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'Vec3') -> 'Vec3':
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> 'Vec3':
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __rmul__(self, scalar: float) -> 'Vec3':
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar: float) -> 'Vec3':
        if scalar == 0:
            return Vec3(0, 0, 0)
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def magnitude(self) -> float:
        """计算向量长度"""
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
    
    def normalized(self) -> 'Vec3':
        """返回单位向量"""
        mag = self.magnitude()
        if mag == 0:
            return Vec3(0, 0, 0)
        return self / mag
    
    def dot(self, other: 'Vec3') -> float:
        """点积"""
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other: 'Vec3') -> 'Vec3':
        """叉积"""
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def copy(self) -> 'Vec3':
        """复制向量"""
        return Vec3(self.x, self.y, self.z)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vec3):
            return False
        return (abs(self.x - other.x) < 1e-6 and 
                abs(self.y - other.y) < 1e-6 and 
                abs(self.z - other.z) < 1e-6)
    
    def __repr__(self) -> str:
        return f"Vec3({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"


@dataclass
class HookState:
    """
    钩锁状态数据类
    
    Attributes:
        is_attached: 是否已附着到表面
        attach_point: 附着点位置
        rope_length: 绳索长度
        tension: 绳索张力
    """
    is_attached: bool = False
    attach_point: Vec3 = field(default_factory=Vec3)
    rope_length: float = 0.0
    tension: float = 0.0
    
    def reset(self) -> None:
        """重置钩锁状态"""
        self.is_attached = False
        self.attach_point = Vec3()
        self.rope_length = 0.0
        self.tension = 0.0


@dataclass
class Surface:
    """
    可附着表面（用于钩锁检测）
    
    Attributes:
        position: 表面位置
        normal: 表面法线
        is_valid: 是否为有效附着点
    """
    position: Vec3 = field(default_factory=Vec3)
    normal: Vec3 = field(default_factory=lambda: Vec3(0, 1, 0))
    is_valid: bool = True


class ODMSystem:
    """
    立体机动装置系统
    
    实现钩锁发射、摆荡物理和气体推进功能。
    
    Requirements:
        2.1 - 钩锁发射并附着到有效表面
        2.2 - 物理模拟绳索摆荡
        2.3 - 气体推进加速
        2.4 - 空中方向控制
        2.5 - 气体耗尽禁用推进
        2.6 - 释放钩锁保持动量
    """
    
    # 物理常量
    GRAVITY = Vec3(0, -9.8, 0)
    AIR_RESISTANCE = 0.02
    ROPE_STIFFNESS = 50.0
    ROPE_DAMPING = 5.0
    
    def __init__(
        self,
        hook_range: float = None,
        max_gas: float = None,
        boost_cost: float = None,
        boost_power: float = None
    ):
        """
        初始化ODM系统
        
        Args:
            hook_range: 钩锁最大射程
            max_gas: 最大气体量
            boost_cost: 推进消耗气体量
            boost_power: 推进力度
        """
        # 配置参数
        self._hook_range = hook_range if hook_range is not None else GAME_CONFIG.HOOK_RANGE
        self._max_gas = max_gas if max_gas is not None else GAME_CONFIG.MAX_GAS
        self._boost_cost = boost_cost if boost_cost is not None else GAME_CONFIG.BOOST_COST
        self._boost_power = boost_power if boost_power is not None else GAME_CONFIG.BOOST_POWER
        
        # 钩锁状态
        self._left_hook = HookState()
        self._right_hook = HookState()
        
        # 运动状态
        self._position = Vec3()
        self._velocity = Vec3()
        self._gas_level = self._max_gas
        
        # 可附着表面列表（由关卡系统提供）
        self._surfaces: List[Surface] = []
    
    # ==================== 属性访问器 ====================
    
    @property
    def left_hook(self) -> HookState:
        """左侧钩锁状态"""
        return self._left_hook
    
    @property
    def right_hook(self) -> HookState:
        """右侧钩锁状态"""
        return self._right_hook
    
    @property
    def position(self) -> Vec3:
        """当前位置"""
        return self._position
    
    @position.setter
    def position(self, value: Vec3) -> None:
        """设置位置"""
        self._position = value
    
    @property
    def velocity(self) -> Vec3:
        """当前速度"""
        return self._velocity
    
    @velocity.setter
    def velocity(self, value: Vec3) -> None:
        """设置速度"""
        self._velocity = value
    
    @property
    def gas_level(self) -> float:
        """当前气体量"""
        return self._gas_level
    
    @property
    def max_gas(self) -> float:
        """最大气体量"""
        return self._max_gas
    
    @property
    def hook_range(self) -> float:
        """钩锁射程"""
        return self._hook_range
    
    @property
    def boost_power(self) -> float:
        """推进力度"""
        return self._boost_power
    
    @property
    def boost_cost(self) -> float:
        """推进消耗"""
        return self._boost_cost
    
    # ==================== 表面管理 ====================
    
    def set_surfaces(self, surfaces: List[Surface]) -> None:
        """设置可附着表面列表"""
        self._surfaces = surfaces
    
    def add_surface(self, surface: Surface) -> None:
        """添加可附着表面"""
        self._surfaces.append(surface)
    
    def clear_surfaces(self) -> None:
        """清除所有表面"""
        self._surfaces.clear()
    
    # ==================== 钩锁操作 ====================
    
    def _get_hook(self, hook_side: str) -> HookState:
        """获取指定侧的钩锁"""
        if hook_side == HookSide.LEFT.value or hook_side == "left":
            return self._left_hook
        return self._right_hook
    
    def _find_attach_point(self, origin: Vec3, direction: Vec3) -> Optional[Surface]:
        """
        查找钩锁附着点
        
        Args:
            origin: 发射起点
            direction: 发射方向（单位向量）
            
        Returns:
            Optional[Surface]: 找到的表面，或None
        """
        direction = direction.normalized()
        best_surface = None
        best_distance = float('inf')
        
        for surface in self._surfaces:
            if not surface.is_valid:
                continue
            
            # 计算到表面的距离
            to_surface = surface.position - origin
            distance = to_surface.magnitude()
            
            # 检查是否在射程内
            if distance > self._hook_range:
                continue
            
            # 检查方向是否大致正确（点积 > 0.5 表示方向相近）
            if distance > 0:
                direction_to_surface = to_surface.normalized()
                dot_product = direction.dot(direction_to_surface)
                if dot_product < 0.5:
                    continue
            
            # 选择最近的有效表面
            if distance < best_distance:
                best_distance = distance
                best_surface = surface
        
        return best_surface

    def fire_hook(self, direction: Vec3, hook_side: str = "right") -> bool:
        """
        发射钩锁
        
        Requirement 2.1: WHEN the player activates the grappling hook 
        THEN the ODM System SHALL fire a hook toward the aimed direction 
        and attach to valid surfaces within range
        
        Args:
            direction: 发射方向
            hook_side: 钩锁侧面 ("left" 或 "right")
            
        Returns:
            bool: 是否成功附着
        """
        hook = self._get_hook(hook_side)
        
        # 如果已经附着，先释放
        if hook.is_attached:
            self.release_hook(hook_side)
        
        # 查找附着点
        surface = self._find_attach_point(self._position, direction)
        
        if surface is None:
            return False
        
        # 附着到表面
        hook.is_attached = True
        hook.attach_point = surface.position.copy()
        hook.rope_length = (surface.position - self._position).magnitude()
        hook.tension = 0.0
        
        return True
    
    def release_hook(self, hook_side: str = "right") -> None:
        """
        释放钩锁
        
        Requirement 2.6: WHEN the player releases the hook 
        THEN the ODM System SHALL detach from the surface and preserve current momentum
        
        Args:
            hook_side: 钩锁侧面 ("left" 或 "right")
        """
        hook = self._get_hook(hook_side)
        
        # 释放时保持当前速度（动量守恒）
        # 速度已经在 self._velocity 中，无需额外处理
        
        hook.reset()
    
    def release_all_hooks(self) -> None:
        """释放所有钩锁"""
        self.release_hook("left")
        self.release_hook("right")
    
    def is_any_hook_attached(self) -> bool:
        """检查是否有任何钩锁附着"""
        return self._left_hook.is_attached or self._right_hook.is_attached
    
    # ==================== 物理更新 ====================
    
    def update_swing_physics(self, dt: float) -> None:
        """
        更新摆荡物理
        
        Requirement 2.2: WHEN the hook is attached 
        THEN the ODM System SHALL simulate physics-based rope swinging with realistic momentum
        
        Requirement 2.4: WHILE the player is airborne 
        THEN the ODM System SHALL allow directional control for aerial maneuvering
        
        Args:
            dt: 时间步长（秒）
        """
        if dt <= 0:
            return
        
        # 应用重力
        gravity_force = self.GRAVITY * dt
        self._velocity = self._velocity + gravity_force
        
        # 处理钩锁约束
        self._apply_hook_constraint(self._left_hook, dt)
        self._apply_hook_constraint(self._right_hook, dt)
        
        # 应用空气阻力
        air_drag = self._velocity * (-self.AIR_RESISTANCE)
        self._velocity = self._velocity + air_drag
        
        # 更新位置
        self._position = self._position + self._velocity * dt
    
    def _apply_hook_constraint(self, hook: HookState, dt: float) -> None:
        """
        应用钩锁约束（绳索物理）
        
        Args:
            hook: 钩锁状态
            dt: 时间步长
        """
        if not hook.is_attached:
            return
        
        # 计算从玩家到附着点的向量
        to_attach = hook.attach_point - self._position
        current_distance = to_attach.magnitude()
        
        if current_distance < 0.001:
            return
        
        # 绳索方向（指向附着点）
        rope_direction = to_attach.normalized()
        
        # 如果超出绳索长度，应用约束力
        if current_distance > hook.rope_length:
            # 计算超出距离
            stretch = current_distance - hook.rope_length
            
            # 弹簧力（将玩家拉回绳索长度内）
            spring_force = rope_direction * (stretch * self.ROPE_STIFFNESS)
            
            # 阻尼力（减少振荡）
            velocity_along_rope = rope_direction * self._velocity.dot(rope_direction)
            damping_force = velocity_along_rope * (-self.ROPE_DAMPING)
            
            # 应用力
            total_force = spring_force + damping_force
            self._velocity = self._velocity + total_force * dt
            
            # 更新张力
            hook.tension = stretch * self.ROPE_STIFFNESS
        else:
            hook.tension = 0.0
    
    # ==================== 气体推进 ====================
    
    def activate_boost(self) -> bool:
        """
        激活气体推进
        
        Requirement 2.3: WHEN the player activates propulsion boost 
        THEN the ODM System SHALL accelerate the player character 
        in the current movement direction while consuming gas
        
        Requirement 2.5: WHEN gas is depleted 
        THEN the ODM System SHALL disable propulsion boost
        
        Returns:
            bool: 是否成功激活推进
        """
        # 检查气体是否足够
        if self._gas_level < self._boost_cost:
            return False
        
        if self._gas_level <= 0:
            return False
        
        # 消耗气体
        self._gas_level -= self._boost_cost
        
        # 确定推进方向
        boost_direction = self._get_boost_direction()
        
        # 应用推进力
        boost_force = boost_direction * self._boost_power
        self._velocity = self._velocity + boost_force
        
        return True
    
    def _get_boost_direction(self) -> Vec3:
        """
        获取推进方向
        
        如果有钩锁附着，向附着点方向推进
        否则向当前速度方向推进
        """
        # 优先使用钩锁方向
        if self._left_hook.is_attached:
            direction = self._left_hook.attach_point - self._position
            if direction.magnitude() > 0.001:
                return direction.normalized()
        
        if self._right_hook.is_attached:
            direction = self._right_hook.attach_point - self._position
            if direction.magnitude() > 0.001:
                return direction.normalized()
        
        # 使用当前速度方向
        if self._velocity.magnitude() > 0.001:
            return self._velocity.normalized()
        
        # 默认向前
        return Vec3(0, 0, 1)
    
    # ==================== 气体管理 ====================
    
    def consume_gas(self, amount: float) -> bool:
        """
        消耗气体
        
        Args:
            amount: 消耗量
            
        Returns:
            bool: 是否成功消耗
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
        """获取气体百分比"""
        if self._max_gas <= 0:
            return 0.0
        return self._gas_level / self._max_gas
    
    # ==================== 动量获取 ====================
    
    def get_momentum(self) -> Vec3:
        """
        获取当前动量（速度向量）
        
        Returns:
            Vec3: 当前速度向量
        """
        return self._velocity.copy()
    
    def get_speed(self) -> float:
        """
        获取当前速度大小
        
        Returns:
            float: 速度标量
        """
        return self._velocity.magnitude()
    
    # ==================== 空中控制 ====================
    
    def apply_aerial_control(self, direction: Vec3, strength: float = 1.0) -> None:
        """
        应用空中方向控制
        
        Requirement 2.4: WHILE the player is airborne 
        THEN the ODM System SHALL allow directional control for aerial maneuvering
        
        Args:
            direction: 控制方向
            strength: 控制强度 (0.0 - 1.0)
        """
        if direction.magnitude() < 0.001:
            return
        
        # 空中控制力度较小
        control_power = 5.0 * strength
        control_force = direction.normalized() * control_power
        
        self._velocity = self._velocity + control_force
    
    # ==================== 状态管理 ====================
    
    def reset(self) -> None:
        """重置ODM系统状态"""
        self._left_hook.reset()
        self._right_hook.reset()
        self._position = Vec3()
        self._velocity = Vec3()
        self._gas_level = self._max_gas
    
    def get_state(self) -> dict:
        """获取当前状态（用于存档）"""
        return {
            'position': {'x': self._position.x, 'y': self._position.y, 'z': self._position.z},
            'velocity': {'x': self._velocity.x, 'y': self._velocity.y, 'z': self._velocity.z},
            'gas_level': self._gas_level,
            'left_hook_attached': self._left_hook.is_attached,
            'right_hook_attached': self._right_hook.is_attached
        }
    
    def set_state(self, state: dict) -> None:
        """设置状态（用于存档恢复）"""
        if 'position' in state:
            pos = state['position']
            self._position = Vec3(pos.get('x', 0), pos.get('y', 0), pos.get('z', 0))
        if 'velocity' in state:
            vel = state['velocity']
            self._velocity = Vec3(vel.get('x', 0), vel.get('y', 0), vel.get('z', 0))
        if 'gas_level' in state:
            self._gas_level = max(0, min(state['gas_level'], self._max_gas))
    
    def __repr__(self) -> str:
        left_status = "attached" if self._left_hook.is_attached else "free"
        right_status = "attached" if self._right_hook.is_attached else "free"
        return (
            f"ODMSystem(pos={self._position}, vel={self._velocity}, "
            f"gas={self._gas_level:.1f}/{self._max_gas}, "
            f"hooks=[L:{left_status}, R:{right_status}])"
        )
