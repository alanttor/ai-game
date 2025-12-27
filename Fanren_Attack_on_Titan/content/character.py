"""
角色系统模块
实现104期训练兵团角色的数据结构和加载逻辑
"""

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class CharacterStats:
    """角色属性数据类"""
    speed: float          # 移动速度修正
    attack_power: float   # 攻击力修正
    stamina: float        # 体力值
    gas_efficiency: float # 气体消耗效率
    
    @staticmethod
    def from_dict(data: Dict) -> 'CharacterStats':
        """从字典创建CharacterStats"""
        return CharacterStats(
            speed=float(data.get('speed', 1.0)),
            attack_power=float(data.get('attack_power', 1.0)),
            stamina=float(data.get('stamina', 100)),
            gas_efficiency=float(data.get('gas_efficiency', 1.0))
        )
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'speed': self.speed,
            'attack_power': self.attack_power,
            'stamina': self.stamina,
            'gas_efficiency': self.gas_efficiency
        }


class CharacterNotFoundError(Exception):
    """角色未找到异常"""
    pass


class Character:
    """可玩角色定义"""
    
    # 角色数据文件路径
    _data_file_path: Optional[str] = None
    _characters_cache: Optional[Dict] = None
    
    def __init__(
        self,
        character_id: str,
        name: str,
        name_en: str,
        portrait: str,
        model_path: str,
        stats: CharacterStats,
        background: str,
        personality_traits: List[str],
        relationships: Dict[str, str]
    ):
        self.id = character_id
        self.name = name
        self.name_en = name_en
        self.portrait = portrait
        self.model_path = model_path
        self.stats = stats
        self.background = background
        self.personality_traits = personality_traits
        self.relationships = relationships
    
    @classmethod
    def set_data_file_path(cls, path: str) -> None:
        """设置角色数据文件路径"""
        cls._data_file_path = path
        cls._characters_cache = None  # 清除缓存
    
    @classmethod
    def _get_data_file_path(cls) -> str:
        """获取角色数据文件路径"""
        if cls._data_file_path:
            return cls._data_file_path
        # 默认路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, 'data_files', 'characters.json')
    
    @classmethod
    def _load_characters_data(cls) -> Dict:
        """加载角色数据（带缓存）"""
        if cls._characters_cache is not None:
            return cls._characters_cache
        
        data_path = cls._get_data_file_path()
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                cls._characters_cache = json.load(f)
                return cls._characters_cache
        except FileNotFoundError:
            raise CharacterNotFoundError(f"角色数据文件未找到: {data_path}")
        except json.JSONDecodeError as e:
            raise CharacterNotFoundError(f"角色数据文件格式错误: {e}")
    
    @classmethod
    def clear_cache(cls) -> None:
        """清除角色数据缓存"""
        cls._characters_cache = None
    
    @staticmethod
    def load_from_json(character_id: str) -> 'Character':
        """从JSON文件加载角色数据"""
        characters_data = Character._load_characters_data()
        
        if character_id not in characters_data:
            raise CharacterNotFoundError(f"角色未找到: {character_id}")
        
        data = characters_data[character_id]
        
        return Character(
            character_id=data['id'],
            name=data['name'],
            name_en=data.get('name_en', data['name']),
            portrait=data.get('portrait', ''),
            model_path=data.get('model', ''),
            stats=CharacterStats.from_dict(data.get('stats', {})),
            background=data.get('background', ''),
            personality_traits=data.get('personality', []),
            relationships=data.get('relationships', {})
        )
    
    @staticmethod
    def get_all_character_ids() -> List[str]:
        """获取所有可用角色ID列表"""
        characters_data = Character._load_characters_data()
        return list(characters_data.keys())
    
    @staticmethod
    def get_all_characters() -> List['Character']:
        """获取所有角色对象列表"""
        character_ids = Character.get_all_character_ids()
        return [Character.load_from_json(cid) for cid in character_ids]
    
    def get_dialogue_variant(self, dialogue_id: str, dialogues_data: Optional[Dict] = None) -> str:
        """
        获取角色特定的对话变体
        
        Args:
            dialogue_id: 对话ID
            dialogues_data: 对话数据字典，格式为 {dialogue_id: {character_id: [dialogue_lines]}}
        
        Returns:
            该角色对应的对话文本，如果没有特定对话则返回默认文本
        """
        if dialogues_data is None:
            return f"[{self.name}]: ..."
        
        if dialogue_id not in dialogues_data:
            return f"[{self.name}]: ..."
        
        dialogue_variants = dialogues_data[dialogue_id]
        
        # 尝试获取角色特定对话
        if self.id in dialogue_variants:
            lines = dialogue_variants[self.id]
            if isinstance(lines, list):
                return '\n'.join(lines)
            return str(lines)
        
        # 如果没有特定对话，返回默认
        if 'default' in dialogue_variants:
            lines = dialogue_variants['default']
            if isinstance(lines, list):
                return '\n'.join(lines)
            return str(lines)
        
        return f"[{self.name}]: ..."
    
    def get_reaction(self, event_id: str, events_data: Optional[Dict] = None) -> str:
        """
        获取角色对特定事件的反应
        基于角色的性格特征和人际关系生成反应
        
        Args:
            event_id: 事件ID
            events_data: 事件数据字典，格式为 {event_id: {character_id: reaction}}
        
        Returns:
            角色对事件的反应文本
        """
        # 如果有预定义的事件反应数据
        if events_data and event_id in events_data:
            event_reactions = events_data[event_id]
            if self.id in event_reactions:
                return event_reactions[self.id]
        
        # 基于性格特征生成默认反应
        return self._generate_personality_based_reaction(event_id)
    
    def _generate_personality_based_reaction(self, event_id: str) -> str:
        """基于性格特征生成反应"""
        if not self.personality_traits:
            return f"[{self.name}] 沉默不语。"
        
        # 根据主要性格特征生成反应模板
        primary_trait = self.personality_traits[0]
        
        reaction_templates = {
            "热血": f"[{self.name}] 握紧拳头，眼中燃烧着斗志。",
            "冷静": f"[{self.name}] 冷静地分析着当前的局势。",
            "聪明": f"[{self.name}] 快速思考着应对方案。",
            "现实": f"[{self.name}] 务实地评估着情况。",
            "乐观": f"[{self.name}] 保持着积极的态度。",
            "贪吃": f"[{self.name}] 下意识地摸了摸口袋里的食物。",
            "可靠": f"[{self.name}] 坚定地站在前方，准备承担责任。",
            "内向": f"[{self.name}] 安静地观察着周围的情况。",
            "尖锐": f"[{self.name}] 露出一丝讽刺的笑容。",
            "温柔": f"[{self.name}] 关切地看向同伴们。",
            "温和": f"[{self.name}] 试图安抚大家的情绪。",
            "冷漠": f"[{self.name}] 面无表情地注视着前方。",
        }
        
        return reaction_templates.get(
            primary_trait, 
            f"[{self.name}] 做出了反应。"
        )
    
    def has_relationship_with(self, other_character_id: str) -> bool:
        """检查是否与另一角色有关系"""
        return other_character_id in self.relationships
    
    def get_relationship(self, other_character_id: str) -> Optional[str]:
        """获取与另一角色的关系描述"""
        return self.relationships.get(other_character_id)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'name_en': self.name_en,
            'portrait': self.portrait,
            'model': self.model_path,
            'stats': self.stats.to_dict(),
            'background': self.background,
            'personality': self.personality_traits,
            'relationships': self.relationships
        }
    
    def __repr__(self) -> str:
        return f"Character(id='{self.id}', name='{self.name}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Character):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
