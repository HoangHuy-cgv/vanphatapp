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
					<span class="tab-badge">{{ xuongSxOrders.length }}</span>
				</button>
				<button
					type="button"
					class="order-tab-btn"
					:class="{ active: activeOrderTab === 'ngcs' }"
					@click="activeOrderTab = 'ngcs'"
				>
					<span>Túi NGCS</span>
					<span class="tab-badge">{{ ngcsOrders.length }}</span>
				</button>
				<button
					type="button"
					class="order-tab-btn"
					:class="{ active: activeOrderTab === 'mua_ngoai' }"
					@click="activeOrderTab = 'mua_ngoai'"
				>
					<span>Mua ngoài trọn gói</span>
					<span class="tab-badge">{{ muaNgoaiOrders.length }}</span>
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
						v-for="o in filteredTabOrders"
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
					<tr v-if="filteredTabOrders.length === 0">
						<td colspan="7" class="empty-cell" style="padding: 2.5rem 1rem; text-align: center;">
							<div v-if="loadingOrders" class="text-secondary">Đang tải đơn hàng...</div>
							<div v-else class="text-secondary text-sm">Không tìm thấy đơn hàng nào</div>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Drawer Chi Tiết Đơn Hàng -->
		<DrawerOrderDetail
			:is-open="showOrderDetail"
			:open="showOrderDetail"
			:order="selectedOrder"
			@close="showOrderDetail = false"
			@update-order="onOrderUpdated"
			@delivery-order="onOrderDelivery"
		/>

		<!-- Modal Tạo Đơn Hàng Mới -->
		<ModalCreateOrder
			:is-open="showCreateOrderModal"
			:open="showCreateOrderModal"
			:master-items="masterItems"
			@close="showCreateOrderModal = false"
			@order-created="handleNewOrderCreated"
		/>
	</div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import DrawerOrderDetail from '../components/DrawerOrderDetail.vue';
import ModalCreateOrder from '../components/ModalCreateOrder.vue';
import { api } from '../composables/useSession';
import { usePortalCounts } from '../composables/usePortalCounts';

const route = useRoute();
const { ordersCount } = usePortalCounts();

const orders = ref([]);
const loadingOrders = ref(false);
const activeOrderTab = ref('xuong_sx');
const orderSearchQuery = ref('');

const currentOrderSearchPlaceholder = computed(() => {
	switch (activeOrderTab.value) {
		case 'xuong_sx':
			return 'Tìm nhanh đơn hàng, khách, màng ghép...';
		case 'ngcs':
			return 'Tìm nhanh đơn hàng, khách, túi có sẵn...';
		case 'mua_ngoai':
			return 'Tìm nhanh đơn hàng, khách, quy cách mua ngoài...';
		default:
			return 'Tìm nhanh đơn hàng, khách, mặt hàng...';
	}
});

watch(activeOrderTab, () => {
	nextTick(() => {
		const containers = document.querySelectorAll('.table-container');
		containers.forEach((el) => {
			el.scrollTop = 0;
			el.scrollLeft = 0;
		});
	});
});

const masterItems = ref([]);
const selectedOrderId = ref('');
const showOrderDetail = ref(false);
const showCreateOrderModal = ref(false);

const selectedOrder = computed(() => {
	return orders.value.find((o) => o.name === selectedOrderId.value) || null;
});

const ngcsOrders = computed(() =>
	orders.value.filter((o) => o.order_tab === 'ngcs' || o.product_group === 'Túi NGCS')
);
const xuongSxOrders = computed(() =>
	orders.value.filter(
		(o) =>
			o.order_tab === 'xuong_sx' ||
			(!o.order_tab && (!o.product_group || o.product_group === 'Túi màng ghép') && o.payment_type !== 'Trả sau')
	)
);
const muaNgoaiOrders = computed(() =>
	orders.value.filter(
		(o) =>
			o.order_tab === 'mua_ngoai' ||
			o.product_group === 'Túi màng đơn' ||
			o.product_group === 'Cuộn màng ghép' ||
			o.payment_type === 'Trả sau'
	)
);

const currentTabOrders = computed(() => {
	if (activeOrderTab.value === 'ngcs') return ngcsOrders.value;
	if (activeOrderTab.value === 'xuong_sx') return xuongSxOrders.value;
	return muaNgoaiOrders.value;
});

const filteredTabOrders = computed(() => {
	let list = currentTabOrders.value;
	const q = orderSearchQuery.value.trim().toLowerCase();
	if (!q) return list;
	return list.filter((o) => {
		const name = (o.name || '').toLowerCase();
		const cust = (o.customer_alias || o.alias || o.customer || o.customer_name || '').toLowerCase();
		const item = (o.custom_alias || o.item_name || '').toLowerCase();
		return name.includes(q) || cust.includes(q) || item.includes(q);
	});
});

function depositColorClass(o) {
	const req = o.required_deposit || (o.grand_total * 0.5);
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

function formatNumber(val) {
	if (val == null || val === '') return '0';
	return Number(val).toLocaleString('vi-VN');
}

function formatDateShort(val) {
	if (!val) return '—';
	const parts = String(val).split('-');
	if (parts.length === 3) {
		return `${parts[2]}/${parts[1]}`;
	}
	return val;
}

function formatCurrency(val) {
	if (val == null || val === '') return '0 đ';
	if (typeof val === 'string' && isNaN(Number(val))) return val;
	return Number(val).toLocaleString('vi-VN') + ' đ';
}

async function loadOrders() {
	loadingOrders.value = true;
	const data = await api('list_orders');
	if (Array.isArray(data)) {
		orders.value = data;
	} else {
		orders.value = [];
	}
	ordersCount.value = orders.value.length;
	loadingOrders.value = false;
}

async function loadMasterItems() {
	try {
		const data = await api('vanphat_portal.api.item.get_list', {}, { get: true });
		if (Array.isArray(data)) {
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
	const idx = orders.value.findIndex((o) => o.name === order.name);
	if (idx !== -1) {
		orders.value[idx].order_state = 'Đã giao hàng';
		orders.value[idx].outstanding_amount = 0;
		orders.value[idx].advance_paid = orders.value[idx].grand_total;
	}
	showOrderDetail.value = false;
}

onMounted(async () => {
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

defineExpose({
	loadOrders,
	openOrderDetail,
	openCreateOrderModal,
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
