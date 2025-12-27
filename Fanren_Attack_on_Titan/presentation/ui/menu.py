"""
菜单系统 - 游戏菜单界面

实现主菜单、角色选择、暂停菜单和结果界面。

Requirements:
    1.1 - 新游戏时显示角色选择界面
    1.3 - 显示角色信息（名称、立绘、属性、背景）
    7.4 - 任务完成显示结果界面
    7.5 - 玩家死亡显示游戏结束界面
"""
from dataclasses import dataclass, field
from typing import Optional, Callable, List, Dict, Any
from enum import Enum
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class MenuState(Enum):
    """菜单状态枚举"""
    HIDDEN = "hidden"
    MAIN_MENU = "main_menu"
    CHARACTER_SELECT = "character_select"
    PAUSE = "pause"
    RESULTS = "results"
    GAME_OVER = "game_over"
    SETTINGS = "settings"


@dataclass
class MenuItem:
    """
    菜单项数据类
    """
    id: str
    text: str
    enabled: bool = True
    selected: bool = False
    action: Optional[Callable] = None
    
    def execute(self) -> bool:
        """
        执行菜单项动作
        
        Returns:
            bool: 是否成功执行
        """
        if self.enabled and self.action:
            self.action()
            return True
        return False


@dataclass
class CharacterSelectData:
    """
    角色选择数据
    
    Requirement 1.3: 显示角色信息
    """
    character_id: str
    name: str
    name_en: str
    portrait: str
    stats: Dict[str, float]
    background: str
    personality: List[str]
    
    @staticmethod
    def from_character(character) -> 'CharacterSelectData':
        """从Character对象创建"""
        return CharacterSelectData(
            character_id=character.id,
            name=character.name,
            name_en=character.name_en,
            portrait=character.portrait,
            stats={
                'speed': character.stats.speed,
                'attack_power': character.stats.attack_power,
                'stamina': character.stats.stamina,
                'gas_efficiency': character.stats.gas_efficiency
            },
            background=character.background,
            personality=character.personality_traits
        )


@dataclass
class ResultsData:
    """
    结果界面数据
    
    Requirement 7.4: 任务完成显示结果
    """
    mission_name: str = ""
    success: bool = True
    total_score: int = 0
    kills: int = 0
    max_combo: int = 0
    time_elapsed: float = 0.0
    rank: str = "C"
    
    def calculate_rank(self) -> str:
        """计算评级"""
        if self.total_score >= 10000:
            return "S"
        elif self.total_score >= 7000:
            return "A"
        elif self.total_score >= 4000:
            return "B"
        elif self.total_score >= 2000:
            return "C"
        else:
            return "D"


class MenuBase:
    """
    菜单基类
    """
    
    def __init__(self, title: str = ""):
        """
        初始化菜单
        
        Args:
            title: 菜单标题
        """
        self.title = title
        self.items: List[MenuItem] = []
        self.selected_index: int = 0
        self.visible: bool = False
        
        # 回调
        self._on_select_callback: Optional[Callable] = None
        self._on_back_callback: Optional[Callable] = None
    
    def add_item(self, item: MenuItem) -> None:
        """添加菜单项"""
        self.items.append(item)
    
    def clear_items(self) -> None:
        """清空菜单项"""
        self.items.clear()
        self.selected_index = 0
    
    def select_next(self) -> None:
        """选择下一项"""
        if not self.items:
            return
        
        # 取消当前选择
        if 0 <= self.selected_index < len(self.items):
            self.items[self.selected_index].selected = False
        
        # 移动到下一项
        self.selected_index = (self.selected_index + 1) % len(self.items)
        
        # 跳过禁用项
        attempts = 0
        while not self.items[self.selected_index].enabled and attempts < len(self.items):
            self.selected_index = (self.selected_index + 1) % len(self.items)
            attempts += 1
        
        # 设置新选择
        self.items[self.selected_index].selected = True
    
    def select_previous(self) -> None:
        """选择上一项"""
        if not self.items:
            return
        
        # 取消当前选择
        if 0 <= self.selected_index < len(self.items):
            self.items[self.selected_index].selected = False
        
        # 移动到上一项
        self.selected_index = (self.selected_index - 1) % len(self.items)
        
        # 跳过禁用项
        attempts = 0
        while not self.items[self.selected_index].enabled and attempts < len(self.items):
            self.selected_index = (self.selected_index - 1) % len(self.items)
            attempts += 1
        
        # 设置新选择
        self.items[self.selected_index].selected = True
    
    def confirm_selection(self) -> bool:
        """
        确认当前选择
        
        Returns:
            bool: 是否成功执行
        """
        if not self.items or not (0 <= self.selected_index < len(self.items)):
            return False
        
        item = self.items[self.selected_index]
        success = item.execute()
        
        if success and self._on_select_callback:
            self._on_select_callback(item)
        
        return success
    
    def back(self) -> None:
        """返回上一级"""
        if self._on_back_callback:
            self._on_back_callback()
    
    def show(self) -> None:
        """显示菜单"""
        self.visible = True
        # 确保有选中项
        if self.items and self.selected_index < len(self.items):
            self.items[self.selected_index].selected = True
    
    def hide(self) -> None:
        """隐藏菜单"""
        self.visible = False
    
    def set_on_select_callback(self, callback: Callable) -> None:
        """设置选择回调"""
        self._on_select_callback = callback
    
    def set_on_back_callback(self, callback: Callable) -> None:
        """设置返回回调"""
        self._on_back_callback = callback
    
    def get_selected_item(self) -> Optional[MenuItem]:
        """获取当前选中项"""
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None
    
    def render(self) -> Dict[str, Any]:
        """
        渲染菜单
        
        Returns:
            dict: 渲染数据
        """
        return {
            'type': 'menu',
            'title': self.title,
            'visible': self.visible,
            'items': [
                {
                    'id': item.id,
                    'text': item.text,
                    'enabled': item.enabled,
                    'selected': item.selected
                }
                for item in self.items
            ],
            'selected_index': self.selected_index
        }



