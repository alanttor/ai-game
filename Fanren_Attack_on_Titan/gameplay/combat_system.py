"""
战斗系统 - 管理攻击、伤害计算和连击系统
"""
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from enum import Enum
import sys
import os
import time

# 添加父目录到路径以便导入config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GAME_CONFIG


@dataclass
class Vec3:
    """简单的3D向量类"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def distance_to(self, other: 'Vec3') -> float:
        """计算到另一个点的距离"""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return (dx * dx + dy * dy + dz * dz) ** 0.5


@dataclass
class AttackResult:
    """
    攻击结果数据类
    
    Attributes:
        hit: 是否命中
        damage: 造成的伤害
        is_critical: 是否暴击（后颈命中）
        target_part: 命中部位
        killed: 是否击杀
    """
    hit: bool = False
    damage: float = 0.0
    is_critical: bool = False
    target_part: str = ""
    killed: bool = False


class TitanHitbox:
    """
    巨人碰撞箱（用于命中检测）
    
    简化模型：巨人由多个碰撞区域组成
    """
    def __init__(
        self,
        position: Vec3,
        nape_center: Vec3,
        nape_radius: float = 1.0,
        health: float = 100.0
    ):
        """
        初始化巨人碰撞箱
        
        Args:
            position: 巨人位置
            nape_center: 后颈中心位置（相对于巨人位置）
            nape_radius: 后颈碰撞半径
            health: 巨人生命值
        """
        self.position = position
        self.nape_center = nape_center
        self.nape_radius = nape_radius
        self.health = health
        self.max_health = health
        self.is_alive = True
    
    def get_absolute_nape_position(self) -> Vec3:
        """获取后颈的绝对位置"""
        return Vec3(
            self.position.x + self.nape_center.x,
            self.position.y + self.nape_center.y,
            self.position.z + self.nape_center.z
        )
    
    def is_point_in_nape(self, point: Vec3) -> bool:
        """检查点是否在后颈碰撞区域内"""
        nape_pos = self.get_absolute_nape_position()
        distance = point.distance_to(nape_pos)
        return distance <= self.nape_radius
    
    def take_damage(self, damage: float, is_nape_hit: bool) -> bool:
        """
        受到伤害
        
        Args:
            damage: 伤害值
            is_nape_hit: 是否后颈命中
            
        Returns:
            bool: 是否被击杀
        """
        if not self.is_alive:
            return False
        
        self.health -= damage
        
        # 后颈命中直接击杀
        if is_nape_hit:
            self.health = 0
            self.is_alive = False
            return True
        
        # 普通伤害检查是否死亡
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            return True
        
        return False



class CombatSystem:
    """
    战斗系统
    
    管理玩家的攻击、伤害计算、连击系统和分数计算。
    
    Requirements:
        3.1 - 后颈攻击造成暴击并触发击杀动画
        3.2 - 非后颈攻击造成减少伤害但不击杀
        3.3 - 连续后颈攻击追踪并显示连击数
        3.4 - 攻击消耗刀刃耐久度
        3.5 - 耐久度为零时禁用攻击
        3.6 - 击杀巨人根据攻击风格和连击倍率奖励分数
    """
    
    # 分数常量
    BASE_KILL_SCORE: float = 100.0
    STYLE_MULTIPLIER_SPEED_THRESHOLD: float = 10.0  # 高速攻击阈值
    STYLE_MULTIPLIER_BONUS: float = 1.5  # 高速攻击额外倍率
    
    def __init__(
        self,
        base_attack_damage: float = None,
        durability_cost: float = None,
        combo_timeout: float = None,
        max_blade_durability: float = None
    ):
        """
        初始化战斗系统
        
        Args:
            base_attack_damage: 基础攻击伤害，默认使用配置值
            durability_cost: 每次攻击消耗的耐久度，默认使用配置值
            combo_timeout: 连击超时时间（秒），默认使用配置值
            max_blade_durability: 最大刀刃耐久度，默认使用配置值
        """
        # 配置值
        self._base_attack_damage = base_attack_damage if base_attack_damage is not None else GAME_CONFIG.BASE_ATTACK_DAMAGE
        self._durability_cost = durability_cost if durability_cost is not None else GAME_CONFIG.DURABILITY_COST_PER_ATTACK
        self._combo_timeout = combo_timeout if combo_timeout is not None else GAME_CONFIG.COMBO_TIMEOUT
        self._max_blade_durability = max_blade_durability if max_blade_durability is not None else GAME_CONFIG.MAX_BLADE_DURABILITY
        
        # 战斗状态
        self._blade_durability: float = self._max_blade_durability
        self._combo_count: int = 0
        self._last_kill_time: float = 0.0
        self._total_score: int = 0
        self._attack_enabled: bool = True
        
        # 风格倍率（基于攻击速度）
        self._current_style_multiplier: float = 1.0
    
    # ==================== 属性访问器 ====================
    
    @property
    def blade_durability(self) -> float:
        """当前刀刃耐久度"""
        return self._blade_durability
    
    @property
    def combo_count(self) -> int:
        """当前连击数"""
        return self._combo_count
    
    @property
    def total_score(self) -> int:
        """总分数"""
        return self._total_score
    
    @property
    def attack_enabled(self) -> bool:
        """攻击是否可用"""
        return self._attack_enabled and self._blade_durability > 0
    
    @property
    def durability_cost(self) -> float:
        """每次攻击消耗的耐久度"""
        return self._durability_cost
    
    @property
    def max_blade_durability(self) -> float:
        """最大刀刃耐久度"""
        return self._max_blade_durability
    
    # ==================== 核心战斗方法 ====================
    
    def check_nape_hit(self, titan: TitanHitbox, hit_point: Vec3) -> bool:
        """
        检查是否命中后颈
        
        Args:
            titan: 巨人碰撞箱
            hit_point: 攻击命中点
            
        Returns:
            bool: 是否命中后颈
            
        Requirements: 3.1 - 后颈命中判定
        """
        if titan is None or hit_point is None:
            return False
        return titan.is_point_in_nape(hit_point)
    
    def calculate_damage(self, is_nape: bool, speed: float = 0.0) -> float:
        """
        计算伤害值
        
        Args:
            is_nape: 是否后颈命中
            speed: 攻击时的移动速度
            
        Returns:
            float: 计算后的伤害值
            
        Requirements: 3.1, 3.2 - 后颈暴击伤害 vs 普通伤害
        """
        base_damage = self._base_attack_damage
        
        # 后颈命中造成致命伤害（实际上会直接击杀）
        if is_nape:
            # 后颈命中伤害 = 基础伤害 * 10（确保击杀）
            damage = base_damage * 10.0
        else:
            # 非后颈命中造成减少伤害
            damage = base_damage * 0.3
        
        # 速度加成
        if speed > self.STYLE_MULTIPLIER_SPEED_THRESHOLD:
            damage *= self.STYLE_MULTIPLIER_BONUS
            self._current_style_multiplier = self.STYLE_MULTIPLIER_BONUS
        else:
            self._current_style_multiplier = 1.0
        
        return damage
    
    def perform_slash(
        self,
        titan: TitanHitbox,
        hit_point: Vec3,
        attack_speed: float = 0.0
    ) -> AttackResult:
        """
        执行斩击攻击
        
        Args:
            titan: 目标巨人
            hit_point: 攻击命中点
            attack_speed: 攻击时的移动速度
            
        Returns:
            AttackResult: 攻击结果
            
        Requirements: 
            3.1 - 后颈攻击造成暴击和击杀
            3.2 - 非后颈攻击造成减少伤害
            3.4 - 攻击消耗刀刃耐久度
            3.5 - 耐久度为零时禁用攻击
        """
        result = AttackResult()
        
        # 检查攻击是否可用 (Requirement 3.5)
        if not self.attack_enabled:
            return result
        
        # 检查目标有效性
        if titan is None or not titan.is_alive:
            return result
        
        # 消耗刀刃耐久度 (Requirement 3.4)
        self._blade_durability -= self._durability_cost
        if self._blade_durability < 0:
            self._blade_durability = 0
        
        # 命中判定
        result.hit = True
        
        # 检查后颈命中 (Requirement 3.1)
        is_nape_hit = self.check_nape_hit(titan, hit_point)
        result.is_critical = is_nape_hit
        result.target_part = "nape" if is_nape_hit else "body"
        
        # 计算伤害
        damage = self.calculate_damage(is_nape_hit, attack_speed)
        result.damage = damage
        
        # 应用伤害并检查击杀
        killed = titan.take_damage(damage, is_nape_hit)
        result.killed = killed
        
        # 如果击杀，更新连击和分数 (Requirement 3.3, 3.6)
        if killed:
            self._update_combo_on_kill()
            score = self._calculate_kill_score()
            self._total_score += score
        
        return result
    
    # ==================== 连击系统 ====================
    
    def _update_combo_on_kill(self) -> None:
        """击杀时更新连击计数"""
        current_time = time.time()
        
        # 检查是否在连击时间窗口内
        if current_time - self._last_kill_time <= self._combo_timeout:
            self._combo_count += 1
        else:
            # 连击中断，重新开始
            self._combo_count = 1
        
        self._last_kill_time = current_time
    
    def update_combo(self, dt: float) -> None:
        """
        更新连击状态（每帧调用）
        
        Args:
            dt: 帧间隔时间
            
        Requirements: 3.3 - 连击计数追踪
        """
        # 检查连击是否超时
        if self._combo_count > 0:
            current_time = time.time()
            if current_time - self._last_kill_time > self._combo_timeout:
                self._combo_count = 0
    
    def reset_combo(self) -> None:
        """重置连击计数"""
        self._combo_count = 0
        self._last_kill_time = 0.0
    
    # ==================== 分数系统 ====================
    
    def get_score_multiplier(self) -> float:
        """
        获取当前分数倍率
        
        基于连击数和攻击风格计算倍率
        
        Returns:
            float: 分数倍率
            
        Requirements: 3.6 - 基于攻击风格和连击倍率计算分数
        """
        # 连击倍率：每次连击增加0.1倍率，最高3倍
        combo_multiplier = min(1.0 + (self._combo_count - 1) * 0.1, 3.0) if self._combo_count > 0 else 1.0
        
        # 风格倍率
        style_multiplier = self._current_style_multiplier
        
        return combo_multiplier * style_multiplier
    
    def _calculate_kill_score(self) -> int:
        """
        计算击杀分数
        
        Returns:
            int: 击杀获得的分数
        """
        multiplier = self.get_score_multiplier()
        score = int(self.BASE_KILL_SCORE * multiplier)
        return score
    
    # ==================== 刀刃管理 ====================
    
    def restore_blade_durability(self) -> None:
        """
        恢复刀刃耐久度（切换刀刃时调用）
        
        Requirements: 4.5 - 切换刀刃恢复耐久度
        """
        self._blade_durability = self._max_blade_durability
    
    def set_blade_durability(self, durability: float) -> None:
        """
        设置刀刃耐久度（用于存档恢复或测试）
        
        Args:
            durability: 新的耐久度值
        """
        self._blade_durability = max(0, min(durability, self._max_blade_durability))
    
    # ==================== 状态管理 ====================
    
    def get_state(self) -> dict:
        """
        获取战斗系统状态（用于存档）
        
        Returns:
            dict: 战斗系统状态
        """
        return {
            'blade_durability': self._blade_durability,
            'combo_count': self._combo_count,
            'total_score': self._total_score
        }
    
    def set_state(self, state: dict) -> None:
        """
        设置战斗系统状态（用于存档恢复）
        
        Args:
            state: 战斗系统状态
        """
        self._blade_durability = state.get('blade_durability', self._max_blade_durability)
        self._combo_count = state.get('combo_count', 0)
        self._total_score = state.get('total_score', 0)
    
    def reset(self) -> None:
        """重置战斗系统到初始状态"""
        self._blade_durability = self._max_blade_durability
        self._combo_count = 0
        self._last_kill_time = 0.0
        self._total_score = 0
        self._current_style_multiplier = 1.0
    
    def __repr__(self) -> str:
        return (
            f"CombatSystem(durability={self._blade_durability:.1f}/{self._max_blade_durability}, "
            f"combo={self._combo_count}, score={self._total_score})"
        )
