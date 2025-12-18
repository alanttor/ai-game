"""
对话系统 - 游戏对话和过场动画

实现对话框UI、过场动画播放和角色立绘显示。

Requirements:
    6.2 - 剧情章节显示角色视角对话
"""
from dataclasses import dataclass, field
from typing import Optional, Callable, List, Dict, Any
from enum import Enum
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class DialogueState(Enum):
    """对话状态枚举"""
    HIDDEN = "hidden"
    SHOWING = "showing"
    WAITING = "waiting"  # 等待玩家输入
    ANIMATING = "animating"  # 文字动画中
    CUTSCENE = "cutscene"  # 过场动画


@dataclass
class DialogueLine:
    """
    对话行数据
    
    表示单条对话内容
    """
    speaker: str  # 说话者名称
    speaker_id: str  # 说话者ID（用于获取立绘）
    text: str  # 对话文本
    portrait: str = ""  # 立绘路径
    portrait_position: str = "left"  # 立绘位置 ("left", "right", "center")
    emotion: str = "normal"  # 表情 ("normal", "happy", "sad", "angry", "surprised")
    voice_clip: str = ""  # 语音文件路径（可选）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'speaker': self.speaker,
            'speaker_id': self.speaker_id,
            'text': self.text,
            'portrait': self.portrait,
            'portrait_position': self.portrait_position,
            'emotion': self.emotion,
            'voice_clip': self.voice_clip
        }


@dataclass
class CutsceneData:
    """
    过场动画数据
    """
    id: str
    title: str
    dialogue_lines: List[DialogueLine] = field(default_factory=list)
    background_image: str = ""
    background_music: str = ""
    skip_allowed: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'dialogue_count': len(self.dialogue_lines),
            'background_image': self.background_image,
            'background_music': self.background_music,
            'skip_allowed': self.skip_allowed
        }


