"""
游戏控制器 - GameController
整合主菜单 -> 角色选择 -> 剧情 -> 关卡 -> 结果的完整游戏流程

Requirements:
    6.1 - 任务完成解锁下一章节
    10.1 - 保存游戏进度
    10.2 - 加载游戏进度
"""
from typing import Optional, Dict, Any, List, Callable
import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.game_manager import GameManager, GameState
from core.scene_manager import SceneManager, SceneType, SceneData, LoadingTask
from content.character import Character, CharacterNotFoundError
from content.story_system import StorySystem, StoryChapter
from content.level_system import LevelSystem, LevelData, LevelState
from data.save_system import SaveSystem, SaveData, SaveNotFoundError, SaveCorruptedError
from presentation.ui.menu import (
    MenuManager, ResultsData, CharacterSelectData
)
from presentation.ui.dialogue import (
    DialogueSystem, DialogueLine, CutsceneData
)
from config import GAME_CONFIG


class GameController:
    """
    游戏控制器
    
    负责协调所有游戏系统，实现完整的游戏流程。
    
    流程:
        主菜单 -> 角色选择 -> 过场动画 -> 关卡 -> 结果 -> (下一关卡/主菜单)
    
    Requirements:
        6.1 - 任务完成解锁下一章节
        10.1 - 保存游戏进度
        10.2 - 加载游戏进度
    """
    
    def __init__(self, save_dir: str = None):
        """
        初始化游戏控制器
        
        Args:
            save_dir: 存档目录路径
        """
        # 核心系统
        self.game_manager = GameManager()
        self.scene_manager = SceneManager()
        
        # 内容系统
        self.story_system = StorySystem()
        self.level_system = LevelSystem()
        
        # 数据系统
        self.save_system = SaveSystem(save_dir)
        
        # UI系统
        self.menu_manager = MenuManager()
        self.dialogue_system = DialogueSystem()
        
        # 当前状态
        self._current_character: Optional[Character] = None
        self._current_level: Optional[LevelData] = None
        self._current_chapter: Optional[StoryChapter] = None
        self._current_mission_index: int = 0
        
        # 游戏统计
        self._total_score: int = 0
        self._play_time: float = 0.0
        self._max_combo: int = 0
        self._total_kills: int = 0
        
        # 设置回调
        self._setup_callbacks()
        
        # 初始化场景
        self._initialize()
    
    def _setup_callbacks(self) -> None:
        """设置各系统回调"""
        # 菜单回调
        self.menu_manager.set_callback('new_game', self._on_new_game)
        self.menu_manager.set_callback('continue', self._on_continue_game)
        self.menu_manager.set_callback('settings', self._on_settings)
        self.menu_manager.set_callback('quit', self._on_quit)
        self.menu_manager.set_callback('character_selected', self._on_character_selected)
        self.menu_manager.set_callback('resume', self._on_resume)
        self.menu_manager.set_callback('quit_to_menu', self._on_quit_to_menu)
        self.menu_manager.set_callback('results_continue', self._on_results_continue)
        self.menu_manager.set_callback('retry', self._on_retry)
        
        # 对话系统回调
        self.dialogue_system.set_on_cutscene_complete_callback(self._on_cutscene_complete)
        self.dialogue_system.set_on_dialogue_complete_callback(self._on_dialogue_complete)
        
        # 关卡系统回调
        self.level_system.set_on_level_complete(self._on_level_complete)
        self.level_system.set_on_level_fail(self._on_level_fail)
        
        # 场景管理器回调
        self.scene_manager.set_on_scene_change_callback(self._on_scene_change)
        self.scene_manager.set_on_scene_loaded_callback(self._on_scene_loaded)
        
        # 游戏状态回调
        self.game_manager.register_callback(GameState.MAIN_MENU, self._on_enter_main_menu)
        self.game_manager.register_callback(GameState.CHARACTER_SELECT, self._on_enter_character_select)
        self.game_manager.register_callback(GameState.CUTSCENE, self._on_enter_cutscene)
        self.game_manager.register_callback(GameState.GAMEPLAY, self._on_enter_gameplay)
        self.game_manager.register_callback(GameState.PAUSED, self._on_enter_paused)
        self.game_manager.register_callback(GameState.RESULTS, self._on_enter_results)
        self.game_manager.register_callback(GameState.GAME_OVER, self._on_enter_game_over)
    
    def _initialize(self) -> None:
        """初始化游戏"""
        # 检查是否有存档
        has_save = self._check_has_save()
        
        # 显示主菜单
        self.menu_manager.show_main_menu(has_save)
        self.scene_manager.go_to_main_menu()
        self.game_manager.force_state(GameState.MAIN_MENU)
    
    def _check_has_save(self) -> bool:
        """检查是否有存档"""
        saves = self.save_system.get_all_saves_info()
        return any(save is not None for save in saves)
    
    # ==================== 菜单回调 ====================
    
    def _on_new_game(self) -> None:
        """新游戏"""
        # 重置进度
        self.story_system.reset_progress()
        self._total_score = 0
        self._play_time = 0.0
        self._max_combo = 0
        self._total_kills = 0
        
        # 显示角色选择
        self._show_character_select()
    
    def _on_continue_game(self) -> None:
        """继续游戏 - 加载存档"""
        # 尝试加载最近的存档
        saves = self.save_system.get_all_saves_info()
        
        # 找到最近的存档
        latest_save = None
        latest_slot = None
        for i, save in enumerate(saves, 1):
            if save is not None:
                if latest_save is None or save['timestamp'] > latest_save['timestamp']:
                    latest_save = save
                    latest_slot = i
        
        if latest_slot:
            self.load_game(latest_slot)
    
    def _on_settings(self) -> None:
        """设置"""
        # TODO: 实现设置界面
        pass
    
    def _on_quit(self) -> None:
        """退出游戏"""
        self.game_manager.quit()
    
    def _on_character_selected(self, character_id: str) -> None:
        """
        角色选择完成
        
        Args:
            character_id: 选择的角色ID
        """
        try:
            self._current_character = Character.load_from_json(character_id)
            
            # 开始新游戏
            self.game_manager.start_new_game(character_id)
            
            # 获取第一章
            self._current_chapter = self.story_system.get_current_chapter()
            self._current_mission_index = 0
            
            # 播放开场过场动画
            if self._current_chapter and self._current_chapter.cutscenes:
                self._play_cutscene(self._current_chapter.cutscenes[0])
            else:
                # 没有过场动画，直接开始关卡
                self._start_current_mission()
        except CharacterNotFoundError:
            # 角色未找到，返回角色选择
            self._show_character_select()
    
    def _on_resume(self) -> None:
        """继续游戏（从暂停）"""
        self.game_manager.resume_game()
        self.menu_manager.hide_all()
    
    def _on_quit_to_menu(self) -> None:
        """返回主菜单"""
        # 自动保存
        self._auto_save()
        
        # 重置关卡
        self.level_system.reset()
        
        # 返回主菜单
        has_save = self._check_has_save()
        self.menu_manager.show_main_menu(has_save)
        self.scene_manager.go_to_main_menu()
        self.game_manager.force_state(GameState.MAIN_MENU)
    
    def _on_results_continue(self) -> None:
        """
        结果界面继续 - 进入下一关
        
        Requirement 6.1: 任务完成解锁下一章节
        """
        # 推进到下一个任务
        self._advance_to_next_mission()
    
    def _on_retry(self) -> None:
        """重试当前关卡"""
        if self._current_level:
            self._start_level(self._current_level.id)
    
    # ==================== 场景回调 ====================
    
    def _on_scene_change(self, old_scene: SceneData, new_scene: SceneData) -> None:
        """场景变化回调"""
        pass
    
    def _on_scene_loaded(self, scene: SceneData) -> None:
        """场景加载完成回调"""
        pass
    
    # ==================== 游戏状态回调 ====================
    
    def _on_enter_main_menu(self) -> None:
        """进入主菜单"""
        pass
    
    def _on_enter_character_select(self) -> None:
        """进入角色选择"""
        pass
    
    def _on_enter_cutscene(self) -> None:
        """进入过场动画"""
        pass
    
    def _on_enter_gameplay(self) -> None:
        """进入游戏"""
        pass
    
    def _on_enter_paused(self) -> None:
        """进入暂停"""
        self.menu_manager.show_pause_menu()
    
    def _on_enter_results(self) -> None:
        """进入结果界面"""
        pass
    
    def _on_enter_game_over(self) -> None:
        """进入游戏结束"""
        pass
    
    # ==================== 对话/过场回调 ====================
    
    def _on_cutscene_complete(self) -> None:
        """过场动画完成"""
        # 开始当前任务
        self._start_current_mission()
    
    def _on_dialogue_complete(self) -> None:
        """对话完成"""
        pass
    
    # ==================== 关卡回调 ====================
    
    def _on_level_complete(self, result: Dict[str, Any]) -> None:
        """
        关卡完成
        
        Args:
            result: 关卡结果数据
            
        Requirement 6.1: 任务完成解锁下一章节
        """
        # 更新统计
        self._total_score += result.get('score', 0)
        self._total_kills += result.get('titans_killed', 0)
        
        # 检查是否解锁新章节
        if self._current_chapter:
            mission_id = self._current_level.id if self._current_level else ""
            new_chapter_id = self.story_system.complete_mission(mission_id)
            
            if new_chapter_id:
                # 解锁了新章节
                self.game_manager.advance_chapter()
        
        # 显示结果界面
        results_data = ResultsData(
            mission_name=result.get('level_name', ''),
            success=True,
            total_score=result.get('score', 0),
            kills=result.get('titans_killed', 0),
            max_combo=self._max_combo,
            time_elapsed=result.get('elapsed_time', 0)
        )
        
        self.menu_manager.show_results(results_data)
        self.scene_manager.go_to_results(result)
        self.game_manager.force_state(GameState.RESULTS)
        
        # 自动保存
        self._auto_save()
    
    def _on_level_fail(self, result: Dict[str, Any]) -> None:
        """
        关卡失败
        
        Args:
            result: 关卡结果数据
        """
        reason = result.get('reason', '任务失败')
        
        self.menu_manager.show_game_over(self._total_score, reason)
        self.scene_manager.go_to_game_over(self._total_score, reason)
        self.game_manager.force_state(GameState.GAME_OVER)
    
    # ==================== 游戏流程方法 ====================
    
    def _show_character_select(self) -> None:
        """显示角色选择界面"""
        characters = Character.get_all_characters()
        self.menu_manager.show_character_select(characters)
        self.scene_manager.go_to_character_select()
        self.game_manager.force_state(GameState.CHARACTER_SELECT)
    
    def _play_cutscene(self, cutscene_id: str) -> None:
        """
        播放过场动画
        
        Args:
            cutscene_id: 过场动画ID
        """
        if not self._current_character:
            return
        
        # 获取过场动画数据
        dialogue_lines = self.story_system.get_cutscene(
            cutscene_id, 
            self._current_character
        )
        
        if dialogue_lines:
            # 创建过场动画数据
            cutscene = CutsceneData(
                id=cutscene_id,
                title=cutscene_id,
                dialogue_lines=[
                    DialogueLine(
                        speaker=line['speaker'],
                        speaker_id=line['speaker_id'],
                        text=line['text'],
                        portrait_position="left" if line.get('is_player') else "right"
                    )
                    for line in dialogue_lines
                ]
            )
            
            self.dialogue_system.play_cutscene(cutscene)
            self.scene_manager.go_to_cutscene(cutscene_id)
            self.game_manager.force_state(GameState.CUTSCENE)
        else:
            # 没有对话，直接开始任务
            self._start_current_mission()
    
    def _start_current_mission(self) -> None:
        """开始当前任务"""
        if not self._current_chapter:
            return
        
        missions = self._current_chapter.missions
        if self._current_mission_index < len(missions):
            mission_id = missions[self._current_mission_index]
            self._start_level(mission_id)
    
    def _start_level(self, level_id: str) -> None:
        """
        开始关卡
        
        Args:
            level_id: 关卡ID
        """
        try:
            self._current_level = self.level_system.load_level(level_id)
            
            self.scene_manager.go_to_gameplay(level_id, {
                'character': self._current_character.id if self._current_character else None,
                'chapter': self._current_chapter.id if self._current_chapter else None
            })
            self.game_manager.force_state(GameState.GAMEPLAY)
            self.menu_manager.hide_all()
        except Exception as e:
            print(f"加载关卡失败: {e}")
            self._on_quit_to_menu()
    
    def _advance_to_next_mission(self) -> None:
        """
        推进到下一个任务
        
        Requirement 6.1: 任务完成解锁下一章节
        """
        if not self._current_chapter:
            self._on_quit_to_menu()
            return
        
        self._current_mission_index += 1
        
        # 检查是否还有更多任务
        if self._current_mission_index < len(self._current_chapter.missions):
            # 还有任务，继续
            self._start_current_mission()
        else:
            # 章节完成，检查是否有下一章
            next_chapter_index = self.story_system.current_chapter + 1
            next_chapter = self.story_system.get_chapter_by_index(next_chapter_index)
            
            if next_chapter and next_chapter.id in self.story_system.unlocked_chapters:
                # 进入下一章
                self.story_system.current_chapter = next_chapter_index
                self._current_chapter = next_chapter
                self._current_mission_index = 0
                
                # 播放章节开场过场动画
                if next_chapter.cutscenes:
                    self._play_cutscene(next_chapter.cutscenes[0])
                else:
                    self._start_current_mission()
            else:
                # 游戏完成或没有更多章节
                self._on_quit_to_menu()
    
    # ==================== 存档系统 ====================
    
    def save_game(self, slot: int) -> bool:
        """
        保存游戏
        
        Args:
            slot: 存档槽位
            
        Returns:
            bool: 是否成功保存
            
        Requirement 10.1: 保存游戏进度
        """
        save_data = SaveData(
            character_id=self._current_character.id if self._current_character else "eren",
            current_chapter=self.story_system.current_chapter + 1,
            unlocked_chapters=[
                i + 1 for i, ch in enumerate(self.story_system.chapters)
                if ch.id in self.story_system.unlocked_chapters
            ],
            total_score=self._total_score,
            play_time=self._play_time,
            settings={}
        )
        
        return self.save_system.save_game(slot, save_data)
    
    def load_game(self, slot: int) -> bool:
        """
        加载游戏
        
        Args:
            slot: 存档槽位
            
        Returns:
            bool: 是否成功加载
            
        Requirement 10.2: 加载游戏进度
        """
        try:
            save_data = self.save_system.load_game(slot)
            
            # 恢复角色
            self._current_character = Character.load_from_json(save_data.character_id)
            
            # 恢复进度
            self._total_score = save_data.total_score
            self._play_time = save_data.play_time
            
            # 恢复剧情进度
            chapter_index = max(0, save_data.current_chapter - 1)
            unlocked_ids = []
            for ch_num in save_data.unlocked_chapters:
                idx = ch_num - 1
                if 0 <= idx < len(self.story_system.chapters):
                    unlocked_ids.append(self.story_system.chapters[idx].id)
            
            self.story_system.set_progress(chapter_index, unlocked_ids)
            self._current_chapter = self.story_system.get_current_chapter()
            self._current_mission_index = 0
            
            # 更新游戏管理器
            self.game_manager.load_game_state(
                save_data.character_id,
                save_data.current_chapter,
                save_data.total_score
            )
            
            # 开始游戏
            if self._current_chapter and self._current_chapter.cutscenes:
                self._play_cutscene(self._current_chapter.cutscenes[0])
            else:
                self._start_current_mission()
            
            return True
        except (SaveNotFoundError, SaveCorruptedError, CharacterNotFoundError) as e:
            print(f"加载存档失败: {e}")
            return False
    
    def _auto_save(self) -> None:
        """自动保存到槽位1"""
        self.save_game(1)
    
    # ==================== 游戏控制 ====================
    
    def pause(self) -> None:
        """暂停游戏"""
        if self.game_manager.current_state == GameState.GAMEPLAY:
            self.game_manager.pause_game()
    
    def resume(self) -> None:
        """继续游戏"""
        if self.game_manager.current_state == GameState.PAUSED:
            self.game_manager.resume_game()
            self.menu_manager.hide_all()
    
    def update(self, dt: float) -> None:
        """
        更新游戏
        
        Args:
            dt: 时间步长
        """
        # 更新游戏时间
        if self.game_manager.current_state == GameState.GAMEPLAY:
            self._play_time += dt
            
            # 更新关卡
            self.level_system.update(dt)
        
        # 更新对话系统
        self.dialogue_system.update(dt)
    
    def handle_input(self, action: str) -> bool:
        """
        处理输入
        
        Args:
            action: 输入动作
            
        Returns:
            bool: 是否处理了输入
        """
        state = self.game_manager.current_state
        
        # 菜单状态下的输入
        if state in [GameState.MAIN_MENU, GameState.CHARACTER_SELECT, 
                     GameState.PAUSED, GameState.RESULTS, GameState.GAME_OVER]:
            return self.menu_manager.handle_input(action)
        
        # 过场动画状态下的输入
        if state == GameState.CUTSCENE:
            if action == "confirm":
                self.dialogue_system.advance()
                return True
            elif action == "back":
                self.dialogue_system.skip()
                return True
        
        # 游戏状态下的输入
        if state == GameState.GAMEPLAY:
            if action == "pause":
                self.pause()
                return True
        
        return False
    
    # ==================== 状态查询 ====================
    
    def get_game_state(self) -> Dict[str, Any]:
        """获取游戏状态"""
        return {
            'state': self.game_manager.current_state.value,
            'character': self._current_character.id if self._current_character else None,
            'chapter': self._current_chapter.id if self._current_chapter else None,
            'mission_index': self._current_mission_index,
            'total_score': self._total_score,
            'play_time': self._play_time,
            'is_loading': self.scene_manager.is_loading
        }
    
    def get_current_character(self) -> Optional[Character]:
        """获取当前角色"""
        return self._current_character
    
    def get_current_chapter(self) -> Optional[StoryChapter]:
        """获取当前章节"""
        return self._current_chapter
    
    def get_current_level(self) -> Optional[LevelData]:
        """获取当前关卡"""
        return self._current_level
