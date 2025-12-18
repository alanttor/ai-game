"""
InputManager 单元测试
测试输入管理器的核心功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from core.input_manager import InputManager, InputAction, InputState, KeyBinding


class TestInputManager:
    """InputManager 测试类"""
    
    def test_initial_state(self):
        """测试初始状态"""
        im = InputManager()
        assert im.input_enabled is True
        assert im.tutorial_visible is False
        assert im.should_show_tutorial_on_start() is True
        assert len(im._key_bindings) > 0
        assert len(im._mouse_bindings) > 0
    
    def test_default_key_bindings(self):
        """测试默认按键绑定"""
        im = InputManager()
        
        # 移动键
        assert im._key_bindings.get('w') == InputAction.MOVE_FORWARD
        assert im._key_bindings.get('s') == InputAction.MOVE_BACKWARD
        assert im._key_bindings.get('a') == InputAction.MOVE_LEFT
        assert im._key_bindings.get('d') == InputAction.MOVE_RIGHT
        assert im._key_bindings.get('space') == InputAction.JUMP
        
        # ODM键
        assert im._key_bindings.get('left shift') == InputAction.BOOST
        assert im._key_bindings.get('q') == InputAction.HOOK_LEFT
        assert im._key_bindings.get('e') == InputAction.HOOK_RELEASE
        
        # 鼠标
        assert im._mouse_bindings.get('left') == InputAction.ATTACK
        assert im._mouse_bindings.get('right') == InputAction.HOOK_RIGHT
    
    def test_key_down_up(self):
        """测试按键按下和释放"""
        im = InputManager()
        
        # 按下W
        im.on_key_down('w')
        assert 'w' in im.state.keys_pressed
        assert 'w' in im.state.keys_just_pressed
        assert im.is_action_pressed(InputAction.MOVE_FORWARD)
        assert im.is_action_just_pressed(InputAction.MOVE_FORWARD)
        
        # 更新帧
        im.update(0.016)
        assert 'w' in im.state.keys_pressed
        assert 'w' not in im.state.keys_just_pressed
        assert im.is_action_pressed(InputAction.MOVE_FORWARD)
        assert not im.is_action_just_pressed(InputAction.MOVE_FORWARD)
        
        # 释放W
        im.on_key_up('w')
        assert 'w' not in im.state.keys_pressed
        assert 'w' in im.state.keys_just_released
        assert not im.is_action_pressed(InputAction.MOVE_FORWARD)
    
    def test_mouse_down_up(self):
        """测试鼠标按下和释放"""
        im = InputManager()
        
        # 按下左键
        im.on_mouse_down('left')
        assert 'left' in im.state.mouse_buttons_pressed
        assert 'left' in im.state.mouse_buttons_just_pressed
        assert im.is_action_pressed(InputAction.ATTACK)
        assert im.is_action_just_pressed(InputAction.ATTACK)
        
        # 更新帧
        im.update(0.016)
        assert 'left' in im.state.mouse_buttons_pressed
        assert 'left' not in im.state.mouse_buttons_just_pressed
        
        # 释放左键
        im.on_mouse_up('left')
        assert 'left' not in im.state.mouse_buttons_pressed
        assert 'left' in im.state.mouse_buttons_just_released
    
    def test_movement_direction(self):
        """测试移动方向计算 - Requirement 11.1"""
        im = InputManager()
        im.set_camera_direction((0, 0, 1), (1, 0, 0))
        
        # 按下W（向前）
        im.on_key_down('w')
        im._update_movement_direction()
        direction = im.get_movement_direction()
        assert direction[2] > 0  # Z方向为正（向前）
        
        im.on_key_up('w')
        im.state.keys_pressed.clear()
        
        # 按下D（向右）
        im.on_key_down('d')
        im._update_movement_direction()
        direction = im.get_movement_direction()
        assert direction[0] > 0  # X方向为正（向右）
    
    def test_action_callback(self):
        """测试动作回调"""
        im = InputManager()
        callback_triggered = [False]
        received_action = [None]
        
        def callback(action):
            callback_triggered[0] = True
            received_action[0] = action
        
        im.register_action_callback(InputAction.ATTACK, callback)
        im.on_mouse_down('left')
        
        assert callback_triggered[0] is True
        assert received_action[0] == InputAction.ATTACK
    
    def test_held_callback(self):
        """测试持续按住回调"""
        im = InputManager()
        held_count = [0]
        
        def held_callback(action):
            held_count[0] += 1
        
        im.register_action_callback(InputAction.BOOST, held_callback, on_held=True)
        im.on_key_down('left shift')
        
        # 模拟多帧
        im.update(0.016)
        im.update(0.016)
        im.update(0.016)
        
        assert held_count[0] == 3
    
    def test_input_disabled(self):
        """测试输入禁用"""
        im = InputManager()
        im.input_enabled = False
        
        im.on_key_down('w')
        assert 'w' not in im.state.keys_pressed
        assert not im.is_action_pressed(InputAction.MOVE_FORWARD)
    
    def test_bind_unbind_key(self):
        """测试按键绑定和解绑"""
        im = InputManager()
        
        # 绑定新按键
        im.bind_key('z', InputAction.ATTACK)
        assert im._key_bindings.get('z') == InputAction.ATTACK
        
        # 解绑
        im.unbind_key('z')
        assert 'z' not in im._key_bindings
    
    def test_reset_to_defaults(self):
        """测试重置为默认绑定"""
        im = InputManager()
        
        # 修改绑定
        im.bind_key('z', InputAction.ATTACK)
        im.bind_mouse('middle', InputAction.BOOST)
        
        # 重置
        im.reset_to_defaults()
        
        assert 'z' not in im._key_bindings
        assert 'middle' not in im._mouse_bindings
        assert im._key_bindings.get('w') == InputAction.MOVE_FORWARD
    
    def test_tutorial_system(self):
        """测试教程系统 - Requirement 11.5"""
        im = InputManager()
        
        # 初始状态
        assert im.should_show_tutorial_on_start() is True
        assert im.tutorial_visible is False
        
        # 显示教程
        im.show_tutorial()
        assert im.tutorial_visible is True
        assert im.should_show_tutorial_on_start() is False  # 已显示过
        
        # 隐藏教程
        im.hide_tutorial()
        assert im.tutorial_visible is False
        
        # 切换教程
        im.toggle_tutorial()
        assert im.tutorial_visible is True
    
    def test_tutorial_content(self):
        """测试教程内容"""
        im = InputManager()
        
        bindings = im.get_tutorial_content()
        assert len(bindings) > 0
        
        # 检查包含关键绑定
        actions = [b.action for b in bindings]
        assert InputAction.MOVE_FORWARD in actions
        assert InputAction.ATTACK in actions
        assert InputAction.HOOK_RIGHT in actions
        assert InputAction.BOOST in actions
        
        # 检查教程文本
        text = im.get_tutorial_text()
        assert '控制教程' in text
        assert 'WASD' in text or 'W' in text
        assert '鼠标左键' in text
    
    def test_get_key_for_action(self):
        """测试获取动作对应的按键"""
        im = InputManager()
        
        key = im.get_key_for_action(InputAction.MOVE_FORWARD)
        assert key == 'w'
        
        keys = im.get_all_keys_for_action(InputAction.ATTACK)
        assert 'mouse_left' in keys
    
    def test_bindings_config_save_load(self):
        """测试按键配置保存和加载"""
        im = InputManager()
        
        # 修改配置
        im.bind_key('z', InputAction.JUMP)
        im.show_tutorial()
        
        # 保存配置
        config = im.get_bindings_config()
        
        # 创建新实例并加载配置
        im2 = InputManager()
        im2.set_bindings_config(config)
        
        assert im2._key_bindings.get('z') == InputAction.JUMP
        assert im2._tutorial_shown_once is True
    
    def test_aim_point(self):
        """测试瞄准点设置"""
        im = InputManager()
        
        im.aim_point = (10.0, 5.0, 20.0)
        assert im.aim_point == (10.0, 5.0, 20.0)
    
    def test_reset(self):
        """测试重置状态"""
        im = InputManager()
        
        im.on_key_down('w')
        im.show_tutorial()
        im.input_enabled = False
        
        im.reset()
        
        assert len(im.state.keys_pressed) == 0
        assert im.tutorial_visible is False
        assert im.input_enabled is True


class TestInputState:
    """InputState 测试类"""
    
    def test_reset_frame(self):
        """测试帧重置"""
        state = InputState()
        
        state.keys_just_pressed.add('w')
        state.keys_just_released.add('s')
        state.mouse_buttons_just_pressed.add('left')
        state.mouse_delta = (10.0, 5.0)
        
        state.reset_frame()
        
        assert len(state.keys_just_pressed) == 0
        assert len(state.keys_just_released) == 0
        assert len(state.mouse_buttons_just_pressed) == 0
        assert state.mouse_delta == (0.0, 0.0)


class TestKeyBinding:
    """KeyBinding 测试类"""
    
    def test_key_binding_creation(self):
        """测试按键绑定创建"""
        binding = KeyBinding(
            action=InputAction.ATTACK,
            key='鼠标左键',
            description='斩击攻击',
            is_mouse=True
        )
        
        assert binding.action == InputAction.ATTACK
        assert binding.key == '鼠标左键'
        assert binding.description == '斩击攻击'
        assert binding.is_mouse is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
