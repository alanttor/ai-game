"""
存档系统 - SaveSystem
实现游戏存档的保存、加载、序列化和反序列化
"""
import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GAME_CONFIG


class SaveCorruptedError(Exception):
    """存档损坏异常"""
    pass


class SaveNotFoundError(Exception):
    """存档未找到异常"""
    pass


@dataclass
class SaveData:
    """存档数据结构"""
    version: str = GAME_CONFIG.SAVE_VERSION
    character_id: str = "eren"
    current_chapter: int = 1
    unlocked_chapters: List[int] = field(default_factory=lambda: [1])
    total_score: int = 0
    play_time: float = 0.0
    settings: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __eq__(self, other: object) -> bool:
        """比较两个SaveData是否等价"""
        if not isinstance(other, SaveData):
            return False
        return (
            self.version == other.version and
            self.character_id == other.character_id and
            self.current_chapter == other.current_chapter and
            sorted(self.unlocked_chapters) == sorted(other.unlocked_chapters) and
            self.total_score == other.total_score and
            abs(self.play_time - other.play_time) < 0.001 and
            self.settings == other.settings and
            self.timestamp == other.timestamp
        )


class SaveSystem:
    """游戏存档管理系统"""
    
    def __init__(self, save_dir: str = None):
        """
        初始化存档系统
        
        Args:
            save_dir: 存档目录路径，默认使用配置中的路径
        """
        self.save_dir = save_dir or GAME_CONFIG.SAVE_DIR
        self.save_slots: Dict[int, Optional[SaveData]] = {}
        self._ensure_save_directory()
    
    def _ensure_save_directory(self) -> None:
        """确保存档目录存在"""
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def _get_save_path(self, slot: int) -> str:
        """获取指定槽位的存档文件路径"""
        return os.path.join(self.save_dir, f"save_slot_{slot}.json")
    
    def serialize_to_json(self, save_data: SaveData) -> str:
        """
        将SaveData序列化为JSON字符串
        
        Args:
            save_data: 要序列化的存档数据
            
        Returns:
            JSON格式的字符串
        """
        data_dict = asdict(save_data)
        return json.dumps(data_dict, ensure_ascii=False, indent=2)
    
    def deserialize_from_json(self, json_str: str) -> SaveData:
        """
        从JSON字符串反序列化为SaveData
        
        Args:
            json_str: JSON格式的字符串
            
        Returns:
            SaveData对象
            
        Raises:
            SaveCorruptedError: 当JSON格式无效或数据损坏时
        """
        try:
            data_dict = json.loads(json_str)
            return SaveData(
                version=data_dict.get('version', GAME_CONFIG.SAVE_VERSION),
                character_id=data_dict.get('character_id', 'eren'),
                current_chapter=data_dict.get('current_chapter', 1),
                unlocked_chapters=data_dict.get('unlocked_chapters', [1]),
                total_score=data_dict.get('total_score', 0),
                play_time=data_dict.get('play_time', 0.0),
                settings=data_dict.get('settings', {}),
                timestamp=data_dict.get('timestamp', datetime.now().isoformat())
            )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise SaveCorruptedError(f"存档数据损坏: {str(e)}")
    
    def save_game(self, slot: int, save_data: SaveData) -> bool:
        """
        保存游戏到指定槽位
        
        Args:
            slot: 存档槽位 (1-3)
            save_data: 要保存的数据
            
        Returns:
            保存是否成功
            
        Raises:
            ValueError: 当槽位无效时
        """
        if not 1 <= slot <= GAME_CONFIG.MAX_SAVE_SLOTS:
            raise ValueError(f"无效的存档槽位: {slot}")
        
        # 更新时间戳
        save_data.timestamp = datetime.now().isoformat()
        
        try:
            json_str = self.serialize_to_json(save_data)
            save_path = self._get_save_path(slot)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
            
            # 更新内存缓存
            self.save_slots[slot] = save_data
            return True
        except (IOError, OSError) as e:
            print(f"保存失败: {str(e)}")
            return False
    
    def load_game(self, slot: int) -> SaveData:
        """
        从指定槽位加载游戏
        
        Args:
            slot: 存档槽位 (1-3)
            
        Returns:
            加载的SaveData对象
            
        Raises:
            ValueError: 当槽位无效时
            SaveNotFoundError: 当存档不存在时
            SaveCorruptedError: 当存档损坏时
        """
        if not 1 <= slot <= GAME_CONFIG.MAX_SAVE_SLOTS:
            raise ValueError(f"无效的存档槽位: {slot}")
        
        save_path = self._get_save_path(slot)
        
        if not os.path.exists(save_path):
            raise SaveNotFoundError(f"存档槽位 {slot} 不存在")
        
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                json_str = f.read()
            
            save_data = self.deserialize_from_json(json_str)
            self.save_slots[slot] = save_data
            return save_data
        except (IOError, OSError) as e:
            raise SaveCorruptedError(f"读取存档失败: {str(e)}")
    
    def delete_save(self, slot: int) -> bool:
        """
        删除指定槽位的存档
        
        Args:
            slot: 存档槽位 (1-3)
            
        Returns:
            删除是否成功
        """
        if not 1 <= slot <= GAME_CONFIG.MAX_SAVE_SLOTS:
            return False
        
        save_path = self._get_save_path(slot)
        
        try:
            if os.path.exists(save_path):
                os.remove(save_path)
            if slot in self.save_slots:
                del self.save_slots[slot]
            return True
        except (IOError, OSError):
            return False
    
    def get_save_info(self, slot: int) -> Optional[Dict[str, Any]]:
        """
        获取指定槽位的存档信息摘要
        
        Args:
            slot: 存档槽位 (1-3)
            
        Returns:
            存档信息字典，不存在则返回None
        """
        save_path = self._get_save_path(slot)
        
        if not os.path.exists(save_path):
            return None
        
        try:
            save_data = self.load_game(slot)
            return {
                'slot': slot,
                'character_id': save_data.character_id,
                'current_chapter': save_data.current_chapter,
                'total_score': save_data.total_score,
                'play_time': save_data.play_time,
                'timestamp': save_data.timestamp
            }
        except (SaveNotFoundError, SaveCorruptedError):
            return None
    
    def get_all_saves_info(self) -> List[Optional[Dict[str, Any]]]:
        """
        获取所有存档槽位的信息
        
        Returns:
            存档信息列表
        """
        return [
            self.get_save_info(slot) 
            for slot in range(1, GAME_CONFIG.MAX_SAVE_SLOTS + 1)
        ]
