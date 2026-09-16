import { createRouter, createWebHashHistory } from 'vue-router';

// S8: routes động 100% — mỗi view 1 chunk riêng (orders/quotes/catalog tách khỏi initial)
const OrdersView = () => import('../views/OrdersView.vue');
const QuotesView = () => import('../views/QuotesView.vue');
const CatalogView = () => import('../views/CatalogView.vue');

const routes = [
	{
		path: '/',
		redirect: '/orders',
	},
	{
		path: '/orders',
		name: 'orders',
		component: OrdersView,
	},
	{
		path: '/quotes',
		name: 'quotes',
		component: QuotesView,
	},
	{
		path: '/catalog',
		name: 'catalog',
		component: CatalogView,
	},
	// Backward compatibility redirects
	{
		path: '/items',
		redirect: (to) => ({ path: '/catalog', query: { tab: 'sp', ...to.query } }),
	},
	{
		path: '/customers',
		redirect: (to) => ({ path: '/catalog', query: { tab: 'kh', ...to.query } }),
	},
	{
		path: '/suppliers',
		redirect: (to) => ({ path: '/catalog', query: { tab: 'ncc', ...to.query } }),
	},
	{
		path: '/users',
		redirect: (to) => ({ path: '/catalog', query: { tab: 'user', ...to.query } }),
	},
];

const router = createRouter({
	history: createWebHashHistory(),
	routes,
});

export default router;
