<template>
  <div class="app">
    <Notification ref="notificationRef" />

    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="brand">
        <div class="logo">TRS</div>
        <div class="title">Task Run Service</div>
      </div>

      <nav class="menu">
        <router-link to="/tasks" class="menu-item" active-class="active">
          <span class="icon" aria-hidden>
            <!-- list icon -->
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 6h13"></path><path d="M8 12h13"></path><path d="M8 18h13"></path><path d="M3 6h.01"></path><path d="M3 12h.01"></path><path d="M3 18h.01"></path></svg>
          </span>
          <span class="label">任务管理</span>
        </router-link>

        <router-link to="/scripts" class="menu-item" active-class="active">
          <span class="icon">
            <!-- file icon -->
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><path d="M14 2v6h6"></path></svg>
          </span>
          <span class="label">脚本管理</span>
        </router-link>

        <router-link to="/runs" class="menu-item" active-class="active">
          <span class="icon">
            <!-- clock icon -->
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path></svg>
          </span>
          <span class="label">执行记录</span>
        </router-link>

        <router-link to="/current" class="menu-item" active-class="active">
          <span class="icon">
            <!-- play icon -->
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
          </span>
          <span class="label">当前任务</span>
        </router-link>

        <router-link to="/monitor" class="menu-item" active-class="active">
          <span class="icon">
            <!-- server/monitor icon -->
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="8" rx="2"></rect><rect x="2" y="13" width="20" height="8" rx="2"></rect></svg>
          </span>
          <span class="label">系统状态</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <button class="collapse-btn" @click="isCollapsed = !isCollapsed" aria-label="切换侧边栏">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>
      </div>
    </aside>

    <div class="content">
      <header class="topbar">
        <div class="top-left">
          <h2 class="page-title">管理面板</h2>
        </div>
        <div class="top-right">
          <Notification ref="notificationRef" />
        </div>
      </header>

      <main class="main">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script>
import Notification from './components/Notification.vue'

export default {
  name: 'App',
  components: { Notification },
  data() {
    return { isCollapsed: false }
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
:root{
  --primary: #2563eb; /* blue */
  --primary-600: #1e40af;
  --bg: #ffffff;
  --muted: #6b7280;
  --surface: #f8fafc;
}

.app{
  display:flex;
  min-height:100vh;
  background:var(--surface);
}

.sidebar{
  width:220px;
  background:white;
  border-right:1px solid #e6eef8;
  padding:1rem 0.5rem;
  display:flex;
  flex-direction:column;
  box-shadow: 2px 0 6px rgba(15,23,42,0.03);
}
.sidebar.collapsed{width:72px}

.brand{display:flex;align-items:center;gap:0.75rem;padding:0.5rem 0.75rem;margin-bottom:0.5rem}
.logo{background:linear-gradient(135deg,var(--primary),var(--primary-600));color:#3b82f6;border-radius:6px;padding:6px 8px;font-weight:700}
.title{font-weight:600;color:var(--primary-600);font-size:0.95rem}

.menu{display:flex;flex-direction:column;gap:6px;padding:0.5rem}
.menu-item{display:flex;align-items:center;gap:0.75rem;padding:0.6rem 0.8rem;border-radius:8px;color:var(--muted);text-decoration:none}
.menu-item .icon{display:inline-flex;align-items:center;justify-content:center;color:var(--primary-600)}
.menu-item .label{font-size:0.95rem}
.menu-item:hover{background:#f1f8ff;color:var(--primary-600)}
.menu-item.active{background:linear-gradient(90deg,var(--primary) 0%, #3b82f6 100%);color:#5568d3}
.menu-item.active .icon{color:#5568d3}

.sidebar-footer{margin-top:auto;padding:0.5rem;display:flex;justify-content:center}
.collapse-btn{background:transparent;border:1px solid #e6eef8;padding:6px;border-radius:6px;cursor:pointer}

.content{flex:1;display:flex;flex-direction:column}
.topbar{height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 1.5rem;background:transparent;border-bottom:1px solid rgba(15,23,42,0.04)}
.page-title{margin:0;color:var(--primary-600);font-size:1.05rem}
.main{padding:1.5rem}

@media(max-width:900px){
  .sidebar{position:fixed;left:0;top:0;bottom:0;z-index:30;transform:translateX(0)}
  .content{margin-left:72px}
}
</style>
