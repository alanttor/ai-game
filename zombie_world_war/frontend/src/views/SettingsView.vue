<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useSettingsStore, DEFAULT_SETTINGS } from '@/stores'
import type { GameSettings } from '@/stores'

/**
 * SettingsView - Full settings page
 * Requirements: 1.2, 10.5
 */

const router = useRouter()
const settingsStore = useSettingsStore()

// Current tab
const currentTab = ref<'controls' | 'audio' | 'graphics' | 'gameplay'>('controls')

// Local copy of settings for editing
const localSettings = ref<GameSettings>({ ...settingsStore.settings })

// Track if settings have changed
const hasChanges = computed(() => {
  return JSON.stringify(localSettings.value) !== JSON.stringify(settingsStore.settings)
})

// Initialize settings on mount
onMounted(() => {
  settingsStore.initSettings()
  localSettings.value = { ...settingsStore.settings }
})

// Watch for store changes
watch(() => settingsStore.settings, (newSettings) => {
  localSettings.value = { ...newSettings }
}, { deep: true })

// Save settings
function saveSettings() {
  settingsStore.updateSettings(localSettings.value)
}

// Reset current tab to defaults
function resetCurrentTab() {
  switch (currentTab.value) {
    case 'controls':
      localSettings.value.mouseSensitivity = DEFAULT_SETTINGS.mouseSensitivity
      localSettings.value.invertMouseY = DEFAULT_SETTINGS.invertMouseY
      break
    case 'audio':
      localSettings.value.masterVolume = DEFAULT_SETTINGS.masterVolume
      localSettings.value.musicVolume = DEFAULT_SETTINGS.musicVolume
      localSettings.value.sfxVolume = DEFAULT_SETTINGS.sfxVolume
      localSettings.value.ambientVolume = DEFAULT_SETTINGS.ambientVolume
      break
    case 'graphics':
      localSettings.value.targetFPS = DEFAULT_SETTINGS.targetFPS
      localSettings.value.shadowQuality = DEFAULT_SETTINGS.shadowQuality
      localSettings.value.drawDistance = DEFAULT_SETTINGS.drawDistance
      break
    case 'gameplay':
      localSettings.value.showCrosshair = DEFAULT_SETTINGS.showCrosshair
      localSettings.value.showDamageNumbers = DEFAULT_SETTINGS.showDamageNumbers
      localSettings.value.screenShake = DEFAULT_SETTINGS.screenShake
      break
  }
}

// Reset all settings
function resetAllSettings() {
  localSettings.value = { ...DEFAULT_SETTINGS }
}

// Go back
function goBack() {
  if (hasChanges.value) {
    settingsStore.updateSettings(localSettings.value)
  }
  router.push('/')
}
</script>

