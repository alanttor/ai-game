"""
巨人AI系统 - 管理巨人行为、检测和攻击逻辑

Requirements:
    5.1 - 巨人生成时根据类型分配行为模式
    5.2 - 玩家在检测范围内时追踪玩家
    5.3 - 被攻击时触发防御或攻击响应
    5.4 - 抓取攻击带有预警动画
    5.5 - 被抓取时触发QTE
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable
from enum import Enum
import json
import os
import sys
import math
import random

# 添加父目录到路径以便导入config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GAME_CONFIG, PATH_CONFIG


class TitanType(Enum):
    """
    巨人类型枚举
    
    Requirements: 5.1 - 根据类型分配行为模式
    """
    NORMAL = "normal"
    ABNORMAL = "abnormal"
    SPECIAL = "special"


class TitanState(Enum):
    """
    巨人状态枚举
    
    用于状态机管理巨人行为
    """
    IDLE = "idle"           # 空闲状态
    WANDERING = "wandering" # 徘徊状态
    PURSUING = "pursuing"   # 追踪状态
    ATTACKING = "attacking" # 攻击状态
    GRABBING = "grabbing"   # 抓取状态
    STUNNED = "stunned"     # 眩晕状态
    DYING = "dying"         # 死亡状态


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
        return math.sqrt(dx * dx + dy * dy + dz * dz)
    
    def direction_to(self, other: 'Vec3') -> 'Vec3':
        """计算指向另一个点的单位方向向量"""
        dx = other.x - self.x
        dy = other.y - self.y
        dz = other.z - self.z
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        if length == 0:
            return Vec3(0, 0, 0)
        return Vec3(dx / length, dy / length, dz / length)
    
    def __add__(self, other: 'Vec3') -> 'Vec3':
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __mul__(self, scalar: float) -> 'Vec3':
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def magnitude(self) -> float:
        """计算向量长度"""
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)



@dataclass
class BehaviorPattern:
    """
    行为模式数据类
    
    定义巨人的行为特征
    """
    name: str
    description: str
    pursuit_style: str
    attack_frequency: float
    retreat_threshold: float
    direction_change_interval: float = 0.0
    preferred_distance: float = 0.0


@dataclass
class TitanData:
    """
    巨人数据类
    
    存储从JSON加载的巨人配置
    """
    id: str
    type: TitanType
    name: str
    name_en: str
    height: float
    health: float
    speed: float
    detection_range: float
    attack_range: float
    attack_damage: float
    grab_chance: float
    response_time: float
    behavior: str
    model: str
    description: str
    # 特殊属性（可选）
    armor_reduction: float = 0.0
    weak_points: List[str] = field(default_factory=list)
    steam_damage: float = 0.0
    steam_range: float = 0.0
    can_harden: bool = False
    can_call_titans: bool = False
    throw_damage: float = 0.0
    throw_range: float = 0.0


class TitanAI:
    """
    巨人AI行为系统
    
    管理单个巨人的行为逻辑，包括检测、追踪、攻击等。
    
    Requirements:
        5.1 - 根据巨人类型分配行为模式
        5.2 - 检测范围内追踪玩家
        5.3 - 被攻击时触发响应
        5.4 - 抓取攻击带有预警
        5.5 - 被抓取触发QTE
    """
    
    # 类级别的数据缓存
    _titan_data_cache: Dict[str, TitanData] = {}
    _behavior_patterns_cache: Dict[str, BehaviorPattern] = {}
    _data_loaded: bool = False
    
    def __init__(
        self,
        titan_type_id: str,
        position: Vec3 = None,
        data_file: str = None
    ):
        """
        初始化巨人AI
        
        Args:
            titan_type_id: 巨人类型ID（如 "normal_3m", "abnormal_7m"）
            position: 初始位置
            data_file: 数据文件路径（可选，用于测试）
        """
        # 加载数据
        if not TitanAI._data_loaded:
            TitanAI._load_titan_data(data_file)
        
        # 获取巨人配置
        if titan_type_id not in TitanAI._titan_data_cache:
            raise ValueError(f"Unknown titan type: {titan_type_id}")
        
        self._data: TitanData = TitanAI._titan_data_cache[titan_type_id]
        self._behavior: BehaviorPattern = TitanAI._behavior_patterns_cache.get(
            self._data.behavior,
            BehaviorPattern("standard", "默认行为", "direct", 1.0, 0.0)
        )
        
        # 状态
        self._current_state: TitanState = TitanState.IDLE
        self._previous_state: TitanState = TitanState.IDLE
        self._position: Vec3 = position if position else Vec3(0, 0, 0)
        self._target: Optional[Vec3] = None
        self._target_entity: Any = None  # 玩家实体引用
        
        # 生命值
        self._health: float = self._data.health
        self._max_health: float = self._data.health
        self._is_alive: bool = True
        
        # 后颈碰撞箱（相对于巨人位置）
        self._nape_offset: Vec3 = Vec3(0, self._data.height * 0.9, -0.5)
        self._nape_radius: float = self._data.height * 0.1
        
        # 计时器
        self._state_timer: float = 0.0
        self._attack_cooldown: float = 0.0
        self._response_timer: float = 0.0
        self._direction_change_timer: float = 0.0
        self._stun_timer: float = 0.0
        
        # 移动
        self._velocity: Vec3 = Vec3(0, 0, 0)
        self._wander_direction: Vec3 = Vec3(1, 0, 0)
        
        # 回调
        self._on_attack_callback: Optional[Callable] = None
        self._on_grab_callback: Optional[Callable] = None
        self._on_death_callback: Optional[Callable] = None
    
    @classmethod
    def _load_titan_data(cls, data_file: str = None) -> None:
        """
        加载巨人数据文件
        
        Args:
            data_file: 数据文件路径（可选）
        """
        if data_file is None:
            # 尝试多个可能的路径
            possible_paths = [
                PATH_CONFIG.TITANS_FILE,
                os.path.join(os.path.dirname(os.path.dirname(__file__)), PATH_CONFIG.TITANS_FILE),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "data_files", "titans.json"),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    data_file = path
                    break
        
        if data_file is None or not os.path.exists(data_file):
            # 如果文件不存在，使用默认数据
            cls._create_default_data()
            cls._data_loaded = True
            return
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 解析巨人类型
            for titan_id, titan_info in data.get('titan_types', {}).items():
                titan_type = TitanType(titan_info.get('type', 'normal'))
                cls._titan_data_cache[titan_id] = TitanData(
                    id=titan_info.get('id', titan_id),
                    type=titan_type,
                    name=titan_info.get('name', titan_id),
                    name_en=titan_info.get('name_en', titan_id),
                    height=titan_info.get('height', 5),
                    health=titan_info.get('health', 100),
                    speed=titan_info.get('speed', 2.0),
                    detection_range=titan_info.get('detection_range', 30),
                    attack_range=titan_info.get('attack_range', 5),
                    attack_damage=titan_info.get('attack_damage', 20),
                    grab_chance=titan_info.get('grab_chance', 0.1),
                    response_time=titan_info.get('response_time', 1.0),
                    behavior=titan_info.get('behavior', 'standard'),
                    model=titan_info.get('model', ''),
                    description=titan_info.get('description', ''),
                    armor_reduction=titan_info.get('armor_reduction', 0.0),
                    weak_points=titan_info.get('weak_points', []),
                    steam_damage=titan_info.get('steam_damage', 0.0),
                    steam_range=titan_info.get('steam_range', 0.0),
                    can_harden=titan_info.get('can_harden', False),
                    can_call_titans=titan_info.get('can_call_titans', False),
                    throw_damage=titan_info.get('throw_damage', 0.0),
                    throw_range=titan_info.get('throw_range', 0.0),
                )
            
            # 解析行为模式
            for behavior_name, behavior_info in data.get('behavior_patterns', {}).items():
                cls._behavior_patterns_cache[behavior_name] = BehaviorPattern(
                    name=behavior_name,
                    description=behavior_info.get('description', ''),
                    pursuit_style=behavior_info.get('pursuit_style', 'direct'),
                    attack_frequency=behavior_info.get('attack_frequency', 1.0),
                    retreat_threshold=behavior_info.get('retreat_threshold', 0.0),
                    direction_change_interval=behavior_info.get('direction_change_interval', 0.0),
                    preferred_distance=behavior_info.get('preferred_distance', 0.0),
                )
            
            cls._data_loaded = True
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load titan data: {e}")
            cls._create_default_data()
            cls._data_loaded = True
    
    @classmethod
    def _create_default_data(cls) -> None:
        """创建默认巨人数据"""
        cls._titan_data_cache['normal_3m'] = TitanData(
            id='normal_3m',
            type=TitanType.NORMAL,
            name='3米级巨人',
            name_en='3m Titan',
            height=3,
            health=100,
            speed=2.0,
            detection_range=30,
            attack_range=3,
            attack_damage=20,
            grab_chance=0.1,
            response_time=1.0,
            behavior='standard',
            model='',
            description='默认巨人'
        )
        cls._behavior_patterns_cache['standard'] = BehaviorPattern(
            name='standard',
            description='标准行为模式',
            pursuit_style='direct',
            attack_frequency=1.0,
            retreat_threshold=0.0
        )
    
    @classmethod
    def reset_cache(cls) -> None:
        """重置数据缓存（用于测试）"""
        cls._titan_data_cache.clear()
        cls._behavior_patterns_cache.clear()
        cls._data_loaded = False

    
    # ==================== 属性访问器 ====================
    
    @property
    def titan_type(self) -> TitanType:
        """巨人类型"""
        return self._data.type
    
    @property
    def current_state(self) -> TitanState:
        """当前状态"""
        return self._current_state
    
    @property
    def position(self) -> Vec3:
        """当前位置"""
        return self._position
    
    @position.setter
    def position(self, value: Vec3) -> None:
        """设置位置"""
        self._position = value
    
    @property
    def health(self) -> float:
        """当前生命值"""
        return self._health
    
    @property
    def max_health(self) -> float:
        """最大生命值"""
        return self._max_health
    
    @property
    def is_alive(self) -> bool:
        """是否存活"""
        return self._is_alive
    
    @property
    def detection_range(self) -> float:
        """检测范围"""
        return self._data.detection_range
    
    @property
    def attack_range(self) -> float:
        """攻击范围"""
        return self._data.attack_range
    
    @property
    def attack_damage(self) -> float:
        """攻击伤害"""
        return self._data.attack_damage
    
    @property
    def behavior_pattern(self) -> BehaviorPattern:
        """行为模式"""
        return self._behavior
    
    @property
    def data(self) -> TitanData:
        """巨人数据"""
        return self._data
    
    @property
    def nape_position(self) -> Vec3:
        """后颈绝对位置"""
        return Vec3(
            self._position.x + self._nape_offset.x,
            self._position.y + self._nape_offset.y,
            self._position.z + self._nape_offset.z
        )
    
    @property
    def nape_radius(self) -> float:
        """后颈碰撞半径"""
        return self._nape_radius
    
    # ==================== 核心更新方法 ====================
    
    def update(self, dt: float, player_position: Vec3 = None) -> None:
        """
        更新巨人AI（每帧调用）
        
        Args:
            dt: 帧间隔时间
            player_position: 玩家位置
        """
        if not self._is_alive:
            return
        
        # 更新计时器
        self._state_timer += dt
        if self._attack_cooldown > 0:
            self._attack_cooldown -= dt
        if self._response_timer > 0:
            self._response_timer -= dt
        if self._stun_timer > 0:
            self._stun_timer -= dt
            if self._stun_timer <= 0:
                self._change_state(self._previous_state)
        
        # 更新目标位置
        if player_position:
            self._target = player_position
        
        # 根据当前状态执行行为
        self._execute_state_behavior(dt)
    
    def _execute_state_behavior(self, dt: float) -> None:
        """执行当前状态的行为"""
        if self._current_state == TitanState.IDLE:
            self._behavior_idle(dt)
        elif self._current_state == TitanState.WANDERING:
            self._behavior_wandering(dt)
        elif self._current_state == TitanState.PURSUING:
            self._behavior_pursuing(dt)
        elif self._current_state == TitanState.ATTACKING:
            self._behavior_attacking(dt)
        elif self._current_state == TitanState.GRABBING:
            self._behavior_grabbing(dt)
        elif self._current_state == TitanState.STUNNED:
            self._behavior_stunned(dt)
        elif self._current_state == TitanState.DYING:
            self._behavior_dying(dt)
    
    def _change_state(self, new_state: TitanState) -> None:
        """
        切换状态
        
        Args:
            new_state: 新状态
        """
        if new_state == self._current_state:
            return
        
        self._previous_state = self._current_state
        self._current_state = new_state
        self._state_timer = 0.0
    
    # ==================== 检测方法 ====================
    
    def detect_player(self, player_position: Vec3) -> bool:
        """
        检测玩家是否在范围内
        
        Args:
            player_position: 玩家位置
            
        Returns:
            bool: 是否检测到玩家
            
        Requirements: 5.2 - 检测范围内追踪玩家
        """
        if player_position is None:
            return False
        
        distance = self._position.distance_to(player_position)
        detected = distance <= self._data.detection_range
        
        # 如果检测到玩家且当前不在追踪/攻击状态，切换到追踪
        if detected and self._current_state in [TitanState.IDLE, TitanState.WANDERING]:
            self._target = player_position
            self._change_state(TitanState.PURSUING)
        
        return detected
    
    def is_player_in_attack_range(self, player_position: Vec3) -> bool:
        """
        检查玩家是否在攻击范围内
        
        Args:
            player_position: 玩家位置
            
        Returns:
            bool: 是否在攻击范围内
        """
        if player_position is None:
            return False
        
        distance = self._position.distance_to(player_position)
        return distance <= self._data.attack_range
    
    # ==================== 追踪方法 ====================
    
    def pursue_target(self, dt: float = 0.016) -> None:
        """
        追踪目标
        
        Requirements: 5.2 - 追踪玩家
        """
        if self._target is None:
            return
        
        # 计算方向
        direction = self._position.direction_to(self._target)
        
        # 根据行为模式调整追踪方式
        if self._behavior.pursuit_style == 'erratic':
            # 奇行种：随机改变方向
            self._direction_change_timer += dt
            if self._direction_change_timer >= self._behavior.direction_change_interval:
                self._direction_change_timer = 0.0
                # 随机偏移方向
                angle = random.uniform(-math.pi / 4, math.pi / 4)
                cos_a, sin_a = math.cos(angle), math.sin(angle)
                new_x = direction.x * cos_a - direction.z * sin_a
                new_z = direction.x * sin_a + direction.z * cos_a
                direction = Vec3(new_x, direction.y, new_z)
        
        elif self._behavior.pursuit_style == 'maintain_distance':
            # 远程型：保持距离
            distance = self._position.distance_to(self._target)
            if distance < self._behavior.preferred_distance:
                # 后退
                direction = direction * -1
        
        # 移动
        speed = self._data.speed
        self._velocity = direction * speed
        self._position = self._position + (self._velocity * dt)

    
    # ==================== 攻击方法 ====================
    
    def perform_attack(self) -> Dict[str, Any]:
        """
        执行攻击
        
        Returns:
            dict: 攻击信息
            
        Requirements: 5.3 - 被攻击时触发响应
        """
        if self._attack_cooldown > 0:
            return {'success': False, 'reason': 'cooldown'}
        
        if self._current_state == TitanState.STUNNED:
            return {'success': False, 'reason': 'stunned'}
        
        # 设置攻击冷却
        attack_interval = 2.0 / self._behavior.attack_frequency
        self._attack_cooldown = attack_interval
        
        # 切换到攻击状态
        self._change_state(TitanState.ATTACKING)
        
        attack_info = {
            'success': True,
            'damage': self._data.attack_damage,
            'type': 'melee',
            'position': self._position
        }
        
        # 触发回调
        if self._on_attack_callback:
            self._on_attack_callback(attack_info)
        
        return attack_info
    
    def perform_grab(self) -> Dict[str, Any]:
        """
        执行抓取攻击
        
        Returns:
            dict: 抓取信息
            
        Requirements: 5.4 - 抓取攻击带有预警动画
        """
        if self._attack_cooldown > 0:
            return {'success': False, 'reason': 'cooldown'}
        
        if self._current_state == TitanState.STUNNED:
            return {'success': False, 'reason': 'stunned'}
        
        # 检查抓取概率
        if random.random() > self._data.grab_chance:
            return {'success': False, 'reason': 'chance_failed'}
        
        # 设置攻击冷却（抓取冷却更长）
        self._attack_cooldown = 3.0
        
        # 切换到抓取状态
        self._change_state(TitanState.GRABBING)
        
        grab_info = {
            'success': True,
            'damage': self._data.attack_damage * 1.5,
            'type': 'grab',
            'position': self._position,
            'requires_qte': True  # 需要QTE逃脱
        }
        
        # 触发回调
        if self._on_grab_callback:
            self._on_grab_callback(grab_info)
        
        return grab_info
    
    def try_attack_or_grab(self, player_position: Vec3) -> Optional[Dict[str, Any]]:
        """
        尝试攻击或抓取玩家
        
        Args:
            player_position: 玩家位置
            
        Returns:
            攻击/抓取信息，如果无法攻击则返回None
        """
        if not self.is_player_in_attack_range(player_position):
            return None
        
        # 根据抓取概率决定是攻击还是抓取
        if random.random() < self._data.grab_chance:
            return self.perform_grab()
        else:
            return self.perform_attack()
    
    # ==================== 受伤和死亡 ====================
    
    def take_damage(self, damage: float, hit_nape: bool = False) -> bool:
        """
        受到伤害
        
        Args:
            damage: 伤害值
            hit_nape: 是否命中后颈
            
        Returns:
            bool: 是否被击杀
            
        Requirements: 5.3 - 被攻击时触发响应
        """
        if not self._is_alive:
            return False
        
        # 应用护甲减伤（特殊巨人）
        if self._data.armor_reduction > 0 and not hit_nape:
            damage *= (1 - self._data.armor_reduction)
        
        # 后颈命中直接击杀
        if hit_nape:
            self._health = 0
            self._is_alive = False
            self.die()
            return True
        
        # 普通伤害
        self._health -= damage
        
        # 触发响应行为
        self._trigger_damage_response()
        
        # 检查死亡
        if self._health <= 0:
            self._health = 0
            self._is_alive = False
            self.die()
            return True
        
        return False
    
    def _trigger_damage_response(self) -> None:
        """
        触发受伤响应
        
        Requirements: 5.3 - 被攻击时触发防御或攻击响应
        """
        # 设置响应计时器
        self._response_timer = self._data.response_time
        
        # 根据行为模式决定响应
        if self._behavior.retreat_threshold > 0:
            health_ratio = self._health / self._max_health
            if health_ratio < self._behavior.retreat_threshold:
                # 低血量时可能眩晕
                self._stun_timer = 1.0
                self._change_state(TitanState.STUNNED)
                return
        
        # 默认响应：切换到攻击状态
        if self._current_state != TitanState.ATTACKING:
            self._change_state(TitanState.ATTACKING)
    
    def die(self) -> None:
        """
        死亡处理
        """
        self._is_alive = False
        self._change_state(TitanState.DYING)
        
        # 触发回调
        if self._on_death_callback:
            self._on_death_callback(self)
    
    # ==================== 状态行为实现 ====================
    
    def _behavior_idle(self, dt: float) -> None:
        """空闲状态行为"""
        # 一段时间后开始徘徊
        if self._state_timer > 3.0:
            self._change_state(TitanState.WANDERING)
    
    def _behavior_wandering(self, dt: float) -> None:
        """徘徊状态行为"""
        # 随机移动
        self._direction_change_timer += dt
        if self._direction_change_timer > 5.0:
            self._direction_change_timer = 0.0
            angle = random.uniform(0, 2 * math.pi)
            self._wander_direction = Vec3(math.cos(angle), 0, math.sin(angle))
        
        # 缓慢移动
        speed = self._data.speed * 0.3
        self._velocity = self._wander_direction * speed
        self._position = self._position + (self._velocity * dt)
    
    def _behavior_pursuing(self, dt: float) -> None:
        """追踪状态行为"""
        if self._target is None:
            self._change_state(TitanState.WANDERING)
            return
        
        # 检查是否在攻击范围内
        distance = self._position.distance_to(self._target)
        if distance <= self._data.attack_range:
            # 尝试攻击
            if self._attack_cooldown <= 0:
                if random.random() < self._data.grab_chance:
                    self.perform_grab()
                else:
                    self.perform_attack()
        else:
            # 继续追踪
            self.pursue_target(dt)
        
        # 检查是否失去目标（超出检测范围）
        if distance > self._data.detection_range * 1.5:
            self._target = None
            self._change_state(TitanState.WANDERING)
    
    def _behavior_attacking(self, dt: float) -> None:
        """攻击状态行为"""
        # 攻击动画时间
        if self._state_timer > 1.0:
            self._change_state(TitanState.PURSUING)
    
    def _behavior_grabbing(self, dt: float) -> None:
        """抓取状态行为"""
        # 抓取动画时间
        if self._state_timer > 2.0:
            self._change_state(TitanState.PURSUING)
    
    def _behavior_stunned(self, dt: float) -> None:
        """眩晕状态行为"""
        # 眩晕时不做任何事
        pass
    
    def _behavior_dying(self, dt: float) -> None:
        """死亡状态行为"""
        # 死亡动画
        pass

    
    # ==================== 回调设置 ====================
    
    def set_on_attack_callback(self, callback: Callable) -> None:
        """设置攻击回调"""
        self._on_attack_callback = callback
    
    def set_on_grab_callback(self, callback: Callable) -> None:
        """设置抓取回调"""
        self._on_grab_callback = callback
    
    def set_on_death_callback(self, callback: Callable) -> None:
        """设置死亡回调"""
        self._on_death_callback = callback
    
    # ==================== 状态管理 ====================
    
    def get_state(self) -> Dict[str, Any]:
        """
        获取AI状态（用于存档）
        
        Returns:
            dict: AI状态
        """
        return {
            'titan_type_id': self._data.id,
            'position': {'x': self._position.x, 'y': self._position.y, 'z': self._position.z},
            'health': self._health,
            'current_state': self._current_state.value,
            'is_alive': self._is_alive
        }
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """
        设置AI状态（用于存档恢复）
        
        Args:
            state: AI状态
        """
        pos = state.get('position', {})
        self._position = Vec3(pos.get('x', 0), pos.get('y', 0), pos.get('z', 0))
        self._health = state.get('health', self._max_health)
        self._is_alive = state.get('is_alive', True)
        state_str = state.get('current_state', 'idle')
        try:
            self._current_state = TitanState(state_str)
        except ValueError:
            self._current_state = TitanState.IDLE
    
    def reset(self) -> None:
        """重置AI到初始状态"""
        self._health = self._max_health
        self._is_alive = True
        self._current_state = TitanState.IDLE
        self._previous_state = TitanState.IDLE
        self._target = None
        self._state_timer = 0.0
        self._attack_cooldown = 0.0
        self._response_timer = 0.0
        self._stun_timer = 0.0
        self._velocity = Vec3(0, 0, 0)
    
    def __repr__(self) -> str:
        return (
            f"TitanAI(type={self._data.id}, state={self._current_state.value}, "
            f"health={self._health:.1f}/{self._max_health}, alive={self._is_alive})"
        )


# ==================== 工厂函数 ====================

def create_titan(titan_type_id: str, position: Vec3 = None) -> TitanAI:
    """
    创建巨人实例
    
    Args:
        titan_type_id: 巨人类型ID
        position: 初始位置
        
    Returns:
        TitanAI: 巨人AI实例
    """
    return TitanAI(titan_type_id, position)


def get_available_titan_types() -> List[str]:
    """
    获取所有可用的巨人类型
    
    Returns:
        List[str]: 巨人类型ID列表
    """
    if not TitanAI._data_loaded:
        TitanAI._load_titan_data()
    return list(TitanAI._titan_data_cache.keys())


def get_titan_data(titan_type_id: str) -> Optional[TitanData]:
    """
    获取巨人数据
    
    Args:
        titan_type_id: 巨人类型ID
        
    Returns:
        TitanData: 巨人数据，如果不存在则返回None
    """
    if not TitanAI._data_loaded:
        TitanAI._load_titan_data()
    return TitanAI._titan_data_cache.get(titan_type_id)
