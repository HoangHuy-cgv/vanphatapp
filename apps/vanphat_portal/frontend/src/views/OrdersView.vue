<template>
	<div class="orders-view-wrapper">
		<!-- Header 1 Dòng Chuẩn Cockpit: 3 Tabs + Quick Search + Action Button -->
		<header class="page-head catalog-header-cockpit">
			<div class="order-tabs-bar catalog-tabs-bar">
				<button
					type="button"
					class="order-tab-btn"
					:class="{ active: activeOrderTab === 'xuong_sx' }"
					@click="activeOrderTab = 'xuong_sx'"
				>
					<span>Xưởng sản xuất</span>
					<span class="tab-badge">{{ tabCounts.xuong_sx || 0 }}</span>
				</button>
				<button
					type="button"
					class="order-tab-btn"
					:class="{ active: activeOrderTab === 'ngcs' }"
					@click="activeOrderTab = 'ngcs'"
				>
					<span>Túi NGCS</span>
					<span class="tab-badge">{{ tabCounts.ngcs || 0 }}</span>
				</button>
				<button
					type="button"
					class="order-tab-btn"
					:class="{ active: activeOrderTab === 'mua_ngoai' }"
					@click="activeOrderTab = 'mua_ngoai'"
				>
					<span>Mua ngoài trọn gói</span>
					<span class="tab-badge">{{ tabCounts.mua_ngoai || 0 }}</span>
				</button>
			</div>

			<!-- Quick Search Tức Thời Cùng Hàng Header Cockpit -->
			<div class="catalog-search-cockpit-wrap">
				<div class="search-input-wrap">
					<svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<circle cx="11" cy="11" r="8"></circle>
						<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
					</svg>
					<input
						type="text"
						v-model="orderSearchQuery"
						:placeholder="currentOrderSearchPlaceholder"
						class="catalog-search-input"
					/>
					<button
						v-if="orderSearchQuery"
						type="button"
						class="btn-clear-search"
						title="Xóa tìm kiếm"
						@click="orderSearchQuery = ''"
					>
						✕
					</button>
				</div>
			</div>

			<button
				type="button"
				class="btn-new-quote whitespace-nowrap flex-shrink-0"
				@click="openCreateOrderModal"
			>
				+ Tạo đơn hàng
			</button>
		</header>

		<div :key="activeOrderTab" class="table-container">
			<table class="data-table">
				<!-- TAB 1: XƯỞNG SẢN XUẤT -->
				<thead v-if="activeOrderTab === 'xuong_sx'">
					<tr>
						<th style="width: 10%;">Ngày</th>
						<th style="width: 20%;">Khách</th>
						<th style="width: 25%;">Mặt hàng</th>
						<th style="width: 13%; text-align: right;">Số lượng</th>
						<th style="width: 13%; text-align: right;">Đã cọc</th>
						<th style="width: 17%; text-align: center;">Vật tư & Máy</th>
						<th style="width: 12%; text-align: center;">Trạng thái</th>
					</tr>
				</thead>

				<!-- TAB 2: TÚI NGCS -->
				<thead v-else-if="activeOrderTab === 'ngcs'">
					<tr>
						<th style="width: 10%;">Ngày</th>
						<th style="width: 22%;">Khách</th>
						<th style="width: 26%;">Mặt hàng</th>
						<th style="width: 13%; text-align: right;">Số lượng</th>
						<th style="width: 13%; text-align: right;">Đã cọc</th>
						<th style="width: 16%; text-align: center;">In lụa NCC</th>
						<th style="width: 10%; text-align: center;">Trạng thái</th>
					</tr>
				</thead>

				<!-- TAB 3: MUA NGOÀI TRỌN GÓI -->
				<thead v-else>
					<tr>
						<th style="width: 10%;">Ngày</th>
						<th style="width: 22%;">Khách</th>
						<th style="width: 26%;">Mặt hàng</th>
						<th style="width: 13%; text-align: right;">Số lượng</th>
						<th style="width: 13%; text-align: right;">Đã cọc</th>
						<th style="width: 16%; text-align: center;">Hạn giao NCC</th>
						<th style="width: 10%; text-align: center;">Trạng thái</th>
					</tr>
				</thead>

				<tbody>
					<tr
						v-for="o in orders"
						:key="o.name"
						class="table-row cursor-pointer"
						@click="openOrderDetail(o)"
					>
						<td class="text-secondary text-num">{{ formatDateShort(o.transaction_date) }}</td>
						<td>
							<div class="font-bold text-white">{{ o.customer_alias || o.alias || o.customer || o.customer_name }}</div>
						</td>
						<td class="truncate" :title="o.item_name">
							<span class="font-medium text-white">{{ o.custom_alias || o.item_name || '—' }}</span>
						</td>
						<td class="text-right text-num font-bold">
							<span>{{ formatNumber(o.qty) }}</span>
							<span class="text-xs text-secondary" style="margin-left: 4px;">{{ o.uom || o.stock_uom || 'Túi' }}</span>
						</td>
						<td class="text-right">
							<span v-if="o.payment_type === 'Trả sau'" class="text-secondary font-bold text-[14px]">
								Trả sau
							</span>
							<span v-else class="text-num font-bold text-[14px]" :class="depositColorClass(o)">
								{{ formatCurrency(o.advance_paid) }}
							</span>
						</td>

						<!-- Cột theo Tab: Xưởng SX (Trạng thái thuần màu 14px) -->
						<td v-if="activeOrderTab === 'xuong_sx'" class="text-center whitespace-nowrap">
							<span class="font-bold text-[14px]" :class="o.materials_status === 'Đủ màng' ? 'text-emerald' : 'text-amber'">
								{{ o.materials_status || 'Chờ màng' }}
							</span>
						</td>

						<!-- Cột theo Tab: NGCS In Lụa (Trạng thái thuần màu 14px) -->
						<td v-else-if="activeOrderTab === 'ngcs'" class="text-center whitespace-nowrap">
							<span v-if="o.supplier_name" class="font-bold text-[14px]" :class="supplierSlaColorClass(o.supplier_eta_days)">
								{{ o.supplier_name }} ({{ supplierSlaText(o.supplier_eta_days) }})
							</span>
							<span v-else class="text-secondary text-xs">—</span>
						</td>

						<!-- Cột theo Tab: Mua Ngoài (Trạng thái thuần màu 14px) -->
						<td v-else class="text-center whitespace-nowrap">
							<span v-if="o.supplier_name" class="font-bold text-[14px]" :class="supplierSlaColorClass(o.supplier_eta_days)">
								{{ o.supplier_name }} ({{ supplierSlaText(o.supplier_eta_days) }})
							</span>
							<span v-else class="text-secondary text-xs">—</span>
						</td>

						<!-- Trạng thái chung (Trạng thái thuần màu 14px in đậm) -->
						<td class="text-center whitespace-nowrap">
							<span class="font-bold text-[14px]" :class="orderStatusColorClass(o)">
								{{ orderStatusText(o) }}
							</span>
						</td>
					</tr>
					<tr
						v-for="i in (orders.length > 0 ? Math.max(0, pageSize - orders.length) : 0)"
						:key="'order-filler-' + i"
						class="filler-row"
						aria-hidden="true"
					>
						<td colspan="7">&nbsp;</td>
					</tr>
					<tr v-if="orders.length === 0">
						<td colspan="7" class="empty-cell">
							<div v-if="loadingOrders" class="cockpit-empty-state">
								<span class="empty-msg">Đang tải đơn hàng từ ERPNext...</span>
							</div>
							<div v-else-if="orderSearchQuery" class="cockpit-empty-state">
								<span class="empty-msg">Không tìm thấy đơn hàng khớp với từ khóa "{{ orderSearchQuery }}"</span>
								<button type="button" class="btn-empty-action" @click="orderSearchQuery = ''">
									✕ Xóa tìm kiếm
								</button>
							</div>
							<div v-else class="cockpit-empty-state">
								<span class="empty-msg">Chưa có đơn hàng nào trong phân loại này</span>
								<button type="button" class="btn-empty-action btn-empty-primary" @click="openCreateOrderModal">
									+ Tạo đơn hàng mới
								</button>
							</div>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Thanh Phân Trang Sát Đáy Màn Hình Chuẩn Buồng Lái (Zero-Scroll 1080p) -->
		<div class="cockpit-pagination-bar">
			<div class="cockpit-pagination-left">
				<span>Hiển thị</span>
				<span class="text-white font-bold">{{ startRecord }}–{{ endRecord }}</span>
				<span>trên tổng số</span>
				<span class="text-white font-bold">{{ totalOrders }}</span>
				<span>đơn hàng</span>
			</div>
			<div class="cockpit-pagination-right">
				<button
					type="button"
					class="btn-page-nav"
					:disabled="currentPage <= 1 || loadingOrders"
					title="Trang trước (Phím [)"
					@click="prevPage"
				>
					‹
				</button>
				<span class="page-indicator">
					Trang {{ currentPage }} / {{ totalPages }}
				</span>
				<button
					type="button"
					class="btn-page-nav"
					:disabled="currentPage >= totalPages || loadingOrders"
					title="Trang sau (Phím ])"
					@click="nextPage"
				>
					›
				</button>
			</div>
		</div>

		<!-- Drawer Chi Tiết Đơn Hàng (S8: Suspense cho async chunk) -->
		<Suspense v-if="showOrderDetail">
			<DrawerOrderDetail
				:is-open="showOrderDetail"
				:open="showOrderDetail"
				:order="selectedOrder"
				@close="showOrderDetail = false"
				@update-order="onOrderUpdated"
				@delivery-order="onOrderDelivery"
			/>
		</Suspense>

		<!-- Modal Tạo Đơn Hàng Mới (S8: Suspense cho async chunk) -->
		<Suspense v-if="showCreateOrderModal">
			<ModalCreateOrder
				:is-open="showCreateOrderModal"
				:open="showCreateOrderModal"
				:master-items="masterItems"
				@close="showCreateOrderModal = false"
				@order-created="handleNewOrderCreated"
			/>
		</Suspense>
	</div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted, defineAsyncComponent } from 'vue';
