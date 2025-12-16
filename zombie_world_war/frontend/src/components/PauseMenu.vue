<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore, useGameStore } from '@/stores'
import { gameApi } from '@/api/game'
import type { GameState } from '@engine/types'

/**
 * PauseMenu Component - In-game pause menu with options
 * Requirements: 9.2 - Display pause menu with resume, save, settings, and quit options
 */

// Props
interface Props {
  gameState: GameState | null
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  (e: 'resume'): void
  (e: 'quit'): void
  (e: 'settingsChanged', settings: GameSettings): void
}>()

// Types
interface GameSettings {
  mouseSensitivity: number
  masterVolume: number
  musicVolume: number
  sfxVolume: number
}

const router = useRouter()
const authStore = useAuthStore()
const gameStore = useGameStore()

// Menu state
const currentView = ref<'main' | 'settings' | 'confirm-quit'>('main')
const isSaving = ref(false)
const saveMessage = ref<string | null>(null)
const saveError = ref<string | null>(null)

// Settings state
const settings = ref<GameSettings>({
  mouseSensitivity: 50,
  masterVolume: 80,
  musicVolume: 70,
  sfxVolume: 90,
})

// Computed
const isAuthenticated = computed(() => authStore.isAuthenticated)
const canSave = computed(() => isAuthenticated.value && props.gameState !== null)

// Load settings from localStorage
function loadSettings() {
  const stored = localStorage.getItem('gameSettings')
  if (stored) {
    try {
      const parsed = JSON.parse(stored)
      settings.value = { ...settings.value, ...parsed }
    } catch {
      // Ignore parse errors
    }
  }
}

// Initialize settings
loadSettings()

// Resume game
function resumeGame() {
  emit('resume')
}

// Save game
async function saveGame() {
  if (!canSave.value || !props.gameState) return
  
  isSaving.value = true
  saveMessage.value = null
  saveError.value = null
  
  try {
    const response = await gameApi.saveGame(props.gameState)
    gameStore.setCurrentSaveId(response.saveId)
    gameStore.updateLastSaveTime()
    saveMessage.value = '游戏已保存!'
    
    // Clear message after 2 seconds
    setTimeout(() => {
      saveMessage.value = null
    }, 2000)
  } catch (error) {
    saveError.value = error instanceof Error ? error.message : '保存失败'
  } finally {
    isSaving.value = false
  }
}

// Open settings
function openSettings() {
  currentView.value = 'settings'
}

// Close settings
function closeSettings() {
  currentView.value = 'main'
}

// Save settings
function saveSettings() {
  localStorage.setItem('gameSettings', JSON.stringify(settings.value))
  emit('settingsChanged', settings.value)
  currentView.value = 'main'
}

// Show quit confirmation
function showQuitConfirm() {
  currentView.value = 'confirm-quit'
}

// Cancel quit
function cancelQuit() {
  currentView.value = 'main'
}

// Confirm quit - go to main menu
function confirmQuit() {
  emit('quit')
  router.push('/')
}
</script>

<template>
  <div class="pause-menu-overlay">
    <div class="pause-menu">
      <!-- Main Pause Menu -->
      <div v-if="currentView === 'main'" class="menu-content">
        <h2 class="menu-title">游戏暂停</h2>
        
        <!-- Save status messages -->
        <div v-if="saveMessage" class="save-message success">
          {{ saveMessage }}
        </div>
        <div v-if="saveError" class="save-message error">
          {{ saveError }}
        </div>
        
        <div class="menu-buttons">
          <button class="menu-btn primary" @click="resumeGame">
            <span class="btn-icon">▶️</span>
            <span class="btn-text">继续游戏</span>
          </button>
          
          <button 
            class="menu-btn" 
            @click="saveGame"
            :disabled="!canSave || isSaving"
            :class="{ disabled: !canSave || isSaving }"
          >
            <span class="btn-icon">💾</span>
            <span class="btn-text">{{ isSaving ? '保存中...' : '保存游戏' }}</span>
          </button>
          
          <button class="menu-btn" @click="openSettings">
            <span class="btn-icon">⚙️</span>
            <span class="btn-text">设置</span>
          </button>
          
          <button class="menu-btn danger" @click="showQuitConfirm">
            <span class="btn-icon">🚪</span>
            <span class="btn-text">退出游戏</span>
          </button>
        </div>
        
        <p v-if="!isAuthenticated" class="login-hint">
          登录后可保存游戏进度
        </p>
      </div>

      <!-- Settings View -->
      <div v-if="currentView === 'settings'" class="menu-content settings-view">
        <h2 class="menu-title">游戏设置</h2>
        
        <div class="settings-list">
          <div class="setting-item">
            <label>鼠标灵敏度</label>
            <div class="slider-container">
              <input 
                type="range" 
                v-model.number="settings.mouseSensitivity" 
                min="1" 
                max="100"
                class="slider"
              />
              <span class="slider-value">{{ settings.mouseSensitivity }}</span>
            </div>
          </div>
          
          <div class="setting-item">
            <label>主音量</label>
            <div class="slider-container">
              <input 
                type="range" 
                v-model.number="settings.masterVolume" 
                min="0" 
                max="100"
                class="slider"
              />
              <span class="slider-value">{{ settings.masterVolume }}%</span>
            </div>
          </div>
          
          <div class="setting-item">
            <label>音乐音量</label>
            <div class="slider-container">
              <input 
                type="range" 
                v-model.number="settings.musicVolume" 
                min="0" 
                max="100"
                class="slider"
              />
              <span class="slider-value">{{ settings.musicVolume }}%</span>
            </div>
          </div>
          
          <div class="setting-item">
            <label>音效音量</label>
            <div class="slider-container">
              <input 
                type="range" 
                v-model.number="settings.sfxVolume" 
                min="0" 
                max="100"
                class="slider"
              />
              <span class="slider-value">{{ settings.sfxVolume }}%</span>
            </div>
          </div>
        </div>
        
        <div class="menu-buttons horizontal">
          <button class="menu-btn" @click="saveSettings">保存</button>
          <button class="menu-btn secondary" @click="closeSettings">返回</button>
        </div>
      </div>

      <!-- Quit Confirmation -->
      <div v-if="currentView === 'confirm-quit'" class="menu-content confirm-view">
        <h2 class="menu-title">确认退出</h2>
        <p class="confirm-text">确定要退出游戏吗？未保存的进度将会丢失。</p>
        
        <div class="menu-buttons horizontal">
          <button class="menu-btn danger" @click="confirmQuit">确认退出</button>
          <button class="menu-btn secondary" @click="cancelQuit">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>


