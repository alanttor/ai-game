<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores'
import { authApi } from '@/api/auth'

const emit = defineEmits<{
  (e: 'success'): void
  (e: 'switch-to-login'): void
}>()

const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)

// Email validation regex
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

// Form validation - Requirement 8.1: validate email format and password strength
const usernameError = computed(() => {
  if (!username.value) return ''
  if (username.value.length < 3) return '用户名至少3个字符'
  if (username.value.length > 50) return '用户名最多50个字符'
  return ''
})

const emailError = computed(() => {
  if (!email.value) return ''
  if (!emailRegex.test(email.value)) return '请输入有效的邮箱地址'
  return ''
})

const passwordError = computed(() => {
  if (!password.value) return ''
  if (password.value.length < 8) return '密码至少8个字符'
  return ''
})

const confirmPasswordError = computed(() => {
  if (!confirmPassword.value) return ''
  if (confirmPassword.value !== password.value) return '两次输入的密码不一致'
  return ''
})

const isFormValid = computed(() => {
  return username.value.length >= 3 &&
         emailRegex.test(email.value) &&
         password.value.length >= 8 &&
         confirmPassword.value === password.value &&
         !usernameError.value &&
         !emailError.value &&
         !passwordError.value &&
         !confirmPasswordError.value
})

const handleSubmit = async () => {
  if (!isFormValid.value) return

  authStore.setLoading(true)
  authStore.setError(null)

  try {
    const response = await authApi.register({
      username: username.value,
      email: email.value,
      password: password.value,
    })
    authStore.setAuth(response)
    emit('success')
  } catch (error: any) {
    const message = error.response?.data?.message || '注册失败，请稍后重试'
    authStore.setError(message)
  } finally {
    authStore.setLoading(false)
  }
}
</script>

<template>
  <div class="register-form">
    <h2 class="form-title">注册</h2>
    
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
        <label for="email">邮箱</label>
        <input
          id="email"
          v-model="email"
          type="email"
          placeholder="请输入邮箱地址"
          :class="{ 'has-error': emailError }"
        />
        <span v-if="emailError" class="error-text">{{ emailError }}</span>
      </div>

      <div class="form-group">
        <label for="password">密码</label>
        <div class="password-input">
          <input
            id="password"
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="请输入密码（至少8个字符）"
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

      <div class="form-group">
        <label for="confirmPassword">确认密码</label>
        <input
          id="confirmPassword"
          v-model="confirmPassword"
          :type="showPassword ? 'text' : 'password'"
          placeholder="请再次输入密码"
          :class="{ 'has-error': confirmPasswordError }"
        />
        <span v-if="confirmPasswordError" class="error-text">{{ confirmPasswordError }}</span>
      </div>

      <div v-if="authStore.error" class="form-error">
        {{ authStore.error }}
      </div>

      <button
        type="submit"
        class="submit-btn"
        :disabled="!isFormValid || authStore.isLoading"
      >
        {{ authStore.isLoading ? '注册中...' : '注册' }}
      </button>
    </form>

    <div class="form-footer">
      <span>已有账号？</span>
      <button type="button" class="link-btn" @click="emit('switch-to-login')">
        立即登录
      </button>
    </div>
  </div>
</template>

<style scoped>
.register-form {
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
  margin-bottom: 1.25rem;
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