import { useRoute } from 'vue-router';
// S8: drawers/modals nặng async — chunk riêng, render khi mở
const DrawerOrderDetail = defineAsyncComponent(() => import('../components/DrawerOrderDetail.vue'));
const ModalCreateOrder = defineAsyncComponent(() => import('../components/ModalCreateOrder.vue'));
import { api } from '../composables/useSession';
import { usePortalCounts } from '../composables/usePortalCounts';
import { useCockpitFormat } from '../composables/useCockpitFormat';

const route = useRoute();
const { ordersCount } = usePortalCounts();
// S7c: formatter dùng chung (xóa 2 bản copy-paste)
const { formatCurrency, formatNumber } = useCockpitFormat();

const orders = ref([]);
const loadingOrders = ref(false);
const activeOrderTab = ref('xuong_sx');
const orderSearchQuery = ref('');

// Pagination state (Zero-scroll 1080p: locked to 15 lines)
const currentPage = ref(1);
const pageSize = ref(15);
const totalOrders = ref(0);
const totalPages = ref(1);
const tabCounts = ref({ xuong_sx: 0, ngcs: 0, mua_ngoai: 0, all: 0 });

const startRecord = computed(() => {
	if (totalOrders.value === 0) return 0;
	return (currentPage.value - 1) * pageSize.value + 1;
});