<style scoped>
.pause-menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.pause-menu {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border: 2px solid rgba(233, 69, 96, 0.5);
  border-radius: 16px;
  padding: 2rem;
  min-width: 350px;
  max-width: 450px;
  box-shadow: 0 0 40px rgba(233, 69, 96, 0.3);
}

.menu-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.menu-title {
  color: #e94560;
  font-size: 2rem;
  margin-bottom: 1.5rem;
  text-shadow: 0 0 10px rgba(233, 69, 96, 0.5);
  text-align: center;
}

/* Save Messages */
.save-message {
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  text-align: center;
  width: 100%;
}

.save-message.success {
  background: rgba(74, 222, 128, 0.2);
  border: 1px solid #4ade80;
  color: #4ade80;
}

.save-message.error {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid #ef4444;
  color: #ef4444;
}

/* Menu Buttons */
.menu-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: 100%;
}

.menu-buttons.horizontal {
  flex-direction: row;
  gap: 1rem;
}

.menu-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  font-size: 1rem;
  background: rgba(233, 69, 96, 0.2);
  border: 2px solid #e94560;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 8px;
  flex: 1;
}

.menu-btn:hover:not(.disabled) {
  background: #e94560;
  transform: translateY(-2px);
}

.menu-btn.primary {
  background: rgba(233, 69, 96, 0.4);
  font-weight: bold;
}

.menu-btn.secondary {
  background: rgba(100, 100, 100, 0.2);
  border-color: #666;
}

.menu-btn.secondary:hover {
  background: #666;
}

.menu-btn.danger {
  background: rgba(239, 68, 68, 0.2);
  border-color: #ef4444;
}

.menu-btn.danger:hover {
  background: #ef4444;
}

.menu-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 1.25rem;
}

.btn-text {
  flex: 1;
  text-align: left;
}

.menu-buttons.horizontal .btn-text {
  text-align: center;
}

/* Login Hint */
.login-hint {
  color: #666;
  font-size: 0.85rem;
  margin-top: 1rem;
  text-align: center;
}

/* Settings View */
.settings-view {
  width: 100%;
}

.settings-list {
  width: 100%;
  margin-bottom: 1.5rem;
}

.setting-item {
  margin-bottom: 1.25rem;
}

.setting-item label {
  display: block;
  color: #a0a0a0;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.slider {
  flex: 1;
  height: 8px;
  -webkit-appearance: none;
  appearance: none;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  outline: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  background: #e94560;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s;
}

.slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

.slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  background: #e94560;
  border-radius: 50%;
  cursor: pointer;
  border: none;
}

.slider-value {
  color: #ffffff;
  font-size: 0.9rem;
  min-width: 50px;
  text-align: right;
}

/* Confirm View */
.confirm-view {
  text-align: center;
}

.confirm-text {
  color: #a0a0a0;
  font-size: 1rem;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

/* Responsive */
@media (max-width: 500px) {
  .pause-menu {
    min-width: 90%;
    padding: 1.5rem;
  }
  
  .menu-title {
    font-size: 1.5rem;
  }
  
  .menu-buttons.horizontal {
    flex-direction: column;
  }
}
</style>
