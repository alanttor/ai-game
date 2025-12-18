"""
游戏状态管理器
负责管理游戏全局状态和流程控制
"""
from enum import Enum
from typing import Optional, Callable, Dict, Any


class GameState(Enum):
    """游戏状态枚举"""
    MAIN_MENU = "main_menu"
    CHARACTER_SELECT = "character_select"
    GAMEPLAY = "gameplay"
    CUTSCENE = "cutscene"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    RESULTS = "results"


class GameManager:
    """
    游戏全局状态管理器
    
    负责:
    - 管理游戏状态转换
    - 控制游戏流程 (新游戏、暂停、继续)
    - 维护当前角色和章节信息
    - 管理分数系统
    """
    
    # 有效的状态转换映射
    VALID_TRANSITIONS: Dict[GameState, set] = {
        GameState.MAIN_MENU: {GameState.CHARACTER_SELECT, GameState.GAMEPLAY},
        GameState.CHARACTER_SELECT: {GameState.MAIN_MENU, GameState.GAMEPLAY, GameState.CUTSCENE},
        GameState.GAMEPLAY: {GameState.PAUSED, GameState.CUTSCENE, GameState.GAME_OVER, GameState.RESULTS},
        GameState.CUTSCENE: {GameState.GAMEPLAY, GameState.RESULTS},
        GameState.PAUSED: {GameState.GAMEPLAY, GameState.MAIN_MENU},
        GameState.GAME_OVER: {GameState.MAIN_MENU, GameState.GAMEPLAY},
        GameState.RESULTS: {GameState.MAIN_MENU, GameState.GAMEPLAY, GameState.CHARACTER_SELECT},
    }
    
    def __init__(self):
        """初始化游戏管理器"""
        self._current_state: GameState = GameState.MAIN_MENU
        self._previous_state: Optional[GameState] = None
        self._selected_character_id: Optional[str] = None
        self._current_chapter: int = 1
        self._score: int = 0
        self._is_running: bool = False
        
        # 状态变化回调
        self._state_callbacks: Dict[GameState, list] = {state: [] for state in GameState}
    
    @property
    def current_state(self) -> GameState:
        """获取当前游戏状态"""
        return self._current_state
    
    @property
    def previous_state(self) -> Optional[GameState]:
        """获取上一个游戏状态"""
        return self._previous_state
    
    @property
    def selected_character_id(self) -> Optional[str]:
        """获取当前选择的角色ID"""
        return self._selected_character_id
    
    @property
    def current_chapter(self) -> int:
        """获取当前章节"""
        return self._current_chapter
    
    @property
    def score(self) -> int:
        """获取当前分数"""
        return self._score
    
    @property
    def is_running(self) -> bool:
        """游戏是否正在运行"""
        return self._is_running
    
    def change_state(self, new_state: GameState) -> bool:
        """
        切换游戏状态
        
        Args:
            new_state: 目标状态
            
        Returns:
            bool: 状态切换是否成功
        """
        if not isinstance(new_state, GameState):
            raise ValueError(f"Invalid state type: {type(new_state)}")
        
        # 检查是否是有效的状态转换
        valid_targets = self.VALID_TRANSITIONS.get(self._current_state, set())
        if new_state not in valid_targets:
            return False
        
        # 执行状态切换
        self._previous_state = self._current_state
        self._current_state = new_state
        
        # 触发状态回调
        self._trigger_callbacks(new_state)
        
        return True
    
    def force_state(self, new_state: GameState) -> None:
        """
        强制切换状态 (跳过验证)
        仅用于特殊情况如加载存档
        
        Args:
            new_state: 目标状态
        """
        if not isinstance(new_state, GameState):
            raise ValueError(f"Invalid state type: {type(new_state)}")
        
        self._previous_state = self._current_state
        self._current_state = new_state
        self._trigger_callbacks(new_state)
    
    def start_new_game(self, character_id: str) -> bool:
        """
        开始新游戏
        
        Args:
            character_id: 选择的角色ID
            
        Returns:
            bool: 是否成功开始新游戏
        """
        if not character_id:
            return False
        
        # 重置游戏状态
        self._selected_character_id = character_id
        self._current_chapter = 1
        self._score = 0
        
        # 切换到游戏状态或过场动画
        self.force_state(GameState.CUTSCENE)
        return True
    
    def load_game_state(self, character_id: str, chapter: int, score: int) -> None:
        """
        加载游戏状态 (用于读档)
        
        Args:
            character_id: 角色ID
            chapter: 章节号
            score: 分数
        """
        self._selected_character_id = character_id
        self._current_chapter = chapter
        self._score = score
    
    def pause_game(self) -> bool:
        """
        暂停游戏
        
        Returns:
            bool: 是否成功暂停
        """
        if self._current_state != GameState.GAMEPLAY:
            return False
        
        return self.change_state(GameState.PAUSED)
    
    def resume_game(self) -> bool:
        """
        继续游戏
        
        Returns:
            bool: 是否成功继续
        """
        if self._current_state != GameState.PAUSED:
            return False
        
        return self.change_state(GameState.GAMEPLAY)
    
    def add_score(self, points: int) -> None:
        """
        增加分数
        
        Args:
            points: 要增加的分数
        """
        if points > 0:
            self._score += points
    
    def advance_chapter(self) -> None:
        """推进到下一章节"""
        self._current_chapter += 1
    
    def register_callback(self, state: GameState, callback: Callable[[], None]) -> None:
        """
        注册状态变化回调
        
        Args:
            state: 触发回调的状态
            callback: 回调函数
        """
        if state in self._state_callbacks:
            self._state_callbacks[state].append(callback)
    
    def _trigger_callbacks(self, state: GameState) -> None:
        """触发指定状态的所有回调"""
        for callback in self._state_callbacks.get(state, []):
            try:
                callback()
            except Exception as e:
                print(f"Callback error for state {state}: {e}")
    
    def run(self) -> None:
        """
        启动游戏主循环
        注意: 实际的Ursina游戏循环将在后续实现
        """
        self._is_running = True
        print("游戏管理器已启动")
        print(f"当前状态: {self._current_state.value}")
        
        # 这里将来会集成Ursina的app.run()
        # 目前仅作为占位
    
    def quit(self) -> None:
        """退出游戏"""
        self._is_running = False
        print("游戏已退出")
