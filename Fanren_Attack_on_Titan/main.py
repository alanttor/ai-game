"""
进击的巨人 - 同人游戏
游戏入口文件

整合主菜单 -> 角色选择 -> 剧情 -> 关卡 -> 结果的完整游戏流程

Requirements:
    6.1 - 任务完成解锁下一章节
    10.1 - 保存游戏进度
    10.2 - 加载游戏进度
"""
import os
import sys

# 确保可以导入本地模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import GAME_CONFIG
from core import GameManager, GameState, GameController


def main():
    """游戏主入口"""
    print(f"启动 {GAME_CONFIG.WINDOW_TITLE}")
    print(f"版本: {GAME_CONFIG.SAVE_VERSION}")
    print("-" * 40)
    
    # 初始化游戏控制器（整合所有系统）
    game_controller = GameController()
    
    print("游戏控制器已初始化")
    print(f"当前状态: {game_controller.game_manager.current_state.value}")
    
    # 显示可用角色
    from content.character import Character
    try:
        characters = Character.get_all_character_ids()
        print(f"可用角色: {', '.join(characters)}")
    except Exception as e:
        print(f"加载角色列表失败: {e}")
    
    # 显示可用章节
    chapters = game_controller.story_system.get_all_chapters()
    print(f"可用章节: {len(chapters)} 个")
    for ch in chapters[:3]:  # 只显示前3个
        print(f"  - {ch.title} (Season {ch.season})")
    
    # 检查存档
    saves = game_controller.save_system.get_all_saves_info()
    has_save = any(save is not None for save in saves)
    print(f"存档状态: {'有存档' if has_save else '无存档'}")
    
    print("-" * 40)
    print("游戏系统已就绪")
    print("注意: 完整的游戏循环需要Ursina引擎支持")
    print("当前为系统测试模式")
    
    # 在实际游戏中，这里会启动Ursina的app.run()
    # 目前仅作为系统测试
    
    return game_controller


if __name__ == "__main__":
    controller = main()
