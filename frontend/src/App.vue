<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API = 'http://127.0.0.1:8000'

// 登录状态
const username = ref('')
const password = ref('')
const isRegisterMode = ref(false)
const userId = ref(null)
const currentUsername = ref('')
const isLoggedIn = ref(false)

// ATM 数据
const balance = ref(0)
const amount = ref('')
const toUserId = ref(2)
const transferAmount = ref('')
const transactions = ref([])
const message = ref('')

async function login() {
  try {
    const response = await axios.post(`${API}/login`, {
      username: username.value,
      password: password.value
    })

    if (response.data.message !== 'Login successful') {
      message.value = response.data.message
      return
    }

    userId.value = response.data.user_id
    currentUsername.value = response.data.username
    isLoggedIn.value = true

    password.value = ''
    message.value = '登录成功'

    await loadBalance()
    await loadTransactions()
  } catch (error) {
    message.value = '登录失败'
  }
}
async function register() {
  try {
    const response = await axios.post(`${API}/register`, {
      username: username.value,
      password: password.value
    })

    message.value = response.data.message

    if (response.data.message === 'Register successful') {
      isRegisterMode.value = false
      password.value = ''
      message.value = '注册成功，请登录'
    }
  } catch (error) {
    message.value = '注册失败'
  }
}
function logout() {
  userId.value = null
  currentUsername.value = ''
  isLoggedIn.value = false
  balance.value = 0
  transactions.value = []
  username.value = ''
  password.value = ''
  message.value = ''
}

async function loadBalance() {
  try {
    const response = await axios.get(
      `${API}/balance/${userId.value}`
    )

    balance.value = response.data.balance
  } catch (error) {
    message.value = '余额加载失败'
  }
}

async function deposit() {
  try {
    const response = await axios.post(`${API}/deposit`, {
      user_id: userId.value,
      amount: Number(amount.value)
    })

    message.value = response.data.message
    amount.value = ''

    await loadBalance()
    await loadTransactions()
  } catch (error) {
    message.value = '存款失败'
  }
}

async function withdraw() {
  try {
    const response = await axios.post(`${API}/withdraw`, {
      user_id: userId.value,
      amount: Number(amount.value)
    })

    message.value = response.data.message
    amount.value = ''

    await loadBalance()
    await loadTransactions()
  } catch (error) {
    message.value = '取款失败'
  }
}

async function transfer() {
  try {
    const response = await axios.post(`${API}/transfer`, {
      from_user_id: userId.value,
      to_user_id: Number(toUserId.value),
      amount: Number(transferAmount.value)
    })

    message.value = response.data.message
    transferAmount.value = ''

    await loadBalance()
    await loadTransactions()
  } catch (error) {
    message.value = '转账失败'
  }
}

async function loadTransactions() {
  try {
   const response = await axios.get(
  `${API}/transactions/${userId.value}`
)
    transactions.value = response.data.transactions
  } catch (error) {
    message.value = '交易记录加载失败'
  }
}

onMounted(() => {
  // 现在不自动加载余额
  // 必须先登录
})
</script>

<template>
  <main class="page">

    <!-- 登录页面 -->
    <section v-if="!isLoggedIn" class="login-box">
     <h1>{{ isRegisterMode ? 'ATM 注册' : 'ATM 登录' }}</h1>

<p class="welcome">
  {{ isRegisterMode ? '创建一个新的银行账户' : '欢迎回来，请登录账户' }}
</p>
      

      <label>用户名</label>
      <input
        v-model="username"
        type="text"
        placeholder="请输入用户名"
      />

      <label>密码</label>
      <input
        v-model="password"
        type="password"
        placeholder="请输入密码"
        @keyup.enter="login"
      />

    <button
  v-if="!isRegisterMode"
  class="login-button"
  @click="login"
>
  登录
</button>

<button
  v-else
  class="login-button"
  @click="register"
>
  注册
</button>

<button
  class="switch-button"
  @click="isRegisterMode = !isRegisterMode"
>
  {{ isRegisterMode ? '已有账户？返回登录' : '没有账户？立即注册' }}
