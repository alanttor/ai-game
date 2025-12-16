<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore, useGameStore } from '@/stores'
import { gameApi } from '@/api/game'

/**
 * MainMenu Component - Main game menu with navigation options
 * Requirements: 9.2 - Display pause menu with resume, save, settings, and quit options
 */

const router = useRouter()
const authStore = useAuthStore()
const gameStore = useGameStore()

// Menu state
const isLoadingSaves = ref(false)
const showSettings = ref(false)
const showLoadGame = ref(false)
const loadError = ref<string | null>(null)

// Settings state
const settings = ref({
  mouseSensitivity: 50,
  masterVolume: 80,
  musicVolume: 70,
  sfxVolume: 90,
})

// Computed
const hasSaves = computed(() => gameStore.saves.length > 0)
const isAuthenticated = computed(() => authStore.isAuthenticated)

// Load saves on mount if authenticated
onMounted(async () => {
  if (isAuthenticated.value) {
    await loadSavesList()
  }
})

// Load saves list from backend
async function loadSavesList() {
  if (!isAuthenticated.value) return
  
  isLoadingSaves.value = true
  loadError.value = null
  
  try {
    const saves = await gameApi.listSaves()
    gameStore.setSaves(saves)
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : 'Failed to load saves'
  } finally {
    isLoadingSaves.value = false
  }
}

// Start new game
function startNewGame() {
  gameStore.clearGameState()
  router.push('/game')
}

// Continue game (load most recent save)
async function continueGame() {
  if (!hasSaves.value) return
  
  const mostRecentSave = gameStore.saves[0]
  await loadGame(mostRecentSave.id)
}

// Load specific save
async function loadGame(saveId: number) {
  isLoadingSaves.value = true
  loadError.value = null
  
  try {
    const gameState = await gameApi.loadGame(saveId)
    gameStore.setGameState(gameState)
    gameStore.setCurrentSaveId(saveId)
    router.push('/game')
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : 'Failed to load game'
  } finally {
    isLoadingSaves.value = false
  }
}

// Delete save
async function deleteSave(saveId: number) {
  try {
    await gameApi.deleteSave(saveId)
    gameStore.removeSave(saveId)
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : 'Failed to delete save'
  }
}

// Go to settings page
function goToSettings() {
  router.push('/settings')
}

// Open settings panel (for inline settings - kept for backward compatibility)
function openSettings() {
  showSettings.value = true
}

// Close settings panel
function closeSettings() {
  showSettings.value = false
}

// Save settings
function saveSettings() {
  // Settings would be persisted to localStorage or backend
  localStorage.setItem('gameSettings', JSON.stringify(settings.value))
  showSettings.value = false
}

// Load settings from storage
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

// Open load game panel
function openLoadGame() {
  showLoadGame.value = true
  loadSavesList()
}

// Close load game panel
function closeLoadGame() {
  showLoadGame.value = false
}

// Go to auth page
function goToAuth() {
  router.push('/auth')
}

// Go to leaderboard
function goToLeaderboard() {
  router.push('/leaderboard')
}

// Logout
function logout() {
  authStore.clearAuth()
  gameStore.clearAll()
}

// Format date for display
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
}

// Load settings on mount
onMounted(() => {
  loadSettings()
})
</script>

<template>
  <div class="main-menu">
    <!-- User Info -->
    <div class="user-info" v-if="isAuthenticated">
      <span class="username">欢迎, {{ authStore.currentUser?.username }}</span>
      <button class="logout-btn" @click="logout">退出登录</button>
    </div>

    <!-- Title -->
    <h1 class="title">Zombie World War</h1>
    <p class="subtitle">丧尸世界大战</p>

    <!-- Main Menu Buttons -->
    <div class="menu-buttons" v-if="!showSettings && !showLoadGame">
      <button class="menu-btn primary" @click="startNewGame">
        <span class="btn-icon">🎮</span>
        <span class="btn-text">开始游戏</span>
      </button>
      
      <button 
        class="menu-btn" 
        @click="continueGame"
        :disabled="!hasSaves || !isAuthenticated"
        :class="{ disabled: !hasSaves || !isAuthenticated }"
      >
        <span class="btn-icon">▶️</span>
        <span class="btn-text">继续游戏</span>
      </button>
      
      <button 
        class="menu-btn" 
        @click="openLoadGame"
        :disabled="!isAuthenticated"
        :class="{ disabled: !isAuthenticated }"
      >
        <span class="btn-icon">📂</span>
        <span class="btn-text">加载存档</span>
      </button>
      
      <button class="menu-btn" @click="goToLeaderboard">
        <span class="btn-icon">🏆</span>
        <span class="btn-text">排行榜</span>
      </button>
      
      <button class="menu-btn" @click="goToSettings">
        <span class="btn-icon">⚙️</span>
        <span class="btn-text">设置</span>
      </button>
      
      <button v-if="!isAuthenticated" class="menu-btn auth-btn" @click="goToAuth">
        <span class="btn-icon">👤</span>
        <span class="btn-text">登录 / 注册</span>
      </button>
    </div>

    <!-- Settings Panel -->
    <div class="settings-panel" v-if="showSettings">
      <h2 class="panel-title">游戏设置</h2>
      
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
      
      <div class="panel-buttons">
        <button class="menu-btn" @click="saveSettings">保存</button>
        <button class="menu-btn secondary" @click="closeSettings">返回</button>
      </div>
    </div>

    <!-- Load Game Panel -->
    <div class="load-panel" v-if="showLoadGame">
      <h2 class="panel-title">加载存档</h2>
      
      <div v-if="loadError" class="error-message">
        {{ loadError }}
      </div>
      
      <div v-if="isLoadingSaves" class="loading">
        加载中...
      </div>
      
      <div v-else-if="!hasSaves" class="no-saves">
        暂无存档
      </div>
      
      <div v-else class="saves-list">
        <div 
          v-for="save in gameStore.saves" 
          :key="save.id" 
          class="save-item"
        >
          <div class="save-info">
            <div class="save-wave">波次 {{ save.waveReached }}</div>
            <div class="save-score">分数: {{ save.score.toLocaleString() }}</div>
            <div class="save-date">{{ formatDate(save.savedAt) }}</div>
          </div>
          <div class="save-actions">
            <button class="action-btn load" @click="loadGame(save.id)">加载</button>
            <button class="action-btn delete" @click="deleteSave(save.id)">删除</button>
          </div>
        </div>
      </div>
      
      <div class="panel-buttons">
        <button class="menu-btn secondary" @click="closeLoadGame">返回</button>
      </div>
    </div>
  </div>
