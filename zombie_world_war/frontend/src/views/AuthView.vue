<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import LoginForm from '@/components/LoginForm.vue'
import RegisterForm from '@/components/RegisterForm.vue'

const router = useRouter()
const isLoginMode = ref(true)

const handleSuccess = () => {
  router.push('/')
}

const switchToRegister = () => {
  isLoginMode.value = false
}

const switchToLogin = () => {
  isLoginMode.value = true
}

const goBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="auth-view">
    <button class="back-btn" @click="goBack">← 返回</button>
    
    <div class="auth-container">
      <Transition name="fade" mode="out-in">
        <LoginForm
          v-if="isLoginMode"
          @success="handleSuccess"
          @switch-to-register="switchToRegister"
        />
        <RegisterForm
          v-else
          @success="handleSuccess"
          @switch-to-login="switchToLogin"
        />
      </Transition>
    </div>
  </div>
</template>

<style scoped>
.auth-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.back-btn {
  position: absolute;
  top: 2rem;
  left: 2rem;
  padding: 0.5rem 1rem;
  background: rgba(233, 69, 96, 0.2);
  border: 1px solid #e94560;
  border-radius: 4px;
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s;
}

.back-btn:hover {
  background: #e94560;
}

.auth-container {
  width: 100%;
  max-width: 400px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
