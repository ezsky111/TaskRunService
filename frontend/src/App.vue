<template>
  <div class="app">
    <Notification ref="notificationRef" />
    
    <header class="header">
      <div class="logo">
        <h1>📋 Task Run Service</h1>
      </div>
      <nav class="nav">
        <router-link to="/tasks">任务列表</router-link>
        <router-link to="/logs">执行日志</router-link>
        <router-link to="/monitor">系统监控</router-link>
      </nav>
    </header>
    
    <main class="main">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
import Notification from './components/Notification.vue'

export default {
  name: 'App',
  components: {
    Notification
  },
  mounted() {
    this.$root.$notify = {
      success: (msg) => this.$refs.notificationRef?.success(msg),
      error: (msg) => this.$refs.notificationRef?.error(msg),
      warning: (msg) => this.$refs.notificationRef?.warning(msg),
      info: (msg) => this.$refs.notificationRef?.info(msg)
    }
  }
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.logo h1 {
  font-size: 1.5rem;
  font-weight: 600;
}

.nav {
  display: flex;
  gap: 2rem;
}

.nav a {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background 0.3s;
}

.nav a:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav a.router-link-active {
  background: rgba(255, 255, 255, 0.2);
  border-bottom: 2px solid white;
}

.main {
  flex: 1;
  padding: 2rem;
  background: #f8f9fa;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .nav {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .main {
    padding: 1rem;
  }
}
</style>
