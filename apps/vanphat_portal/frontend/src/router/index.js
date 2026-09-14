import { createRouter, createWebHashHistory } from 'vue-router';
import OrdersView from '../views/OrdersView.vue';
import QuotesView from '../views/QuotesView.vue';
import CatalogView from '../views/CatalogView.vue';

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
