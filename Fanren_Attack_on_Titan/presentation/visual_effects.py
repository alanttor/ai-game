"""
视觉特效系统 - Attack on Titan Fan Game
实现速度线、运动模糊、巨人蒸汽消散效果
Requirements: 8.2, 8.3
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple, Callable
from enum import Enum
import math
import random


class EffectType(Enum):
    """特效类型"""
    SPEED_LINES = "speed_lines"
    MOTION_BLUR = "motion_blur"
    STEAM_DISSOLUTION = "steam_dissolution"
    IMPACT = "impact"
    SLASH_TRAIL = "slash_trail"


@dataclass
class SpeedLineConfig:
    """速度线配置"""
    line_count: int = 20
    min_length: float = 0.3
    max_length: float = 0.8
    line_width: float = 2.0
    color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 0.6)
    fade_speed: float = 2.0
    spawn_radius: float = 0.8  # 相对于屏幕中心的生成半径


@dataclass
class MotionBlurConfig:
    """运动模糊配置"""
    intensity: float = 0.5
    samples: int = 8
    direction_based: bool = True  # 基于运动方向的模糊
    velocity_threshold: float = 10.0  # 触发模糊的速度阈值


@dataclass
class SteamConfig:
    """蒸汽消散配置"""
    particle_count: int = 50
    min_size: float = 0.5
    max_size: float = 2.0
    rise_speed: float = 3.0
    spread_speed: float = 1.5
    lifetime: float = 3.0
    color_start: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 0.8)
    color_end: Tuple[float, float, float, float] = (0.8, 0.8, 0.8, 0.0)


@dataclass
class SpeedLine:
    """单条速度线数据"""
    start_x: float
    start_y: float
    angle: float
    length: float
    alpha: float = 1.0
    active: bool = True


@dataclass
class SteamParticle:
    """蒸汽粒子数据"""
    x: float
    y: float
    z: float
    size: float
    velocity_x: float
    velocity_y: float
    velocity_z: float
    lifetime: float
    max_lifetime: float
    alpha: float = 1.0
    active: bool = True


class SpeedLineEffect:
    """
    速度线特效
    当玩家高速移动时显示动漫风格的速度线
    Requirements: 8.2
    """
    
    def __init__(self, config: Optional[SpeedLineConfig] = None):
        """
        初始化速度线特效
        
        Args:
            config: 速度线配置
        """
        self.config = config if config else SpeedLineConfig()
        self._lines: List[SpeedLine] = []
        self._active = False
        self._intensity = 0.0
    
    def activate(self, intensity: float = 1.0) -> None:
        """
        激活速度线效果
        
        Args:
            intensity: 效果强度 (0.0-1.0)
        """
        self._active = True
        self._intensity = max(0.0, min(1.0, intensity))
        self._spawn_lines()
    
    def deactivate(self) -> None:
        """停用速度线效果"""
        self._active = False
    
    def _spawn_lines(self) -> None:
        """生成速度线"""
        self._lines.clear()
        line_count = int(self.config.line_count * self._intensity)
        
        for _ in range(line_count):
            # 在屏幕边缘随机生成速度线
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0.5, self.config.spawn_radius)
            
            start_x = math.cos(angle) * radius
            start_y = math.sin(angle) * radius
            
            # 速度线指向屏幕中心
            line_angle = angle + math.pi
            length = random.uniform(self.config.min_length, self.config.max_length)
            
            line = SpeedLine(
                start_x=start_x,
                start_y=start_y,
                angle=line_angle,
                length=length * self._intensity,
                alpha=random.uniform(0.5, 1.0)
            )
            self._lines.append(line)
    
    def update(self, dt: float) -> None:
        """
        更新速度线状态
        
        Args:
            dt: 时间增量(秒)
        """
        if not self._active:
            # 淡出现有速度线
            for line in self._lines:
                line.alpha -= self.config.fade_speed * dt
                if line.alpha <= 0:
                    line.active = False
            self._lines = [l for l in self._lines if l.active]
            return
        
        # 更新现有速度线
        for line in self._lines:
            # 速度线向中心移动
            move_speed = 2.0 * dt
            line.start_x *= (1.0 - move_speed)
            line.start_y *= (1.0 - move_speed)
            
            # 检查是否到达中心
            if abs(line.start_x) < 0.1 and abs(line.start_y) < 0.1:
                line.active = False
        
        # 移除不活跃的速度线
        self._lines = [l for l in self._lines if l.active]
        
        # 补充新的速度线
        if len(self._lines) < self.config.line_count * self._intensity:
            self._spawn_single_line()
    
    def _spawn_single_line(self) -> None:
        """生成单条速度线"""
        angle = random.uniform(0, 2 * math.pi)
        radius = self.config.spawn_radius
        
        line = SpeedLine(
            start_x=math.cos(angle) * radius,
            start_y=math.sin(angle) * radius,
            angle=angle + math.pi,
            length=random.uniform(self.config.min_length, self.config.max_length) * self._intensity,
            alpha=random.uniform(0.5, 1.0)
        )
        self._lines.append(line)
    
    def get_lines(self) -> List[SpeedLine]:
        """获取当前所有速度线"""
        return self._lines.copy()
    
    def is_active(self) -> bool:
        """检查效果是否激活"""
        return self._active
    
    def get_line_count(self) -> int:
        """获取当前速度线数量"""
        return len(self._lines)
    
    def set_intensity(self, intensity: float) -> None:
        """设置效果强度"""
        self._intensity = max(0.0, min(1.0, intensity))


class MotionBlurEffect:
    """
    运动模糊特效
    当玩家高速移动时产生运动模糊效果
    Requirements: 8.2
    """
    
    def __init__(self, config: Optional[MotionBlurConfig] = None):
        """
        初始化运动模糊特效
        
        Args:
            config: 运动模糊配置
        """
        self.config = config if config else MotionBlurConfig()
        self._active = False
        self._current_intensity = 0.0
        self._velocity = (0.0, 0.0, 0.0)
        self._blur_direction = (0.0, 0.0)
    
    def update(self, velocity: Tuple[float, float, float], dt: float) -> None:
        """
        根据速度更新运动模糊
        
        Args:
            velocity: 当前速度向量 (x, y, z)
            dt: 时间增量(秒)
        """
        self._velocity = velocity
        speed = math.sqrt(velocity[0]**2 + velocity[1]**2 + velocity[2]**2)
        
        # 计算模糊强度
        if speed > self.config.velocity_threshold:
            target_intensity = min(1.0, (speed - self.config.velocity_threshold) / 
                                   (self.config.velocity_threshold * 2))
            self._active = True
        else:
            target_intensity = 0.0
            self._active = False
        
        # 平滑过渡
        lerp_speed = 5.0 * dt
        self._current_intensity += (target_intensity - self._current_intensity) * lerp_speed
        
        # 计算模糊方向(基于速度方向)
        if self.config.direction_based and speed > 0.1:
            # 将3D速度投影到2D屏幕空间
            self._blur_direction = (
                velocity[0] / speed,
                velocity[1] / speed
            )
    
    def get_blur_params(self) -> Dict[str, Any]:
        """
        获取模糊参数
        
        Returns:
            Dict: 包含强度、方向、采样数的字典
        """
        return {
            'intensity': self._current_intensity * self.config.intensity,
            'direction': self._blur_direction,
            'samples': self.config.samples,
            'active': self._active
        }
    
    def is_active(self) -> bool:
        """检查效果是否激活"""
        return self._active
    
    def get_intensity(self) -> float:
        """获取当前模糊强度"""
        return self._current_intensity
    
    def set_velocity_threshold(self, threshold: float) -> None:
        """设置触发模糊的速度阈值"""
        self.config.velocity_threshold = max(0.1, threshold)


class SteamDissolutionEffect:
    """
    蒸汽消散特效
    巨人死亡时的蒸汽消散效果
    Requirements: 8.3
    """
    
    def __init__(self, config: Optional[SteamConfig] = None):
        """
        初始化蒸汽消散特效
        
        Args:
            config: 蒸汽配置
        """
        self.config = config if config else SteamConfig()
        self._particles: List[SteamParticle] = []
        self._active = False
        self._origin = (0.0, 0.0, 0.0)
    
    def spawn(self, position: Tuple[float, float, float], 
              scale: float = 1.0) -> None:
        """
        在指定位置生成蒸汽效果
        
        Args:
            position: 生成位置 (x, y, z)
            scale: 效果缩放(基于巨人大小)
        """
        self._active = True
        self._origin = position
        self._particles.clear()
        
        particle_count = int(self.config.particle_count * scale)
        
        for _ in range(particle_count):
            # 在原点周围随机生成粒子
            offset_x = random.uniform(-1.0, 1.0) * scale
            offset_y = random.uniform(0.0, 2.0) * scale
            offset_z = random.uniform(-1.0, 1.0) * scale
            
            # 随机速度(主要向上)
            vel_x = random.uniform(-1.0, 1.0) * self.config.spread_speed
            vel_y = random.uniform(0.5, 1.0) * self.config.rise_speed
            vel_z = random.uniform(-1.0, 1.0) * self.config.spread_speed
            
            particle = SteamParticle(
                x=position[0] + offset_x,
                y=position[1] + offset_y,
                z=position[2] + offset_z,
                size=random.uniform(self.config.min_size, self.config.max_size) * scale,
                velocity_x=vel_x,
                velocity_y=vel_y,
                velocity_z=vel_z,
                lifetime=self.config.lifetime,
                max_lifetime=self.config.lifetime,
                alpha=1.0
            )
            self._particles.append(particle)
    
    def update(self, dt: float) -> None:
        """
        更新蒸汽粒子
        
        Args:
            dt: 时间增量(秒)
        """
        if not self._active:
            return
        
        for particle in self._particles:
            if not particle.active:
                continue
            
            # 更新位置
            particle.x += particle.velocity_x * dt
            particle.y += particle.velocity_y * dt
            particle.z += particle.velocity_z * dt
            
            # 粒子逐渐变大(蒸汽扩散)
            particle.size += 0.5 * dt
            
            # 速度逐渐减慢
            particle.velocity_x *= 0.98
            particle.velocity_z *= 0.98
            
            # 更新生命周期
            particle.lifetime -= dt
            
            # 计算透明度(基于生命周期)
            life_ratio = particle.lifetime / particle.max_lifetime
            particle.alpha = life_ratio
            
            # 检查是否过期
            if particle.lifetime <= 0:
                particle.active = False
        
        # 移除不活跃的粒子
        self._particles = [p for p in self._particles if p.active]
        
        # 如果所有粒子都消失,停用效果
        if len(self._particles) == 0:
            self._active = False
    
    def get_particles(self) -> List[SteamParticle]:
        """获取当前所有粒子"""
        return self._particles.copy()
    
    def is_active(self) -> bool:
        """检查效果是否激活"""
        return self._active
    
    def get_particle_count(self) -> int:
        """获取当前粒子数量"""
        return len(self._particles)
    
    def get_particle_color(self, particle: SteamParticle) -> Tuple[float, float, float, float]:
        """
        获取粒子当前颜色(基于生命周期插值)
        
        Args:
            particle: 蒸汽粒子
            
        Returns:
            Tuple: RGBA颜色值
        """
        life_ratio = particle.lifetime / particle.max_lifetime
        
        # 在起始颜色和结束颜色之间插值
        r = self.config.color_start[0] * life_ratio + self.config.color_end[0] * (1 - life_ratio)
        g = self.config.color_start[1] * life_ratio + self.config.color_end[1] * (1 - life_ratio)
        b = self.config.color_start[2] * life_ratio + self.config.color_end[2] * (1 - life_ratio)
        a = self.config.color_start[3] * life_ratio + self.config.color_end[3] * (1 - life_ratio)
        
        return (r, g, b, a * particle.alpha)


class SlashTrailEffect:
    """
    斩击轨迹特效
    攻击时的刀光效果
    """
    
    @dataclass
    class TrailPoint:
        """轨迹点"""
        x: float
        y: float
        z: float
        alpha: float
        time: float
    
    def __init__(self, trail_length: int = 10, fade_time: float = 0.3):
        """
        初始化斩击轨迹
        
        Args:
            trail_length: 轨迹点数量
            fade_time: 淡出时间
        """
        self.trail_length = trail_length
        self.fade_time = fade_time
        self._points: List[SlashTrailEffect.TrailPoint] = []
        self._active = False
        self._color = (1.0, 1.0, 1.0, 0.8)
    
    def start_trail(self, color: Optional[Tuple[float, float, float, float]] = None) -> None:
        """开始记录轨迹"""
        self._active = True
        self._points.clear()
        if color:
            self._color = color
    
    def add_point(self, position: Tuple[float, float, float]) -> None:
        """
        添加轨迹点
        
        Args:
            position: 位置 (x, y, z)
        """
        if not self._active:
            return
        
        point = SlashTrailEffect.TrailPoint(
            x=position[0],
            y=position[1],
            z=position[2],
            alpha=1.0,
            time=0.0
        )
        self._points.append(point)
        
        # 限制轨迹长度
        if len(self._points) > self.trail_length:
            self._points.pop(0)
    
    def end_trail(self) -> None:
        """结束轨迹记录"""
        self._active = False
    
    def update(self, dt: float) -> None:
        """更新轨迹"""
        for point in self._points:
            point.time += dt
            point.alpha = max(0.0, 1.0 - point.time / self.fade_time)
        
        # 移除完全淡出的点
        self._points = [p for p in self._points if p.alpha > 0]
    
    def get_points(self) -> List['SlashTrailEffect.TrailPoint']:
        """获取轨迹点"""
        return self._points.copy()
    
    def is_active(self) -> bool:
        """检查是否正在记录"""
        return self._active
    
    def get_color(self) -> Tuple[float, float, float, float]:
        """获取轨迹颜色"""
        return self._color


class VisualEffectsManager:
    """
    视觉特效管理器
    统一管理所有视觉特效
    """
    
    def __init__(self):
        """初始化特效管理器"""
        self.speed_lines = SpeedLineEffect()
        self.motion_blur = MotionBlurEffect()
        self.steam_effects: Dict[int, SteamDissolutionEffect] = {}
        self.slash_trails: Dict[int, SlashTrailEffect] = {}
        self._next_effect_id = 0
    
    def update(self, dt: float, player_velocity: Optional[Tuple[float, float, float]] = None) -> None:
        """
        更新所有特效
        
        Args:
            dt: 时间增量(秒)
            player_velocity: 玩家速度(用于速度相关特效)
        """
        # 更新速度线
        self.speed_lines.update(dt)
        
        # 更新运动模糊
        if player_velocity:
            self.motion_blur.update(player_velocity, dt)
        
        # 更新蒸汽效果
        expired_steam = []
        for effect_id, effect in self.steam_effects.items():
            effect.update(dt)
            if not effect.is_active():
                expired_steam.append(effect_id)
        for effect_id in expired_steam:
            del self.steam_effects[effect_id]
        
        # 更新斩击轨迹
        expired_trails = []
        for trail_id, trail in self.slash_trails.items():
            trail.update(dt)
            if not trail.is_active() and len(trail.get_points()) == 0:
                expired_trails.append(trail_id)
        for trail_id in expired_trails:
            del self.slash_trails[trail_id]
    
    def activate_speed_lines(self, intensity: float = 1.0) -> None:
        """激活速度线效果"""
        self.speed_lines.activate(intensity)
    
    def deactivate_speed_lines(self) -> None:
        """停用速度线效果"""
        self.speed_lines.deactivate()
    
    def spawn_titan_steam(self, position: Tuple[float, float, float], 
                          titan_scale: float = 1.0) -> int:
        """
        生成巨人蒸汽消散效果
        
        Args:
            position: 巨人位置
            titan_scale: 巨人大小缩放
            
        Returns:
            int: 效果ID
        """
        effect = SteamDissolutionEffect()
        effect.spawn(position, titan_scale)
        
        effect_id = self._next_effect_id
        self._next_effect_id += 1
        self.steam_effects[effect_id] = effect
        
        return effect_id
    
    def create_slash_trail(self, color: Optional[Tuple[float, float, float, float]] = None) -> int:
        """
        创建斩击轨迹
        
        Args:
            color: 轨迹颜色
            
        Returns:
            int: 轨迹ID
        """
        trail = SlashTrailEffect()
        trail.start_trail(color)
        
        trail_id = self._next_effect_id
        self._next_effect_id += 1
        self.slash_trails[trail_id] = trail
        
        return trail_id
    
    def add_slash_point(self, trail_id: int, position: Tuple[float, float, float]) -> bool:
        """
        向斩击轨迹添加点
        
        Args:
            trail_id: 轨迹ID
            position: 位置
            
        Returns:
            bool: 是否成功添加
        """
        if trail_id not in self.slash_trails:
            return False
        self.slash_trails[trail_id].add_point(position)
        return True
    
    def end_slash_trail(self, trail_id: int) -> bool:
        """
        结束斩击轨迹
        
        Args:
            trail_id: 轨迹ID
            
        Returns:
            bool: 是否成功结束
        """
        if trail_id not in self.slash_trails:
            return False
        self.slash_trails[trail_id].end_trail()
        return True
    
    def get_active_effects_count(self) -> Dict[str, int]:
        """获取活跃特效数量统计"""
        return {
            'speed_lines': self.speed_lines.get_line_count(),
            'steam_effects': len(self.steam_effects),
            'slash_trails': len(self.slash_trails),
            'motion_blur_active': 1 if self.motion_blur.is_active() else 0
        }
    
    def clear_all_effects(self) -> None:
        """清除所有特效"""
        self.speed_lines.deactivate()
        self.steam_effects.clear()
        self.slash_trails.clear()