class MainMenu(MenuBase):
    """
    主菜单
    
    提供新游戏、继续、设置、退出选项。
    
    Requirement 1.1: 新游戏时显示角色选择界面
    """
    
    def __init__(
        self,
        on_new_game: Optional[Callable] = None,
        on_continue: Optional[Callable] = None,
        on_settings: Optional[Callable] = None,
        on_quit: Optional[Callable] = None
    ):
        """
        初始化主菜单
        
        Args:
            on_new_game: 新游戏回调
            on_continue: 继续游戏回调
            on_settings: 设置回调
            on_quit: 退出回调
        """
        super().__init__("进击的巨人 - 同人游戏")
        
        self._on_new_game = on_new_game
        self._on_continue = on_continue
        self._on_settings = on_settings
        self._on_quit = on_quit
        
        self._has_save = False
        
        self._setup_items()
    
    def _setup_items(self) -> None:
        """设置菜单项"""
        self.clear_items()
        
        self.add_item(MenuItem(
            id="new_game",
            text="新游戏",
            enabled=True,
            action=self._on_new_game
        ))
        
        self.add_item(MenuItem(
            id="continue",
            text="继续游戏",
            enabled=self._has_save,
            action=self._on_continue
        ))
        
        self.add_item(MenuItem(
            id="settings",
            text="设置",
            enabled=True,
            action=self._on_settings
        ))
        
        self.add_item(MenuItem(
            id="quit",
            text="退出",
            enabled=True,
            action=self._on_quit
        ))
        
        # 默认选中第一项
        if self.items:
            self.items[0].selected = True
    
    def set_has_save(self, has_save: bool) -> None:
        """设置是否有存档"""
        self._has_save = has_save
        # 更新继续按钮状态
        for item in self.items:
            if item.id == "continue":
                item.enabled = has_save
                break
    
    def render(self) -> Dict[str, Any]:
        """渲染主菜单"""
        base = super().render()
        base['menu_type'] = 'main_menu'
        base['has_save'] = self._has_save
        return base