const endRecord = computed(() => {
	return Math.min(currentPage.value * pageSize.value, totalOrders.value);
});

function prevPage() {
	if (currentPage.value > 1 && !loadingOrders.value) {
		currentPage.value--;
		loadOrders();
	}
}

function nextPage() {
	if (currentPage.value < totalPages.value && !loadingOrders.value) {
		currentPage.value++;
		loadOrders();
	}
}

function handleKeyDown(e) {
	if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target?.tagName)) return;
	if (e.key === '[') {
		prevPage();
	} else if (e.key === ']') {
		nextPage();
	}
}

const currentOrderSearchPlaceholder = computed(() => {
	switch (activeOrderTab.value) {
		case 'xuong_sx':
			return 'Tìm nhanh đơn xưởng sản xuất, tên khách, quy cách...';
		case 'ngcs':
			return 'Tìm nhanh đơn túi NGCS in sẵn, thương hiệu in lụa...';
		case 'mua_ngoai':
			return 'Tìm nhanh đơn hàng mua ngoài trọn gói, nhà cung cấp...';
		default:
			return 'Tìm nhanh đơn hàng, khách, mặt hàng...';
	}
});

watch(activeOrderTab, () => {
	currentPage.value = 1;
	loadOrders();
});

const masterItems = ref([]);
const selectedOrderId = ref('');
const showOrderDetail = ref(false);
const showCreateOrderModal = ref(false);

const selectedOrder = computed(() => {
	return orders.value.find((o) => o.name === selectedOrderId.value) || null;
});

let searchTimer = null;
watch(orderSearchQuery, () => {
	clearTimeout(searchTimer);
	searchTimer = setTimeout(() => {
		currentPage.value = 1;
		loadOrders();
	}, 250);
});

function depositColorClass(o) {
	const req = Number(o.required_deposit) || 0;
	if (!req) return 'text-secondary';
	if (o.advance_paid >= req) return 'text-emerald';
	if (o.advance_paid > 0) return 'text-amber';
	return 'text-secondary';
}

function supplierSlaColorClass(days) {
	if (days == null) return 'text-secondary';
	if (days < 0) return 'text-rose';
	if (days === 0) return 'text-amber';
	return 'text-emerald';
}

function supplierSlaText(days) {
	if (days == null) return '—';
	if (days < 0) return `Trễ ${Math.abs(days)} ngày`;
	if (days === 0) return 'Hôm nay';
	return `Còn ${days} ngày`;
}

