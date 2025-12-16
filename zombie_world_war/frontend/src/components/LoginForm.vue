<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores'
import { authApi } from '@/api/auth'

const emit = defineEmits<{
  (e: 'success'): void
  (e: 'switch-to-register'): void
}>()

const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const showPassword = ref(false)

// Form validation
const usernameError = computed(() => {
  if (!username.value) return ''
  if (username.value.length < 3) return '用户名至少3个字符'
  return ''
})

const passwordError = computed(() => {
  if (!password.value) return ''
  if (password.value.length < 8) return '密码至少8个字符'
  return ''
})

const isFormValid = computed(() => {
  return username.value.length >= 3 && 
         password.value.length >= 8 &&
         !usernameError.value &&
         !passwordError.value
})

const handleSubmit = async () => {
  if (!isFormValid.value) return

  authStore.setLoading(true)
  authStore.setError(null)

  try {
    const response = await authApi.login({
      username: username.value,
      password: password.value,
    })
    authStore.setAuth(response)
    emit('success')
  } catch (error: any) {
    // Requirement 8.3: Error message should not reveal which field is incorrect
    authStore.setError('用户名或密码错误')
  } finally {
    authStore.setLoading(false)
  }
}
</script>

<template>
  <div class="login-form">
    <h2 class="form-title">登录</h2>
    
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="username">用户名</label>
        <input
          id="username"
          v-model="username"
          type="text"
          placeholder="请输入用户名"
          :class="{ 'has-error': usernameError }"
        />
        <span v-if="usernameError" class="error-text">{{ usernameError }}</span>
      </div>

      <div class="form-group">
        <label for="password">密码</label>
        <div class="password-input">
          <input
            id="password"
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="请输入密码"
            :class="{ 'has-error': passwordError }"
          />
          <button
            type="button"
            class="toggle-password"
            @click="showPassword = !showPassword"
          >
            {{ showPassword ? '隐藏' : '显示' }}
          </button>
        </div>
        <span v-if="passwordError" class="error-text">{{ passwordError }}</span>
      </div>

      <div v-if="authStore.error" class="form-error">
        {{ authStore.error }}
      </div>

      <button
        type="submit"
        class="submit-btn"
        :disabled="!isFormValid || authStore.isLoading"
      >
        {{ authStore.isLoading ? '登录中...' : '登录' }}
      </button>
    </form>

    <div class="form-footer">
      <span>还没有账号？</span>
      <button type="button" class="link-btn" @click="emit('switch-to-register')">
        立即注册
      </button>
    </div>
  </div>
</template>

<style scoped>
.login-form {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  background: rgba(26, 26, 46, 0.95);
  border-radius: 8px;
  border: 1px solid rgba(233, 69, 96, 0.3);
}

.form-title {
  text-align: center;
  color: #e94560;
  margin-bottom: 2rem;
  font-size: 1.8rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #a0a0a0;
  font-size: 0.9rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  color: #ffffff;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #e94560;
}

.form-group input.has-error {
  border-color: #ff4444;
}

.password-input {
  position: relative;
  display: flex;
}

.password-input input {
  flex: 1;
  padding-right: 4rem;
}

.toggle-password {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #a0a0a0;
  cursor: pointer;
  font-size: 0.8rem;
}

.toggle-password:hover {
  color: #e94560;
}

.error-text {
  display: block;
  margin-top: 0.25rem;
  color: #ff4444;
  font-size: 0.8rem;
}

.form-error {
  padding: 0.75rem;
  margin-bottom: 1rem;
  background: rgba(255, 68, 68, 0.1);
  border: 1px solid rgba(255, 68, 68, 0.3);
  border-radius: 4px;
  color: #ff4444;
  font-size: 0.9rem;
  text-align: center;
}

.submit-btn {
  width: 100%;
  padding: 1rem;
  background: #e94560;
  border: none;
  border-radius: 4px;
  color: #ffffff;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s, transform 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: #d63850;
  transform: translateY(-2px);
}

.submit-btn:disabled {
  background: #666;
  cursor: not-allowed;
}

.form-footer {
  margin-top: 1.5rem;
  text-align: center;
  color: #a0a0a0;
}

.link-btn {
  background: none;
  border: none;
  color: #e94560;
  cursor: pointer;
  font-size: 1rem;
  text-decoration: underline;
}

.link-btn:hover {
  color: #ff6b7a;
}
</style>