class CharacterSelectMenu(MenuBase):
    """
    角色选择界面
    
    显示所有可选角色及其详细信息。
    
    Requirements:
        1.1 - 新游戏时显示角色选择界面
        1.3 - 显示角色信息
    """
    
    def __init__(
        self,
        on_select: Optional[Callable[[str], None]] = None,
        on_back: Optional[Callable] = None
    ):
        """
        初始化角色选择界面
        
        Args:
            on_select: 选择角色回调，参数为角色ID
            on_back: 返回回调
        """
        super().__init__("选择角色")
        
        self._on_character_select = on_select
        self._on_back_callback = on_back
        
        self.characters: List[CharacterSelectData] = []
        self.selected_character: Optional[CharacterSelectData] = None
    
    def load_characters(self, characters: List) -> None:
        """
        加载角色列表
        
        Args:
            characters: Character对象列表
        """
        self.characters.clear()
        self.clear_items()
        
        for char in characters:
            char_data = CharacterSelectData.from_character(char)
            self.characters.append(char_data)
            
            self.add_item(MenuItem(
                id=char_data.character_id,
                text=f"{char_data.name} ({char_data.name_en})",
                enabled=True,
                action=lambda cid=char_data.character_id: self._select_character(cid)
            ))
        
        # 默认选中第一个
        if self.items:
            self.items[0].selected = True
            self.selected_character = self.characters[0] if self.characters else None
    
    def _select_character(self, character_id: str) -> None:
        """选择角色"""
        if self._on_character_select:
            self._on_character_select(character_id)
    
    def select_next(self) -> None:
        """选择下一个角色"""
        super().select_next()
        if 0 <= self.selected_index < len(self.characters):
            self.selected_character = self.characters[self.selected_index]
    
    def select_previous(self) -> None:
        """选择上一个角色"""
        super().select_previous()
        if 0 <= self.selected_index < len(self.characters):
            self.selected_character = self.characters[self.selected_index]
    
    def get_selected_character_info(self) -> Optional[Dict[str, Any]]:
        """
        获取当前选中角色的详细信息
        
        Requirement 1.3: 显示角色信息
        
        Returns:
            dict: 角色信息
        """
        if self.selected_character is None:
            return None
        
        char = self.selected_character
        return {
            'id': char.character_id,
            'name': char.name,
            'name_en': char.name_en,
            'portrait': char.portrait,
            'stats': char.stats,
            'background': char.background,
            'personality': char.personality,
            'stats_display': {
                '速度': f"{char.stats['speed']:.1f}",
                '攻击力': f"{char.stats['attack_power']:.1f}",
                '体力': f"{char.stats['stamina']:.0f}",
                '气体效率': f"{char.stats['gas_efficiency']:.1f}"
            }
        }
    
    def render(self) -> Dict[str, Any]:
        """渲染角色选择界面"""
        base = super().render()
        base['menu_type'] = 'character_select'
        base['selected_character'] = self.get_selected_character_info()
        base['character_count'] = len(self.characters)
        return base


class PauseMenu(MenuBase):
    """
    暂停菜单
    
    游戏暂停时显示的菜单。
    """
    
    def __init__(
        self,
        on_resume: Optional[Callable] = None,
        on_settings: Optional[Callable] = None,
        on_quit_to_menu: Optional[Callable] = None
    ):
        """
        初始化暂停菜单
        
        Args:
            on_resume: 继续游戏回调
            on_settings: 设置回调
            on_quit_to_menu: 返回主菜单回调
        """
        super().__init__("暂停")
        
        self.add_item(MenuItem(
            id="resume",
            text="继续游戏",
            enabled=True,
            action=on_resume
        ))
        
        self.add_item(MenuItem(
            id="settings",
            text="设置",
            enabled=True,
            action=on_settings
        ))
        
        self.add_item(MenuItem(
            id="quit_to_menu",
            text="返回主菜单",
            enabled=True,
            action=on_quit_to_menu
        ))
        
        if self.items:
            self.items[0].selected = True
    
    def render(self) -> Dict[str, Any]:
        """渲染暂停菜单"""
        base = super().render()
        base['menu_type'] = 'pause'
        return base


