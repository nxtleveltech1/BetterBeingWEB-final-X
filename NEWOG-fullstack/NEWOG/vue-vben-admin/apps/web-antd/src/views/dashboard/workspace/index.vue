<script lang="ts" setup>
import type {
  WorkbenchProjectItem,
  WorkbenchQuickNavItem,
  WorkbenchTodoItem,
  WorkbenchTrendItem,
} from '@vben/common-ui';

import { ref } from 'vue';
import { useRouter } from 'vue-router';

import {
  AnalysisChartCard,
  WorkbenchHeader,
  WorkbenchProject,
  WorkbenchQuickNav,
  WorkbenchTodo,
  WorkbenchTrends,
} from '@vben/common-ui';
import { preferences } from '@vben/preferences';
import { useUserStore } from '@vben/stores';
import { openWindow } from '@vben/utils';

import AnalyticsVisitsSource from '../analytics/analytics-visits-source.vue';

const userStore = useUserStore();

// 这是一个示例数据，实际项目中需要根据实际情况进行调整
// url 也可以是内部路由，在 navTo 方法中识别处理，进行内部跳转
// 例如：url: /dashboard/workspace
const projectItems: WorkbenchProjectItem[] = [
  {
    color: '#1769aa',
    content: 'Better Being product management dashboard.',
    date: '2025-08-01',
    group: 'Admin',
    icon: 'carbon:analytics',
    title: 'Better Being Website',
    url: 'https://betterbeing.com',
  },
  {
    color: '#3fb27f',
    content: 'Monitor latest member registrations and users.',
    date: '2025-08-03',
    group: 'Users',
    icon: 'ion:people',
    title: 'User Portal',
    url: '/admin/users',
  },
  {
    color: '#e18525',
    content: 'View and moderate user feedback.',
    date: '2025-08-02',
    group: 'Feedback',
    icon: 'ic:outline-feedback',
    title: 'Feedback Center',
    url: '/admin/feedback',
  }
];

// 同样，这里的 url 也可以使用以 http 开头的外部链接
const quickNavItems: WorkbenchQuickNavItem[] = [
  {
    color: '#1fdaca',
    icon: 'ion:home-outline',
    title: 'Home',
    url: '/',
  },
  {
    color: '#3fb27f',
    icon: 'ion:settings-outline',
    title: 'Admin',
    url: '/admin',
  },
  {
    color: '#e18525',
    icon: 'ion:layers-outline',
    title: 'Content',
    url: '/admin/content',
  },
  {
    color: '#bf0c2c',
    icon: 'ion:people',
    title: 'Users',
    url: '/admin/users',
  },
  {
    color: '#00d8ff',
    icon: 'ion:bar-chart-outline',
    title: 'Analytics',
    url: '/admin/analytics',
  }
];

const todoItems = ref<WorkbenchTodoItem[]>([
  {
    completed: false,
    content: 'Review latest content updates and approve as needed.',
    date: '2025-08-05 11:00',
    title: 'Review Content Approvals',
  },
  {
    completed: false,
    content: 'Respond to user feedback for this week.',
    date: '2025-08-05 14:00',
    title: 'Feedback Response',
  },
  {
    completed: true,
    content: 'Check daily security & login logs.',
    date: '2025-08-04 09:00',
    title: 'Security Audit',
  }
]);
const trendItems: WorkbenchTrendItem[] = [
  {
    avatar: 'svg:avatar-1',
    content: `New user <a>Jane Doe</a> joined Better Being.`,
    date: 'Just now',
    title: 'Notification',
  },
  {
    avatar: 'svg:avatar-2',
    content: `<a>John Smith</a> published a wellness article.`,
    date: '1 hour ago',
    title: 'Article',
  },
  {
    avatar: 'svg:avatar-3',
    content: `User <a>Mark Lee</a> submitted feedback.`,
    date: 'Yesterday',
    title: 'Feedback',
  }
];

const router = useRouter();

// 这是一个示例方法，实际项目中需要根据实际情况进行调整
// This is a sample method, adjust according to the actual project requirements
function navTo(nav: WorkbenchProjectItem | WorkbenchQuickNavItem) {
  if (nav.url?.startsWith('http')) {
    openWindow(nav.url);
    return;
  }
  if (nav.url?.startsWith('/')) {
    router.push(nav.url).catch((error) => {
      console.error('Navigation failed:', error);
    });
  } else {
    console.warn(`Unknown URL for navigation item: ${nav.title} -> ${nav.url}`);
  }
}
</script>

<template>
  <div class="p-5">
    <WorkbenchHeader
      :avatar="userStore.userInfo?.avatar || preferences.app.defaultAvatar"
    >
      <template #title>
        Good morning, {{ userStore.userInfo?.realName || 'Admin' }}. Welcome to your Better Being dashboard!
      </template>
      <template #description> It's sunny today, 20°C - 32°C! </template>
    </WorkbenchHeader>

    <div class="mt-5 flex flex-col lg:flex-row">
      <div class="mr-4 w-full lg:w-3/5">
        <WorkbenchProject :items="projectItems" title="Your Projects" @click="navTo" />
        <WorkbenchTrends :items="trendItems" class="mt-5" title="Recent Activity" />
      </div>
      <div class="w-full lg:w-2/5">
        <WorkbenchQuickNav
          :items="quickNavItems"
          class="mt-5 lg:mt-0"
          title="Quick Navigation"
          @click="navTo"
        />
        <WorkbenchTodo :items="todoItems" class="mt-5" title="Todos" />
        <AnalysisChartCard class="mt-5" title="Visit Source">
          <AnalyticsVisitsSource />
        </AnalysisChartCard>
      </div>
    </div>
  </div>
</template>
