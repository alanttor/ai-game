"""
玩家与巨人交互系统

处理玩家攻击巨人、被巨人抓取等交互逻辑

Requirements:
    3.1 - 后颈攻击击杀巨人
    5.5 - 被抓取触发QTE
    7.5 - 玩家死亡处理
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Callable, TYPE_CHECKING
import math
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gameplay.player import Player, PlayerState
from gameplay.titan_ai import TitanAI, TitanState
from gameplay.combat_system import AttackResult, TitanHitbox
from gameplay.odm_system import Vec3


@dataclass
class InteractionResult:
    """
    交互结果数据类
    """
    interaction_type: str  # "attack", "grab", "collision"
    success: bool
    damage_dealt: float = 0.0
    damage_received: float = 0.0
    titan_killed: bool = False
    player_grabbed: bool = False
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


class PlayerTitanInteraction:
    """
    玩家与巨人交互管理器
    
    处理玩家与巨人之间的所有交互，包括：
    - 攻击碰撞检测
    - 被抓取QTE
    - 死亡处理
    
    Requirements:
        3.1 - 后颈攻击击杀巨人
        5.5 - 被抓取触发QTE
        7.5 - 玩家死亡处理
    """
    
    # 攻击检测参数
    ATTACK_RANGE: float = 3.0
    ATTACK_ANGLE: float = 90.0  # 攻击扇形角度（度）
    NAPE_HIT_BONUS_RANGE: float = 1.5  # 后颈命中额外范围
    
    def __init__(self, player: Player):
        """
        初始化交互管理器
        
        Args:
            player: 玩家实体
        """
        self._player = player
        self._active_titans: List[TitanAI] = []
        
        # 回调
        self._on_titan_killed_callback: Optional[Callable] = None
        self._on_player_hit_callback: Optional[Callable] = None
        self._on_player_grabbed_callback: Optional[Callable] = None
        self._on_player_death_callback: Optional[Callable] = None
    
    # ==================== 巨人管理 ====================
    
    def set_active_titans(self, titans: List[TitanAI]) -> None:
        """
        设置活跃的巨人列表
        
        Args:
            titans: 巨人列表
        """
        self._active_titans = titans
    
    def add_titan(self, titan: TitanAI) -> None:
        """添加巨人"""
        if titan not in self._active_titans:
            self._active_titans.append(titan)
    
    def remove_titan(self, titan: TitanAI) -> None:
        """移除巨人"""
        if titan in self._active_titans:
            self._active_titans.remove(titan)
    
    def clear_titans(self) -> None:
        """清除所有巨人"""
        self._active_titans.clear()
    
    # ==================== 攻击检测 ====================
    
    def perform_attack(self) -> List[InteractionResult]:
        """
        执行玩家攻击，检测所有可能命中的巨人
        
        Returns:
            List[InteractionResult]: 攻击结果列表
            
        Requirement 3.1: 后颈攻击击杀巨人
        """
        results = []
        
        if not self._player.is_alive:
            return results
        
        if self._player.current_state == PlayerState.GRABBED:
            return results
        
        # 检查刀刃耐久度
        if self._player.blade_durability <= 0:
            return results
        
        # 获取攻击参数
        player_pos = self._player.position
        player_speed = self._player.velocity.magnitude()
        attack_direction = self._get_attack_direction()
        
        # 检测所有在攻击范围内的巨人
        for titan in self._active_titans:
            if not titan.is_alive:
                continue
            
            # 检查是否在攻击范围内
            hit_result = self._check_attack_hit(
                player_pos, attack_direction, titan
            )
            
            if hit_result is not None:
                # 创建TitanHitbox用于战斗系统
                titan_hitbox = self._create_titan_hitbox(titan)
                
                # 执行攻击
                attack_result = self._player.attack(
                    titan_hitbox, hit_result['hit_point']
                )
                
                if attack_result.hit:
                    # 应用伤害到巨人AI
                    killed = titan.take_damage(
                        attack_result.damage,
                        attack_result.is_critical
                    )
                    
                    result = InteractionResult(
                        interaction_type="attack",
                        success=True,
                        damage_dealt=attack_result.damage,
                        titan_killed=killed,
                        details={
                            'titan_id': titan.data.id,
                            'hit_nape': attack_result.is_critical,
                            'combo_count': self._player.combo_count
                        }
                    )
                    results.append(result)
                    
                    # 触发回调
                    if killed and self._on_titan_killed_callback:
                        self._on_titan_killed_callback(titan, attack_result)
                
                # 只攻击一个巨人（单次攻击）
                break
        
        return results
    
    def _get_attack_direction(self) -> Vec3:
        """获取攻击方向"""
        # 基于玩家旋转角度
        angle = math.radians(self._player.rotation)
        return Vec3(
            math.sin(angle),
            0,
            math.cos(angle)
        )
    
    def _check_attack_hit(
        self,
        player_pos: Vec3,
        attack_dir: Vec3,
        titan: TitanAI
    ) -> Optional[Dict[str, Any]]:
        """
        检查攻击是否命中巨人
        
        Args:
            player_pos: 玩家位置
            attack_dir: 攻击方向
            titan: 目标巨人
            
        Returns:
            命中信息字典，如果未命中则返回None
        """
        titan_pos = titan.position
        
        # 计算到巨人的距离
        dx = titan_pos.x - player_pos.x
        dy = titan_pos.y - player_pos.y
        dz = titan_pos.z - player_pos.z
        distance = math.sqrt(dx * dx + dy * dy + dz * dz)
        
        # 检查距离
        if distance > self.ATTACK_RANGE + titan.data.height * 0.5:
            return None
        
        # 检查角度（是否在攻击扇形内）
        if distance > 0.001:
            to_titan = Vec3(dx / distance, dy / distance, dz / distance)
            dot = attack_dir.x * to_titan.x + attack_dir.z * to_titan.z
            angle = math.degrees(math.acos(max(-1, min(1, dot))))
            
            if angle > self.ATTACK_ANGLE / 2:
                return None
        
        # 计算命中点
        # 检查是否能命中后颈
        nape_pos = titan.nape_position
        nape_distance = math.sqrt(
            (nape_pos.x - player_pos.x) ** 2 +
            (nape_pos.y - player_pos.y) ** 2 +
            (nape_pos.z - player_pos.z) ** 2
        )
        
        if nape_distance <= self.ATTACK_RANGE + self.NAPE_HIT_BONUS_RANGE:
            # 命中后颈
            hit_point = nape_pos
        else:
            # 命中身体
            hit_point = Vec3(
                titan_pos.x,
                titan_pos.y + titan.data.height * 0.5,
                titan_pos.z
            )
        
        return {
            'hit_point': hit_point,
            'distance': distance,
            'is_nape_hit': nape_distance <= titan.nape_radius + self.NAPE_HIT_BONUS_RANGE
        }
    
    def _create_titan_hitbox(self, titan: TitanAI) -> TitanHitbox:
        """
        从TitanAI创建TitanHitbox
        
        Args:
            titan: 巨人AI
            
        Returns:
            TitanHitbox: 战斗系统用的碰撞箱
        """
        from gameplay.combat_system import Vec3 as CombatVec3
        
        titan_pos = titan.position
        nape_offset = Vec3(0, titan.data.height * 0.9, -0.5)
        
        return TitanHitbox(
            position=CombatVec3(titan_pos.x, titan_pos.y, titan_pos.z),
            nape_center=CombatVec3(nape_offset.x, nape_offset.y, nape_offset.z),
            nape_radius=titan.nape_radius,
            health=titan.health
        )
    
    # ==================== 巨人攻击检测 ====================
    
    def check_titan_attacks(self, dt: float) -> List[InteractionResult]:
        """
        检测巨人对玩家的攻击
        
        Args:
            dt: 时间步长
            
        Returns:
            List[InteractionResult]: 攻击结果列表
            
        Requirement 5.5: 被抓取触发QTE
        """
        results = []
        
        if not self._player.is_alive:
            return results
        
        if self._player.current_state == PlayerState.GRABBED:
            return results
        
        player_pos = self._player.position
        
        for titan in self._active_titans:
            if not titan.is_alive:
                continue
            
            # 检查巨人是否在攻击状态
            if titan.current_state == TitanState.ATTACKING:
                result = self._handle_titan_attack(titan, player_pos)
                if result:
                    results.append(result)
            
            elif titan.current_state == TitanState.GRABBING:
                result = self._handle_titan_grab(titan, player_pos)
                if result:
                    results.append(result)
        
        return results
    
    def _handle_titan_attack(
        self,
        titan: TitanAI,
        player_pos: Vec3
    ) -> Optional[InteractionResult]:
        """
        处理巨人普通攻击
        
        Args:
            titan: 攻击的巨人
            player_pos: 玩家位置
            
        Returns:
            InteractionResult: 攻击结果
        """
        # 检查玩家是否在攻击范围内
        titan_pos = titan.position
        distance = math.sqrt(
            (player_pos.x - titan_pos.x) ** 2 +
            (player_pos.z - titan_pos.z) ** 2
        )
        
        if distance > titan.attack_range:
            return None
        
        # 玩家受到伤害
        damage = titan.attack_damage
        died = self._player.take_damage(damage)
        
        result = InteractionResult(
            interaction_type="titan_attack",
            success=True,
            damage_received=damage,
            details={
                'titan_id': titan.data.id,
                'player_died': died
            }
        )
        
        # 触发回调
        if self._on_player_hit_callback:
            self._on_player_hit_callback(titan, damage)
        
        if died and self._on_player_death_callback:
            self._on_player_death_callback(self._player)
        
        return result
    
    def _handle_titan_grab(
        self,
        titan: TitanAI,
        player_pos: Vec3
    ) -> Optional[InteractionResult]:
        """
        处理巨人抓取攻击
        
        Args:
            titan: 抓取的巨人
            player_pos: 玩家位置
            
        Returns:
            InteractionResult: 抓取结果
            
        Requirement 5.5: 被抓取触发QTE
        """
        # 检查玩家是否在抓取范围内
        titan_pos = titan.position
        distance = math.sqrt(
            (player_pos.x - titan_pos.x) ** 2 +
            (player_pos.z - titan_pos.z) ** 2
        )
        
        # 抓取范围比普通攻击稍大
        grab_range = titan.attack_range * 1.2
        
        if distance > grab_range:
            return None
        
        # 触发QTE
        self._player.on_grabbed(titan)
        
        result = InteractionResult(
            interaction_type="grab",
            success=True,
            player_grabbed=True,
            details={
                'titan_id': titan.data.id,
                'qte_key': self._player.current_qte.required_key if self._player.current_qte else None
            }
        )
        
        # 触发回调
        if self._on_player_grabbed_callback:
            self._on_player_grabbed_callback(titan)
        
        return result
    
    # ==================== 碰撞检测 ====================
    
    def check_collisions(self) -> List[InteractionResult]:
        """
        检测玩家与巨人的碰撞
        
        Returns:
            List[InteractionResult]: 碰撞结果列表
        """
        results = []
        
        if not self._player.is_alive:
            return results
        
        player_pos = self._player.position
        player_bounds = self._player.get_collision_bounds()
        
        for titan in self._active_titans:
            if not titan.is_alive:
                continue
            
            # 简化的碰撞检测
            titan_pos = titan.position
            titan_radius = titan.data.height * 0.3  # 巨人碰撞半径
            
            if self._player.check_collision_with_titan(titan_pos, titan_radius):
                # 碰撞发生
                result = InteractionResult(
                    interaction_type="collision",
                    success=True,
                    details={
                        'titan_id': titan.data.id,
                        'titan_position': {
                            'x': titan_pos.x,
                            'y': titan_pos.y,
                            'z': titan_pos.z
                        }
                    }
                )
                results.append(result)
        
        return results
    
    # ==================== 更新循环 ====================
    
    def update(self, dt: float) -> Dict[str, List[InteractionResult]]:
        """
        每帧更新交互检测
        
        Args:
            dt: 时间步长
            
        Returns:
            Dict: 各类交互结果
        """
        results = {
            'titan_attacks': [],
            'collisions': []
        }
        
        if not self._player.is_alive:
            return results
        
        # 检测巨人攻击
        results['titan_attacks'] = self.check_titan_attacks(dt)
        
        # 检测碰撞
        results['collisions'] = self.check_collisions()
        
        return results
    
    # ==================== 回调设置 ====================
    
    def set_on_titan_killed_callback(self, callback: Callable) -> None:
        """设置巨人被击杀回调"""
        self._on_titan_killed_callback = callback
    
    def set_on_player_hit_callback(self, callback: Callable) -> None:
        """设置玩家被击中回调"""
        self._on_player_hit_callback = callback
    
    def set_on_player_grabbed_callback(self, callback: Callable) -> None:
        """设置玩家被抓取回调"""
        self._on_player_grabbed_callback = callback
    
    def set_on_player_death_callback(self, callback: Callable) -> None:
        """设置玩家死亡回调"""
        self._on_player_death_callback = callback
    
    # ==================== 辅助方法 ====================
    
    def get_nearest_titan(self) -> Optional[TitanAI]:
        """
        获取最近的巨人
        
        Returns:
            TitanAI: 最近的巨人，如果没有则返回None
        """
        if not self._active_titans:
            return None
        
        player_pos = self._player.position
        nearest = None
        min_distance = float('inf')
        
        for titan in self._active_titans:
            if not titan.is_alive:
                continue
            
            titan_pos = titan.position
            distance = math.sqrt(
                (player_pos.x - titan_pos.x) ** 2 +
                (player_pos.y - titan_pos.y) ** 2 +
                (player_pos.z - titan_pos.z) ** 2
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest = titan
        
        return nearest
    
    def get_titans_in_range(self, range_distance: float) -> List[TitanAI]:
        """
        获取指定范围内的所有巨人
        
        Args:
            range_distance: 范围距离
            
        Returns:
            List[TitanAI]: 范围内的巨人列表
        """
        in_range = []
        player_pos = self._player.position
        
        for titan in self._active_titans:
            if not titan.is_alive:
                continue
            
            titan_pos = titan.position
            distance = math.sqrt(
                (player_pos.x - titan_pos.x) ** 2 +
                (player_pos.y - titan_pos.y) ** 2 +
                (player_pos.z - titan_pos.z) ** 2
            )
            
            if distance <= range_distance:
                in_range.append(titan)
        
        return in_range
    
    def __repr__(self) -> str:
        return (
            f"PlayerTitanInteraction(player={self._player}, "
            f"active_titans={len(self._active_titans)})"
        )