class DialogueBox:
    """
    对话框UI组件
    
    显示对话文本和说话者信息。
    
    Requirement 6.2: 显示角色视角对话
    """
    
    # 文字显示速度（字符/秒）
    TEXT_SPEED: float = 30.0
    
    def __init__(
        self,
        x: float = 0,
        y: float = -0.35,
        width: float = 0.8,
        height: float = 0.2
    ):
        """
        初始化对话框
        
        Args:
            x: X坐标
            y: Y坐标
            width: 宽度
            height: 高度
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.visible = False
        self.current_line: Optional[DialogueLine] = None
        
        # 文字动画
        self._full_text: str = ""
        self._displayed_text: str = ""
        self._char_index: int = 0
        self._text_timer: float = 0.0
        self._is_animating: bool = False
        
        # 样式
        self.background_color: str = "rgba(0, 0, 0, 0.8)"
        self.text_color: str = "#FFFFFF"
        self.speaker_color: str = "#FFD700"
        self.font_size: float = 0.025
    
    def show_line(self, line: DialogueLine, animate: bool = True) -> None:
        """
        显示对话行
        
        Args:
            line: 对话行数据
            animate: 是否使用文字动画
        """
        self.current_line = line
        self._full_text = line.text
        self.visible = True
        
        if animate:
            self._displayed_text = ""
            self._char_index = 0
            self._text_timer = 0.0
            self._is_animating = True
        else:
            self._displayed_text = self._full_text
            self._is_animating = False
    
    def update(self, dt: float) -> None:
        """
        更新对话框（文字动画）
        
        Args:
            dt: 时间步长
        """
        if not self._is_animating:
            return
        
        self._text_timer += dt
        chars_to_show = int(self._text_timer * self.TEXT_SPEED)
        
        if chars_to_show > self._char_index:
            self._char_index = min(chars_to_show, len(self._full_text))
            self._displayed_text = self._full_text[:self._char_index]
            
            if self._char_index >= len(self._full_text):
                self._is_animating = False
    
    def skip_animation(self) -> None:
        """跳过文字动画，立即显示全部文本"""
        self._displayed_text = self._full_text
        self._char_index = len(self._full_text)
        self._is_animating = False
    
    def is_animation_complete(self) -> bool:
        """检查文字动画是否完成"""
        return not self._is_animating
    
    def hide(self) -> None:
        """隐藏对话框"""
        self.visible = False
        self.current_line = None
        self._full_text = ""
        self._displayed_text = ""
        self._is_animating = False
    
    def render(self) -> Dict[str, Any]:
        """
        渲染对话框
        
        Returns:
            dict: 渲染数据
        """
        return {
            'type': 'dialogue_box',
            'visible': self.visible,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'speaker': self.current_line.speaker if self.current_line else "",
            'text': self._displayed_text,
            'full_text': self._full_text,
            'is_animating': self._is_animating,
            'background_color': self.background_color,
            'text_color': self.text_color,
            'speaker_color': self.speaker_color,
            'font_size': self.font_size
        }


class PortraitDisplay:
    """
    角色立绘显示组件
    
    显示对话中角色的立绘。
    
    Requirement 6.2: 显示角色立绘
    """
    
    def __init__(self, position: str = "left"):
        """
        初始化立绘显示
        
        Args:
            position: 位置 ("left", "right", "center")
        """
        self.position = position
        self.visible = False
        
        self.portrait_path: str = ""
        self.character_id: str = ""
        self.emotion: str = "normal"
        
        # 动画
        self._fade_alpha: float = 1.0
        self._is_fading: bool = False
        self._fade_direction: int = 1  # 1 = fade in, -1 = fade out
        self._fade_speed: float = 3.0
    
    def show(self, portrait_path: str, character_id: str = "", emotion: str = "normal") -> None:
        """
        显示立绘
        
        Args:
            portrait_path: 立绘路径
            character_id: 角色ID
            emotion: 表情
        """
        self.portrait_path = portrait_path
        self.character_id = character_id
        self.emotion = emotion
        self.visible = True
        
        # 开始淡入动画
        self._fade_alpha = 0.0
        self._is_fading = True
        self._fade_direction = 1
    
    def hide(self, animate: bool = True) -> None:
        """
        隐藏立绘
        
        Args:
            animate: 是否使用淡出动画
        """
        if animate:
            self._is_fading = True
            self._fade_direction = -1
        else:
            self.visible = False
            self._fade_alpha = 0.0
    
    def update(self, dt: float) -> None:
        """更新动画"""
        if not self._is_fading:
            return
        
        self._fade_alpha += self._fade_direction * self._fade_speed * dt
        
        if self._fade_direction > 0 and self._fade_alpha >= 1.0:
            self._fade_alpha = 1.0
            self._is_fading = False
        elif self._fade_direction < 0 and self._fade_alpha <= 0.0:
            self._fade_alpha = 0.0
            self._is_fading = False
            self.visible = False
    
    def get_screen_position(self) -> Dict[str, float]:
        """获取屏幕位置"""
        positions = {
            "left": {"x": -0.35, "y": 0.0},
            "right": {"x": 0.35, "y": 0.0},
            "center": {"x": 0.0, "y": 0.0}
        }
        return positions.get(self.position, positions["left"])
    
    def render(self) -> Dict[str, Any]:
        """渲染立绘"""
        pos = self.get_screen_position()
        return {
            'type': 'portrait',
            'visible': self.visible,
            'portrait_path': self.portrait_path,
            'character_id': self.character_id,
            'emotion': self.emotion,
            'position': self.position,
            'x': pos['x'],
            'y': pos['y'],
            'alpha': self._fade_alpha,
            'is_fading': self._is_fading
        }



class CutscenePlayer:
    """
    过场动画播放器
    
    管理过场动画的播放流程。
    
    Requirement 6.2: 过场动画播放
    """
    
    def __init__(self):
        """初始化过场动画播放器"""
        self.current_cutscene: Optional[CutsceneData] = None
        self.current_line_index: int = 0
        self.is_playing: bool = False
        self.is_paused: bool = False
        
        # 回调
        self._on_complete_callback: Optional[Callable] = None
        self._on_line_change_callback: Optional[Callable[[DialogueLine], None]] = None
    
    def load_cutscene(self, cutscene: CutsceneData) -> None:
        """
        加载过场动画
        
        Args:
            cutscene: 过场动画数据
        """
        self.current_cutscene = cutscene
        self.current_line_index = 0
        self.is_playing = False
        self.is_paused = False
    
    def play(self) -> None:
        """开始播放"""
        if self.current_cutscene is None:
            return
        
        self.is_playing = True
        self.is_paused = False
        self.current_line_index = 0
        
        # 触发第一行
        self._trigger_current_line()
    
    def pause(self) -> None:
        """暂停播放"""
        self.is_paused = True
    
    def resume(self) -> None:
        """继续播放"""
        self.is_paused = False
    
    def skip(self) -> None:
        """跳过过场动画"""
        if self.current_cutscene and self.current_cutscene.skip_allowed:
            self._complete()
    
    def advance(self) -> bool:
        """
        前进到下一行
        
        Returns:
            bool: 是否还有更多对话
        """
        if not self.is_playing or self.current_cutscene is None:
            return False
        
        self.current_line_index += 1
        
        if self.current_line_index >= len(self.current_cutscene.dialogue_lines):
            self._complete()
            return False
        
        self._trigger_current_line()
        return True
    
    def _trigger_current_line(self) -> None:
        """触发当前对话行"""
        if self.current_cutscene is None:
            return
        
        if 0 <= self.current_line_index < len(self.current_cutscene.dialogue_lines):
            line = self.current_cutscene.dialogue_lines[self.current_line_index]
            if self._on_line_change_callback:
                self._on_line_change_callback(line)
    
    def _complete(self) -> None:
        """完成过场动画"""
        self.is_playing = False
        if self._on_complete_callback:
            self._on_complete_callback()
    
    def get_current_line(self) -> Optional[DialogueLine]:
        """获取当前对话行"""
        if self.current_cutscene is None:
            return None
        
        if 0 <= self.current_line_index < len(self.current_cutscene.dialogue_lines):
            return self.current_cutscene.dialogue_lines[self.current_line_index]
        return None
    
    def get_progress(self) -> float:
        """
        获取播放进度
        
        Returns:
            float: 进度 (0.0 - 1.0)
        """
        if self.current_cutscene is None or len(self.current_cutscene.dialogue_lines) == 0:
            return 0.0
        
        return self.current_line_index / len(self.current_cutscene.dialogue_lines)
    
    def set_on_complete_callback(self, callback: Callable) -> None:
        """设置完成回调"""
        self._on_complete_callback = callback
    
    def set_on_line_change_callback(self, callback: Callable[[DialogueLine], None]) -> None:
        """设置对话行变化回调"""
        self._on_line_change_callback = callback
    
    def render(self) -> Dict[str, Any]:
        """渲染过场动画状态"""
        return {
            'type': 'cutscene_player',
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'cutscene': self.current_cutscene.to_dict() if self.current_cutscene else None,
            'current_line_index': self.current_line_index,
            'progress': self.get_progress(),
            'current_line': self.get_current_line().to_dict() if self.get_current_line() else None
        }


class DialogueSystem:
    """
    对话系统管理器
    
    整合对话框、立绘显示和过场动画播放。
    
    Requirement 6.2: 剧情章节显示角色视角对话
    """
    
    def __init__(self):
        """初始化对话系统"""
        self._state: DialogueState = DialogueState.HIDDEN
        
        # 组件
        self.dialogue_box = DialogueBox()
        self.left_portrait = PortraitDisplay("left")
        self.right_portrait = PortraitDisplay("right")
        self.cutscene_player = CutscenePlayer()
        
        # 设置过场动画回调
        self.cutscene_player.set_on_line_change_callback(self._on_cutscene_line_change)
        self.cutscene_player.set_on_complete_callback(self._on_cutscene_complete)
        
        # 外部回调
        self._on_dialogue_complete_callback: Optional[Callable] = None
        self._on_cutscene_complete_callback: Optional[Callable] = None
        
        # 当前对话队列
        self._dialogue_queue: List[DialogueLine] = []
        self._queue_index: int = 0
    
    @property
    def state(self) -> DialogueState:
        """当前状态"""
        return self._state
    
    @property
    def is_active(self) -> bool:
        """对话系统是否活动"""
        return self._state != DialogueState.HIDDEN
    
    def show_dialogue(self, lines: List[DialogueLine]) -> None:
        """
        显示对话序列
        
        Args:
            lines: 对话行列表
        """
        if not lines:
            return
        
        self._dialogue_queue = lines
        self._queue_index = 0
        self._state = DialogueState.SHOWING
        
        self._show_current_line()
    
    def show_single_line(self, line: DialogueLine) -> None:
        """
        显示单条对话
        
        Args:
            line: 对话行
        """
        self.show_dialogue([line])
    
    def _show_current_line(self) -> None:
        """显示当前对话行"""
        if self._queue_index >= len(self._dialogue_queue):
            self._complete_dialogue()
            return
        
        line = self._dialogue_queue[self._queue_index]
        
        # 显示对话框
        self.dialogue_box.show_line(line, animate=True)
        self._state = DialogueState.ANIMATING
        
        # 显示立绘
        self._update_portraits(line)
    
    def _update_portraits(self, line: DialogueLine) -> None:
        """更新立绘显示"""
        if line.portrait:
            if line.portrait_position == "left":
                self.left_portrait.show(line.portrait, line.speaker_id, line.emotion)
                self.right_portrait.hide()
            elif line.portrait_position == "right":
                self.right_portrait.show(line.portrait, line.speaker_id, line.emotion)
                self.left_portrait.hide()
            else:
                # center - 使用左侧
                self.left_portrait.show(line.portrait, line.speaker_id, line.emotion)
                self.right_portrait.hide()
        else:
            # 无立绘
            self.left_portrait.hide()
            self.right_portrait.hide()
    
    def advance(self) -> bool:
        """
        前进对话
        
        Returns:
            bool: 是否还有更多对话
        """
        if self._state == DialogueState.HIDDEN:
            return False
        
        # 如果正在播放过场动画
        if self._state == DialogueState.CUTSCENE:
            if not self.dialogue_box.is_animation_complete():
                self.dialogue_box.skip_animation()
                return True
            return self.cutscene_player.advance()
        
        # 如果文字动画未完成，跳过动画
        if not self.dialogue_box.is_animation_complete():
            self.dialogue_box.skip_animation()
            self._state = DialogueState.WAITING
            return True
        
        # 前进到下一行
        self._queue_index += 1
        if self._queue_index >= len(self._dialogue_queue):
            self._complete_dialogue()
            return False
        
        self._show_current_line()
        return True
    
    def skip(self) -> None:
        """跳过当前对话/过场"""
        if self._state == DialogueState.CUTSCENE:
            self.cutscene_player.skip()
        else:
            self._complete_dialogue()
    
    def _complete_dialogue(self) -> None:
        """完成对话"""
        self._state = DialogueState.HIDDEN
        self.dialogue_box.hide()
        self.left_portrait.hide(animate=False)
        self.right_portrait.hide(animate=False)
        self._dialogue_queue.clear()
        self._queue_index = 0
        
        if self._on_dialogue_complete_callback:
            self._on_dialogue_complete_callback()
    
    def play_cutscene(self, cutscene: CutsceneData) -> None:
        """
        播放过场动画
        
        Args:
            cutscene: 过场动画数据
        """
        self._state = DialogueState.CUTSCENE
        self.cutscene_player.load_cutscene(cutscene)
        self.cutscene_player.play()
    
    def _on_cutscene_line_change(self, line: DialogueLine) -> None:
        """过场动画对话行变化回调"""
        self.dialogue_box.show_line(line, animate=True)
        self._update_portraits(line)
    
    def _on_cutscene_complete(self) -> None:
        """过场动画完成回调"""
        self._state = DialogueState.HIDDEN
        self.dialogue_box.hide()
        self.left_portrait.hide(animate=False)
        self.right_portrait.hide(animate=False)
        
        if self._on_cutscene_complete_callback:
            self._on_cutscene_complete_callback()
    
    def update(self, dt: float) -> None:
        """
        更新对话系统
        
        Args:
            dt: 时间步长
        """
        if self._state == DialogueState.HIDDEN:
            return
        
        # 更新对话框动画
        self.dialogue_box.update(dt)
        
        # 更新立绘动画
        self.left_portrait.update(dt)
        self.right_portrait.update(dt)
        
        # 检查动画完成
        if self._state == DialogueState.ANIMATING:
            if self.dialogue_box.is_animation_complete():
                self._state = DialogueState.WAITING
    
    def set_on_dialogue_complete_callback(self, callback: Callable) -> None:
        """设置对话完成回调"""
        self._on_dialogue_complete_callback = callback
    
    def set_on_cutscene_complete_callback(self, callback: Callable) -> None:
        """设置过场动画完成回调"""
        self._on_cutscene_complete_callback = callback
    
    def hide(self) -> None:
        """隐藏对话系统"""
        self._state = DialogueState.HIDDEN
        self.dialogue_box.hide()
        self.left_portrait.hide(animate=False)
        self.right_portrait.hide(animate=False)
    
    def render(self) -> Dict[str, Any]:
        """
        渲染对话系统
        
        Returns:
            dict: 渲染数据
        """
        return {
            'type': 'dialogue_system',
            'state': self._state.value,
            'is_active': self.is_active,
            'dialogue_box': self.dialogue_box.render(),
            'left_portrait': self.left_portrait.render(),
            'right_portrait': self.right_portrait.render(),
            'cutscene': self.cutscene_player.render() if self._state == DialogueState.CUTSCENE else None,
            'queue_length': len(self._dialogue_queue),
            'queue_index': self._queue_index
        }
    
    def create_dialogue_from_story_data(
        self,
        dialogue_id: str,
        character,
        story_dialogues: Dict
    ) -> List[DialogueLine]:
        """
        从剧情数据创建对话行列表
        
        Args:
            dialogue_id: 对话ID
            character: 当前角色
            story_dialogues: 剧情对话数据
            
        Returns:
            List[DialogueLine]: 对话行列表
        """
        lines = []
        
        if dialogue_id not in story_dialogues:
            return lines
        
        dialogue_data = story_dialogues[dialogue_id]
        
        # 获取角色特定对话
        if character.id in dialogue_data:
            texts = dialogue_data[character.id]
            if isinstance(texts, list):
                for text in texts:
                    lines.append(DialogueLine(
                        speaker=character.name,
                        speaker_id=character.id,
                        text=text,
                        portrait=character.portrait,
                        portrait_position="left"
                    ))
            else:
                lines.append(DialogueLine(
                    speaker=character.name,
                    speaker_id=character.id,
                    text=str(texts),
                    portrait=character.portrait,
                    portrait_position="left"
                ))
        
        return lines
