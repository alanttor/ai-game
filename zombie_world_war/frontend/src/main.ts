import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

// Create Pinia store
const pinia = createPinia()

// Create Vue Router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('./views/HomeView.vue'),
    },
    {
      path: '/game',
      name: 'game',
      component: () => import('./views/GameView.vue'),
    },
    {
      path: '/auth',
      name: 'auth',
      component: () => import('./views/AuthView.vue'),
    },
    {
      path: '/leaderboard',
      name: 'leaderboard',
      component: () => import('./views/LeaderboardView.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('./views/SettingsView.vue'),
    },
  ],
})

// Create and mount app
const app = createApp(App)
app.use(pinia)
app.use(router)
app.mount('#app')