<template>
  <div class="settings-view">
    <div class="settings-container">
      <h1 class="settings-title">游戏设置</h1>
      
      <!-- Tab Navigation -->
      <div class="tab-nav">
        <button class="tab-btn" :class="{ active: currentTab === 'controls' }" @click="currentTab = 'controls'">控制</button>
        <button class="tab-btn" :class="{ active: currentTab === 'audio' }" @click="currentTab = 'audio'">音频</button>
        <button class="tab-btn" :class="{ active: currentTab === 'graphics' }" @click="currentTab = 'graphics'">画面</button>
        <button class="tab-btn" :class="{ active: currentTab === 'gameplay' }" @click="currentTab = 'gameplay'">游戏</button>
      </div>
      
      <!-- Settings Content -->
      <div class="settings-content">
        <!-- Controls Tab -->
        <div v-if="currentTab === 'controls'" class="tab-content">
          <div class="setting-item">
            <label>鼠标灵敏度</label>
            <div class="slider-container">
              <input type="range" v-model.number="localSettings.mouseSensitivity" min="1" max="100" class="slider" />
              <span class="slider-value">{{ localSettings.mouseSensitivity }}</span>
            </div>
          </div>
          <div class="setting-item">
            <label>反转垂直视角</label>
            <div class="toggle-container">
              <button class="toggle-btn" :class="{ active: localSettings.invertMouseY }" @click="localSettings.invertMouseY = !localSettings.invertMouseY">
                {{ localSettings.invertMouseY ? '开启' : '关闭' }}
              </button>
            </div>
          </div>
        </div>
        
        <!-- Audio Tab -->
        <div v-if="currentTab === 'audio'" class="tab-content">
          <div class="setting-item">
            <label>主音量</label>
            <div class="slider-container">
              <input type="range" v-model.number="localSettings.masterVolume" min="0" max="100" class="slider" />
              <span class="slider-value">{{ localSettings.masterVolume }}%</span>
            </div>
          </div>
          <div class="setting-item">
            <label>音乐音量</label>
            <div class="slider-container">
              <input type="range" v-model.number="localSettings.musicVolume" min="0" max="100" class="slider" />
              <span class="slider-value">{{ localSettings.musicVolume }}%</span>
            </div>
          </div>
          <div class="setting-item">
            <label>音效音量</label>
            <div class="slider-container">
              <input type="range" v-model.number="localSettings.sfxVolume" min="0" max="100" class="slider" />
              <span class="slider-value">{{ localSettings.sfxVolume }}%</span>
            </div>
          </div>
          <div class="setting-item">
            <label>环境音量</label>
            <div class="slider-container">
              <input type="range" v-model.number="localSettings.ambientVolume" min="0" max="100" class="slider" />
              <span class="slider-value">{{ localSettings.ambientVolume }}%</span>
            </div>
          </div>
        </div>
        
        <!-- Graphics Tab -->
        <div v-if="currentTab === 'graphics'" class="tab-content">
          <div class="setting-item">
            <label>目标帧率</label>
            <div class="select-container">
              <select v-model.number="localSettings.targetFPS" class="select-input">
                <option :value="30">30 FPS</option>
                <option :value="60">60 FPS</option>
                <option :value="120">120 FPS</option>
              </select>
            </div>
          </div>
          <div class="setting-item">
            <label>阴影质量</label>
            <div class="select-container">
              <select v-model="localSettings.shadowQuality" class="select-input">
                <option value="low">低</option>
                <option value="medium">中</option>
                <option value="high">高</option>
              </select>
            </div>
          </div>
          <div class="setting-item">
            <label>视距</label>
            <div class="select-container">
              <select v-model="localSettings.drawDistance" class="select-input">
                <option value="low">近</option>
                <option value="medium">中</option>
                <option value="high">远</option>
              </select>
            </div>
          </div>
        </div>
        
        <!-- Gameplay Tab -->
        <div v-if="currentTab === 'gameplay'" class="tab-content">
          <div class="setting-item">
            <label>显示准星</label>
            <div class="toggle-container">
              <button class="toggle-btn" :class="{ active: localSettings.showCrosshair }" @click="localSettings.showCrosshair = !localSettings.showCrosshair">
                {{ localSettings.showCrosshair ? '开启' : '关闭' }}
              </button>
            </div>
          </div>
          <div class="setting-item">
            <label>显示伤害数字</label>
            <div class="toggle-container">
              <button class="toggle-btn" :class="{ active: localSettings.showDamageNumbers }" @click="localSettings.showDamageNumbers = !localSettings.showDamageNumbers">
                {{ localSettings.showDamageNumbers ? '开启' : '关闭' }}
              </button>
            </div>
          </div>
          <div class="setting-item">
            <label>屏幕震动</label>
            <div class="toggle-container">
              <button class="toggle-btn" :class="{ active: localSettings.screenShake }" @click="localSettings.screenShake = !localSettings.screenShake">
                {{ localSettings.screenShake ? '开启' : '关闭' }}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Action Buttons -->
      <div class="action-buttons">
        <button class="action-btn reset" @click="resetCurrentTab">重置当前页</button>
        <button class="action-btn reset-all" @click="resetAllSettings">重置全部</button>
        <button class="action-btn save" @click="saveSettings" :disabled="!hasChanges">保存设置</button>
        <button class="action-btn back" @click="goBack">返回</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.settings-container {
  background: rgba(0, 0, 0, 0.6);
  border: 2px solid rgba(233, 69, 96, 0.5);
  border-radius: 16px;
  padding: 2rem;
  width: 100%;
  max-width: 600px;
}

