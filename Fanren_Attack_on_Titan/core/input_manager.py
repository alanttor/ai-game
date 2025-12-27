"""
输入管理器 - 处理键盘和鼠标输入
负责输入映射、事件分发和控制教程显示

Requirements: 11.1, 11.2, 11.3, 11.4, 11.5
"""
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Optional, Any, Set
from enum import Enum
import sys
import os

# 添加父目录到路径以便导入config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class InputAction(Enum):
    """输入动作枚举"""
    # 移动
    MOVE_FORWARD = "move_forward"
    MOVE_BACKWARD = "move_backward"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    JUMP = "jump"
    
    # 战斗
    ATTACK = "attack"
    
    # ODM系统
    HOOK_LEFT = "hook_left"
    HOOK_RIGHT = "hook_right"
    HOOK_RELEASE = "hook_release"
    BOOST = "boost"
    
    # 资源管理
    SWITCH_BLADE = "switch_blade"
    
    # 系统
    PAUSE = "pause"
    INTERACT = "interact"


@dataclass
class KeyBinding:
    """
    按键绑定数据类
    
    Attributes:
        action: 对应的输入动作
        key: 绑定的按键
        description: 按键描述（用于教程显示）
        is_mouse: 是否为鼠标按键
    """
    action: InputAction
    key: str
    description: str
    is_mouse: bool = False


@dataclass
class InputState:
    """
    输入状态数据类
    
    追踪当前帧的输入状态
    """
    # 按键状态
    keys_pressed: Set[str] = field(default_factory=set)
    keys_just_pressed: Set[str] = field(default_factory=set)
    keys_just_released: Set[str] = field(default_factory=set)
    
    # 鼠标状态
    mouse_position: tuple = (0.0, 0.0)
    mouse_delta: tuple = (0.0, 0.0)
    mouse_buttons_pressed: Set[str] = field(default_factory=set)
    mouse_buttons_just_pressed: Set[str] = field(default_factory=set)
    mouse_buttons_just_released: Set[str] = field(default_factory=set)
    
    # 移动方向（归一化）
    movement_direction: tuple = (0.0, 0.0, 0.0)  # (x, y, z)
    
    def reset_frame(self) -> None:
        """重置帧状态（每帧开始时调用）"""
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.mouse_buttons_just_pressed.clear()
        self.mouse_buttons_just_released.clear()
        self.mouse_delta = (0.0, 0.0)


# 输入事件回调类型
InputCallback = Callable[[InputAction], None]


