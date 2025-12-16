<script setup lang="ts">
import { computed } from 'vue'
import { WeaponType } from '@engine/types'

/**
 * InventoryView Component - Displays player's weapons in a grid layout
 * Requirements: 9.3 - Display all collected weapons and items in grid layout
 */

// Weapon display info interface
export interface WeaponDisplayInfo {
  id: string
  name: string
  type: WeaponType
  currentAmmo: number
  reserveAmmo: number
  magazineSize: number
  damage: number
  fireRate: number
  isEquipped: boolean
  slot: number
}

// Props
interface Props {
  weapons: WeaponDisplayInfo[]
  currentWeaponIndex: number
}

const props = withDefaults(defineProps<Props>(), {
  weapons: () => [],
  currentWeaponIndex: 0,
})

// Emits
const emit = defineEmits<{
  (e: 'select', slot: number): void
  (e: 'close'): void
}>()

// Get weapon icon based on type
function getWeaponIcon(type: WeaponType): string {
  switch (type) {
    case WeaponType.PISTOL:
      return '🔫'
    case WeaponType.RIFLE:
      return '🎯'
    case WeaponType.SHOTGUN:
      return '💥'
    case WeaponType.MELEE:
      return '🔪'
    default:
      return '❓'
  }
}

// Get weapon type display name
function getWeaponTypeName(type: WeaponType): string {
  switch (type) {
    case WeaponType.PISTOL:
      return '手枪'
    case WeaponType.RIFLE:
      return '步枪'
    case WeaponType.SHOTGUN:
      return '霰弹枪'
    case WeaponType.MELEE:
      return '近战'
    default:
      return '未知'
  }
}

// Calculate ammo percentage for display
function getAmmoPercent(weapon: WeaponDisplayInfo): number {
  const total = weapon.currentAmmo + weapon.reserveAmmo
  const max = weapon.magazineSize + weapon.reserveAmmo
  return max > 0 ? (total / max) * 100 : 0
}

// Get ammo bar color based on percentage
function getAmmoColor(weapon: WeaponDisplayInfo): string {
  const percent = getAmmoPercent(weapon)
  if (percent > 50) return '#4ade80'
  if (percent > 25) return '#fbbf24'
  return '#ef4444'
}

// Select weapon
function selectWeapon(slot: number) {
  emit('select', slot)
}

// Close inventory
function closeInventory() {
  emit('close')
}

// Create empty slots for grid display (4 weapon slots)
const weaponSlots = computed(() => {
  const slots: (WeaponDisplayInfo | null)[] = [null, null, null, null]
  props.weapons.forEach((weapon) => {
    if (weapon.slot >= 0 && weapon.slot < 4) {
      slots[weapon.slot] = weapon
    }
  })
  return slots
})
</script>

<template>
  <div class="inventory-overlay" @click.self="closeInventory">
    <div class="inventory-panel">
      <div class="inventory-header">
        <h2 class="inventory-title">武器库</h2>
        <button class="close-btn" @click="closeInventory">✕</button>
      </div>
      
      <div class="weapons-grid">
        <div 
          v-for="(weapon, index) in weaponSlots" 
          :key="index"
          class="weapon-slot"
          :class="{ 
            'equipped': weapon && index === currentWeaponIndex,
            'empty': !weapon,
            'has-weapon': weapon
          }"
          @click="weapon && selectWeapon(index)"
        >
          <!-- Empty slot -->
          <template v-if="!weapon">
            <div class="empty-slot">
              <span class="slot-number">{{ index + 1 }}</span>
              <span class="empty-text">空</span>
            </div>
          </template>
          
          <!-- Weapon slot -->
          <template v-else>
            <div class="weapon-content">
              <!-- Slot indicator -->
              <div class="slot-indicator">
                <span class="slot-key">{{ index + 1 }}</span>
                <span v-if="index === currentWeaponIndex" class="equipped-badge">装备中</span>
              </div>
              
              <!-- Weapon icon -->
              <div class="weapon-icon">
                {{ getWeaponIcon(weapon.type) }}
              </div>
              
              <!-- Weapon info -->
              <div class="weapon-info">
                <div class="weapon-name">{{ weapon.name }}</div>
                <div class="weapon-type">{{ getWeaponTypeName(weapon.type) }}</div>
              </div>
              
              <!-- Weapon stats -->
              <div class="weapon-stats">
                <div class="stat-row">
                  <span class="stat-label">伤害</span>
                  <span class="stat-value">{{ weapon.damage }}</span>
                </div>
                <div class="stat-row">
                  <span class="stat-label">射速</span>
                  <span class="stat-value">{{ weapon.fireRate }}/s</span>
                </div>
              </div>
              
              <!-- Ammo bar -->
              <div class="ammo-section" v-if="weapon.type !== WeaponType.MELEE">
                <div class="ammo-label">
                  <span>弹药</span>
                  <span class="ammo-count">{{ weapon.currentAmmo }} / {{ weapon.reserveAmmo }}</span>
                </div>
                <div class="ammo-bar">
                  <div 
                    class="ammo-fill" 
                    :style="{ 
                      width: `${getAmmoPercent(weapon)}%`,
                      backgroundColor: getAmmoColor(weapon)
                    }"
                  ></div>
                </div>
              </div>
              
              <!-- Melee indicator -->
              <div class="melee-indicator" v-else>
                <span>无限使用</span>
              </div>
            </div>
          </template>
        </div>
      </div>
      
      <div class="inventory-footer">
        <p class="hint">按 <kbd>1</kbd>-<kbd>4</kbd> 或点击切换武器 | 按 <kbd>Tab</kbd> 或 <kbd>I</kbd> 关闭</p>
      </div>
    </div>
  </div>
