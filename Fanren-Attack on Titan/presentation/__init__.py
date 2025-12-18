"""
表现层模块
包含图形渲染、视觉特效、UI系统、音频系统
"""
from .graphics import (
    GraphicsSystem,
    CelShadingRenderer,
    OutlineRenderer,
    ShaderConfig,
    RenderMode
)
from .visual_effects import (
    VisualEffectsManager,
    SpeedLineEffect,
    MotionBlurEffect,
    SteamDissolutionEffect,
    SlashTrailEffect,
    EffectType,
    SpeedLineConfig,
    MotionBlurConfig,
    SteamConfig
)
from .audio import (
    AudioSystem,
    AudioConfig,
    SoundCategory,
    MusicMood,
    SoundEffect
)

__all__ = [
    # Graphics
    'GraphicsSystem',
    'CelShadingRenderer',
    'OutlineRenderer',
    'ShaderConfig',
    'RenderMode',
    # Visual Effects
    'VisualEffectsManager',
    'SpeedLineEffect',
    'MotionBlurEffect',
    'SteamDissolutionEffect',
    'SlashTrailEffect',
    'EffectType',
    'SpeedLineConfig',
    'MotionBlurConfig',
    'SteamConfig',
    # Audio
    'AudioSystem',
    'AudioConfig',
    'SoundCategory',
    'MusicMood',
    'SoundEffect',
]
