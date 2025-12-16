<script setup lang="ts">
import { computed } from 'vue'

/**
 * GameHUD Component - Displays in-game HUD elements
 * Requirements: 9.1 - Display health bar, ammo count, current weapon, and wave number
 */

// Props for HUD data
interface Props {
  // Player stats
  health: number
  maxHealth: number
  stamina: number
  maxStamina: number
  
  // Weapon info
  currentWeaponName: string
  currentWeaponSlot: number
  currentAmmo: number
  reserveAmmo: number
  magazineSize: number
  isReloading: boolean
  
  // Wave info
  currentWave: number
  zombiesKilled: number
  totalZombiesInWave: number
  isPreparationPhase: boolean
  preparationTimeLeft: number
  
  // Score
  score: number
}

const props = withDefaults(defineProps<Props>(), {
  health: 100,
  maxHealth: 100,
  stamina: 100,
  maxStamina: 100,
  currentWeaponName: 'Pistol',
  currentWeaponSlot: 0,
  currentAmmo: 15,
  reserveAmmo: 60,
  magazineSize: 15,
  isReloading: false,
  currentWave: 1,
  zombiesKilled: 0,
  totalZombiesInWave: 15,
  isPreparationPhase: false,
  preparationTimeLeft: 30,
  score: 0,
})

// Computed values
const healthPercent = computed(() => (props.health / props.maxHealth) * 100)
const staminaPercent = computed(() => (props.stamina / props.maxStamina) * 100)
const zombiesRemaining = computed(() => props.totalZombiesInWave - props.zombiesKilled)

// Health bar color based on health percentage
const healthBarColor = computed(() => {
  if (healthPercent.value > 50) return '#4ade80' // Green
  if (healthPercent.value > 25) return '#fbbf24' // Yellow
  return '#ef4444' // Red
})

// Format preparation time as MM:SS
const formattedPrepTime = computed(() => {
  const seconds = Math.ceil(props.preparationTimeLeft)
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
})

// Format score with commas
const formattedScore = computed(() => {
  return props.score.toLocaleString()
})

// Weapon slot display (1-indexed for user)
const weaponSlotDisplay = computed(() => props.currentWeaponSlot + 1)

// Ammo display text
const ammoDisplay = computed(() => {
  if (props.isReloading) return 'RELOADING...'
  return `${props.currentAmmo} / ${props.reserveAmmo}`
})

// Check if ammo is low (less than 25% of magazine)
const isAmmoLow = computed(() => props.currentAmmo <= props.magazineSize * 0.25 && props.currentAmmo > 0)
const isAmmoEmpty = computed(() => props.currentAmmo === 0)
</script>

