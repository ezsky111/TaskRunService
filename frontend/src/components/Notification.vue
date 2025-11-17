<template>
  <div class="notification-container">
    <transition-group name="notify" tag="div">
      <div v-for="notif in notifications" :key="notif.id" :class="['notification', `notification-${notif.type}`]">
        <div class="notification-content">
          <span class="notification-message">{{ notif.message }}</span>
          <button @click="close(notif.id)" class="notification-close">×</button>
        </div>
      </div>
    </transition-group>
  </div>
</template>

<script>
export default {
  name: 'Notification',
  data() {
    return {
      notifications: [],
      nextId: 0
    }
  },
  methods: {
    show(message, type = 'info', duration = 3000) {
      const id = this.nextId++
      const notif = { id, message, type }
      this.notifications.push(notif)
      
      if (duration > 0) {
        setTimeout(() => this.close(id), duration)
      }
      
      return id
    },
    success(message, duration = 3000) {
      return this.show(message, 'success', duration)
    },
    error(message, duration = 5000) {
      return this.show(message, 'error', duration)
    },
    warning(message, duration = 4000) {
      return this.show(message, 'warning', duration)
    },
    info(message, duration = 3000) {
      return this.show(message, 'info', duration)
    },
    close(id) {
      this.notifications = this.notifications.filter(n => n.id !== id)
    }
  }
}
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  max-width: 400px;
}

.notification {
  margin-bottom: 10px;
  padding: 12px 16px;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-width: 300px;
  animation: slideIn 0.3s ease-out;
}

.notification-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.notification-message {
  flex: 1;
}

.notification-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  margin-left: 12px;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.notification-close:hover {
  opacity: 1;
}

.notification-success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.notification-error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.notification-warning {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeeba;
}

.notification-info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

@keyframes slideIn {
  from {
    transform: translateX(400px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.notify-enter-active, .notify-leave-active {
  transition: all 0.3s ease;
}

.notify-enter-from, .notify-leave-to {
  transform: translateX(400px);
  opacity: 0;
}
</style>
