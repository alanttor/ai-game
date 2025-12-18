"""
场景管理器 - SceneManager
实现场景切换逻辑和加载画面

Requirements:
    7.1 - 关卡加载时生成对应环境
"""
from enum import Enum
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass, field
import time


class SceneType(Enum):
    """场景类型枚举"""
    NONE = "none"
    MAIN_MENU = "main_menu"
    CHARACTER_SELECT = "character_select"
    CUTSCENE = "cutscene"
    GAMEPLAY = "gameplay"
    RESULTS = "results"
    GAME_OVER = "game_over"
    LOADING = "loading"


class LoadingState(Enum):
    """加载状态枚举"""
    IDLE = "idle"
    LOADING = "loading"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class LoadingTask:
    """加载任务数据类"""
    name: str
    description: str
    weight: float = 1.0  # 任务权重，用于计算进度
    completed: bool = False
    error: Optional[str] = None


@dataclass
class LoadingProgress:
    """加载进度数据类"""
    current_task: str = ""
    current_description: str = ""
    progress: float = 0.0  # 0.0 - 1.0
    tasks_completed: int = 0
    total_tasks: int = 0
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'current_task': self.current_task,
            'current_description': self.current_description,
            'progress': self.progress,
            'tasks_completed': self.tasks_completed,
            'total_tasks': self.total_tasks,
            'error_message': self.error_message,
            'percentage': int(self.progress * 100)
        }


@dataclass
class SceneData:
    """场景数据类"""
    scene_type: SceneType
    scene_id: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'scene_type': self.scene_type.value,
            'scene_id': self.scene_id,
            'params': self.params
        }


class LoadingScreen:
    """
    加载画面管理
    
    显示加载进度和提示信息
    """
    
    # 加载提示文本
    LOADING_TIPS: List[str] = [
        "立体机动装置需要消耗气体，注意补给！",
        "攻击巨人的后颈是唯一的致命弱点。",
        "连续击杀可以获得更高的分数加成。",
        "刀刃会随着使用而损耗，记得及时更换。",
        "不同角色有不同的属性加成，选择适合你的角色。",
        "利用建筑物和树木进行立体机动。",
        "奇行种巨人的行动难以预测，要格外小心。",
        "完成任务目标才能通关。",
    ]
    
    def __init__(self):
        """初始化加载画面"""
        self.visible: bool = False
        self.state: LoadingState = LoadingState.IDLE
        self.progress: LoadingProgress = LoadingProgress()
        
        # 加载任务队列
        self._tasks: List[LoadingTask] = []
        self._current_task_index: int = 0
        
        # 当前提示
        self._current_tip: str = ""
        self._tip_index: int = 0
        
        # 回调
        self._on_complete_callback: Optional[Callable] = None
        self._on_error_callback: Optional[Callable[[str], None]] = None
        
        # 最小显示时间（秒），避免加载画面闪烁
        self._min_display_time: float = 0.5
        self._start_time: float = 0.0
    
    def start_loading(self, tasks: List[LoadingTask] = None) -> None:
        """
        开始加载
        
        Args:
            tasks: 加载任务列表
        """
        self.visible = True
        self.state = LoadingState.LOADING
        self._start_time = time.time()
        
        if tasks:
            self._tasks = tasks
        else:
            # 默认任务
            self._tasks = [
                LoadingTask("init", "初始化..."),
                LoadingTask("assets", "加载资源..."),
                LoadingTask("scene", "构建场景...")
            ]
        
        self._current_task_index = 0
        self._update_progress()
        
        # 选择随机提示
        import random
        self._current_tip = random.choice(self.LOADING_TIPS)
    
    def complete_task(self, task_name: str) -> None:
        """
        完成指定任务
        
        Args:
            task_name: 任务名称
        """
        for task in self._tasks:
            if task.name == task_name:
                task.completed = True
                break
        
        self._update_progress()
        
        # 检查是否全部完成
        if all(task.completed for task in self._tasks):
            self._check_complete()
    
    def set_task_error(self, task_name: str, error: str) -> None:
        """
        设置任务错误
        
        Args:
            task_name: 任务名称
            error: 错误信息
        """
        for task in self._tasks:
            if task.name == task_name:
                task.error = error
                break
        
        self.state = LoadingState.ERROR
        self.progress.error_message = error
        
        if self._on_error_callback:
            self._on_error_callback(error)
    
    def _update_progress(self) -> None:
        """更新进度"""
        if not self._tasks:
            return
        
        total_weight = sum(task.weight for task in self._tasks)
        completed_weight = sum(task.weight for task in self._tasks if task.completed)
        
        self.progress.progress = completed_weight / total_weight if total_weight > 0 else 0.0
        self.progress.tasks_completed = sum(1 for task in self._tasks if task.completed)
        self.progress.total_tasks = len(self._tasks)
        
        # 找到当前任务
        for task in self._tasks:
            if not task.completed:
                self.progress.current_task = task.name
                self.progress.current_description = task.description
                break
    
    def _check_complete(self) -> None:
        """检查是否可以完成加载"""
        elapsed = time.time() - self._start_time
        
        if elapsed >= self._min_display_time:
            self._finish_loading()
        else:
            # 需要等待最小显示时间
            # 在实际游戏中，这里会设置一个定时器
            self._finish_loading()
    
    def _finish_loading(self) -> None:
        """完成加载"""
        self.state = LoadingState.COMPLETE
        self.progress.progress = 1.0
        
        if self._on_complete_callback:
            self._on_complete_callback()
    
    def hide(self) -> None:
        """隐藏加载画面"""
        self.visible = False
        self.state = LoadingState.IDLE
        self._tasks.clear()
        self._current_task_index = 0
    
    def set_on_complete_callback(self, callback: Callable) -> None:
        """设置完成回调"""
        self._on_complete_callback = callback
    
    def set_on_error_callback(self, callback: Callable[[str], None]) -> None:
        """设置错误回调"""
        self._on_error_callback = callback
    
    def get_tip(self) -> str:
        """获取当前提示"""
        return self._current_tip
    
    def render(self) -> Dict[str, Any]:
        """
        渲染加载画面
        
        Returns:
            dict: 渲染数据
        """
        return {
            'type': 'loading_screen',
            'visible': self.visible,
            'state': self.state.value,
            'progress': self.progress.to_dict(),
            'tip': self._current_tip,
            'tasks': [
                {
                    'name': task.name,
                    'description': task.description,
                    'completed': task.completed,
                    'error': task.error
                }
                for task in self._tasks
            ]
        }


