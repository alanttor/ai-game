"""
场景管理器测试
测试SceneManager和GameController的功能

Requirements:
    7.1 - 关卡加载时生成对应环境
    6.1 - 任务完成解锁下一章节
    10.1 - 保存游戏进度
    10.2 - 加载游戏进度
"""
import pytest
import os
import sys
import tempfile
import shutil

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.scene_manager import (
    SceneManager, SceneType, SceneData, 
    LoadingScreen, LoadingTask, LoadingState, LoadingProgress
)
from core.game_controller import GameController
from core.game_manager import GameState


class TestSceneManager:
    """SceneManager测试类"""
    
    def test_initial_state(self):
        """测试初始状态"""
        sm = SceneManager()
        assert sm.current_scene_type == SceneType.NONE
        assert not sm.is_loading
    
    def test_change_scene_no_loading(self):
        """测试无加载画面的场景切换"""
        sm = SceneManager()
        sm.change_scene(SceneType.MAIN_MENU, show_loading=False)
        assert sm.current_scene_type == SceneType.MAIN_MENU
        assert not sm.is_loading
    
    def test_go_to_main_menu(self):
        """测试切换到主菜单"""
        sm = SceneManager()
        sm.go_to_main_menu()
        assert sm.current_scene_type == SceneType.MAIN_MENU
    
    def test_go_to_character_select(self):
        """测试切换到角色选择"""
        sm = SceneManager()
        sm.go_to_character_select()
        assert sm.current_scene_type == SceneType.CHARACTER_SELECT
    
    def test_scene_data(self):
        """测试场景数据"""
        sm = SceneManager()
        sm.change_scene(
            SceneType.GAMEPLAY, 
            scene_id="test_level",
            params={'difficulty': 1},
            show_loading=False
        )
        
        assert sm.current_scene.scene_type == SceneType.GAMEPLAY
        assert sm.current_scene.scene_id == "test_level"
        assert sm.current_scene.params['difficulty'] == 1
    
    def test_scene_info(self):
        """测试获取场景信息"""
        sm = SceneManager()
        sm.go_to_main_menu()
        
        info = sm.get_scene_info()
        assert info['current_scene']['scene_type'] == 'main_menu'
        assert not info['is_loading']


class TestLoadingScreen:
    """LoadingScreen测试类"""
    
    def test_initial_state(self):
        """测试初始状态"""
        ls = LoadingScreen()
        assert not ls.visible
        assert ls.state == LoadingState.IDLE
    
    def test_start_loading(self):
        """测试开始加载"""
        ls = LoadingScreen()
        tasks = [
            LoadingTask("task1", "任务1"),
            LoadingTask("task2", "任务2")
        ]
        ls.start_loading(tasks)
        
        assert ls.visible
        assert ls.state == LoadingState.LOADING
        assert ls.progress.total_tasks == 2
        assert ls.progress.progress == 0.0
    
    def test_complete_task(self):
        """测试完成任务"""
        ls = LoadingScreen()
        tasks = [
            LoadingTask("task1", "任务1", weight=1.0),
            LoadingTask("task2", "任务2", weight=1.0)
        ]
        ls.start_loading(tasks)
        
        ls.complete_task("task1")
        assert ls.progress.tasks_completed == 1
        assert ls.progress.progress == 0.5
    
    def test_all_tasks_complete(self):
        """测试所有任务完成"""
        ls = LoadingScreen()
        completed = False
        
        def on_complete():
            nonlocal completed
            completed = True
        
        ls.set_on_complete_callback(on_complete)
        
        tasks = [LoadingTask("task1", "任务1")]
        ls.start_loading(tasks)
        ls.complete_task("task1")
        
        assert completed
        assert ls.state == LoadingState.COMPLETE
    
    def test_loading_error(self):
        """测试加载错误"""
        ls = LoadingScreen()
        error_msg = None
        
        def on_error(msg):
            nonlocal error_msg
            error_msg = msg
        
        ls.set_on_error_callback(on_error)
        
        tasks = [LoadingTask("task1", "任务1")]
        ls.start_loading(tasks)
        ls.set_task_error("task1", "加载失败")
        
        assert ls.state == LoadingState.ERROR
        assert error_msg == "加载失败"
    
    def test_render(self):
        """测试渲染数据"""
        ls = LoadingScreen()
        tasks = [LoadingTask("task1", "任务1")]
        ls.start_loading(tasks)
        
        render_data = ls.render()
        assert render_data['visible'] == True
        assert render_data['state'] == 'loading'
        assert len(render_data['tasks']) == 1


