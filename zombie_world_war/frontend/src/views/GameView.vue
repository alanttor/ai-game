<script setup lang="ts">
import { onMounted, onUnmounted, ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { GameEngine } from '@engine/GameEngine'
import { GameController, GameControllerEvent } from '@engine/GameController'
import { GameEvent } from '@engine/types'
import { useAuthStore, useGameStore } from '@/stores'
import { gameApi } from '@/api/game'
import { leaderboardApi } from '@/api/leaderboard'
import GameHUD from '@/components/GameHUD.vue'
import DamageOverlay from '@/components/DamageOverlay.vue'
import PauseMenu from '@/components/PauseMenu.vue'
import PerformanceStats from '@/components/PerformanceStats.vue'
import type { PerformanceMetrics } from '@engine/performance/PerformanceMonitor'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const gameStore = useGameStore()

const gameContainer = ref<HTMLDivElement | null>(null)
let gameEngine: GameEngine | null = null
let gameController: GameController | null = null

// Game state
const isPaused = ref(false)
const isGameOver = ref(false)
const isLoading = ref(true)
const loadError = ref<string | null>(null)

// Performance stats
const showPerformanceStats = ref(false)
const performanceMetrics = ref<PerformanceMetrics | null>(null)

// Game over state
const gameOverData = reactive({
  score: 0,
  waveReached: 0,
  zombiesKilled: 0,
  playTime: 0,
  isTopTen: false,
})

// HUD state - reactive object for all HUD data
const hudState = reactive({
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
  isPreparationPhase: true,
  preparationTimeLeft: 30,
  score: 0,
  lastDamage: 0,
  damageTimestamp: 0,
})

// Computed
const isAuthenticated = computed(() => authStore.isAuthenticated)


// Update HUD from game controller
function updateHUDFromController() {
  if (!gameController) return
  const state = gameController.getHUDState()
  Object.assign(hudState, state)
  
  // Update performance metrics
  if (showPerformanceStats.value) {
    performanceMetrics.value = gameController.getPerformanceMetrics()
  }
}

// Toggle performance stats display (F3 key)
function handleKeyDown(event: KeyboardEvent) {
  if (event.code === 'F3') {
    event.preventDefault()
    showPerformanceStats.value = !showPerformanceStats.value
  }
}

// Handle state changed event
function onStateChanged(data: unknown) {
  const state = data as typeof hudState
  Object.assign(hudState, state)
}

// Handle player damage event
function onPlayerDamaged(data: unknown) {
  const damageData = data as { damage: number }
  hudState.lastDamage = damageData.damage
  hudState.damageTimestamp = Date.now()
}

// Handle game over event
async function onGameOver(data: unknown) {
  const overData = data as {
    finalScore: number
    waveReached: number
    totalZombiesKilled: number
    playTime: number
  }
  
  isGameOver.value = true
  gameOverData.score = overData.finalScore
  gameOverData.waveReached = overData.waveReached
  gameOverData.zombiesKilled = overData.totalZombiesKilled
  gameOverData.playTime = overData.playTime
  
  // Submit score to leaderboard if authenticated
  if (isAuthenticated.value) {
    try {
      const response = await leaderboardApi.submitScore({
        score: overData.finalScore,
        waveReached: overData.waveReached,
        zombiesKilled: overData.totalZombiesKilled,
        playTimeSeconds: Math.floor(overData.playTime),
      })
      gameOverData.isTopTen = response.isTopTen
    } catch (error) {
      console.error('Failed to submit score:', error)
    }
  }
}

// Handle game pause event
function onGamePause() {
  isPaused.value = true
}

// Handle game resume event
function onGameResume() {
  isPaused.value = false
}


// Resume game from pause menu
function resumeGame() {
  if (gameController) {
    gameController.resume()
  }
}

// Save game from pause menu
async function saveGame() {
  if (!gameController || !isAuthenticated.value) return
  
  try {
    const state = gameController.getGameState()
    const response = await gameApi.saveGame(state)
    gameStore.setCurrentSaveId(response.saveId)
    gameStore.updateLastSaveTime()
    return { success: true, message: '游戏已保存!' }
  } catch (error) {
    const message = error instanceof Error ? error.message : '保存失败'
    return { success: false, message }
  }
}

// Quit game from pause menu
function quitGame() {
  if (gameController) {
    gameController.stop()
  }
  if (gameEngine) {
    gameEngine.stop()
  }
  router.push('/')
}

// Handle settings changed from pause menu
function onSettingsChanged(settings: { mouseSensitivity: number; masterVolume?: number; musicVolume?: number; sfxVolume?: number }) {
  if (gameController) {
    gameController.applyConfig(settings)
  }
}

// Get current game state for pause menu
function getCurrentGameState() {
  return gameController?.getGameState() ?? null
}

// Restart game after game over
function restartGame() {
  isGameOver.value = false
  if (gameController) {
    gameController.startNewGame()
  }
}

// Return to main menu after game over
function returnToMenu() {
  quitGame()
}


// Initialize game
async function initGame() {
  if (!gameContainer.value) {
    loadError.value = '游戏容器未找到'
    isLoading.value = false
    return
  }
  
  isLoading.value = true
  loadError.value = null
  
  try {
    console.log('[GameView] 开始初始化游戏引擎...')
    
    // Create game engine
    gameEngine = new GameEngine(gameContainer.value)
    console.log('[GameView] GameEngine 创建成功，开始初始化...')
    
    await gameEngine.init()
    console.log('[GameView] GameEngine 初始化完成')
    
    // Create game controller
    console.log('[GameView] 开始创建 GameController...')
    gameController = new GameController(
      gameEngine.getSceneManager(),
      gameEngine.getInputManager()
    )
    console.log('[GameView] GameController 创建成功，开始初始化...')
    
    await gameController.init()
    console.log('[GameView] GameController 初始化完成')
    
    // Subscribe to game controller events
    gameController.on(GameControllerEvent.STATE_CHANGED, onStateChanged)
    gameController.on(GameControllerEvent.PLAYER_DAMAGED, onPlayerDamaged)
    gameController.on(GameControllerEvent.GAME_OVER, onGameOver)
    gameController.on(GameEvent.GAME_PAUSE, onGamePause)
    gameController.on(GameEvent.GAME_RESUME, onGameResume)
    
    // Check if we're loading a saved game
    const savedState = gameStore.gameState
    if (savedState) {
      gameController.loadGame(savedState)
      gameStore.clearGameState() // Clear after loading
    } else {
      gameController.startNewGame()
    }
    
    // Start the game engine loop
    console.log('[GameView] 启动游戏引擎循环...')
    gameEngine.start()
    
    // Setup game loop integration
    setupGameLoop()
    
    console.log('[GameView] 游戏初始化完成!')
    isLoading.value = false
  } catch (error) {
    console.error('[GameView] 游戏初始化失败:', error)
    loadError.value = error instanceof Error ? error.message : '游戏加载失败'
    isLoading.value = false
  }
}

// Setup game loop to integrate controller with engine
function setupGameLoop() {
  if (!gameEngine || !gameController) return
  
  // Override the engine's fixedUpdate to use our controller
  const originalFixedUpdate = gameEngine['fixedUpdate'].bind(gameEngine)
  gameEngine['fixedUpdate'] = (deltaTime: number) => {
    originalFixedUpdate(deltaTime)
    if (gameController && !isPaused.value && !isGameOver.value) {
      gameController.processInput(deltaTime)
      gameController.update(deltaTime)
      updateHUDFromController()
    }
  }
}


// Format play time for display
function formatPlayTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

onMounted(async () => {
  // Add keyboard listener for performance stats toggle
  window.addEventListener('keydown', handleKeyDown)
  await initGame()
})

onUnmounted(() => {
  // Remove keyboard listener
  window.removeEventListener('keydown', handleKeyDown)
  
  if (gameController) {
    gameController.off(GameControllerEvent.STATE_CHANGED, onStateChanged)
    gameController.off(GameControllerEvent.PLAYER_DAMAGED, onPlayerDamaged)
    gameController.off(GameControllerEvent.GAME_OVER, onGameOver)
    gameController.off(GameEvent.GAME_PAUSE, onGamePause)
    gameController.off(GameEvent.GAME_RESUME, onGameResume)
    gameController.dispose()
    gameController = null
  }
  
  if (gameEngine) {
    gameEngine.stop()
    gameEngine = null
  }
})
</script>

<template>
  <div class="game-view">
    <!-- Game Container - 始终存在，用于 Three.js 渲染 -->
    <div ref="gameContainer" class="game-container"></div>
    
    <!-- Loading Screen - 覆盖在游戏容器上 -->
    <div v-if="isLoading" class="loading-screen">
      <div class="loading-content">
        <h2>加载中...</h2>
        <div class="loading-spinner"></div>
      </div>
    </div>
    
    <!-- Error Screen -->
    <div v-else-if="loadError" class="error-screen">
      <div class="error-content">
        <h2>加载失败</h2>
        <p>{{ loadError }}</p>
        <button class="menu-btn" @click="router.push('/')">返回主菜单</button>
      </div>
    </div>
    
    <!-- Game UI Overlays - 只在游戏运行时显示 -->
    <template v-else>
      <!-- Game HUD Overlay -->
      <GameHUD
        :health="hudState.health"
        :max-health="hudState.maxHealth"
        :stamina="hudState.stamina"
        :max-stamina="hudState.maxStamina"
        :current-weapon-name="hudState.currentWeaponName"
        :current-weapon-slot="hudState.currentWeaponSlot"
        :current-ammo="hudState.currentAmmo"
        :reserve-ammo="hudState.reserveAmmo"
        :magazine-size="hudState.magazineSize"
        :is-reloading="hudState.isReloading"
        :current-wave="hudState.currentWave"
        :zombies-killed="hudState.zombiesKilled"
        :total-zombies-in-wave="hudState.totalZombiesInWave"
        :is-preparation-phase="hudState.isPreparationPhase"
        :preparation-time-left="hudState.preparationTimeLeft"
        :score="hudState.score"
      />

      
      <!-- Damage and Low Health Overlay -->
      <DamageOverlay
        :health="hudState.health"
        :max-health="hudState.maxHealth"
        :last-damage="hudState.lastDamage"
        :damage-timestamp="hudState.damageTimestamp"
      />
      
      <!-- Performance Stats (F3 to toggle) -->
      <PerformanceStats
        :metrics="performanceMetrics"
        :visible="showPerformanceStats"
      />
      
      <!-- Pause Menu -->
      <PauseMenu
        v-if="isPaused && !isGameOver"
        :game-state="getCurrentGameState()"
        @resume="resumeGame"
        @quit="quitGame"
        @settings-changed="onSettingsChanged"
      />
      
      <!-- Game Over Screen -->
      <div v-if="isGameOver" class="game-over-overlay">
        <div class="game-over-content">
          <h1 class="game-over-title">游戏结束</h1>
          
          <div v-if="gameOverData.isTopTen" class="top-ten-badge">
            🏆 进入前10名!
          </div>
          
          <div class="game-over-stats">
            <div class="stat-item">
              <span class="stat-label">最终分数</span>
              <span class="stat-value score">{{ gameOverData.score.toLocaleString() }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">到达波次</span>
              <span class="stat-value">{{ gameOverData.waveReached }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">击杀丧尸</span>
              <span class="stat-value">{{ gameOverData.zombiesKilled }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">游戏时间</span>
              <span class="stat-value">{{ formatPlayTime(gameOverData.playTime) }}</span>
            </div>
          </div>
          
          <div class="game-over-buttons">
            <button class="menu-btn primary" @click="restartGame">再来一局</button>
            <button class="menu-btn" @click="router.push('/leaderboard')">查看排行榜</button>
            <button class="menu-btn secondary" @click="returnToMenu">返回主菜单</button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>


<style scoped>
.game-view {
  width: 100%;
  height: 100%;
  position: relative;
}

.game-container {
  width: 100%;
  height: 100%;
}

/* Loading Screen */
.loading-screen,
.error-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-content,
.error-content {
  text-align: center;
  color: #ffffff;
}

.loading-content h2,
.error-content h2 {
  font-size: 2rem;
  color: #e94560;
  margin-bottom: 1.5rem;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(233, 69, 96, 0.3);
  border-top-color: #e94560;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-content p {
  color: #a0a0a0;
  margin-bottom: 1.5rem;
}

/* Game Over Screen */
.game-over-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}


.game-over-content {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border: 2px solid rgba(233, 69, 96, 0.5);
  border-radius: 16px;
  padding: 2.5rem;
  text-align: center;
  min-width: 400px;
  box-shadow: 0 0 40px rgba(233, 69, 96, 0.3);
}

.game-over-title {
  font-size: 3rem;
  color: #e94560;
  text-shadow: 0 0 20px rgba(233, 69, 96, 0.5);
  margin-bottom: 1rem;
}

.top-ten-badge {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: #1a1a2e;
  padding: 0.5rem 1.5rem;
  border-radius: 20px;
  font-weight: bold;
  font-size: 1.1rem;
  display: inline-block;
  margin-bottom: 1.5rem;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.game-over-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-item {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 1rem;
}

.stat-label {
  display: block;
  color: #a0a0a0;
  font-size: 0.85rem;
  margin-bottom: 0.25rem;
}

.stat-value {
  display: block;
  color: #ffffff;
  font-size: 1.5rem;
  font-weight: bold;
}

.stat-value.score {
  color: #fbbf24;
  font-size: 2rem;
}


.game-over-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* Menu Buttons */
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
  border-radius: 8px;
}

.menu-btn:hover {
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

/* Responsive */
@media (max-width: 500px) {
  .game-over-content {
    min-width: 90%;
    padding: 1.5rem;
  }
  
  .game-over-title {
    font-size: 2rem;
  }
  
  .game-over-stats {
    grid-template-columns: 1fr;
  }
}
</style>
