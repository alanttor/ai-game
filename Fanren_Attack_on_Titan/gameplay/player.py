"""
玩家实体 - 整合角色、ODM、战斗和资源系统

Requirements:
    1.4 - 角色属性应用到玩家
    2.4 - 空中方向控制
    3.4 - 攻击消耗刀刃耐久
    4.1 - 显示气体和刀刃资源
    3.1 - 后颈攻击击杀巨人
    5.5 - 被抓取触发QTE
    7.5 - 玩家死亡显示游戏结束
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable, TYPE_CHECKING
from enum import Enum
import sys
import os
import math

# 添加父目录到路径以便导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import GAME_CONFIG
from content.character import Character, CharacterStats
from gameplay.odm_system import ODMSystem, Vec3, Surface
from gameplay.combat_system import CombatSystem, AttackResult, TitanHitbox
from gameplay.resource_system import ResourceSystem


class PlayerState(Enum):
    """玩家状态枚举"""
    IDLE = "idle"
    MOVING = "moving"
    AIRBORNE = "airborne"
    SWINGING = "swinging"
    ATTACKING = "attacking"
    GRABBED = "grabbed"
    DEAD = "dead"


@dataclass
class QTEEvent:
    """
    QTE事件数据类
    
    用于被抓取时的快速反应事件
    """
    required_key: str
    time_limit: float
    elapsed_time: float = 0.0
    success: bool = False
    failed: bool = False
    
    def update(self, dt: float) -> None:
        """更新QTE计时"""
        self.elapsed_time += dt
        if self.elapsed_time >= self.time_limit:
            self.failed = True
    
    def check_input(self, key: str) -> bool:
        """检查输入是否正确"""
        if key.lower() == self.required_key.lower():
            self.success = True
            return True
        return False
    
    @property
    def is_active(self) -> bool:
        """QTE是否仍在进行"""
        return not self.success and not self.failed
    
    @property
    def time_remaining(self) -> float:
        """剩余时间"""
        return max(0, self.time_limit - self.elapsed_time)


class Player:
    """
    玩家实体类
    
    整合角色系统、ODM系统、战斗系统和资源系统，
    提供统一的玩家控制接口。
    
    Requirements:
        1.4 - 角色属性修正应用到移动速度、攻击力等
        2.4 - 空中方向控制
        3.4 - 攻击消耗刀刃耐久
        4.1 - 资源显示
        3.1 - 后颈攻击击杀
        5.5 - 被抓取QTE
        7.5 - 死亡处理
    """
    
    # 基础属性
    BASE_MOVE_SPEED: float = 10.0
    BASE_HEALTH: float = 100.0
    GRAVITY: float = 9.8
    GROUND_Y: float = 0.0
    
    # QTE设置
    QTE_TIME_LIMIT: float = 2.0
    QTE_KEYS: List[str] = ['space', 'e', 'q']
    
    def __init__(
        self,
        character: Character = None,
        position: Vec3 = None
    ):
        """
        初始化玩家实体
        
        Args:
            character: 选择的角色（可选，默认使用艾伦）
            position: 初始位置
        """
        # 角色数据
        self._character: Optional[Character] = character
        
        # 位置和运动
        self._position: Vec3 = position if position else Vec3(0, 0, 0)
        self._velocity: Vec3 = Vec3(0, 0, 0)
        self._rotation: float = 0.0  # Y轴旋转角度
        
        # 状态
        self._current_state: PlayerState = PlayerState.IDLE
        self._is_grounded: bool = True
        self._is_alive: bool = True
        
        # 生命值
        self._health: float = self.BASE_HEALTH
        self._max_health: float = self.BASE_HEALTH
        
        # 子系统
        self._odm_system: ODMSystem = ODMSystem()
        self._combat_system: CombatSystem = CombatSystem()
        self._resource_system: ResourceSystem = ResourceSystem()
        
        # 同步ODM系统位置
        self._odm_system.position = self._position
        
        # 应用角色属性修正
        if character:
            self._apply_character_stats(character.stats)
        
        # QTE状态
        self._current_qte: Optional[QTEEvent] = None
        self._grabbing_titan: Any = None  # 抓取玩家的巨人引用
        
        # 回调
        self._on_death_callback: Optional[Callable] = None
        self._on_qte_start_callback: Optional[Callable] = None
        self._on_qte_result_callback: Optional[Callable] = None
        
        # 模型和动画（占位）
        self._model_path: str = ""
        self._current_animation: str = "idle"
        
        # 碰撞检测
        self._collision_radius: float = 0.5
        self._collision_height: float = 1.8
    
    def _apply_character_stats(self, stats: CharacterStats) -> None:
        """
        应用角色属性修正
        
        Requirement 1.4: 角色属性修正应用到玩家
        
        Args:
            stats: 角色属性
        """
        # 应用体力值
        self._max_health = stats.stamina
        self._health = self._max_health
        
        # 应用气体效率到ODM系统
        # 气体效率越高，消耗越少
        if stats.gas_efficiency > 0:
            adjusted_boost_cost = GAME_CONFIG.BOOST_COST / stats.gas_efficiency
            self._odm_system = ODMSystem(boost_cost=adjusted_boost_cost)
            self._odm_system.position = self._position
        
        # 应用攻击力修正到战斗系统
        adjusted_damage = GAME_CONFIG.BASE_ATTACK_DAMAGE * stats.attack_power
        self._combat_system = CombatSystem(base_attack_damage=adjusted_damage)
        
        # 存储速度修正
        self._speed_modifier = stats.speed
    
    # ==================== 属性访问器 ====================
    
    @property
    def character(self) -> Optional[Character]:
        """当前角色"""
        return self._character
    
    @property
    def position(self) -> Vec3:
        """当前位置"""
        return self._position
    
    @position.setter
    def position(self, value: Vec3) -> None:
        """设置位置"""
        self._position = value
        self._odm_system.position = value
    
    @property
    def velocity(self) -> Vec3:
        """当前速度"""
        return self._velocity
    
    @property
    def rotation(self) -> float:
        """Y轴旋转角度"""
        return self._rotation
    
    @rotation.setter
    def rotation(self, value: float) -> None:
        """设置旋转"""
        self._rotation = value
    
    @property
    def current_state(self) -> PlayerState:
        """当前状态"""
        return self._current_state
    
    @property
    def is_alive(self) -> bool:
        """是否存活"""
        return self._is_alive
    
    @property
    def is_grounded(self) -> bool:
        """是否在地面"""
        return self._is_grounded
    
    @property
    def health(self) -> float:
        """当前生命值"""
        return self._health
    
    @property
    def max_health(self) -> float:
        """最大生命值"""
        return self._max_health
    
    @property
    def odm_system(self) -> ODMSystem:
        """ODM系统"""
        return self._odm_system
    
    @property
    def combat_system(self) -> CombatSystem:
        """战斗系统"""
        return self._combat_system
    
    @property
    def resource_system(self) -> ResourceSystem:
        """资源系统"""
        return self._resource_system
    
    @property
    def current_qte(self) -> Optional[QTEEvent]:
        """当前QTE事件"""
        return self._current_qte
    
    # ==================== 资源快捷访问 ====================
    
    @property
    def gas_level(self) -> float:
        """当前气体量"""
        return self._resource_system.gas_level
    
    @property
    def blade_count(self) -> int:
        """当前刀刃数量"""
        return self._resource_system.blade_count
    
    @property
    def blade_durability(self) -> float:
        """当前刀刃耐久度"""
        return self._resource_system.blade_durability
    
    @property
    def combo_count(self) -> int:
        """当前连击数"""
        return self._combat_system.combo_count
    
    @property
    def total_score(self) -> int:
        """总分数"""
        return self._combat_system.total_score
    
    # ==================== 移动控制 ====================
    
    def move(self, direction: Vec3, dt: float) -> None:
        """
        移动玩家
        
        Args:
            direction: 移动方向（归一化）
            dt: 时间步长
        """
        if not self._is_alive or self._current_state == PlayerState.GRABBED:
            return
        
        # 计算移动速度
        speed = self.BASE_MOVE_SPEED
        if self._character:
            speed *= self._character.stats.speed
        
        # 应用移动
        move_velocity = direction * speed
        
        if self._is_grounded:
            self._velocity.x = move_velocity.x
            self._velocity.z = move_velocity.z
            if direction.magnitude() > 0.1:
                self._current_state = PlayerState.MOVING
            else:
                self._current_state = PlayerState.IDLE
        else:
            # 空中控制（减弱）
            air_control = 0.3
            self._velocity.x += move_velocity.x * air_control * dt
            self._velocity.z += move_velocity.z * air_control * dt
    
    def jump(self) -> bool:
        """
        跳跃
        
        Returns:
            bool: 是否成功跳跃
        """
        if not self._is_alive or not self._is_grounded:
            return False
        
        if self._current_state == PlayerState.GRABBED:
            return False
        
        jump_force = 8.0
        self._velocity.y = jump_force
        self._is_grounded = False
        self._current_state = PlayerState.AIRBORNE
        return True
    
    # ==================== ODM控制 ====================
    
    def fire_hook(self, direction: Vec3, side: str = "right") -> bool:
        """
        发射钩锁
        
        Args:
            direction: 发射方向
            side: 钩锁侧面 ("left" 或 "right")
            
        Returns:
            bool: 是否成功附着
        """
        if not self._is_alive or self._current_state == PlayerState.GRABBED:
            return False
        
        success = self._odm_system.fire_hook(direction, side)
        if success:
            self._is_grounded = False
            self._current_state = PlayerState.SWINGING
        return success
    
    def release_hook(self, side: str = "right") -> None:
        """
        释放钩锁
        
        Args:
            side: 钩锁侧面
        """
        self._odm_system.release_hook(side)
        
        # 更新状态
        if not self._odm_system.is_any_hook_attached():
            if self._is_grounded:
                self._current_state = PlayerState.IDLE
            else:
                self._current_state = PlayerState.AIRBORNE
    
    def release_all_hooks(self) -> None:
        """释放所有钩锁"""
        self._odm_system.release_all_hooks()
        if self._is_grounded:
            self._current_state = PlayerState.IDLE
        else:
            self._current_state = PlayerState.AIRBORNE
    
    def activate_boost(self) -> bool:
        """
        激活气体推进
        
        Returns:
            bool: 是否成功激活
        """
        if not self._is_alive or self._current_state == PlayerState.GRABBED:
            return False
        
        # 检查资源系统的气体
        if self._resource_system.gas_level < self._odm_system.boost_cost:
            return False
        
        # 消耗气体
        self._resource_system.consume_gas(self._odm_system.boost_cost)
        
        # 激活推进（ODM系统内部也会消耗，但我们用资源系统管理）
        # 直接应用推进力
        boost_direction = self._get_boost_direction()
        boost_force = boost_direction * self._odm_system.boost_power
        self._velocity = self._velocity + boost_force
        
        return True
    
    def _get_boost_direction(self) -> Vec3:
        """获取推进方向"""
        # 优先使用钩锁方向
        if self._odm_system.left_hook.is_attached:
            direction = self._odm_system.left_hook.attach_point - self._position
            if direction.magnitude() > 0.001:
                return direction.normalized()
        
        if self._odm_system.right_hook.is_attached:
            direction = self._odm_system.right_hook.attach_point - self._position
            if direction.magnitude() > 0.001:
                return direction.normalized()
        
        # 使用当前速度方向
        if self._velocity.magnitude() > 0.001:
            return self._velocity.normalized()
        
        # 默认向前
        return Vec3(0, 0, 1)
    
    def set_surfaces(self, surfaces: List[Surface]) -> None:
        """设置可附着表面"""
        self._odm_system.set_surfaces(surfaces)
    
    # ==================== 战斗控制 ====================

    def attack(self, target: TitanHitbox, hit_point: Vec3) -> AttackResult:
        """
        执行攻击
        
        Args:
            target: 目标巨人
            hit_point: 攻击命中点
            
        Returns:
            AttackResult: 攻击结果
            
        Requirements:
            3.1 - 后颈攻击击杀巨人
            3.4 - 攻击消耗刀刃耐久
        """
        if not self._is_alive or self._current_state == PlayerState.GRABBED:
            return AttackResult()
        
        # 检查刀刃耐久度
        if self._resource_system.blade_durability <= 0:
            return AttackResult()
        
        # 执行攻击
        attack_speed = self._velocity.magnitude()
        result = self._combat_system.perform_slash(target, hit_point, attack_speed)
        
        # 同步刀刃耐久度到资源系统
        if result.hit:
            self._resource_system.consume_blade_durability(
                self._combat_system.durability_cost
            )
            self._current_state = PlayerState.ATTACKING
        
        return result
    
    def switch_blade(self) -> bool:
        """
        切换刀刃
        
        Returns:
            bool: 是否成功切换
        """
        if not self._is_alive:
            return False
        
        success = self._resource_system.switch_blade()
        if success:
            # 同步到战斗系统
            self._combat_system.restore_blade_durability()
        return success
    
    def interact_with_supply_station(self) -> None:
        """与补给站交互，补充资源"""
        if not self._is_alive:
            return
        
        self._resource_system.interact_with_supply_station()
        self._odm_system.refill_gas()
        self._combat_system.restore_blade_durability()
    
    # ==================== 伤害和死亡 ====================
    
    def take_damage(self, damage: float) -> bool:
        """
        受到伤害
        
        Args:
            damage: 伤害值
            
        Returns:
            bool: 是否死亡
            
        Requirement 7.5: 玩家死亡处理
        """
        if not self._is_alive:
            return True
        
        self._health -= damage
        
        if self._health <= 0:
            self._health = 0
            self.die()
            return True
        
        return False
    
    def heal(self, amount: float) -> None:
        """
        恢复生命值
        
        Args:
            amount: 恢复量
        """
        if not self._is_alive:
            return
        
        self._health = min(self._health + amount, self._max_health)
    
    def die(self) -> None:
        """
        死亡处理
        
        Requirement 7.5: 玩家死亡显示游戏结束
        """
        self._is_alive = False
        self._current_state = PlayerState.DEAD
        self._velocity = Vec3(0, 0, 0)
        
        # 释放所有钩锁
        self._odm_system.release_all_hooks()
        
        # 触发回调
        if self._on_death_callback:
            self._on_death_callback(self)
    
    def respawn(self, position: Vec3 = None) -> None:
        """
        重生
        
        Args:
            position: 重生位置
        """
        self._is_alive = True
        self._health = self._max_health
        self._current_state = PlayerState.IDLE
        self._is_grounded = True
        
        if position:
            self._position = position
            self._odm_system.position = position
        
        self._velocity = Vec3(0, 0, 0)
        self._current_qte = None
        self._grabbing_titan = None
    
    # ==================== QTE系统（被抓取） ====================
    
    def on_grabbed(self, titan: Any) -> None:
        """
        被巨人抓取
        
        Args:
            titan: 抓取的巨人
            
        Requirement 5.5: 被抓取触发QTE
        """
        if not self._is_alive:
            return
        
        self._current_state = PlayerState.GRABBED
        self._grabbing_titan = titan
        self._velocity = Vec3(0, 0, 0)
        
        # 释放钩锁
        self._odm_system.release_all_hooks()
        
        # 创建QTE事件
        import random
        required_key = random.choice(self.QTE_KEYS)
        self._current_qte = QTEEvent(
            required_key=required_key,
            time_limit=self.QTE_TIME_LIMIT
        )
        
        # 触发回调
        if self._on_qte_start_callback:
            self._on_qte_start_callback(self._current_qte)
    
    def process_qte_input(self, key: str) -> bool:
        """
        处理QTE输入
        
        Args:
            key: 按下的按键
            
        Returns:
            bool: 是否成功逃脱
        """
        if self._current_qte is None or not self._current_qte.is_active:
            return False
        
        if self._current_qte.check_input(key):
            # QTE成功，逃脱
            self._escape_grab()
            return True
        
        return False
    
    def _escape_grab(self) -> None:
        """逃脱抓取"""
        self._current_state = PlayerState.AIRBORNE
        self._grabbing_titan = None
        
        # 给予逃脱动量
        escape_velocity = Vec3(0, 5, -3)
        self._velocity = escape_velocity
        
        # 触发回调
        if self._on_qte_result_callback:
            self._on_qte_result_callback(True)
        
        self._current_qte = None
    
    def _fail_qte(self) -> None:
        """QTE失败"""
        # 受到伤害
        grab_damage = 30.0
        if self._grabbing_titan and hasattr(self._grabbing_titan, 'attack_damage'):
            grab_damage = self._grabbing_titan.attack_damage * 1.5
        
        self.take_damage(grab_damage)
        
        # 触发回调
        if self._on_qte_result_callback:
            self._on_qte_result_callback(False)
        
        # 如果还活着，恢复状态
        if self._is_alive:
            self._current_state = PlayerState.AIRBORNE
            self._velocity = Vec3(0, 2, -2)
        
        self._grabbing_titan = None
        self._current_qte = None
    
    # ==================== 更新循环 ====================
    
    def update(self, dt: float) -> None:
        """
        每帧更新
        
        Args:
            dt: 时间步长
        """
        if not self._is_alive:
            return
        
        # 更新QTE
        if self._current_qte and self._current_qte.is_active:
            self._current_qte.update(dt)
            if self._current_qte.failed:
                self._fail_qte()
            return  # 被抓取时不更新其他逻辑
        
        # 更新ODM物理
        if self._odm_system.is_any_hook_attached():
            self._odm_system.velocity = self._velocity
            self._odm_system.update_swing_physics(dt)
            self._velocity = self._odm_system.velocity
            self._position = self._odm_system.position
        else:
            # 应用重力
            if not self._is_grounded:
                self._velocity.y -= self.GRAVITY * dt
            
            # 更新位置
            self._position = self._position + self._velocity * dt
        
        # 地面检测
        self._check_ground()
        
        # 更新战斗系统（连击计时）
        self._combat_system.update_combo(dt)
        
        # 更新状态
        self._update_state()
    
    def _check_ground(self) -> None:
        """检测地面碰撞"""
        if self._position.y <= self.GROUND_Y:
            self._position.y = self.GROUND_Y
            self._velocity.y = 0
            self._is_grounded = True
            
            # 着陆时更新状态
            if self._current_state == PlayerState.AIRBORNE:
                if self._velocity.magnitude() > 0.1:
                    self._current_state = PlayerState.MOVING
                else:
                    self._current_state = PlayerState.IDLE
        else:
            self._is_grounded = False
    
    def _update_state(self) -> None:
        """更新玩家状态"""
        if self._current_state == PlayerState.DEAD:
            return
        
        if self._current_state == PlayerState.GRABBED:
            return
        
        if self._odm_system.is_any_hook_attached():
            self._current_state = PlayerState.SWINGING
        elif not self._is_grounded:
            self._current_state = PlayerState.AIRBORNE
        elif self._velocity.magnitude() > 0.1:
            self._current_state = PlayerState.MOVING
        else:
            self._current_state = PlayerState.IDLE
    
    # ==================== 碰撞检测 ====================
    
    def get_collision_bounds(self) -> Dict[str, float]:
        """
        获取碰撞边界
        
        Returns:
            dict: 碰撞边界信息
        """
        return {
            'center_x': self._position.x,
            'center_y': self._position.y + self._collision_height / 2,
            'center_z': self._position.z,
            'radius': self._collision_radius,
            'height': self._collision_height
        }
    
    def check_collision_with_titan(self, titan_position: Vec3, titan_radius: float) -> bool:
        """
        检测与巨人的碰撞
        
        Args:
            titan_position: 巨人位置
            titan_radius: 巨人碰撞半径
            
        Returns:
            bool: 是否碰撞
        """
        # 简化的圆柱体碰撞检测
        dx = self._position.x - titan_position.x
        dz = self._position.z - titan_position.z
        horizontal_distance = math.sqrt(dx * dx + dz * dz)
        
        return horizontal_distance < (self._collision_radius + titan_radius)
    
    def get_attack_hitbox(self) -> Dict[str, Any]:
        """
        获取攻击碰撞箱
        
        Returns:
            dict: 攻击碰撞箱信息
        """
        # 攻击范围在玩家前方
        attack_range = 3.0
        attack_angle = math.radians(self._rotation)
        
        attack_center = Vec3(
            self._position.x + math.sin(attack_angle) * attack_range,
            self._position.y + 1.0,
            self._position.z + math.cos(attack_angle) * attack_range
        )
        
        return {
            'center': attack_center,
            'radius': 2.0,
            'active': self._current_state == PlayerState.ATTACKING
        }
    
    # ==================== 回调设置 ====================
    
    def set_on_death_callback(self, callback: Callable) -> None:
        """设置死亡回调"""
        self._on_death_callback = callback
    
    def set_on_qte_start_callback(self, callback: Callable) -> None:
        """设置QTE开始回调"""
        self._on_qte_start_callback = callback
    
    def set_on_qte_result_callback(self, callback: Callable) -> None:
        """设置QTE结果回调"""
        self._on_qte_result_callback = callback
    
    # ==================== 状态管理 ====================
    
    def get_state(self) -> Dict[str, Any]:
        """
        获取玩家状态（用于存档）
        
        Returns:
            dict: 玩家状态
        """
        return {
            'character_id': self._character.id if self._character else None,
            'position': {
                'x': self._position.x,
                'y': self._position.y,
                'z': self._position.z
            },
            'health': self._health,
            'is_alive': self._is_alive,
            'resource_state': {
                'gas_level': self._resource_system.gas_level,
                'blade_count': self._resource_system.blade_count,
                'blade_durability': self._resource_system.blade_durability
            },
            'combat_state': self._combat_system.get_state(),
            'odm_state': self._odm_system.get_state()
        }
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """
        设置玩家状态（用于存档恢复）
        
        Args:
            state: 玩家状态
        """
        # 位置
        pos = state.get('position', {})
        self._position = Vec3(
            pos.get('x', 0),
            pos.get('y', 0),
            pos.get('z', 0)
        )
        self._odm_system.position = self._position
        
        # 生命值
        self._health = state.get('health', self._max_health)
        self._is_alive = state.get('is_alive', True)
        
        # 资源状态
        resource_state = state.get('resource_state', {})
        from gameplay.resource_system import ResourceState
        self._resource_system.set_state(ResourceState(
            gas_level=resource_state.get('gas_level', self._resource_system.max_gas),
            blade_count=resource_state.get('blade_count', self._resource_system.max_blades),
            blade_durability=resource_state.get('blade_durability', self._resource_system.max_blade_durability)
        ))
        
        # 战斗状态
        combat_state = state.get('combat_state', {})
        self._combat_system.set_state(combat_state)
        
        # ODM状态
        odm_state = state.get('odm_state', {})
        self._odm_system.set_state(odm_state)
        
        # 更新状态
        if not self._is_alive:
            self._current_state = PlayerState.DEAD
        else:
            self._current_state = PlayerState.IDLE
    
    def reset(self) -> None:
        """重置玩家到初始状态"""
        self._health = self._max_health
        self._is_alive = True
        self._current_state = PlayerState.IDLE
        self._is_grounded = True
        self._position = Vec3(0, 0, 0)
        self._velocity = Vec3(0, 0, 0)
        self._rotation = 0.0
        
        self._odm_system.reset()
        self._combat_system.reset()
        self._resource_system = ResourceSystem()
        
        self._current_qte = None
        self._grabbing_titan = None
    
    def __repr__(self) -> str:
        char_name = self._character.name if self._character else "Unknown"
        return (
            f"Player(character={char_name}, state={self._current_state.value}, "
            f"health={self._health:.1f}/{self._max_health}, "
            f"pos={self._position})"
        )