class TestGameController:
    """GameController测试类"""
    
    @pytest.fixture
    def temp_save_dir(self):
        """创建临时存档目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_initial_state(self, temp_save_dir):
        """测试初始状态"""
        gc = GameController(save_dir=temp_save_dir)
        assert gc.game_manager.current_state == GameState.MAIN_MENU
        assert gc.scene_manager.current_scene_type == SceneType.MAIN_MENU
    
    def test_get_game_state(self, temp_save_dir):
        """测试获取游戏状态"""
        gc = GameController(save_dir=temp_save_dir)
        state = gc.get_game_state()
        
        assert state['state'] == 'main_menu'
        assert state['character'] is None
        assert state['total_score'] == 0
    
    def test_save_and_load_game(self, temp_save_dir):
        """
        测试存档和读档
        
        Requirements: 10.1, 10.2
        """
        gc = GameController(save_dir=temp_save_dir)
        
        # 模拟游戏进度
        from content.character import Character
        gc._current_character = Character.load_from_json('eren')
        gc._total_score = 5000
        gc._play_time = 120.0
        
        # 保存
        result = gc.save_game(1)
        assert result == True
        
        # 创建新控制器并加载
        gc2 = GameController(save_dir=temp_save_dir)
        result = gc2.load_game(1)
        assert result == True
        
        assert gc2._current_character.id == 'eren'
        assert gc2._total_score == 5000
        assert gc2._play_time == 120.0
    
    def test_pause_resume(self, temp_save_dir):
        """测试暂停和继续"""
        gc = GameController(save_dir=temp_save_dir)
        
        # 强制进入游戏状态
        gc.game_manager.force_state(GameState.GAMEPLAY)
        
        # 暂停
        gc.pause()
        assert gc.game_manager.current_state == GameState.PAUSED
        
        # 继续
        gc.resume()
        assert gc.game_manager.current_state == GameState.GAMEPLAY
    
    def test_handle_menu_input(self, temp_save_dir):
        """测试菜单输入处理"""
        gc = GameController(save_dir=temp_save_dir)
        
        # 在主菜单状态下
        assert gc.game_manager.current_state == GameState.MAIN_MENU
        
        # 处理输入
        result = gc.handle_input("down")
        assert result == True
    
    def test_story_system_integration(self, temp_save_dir):
        """测试剧情系统集成"""
        gc = GameController(save_dir=temp_save_dir)
        
        # 检查章节
        chapters = gc.story_system.get_all_chapters()
        assert len(chapters) > 0
        
        # 检查第一章已解锁
        first_chapter = chapters[0]
        assert gc.story_system.is_chapter_unlocked(first_chapter.id)


class TestSceneData:
    """SceneData测试类"""
    
    def test_to_dict(self):
        """测试转换为字典"""
        sd = SceneData(
            scene_type=SceneType.GAMEPLAY,
            scene_id="level_1",
            params={'difficulty': 2}
        )
        
        data = sd.to_dict()
        assert data['scene_type'] == 'gameplay'
        assert data['scene_id'] == 'level_1'
        assert data['params']['difficulty'] == 2


class TestLoadingProgress:
    """LoadingProgress测试类"""
    
    def test_to_dict(self):
        """测试转换为字典"""
        lp = LoadingProgress(
            current_task="loading",
            current_description="加载中...",
            progress=0.5,
            tasks_completed=1,
            total_tasks=2
        )
        
        data = lp.to_dict()
        assert data['current_task'] == 'loading'
        assert data['progress'] == 0.5
        assert data['percentage'] == 50
