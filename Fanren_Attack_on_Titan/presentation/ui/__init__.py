"""
UI组件模块

包含游戏的所有UI组件：
- HUD: 游戏界面显示
- Menu: 菜单系统
- Dialogue: 对话系统
"""

from presentation.ui.hud import (
    HUD,
    HUDData,
    HUDElement,
    ResourceBar,
    CounterDisplay,
    ComboDisplay,
    WarningIndicator,
    ScoreDisplay,
    WarningType
)

from presentation.ui.menu import (
    MenuManager,
    MenuState,
    MenuBase,
    MenuItem,
    MainMenu,
    CharacterSelectMenu,
    PauseMenu,
    ResultsScreen,
    GameOverScreen,
    CharacterSelectData,
    ResultsData
)

from presentation.ui.dialogue import (
    DialogueSystem,
    DialogueState,
    DialogueBox,
    DialogueLine,
    PortraitDisplay,
    CutscenePlayer,
    CutsceneData
)

__all__ = [
    # HUD
    'HUD',
    'HUDData',
    'HUDElement',
    'ResourceBar',
    'CounterDisplay',
    'ComboDisplay',
    'WarningIndicator',
    'ScoreDisplay',
    'WarningType',
    # Menu
    'MenuManager',
    'MenuState',
    'MenuBase',
    'MenuItem',
    'MainMenu',
    'CharacterSelectMenu',
    'PauseMenu',
    'ResultsScreen',
    'GameOverScreen',
    'CharacterSelectData',
    'ResultsData',
    # Dialogue
    'DialogueSystem',
    'DialogueState',
    'DialogueBox',
    'DialogueLine',
    'PortraitDisplay',
    'CutscenePlayer',
    'CutsceneData'
]