class ResultsScreen(MenuBase):
    """
    结果界面
    
    任务完成后显示的结果界面。
    
    Requirement 7.4: 任务完成显示结果界面
    """
    
    def __init__(
        self,
        on_continue: Optional[Callable] = None,
        on_retry: Optional[Callable] = None,
        on_quit_to_menu: Optional[Callable] = None
    ):
        """
        初始化结果界面
        
        Args:
            on_continue: 继续下一关回调
            on_retry: 重试回调
            on_quit_to_menu: 返回主菜单回调
        """
        super().__init__("任务完成")
        
        self.results_data: Optional[ResultsData] = None
        
        self._on_continue = on_continue
        self._on_retry = on_retry
        self._on_quit_to_menu = on_quit_to_menu
        
        self._setup_items()
    
    def _setup_items(self) -> None:
        """设置菜单项"""
        self.clear_items()
        
        self.add_item(MenuItem(
            id="continue",
            text="继续",
            enabled=True,
            action=self._on_continue
        ))
        
        self.add_item(MenuItem(
            id="retry",
            text="重试",
            enabled=True,
            action=self._on_retry
        ))
        
        self.add_item(MenuItem(
            id="quit_to_menu",
            text="返回主菜单",
            enabled=True,
            action=self._on_quit_to_menu
        ))
        
        if self.items:
            self.items[0].selected = True
    
    def set_results(self, results: ResultsData) -> None:
        """设置结果数据"""
        self.results_data = results
        results.rank = results.calculate_rank()
        self.title = "任务完成" if results.success else "任务失败"
    
    def render(self) -> Dict[str, Any]:
        """渲染结果界面"""
        base = super().render()
        base['menu_type'] = 'results'
        
        if self.results_data:
            base['results'] = {
                'mission_name': self.results_data.mission_name,
                'success': self.results_data.success,
                'total_score': self.results_data.total_score,
                'kills': self.results_data.kills,
                'max_combo': self.results_data.max_combo,
                'time_elapsed': self.results_data.time_elapsed,
                'rank': self.results_data.rank,
                'time_display': self._format_time(self.results_data.time_elapsed)
            }
        
        return base
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间显示"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"


class GameOverScreen(MenuBase):
    """
    游戏结束界面
    
    玩家死亡时显示的界面。
    
    Requirement 7.5: 玩家死亡显示游戏结束界面
    """
    
    def __init__(
        self,
        on_retry: Optional[Callable] = None,
        on_quit_to_menu: Optional[Callable] = None
    ):
        """
        初始化游戏结束界面
        
        Args:
            on_retry: 重试回调
            on_quit_to_menu: 返回主菜单回调
        """
        super().__init__("游戏结束")
        
        self.final_score: int = 0
        self.death_message: str = "你被巨人吞噬了..."
        
        self.add_item(MenuItem(
            id="retry",
            text="重试",
            enabled=True,
            action=on_retry
        ))
        
        self.add_item(MenuItem(
            id="quit_to_menu",
            text="返回主菜单",
            enabled=True,
            action=on_quit_to_menu
        ))
        
        if self.items:
            self.items[0].selected = True
    
    def set_game_over_data(self, score: int, message: str = None) -> None:
        """设置游戏结束数据"""
        self.final_score = score
        if message:
            self.death_message = message
    
    def render(self) -> Dict[str, Any]:
        """渲染游戏结束界面"""
        base = super().render()
        base['menu_type'] = 'game_over'
        base['final_score'] = self.final_score
        base['death_message'] = self.death_message
        return base



