"""
Checkpoint 8 - 验证核心系统基本功能
确保所有已实现的系统可以正常工作
"""
import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.game_manager import GameManager, GameState
from gameplay.resource_system import ResourceSystem
from gameplay.odm_system import ODMSystem, Vec3, Surface
from gameplay.combat_system import CombatSystem, TitanHitbox, Vec3 as CombatVec3
from data.save_system import SaveSystem, SaveData
from content.character import Character, CharacterStats


class TestGameManager:
    """GameManager 基本功能测试"""
    
    def test_initial_state(self):
        """测试初始状态"""
        gm = GameManager()
        assert gm.current_state == GameState.MAIN_MENU
    
    def test_state_transition(self):
        """测试状态转换"""
        gm = GameManager()
        assert gm.change_state(GameState.CHARACTER_SELECT) == True
        assert gm.current_state == GameState.CHARACTER_SELECT
    
    def test_start_new_game(self):
        """测试开始新游戏"""
        gm = GameManager()
        assert gm.start_new_game("eren") == True
        assert gm.selected_character_id == "eren"


class TestResourceSystem:
    """ResourceSystem 基本功能测试"""
    
    def test_initial_resources(self):
        """测试初始资源"""
        rs = ResourceSystem()
        assert rs.gas_level == rs.max_gas
        assert rs.blade_count == rs.max_blades
    
    def test_consume_gas(self):
        """测试消耗气体"""
        rs = ResourceSystem()
        initial_gas = rs.gas_level
        assert rs.consume_gas(10) == True
        assert rs.gas_level == initial_gas - 10
    
    def test_switch_blade(self):
        """测试切换刀刃"""
        rs = ResourceSystem()
        rs._blade_durability = 10  # 模拟耐久度降低
        initial_count = rs.blade_count
        assert rs.switch_blade() == True
        assert rs.blade_count == initial_count - 1
        assert rs.blade_durability == rs.max_blade_durability
    
    def test_supply_station(self):
        """测试补给站"""
        rs = ResourceSystem()
        rs.consume_gas(50)
        rs._blade_count = 2
        rs.interact_with_supply_station()
        assert rs.gas_level == rs.max_gas
        assert rs.blade_count == rs.max_blades


class TestODMSystem:
    """ODMSystem 基本功能测试"""
    
    def test_initial_state(self):
        """测试初始状态"""
        odm = ODMSystem()
        assert odm.gas_level == odm.max_gas
        assert not odm.left_hook.is_attached
        assert not odm.right_hook.is_attached
    
    def test_fire_hook_no_surface(self):
        """测试无表面时发射钩锁"""
        odm = ODMSystem()
        result = odm.fire_hook(Vec3(1, 0, 0))
        assert result == False
    
    def test_fire_hook_with_surface(self):
        """测试有表面时发射钩锁"""
        odm = ODMSystem()
        surface = Surface(position=Vec3(10, 10, 0), is_valid=True)
        odm.add_surface(surface)
        result = odm.fire_hook(Vec3(1, 1, 0))
        assert result == True
        assert odm.right_hook.is_attached
    
    def test_boost_consumes_gas(self):
        """测试推进消耗气体"""
        odm = ODMSystem()
        initial_gas = odm.gas_level
        odm.activate_boost()
        assert odm.gas_level < initial_gas
    
    def test_boost_fails_when_no_gas(self):
        """测试无气体时推进失败"""
        odm = ODMSystem()
        odm._gas_level = 0
        result = odm.activate_boost()
        assert result == False


class TestCombatSystem:
    """CombatSystem 基本功能测试"""
    
    def test_initial_state(self):
        """测试初始状态"""
        cs = CombatSystem()
        assert cs.blade_durability == cs.max_blade_durability
        assert cs.combo_count == 0
    
    def test_nape_hit_detection(self):
        """测试后颈命中检测"""
        cs = CombatSystem()
        titan = TitanHitbox(
            position=CombatVec3(0, 0, 0),
            nape_center=CombatVec3(0, 5, -1),
            nape_radius=1.0
        )
        # 命中后颈
        assert cs.check_nape_hit(titan, CombatVec3(0, 5, -1)) == True
        # 未命中后颈
        assert cs.check_nape_hit(titan, CombatVec3(0, 0, 0)) == False
    
    def test_attack_consumes_durability(self):
        """测试攻击消耗耐久度"""
        cs = CombatSystem()
        titan = TitanHitbox(
            position=CombatVec3(0, 0, 0),
            nape_center=CombatVec3(0, 5, -1),
            nape_radius=1.0
        )
        initial_durability = cs.blade_durability
        cs.perform_slash(titan, CombatVec3(0, 0, 0))
        assert cs.blade_durability < initial_durability
    
    def test_attack_disabled_at_zero_durability(self):
        """测试零耐久度时攻击禁用"""
        cs = CombatSystem()
        cs._blade_durability = 0
        titan = TitanHitbox(
            position=CombatVec3(0, 0, 0),
            nape_center=CombatVec3(0, 5, -1),
            nape_radius=1.0
        )
        result = cs.perform_slash(titan, CombatVec3(0, 5, -1))
        assert result.hit == False


class TestSaveSystem:
    """SaveSystem 基本功能测试"""
    
    def test_serialize_deserialize(self):
        """测试序列化和反序列化"""
        ss = SaveSystem(save_dir="test_saves")
        save_data = SaveData(
            character_id="mikasa",
            current_chapter=3,
            total_score=5000
        )
        json_str = ss.serialize_to_json(save_data)
        restored = ss.deserialize_from_json(json_str)
        assert restored.character_id == save_data.character_id
        assert restored.current_chapter == save_data.current_chapter
        assert restored.total_score == save_data.total_score
    
    def test_save_and_load(self, tmp_path):
        """测试保存和加载"""
        ss = SaveSystem(save_dir=str(tmp_path))
        save_data = SaveData(
            character_id="armin",
            current_chapter=2,
            total_score=3000
        )
        assert ss.save_game(1, save_data) == True
        loaded = ss.load_game(1)
        assert loaded.character_id == save_data.character_id
        assert loaded.current_chapter == save_data.current_chapter


class TestCharacter:
    """Character 基本功能测试"""
    
    def test_load_character(self):
        """测试加载角色"""
        Character.clear_cache()
        char = Character.load_from_json("eren")
        assert char.id == "eren"
        assert char.name == "艾伦·耶格尔"
        assert char.stats is not None
    
    def test_character_stats(self):
        """测试角色属性"""
        Character.clear_cache()
        char = Character.load_from_json("mikasa")
        assert char.stats.speed > 0
        assert char.stats.attack_power > 0
        assert char.stats.stamina > 0
    
    def test_get_all_characters(self):
        """测试获取所有角色"""
        Character.clear_cache()
        characters = Character.get_all_characters()
        assert len(characters) >= 12  # 至少12个104期成员