</template>


<style scoped>
.inventory-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.inventory-panel {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border: 2px solid rgba(233, 69, 96, 0.5);
  border-radius: 16px;
  padding: 1.5rem;
  min-width: 600px;
  max-width: 800px;
  box-shadow: 0 0 40px rgba(233, 69, 96, 0.3);
}

.inventory-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.inventory-title {
  color: #e94560;
  font-size: 1.75rem;
  margin: 0;
  text-shadow: 0 0 10px rgba(233, 69, 96, 0.5);
}

.close-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  width: 36px;
  height: 36px;
  color: #a0a0a0;
  font-size: 1.25rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #e94560;
  border-color: #e94560;
  color: #ffffff;
}

/* Weapons Grid */
.weapons-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.weapon-slot {
  background: rgba(0, 0, 0, 0.4);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1rem;
  min-height: 180px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.weapon-slot.empty {
  cursor: default;
  opacity: 0.5;
}

.weapon-slot.has-weapon:hover {
  border-color: rgba(233, 69, 96, 0.5);
  background: rgba(233, 69, 96, 0.1);
  transform: translateY(-2px);
}

.weapon-slot.equipped {
  border-color: #e94560;
  background: rgba(233, 69, 96, 0.2);
  box-shadow: 0 0 20px rgba(233, 69, 96, 0.3);
}

/* Empty Slot */
.empty-slot {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
}

.empty-slot .slot-number {
  font-size: 2rem;
  font-weight: bold;
  opacity: 0.5;
}

.empty-slot .empty-text {
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

/* Weapon Content */
.weapon-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.slot-indicator {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.slot-key {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  font-size: 0.85rem;
  color: #a0a0a0;
  font-weight: bold;
}

.equipped-badge {
  background: #e94560;
  color: #ffffff;
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-weight: bold;
  text-transform: uppercase;
}

.weapon-icon {
  font-size: 2.5rem;
  text-align: center;
  margin-bottom: 0.5rem;
}

.weapon-info {
  text-align: center;
  margin-bottom: 0.75rem;
}

.weapon-name {
  color: #ffffff;
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.weapon-type {
  color: #a0a0a0;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Weapon Stats */
.weapon-stats {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 0.75rem;
  padding: 0.5rem;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
}

.stat-row {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  color: #666;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stat-value {
  color: #fbbf24;
  font-size: 1rem;
  font-weight: bold;
}

/* Ammo Section */
.ammo-section {
  margin-top: auto;
}

.ammo-label {
  display: flex;
  justify-content: space-between;
  color: #a0a0a0;
  font-size: 0.8rem;
  margin-bottom: 0.35rem;
}

.ammo-count {
  color: #ffffff;
  font-family: 'Courier New', monospace;
}

.ammo-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.ammo-fill {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
  border-radius: 4px;
}

/* Melee Indicator */
.melee-indicator {
  margin-top: auto;
  text-align: center;
  color: #4ade80;
  font-size: 0.85rem;
  padding: 0.5rem;
  background: rgba(74, 222, 128, 0.1);
  border-radius: 6px;
}

/* Footer */
.inventory-footer {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.hint {
  color: #666;
  font-size: 0.85rem;
  margin: 0;
}

.hint kbd {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  padding: 0.15rem 0.4rem;
  font-family: inherit;
  font-size: 0.8rem;
  color: #a0a0a0;
}

/* Responsive */
@media (max-width: 700px) {
  .inventory-panel {
    min-width: 90%;
    padding: 1rem;
  }
  
  .weapons-grid {
    grid-template-columns: 1fr;
  }
  
  .inventory-title {
    font-size: 1.5rem;
  }
}
</style>
