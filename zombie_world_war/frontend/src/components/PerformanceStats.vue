<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import type { PerformanceMetrics } from '@engine/performance/PerformanceMonitor'

const props = defineProps<{
  metrics: PerformanceMetrics | null
  visible?: boolean
}>()

// FPS color based on performance
const fpsColor = computed(() => {
  if (!props.metrics) return '#ffffff'
  const fps = props.metrics.fps
  if (fps >= 55) return '#4ade80' // Green
  if (fps >= 40) return '#fbbf24' // Yellow
  return '#ef4444' // Red
})

// Format memory
const formatMemory = (mb: number): string => {
  return `${mb} MB`
}

// Format number with K suffix
const formatNumber = (num: number): string => {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
}
</script>

<template>
  <div v-if="visible && metrics" class="performance-stats">
    <div class="stat-row">
      <span class="stat-label">FPS:</span>
      <span class="stat-value" :style="{ color: fpsColor }">{{ metrics.fps }}</span>
    </div>
    <div class="stat-row">
      <span class="stat-label">Frame:</span>
      <span class="stat-value">{{ metrics.avgFrameTime.toFixed(1) }}ms</span>
    </div>
    <div class="stat-row">
      <span class="stat-label">Draw:</span>
      <span class="stat-value">{{ metrics.drawCalls }}</span>
    </div>
    <div class="stat-row">
      <span class="stat-label">Tris:</span>
      <span class="stat-value">{{ formatNumber(metrics.triangles) }}</span>
    </div>
    <div class="stat-row">
      <span class="stat-label">Zombies:</span>
      <span class="stat-value">{{ metrics.zombieCount }}</span>
    </div>
    <div v-if="metrics.memoryUsed > 0" class="stat-row">
      <span class="stat-label">Mem:</span>
      <span class="stat-value">{{ formatMemory(metrics.memoryUsed) }}</span>
    </div>
  </div>
</template>

<style scoped>
.performance-stats {
  position: fixed;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  padding: 8px 12px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  color: #ffffff;
  z-index: 9999;
  pointer-events: none;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  line-height: 1.4;
}

.stat-label {
  color: #a0a0a0;
}

.stat-value {
  font-weight: bold;
  text-align: right;
  min-width: 50px;
}
</style>