class InputManager:
    """
    输入管理器
    
    负责处理键盘和鼠标输入，将原始输入映射到游戏动作，
    并分发输入事件给注册的监听器。
    
    Requirements:
        11.1 - 移动键映射到相对于相机方向的移动
        11.2 - 钩锁键触发向相机瞄准点发射钩锁
        11.3 - 攻击键触发向瞄准方向的斩击
        11.4 - 推进键激活气体推进
        11.5 - 游戏开始时显示控制教程
    """
    
    # 默认按键映射
    DEFAULT_KEY_BINDINGS: Dict[str, InputAction] = {
        # 移动 (WASD)
        'w': InputAction.MOVE_FORWARD,
        's': InputAction.MOVE_BACKWARD,
        'a': InputAction.MOVE_LEFT,
        'd': InputAction.MOVE_RIGHT,
        'space': InputAction.JUMP,
        
        # ODM系统
        'left shift': InputAction.BOOST,
        'q': InputAction.HOOK_LEFT,
        'e': InputAction.HOOK_RELEASE,
        'r': InputAction.SWITCH_BLADE,
        
        # 系统
        'escape': InputAction.PAUSE,
        'f': InputAction.INTERACT,
    }
    
    # 默认鼠标映射
    DEFAULT_MOUSE_BINDINGS: Dict[str, InputAction] = {
        'left': InputAction.ATTACK,      # 鼠标左键 - 攻击
        'right': InputAction.HOOK_RIGHT,  # 鼠标右键 - 钩锁
    }
    
    def __init__(self):
        """初始化输入管理器"""
        # 按键绑定
        self._key_bindings: Dict[str, InputAction] = dict(self.DEFAULT_KEY_BINDINGS)
        self._mouse_bindings: Dict[str, InputAction] = dict(self.DEFAULT_MOUSE_BINDINGS)
        
        # 反向映射（动作 -> 按键列表）
        self._action_to_keys: Dict[InputAction, List[str]] = {}
        self._rebuild_action_mapping()
        
        # 输入状态
        self._state = InputState()
        
        # 事件回调
        self._action_callbacks: Dict[InputAction, List[InputCallback]] = {
            action: [] for action in InputAction
        }
        
        # 持续按住的动作回调（每帧触发）
        self._held_callbacks: Dict[InputAction, List[InputCallback]] = {
            action: [] for action in InputAction
        }
        
        # 教程显示状态
        self._tutorial_visible: bool = False
        self._tutorial_shown_once: bool = False
        
        # 相机方向（用于相对移动计算）
        self._camera_forward: tuple = (0.0, 0.0, 1.0)
        self._camera_right: tuple = (1.0, 0.0, 0.0)
        
        # 瞄准点（用于钩锁和攻击方向）
        self._aim_point: tuple = (0.0, 0.0, 10.0)
        
        # 输入启用状态
        self._input_enabled: bool = True
    
    # ==================== 属性访问器 ====================
    
    @property
    def state(self) -> InputState:
        """获取当前输入状态"""
        return self._state
    
    @property
    def tutorial_visible(self) -> bool:
        """教程是否可见"""
        return self._tutorial_visible
    
    @property
    def input_enabled(self) -> bool:
        """输入是否启用"""
        return self._input_enabled
    
    @input_enabled.setter
    def input_enabled(self, value: bool) -> None:
        """设置输入启用状态"""
        self._input_enabled = value
    
    @property
    def aim_point(self) -> tuple:
        """获取当前瞄准点"""
        return self._aim_point
    
    @aim_point.setter
    def aim_point(self, value: tuple) -> None:
        """设置瞄准点"""
        self._aim_point = value
    
    # ==================== 按键绑定管理 ====================
    
    def _rebuild_action_mapping(self) -> None:
        """重建动作到按键的映射"""
        self._action_to_keys = {action: [] for action in InputAction}
        
        for key, action in self._key_bindings.items():
            self._action_to_keys[action].append(key)
        
        for button, action in self._mouse_bindings.items():
            self._action_to_keys[action].append(f"mouse_{button}")
    
    def bind_key(self, key: str, action: InputAction) -> None:
        """
        绑定按键到动作
        
        Args:
            key: 按键名称
            action: 输入动作
        """
        self._key_bindings[key.lower()] = action
        self._rebuild_action_mapping()
    
    def bind_mouse(self, button: str, action: InputAction) -> None:
        """
        绑定鼠标按键到动作
        
        Args:
            button: 鼠标按键名称 ('left', 'right', 'middle')
            action: 输入动作
        """
        self._mouse_bindings[button.lower()] = action
        self._rebuild_action_mapping()
    
    def unbind_key(self, key: str) -> None:
        """解除按键绑定"""
        key = key.lower()
        if key in self._key_bindings:
            del self._key_bindings[key]
            self._rebuild_action_mapping()
    
    def get_key_for_action(self, action: InputAction) -> Optional[str]:
        """获取动作对应的主要按键"""
        keys = self._action_to_keys.get(action, [])
        return keys[0] if keys else None
    
    def get_all_keys_for_action(self, action: InputAction) -> List[str]:
        """获取动作对应的所有按键"""
        return self._action_to_keys.get(action, []).copy()
    
    def reset_to_defaults(self) -> None:
        """重置为默认按键绑定"""
        self._key_bindings = dict(self.DEFAULT_KEY_BINDINGS)
        self._mouse_bindings = dict(self.DEFAULT_MOUSE_BINDINGS)
        self._rebuild_action_mapping()
    
    # ==================== 事件回调注册 ====================
    
    def register_action_callback(
        self,
        action: InputAction,
        callback: InputCallback,
        on_held: bool = False
    ) -> None:
        """
        注册动作回调
        
        Args:
            action: 输入动作
            callback: 回调函数
            on_held: 是否为持续按住回调（每帧触发）
        """
        if on_held:
            self._held_callbacks[action].append(callback)
        else:
            self._action_callbacks[action].append(callback)
    
    def unregister_action_callback(
        self,
        action: InputAction,
        callback: InputCallback,
        on_held: bool = False
    ) -> None:
        """注销动作回调"""
        callbacks = self._held_callbacks if on_held else self._action_callbacks
        if callback in callbacks[action]:
            callbacks[action].remove(callback)
    
    def clear_callbacks(self) -> None:
        """清除所有回调"""
        for action in InputAction:
            self._action_callbacks[action].clear()
            self._held_callbacks[action].clear()
    
    # ==================== 输入处理 ====================
    
    def on_key_down(self, key: str) -> None:
        """
        处理按键按下事件
        
        Args:
            key: 按下的按键
        """
        if not self._input_enabled:
            return
        
        key = key.lower()
        self._state.keys_pressed.add(key)
        self._state.keys_just_pressed.add(key)
        
        # 触发动作回调
        if key in self._key_bindings:
            action = self._key_bindings[key]
            self._trigger_action(action)
    
    def on_key_up(self, key: str) -> None:
        """
        处理按键释放事件
        
        Args:
            key: 释放的按键
        """
        key = key.lower()
        self._state.keys_pressed.discard(key)
        self._state.keys_just_released.add(key)
    
    def on_mouse_down(self, button: str) -> None:
        """
        处理鼠标按下事件
        
        Args:
            button: 按下的鼠标按键
        """
        if not self._input_enabled:
            return
        
        button = button.lower()
        self._state.mouse_buttons_pressed.add(button)
        self._state.mouse_buttons_just_pressed.add(button)
        
        # 触发动作回调
        if button in self._mouse_bindings:
            action = self._mouse_bindings[button]
            self._trigger_action(action)
    
    def on_mouse_up(self, button: str) -> None:
        """
        处理鼠标释放事件
        
        Args:
            button: 释放的鼠标按键
        """
        button = button.lower()
        self._state.mouse_buttons_pressed.discard(button)
        self._state.mouse_buttons_just_released.add(button)
    
    def on_mouse_move(self, position: tuple, delta: tuple) -> None:
        """
        处理鼠标移动事件
        
        Args:
            position: 鼠标位置
            delta: 鼠标移动增量
        """
        self._state.mouse_position = position
        self._state.mouse_delta = delta
    
    def _trigger_action(self, action: InputAction) -> None:
        """触发动作回调"""
        for callback in self._action_callbacks[action]:
            try:
                callback(action)
            except Exception as e:
                print(f"Input callback error for {action}: {e}")
    
    # ==================== 帧更新 ====================
    
    def update(self, dt: float) -> None:
        """
        每帧更新（处理持续按住的输入）
        
        Args:
            dt: 帧间隔时间
        """
        if not self._input_enabled:
            return
        
        # 更新移动方向
        self._update_movement_direction()
        
        # 触发持续按住的动作回调
        self._process_held_actions()
        
        # 重置帧状态
        self._state.reset_frame()
    
    def _update_movement_direction(self) -> None:
        """
        更新移动方向
        
        Requirement 11.1: 移动键映射到相对于相机方向的移动
        """
        # 计算输入方向
        forward = 0.0
        right = 0.0
        
        # 检查移动按键
        for key, action in self._key_bindings.items():
            if key in self._state.keys_pressed:
                if action == InputAction.MOVE_FORWARD:
                    forward += 1.0
                elif action == InputAction.MOVE_BACKWARD:
                    forward -= 1.0
                elif action == InputAction.MOVE_RIGHT:
                    right += 1.0
                elif action == InputAction.MOVE_LEFT:
                    right -= 1.0
        
        # 计算相对于相机的移动方向
        if forward != 0.0 or right != 0.0:
            # 归一化输入
            length = (forward * forward + right * right) ** 0.5
            if length > 0:
                forward /= length
                right /= length
            
            # 计算世界空间移动方向
            cf = self._camera_forward
            cr = self._camera_right
            
            move_x = cf[0] * forward + cr[0] * right
            move_y = 0.0  # 水平移动不改变Y
            move_z = cf[2] * forward + cr[2] * right
            
            # 归一化
            length = (move_x * move_x + move_z * move_z) ** 0.5
            if length > 0:
                move_x /= length
                move_z /= length
            
            self._state.movement_direction = (move_x, move_y, move_z)
        else:
            self._state.movement_direction = (0.0, 0.0, 0.0)
    
    def _process_held_actions(self) -> None:
        """处理持续按住的动作"""
        # 检查按键
        for key, action in self._key_bindings.items():
            if key in self._state.keys_pressed:
                for callback in self._held_callbacks[action]:
                    try:
                        callback(action)
                    except Exception as e:
                        print(f"Held callback error for {action}: {e}")
        
        # 检查鼠标按键
        for button, action in self._mouse_bindings.items():
            if button in self._state.mouse_buttons_pressed:
                for callback in self._held_callbacks[action]:
                    try:
                        callback(action)
                    except Exception as e:
                        print(f"Held callback error for {action}: {e}")
    
    # ==================== 相机方向设置 ====================
    
    def set_camera_direction(self, forward: tuple, right: tuple) -> None:
        """
        设置相机方向（用于相对移动计算）
        
        Args:
            forward: 相机前方向量 (x, y, z)
            right: 相机右方向量 (x, y, z)
        """
        self._camera_forward = forward
        self._camera_right = right
    
    # ==================== 输入查询 ====================
    
    def is_action_pressed(self, action: InputAction) -> bool:
        """
        检查动作是否正在按住
        
        Args:
            action: 输入动作
            
        Returns:
            bool: 是否按住
        """
        # 检查按键
        for key, bound_action in self._key_bindings.items():
            if bound_action == action and key in self._state.keys_pressed:
                return True
        
        # 检查鼠标
        for button, bound_action in self._mouse_bindings.items():
            if bound_action == action and button in self._state.mouse_buttons_pressed:
                return True
        
        return False
    
    def is_action_just_pressed(self, action: InputAction) -> bool:
        """
        检查动作是否刚刚按下
        
        Args:
            action: 输入动作
            
        Returns:
            bool: 是否刚按下
        """
        # 检查按键
        for key, bound_action in self._key_bindings.items():
            if bound_action == action and key in self._state.keys_just_pressed:
                return True
        
        # 检查鼠标
        for button, bound_action in self._mouse_bindings.items():
            if bound_action == action and button in self._state.mouse_buttons_just_pressed:
                return True
        
        return False
    
    def is_action_just_released(self, action: InputAction) -> bool:
        """
        检查动作是否刚刚释放
        
        Args:
            action: 输入动作
            
        Returns:
            bool: 是否刚释放
        """
        # 检查按键
        for key, bound_action in self._key_bindings.items():
            if bound_action == action and key in self._state.keys_just_released:
                return True
        
        # 检查鼠标
        for button, bound_action in self._mouse_bindings.items():
            if bound_action == action and button in self._state.mouse_buttons_just_released:
                return True
        
        return False
    
    def get_movement_direction(self) -> tuple:
        """
        获取当前移动方向
        
        Requirement 11.1: 返回相对于相机方向的移动向量
        
        Returns:
            tuple: 移动方向 (x, y, z)
        """
        return self._state.movement_direction
    
    def get_aim_direction(self) -> tuple:
        """
        获取瞄准方向（从玩家位置指向瞄准点）
        
        Requirements 11.2, 11.3: 用于钩锁发射和攻击方向
        
        Returns:
            tuple: 瞄准方向 (x, y, z)
        """
        # 简化实现：返回相机前方向
        # 实际游戏中应该从玩家位置计算到瞄准点的方向
        return self._camera_forward
    
    # ==================== 教程系统 ====================
    
    def show_tutorial(self) -> None:
        """
        显示控制教程
        
        Requirement 11.5: 游戏开始时显示控制教程
        """
        self._tutorial_visible = True
        self._tutorial_shown_once = True
    
    def hide_tutorial(self) -> None:
        """隐藏控制教程"""
        self._tutorial_visible = False
    
    def toggle_tutorial(self) -> None:
        """切换教程显示状态"""
        self._tutorial_visible = not self._tutorial_visible
    
    def get_tutorial_content(self) -> List[KeyBinding]:
        """
        获取教程内容（按键绑定列表）
        
        Returns:
            List[KeyBinding]: 按键绑定列表
        """
        bindings = []
        
        # 移动控制
        bindings.append(KeyBinding(
            InputAction.MOVE_FORWARD, 'W', '向前移动'
        ))
        bindings.append(KeyBinding(
            InputAction.MOVE_BACKWARD, 'S', '向后移动'
        ))
        bindings.append(KeyBinding(
            InputAction.MOVE_LEFT, 'A', '向左移动'
        ))
        bindings.append(KeyBinding(
            InputAction.MOVE_RIGHT, 'D', '向右移动'
        ))
        bindings.append(KeyBinding(
            InputAction.JUMP, 'Space', '跳跃'
        ))
        
        # 战斗控制
        bindings.append(KeyBinding(
            InputAction.ATTACK, '鼠标左键', '斩击攻击', is_mouse=True
        ))
        bindings.append(KeyBinding(
            InputAction.HOOK_RIGHT, '鼠标右键', '发射钩锁', is_mouse=True
        ))
        bindings.append(KeyBinding(
            InputAction.HOOK_LEFT, 'Q', '发射左钩锁'
        ))
        bindings.append(KeyBinding(
            InputAction.HOOK_RELEASE, 'E', '释放钩锁'
        ))
        bindings.append(KeyBinding(
            InputAction.BOOST, 'Shift', '气体推进'
        ))
        bindings.append(KeyBinding(
            InputAction.SWITCH_BLADE, 'R', '切换刀刃'
        ))
        
        # 系统控制
        bindings.append(KeyBinding(
            InputAction.PAUSE, 'Esc', '暂停游戏'
        ))
        bindings.append(KeyBinding(
            InputAction.INTERACT, 'F', '交互'
        ))
        
        return bindings
    
    def get_tutorial_text(self) -> str:
        """
        获取教程文本（格式化的字符串）
        
        Returns:
            str: 格式化的教程文本
        """
        lines = [
            "=== 控制教程 ===",
            "",
            "【移动】",
            "  W - 向前移动",
            "  S - 向后移动",
            "  A - 向左移动",
            "  D - 向右移动",
            "  Space - 跳跃",
            "",
            "【战斗】",
            "  鼠标左键 - 斩击攻击",
            "  R - 切换刀刃",
            "",
            "【立体机动装置】",
            "  鼠标右键 - 发射钩锁",
            "  Q - 发射左钩锁",
            "  E - 释放钩锁",
            "  Shift - 气体推进",
            "",
            "【系统】",
            "  Esc - 暂停游戏",
            "  F - 交互",
            "",
            "按任意键关闭教程..."
        ]
        return "\n".join(lines)
    
    def should_show_tutorial_on_start(self) -> bool:
        """
        检查是否应该在游戏开始时显示教程
        
        Requirement 11.5: 为新玩家显示控制教程
        
        Returns:
            bool: 是否应该显示教程
        """
        return not self._tutorial_shown_once
    
    # ==================== 状态管理 ====================
    
    def get_bindings_config(self) -> Dict[str, Any]:
        """
        获取按键绑定配置（用于存档）
        
        Returns:
            dict: 按键绑定配置
        """
        return {
            'key_bindings': {k: v.value for k, v in self._key_bindings.items()},
            'mouse_bindings': {k: v.value for k, v in self._mouse_bindings.items()},
            'tutorial_shown': self._tutorial_shown_once
        }
    
    def set_bindings_config(self, config: Dict[str, Any]) -> None:
        """
        设置按键绑定配置（用于存档恢复）
        
        Args:
            config: 按键绑定配置
        """
        if 'key_bindings' in config:
            self._key_bindings = {
                k: InputAction(v) for k, v in config['key_bindings'].items()
            }
        
        if 'mouse_bindings' in config:
            self._mouse_bindings = {
                k: InputAction(v) for k, v in config['mouse_bindings'].items()
            }
        
        if 'tutorial_shown' in config:
            self._tutorial_shown_once = config['tutorial_shown']
        
        self._rebuild_action_mapping()
    
    def reset(self) -> None:
        """重置输入管理器状态"""
        self._state = InputState()
        self._tutorial_visible = False
        self._input_enabled = True
    
    def __repr__(self) -> str:
        return (
            f"InputManager(enabled={self._input_enabled}, "
            f"tutorial_visible={self._tutorial_visible}, "
            f"keys_pressed={len(self._state.keys_pressed)})"
        )
