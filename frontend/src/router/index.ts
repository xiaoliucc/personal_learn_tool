import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/pages/DashboardPage.vue'),
    },
    {
      path: '/library',
      name: 'library',
      component: () => import('@/pages/LibraryPage.vue'),
    },
    {
      path: '/materials/:id',
      name: 'material-detail',
      component: () => import('@/pages/MaterialDetailPage.vue'),
    },
    {
      path: '/graph',
      name: 'knowledge-graph',
      component: () => import('@/pages/KnowledgeGraphPage.vue'),
    },
    {
      path: '/review',
      name: 'review',
      component: () => import('@/pages/ReviewPage.vue'),
    },
  ],
})

export default router
