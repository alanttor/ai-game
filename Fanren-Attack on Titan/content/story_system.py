"""
剧情系统模块
实现剧情章节管理、过场动画和角色视角功能
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from .character import Character


@dataclass
class StoryChapter:
    """剧情章节数据类"""
    id: str
    title: str
    title_en: str
    season: int
    description: str
    missions: List[str]
    cutscenes: List[str]
    unlock_condition: str
    
    @staticmethod
    def from_dict(data: Dict) -> 'StoryChapter':
        """从字典创建StoryChapter"""
        return StoryChapter(
            id=data.get('id', ''),
            title=data.get('title', ''),
            title_en=data.get('title_en', ''),
            season=int(data.get('season', 1)),
            description=data.get('description', ''),
            missions=data.get('missions', []),
            cutscenes=data.get('cutscenes', []),
            unlock_condition=data.get('unlock_condition', 'start')
        )
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'title_en': self.title_en,
            'season': self.season,
            'description': self.description,
            'missions': self.missions,
            'cutscenes': self.cutscenes,
            'unlock_condition': self.unlock_condition
        }


class StoryNotFoundError(Exception):
    """剧情数据未找到异常"""
    pass


class ChapterNotFoundError(Exception):
    """章节未找到异常"""
    pass


class StorySystem:
    """剧情流程管理"""
    
    # 剧情数据文件路径
    _data_file_path: Optional[str] = None
    _story_cache: Optional[Dict] = None
    
    def __init__(self):
        self.chapters: List[StoryChapter] = []
        self.current_chapter: int = 0
        self.unlocked_chapters: Set[str] = set()
        self.character_dialogues: Dict[str, Dict] = {}
        self.character_perspectives: Dict[str, Dict] = {}
        self.character_reactions: Dict[str, Dict] = {}
        
        # 加载剧情数据
        self._load_story_data()
    
    @classmethod
    def set_data_file_path(cls, path: str) -> None:
        """设置剧情数据文件路径"""
        cls._data_file_path = path
        cls._story_cache = None  # 清除缓存
    
    @classmethod
    def _get_data_file_path(cls) -> str:
        """获取剧情数据文件路径"""
        if cls._data_file_path:
            return cls._data_file_path
        # 默认路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, 'data_files', 'stories.json')
    
    @classmethod
    def _load_raw_story_data(cls) -> Dict:
        """加载原始剧情数据（带缓存）"""
        if cls._story_cache is not None:
            return cls._story_cache
        
        data_path = cls._get_data_file_path()
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                cls._story_cache = json.load(f)
                return cls._story_cache
        except FileNotFoundError:
            raise StoryNotFoundError(f"剧情数据文件未找到: {data_path}")
        except json.JSONDecodeError as e:
            raise StoryNotFoundError(f"剧情数据文件格式错误: {e}")
    
    @classmethod
    def clear_cache(cls) -> None:
        """清除剧情数据缓存"""
        cls._story_cache = None
    
    def _load_story_data(self) -> None:
        """加载剧情数据"""
        data = self._load_raw_story_data()
        
        # 加载章节
        chapters_data = data.get('chapters', [])
        self.chapters = [StoryChapter.from_dict(ch) for ch in chapters_data]
        
        # 加载对话数据
        self.character_dialogues = data.get('dialogues', {})
        
        # 加载角色视角数据
        self.character_perspectives = data.get('character_perspectives', {})
        
        # 加载角色反应数据
        self.character_reactions = data.get('character_reactions', {})
        
        # 初始化解锁状态 - 默认解锁第一章
        if self.chapters:
            first_chapter = self.chapters[0]
            if first_chapter.unlock_condition == 'start':
                self.unlocked_chapters.add(first_chapter.id)
    
    def load_chapter(self, chapter_id: str) -> StoryChapter:
        """
        加载指定章节
        
        Args:
            chapter_id: 章节ID
            
        Returns:
            StoryChapter对象
            
        Raises:
            ChapterNotFoundError: 章节未找到
        """
        for chapter in self.chapters:
            if chapter.id == chapter_id:
                return chapter
        raise ChapterNotFoundError(f"章节未找到: {chapter_id}")
    
    def get_chapter_by_index(self, index: int) -> Optional[StoryChapter]:
        """
        通过索引获取章节
        
        Args:
            index: 章节索引（从0开始）
            
        Returns:
            StoryChapter对象，如果索引无效则返回None
        """
        if 0 <= index < len(self.chapters):
            return self.chapters[index]
        return None
    
    def unlock_next_chapter(self) -> Optional[str]:
        """
        解锁下一章节
        
        Returns:
            新解锁的章节ID，如果没有更多章节则返回None
        """
        # 找到当前章节的索引
        current_index = self.current_chapter
        next_index = current_index + 1
        
        if next_index < len(self.chapters):
            next_chapter = self.chapters[next_index]
            self.unlocked_chapters.add(next_chapter.id)
            return next_chapter.id
        
        return None
    
    def unlock_chapter(self, chapter_id: str) -> bool:
        """
        解锁指定章节
        
        Args:
            chapter_id: 要解锁的章节ID
            
        Returns:
            是否成功解锁
        """
        # 验证章节存在
        try:
            self.load_chapter(chapter_id)
            self.unlocked_chapters.add(chapter_id)
            return True
        except ChapterNotFoundError:
            return False
    
    def is_chapter_unlocked(self, chapter_id: str) -> bool:
        """
        检查章节是否已解锁
        
        Args:
            chapter_id: 章节ID
            
        Returns:
            是否已解锁
        """
        return chapter_id in self.unlocked_chapters
    
    def set_current_chapter(self, chapter_id: str) -> bool:
        """
        设置当前章节
        
        Args:
            chapter_id: 章节ID
            
        Returns:
            是否成功设置
        """
        for i, chapter in enumerate(self.chapters):
            if chapter.id == chapter_id:
                self.current_chapter = i
                return True
        return False
    
    def get_current_chapter(self) -> Optional[StoryChapter]:
        """获取当前章节"""
        return self.get_chapter_by_index(self.current_chapter)
    
    def complete_mission(self, mission_id: str) -> Optional[str]:
        """
        完成任务，检查是否需要解锁下一章节
        
        Args:
            mission_id: 完成的任务ID
            
        Returns:
            如果解锁了新章节，返回新章节ID；否则返回None
        """
        current = self.get_current_chapter()
        if not current:
            return None
        
        # 检查是否是当前章节的最后一个任务
        if mission_id in current.missions:
            mission_index = current.missions.index(mission_id)
            if mission_index == len(current.missions) - 1:
                # 完成了章节的最后一个任务，解锁下一章
                return self.unlock_next_chapter()
        
        return None
    
    def get_cutscene(self, cutscene_id: str, character: Character) -> List[Dict]:
        """
        获取过场动画数据，包含角色特定对话
        
        Args:
            cutscene_id: 过场动画ID
            character: 当前玩家角色
            
        Returns:
            过场动画数据列表，每个元素包含 speaker 和 text
        """
        if cutscene_id not in self.character_dialogues:
            return []
        
        dialogue_data = self.character_dialogues[cutscene_id]
        result = []
        
        # 获取角色特定对话
        if character.id in dialogue_data:
            lines = dialogue_data[character.id]
            for line in lines:
                result.append({
                    'speaker': character.name,
                    'speaker_id': character.id,
                    'text': line,
                    'is_player': True
                })
        
        # 也可以添加其他角色的对话作为背景
        for char_id, lines in dialogue_data.items():
            if char_id != character.id:
                for line in lines:
                    # 尝试获取角色名称
                    try:
                        other_char = Character.load_from_json(char_id)
                        speaker_name = other_char.name
                    except:
                        speaker_name = char_id
                    
                    result.append({
                        'speaker': speaker_name,
                        'speaker_id': char_id,
                        'text': line,
                        'is_player': False
                    })
        
        return result
    
    def get_character_perspective(self, event_id: str, character: Character) -> str:
        """
        获取角色对特定事件的视角描述
        
        Args:
            event_id: 事件ID（通常对应任务或章节）
            character: 当前玩家角色
            
        Returns:
            角色视角的描述文本
        """
        if event_id not in self.character_perspectives:
            # 如果没有预定义视角，生成基于性格的默认视角
            return self._generate_default_perspective(event_id, character)
        
        perspectives = self.character_perspectives[event_id]
        
        if character.id in perspectives:
            return perspectives[character.id]
        
        # 如果没有该角色的特定视角，生成默认视角
        return self._generate_default_perspective(event_id, character)
    
    def _generate_default_perspective(self, event_id: str, character: Character) -> str:
        """生成基于角色性格的默认视角"""
        if not character.personality_traits:
            return f"{character.name}默默地注视着眼前发生的一切。"
        
        primary_trait = character.personality_traits[0]
        
        perspective_templates = {
            "热血": f"{character.name}感到热血沸腾，准备迎接任何挑战。",
            "冷静": f"{character.name}冷静地分析着局势，寻找最佳的行动方案。",
            "聪明": f"{character.name}的大脑飞速运转，思考着各种可能性。",
            "现实": f"{character.name}务实地评估着当前的处境和可用的资源。",
            "乐观": f"{character.name}相信一切都会好起来的，保持着积极的心态。",
            "贪吃": f"{character.name}虽然有些紧张，但还是忍不住想着之后要吃什么。",
            "可靠": f"{character.name}坚定地站在前方，准备为同伴们承担责任。",
            "内向": f"{character.name}安静地观察着周围，心中有着自己的想法。",
            "尖锐": f"{character.name}用锐利的目光审视着一切，嘴角带着一丝讽刺。",
            "温柔": f"{character.name}关切地看向同伴们，希望大家都能平安。",
            "温和": f"{character.name}试图用温和的态度安抚大家的情绪。",
            "冷漠": f"{character.name}面无表情地注视着前方，内心深处却有着复杂的情感。",
        }
        
        return perspective_templates.get(
            primary_trait,
            f"{character.name}注视着眼前的一切，心中充满了复杂的情感。"
        )
    
    def get_character_reaction(self, reaction_type: str, character: Character) -> str:
        """
        获取角色对特定类型事件的反应
        
        Args:
            reaction_type: 反应类型（如 'comrade_death', 'victory', 'betrayal_revealed'）
            character: 当前角色
            
        Returns:
            角色反应文本
        """
        if reaction_type not in self.character_reactions:
            return character.get_reaction(reaction_type)
        
        reactions = self.character_reactions[reaction_type]
        
        if character.id in reactions:
            return reactions[character.id]
        
        # 使用Character类的反应生成
        return character.get_reaction(reaction_type)
    
    def get_all_chapters(self) -> List[StoryChapter]:
        """获取所有章节"""
        return self.chapters.copy()
    
    def get_unlocked_chapters(self) -> List[StoryChapter]:
        """获取所有已解锁的章节"""
        return [ch for ch in self.chapters if ch.id in self.unlocked_chapters]
    
    def get_chapters_by_season(self, season: int) -> List[StoryChapter]:
        """
        获取指定季度的所有章节
        
        Args:
            season: 季度编号（1, 2, 3）
            
        Returns:
            该季度的章节列表
        """
        return [ch for ch in self.chapters if ch.season == season]
    
    def get_chapter_progress(self) -> Dict:
        """
        获取章节进度信息
        
        Returns:
            包含总章节数、已解锁章节数、当前章节等信息的字典
        """
        return {
            'total_chapters': len(self.chapters),
            'unlocked_count': len(self.unlocked_chapters),
            'current_chapter_index': self.current_chapter,
            'current_chapter_id': self.chapters[self.current_chapter].id if self.chapters else None,
            'unlocked_chapter_ids': list(self.unlocked_chapters)
        }
    
    def reset_progress(self) -> None:
        """重置剧情进度"""
        self.current_chapter = 0
        self.unlocked_chapters.clear()
        
        # 重新解锁第一章
        if self.chapters:
            first_chapter = self.chapters[0]
            if first_chapter.unlock_condition == 'start':
                self.unlocked_chapters.add(first_chapter.id)
    
    def set_progress(self, current_chapter: int, unlocked_chapters: List[str]) -> None:
        """
        设置剧情进度（用于存档加载）
        
        Args:
            current_chapter: 当前章节索引
            unlocked_chapters: 已解锁章节ID列表
        """
        self.current_chapter = current_chapter
        self.unlocked_chapters = set(unlocked_chapters)
    
    def to_save_data(self) -> Dict:
        """转换为存档数据"""
        return {
            'current_chapter': self.current_chapter,
            'unlocked_chapters': list(self.unlocked_chapters)
        }
    
    @staticmethod
    def from_save_data(save_data: Dict) -> 'StorySystem':
        """从存档数据恢复"""
        story_system = StorySystem()
        story_system.current_chapter = save_data.get('current_chapter', 0)
        story_system.unlocked_chapters = set(save_data.get('unlocked_chapters', []))
        return story_system
