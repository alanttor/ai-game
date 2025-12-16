<script setup lang="ts">
import { computed, ref, watch } from 'vue'

/**
 * DamageOverlay Component - Visual feedback for damage and low health
 * Requirements: 9.4 - Red vignette effect proportional to damage received
 * Requirements: 9.5 - Pulsing low health warning indicator when health < 25%
 */

interface Props {
  health: number
  maxHealth: number
  lastDamage: number  // Amount of last damage taken (triggers flash)
  damageTimestamp: number  // Timestamp of last damage (for triggering animation)
}

const props = withDefaults(defineProps<Props>(), {
  health: 100,
  maxHealth: 100,
  lastDamage: 0,
  damageTimestamp: 0,
})

// Track damage flash state
const isDamageFlashing = ref(false)
const damageIntensity = ref(0)

// Computed: Health percentage
const healthPercent = computed(() => (props.health / props.maxHealth) * 100)

// Computed: Is low health (< 25%)
const isLowHealth = computed(() => healthPercent.value < 25 && healthPercent.value > 0)

// Computed: Is critical health (< 10%)
const isCriticalHealth = computed(() => healthPercent.value < 10 && healthPercent.value > 0)

// Computed: Low health vignette intensity (increases as health decreases)
const lowHealthIntensity = computed(() => {
  if (!isLowHealth.value) return 0
  // Scale from 0 at 25% to 0.6 at 0%
  return Math.min(0.6, (25 - healthPercent.value) / 25 * 0.6)
})

// Watch for damage events
watch(() => props.damageTimestamp, () => {
  if (props.lastDamage > 0) {
    triggerDamageFlash(props.lastDamage)
  }
})

// Trigger damage flash effect
function triggerDamageFlash(damage: number) {
  // Calculate intensity based on damage (max at 50 damage)
  damageIntensity.value = Math.min(0.8, damage / 50 * 0.8)
  isDamageFlashing.value = true
  
  // Reset flash after animation
  setTimeout(() => {
    isDamageFlashing.value = false
    damageIntensity.value = 0
  }, 300)
}

// Computed: Combined vignette opacity
const vignetteOpacity = computed(() => {
  if (isDamageFlashing.value) {
    return damageIntensity.value
  }
  return lowHealthIntensity.value
})
</script>

<template>
  <div class="damage-overlay">
    <!-- Damage Flash Vignette -->
    <div 
      class="vignette damage-vignette"
      :class="{ 'flash-active': isDamageFlashing }"
      :style="{ opacity: isDamageFlashing ? damageIntensity : 0 }"
    ></div>

    <!-- Low Health Vignette (persistent) -->
    <div 
      v-if="isLowHealth"
      class="vignette low-health-vignette"
      :class="{ 'critical': isCriticalHealth }"
      :style="{ opacity: lowHealthIntensity }"
    ></div>

    <!-- Low Health Warning Indicator -->
    <div 
      v-if="isLowHealth"
      class="low-health-warning"
      :class="{ 'critical': isCriticalHealth }"
    >
      <div class="warning-icon">⚠</div>
      <div class="warning-text">LOW HEALTH</div>
      <div class="health-value">{{ Math.ceil(props.health) }}</div>
    </div>

    <!-- Heartbeat Effect for Critical Health -->
    <div 
      v-if="isCriticalHealth"
      class="heartbeat-overlay"
    ></div>
  </div>
</template>

<style scoped>
.damage-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 99;
}

/* Base Vignette Style */
.vignette {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  transition: opacity 0.15s ease-out;
}

/* Damage Flash Vignette */
.damage-vignette {
  background: radial-gradient(
    ellipse at center,
    transparent 30%,
    rgba(255, 0, 0, 0.3) 60%,
    rgba(200, 0, 0, 0.7) 100%
  );
}

.damage-vignette.flash-active {
  animation: damageFlash 0.3s ease-out;
}

@keyframes damageFlash {
  0% {
    opacity: 0;
  }
  20% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}

/* Low Health Vignette */
.low-health-vignette {
  background: radial-gradient(
    ellipse at center,
    transparent 40%,
    rgba(180, 0, 0, 0.2) 70%,
    rgba(120, 0, 0, 0.5) 100%
  );
  animation: lowHealthPulse 1.5s ease-in-out infinite;
}

.low-health-vignette.critical {
  background: radial-gradient(
    ellipse at center,
    transparent 30%,
    rgba(200, 0, 0, 0.3) 60%,
    rgba(150, 0, 0, 0.6) 100%
  );
  animation: criticalHealthPulse 0.8s ease-in-out infinite;
}

@keyframes lowHealthPulse {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 0.6;
  }
}

@keyframes criticalHealthPulse {
  0%, 100% {
    opacity: 0.4;
  }
  50% {
    opacity: 0.8;
  }
}

/* Low Health Warning Indicator */
.low-health-warning {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 1rem 2rem;
  background: rgba(0, 0, 0, 0.5);
  border: 2px solid rgba(255, 0, 0, 0.5);
  border-radius: 8px;
  animation: warningPulse 1.5s ease-in-out infinite;
  opacity: 0.8;
}

.low-health-warning.critical {
  border-color: rgba(255, 0, 0, 0.8);
  animation: criticalWarningPulse 0.8s ease-in-out infinite;
}

@keyframes warningPulse {
  0%, 100% {
    opacity: 0.6;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 0.9;
    transform: translate(-50%, -50%) scale(1.02);
  }
}

@keyframes criticalWarningPulse {
  0%, 100% {
    opacity: 0.7;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1.05);
  }
}

.warning-icon {
  font-size: 2rem;
  color: #ef4444;
  animation: iconPulse 0.8s ease-in-out infinite;
}

@keyframes iconPulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.warning-text {
  color: #ef4444;
  font-size: 0.9rem;
  font-weight: bold;
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
}

.health-value {
  color: #ffffff;
  font-size: 1.5rem;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
}

/* Heartbeat Overlay for Critical Health */
.heartbeat-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 4px solid transparent;
  box-sizing: border-box;
  animation: heartbeat 0.8s ease-in-out infinite;
}

@keyframes heartbeat {
  0%, 100% {
    border-color: transparent;
  }
  25% {
    border-color: rgba(255, 0, 0, 0.3);
  }
  50% {
    border-color: transparent;
  }
  75% {
    border-color: rgba(255, 0, 0, 0.2);
  }
}
</style>