<template>
  <div class="game-hud">
    <!-- Top Left: Wave Info -->
    <div class="hud-section top-left">
      <div class="wave-info">
        <div class="wave-number">
          <span class="label">WAVE</span>
          <span class="value">{{ currentWave }}</span>
        </div>
        <div v-if="isPreparationPhase" class="preparation-phase">
          <span class="prep-label">NEXT WAVE IN</span>
          <span class="prep-time">{{ formattedPrepTime }}</span>
        </div>
        <div v-else class="zombie-count">
          <span class="label">ZOMBIES</span>
          <span class="value">{{ zombiesRemaining }}</span>
        </div>
      </div>
    </div>

    <!-- Top Right: Score -->
    <div class="hud-section top-right">
      <div class="score-display">
        <span class="label">SCORE</span>
        <span class="value">{{ formattedScore }}</span>
      </div>
    </div>

    <!-- Bottom Left: Health & Stamina -->
    <div class="hud-section bottom-left">
      <div class="player-stats">
        <!-- Health Bar -->
        <div class="stat-bar health-bar">
          <div class="bar-label">
            <span class="icon">❤</span>
            <span class="text">HEALTH</span>
          </div>
          <div class="bar-container">
            <div 
              class="bar-fill" 
              :style="{ 
                width: `${healthPercent}%`,
                backgroundColor: healthBarColor 
              }"
            ></div>
            <span class="bar-value">{{ Math.ceil(health) }} / {{ maxHealth }}</span>
          </div>
        </div>

        <!-- Stamina Bar -->
        <div class="stat-bar stamina-bar">
          <div class="bar-label">
            <span class="icon">⚡</span>
            <span class="text">STAMINA</span>
          </div>
          <div class="bar-container">
            <div 
              class="bar-fill stamina-fill" 
              :style="{ width: `${staminaPercent}%` }"
            ></div>
            <span class="bar-value">{{ Math.ceil(stamina) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Right: Weapon & Ammo -->
    <div class="hud-section bottom-right">
      <div class="weapon-info">
        <!-- Weapon Name & Slot -->
        <div class="weapon-name">
          <span class="slot-indicator">[{{ weaponSlotDisplay }}]</span>
          <span class="name">{{ currentWeaponName }}</span>
        </div>

        <!-- Ammo Display -->
        <div 
          class="ammo-display"
          :class="{ 
            'low-ammo': isAmmoLow, 
            'empty-ammo': isAmmoEmpty,
            'reloading': isReloading 
          }"
        >
          <span class="ammo-icon">🔫</span>
          <span class="ammo-text">{{ ammoDisplay }}</span>
        </div>
      </div>
    </div>

    <!-- Center: Crosshair -->
    <div class="crosshair">
      <div class="crosshair-dot"></div>
      <div class="crosshair-line top"></div>
      <div class="crosshair-line bottom"></div>
      <div class="crosshair-line left"></div>
      <div class="crosshair-line right"></div>
    </div>
  </div>
</template>


<style scoped>
.game-hud {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 100;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* HUD Sections */
.hud-section {
  position: absolute;
  padding: 1rem;
}

.top-left {
  top: 0;
  left: 0;
}

.top-right {
  top: 0;
  right: 0;
}

.bottom-left {
  bottom: 0;
  left: 0;
}

.bottom-right {
  bottom: 0;
  right: 0;
}

/* Wave Info */
.wave-info {
  background: rgba(0, 0, 0, 0.6);
  border: 2px solid rgba(233, 69, 96, 0.5);
  border-radius: 8px;
  padding: 0.75rem 1.25rem;
  min-width: 150px;
}

.wave-number {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.wave-number .label {
  color: #a0a0a0;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 1px;
}

.wave-number .value {
  color: #e94560;
  font-size: 2rem;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(233, 69, 96, 0.5);
}

.preparation-phase {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.prep-label {
  color: #fbbf24;
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 1px;
}

.prep-time {
  color: #fbbf24;
  font-size: 1.5rem;
  font-weight: bold;
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.zombie-count {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.zombie-count .label {
  color: #a0a0a0;
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 1px;
}

.zombie-count .value {
  color: #ffffff;
  font-size: 1.25rem;
  font-weight: bold;
}

/* Score Display */
.score-display {
  background: rgba(0, 0, 0, 0.6);
  border: 2px solid rgba(233, 69, 96, 0.5);
  border-radius: 8px;
  padding: 0.75rem 1.25rem;
  text-align: right;
}

.score-display .label {
  display: block;
  color: #a0a0a0;
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 1px;
  margin-bottom: 0.25rem;
}

.score-display .value {
  color: #fbbf24;
  font-size: 1.75rem;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(251, 191, 36, 0.5);
}

/* Player Stats */
.player-stats {
  background: rgba(0, 0, 0, 0.6);
  border: 2px solid rgba(233, 69, 96, 0.5);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  min-width: 220px;
}

.stat-bar {
  margin-bottom: 0.5rem;
}

.stat-bar:last-child {
  margin-bottom: 0;
}

.bar-label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin-bottom: 0.25rem;
}

.bar-label .icon {
  font-size: 0.9rem;
}

.bar-label .text {
  color: #a0a0a0;
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 1px;
}

.bar-container {
  position: relative;
  height: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
  border-radius: 4px;
}

.stamina-fill {
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
}

.bar-value {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #ffffff;
  font-size: 0.75rem;
  font-weight: bold;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
}

/* Weapon Info */
.weapon-info {
  background: rgba(0, 0, 0, 0.6);
  border: 2px solid rgba(233, 69, 96, 0.5);
  border-radius: 8px;
  padding: 0.75rem 1.25rem;
  text-align: right;
  min-width: 180px;
}

.weapon-name {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.slot-indicator {
  color: #a0a0a0;
  font-size: 0.9rem;
  font-weight: 600;
}

.weapon-name .name {
  color: #ffffff;
  font-size: 1.1rem;
  font-weight: bold;
  text-transform: uppercase;
}

.ammo-display {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
}

.ammo-icon {
  font-size: 1.25rem;
}

.ammo-text {
  color: #ffffff;
  font-size: 1.5rem;
  font-weight: bold;
  font-family: 'Courier New', monospace;
}

.ammo-display.low-ammo .ammo-text {
  color: #fbbf24;
  animation: pulse 0.5s ease-in-out infinite;
}

.ammo-display.empty-ammo .ammo-text {
  color: #ef4444;
}

.ammo-display.reloading .ammo-text {
  color: #60a5fa;
  font-size: 1rem;
  animation: pulse 0.5s ease-in-out infinite;
}

/* Crosshair */
.crosshair {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.crosshair-dot {
  width: 4px;
  height: 4px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.crosshair-line {
  position: absolute;
  background: rgba(255, 255, 255, 0.7);
}

.crosshair-line.top,
.crosshair-line.bottom {
  width: 2px;
  height: 10px;
  left: 50%;
  transform: translateX(-50%);
}

.crosshair-line.top {
  bottom: 8px;
}

.crosshair-line.bottom {
  top: 8px;
}

.crosshair-line.left,
.crosshair-line.right {
  width: 10px;
  height: 2px;
  top: 50%;
  transform: translateY(-50%);
}

.crosshair-line.left {
  right: 8px;
}

.crosshair-line.right {
  left: 8px;
}
</style>
