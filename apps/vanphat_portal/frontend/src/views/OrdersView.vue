<template>
	<div class="orders-view-wrapper">
		<header class="page-head">
			<h2 class="page-title">Đơn hàng</h2>
			<button
				type="button"
				class="btn-new-quote"
				@click="openCreateOrderModal"
			>
				+ Tạo đơn hàng
			</button>
		</header>

		<!-- Sub-navigation 3 Tabs -->
		<div class="order-tabs-bar">
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

		<div class="table-container">
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
						v-for="o in currentTabOrders"
						:key="o.name"
						class="table-row cursor-pointer"
						@click="openOrderDetail(o)"
					>
						<td class="text-secondary font-mono">{{ formatDateShort(o.transaction_date) }}</td>
						<td>
							<div class="font-bold text-white">{{ o.customer_alias || o.alias || o.customer || o.customer_name }}</div>
						</td>
						<td class="truncate" :title="o.item_name">
							<span class="font-medium text-white">{{ o.custom_alias || o.item_name || '—' }}</span>
						</td>
						<td class="text-right text-num">
							<span>{{ formatNumber(o.qty) }}</span>
							<span class="text-xs text-secondary" style="margin-left: 4px;">{{ o.uom || o.stock_uom || 'Túi' }}</span>
						</td>
						<td class="text-right">
							<div v-if="o.payment_type === 'Trả sau'" class="text-xs text-secondary font-semibold">
								Trả sau
							</div>
							<div v-else class="deposit-mini-cell">
								<div class="text-num font-bold" :class="o.advance_paid >= (o.required_deposit || o.grand_total * 0.5) ? 'text-emerald' : (o.advance_paid > 0 ? 'text-amber' : 'text-secondary')">
									{{ formatCurrency(o.advance_paid) }}
								</div>
								<div class="mini-bar-track">
									<div
										class="mini-bar-fill"
										:style="{ width: Math.min(100, Math.round((o.advance_paid / (o.required_deposit || (o.grand_total * 0.5))) * 100)) + '%' }"
										:class="o.advance_paid >= (o.required_deposit || (o.grand_total * 0.5)) ? 'bg-emerald' : 'bg-amber'"
									></div>
								</div>
							</div>
						</td>

						<!-- Cột theo Tab: Xưởng SX -->
						<td v-if="activeOrderTab === 'xuong_sx'" class="text-center">
							<div class="factory-status-cell">
								<span class="badge-mat" :class="o.materials_status === 'Đủ màng' ? 'mat-ready' : 'mat-waiting'">
									{{ o.materials_status || 'Chờ màng' }}
								</span>
								<span class="badge-stage">
									{{ o.factory_stage || 'Chờ cọc' }}
								</span>
							</div>
						</td>

						<!-- Cột theo Tab: NGCS In Lụa -->
						<td v-else-if="activeOrderTab === 'ngcs'" class="text-center">
							<div v-if="o.supplier_name" class="sla-cell">
								<span class="sla-supplier">{{ o.supplier_name }}</span>
								<span class="sla-badge" :class="supplierSlaBadge(o.supplier_eta_days).cls">
									{{ supplierSlaBadge(o.supplier_eta_days).text }}
								</span>
							</div>
							<span v-else class="text-secondary text-xs">—</span>
						</td>

						<!-- Cột theo Tab: Mua Ngoài -->
						<td v-else class="text-center">
							<div v-if="o.supplier_name" class="sla-cell">
								<span class="sla-supplier">{{ o.supplier_name }}</span>
								<span class="sla-badge" :class="supplierSlaBadge(o.supplier_eta_days).cls">
									{{ supplierSlaBadge(o.supplier_eta_days).text }}
								</span>
							</div>
							<span v-else class="text-secondary text-xs">—</span>
						</td>

						<!-- Trạng thái chung -->
						<td class="text-center">
							<span class="status-badge" :class="orderStatusClass(o)">
								{{ orderStatusText(o) }}
							</span>
						</td>
					</tr>
					<tr v-if="currentTabOrders.length === 0">
						<td colspan="7" class="empty-cell">
							{{ loadingOrders ? 'Đang tải...' : 'Không có dữ liệu trong tab này' }}
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
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import DrawerOrderDetail from '../components/DrawerOrderDetail.vue';
import ModalCreateOrder from '../components/ModalCreateOrder.vue';
import { INITIAL_ORDERS, MASTER_CATALOG_ITEMS } from '../data/mockData';
import { api } from '../composables/useSession';
import { usePortalCounts } from '../composables/usePortalCounts';

const route = useRoute();
const { ordersCount } = usePortalCounts();

const orders = ref([]);
const loadingOrders = ref(false);
const activeOrderTab = ref('xuong_sx');

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

function supplierSlaBadge(days) {
	if (days == null) return { text: '—', cls: 'sla-none' };
	if (days < 0) return { text: 'Trễ ' + Math.abs(days) + ' ngày', cls: 'sla-overdue' };
	if (days === 0) return { text: 'Hôm nay giao', cls: 'sla-today' };
	return { text: 'Còn ' + days + ' ngày', cls: 'sla-ontime' };
}

function orderStatusText(o) {
	if (o.order_status_label) return o.order_status_label;
	if (o.is_hold || o.order_state?.includes('HOLD')) return 'HOLD';
	if (o.payment_type === 'Trả sau' && o.docstatus === 1) return 'Trả sau';
	if (o.docstatus === 1) return 'Đã duyệt';
	return 'Chờ cọc';
}

