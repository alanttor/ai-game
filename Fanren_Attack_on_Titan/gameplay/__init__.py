"""
游戏玩法模块
"""
from .resource_system import ResourceSystem, ResourceState
from .odm_system import ODMSystem, HookState, Vec3, Surface, HookSide
from .combat_system import CombatSystem, AttackResult, TitanHitbox
from .combat_system import Vec3 as CombatVec3
from .titan_ai import (
    TitanAI, TitanType, TitanState, TitanData, BehaviorPattern,
    create_titan, get_available_titan_types, get_titan_data
)
from .titan_ai import Vec3 as TitanVec3
from .player import Player, PlayerState, QTEEvent
from .player_titan_interaction import PlayerTitanInteraction, InteractionResult

__all__ = [
    'ResourceSystem', 
    'ResourceState',
    'ODMSystem',
    'HookState',
    'Vec3',
    'Surface',
    'HookSide',
    'CombatSystem',
    'AttackResult',
    'TitanHitbox',
    'CombatVec3',
    'TitanAI',
    'TitanType',
    'TitanState',
    'TitanData',
    'BehaviorPattern',
    'TitanVec3',
    'create_titan',
    'get_available_titan_types',
    'get_titan_data',
    'Player',
    'PlayerState',
    'QTEEvent',
    'PlayerTitanInteraction',
    'InteractionResult'
]
