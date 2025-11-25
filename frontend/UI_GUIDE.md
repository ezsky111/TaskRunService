# 前端 UI 现代化指南

## 已完成

✅ **Tailwind CSS** - 已安装并配置  
✅ **Lucide Vue Next** - 图标库已安装  
✅ **Headless UI** - 基础组件库已安装  
✅ **TaskList.vue** - 已使用 Tailwind + Lucide 重写  
✅ **可复用 UI 组件** - Button, Card, Badge 已创建

## 使用指南

### 1. 在任何 Vue 文件中使用 Tailwind CSS

```vue
<template>
  <div class="min-h-screen bg-slate-50 p-8">
    <h1 class="text-3xl font-bold text-slate-900">标题</h1>
    <p class="mt-2 text-slate-600">描述文字</p>
  </div>
</template>
```

### 2. 使用 Lucide 图标

```vue
<script>
import { Plus, Play, BarChart3, Trash2, Edit, Settings } from 'lucide-vue-next'

export default {
  components: { Plus, Play, BarChart3, Trash2, Edit, Settings }
}
</script>

<template>
  <button>
    <Plus :size="20" />
    新增
  </button>
</template>
```

**常用图标：**
- Plus (新增)
- Trash2 (删除)
- Edit (编辑)
- Play (执行)
- BarChart3 (报表)
- Settings (设置)
- Search (搜索)
- ChevronDown (下拉)
- AlertCircle (警告)
- CheckCircle (成功)
- Clock (时间)
- Database (数据库)

[完整图标列表](https://lucide.dev)

### 3. 使用可复用 UI 组件

#### Button
```vue
<script>
import { Button } from '@/components/ui'

export default {
  components: { Button }
}
</script>

<template>
  <!-- 主按钮 -->
  <Button variant="primary">主按钮</Button>
  
  <!-- 次按钮 -->
  <Button variant="secondary">次按钮</Button>
  
  <!-- 危险按钮 -->
  <Button variant="danger">删除</Button>
  
  <!-- 幽灵按钮 -->
  <Button variant="ghost">取消</Button>
  
  <!-- 不同尺寸 -->
  <Button size="sm">小</Button>
  <Button size="md">中</Button>
  <Button size="lg">大</Button>
  
  <!-- 禁用状态 -->
  <Button disabled>禁用</Button>
  
  <!-- 带图标 -->
  <Button>
    <Plus :size="18" />
    新增
  </Button>
</template>
```

#### Card
```vue
<script>
import { Card } from '@/components/ui'

export default {
  components: { Card }
}
</script>

<template>
  <Card>
    <h2 class="text-xl font-bold">卡片标题</h2>
    <p class="mt-2 text-slate-600">卡片内容</p>
  </Card>
  
  <!-- 无内边距 -->
  <Card no-padding>
    <img src="image.jpg" alt="Image" class="w-full" />
  </Card>
</template>
```

#### Badge
```vue
<script>
import { Badge } from '@/components/ui'

export default {
  components: { Badge }
}
</script>

<template>
  <Badge variant="blue">蓝色</Badge>
  <Badge variant="green">绿色</Badge>
  <Badge variant="red">红色</Badge>
  <Badge variant="yellow">黄色</Badge>
  <Badge variant="slate">灰色</Badge>
</template>
```

### 4. Tailwind 常用样式速查表

#### 布局
```vue
<!-- 弹性布局 -->
<div class="flex items-center justify-between gap-4">...</div>

<!-- 网格 -->
<div class="grid grid-cols-3 gap-4">...</div>

<!-- 间距 -->
<div class="p-6 m-4">...</div> <!-- p=padding, m=margin -->
<div class="px-6 py-4">...</div> <!-- x/y 轴 -->

<!-- 宽高 -->
<div class="w-full h-screen">...</div>
<div class="w-1/2 h-32">...</div>
```

#### 文本
```vue
<!-- 尺寸 -->
<h1 class="text-3xl">...</h1> <!-- text-sm/base/lg/xl/2xl/3xl/4xl -->

<!-- 字体 -->
<div class="font-bold">粗体</div> <!-- font-light/normal/semibold/bold -->

<!-- 颜色 -->
<p class="text-slate-600">...</p> <!-- text-red/blue/green/yellow/slate-50/100/200/.../900 -->

<!-- 对齐 -->
<p class="text-left">左对齐</p>
<p class="text-center">居中</p>
<p class="text-right">右对齐</p>
```

#### 背景 & 边框
```vue
<!-- 背景 -->
<div class="bg-blue-600">蓝色背景</div>
<div class="bg-gradient-to-r from-blue-600 to-purple-600">渐变</div>

<!-- 边框 -->
<div class="border border-slate-200">...</div>
<div class="rounded-lg">圆角</div> <!-- rounded-none/sm/md/lg/xl/full -->
<div class="border-2 border-blue-600 rounded-lg">...</div>

<!-- 阴影 -->
<div class="shadow-sm">小阴影</div>
<div class="shadow-md">中阴影</div>
<div class="shadow-lg">大阴影</div>
```

#### 互动 & 状态
```vue
<!-- 悬停 -->
<button class="hover:bg-blue-700">...</button>

<!-- 焦点 -->
<input class="focus:ring-2 focus:ring-blue-600">

<!-- 禁用 -->
<button class="disabled:opacity-50 disabled:cursor-not-allowed">...</button>

<!-- 过渡 -->
<div class="transition hover:scale-110">...</div>

<!-- 动画 -->
<div class="animate-spin">...</div> <!-- spin/pulse/bounce -->
```

#### 响应式
```vue
<!-- 手机优先 -->
<div class="text-sm md:text-base lg:text-lg">
  <!-- 小屏幕: 14px, 中屏幕(md): 16px, 大屏幕(lg): 18px -->
</div>
```

## 更新其他视图

按照 `TaskList.vue` 的模式更新其他视图：

1. **替换手写样式** → 使用 Tailwind 类名
2. **替换 emoji 图标** → 使用 Lucide 图标
3. **删除 `<style scoped>` 块** → 只保留 `/* Using Tailwind CSS */` 注释
4. **导入需要的图标** → 从 `lucide-vue-next` 导入

### 需要更新的视图
- ✅ TaskList.vue (已完成)
- ⏳ DbTaskEditor.vue
- ⏳ DbTaskExecute.vue
- ⏳ DbTaskRuns.vue
- ⏳ TaskEditor.vue
- ⏳ TaskLogs.vue
- ⏳ SystemMonitor.vue

## 配置文件

- `tailwind.config.js` - Tailwind 配置
- `postcss.config.js` - PostCSS 配置
- `src/index.css` - Tailwind 指令导入
- `src/main.js` - 已导入 index.css
- `src/components/ui/` - 可复用组件库

## 主题颜色

当前主题使用 **蓝色** 作为主色调：
- 主色: `blue-600` (#2563eb)
- 次色: `blue-700` (#1d4ed8)
- 浅色: `blue-100` (#dbeafe)
- 深色: `blue-900` (#1e3a8a)

## 下一步

1. 根据需要更新其他视图
2. 考虑创建更多 UI 组件（Modal, Input, Select, Table, etc.)
3. 建立设计规范文档
4. 根据用户反馈调整样式