</template>


<style scoped>
.main-menu {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 2rem;
  position: relative;
}

/* User Info */
.user-info {
  position: absolute;
  top: 2rem;
  right: 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.username {
  color: #a0a0a0;
  font-size: 0.95rem;
}

.logout-btn {
  padding: 0.5rem 1rem;
  background: rgba(233, 69, 96, 0.2);
  border: 1px solid #e94560;
  border-radius: 4px;
  color: #ffffff;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s;
}

.logout-btn:hover {
  background: #e94560;
}

/* Title */
.title {
  font-size: 4rem;
  color: #e94560;
  text-shadow: 0 0 20px rgba(233, 69, 96, 0.5);
  margin-bottom: 0.5rem;
  text-align: center;
}

.subtitle {
  font-size: 1.5rem;
  color: #a0a0a0;
  margin-bottom: 3rem;
}

/* Menu Buttons */
.menu-buttons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 300px;
}

.menu-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  background: rgba(233, 69, 96, 0.2);
  border: 2px solid #e94560;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 4px;
}

.menu-btn:hover:not(.disabled) {
  background: #e94560;
  transform: scale(1.02);
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

.menu-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.menu-btn.auth-btn {
  margin-top: 1rem;
  background: rgba(100, 200, 100, 0.2);
  border-color: #64c864;
}

.menu-btn.auth-btn:hover {
  background: #64c864;
}

.btn-icon {
  font-size: 1.25rem;
}

.btn-text {
  flex: 1;
  text-align: left;
}

/* Settings Panel */
.settings-panel,
.load-panel {
  background: rgba(0, 0, 0, 0.6);
  border: 2px solid rgba(233, 69, 96, 0.5);
  border-radius: 12px;
  padding: 2rem;
  min-width: 400px;
  max-width: 500px;
}

.panel-title {
  color: #e94560;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  text-align: center;
}

.setting-item {
  margin-bottom: 1.5rem;
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

.panel-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.panel-buttons .menu-btn {
  flex: 1;
}

/* Load Panel */
.error-message {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid #ef4444;
  border-radius: 4px;
  padding: 0.75rem;
  color: #ef4444;
  margin-bottom: 1rem;
  text-align: center;
}

.loading,
.no-saves {
  color: #a0a0a0;
  text-align: center;
  padding: 2rem;
}

.saves-list {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 1rem;
}

.save-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 0.75rem;
  transition: background 0.2s;
}

.save-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.save-info {
  flex: 1;
}

.save-wave {
  color: #e94560;
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.save-score {
  color: #fbbf24;
  font-size: 0.9rem;
}

.save-date {
  color: #666;
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

.save-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.action-btn.load {
  background: #e94560;
  color: #ffffff;
}

.action-btn.load:hover {
  background: #d63850;
}

.action-btn.delete {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid #ef4444;
}

.action-btn.delete:hover {
  background: #ef4444;
  color: #ffffff;
}

/* Scrollbar styling */
.saves-list::-webkit-scrollbar {
  width: 8px;
}

.saves-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.saves-list::-webkit-scrollbar-thumb {
  background: rgba(233, 69, 96, 0.5);
  border-radius: 4px;
}

.saves-list::-webkit-scrollbar-thumb:hover {
  background: #e94560;
}

/* Responsive */
@media (max-width: 600px) {
  .title {
    font-size: 2.5rem;
  }
  
  .subtitle {
    font-size: 1.1rem;
  }
  
  .menu-buttons {
    min-width: 100%;
  }
  
  .settings-panel,
  .load-panel {
    min-width: 100%;
    padding: 1.5rem;
  }
  
  .user-info {
    position: static;
    margin-bottom: 2rem;
  }
}
</style>
