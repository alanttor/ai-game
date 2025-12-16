<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { leaderboardApi, type LeaderboardEntry, type PageResponse } from '@/api'
import { useAuthStore } from '@/stores'

const router = useRouter()
const authStore = useAuthStore()

// State
const leaderboardData = ref<PageResponse<LeaderboardEntry> | null>(null)
const currentPage = ref(0)
const pageSize = ref(20)
const loading = ref(false)
const error = ref<string | null>(null)

// Computed
const entries = computed(() => leaderboardData.value?.content || [])
const totalPages = computed(() => leaderboardData.value?.totalPages || 0)
const isFirstPage = computed(() => leaderboardData.value?.first ?? true)
const isLastPage = computed(() => leaderboardData.value?.last ?? true)

/**
 * Check if entry is in Top 10
 * Requirements: 7.3
 */
const isTopTen = (entry: LeaderboardEntry): boolean => {
  return entry.rank <= 10
}

/**
 * Format play time from seconds to readable format
 */
const formatPlayTime = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`
  }
  return `${secs}s`
}

/**
 * Format date to readable format
 */
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}


/**
 * Fetch leaderboard data
 * Requirements: 7.2, 11.3
 */
const fetchLeaderboard = async () => {
  loading.value = true
  error.value = null
  
  try {
    leaderboardData.value = await leaderboardApi.getTopScores(currentPage.value, pageSize.value)
  } catch (err: any) {
    error.value = err.response?.data?.message || '加载排行榜失败'
    console.error('Failed to fetch leaderboard:', err)
  } finally {
    loading.value = false
  }
}

/**
 * Go to previous page
 */
const prevPage = () => {
  if (!isFirstPage.value) {
    currentPage.value--
    fetchLeaderboard()
  }
}

/**
 * Go to next page
 */
const nextPage = () => {
  if (!isLastPage.value) {
    currentPage.value++
    fetchLeaderboard()
  }
}

/**
 * Go to specific page
 */
const goToPage = (page: number) => {
  if (page >= 0 && page < totalPages.value) {
    currentPage.value = page
    fetchLeaderboard()
  }
}

/**
 * Go back to home
 */
const goBack = () => {
  router.push('/')
}

// Fetch data on mount
onMounted(() => {
  fetchLeaderboard()
})
</script>

<template>
  <div class="leaderboard-view">
    <div class="header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h1 class="title">🏆 排行榜</h1>
      <div class="spacer"></div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="fetchLeaderboard">重试</button>
    </div>

    <!-- Leaderboard Table -->
    <div v-else class="leaderboard-container">
      <table class="leaderboard-table">
        <thead>
          <tr>
            <th class="rank-col">排名</th>
            <th class="name-col">玩家</th>
            <th class="score-col">分数</th>
            <th class="wave-col">波次</th>
            <th class="kills-col">击杀</th>
            <th class="time-col">游戏时长</th>
            <th class="date-col">达成时间</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="entry in entries" 
            :key="entry.id"
            :class="{ 
              'top-ten': isTopTen(entry),
              'top-three': entry.rank <= 3,
              'current-user': authStore.currentUser?.id === entry.userId
            }"
          >
            <td class="rank-col">
              <span class="rank-badge" :class="`rank-${entry.rank}`">
                <template v-if="entry.rank === 1">🥇</template>
                <template v-else-if="entry.rank === 2">🥈</template>
                <template v-else-if="entry.rank === 3">🥉</template>
                <template v-else>#{{ entry.rank }}</template>
              </span>
            </td>
            <td class="name-col">{{ entry.playerName }}</td>
            <td class="score-col">{{ entry.score.toLocaleString() }}</td>
            <td class="wave-col">{{ entry.waveReached }}</td>
            <td class="kills-col">{{ entry.zombiesKilled }}</td>
            <td class="time-col">{{ formatPlayTime(entry.playTimeSeconds) }}</td>
            <td class="date-col">{{ formatDate(entry.achievedAt) }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="entries.length === 0" class="empty-state">
        <p>暂无排行榜数据</p>
        <p class="hint">成为第一个上榜的玩家吧！</p>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          class="page-btn" 
          :disabled="isFirstPage"
          @click="prevPage"
        >
          ← 上一页
        </button>
        
        <div class="page-numbers">
          <button
            v-for="page in Math.min(totalPages, 5)"
            :key="page - 1"
            class="page-num"
            :class="{ active: currentPage === page - 1 }"
            @click="goToPage(page - 1)"
          >
            {{ page }}
          </button>
          <span v-if="totalPages > 5" class="ellipsis">...</span>
        </div>
        
        <button 
          class="page-btn" 
          :disabled="isLastPage"
          @click="nextPage"
        >
          下一页 →
        </button>
      </div>

      <!-- Page Info -->
      <div class="page-info">
        第 {{ currentPage + 1 }} / {{ totalPages }} 页
      </div>
    </div>
  </div>
</template>


<style scoped>
.leaderboard-view {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 2rem;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
}

.back-btn {
  padding: 0.75rem 1.5rem;
  background: rgba(233, 69, 96, 0.2);
  border: 2px solid #e94560;
  color: #ffffff;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: #e94560;
}

.title {
  font-size: 2.5rem;
  color: #ffd700;
  text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
  margin: 0;
}

.spacer {
  width: 120px;
}

/* Loading State */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: #a0a0a0;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(233, 69, 96, 0.3);
  border-top-color: #e94560;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error State */
.error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: #e94560;
}

.retry-btn {
  margin-top: 1rem;
  padding: 0.75rem 2rem;
  background: rgba(233, 69, 96, 0.2);
  border: 2px solid #e94560;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: #e94560;
}

/* Leaderboard Container */
.leaderboard-container {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* Table Styles */
.leaderboard-table {
  width: 100%;
  border-collapse: collapse;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  overflow: hidden;
}

.leaderboard-table th,
.leaderboard-table td {
  padding: 1rem;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.leaderboard-table th {
  background: rgba(233, 69, 96, 0.3);
  color: #ffffff;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
}

.leaderboard-table tbody tr {
  transition: background 0.3s ease;
}

.leaderboard-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.05);
}

/* Top 10 Highlight - Requirements: 7.3 */
.leaderboard-table tbody tr.top-ten {
  background: rgba(255, 215, 0, 0.1);
}

.leaderboard-table tbody tr.top-ten:hover {
  background: rgba(255, 215, 0, 0.15);
}

/* Top 3 Special Styling */
.leaderboard-table tbody tr.top-three {
  background: rgba(255, 215, 0, 0.2);
  font-weight: 600;
}

.leaderboard-table tbody tr.top-three:hover {
  background: rgba(255, 215, 0, 0.25);
}

/* Current User Highlight */
.leaderboard-table tbody tr.current-user {
  background: rgba(100, 200, 100, 0.2);
  border-left: 3px solid #64c864;
}

/* Column Widths */
.rank-col { width: 80px; }
.name-col { width: 150px; text-align: left !important; }
.score-col { width: 120px; color: #ffd700; font-weight: 600; }
.wave-col { width: 80px; }
.kills-col { width: 80px; }
.time-col { width: 120px; }
.date-col { width: 150px; font-size: 0.9rem; color: #a0a0a0; }

/* Rank Badge */
.rank-badge {
  display: inline-block;
  min-width: 40px;
  font-size: 1.2rem;
}

.rank-badge.rank-1,
.rank-badge.rank-2,
.rank-badge.rank-3 {
  font-size: 1.5rem;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: #a0a0a0;
}

.empty-state .hint {
  font-size: 0.9rem;
  margin-top: 0.5rem;
  color: #666;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
}

.page-btn {
  padding: 0.75rem 1.5rem;
  background: rgba(233, 69, 96, 0.2);
  border: 2px solid #e94560;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background: #e94560;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 0.5rem;
}

.page-num {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-num:hover {
  background: rgba(233, 69, 96, 0.3);
}

.page-num.active {
  background: #e94560;
  border-color: #e94560;
}

.ellipsis {
  display: flex;
  align-items: center;
  color: #a0a0a0;
}

/* Page Info */
.page-info {
  text-align: center;
  margin-top: 1rem;
  color: #a0a0a0;
  font-size: 0.9rem;
}
</style>