class SceneManager:
    """
    场景管理器
    
    负责场景切换、加载画面显示和场景生命周期管理。
    
    Requirements:
        7.1 - 关卡加载时生成对应环境
    """
    
    def __init__(self):
        """初始化场景管理器"""
        self._current_scene: SceneData = SceneData(SceneType.NONE)
        self._previous_scene: Optional[SceneData] = None
        self._pending_scene: Optional[SceneData] = None
        
        # 加载画面
        self.loading_screen = LoadingScreen()
        self.loading_screen.set_on_complete_callback(self._on_loading_complete)
        
        # 场景切换回调
        self._scene_callbacks: Dict[SceneType, List[Callable]] = {
            scene_type: [] for scene_type in SceneType
        }
        
        # 场景加载器
        self._scene_loaders: Dict[SceneType, Callable] = {}
        
        # 场景卸载器
        self._scene_unloaders: Dict[SceneType, Callable] = {}
        
        # 通用回调
        self._on_scene_change_callback: Optional[Callable[[SceneData, SceneData], None]] = None
        self._on_scene_loaded_callback: Optional[Callable[[SceneData], None]] = None
    
    @property
    def current_scene(self) -> SceneData:
        """当前场景"""
        return self._current_scene
    
    @property
    def current_scene_type(self) -> SceneType:
        """当前场景类型"""
        return self._current_scene.scene_type
    
    @property
    def is_loading(self) -> bool:
        """是否正在加载"""
        return self.loading_screen.visible
    
    def change_scene(
        self,
        scene_type: SceneType,
        scene_id: str = "",
        params: Dict[str, Any] = None,
        show_loading: bool = True,
        loading_tasks: List[LoadingTask] = None
    ) -> None:
        """
        切换场景
        
        Args:
            scene_type: 目标场景类型
            scene_id: 场景ID（如关卡ID）
            params: 场景参数
            show_loading: 是否显示加载画面
            loading_tasks: 自定义加载任务
        """
        if params is None:
            params = {}
        
        # 创建新场景数据
        new_scene = SceneData(
            scene_type=scene_type,
            scene_id=scene_id,
            params=params
        )
        
        self._pending_scene = new_scene
        
        if show_loading:
            # 显示加载画面
            tasks = loading_tasks or self._get_default_loading_tasks(scene_type)
            self.loading_screen.start_loading(tasks)
            
            # 开始加载场景
            self._start_scene_loading(new_scene)
        else:
            # 直接切换
            self._perform_scene_change(new_scene)
    
    def _get_default_loading_tasks(self, scene_type: SceneType) -> List[LoadingTask]:
        """获取默认加载任务"""
        if scene_type == SceneType.GAMEPLAY:
            return [
                LoadingTask("unload", "卸载当前场景...", weight=0.5),
                LoadingTask("environment", "加载环境...", weight=2.0),
                LoadingTask("titans", "生成巨人...", weight=1.5),
                LoadingTask("player", "初始化玩家...", weight=1.0),
                LoadingTask("ui", "准备界面...", weight=0.5)
            ]
        elif scene_type == SceneType.CUTSCENE:
            return [
                LoadingTask("unload", "准备过场动画...", weight=0.5),
                LoadingTask("assets", "加载资源...", weight=1.0),
                LoadingTask("dialogue", "加载对话...", weight=0.5)
            ]
        else:
            return [
                LoadingTask("init", "初始化...", weight=1.0)
            ]
    
    def _start_scene_loading(self, scene: SceneData) -> None:
        """开始场景加载"""
        # 卸载当前场景
        self._unload_current_scene()
        self.loading_screen.complete_task("unload")
        
        # 调用场景加载器
        if scene.scene_type in self._scene_loaders:
            try:
                loader = self._scene_loaders[scene.scene_type]
                loader(scene, self.loading_screen)
            except Exception as e:
                self.loading_screen.set_task_error("environment", str(e))
                return
        else:
            # 没有自定义加载器，直接完成所有任务
            for task in self.loading_screen._tasks:
                if not task.completed:
                    self.loading_screen.complete_task(task.name)
    
    def _unload_current_scene(self) -> None:
        """卸载当前场景"""
        if self._current_scene.scene_type in self._scene_unloaders:
            unloader = self._scene_unloaders[self._current_scene.scene_type]
            unloader(self._current_scene)
    
    def _on_loading_complete(self) -> None:
        """加载完成回调"""
        if self._pending_scene:
            self._perform_scene_change(self._pending_scene)
            self._pending_scene = None
        
        # 延迟隐藏加载画面
        self.loading_screen.hide()
    
    def _perform_scene_change(self, new_scene: SceneData) -> None:
        """执行场景切换"""
        old_scene = self._current_scene
        self._previous_scene = old_scene
        self._current_scene = new_scene
        
        # 触发场景变化回调
        if self._on_scene_change_callback:
            self._on_scene_change_callback(old_scene, new_scene)
        
        # 触发场景类型特定回调
        for callback in self._scene_callbacks.get(new_scene.scene_type, []):
            callback(new_scene)
        
        # 触发场景加载完成回调
        if self._on_scene_loaded_callback:
            self._on_scene_loaded_callback(new_scene)
    
    def complete_loading_task(self, task_name: str) -> None:
        """
        完成加载任务（供外部调用）
        
        Args:
            task_name: 任务名称
        """
        self.loading_screen.complete_task(task_name)
    
    def set_loading_error(self, task_name: str, error: str) -> None:
        """
        设置加载错误
        
        Args:
            task_name: 任务名称
            error: 错误信息
        """
        self.loading_screen.set_task_error(task_name, error)
    
    # ==================== 场景快捷方法 ====================
    
    def go_to_main_menu(self) -> None:
        """切换到主菜单"""
        self.change_scene(SceneType.MAIN_MENU, show_loading=False)
    
    def go_to_character_select(self) -> None:
        """切换到角色选择"""
        self.change_scene(SceneType.CHARACTER_SELECT, show_loading=False)
    
    def go_to_cutscene(self, cutscene_id: str, params: Dict[str, Any] = None) -> None:
        """
        切换到过场动画
        
        Args:
            cutscene_id: 过场动画ID
            params: 额外参数
        """
        self.change_scene(
            SceneType.CUTSCENE,
            scene_id=cutscene_id,
            params=params or {},
            show_loading=True
        )
    
    def go_to_gameplay(self, level_id: str, params: Dict[str, Any] = None) -> None:
        """
        切换到游戏关卡
        
        Args:
            level_id: 关卡ID
            params: 额外参数
            
        Requirements: 7.1 - 关卡加载时生成对应环境
        """
        self.change_scene(
            SceneType.GAMEPLAY,
            scene_id=level_id,
            params=params or {},
            show_loading=True
        )
    
    def go_to_results(self, results: Dict[str, Any]) -> None:
        """
        切换到结果界面
        
        Args:
            results: 结果数据
        """
        self.change_scene(
            SceneType.RESULTS,
            params={'results': results},
            show_loading=False
        )
    
    def go_to_game_over(self, score: int, message: str = "") -> None:
        """
        切换到游戏结束界面
        
        Args:
            score: 最终分数
            message: 死亡信息
        """
        self.change_scene(
            SceneType.GAME_OVER,
            params={'score': score, 'message': message},
            show_loading=False
        )
    
    def go_back(self) -> bool:
        """
        返回上一个场景
        
        Returns:
            bool: 是否成功返回
        """
        if self._previous_scene:
            self.change_scene(
                self._previous_scene.scene_type,
                self._previous_scene.scene_id,
                self._previous_scene.params,
                show_loading=False
            )
            return True
        return False
    
    # ==================== 回调注册 ====================
    
    def register_scene_callback(
        self,
        scene_type: SceneType,
        callback: Callable[[SceneData], None]
    ) -> None:
        """
        注册场景切换回调
        
        Args:
            scene_type: 场景类型
            callback: 回调函数
        """
        if scene_type in self._scene_callbacks:
            self._scene_callbacks[scene_type].append(callback)
    
    def register_scene_loader(
        self,
        scene_type: SceneType,
        loader: Callable[[SceneData, LoadingScreen], None]
    ) -> None:
        """
        注册场景加载器
        
        Args:
            scene_type: 场景类型
            loader: 加载器函数
        """
        self._scene_loaders[scene_type] = loader
    
    def register_scene_unloader(
        self,
        scene_type: SceneType,
        unloader: Callable[[SceneData], None]
    ) -> None:
        """
        注册场景卸载器
        
        Args:
            scene_type: 场景类型
            unloader: 卸载器函数
        """
        self._scene_unloaders[scene_type] = unloader
    
    def set_on_scene_change_callback(
        self,
        callback: Callable[[SceneData, SceneData], None]
    ) -> None:
        """设置场景变化回调"""
        self._on_scene_change_callback = callback
    
    def set_on_scene_loaded_callback(
        self,
        callback: Callable[[SceneData], None]
    ) -> None:
        """设置场景加载完成回调"""
        self._on_scene_loaded_callback = callback
    
    # ==================== 状态查询 ====================
    
    def get_scene_info(self) -> Dict[str, Any]:
        """
        获取当前场景信息
        
        Returns:
            dict: 场景信息
        """
        return {
            'current_scene': self._current_scene.to_dict(),
            'previous_scene': self._previous_scene.to_dict() if self._previous_scene else None,
            'is_loading': self.is_loading,
            'loading_progress': self.loading_screen.progress.to_dict() if self.is_loading else None
        }
    
    def render(self) -> Dict[str, Any]:
        """
        渲染场景管理器状态
        
        Returns:
            dict: 渲染数据
        """
        return {
            'type': 'scene_manager',
            'current_scene': self._current_scene.to_dict(),
            'is_loading': self.is_loading,
            'loading_screen': self.loading_screen.render() if self.is_loading else None
        }