.settings-title {
  color: #e94560;
  font-size: 2rem;
  text-align: center;
  margin-bottom: 1.5rem;
  text-shadow: 0 0 10px rgba(233, 69, 96, 0.5);
}

.tab-nav {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 0.5rem;
}

.tab-btn {
  flex: 1;
  padding: 0.75rem 1rem;
  background: transparent;
  border: none;
  color: #a0a0a0;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 4px;
}

.tab-btn:hover { color: #ffffff; background: rgba(255, 255, 255, 0.1); }
.tab-btn.active { color: #e94560; background: rgba(233, 69, 96, 0.2); }

.settings-content { min-height: 300px; }
.tab-content { animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.setting-item { margin-bottom: 1.5rem; }
.setting-item label { display: block; color: #a0a0a0; font-size: 0.9rem; margin-bottom: 0.5rem; }

.slider-container { display: flex; align-items: center; gap: 1rem; }
.slider { flex: 1; height: 8px; -webkit-appearance: none; appearance: none; background: rgba(255, 255, 255, 0.1); border-radius: 4px; outline: none; }
.slider::-webkit-slider-thumb { -webkit-appearance: none; appearance: none; width: 20px; height: 20px; background: #e94560; border-radius: 50%; cursor: pointer; transition: transform 0.2s; }
.slider::-webkit-slider-thumb:hover { transform: scale(1.2); }
.slider::-moz-range-thumb { width: 20px; height: 20px; background: #e94560; border-radius: 50%; cursor: pointer; border: none; }
.slider-value { color: #ffffff; font-size: 0.9rem; min-width: 50px; text-align: right; }

.toggle-container { display: flex; }
.toggle-btn { padding: 0.5rem 1.5rem; background: rgba(255, 255, 255, 0.1); border: 2px solid rgba(255, 255, 255, 0.2); border-radius: 4px; color: #a0a0a0; cursor: pointer; transition: all 0.3s; }
.toggle-btn.active { background: rgba(233, 69, 96, 0.3); border-color: #e94560; color: #ffffff; }
.toggle-btn:hover { border-color: #e94560; }

.select-container { display: flex; }
.select-input { padding: 0.5rem 1rem; background: rgba(255, 255, 255, 0.1); border: 2px solid rgba(255, 255, 255, 0.2); border-radius: 4px; color: #ffffff; font-size: 1rem; cursor: pointer; min-width: 150px; }
.select-input:focus { outline: none; border-color: #e94560; }
.select-input option { background: #1a1a2e; color: #ffffff; }

.action-buttons { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 2rem; padding-top: 1.5rem; border-top: 2px solid rgba(255, 255, 255, 0.1); }
.action-btn { flex: 1; min-width: 120px; padding: 0.75rem 1rem; border: 2px solid; border-radius: 4px; font-size: 0.95rem; cursor: pointer; transition: all 0.3s; }
.action-btn.reset { background: rgba(100, 100, 100, 0.2); border-color: #666; color: #a0a0a0; }
.action-btn.reset:hover { background: #666; color: #ffffff; }
.action-btn.reset-all { background: rgba(239, 68, 68, 0.2); border-color: #ef4444; color: #ef4444; }
.action-btn.reset-all:hover { background: #ef4444; color: #ffffff; }
.action-btn.save { background: rgba(74, 222, 128, 0.2); border-color: #4ade80; color: #4ade80; }
.action-btn.save:hover:not(:disabled) { background: #4ade80; color: #1a1a2e; }
.action-btn.save:disabled { opacity: 0.5; cursor: not-allowed; }
.action-btn.back { background: rgba(233, 69, 96, 0.2); border-color: #e94560; color: #ffffff; }
.action-btn.back:hover { background: #e94560; }

@media (max-width: 500px) {
  .settings-container { padding: 1.5rem; }
  .tab-nav { flex-wrap: wrap; }
  .tab-btn { flex: 1 1 45%; }
  .action-buttons { flex-direction: column; }
  .action-btn { width: 100%; }
}
</style>