function orderStatusText(o) {
	if (o.order_status_label) return o.order_status_label;
	if (o.is_hold || o.order_state?.includes('HOLD')) return 'HOLD';
	if (o.payment_type === 'Trả sau' && o.docstatus === 1) return 'Trả sau';
	if (o.docstatus === 1) return 'Đã duyệt';
	return 'Chờ cọc';
}

function orderStatusColorClass(o) {
	if (o.order_status_class) {
		if (o.order_status_class.includes('hold')) return 'text-rose';
		if (o.order_status_class.includes('ordered')) return 'text-emerald';
		if (o.order_status_class.includes('draft')) return 'text-amber';
	}
	if (o.is_hold || o.order_state?.includes('HOLD')) return 'text-rose';
	if (o.docstatus === 1 || o.order_state?.includes('Chính thức')) return 'text-emerald';
	if (o.advance_paid > 0) return 'text-sky';
	return 'text-amber';
}

function formatDateShort(val) {
	if (!val) return '—';
	const parts = String(val).split('-');
	if (parts.length === 3) {
		return `${parts[2]}/${parts[1]}`;
	}
	return val;
}

async function loadOrders() {
	loadingOrders.value = true;
	try {
		const data = await api('order.list_orders', {
			tab: activeOrderTab.value,
			query: orderSearchQuery.value.trim() || undefined,
			page: currentPage.value,
			page_length: pageSize.value,
		}, { get: true });
		if (data && Array.isArray(data.orders)) {
			orders.value = data.orders;
			totalOrders.value = data.total_count || 0;
			totalPages.value = data.total_pages || 1;
			if (data.tab_counts) {
				tabCounts.value = data.tab_counts;
			}
		} else if (Array.isArray(data)) {
			orders.value = data;
			totalOrders.value = data.length;
			totalPages.value = Math.ceil(data.length / pageSize.value) || 1;
		} else {
			orders.value = [];
			totalOrders.value = 0;
			totalPages.value = 1;
		}
		ordersCount.value = tabCounts.value.all || totalOrders.value;
	} catch (err) {
		console.error('Error loading orders:', err);
		orders.value = [];
	} finally {
		loadingOrders.value = false;
	}
}

async function loadMasterItems() {
	try {
		// ADR-006: picker tham chiếu trong trần 100 + filter server, không xin vượt trần.
		const data = await api('item.get_list', { page_length: 100 }, { get: true });
		if (data && Array.isArray(data.items)) {
			masterItems.value = data.items;
		} else if (Array.isArray(data)) {
			masterItems.value = data;
		}
	} catch (err) {
		console.error('Error loading master items:', err);
	}
}

function openOrderDetail(o) {
	selectedOrderId.value = o.name;
	showOrderDetail.value = true;
}

function openCreateOrderModal() {
	showCreateOrderModal.value = true;
	if (!masterItems.value.length) {
		loadMasterItems();
	}
}

async function handleNewOrderCreated(newOrder) {
	activeOrderTab.value = newOrder.order_tab || 'xuong_sx';
	selectedOrderId.value = newOrder.name;
	showOrderDetail.value = true;
	await loadOrders();
}

async function onOrderUpdated(updatedOrder) {
	const idx = orders.value.findIndex((o) => o.name === updatedOrder.name);
	if (idx !== -1) {
		orders.value[idx] = { ...updatedOrder };
	}
	await loadOrders();
}

function onOrderDelivery(order) {
	// ADR-006: trạng thái/số cọc do backend trả qua loadOrders; ở đây chỉ đóng drawer + refresh.
	showOrderDetail.value = false;
	loadOrders();
}

onMounted(async () => {
	window.addEventListener('keydown', handleKeyDown);
	await Promise.all([loadOrders(), loadMasterItems()]);

	// Sync from query parameters
	const query = route?.query || {};
	const urlParams = new URLSearchParams(window.location.search);

	const tabVal = query.tab || urlParams.get('tab');
	if (tabVal && ['xuong_sx', 'ngcs', 'mua_ngoai'].includes(tabVal)) {
		activeOrderTab.value = tabVal;
	}

	const orderParam = query.order || urlParams.get('order');
	if (orderParam) {
		selectedOrderId.value = orderParam;
		showOrderDetail.value = true;
	}

	const modalParam = query.modal || urlParams.get('modal');
	if (modalParam === 'create') {
		showCreateOrderModal.value = true;
	}
});

onUnmounted(() => {
	window.removeEventListener('keydown', handleKeyDown);
});

</script>

<style scoped>
.orders-view-wrapper {
	display: flex;
	flex-direction: column;
	flex: 1;
	min-height: 0;
}
</style>