class MenuManager:
    """
    菜单管理器
    
    统一管理所有菜单界面的显示和切换。
    """
    
    def __init__(self):
        """初始化菜单管理器"""
        self._current_state: MenuState = MenuState.HIDDEN
        
        # 创建所有菜单
        self.main_menu = MainMenu(
            on_new_game=self._on_new_game,
            on_continue=self._on_continue,
            on_settings=self._on_settings,
            on_quit=self._on_quit
        )
        
        self.character_select = CharacterSelectMenu(
            on_select=self._on_character_selected,
            on_back=self._on_character_select_back
        )
        
        self.pause_menu = PauseMenu(
            on_resume=self._on_resume,
            on_settings=self._on_settings,
            on_quit_to_menu=self._on_quit_to_menu
        )
        
        self.results_screen = ResultsScreen(
            on_continue=self._on_results_continue,
            on_retry=self._on_retry,
            on_quit_to_menu=self._on_quit_to_menu
        )
        
        self.game_over_screen = GameOverScreen(
            on_retry=self._on_retry,
            on_quit_to_menu=self._on_quit_to_menu
        )
        
        # 外部回调
        self._callbacks: Dict[str, Optional[Callable]] = {
            'new_game': None,
            'continue': None,
            'settings': None,
            'quit': None,
            'character_selected': None,
            'resume': None,
            'quit_to_menu': None,
            'results_continue': None,
            'retry': None
        }
    
    @property
    def current_state(self) -> MenuState:
        """当前菜单状态"""
        return self._current_state
    
    def set_callback(self, event: str, callback: Callable) -> None:
        """
        设置事件回调
        
        Args:
            event: 事件名称
            callback: 回调函数
        """
        if event in self._callbacks:
            self._callbacks[event] = callback
    
    def show_main_menu(self, has_save: bool = False) -> None:
        """显示主菜单"""
        self._hide_all()
        self.main_menu.set_has_save(has_save)
        self.main_menu.show()
        self._current_state = MenuState.MAIN_MENU
    
    def show_character_select(self, characters: List = None) -> None:
        """显示角色选择界面"""
        self._hide_all()
        if characters:
            self.character_select.load_characters(characters)
        self.character_select.show()
        self._current_state = MenuState.CHARACTER_SELECT
    
    def show_pause_menu(self) -> None:
        """显示暂停菜单"""
        self._hide_all()
        self.pause_menu.show()
        self._current_state = MenuState.PAUSE
    
    def show_results(self, results: ResultsData) -> None:
        """显示结果界面"""
        self._hide_all()
        self.results_screen.set_results(results)
        self.results_screen.show()
        self._current_state = MenuState.RESULTS
    
    def show_game_over(self, score: int, message: str = None) -> None:
        """显示游戏结束界面"""
        self._hide_all()
        self.game_over_screen.set_game_over_data(score, message)
        self.game_over_screen.show()
        self._current_state = MenuState.GAME_OVER
    
    def hide_all(self) -> None:
        """隐藏所有菜单"""
        self._hide_all()
        self._current_state = MenuState.HIDDEN
    
    def _hide_all(self) -> None:
        """内部方法：隐藏所有菜单"""
        self.main_menu.hide()
        self.character_select.hide()
        self.pause_menu.hide()
        self.results_screen.hide()
        self.game_over_screen.hide()
    
    def get_active_menu(self) -> Optional[MenuBase]:
        """获取当前活动的菜单"""
        menu_map = {
            MenuState.MAIN_MENU: self.main_menu,
            MenuState.CHARACTER_SELECT: self.character_select,
            MenuState.PAUSE: self.pause_menu,
            MenuState.RESULTS: self.results_screen,
            MenuState.GAME_OVER: self.game_over_screen
        }
        return menu_map.get(self._current_state)
    
    def handle_input(self, action: str) -> bool:
        """
        处理输入
        
        Args:
            action: 输入动作 ("up", "down", "confirm", "back")
            
        Returns:
            bool: 是否处理了输入
        """
        menu = self.get_active_menu()
        if menu is None:
            return False
        
        if action == "up":
            menu.select_previous()
            return True
        elif action == "down":
            menu.select_next()
            return True
        elif action == "confirm":
            return menu.confirm_selection()
        elif action == "back":
            menu.back()
            return True
        
        return False
    
    def render(self) -> Dict[str, Any]:
        """
        渲染当前菜单
        
        Returns:
            dict: 渲染数据
        """
        menu = self.get_active_menu()
        if menu is None:
            return {'state': 'hidden', 'visible': False}
        
        render_data = menu.render()
        render_data['state'] = self._current_state.value
        return render_data
    
    # ==================== 内部回调 ====================
    
    def _on_new_game(self) -> None:
        """新游戏"""
        if self._callbacks['new_game']:
            self._callbacks['new_game']()
        else:
            # 默认行为：显示角色选择
            self.show_character_select()
    
    def _on_continue(self) -> None:
        """继续游戏"""
        if self._callbacks['continue']:
            self._callbacks['continue']()
    
    def _on_settings(self) -> None:
        """设置"""
        if self._callbacks['settings']:
            self._callbacks['settings']()
    
    def _on_quit(self) -> None:
        """退出"""
        if self._callbacks['quit']:
            self._callbacks['quit']()
    
    def _on_character_selected(self, character_id: str) -> None:
        """角色选择完成"""
        if self._callbacks['character_selected']:
            self._callbacks['character_selected'](character_id)
    
    def _on_character_select_back(self) -> None:
        """角色选择返回"""
        self.show_main_menu()
    
    def _on_resume(self) -> None:
        """继续游戏"""
        if self._callbacks['resume']:
            self._callbacks['resume']()
        self.hide_all()
    
    def _on_quit_to_menu(self) -> None:
        """返回主菜单"""
        if self._callbacks['quit_to_menu']:
            self._callbacks['quit_to_menu']()
        self.show_main_menu()
    
    def _on_results_continue(self) -> None:
        """结果界面继续"""
        if self._callbacks['results_continue']:
            self._callbacks['results_continue']()
    
    def _on_retry(self) -> None:
        """重试"""
        if self._callbacks['retry']:
            self._callbacks['retry']()