function orderStatusClass(o) {
	if (o.order_status_class) return o.order_status_class;
	if (o.is_hold || o.order_state?.includes('HOLD')) return 'status-hold';
	if (o.docstatus === 1 || o.order_state?.includes('Chính thức')) return 'status-ordered';
	return 'status-draft';
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
	if (Array.isArray(data) && data.length > 0) {
		orders.value = data;
	} else {
		orders.value = [...INITIAL_ORDERS];
	}
	ordersCount.value = orders.value.length;
	loadingOrders.value = false;
}

async function loadMasterItems() {
	try {
		const data = await api('vanphat_portal.api.item.get_list', {}, { get: true });
		if (Array.isArray(data) && data.length > 0) {
			masterItems.value = data;
		} else if (masterItems.value.length === 0) {
			masterItems.value = [...(MASTER_CATALOG_ITEMS || [])];
		}
	} catch (err) {
		if (masterItems.value.length === 0) {
			masterItems.value = [...(MASTER_CATALOG_ITEMS || [])];
		}
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

function handleNewOrderCreated(newOrder) {
	orders.value.unshift(newOrder);
	activeOrderTab.value = newOrder.order_tab || 'xuong_sx';
	selectedOrderId.value = newOrder.name;
	showOrderDetail.value = true;
	ordersCount.value = orders.value.length;
}

function onOrderUpdated(updatedOrder) {
	const idx = orders.value.findIndex((o) => o.name === updatedOrder.name);
	if (idx !== -1) {
		orders.value[idx] = { ...updatedOrder };
	}
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

.order-tabs-bar {
	display: flex;
	gap: 6px;
	margin-bottom: 12px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.08);
	padding-bottom: 10px;
	flex-shrink: 0;
}

.order-tab-btn {
	display: inline-flex;
	align-items: center;
	gap: 7px;
	padding: 6px 13px;
	border-radius: 8px;
	border: 1px solid transparent;
	background: transparent;
	color: #94a3b8;
	font-size: 13.5px;
	font-weight: 600;
	cursor: pointer;
	white-space: nowrap !important;
	flex-shrink: 0;
	transition: all 0.15s ease;
}

.order-tab-btn span {
	white-space: nowrap !important;
}

.order-tab-btn:hover {
	background: rgba(255, 255, 255, 0.04);
	color: #f1f5f9;
}

.order-tab-btn.active {
	background: #161b22;
	border-color: #3a424e;
	color: #4ea1e0;
	font-weight: 700;
}

.tab-badge {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	min-width: 20px;
	height: 19px;
	padding: 0 6px;
	border-radius: 10px;
	font-size: 12.5px;
	font-weight: 700;
	background: rgba(255, 255, 255, 0.08);
	color: #94a3b8;
	font-variant-numeric: tabular-nums;
}

.order-tab-btn.active .tab-badge {
	background: rgba(78, 161, 224, 0.2);
	color: #4ea1e0;
}

.sla-cell {
	display: inline-flex;
	flex-direction: column;
	align-items: center;
	gap: 2px;
}

.sla-supplier {
	font-size: 10.5px;
	font-weight: 700;
	color: #cbd5e1;
	letter-spacing: 0.3px;
}

.sla-badge {
	font-size: 10.5px;
	font-weight: 700;
	padding: 2px 7px;
	border-radius: 4px;
	white-space: nowrap;
}

.sla-ontime {
	background: rgba(148, 163, 184, 0.15);
	color: #94a3b8;
	border: 1px solid rgba(148, 163, 184, 0.3);
}

.sla-today {
	background: rgba(245, 158, 11, 0.18);
	color: #fbbf24;
	border: 1px solid rgba(245, 158, 11, 0.4);
}

.sla-overdue {
	background: rgba(239, 68, 68, 0.25);
	color: #fca5a5;
	border: 1px solid rgba(239, 68, 68, 0.5);
	animation: pulse-red 2s infinite;
}

@keyframes pulse-red {
	0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
	50% { box-shadow: 0 0 0 4px rgba(239, 68, 68, 0); }
}

.factory-status-cell {
	display: inline-flex;
	align-items: center;
	gap: 6px;
	justify-content: center;
}

.badge-mat {
	font-size: 10.5px;
	font-weight: 700;
	padding: 2px 6px;
	border-radius: 4px;
}

.mat-ready {
	background: rgba(52, 211, 153, 0.15);
	color: #34d399;
	border: 1px solid rgba(52, 211, 153, 0.3);
}

.mat-waiting {
	background: rgba(245, 158, 11, 0.15);
	color: #fbbf24;
	border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-stage {
	font-size: 11px;
	font-weight: 600;
	color: #93c5fd;
	background: rgba(78, 161, 224, 0.12);
	border: 1px solid rgba(78, 161, 224, 0.3);
	padding: 2px 6px;
	border-radius: 4px;
}

.status-hold {
	background: rgba(239, 68, 68, 0.2);
	color: #f87171;
	border: 1px solid rgba(239, 68, 68, 0.4);
}

.text-emerald {
	color: #34d399;
}

.text-amber {
	color: #f59e0b;
}

.font-mono {
	font-family: inherit;
	font-variant-numeric: tabular-nums;
	font-feature-settings: "tnum";
}

.deposit-mini-cell {
	display: flex;
	flex-direction: column;
	align-items: flex-end;
	gap: 3px;
}

.mini-bar-track {
	width: 100%;
	max-width: 80px;
	height: 3px;
	background: rgba(255, 255, 255, 0.08);
	border-radius: 2px;
	overflow: hidden;
}

.mini-bar-fill {
	height: 100%;
	transition: width 0.3s ease;
}

.bg-emerald {
	background-color: #34d399;
}

.bg-amber {
	background-color: #f59e0b;
}

.empty-cell {
	text-align: center;
	padding: 40px 0;
	color: #9da7b5;
}
</style>
