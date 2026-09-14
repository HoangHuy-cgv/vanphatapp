<template>
	<FrappeUIProvider>
	<div class="portal-layout">
		<!-- Sidebar Navigation -->
		<aside class="sidebar">
			<div class="brand-block">
				<img :src="logoUrl" alt="Bao Bì Vạn Phát" class="brand-logo" />
				<div class="brand-title">BAO BÌ VẠN PHÁT</div>
			</div>

			<nav class="nav-menu">
				<button type="button" class="nav-btn">
					<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<rect x="3" y="3" width="7" height="7"></rect>
						<rect x="14" y="3" width="7" height="7"></rect>
						<rect x="14" y="14" width="7" height="7"></rect>
						<rect x="3" y="14" width="7" height="7"></rect>
					</svg>
					<span class="nav-text">Tổng quan</span>
				</button>
				<button
					type="button"
					class="nav-btn"
					:class="{ active: currentView === 'quotes' }"
					@click="navigateTo('quotes')"
				>
					<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
						<polyline points="14 2 14 8 20 8"></polyline>
						<line x1="16" y1="13" x2="8" y2="13"></line>
						<line x1="16" y1="17" x2="8" y2="17"></line>
						<polyline points="10 9 9 9 8 9"></polyline>
					</svg>
					<span class="nav-text">Báo giá</span>
					<span v-if="quotesCount" class="nav-badge">{{ quotesCount }}</span>
				</button>
				<button
					type="button"
					class="nav-btn"
					:class="{ active: currentView === 'orders' }"
					@click="navigateTo('orders')"
				>
					<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<line x1="16.5" y1="9.4" x2="7.5" y2="4.21"></line>
						<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
						<polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
						<line x1="12" y1="22.08" x2="12" y2="12"></line>
					</svg>
					<span class="nav-text">Đơn hàng</span>
					<span v-if="ordersCount" class="nav-badge">{{ ordersCount }}</span>
				</button>
				<button type="button" class="nav-btn">
					<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
						<polyline points="2 17 12 22 22 17"></polyline>
						<polyline points="2 12 12 17 22 12"></polyline>
					</svg>
					<span class="nav-text">Sản xuất</span>
				</button>
				<button
					type="button"
					class="nav-btn"
					:class="{ active: isCatalogView }"
					@click="navigateTo('catalog')"
				>
					<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
						<line x1="3" y1="9" x2="21" y2="9"></line>
						<line x1="9" y1="21" x2="9" y2="9"></line>
					</svg>
					<span class="nav-text">Danh mục</span>
					<span v-if="catalogTotalCount" class="nav-badge">{{ catalogTotalCount }}</span>
				</button>
			</nav>

			<!-- Bottom User & Logout (ADR-006: trạng thái đăng nhập thật từ get_boot) -->
			<div class="sidebar-footer">
				<div class="user-block" :title="currentUser || 'Chưa đăng nhập'">
					<div class="user-avatar">
						<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
							<circle cx="12" cy="7" r="4"></circle>
						</svg>
					</div>
					<span class="user-id">{{ currentUser || 'Chưa đăng nhập' }}</span>
				</div>
				<button
					type="button"
					class="btn-logout"
					title="Đăng xuất"
					@click="handleLogout"
				>
					<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
						<polyline points="16 17 21 12 16 7"></polyline>
						<line x1="21" y1="12" x2="9" y2="12"></line>
					</svg>
				</button>
			</div>
		</aside>

		<!-- Main Routed View (S8: keep-alive CHỈ list đọc nhiều, include+max, refresh onActivated) -->
		<main class="main-content">
			<router-view v-slot="{ Component }">
				<Suspense>
					<template #default>
						<keep-alive include="OrdersView,CatalogView,QuotesView" :max="5">
							<component :is="Component" />
						</keep-alive>
					</template>
					<template #fallback>
						<div class="cockpit-empty-state" aria-busy="true">
							<span class="empty-msg">Đang tải màn hình...</span>
						</div>
					</template>
				</Suspense>
			</router-view>
		</main>

		<!-- Toast qua lib frappe-ui (FrappeUIProvider portals) — P4c xóa CockpitToast tự viết -->
	</div>
	</FrappeUIProvider>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { FrappeUIProvider } from 'frappe-ui';
import logoUrl from './assets/logo-vanphat.png';
import { useSession } from './composables/useSession';
import { usePortalCounts } from './composables/usePortalCounts';

const route = useRoute();
const router = useRouter();

const { currentUser, boot, handleLogout } = useSession();
const { quotesCount, ordersCount, catalogCount: catalogTotalCount } = usePortalCounts();

// View alias for backward compatibility and reactive binding
const view = ref('orders');

const currentView = computed(() => {
	if (route && route.name) return route.name;
	return view.value;
});

const isCatalogView = computed(() => {
	return currentView.value === 'catalog' || view.value === 'catalog' || view.value === 'items';
});

function navigateTo(targetView) {
	view.value = targetView;
	if (router) {
		router.push({ path: `/${targetView}` });
	}
}

onMounted(async () => {
	await boot();

	// Support legacy query parameter redirects: /portal?view=catalog, /portal?view=quotes, etc.
	const urlParams = new URLSearchParams(window.location.search);
	const urlView = urlParams.get('view');
	if (urlView) {
		if (['customers', 'suppliers', 'users', 'items', 'catalog'].includes(urlView)) {
			let tab = 'sp';
			if (urlView === 'customers') tab = 'kh';
			else if (urlView === 'suppliers') tab = 'ncc';
			else if (urlView === 'users') tab = 'user';
			view.value = 'catalog';
			if (router) {
				router.replace({ path: '/catalog', query: { tab, ...Object.fromEntries(urlParams) } });
			}
		} else if (urlView === 'quotes' || urlView === 'orders') {
			view.value = urlView;
			if (router) {
				router.replace({ path: `/${urlView}`, query: Object.fromEntries(urlParams) });
			}
		}
	}
});
</script>
