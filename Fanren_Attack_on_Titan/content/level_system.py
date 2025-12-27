"""
关卡系统模块
实现关卡加载、巨人生成、目标检查等功能

Requirements:
    7.1 - 关卡加载时生成对应环境
    7.2 - 关卡加载时在指定位置生成巨人
    7.4 - 目标完成时触发任务完成
    7.5 - 玩家死亡时显示游戏结束
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Callable
from enum import Enum

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PATH_CONFIG


class ObjectiveType(Enum):
    """目标类型枚举"""
    KILL = "kill"
    SURVIVE = "survive"
    REACH = "reach"
    PROTECT = "protect"
    DEFEAT = "defeat"
    DAMAGE = "damage"
    ESCAPE = "escape"
    INVESTIGATE = "investigate"
    RESCUE = "rescue"


class LevelState(Enum):
    """关卡状态枚举"""
    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SpawnPoint:
    """
    巨人生成点数据类
    
    Requirements: 7.2 - 在指定位置生成巨人
    """
    position: List[float]  # [x, y, z]
    titan_type: str
    delay: float = 0.0
    
    @staticmethod
    def from_dict(data: Dict) -> 'SpawnPoint':
        """从字典创建SpawnPoint"""
        return SpawnPoint(
            position=data.get('position', [0, 0, 0]),
            titan_type=data.get('titan_type', 'normal_3m'),
            delay=float(data.get('delay', 0))
        )
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'position': self.position,
            'titan_type': self.titan_type,
            'delay': self.delay
        }


@dataclass
class Objective:
    """
    任务目标数据类
    
    Requirements: 7.4 - 目标完成触发结果
    """
    id: str
    type: ObjectiveType
    description: str
    # 可选参数
    target: str = ""
    count: int = 0
    time: float = 0.0
    position: List[float] = field(default_factory=lambda: [0, 0, 0])
    radius: float = 10.0
    min_health: float = 0.0
    damage_threshold: float = 0.0
    # 状态
    current_progress: float = 0.0
    is_completed: bool = False
    
    @staticmethod
    def from_dict(data: Dict) -> 'Objective':
        """从字典创建Objective"""
        obj_type_str = data.get('type', 'kill')
        try:
            obj_type = ObjectiveType(obj_type_str)
        except ValueError:
            obj_type = ObjectiveType.KILL
        
        return Objective(
            id=data.get('id', ''),
            type=obj_type,
            description=data.get('description', ''),
            target=data.get('target', ''),
            count=int(data.get('count', 0)),
            time=float(data.get('time', 0)),
            position=data.get('position', [0, 0, 0]),
            radius=float(data.get('radius', 10)),
            min_health=float(data.get('min_health', 0)),
            damage_threshold=float(data.get('damage_threshold', 0))
        )
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'type': self.type.value,
            'description': self.description,
            'target': self.target,
            'count': self.count,
            'time': self.time,
            'position': self.position,
            'radius': self.radius,
            'min_health': self.min_health,
            'damage_threshold': self.damage_threshold,
            'current_progress': self.current_progress,
            'is_completed': self.is_completed
        }


@dataclass
class EnvironmentConfig:
    """环境配置数据类"""
    buildings: bool = True
    walls: bool = True
    trees: bool = False
    tree_density: str = "medium"
    weather: str = "clear"
    time_of_day: str = "afternoon"
    
    @staticmethod
    def from_dict(data: Dict) -> 'EnvironmentConfig':
        """从字典创建EnvironmentConfig"""
        return EnvironmentConfig(
            buildings=data.get('buildings', True),
            walls=data.get('walls', True),
            trees=data.get('trees', False),
            tree_density=data.get('tree_density', 'medium'),
            weather=data.get('weather', 'clear'),
            time_of_day=data.get('time_of_day', 'afternoon')
        )
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'buildings': self.buildings,
            'walls': self.walls,
            'trees': self.trees,
            'tree_density': self.tree_density,
            'weather': self.weather,
            'time_of_day': self.time_of_day
        }


@dataclass
class LevelData:
    """
    关卡数据类
    
    Requirements: 7.1, 7.2 - 关卡环境和巨人生成
    """
    id: str
    name: str
    name_en: str
    environment: str
    description: str
    chapter_id: str
    difficulty: int
    spawn_points: List[SpawnPoint]
    objectives: List[Objective]
    time_limit: float
    environment_config: EnvironmentConfig
    
    @staticmethod
    def from_dict(data: Dict) -> 'LevelData':
        """从字典创建LevelData"""
        spawn_points = [SpawnPoint.from_dict(sp) for sp in data.get('spawn_points', [])]
        objectives = [Objective.from_dict(obj) for obj in data.get('objectives', [])]
        env_config = EnvironmentConfig.from_dict(data.get('environment_config', {}))
        
        return LevelData(
            id=data.get('id', ''),
            name=data.get('name', ''),
            name_en=data.get('name_en', ''),
            environment=data.get('environment', ''),
            description=data.get('description', ''),
            chapter_id=data.get('chapter_id', ''),
            difficulty=int(data.get('difficulty', 1)),
            spawn_points=spawn_points,
            objectives=objectives,
            time_limit=float(data.get('time_limit', 600)),
            environment_config=env_config
        )
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'name_en': self.name_en,
            'environment': self.environment,
            'description': self.description,
            'chapter_id': self.chapter_id,
            'difficulty': self.difficulty,
            'spawn_points': [sp.to_dict() for sp in self.spawn_points],
            'objectives': [obj.to_dict() for obj in self.objectives],
            'time_limit': self.time_limit,
            'environment_config': self.environment_config.to_dict()
        }


@dataclass
class EnvironmentData:
    """环境数据类"""
    id: str
    name: str
    name_en: str
    description: str
    model_path: str
    size: List[float]
    features: List[str]
    odm_anchor_density: str
    
    @staticmethod
    def from_dict(data: Dict) -> 'EnvironmentData':
        """从字典创建EnvironmentData"""
        return EnvironmentData(
            id=data.get('id', ''),
            name=data.get('name', ''),
            name_en=data.get('name_en', ''),
            description=data.get('description', ''),
            model_path=data.get('model_path', ''),
            size=data.get('size', [500, 100, 500]),
            features=data.get('features', []),
            odm_anchor_density=data.get('odm_anchor_density', 'medium')
        )


class LevelNotFoundError(Exception):
    """关卡未找到异常"""
    pass


class LevelLoadError(Exception):
    """关卡加载错误异常"""
    pass


class LevelSystem:
    """
    关卡加载与管理系统
    
    Requirements:
        7.1 - 关卡加载时生成对应环境
        7.2 - 关卡加载时在指定位置生成巨人
        7.4 - 目标完成时触发任务完成
        7.5 - 玩家死亡时显示游戏结束
    """
    
    # 类级别的数据缓存
    _data_file_path: Optional[str] = None
    _level_cache: Optional[Dict] = None
    
    def __init__(self):
        self.current_level: Optional[LevelData] = None
        self.active_titans: List[Any] = []  # 活跃的巨人实体列表
        self.objectives_completed: Set[str] = set()
        self.elapsed_time: float = 0.0
        self.level_state: LevelState = LevelState.NOT_LOADED
        
        # 统计数据
        self.titans_killed: int = 0
        self.damage_dealt: float = 0.0
        self.player_health: float = 100.0
        
        # 待生成的巨人队列
        self._spawn_queue: List[SpawnPoint] = []
        
        # 环境数据
        self._environments: Dict[str, EnvironmentData] = {}
        
        # 回调函数
        self._on_level_complete: Optional[Callable] = None
        self._on_level_fail: Optional[Callable] = None
        self._on_titan_spawn: Optional[Callable] = None
        
        # 加载关卡数据
        self._load_level_data()

    
    @classmethod
    def set_data_file_path(cls, path: str) -> None:
        """设置关卡数据文件路径"""
        cls._data_file_path = path
        cls._level_cache = None
    
    @classmethod
    def _get_data_file_path(cls) -> str:
        """获取关卡数据文件路径"""
        if cls._data_file_path:
            return cls._data_file_path
        # 默认路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, 'data_files', 'levels.json')
    
    @classmethod
    def _load_raw_level_data(cls) -> Dict:
        """加载原始关卡数据（带缓存）"""
        if cls._level_cache is not None:
            return cls._level_cache
        
        data_path = cls._get_data_file_path()
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                cls._level_cache = json.load(f)
                return cls._level_cache
        except FileNotFoundError:
            raise LevelNotFoundError(f"关卡数据文件未找到: {data_path}")
        except json.JSONDecodeError as e:
            raise LevelLoadError(f"关卡数据文件格式错误: {e}")
    
    @classmethod
    def clear_cache(cls) -> None:
        """清除关卡数据缓存"""
        cls._level_cache = None
    
    def _load_level_data(self) -> None:
        """加载关卡数据"""
        try:
            data = self._load_raw_level_data()
            
            # 加载环境数据
            for env_id, env_data in data.get('environments', {}).items():
                self._environments[env_id] = EnvironmentData.from_dict(env_data)
        except (LevelNotFoundError, LevelLoadError):
            # 如果文件不存在，使用空数据
            pass
    
    def load_level(self, level_id: str) -> LevelData:
        """
        加载指定关卡
        
        Args:
            level_id: 关卡ID
            
        Returns:
            LevelData对象
            
        Raises:
            LevelNotFoundError: 关卡未找到
            
        Requirements: 7.1 - 关卡加载时生成对应环境
        """
        self.level_state = LevelState.LOADING
        
        data = self._load_raw_level_data()
        levels = data.get('levels', {})
        
        if level_id not in levels:
            self.level_state = LevelState.NOT_LOADED
            raise LevelNotFoundError(f"关卡未找到: {level_id}")
        
        level_data = LevelData.from_dict(levels[level_id])
        
        # 重置状态
        self.current_level = level_data
        self.active_titans.clear()
        self.objectives_completed.clear()
        self.elapsed_time = 0.0
        self.titans_killed = 0
        self.damage_dealt = 0.0
        self.player_health = 100.0
        
        # 重置目标进度
        for obj in self.current_level.objectives:
            obj.current_progress = 0.0
            obj.is_completed = False
        
        # 准备生成队列
        self._spawn_queue = list(level_data.spawn_points)
        
        self.level_state = LevelState.ACTIVE
        return level_data

    
    def spawn_titan(self, spawn_point: SpawnPoint) -> Optional[Any]:
        """
        在指定位置生成巨人
        
        Args:
            spawn_point: 生成点数据
            
        Returns:
            生成的巨人实体（如果有回调则返回回调结果）
            
        Requirements: 7.2 - 在指定位置生成巨人
        """
        titan_info = {
            'titan_type': spawn_point.titan_type,
            'position': spawn_point.position,
            'delay': spawn_point.delay
        }
        
        # 触发生成回调
        if self._on_titan_spawn:
            titan = self._on_titan_spawn(titan_info)
            if titan:
                self.active_titans.append(titan)
            return titan
        
        # 如果没有回调，只记录信息
        self.active_titans.append(titan_info)
        return titan_info
    
    def update(self, dt: float, player_position: List[float] = None) -> None:
        """
        更新关卡状态（每帧调用）
        
        Args:
            dt: 帧间隔时间
            player_position: 玩家位置 [x, y, z]
        """
        if self.level_state != LevelState.ACTIVE:
            return
        
        if self.current_level is None:
            return
        
        # 更新时间
        self.elapsed_time += dt
        
        # 检查时间限制
        if self.elapsed_time >= self.current_level.time_limit:
            self.fail_level("时间耗尽")
            return
        
        # 处理生成队列
        self._process_spawn_queue()
        
        # 更新目标进度
        self._update_objectives(dt, player_position)
        
        # 检查目标完成
        if self.check_objectives():
            self.complete_level()
    
    def _process_spawn_queue(self) -> None:
        """处理巨人生成队列"""
        remaining = []
        for spawn_point in self._spawn_queue:
            if self.elapsed_time >= spawn_point.delay:
                self.spawn_titan(spawn_point)
            else:
                remaining.append(spawn_point)
        self._spawn_queue = remaining
    
    def _update_objectives(self, dt: float, player_position: List[float] = None) -> None:
        """更新目标进度"""
        if self.current_level is None:
            return
        
        for obj in self.current_level.objectives:
            if obj.is_completed:
                continue
            
            if obj.type == ObjectiveType.SURVIVE:
                # 生存目标：累计时间
                obj.current_progress = min(self.elapsed_time, obj.time)
                if obj.current_progress >= obj.time:
                    obj.is_completed = True
                    self.objectives_completed.add(obj.id)
            
            elif obj.type == ObjectiveType.KILL:
                # 击杀目标：检查击杀数
                obj.current_progress = float(self.titans_killed)
                if obj.current_progress >= obj.count:
                    obj.is_completed = True
                    self.objectives_completed.add(obj.id)
            
            elif obj.type == ObjectiveType.REACH and player_position:
                # 到达目标：检查距离
                distance = self._calculate_distance(player_position, obj.position)
                if distance <= obj.radius:
                    obj.is_completed = True
                    obj.current_progress = 1.0
                    self.objectives_completed.add(obj.id)
            
            elif obj.type == ObjectiveType.DAMAGE:
                # 伤害目标：检查累计伤害
                obj.current_progress = self.damage_dealt
                if obj.current_progress >= obj.damage_threshold:
                    obj.is_completed = True
                    self.objectives_completed.add(obj.id)
            
            elif obj.type == ObjectiveType.PROTECT:
                # 保护目标：检查目标生命值
                # 这里需要外部更新 current_progress
                if obj.current_progress >= obj.min_health:
                    obj.is_completed = True
                    self.objectives_completed.add(obj.id)
            
            elif obj.type == ObjectiveType.ESCAPE and player_position:
                # 逃离目标：检查是否到达安全区域
                distance = self._calculate_distance(player_position, obj.position)
                if distance <= obj.radius:
                    obj.is_completed = True
                    obj.current_progress = 1.0
                    self.objectives_completed.add(obj.id)

    
    def _calculate_distance(self, pos1: List[float], pos2: List[float]) -> float:
        """计算两点之间的距离"""
        import math
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1] if len(pos1) > 1 and len(pos2) > 1 else 0
        dz = pos1[2] - pos2[2] if len(pos1) > 2 and len(pos2) > 2 else 0
        return math.sqrt(dx * dx + dy * dy + dz * dz)
    
    def check_objectives(self) -> bool:
        """
        检查所有目标是否完成
        
        Returns:
            bool: 是否所有目标都已完成
            
        Requirements: 7.4 - 目标完成触发结果
        """
        if self.current_level is None:
            return False
        
        for obj in self.current_level.objectives:
            if not obj.is_completed:
                return False
        
        return True
    
    def complete_level(self) -> Dict:
        """
        完成关卡
        
        Returns:
            dict: 关卡结果数据
            
        Requirements: 7.4 - 目标完成触发结果
        """
        self.level_state = LevelState.COMPLETED
        
        result = {
            'success': True,
            'level_id': self.current_level.id if self.current_level else '',
            'level_name': self.current_level.name if self.current_level else '',
            'elapsed_time': self.elapsed_time,
            'titans_killed': self.titans_killed,
            'damage_dealt': self.damage_dealt,
            'objectives_completed': list(self.objectives_completed),
            'score': self._calculate_score()
        }
        
        # 触发完成回调
        if self._on_level_complete:
            self._on_level_complete(result)
        
        return result
    
    def fail_level(self, reason: str) -> Dict:
        """
        关卡失败
        
        Args:
            reason: 失败原因
            
        Returns:
            dict: 关卡结果数据
            
        Requirements: 7.5 - 玩家死亡时显示游戏结束
        """
        self.level_state = LevelState.FAILED
        
        result = {
            'success': False,
            'level_id': self.current_level.id if self.current_level else '',
            'level_name': self.current_level.name if self.current_level else '',
            'reason': reason,
            'elapsed_time': self.elapsed_time,
            'titans_killed': self.titans_killed,
            'damage_dealt': self.damage_dealt,
            'objectives_completed': list(self.objectives_completed)
        }
        
        # 触发失败回调
        if self._on_level_fail:
            self._on_level_fail(result)
        
        return result
    
    def _calculate_score(self) -> int:
        """计算关卡得分"""
        if self.current_level is None:
            return 0
        
        base_score = 1000
        
        # 击杀加分
        kill_bonus = self.titans_killed * 100
        
        # 时间加分（越快越高）
        time_ratio = 1 - (self.elapsed_time / self.current_level.time_limit)
        time_bonus = int(500 * max(0, time_ratio))
        
        # 难度加成
        difficulty_multiplier = 1 + (self.current_level.difficulty * 0.2)
        
        total_score = int((base_score + kill_bonus + time_bonus) * difficulty_multiplier)
        return total_score

    
    # ==================== 事件处理 ====================
    
    def on_titan_killed(self, titan: Any = None) -> None:
        """
        巨人被击杀时调用
        
        Args:
            titan: 被击杀的巨人
        """
        self.titans_killed += 1
        
        # 从活跃列表中移除
        if titan and titan in self.active_titans:
            self.active_titans.remove(titan)
    
    def on_damage_dealt(self, damage: float, target: str = "") -> None:
        """
        造成伤害时调用
        
        Args:
            damage: 伤害值
            target: 目标标识
        """
        self.damage_dealt += damage
        
        # 更新伤害目标进度
        if self.current_level:
            for obj in self.current_level.objectives:
                if obj.type == ObjectiveType.DAMAGE and obj.target == target:
                    obj.current_progress += damage
    
    def on_player_damaged(self, damage: float) -> None:
        """
        玩家受伤时调用
        
        Args:
            damage: 伤害值
        """
        self.player_health -= damage
        
        if self.player_health <= 0:
            self.fail_level("玩家死亡")
    
    def on_protect_target_damaged(self, target: str, current_health: float) -> None:
        """
        保护目标受伤时调用
        
        Args:
            target: 目标标识
            current_health: 当前生命值
        """
        if self.current_level:
            for obj in self.current_level.objectives:
                if obj.type == ObjectiveType.PROTECT and obj.target == target:
                    obj.current_progress = current_health
                    if current_health < obj.min_health:
                        self.fail_level(f"保护目标 {target} 被摧毁")
    
    # ==================== 回调设置 ====================
    
    def set_on_level_complete(self, callback: Callable) -> None:
        """设置关卡完成回调"""
        self._on_level_complete = callback
    
    def set_on_level_fail(self, callback: Callable) -> None:
        """设置关卡失败回调"""
        self._on_level_fail = callback
    
    def set_on_titan_spawn(self, callback: Callable) -> None:
        """设置巨人生成回调"""
        self._on_titan_spawn = callback
    
    # ==================== 查询方法 ====================
    
    def get_level_info(self, level_id: str) -> Optional[LevelData]:
        """
        获取关卡信息（不加载）
        
        Args:
            level_id: 关卡ID
            
        Returns:
            LevelData对象，如果不存在则返回None
        """
        try:
            data = self._load_raw_level_data()
            levels = data.get('levels', {})
            if level_id in levels:
                return LevelData.from_dict(levels[level_id])
        except (LevelNotFoundError, LevelLoadError):
            pass
        return None
    
    def get_all_levels(self) -> List[LevelData]:
        """获取所有关卡"""
        try:
            data = self._load_raw_level_data()
            levels = data.get('levels', {})
            return [LevelData.from_dict(level_data) for level_data in levels.values()]
        except (LevelNotFoundError, LevelLoadError):
            return []
    
    def get_levels_by_chapter(self, chapter_id: str) -> List[LevelData]:
        """
        获取指定章节的所有关卡
        
        Args:
            chapter_id: 章节ID
            
        Returns:
            该章节的关卡列表
        """
        all_levels = self.get_all_levels()
        return [level for level in all_levels if level.chapter_id == chapter_id]
    
    def get_environment(self, environment_id: str) -> Optional[EnvironmentData]:
        """
        获取环境数据
        
        Args:
            environment_id: 环境ID
            
        Returns:
            EnvironmentData对象，如果不存在则返回None
        """
        return self._environments.get(environment_id)
    
    def get_current_environment(self) -> Optional[EnvironmentData]:
        """获取当前关卡的环境数据"""
        if self.current_level:
            return self.get_environment(self.current_level.environment)
        return None

    
    # ==================== 进度和状态 ====================
    
    def get_objective_progress(self) -> List[Dict]:
        """
        获取所有目标的进度
        
        Returns:
            目标进度列表
        """
        if self.current_level is None:
            return []
        
        progress_list = []
        for obj in self.current_level.objectives:
            progress = {
                'id': obj.id,
                'type': obj.type.value,
                'description': obj.description,
                'is_completed': obj.is_completed,
                'current_progress': obj.current_progress
            }
            
            # 添加目标值
            if obj.type == ObjectiveType.KILL:
                progress['target_value'] = obj.count
            elif obj.type == ObjectiveType.SURVIVE:
                progress['target_value'] = obj.time
            elif obj.type == ObjectiveType.DAMAGE:
                progress['target_value'] = obj.damage_threshold
            else:
                progress['target_value'] = 1.0
            
            progress_list.append(progress)
        
        return progress_list
    
    def get_level_progress(self) -> Dict:
        """
        获取关卡进度信息
        
        Returns:
            关卡进度字典
        """
        return {
            'level_id': self.current_level.id if self.current_level else None,
            'level_name': self.current_level.name if self.current_level else None,
            'state': self.level_state.value,
            'elapsed_time': self.elapsed_time,
            'time_limit': self.current_level.time_limit if self.current_level else 0,
            'time_remaining': (self.current_level.time_limit - self.elapsed_time) if self.current_level else 0,
            'titans_killed': self.titans_killed,
            'active_titans': len(self.active_titans),
            'objectives': self.get_objective_progress(),
            'objectives_completed': len(self.objectives_completed),
            'total_objectives': len(self.current_level.objectives) if self.current_level else 0
        }
    
    def reset(self) -> None:
        """重置关卡系统"""
        self.current_level = None
        self.active_titans.clear()
        self.objectives_completed.clear()
        self.elapsed_time = 0.0
        self.level_state = LevelState.NOT_LOADED
        self.titans_killed = 0
        self.damage_dealt = 0.0
        self.player_health = 100.0
        self._spawn_queue.clear()
    
    def to_save_data(self) -> Dict:
        """转换为存档数据"""
        return {
            'level_id': self.current_level.id if self.current_level else None,
            'elapsed_time': self.elapsed_time,
            'titans_killed': self.titans_killed,
            'damage_dealt': self.damage_dealt,
            'player_health': self.player_health,
            'objectives_completed': list(self.objectives_completed),
            'level_state': self.level_state.value
        }
    
    @staticmethod
    def from_save_data(save_data: Dict) -> 'LevelSystem':
        """从存档数据恢复"""
        level_system = LevelSystem()
        
        level_id = save_data.get('level_id')
        if level_id:
            try:
                level_system.load_level(level_id)
                level_system.elapsed_time = save_data.get('elapsed_time', 0.0)
                level_system.titans_killed = save_data.get('titans_killed', 0)
                level_system.damage_dealt = save_data.get('damage_dealt', 0.0)
                level_system.player_health = save_data.get('player_health', 100.0)
                level_system.objectives_completed = set(save_data.get('objectives_completed', []))
                
                state_str = save_data.get('level_state', 'active')
                try:
                    level_system.level_state = LevelState(state_str)
                except ValueError:
                    level_system.level_state = LevelState.ACTIVE
            except LevelNotFoundError:
                pass
        
        return level_system