</button>

      <p v-if="message" class="message">
        {{ message }}
      </p>
    </section>

    <!-- ATM 主页面 -->
    <section v-else class="atm">

      <div class="header">
        <div>
          <p class="eyebrow">XIAOXIONG BANK</p>
          <h1>ATM 控制台</h1>
        </div>

        <div class="user-area">
          <span>{{ currentUsername }}</span>
          <button class="small" @click="logout">
            退出登录
          </button>
        </div>
      </div>

      <div class="balance-card">
        <span>当前余额</span>
        <strong>¥ {{ balance }}</strong>
        <small>
          {{ currentUsername }} · 账户 ID：{{ userId }}
        </small>
      </div>

      <p v-if="message" class="message">
        {{ message }}
      </p>

      <div class="grid">

        <section class="card">
          <h2>存款 / 取款</h2>

          <input
            v-model="amount"
            type="number"
            min="0"
            placeholder="请输入金额"
          />

          <div class="buttons">
            <button @click="deposit">
              存款
            </button>

            <button class="secondary" @click="withdraw">
              取款
            </button>
          </div>
        </section>

        <section class="card">
          <h2>账户转账</h2>

          <label>收款账户 ID</label>
          <input
            v-model="toUserId"
            type="number"
            placeholder="用户 ID"
          />

          <label>转账金额</label>
          <input
            v-model="transferAmount"
            type="number"
            min="0"
            placeholder="请输入金额"
          />

          <button @click="transfer">
            确认转账
          </button>
        </section>

      </div>

      <section class="card records">

        <div class="records-title">
          <h2>最近交易</h2>

          <button
            class="small"
            @click="loadTransactions"
          >
            刷新
          </button>
        </div>

        <div
          v-for="transaction in transactions"
          :key="transaction[0]"
          class="transaction"
        >
          <div>
            <strong>{{ transaction[3] }}</strong>

            <small>
              {{ transaction[1] ?? '外部' }}
              →
              {{ transaction[2] ?? '外部' }}
            </small>
          </div>

          <span>
            ¥ {{ transaction[4] }}
          </span>
        </div>

        <p
          v-if="transactions.length === 0"
          class="empty"
        >
          暂无交易记录
        </p>

      </section>

    </section>
  </main>
</template>

<style scoped>
* {
  box-sizing: border-box;
}

.page {
  min-height: 100vh;
  padding: 50px 20px;
  background: #f4f6f8;
  color: #1f2937;
}

.login-box,
.atm {
  width: min(900px, 100%);
  margin: 0 auto;
}

.login-box {
  width: min(420px, 100%);
  margin-top: 80px;
  padding: 32px;
  border-radius: 18px;
  background: white;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.07);
}

.login-box h1 {
  margin-bottom: 8px;
}

.welcome {
  margin-bottom: 28px;
  color: #6b7280;
}

.header,
.records-title,
.buttons,
.user-area {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header {
  margin-bottom: 24px;
}

.user-area {
  gap: 12px;
}

h1,
h2,
p {
  margin-top: 0;
}

h1 {
  margin-bottom: 0;
  font-size: 30px;
}

h2 {
  font-size: 17px;
}

.eyebrow {
  margin-bottom: 5px;
  font-size: 12px;
  letter-spacing: 2px;
  color: #6b7280;
}

.balance-card {
  display: flex;
  flex-direction: column;
  padding: 30px;
  margin-bottom: 20px;
  border-radius: 18px;
  background: #111827;
  color: white;
}

.balance-card strong {
  margin: 8px 0;
  font-size: 42px;
}

.balance-card small {
  color: #9ca3af;
}

.message {
  padding: 12px 16px;
  border-radius: 10px;
  background: white;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.card {
  padding: 24px;
  margin-bottom: 20px;
  border-radius: 16px;
  background: white;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
}

label {
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
  color: #6b7280;
}

input {
  width: 100%;
  padding: 12px 14px;
  margin-bottom: 14px;
  border: 1px solid #d1d5db;
  border-radius: 9px;
  font-size: 15px;
}

button {
  padding: 11px 18px;
  border: 0;
  border-radius: 9px;
  background: #111827;
  color: white;
  cursor: pointer;
}

.login-button {
  width: 100%;
}

.buttons {
  gap: 10px;
}

.buttons button {
  flex: 1;
}

.secondary,
.small {
  background: #e5e7eb;
  color: #111827;
}

.small {
  padding: 7px 12px;
}

.transaction {
  display: flex;
  justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid #eee;
}

.transaction div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.transaction small,
.empty {
  color: #6b7280;
}

@media (max-width: 650px) {
  .grid {
    grid-template-columns: 1fr;
  }

  .header {
    align-items: flex-start;
    gap: 15px;
  }
}
.switch-button {
  width: 100%;
  margin-top: 10px;
  background: transparent;
  color: #6b7280;
}
</style>