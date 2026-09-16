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
						id="order-search-input"
						name="order_search"
						type="text"
						v-model="orderSearchQuery"
						:placeholder="currentOrderSearchPlaceholder"
						aria-label="Tìm kiếm đơn hàng"
						class="catalog-search-input"
					/>
					<button
						v-if="orderSearchQuery"
						type="button"
						class="btn-clear-search"
						title="Xóa tìm kiếm"
						aria-label="Xóa tìm kiếm"
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

		<!-- S6: đổi thead/tbody theo tab là đủ — không :key remount (giữ scroll/focus, hợp keep-alive) -->
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
						v-for="o in orders"
						:key="o.name"
						class="table-row cursor-pointer"
						tabindex="0"
						role="button"
						:aria-label="'Mở chi tiết đơn ' + o.name"
						@click="openOrderDetail(o)"
						@keydown.enter="openOrderDetail(o)"
						@keydown.space.prevent="openOrderDetail(o)"
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
							<span class="font-bold text-sm" :class="orderStatusColorClass(o)">
								{{ orderStatusText(o) }}
							</span>
						</td>
					</tr>
					<TableFiller
						:shown="orders.length"
						:page-size="pageSize"
						:colspan="7"
						prefix="order"
					/>
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

		<!-- Phân trang tối giản (BasePagination: số căn giữa, không khung) -->
		<div class="cockpit-pagination-bar">
			<BasePagination
				:page="currentPage"
				:total-pages="totalPages"
				:loading="loadingOrders"
				@prev="prevPage"
				@next="nextPage"
				@goto="gotoPage"
			/>
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
			<template #fallback>
				<div class="cockpit-empty-state" aria-busy="true">
					<span class="empty-msg">Đang tải chi tiết...</span>
				</div>
			</template>
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
			<template #fallback>
				<div class="cockpit-empty-state" aria-busy="true">
					<span class="empty-msg">Đang tải form...</span>
				</div>
			</template>
		</Suspense>
	</div>
</template>

<script setup>
import { onMounted, onUnmounted, defineAsyncComponent } from 'vue';
import { useRoute } from 'vue-router';
// S8: drawers/modals nặng async — chunk riêng, render khi mở
const DrawerOrderDetail = defineAsyncComponent(() => import('../components/DrawerOrderDetail.vue'));
const ModalCreateOrder = defineAsyncComponent(() => import('../components/ModalCreateOrder.vue'));
import BasePagination from '../components/BasePagination.vue';
import TableFiller from '../components/TableFiller.vue';
import { useCockpitFormat } from '../composables/useCockpitFormat';
import { useOrdersList } from '../composables/useOrdersList';

const route = useRoute();
// S7c: formatter dùng chung (xóa 2 bản copy-paste)
// S8a/b: status helpers dùng chung từ useCockpitFormat (rút view dưới 500L).
// Task 7: SLA NCC cũng dùng chung; list state + loaders trong useOrdersList.
const { formatCurrency, formatNumber, depositColorClass, orderStatusText, orderStatusColorClass, formatDateShort, supplierSlaColorClass, supplierSlaText } = useCockpitFormat();

// Task 7: view chỉ còn composition + render — logic list trong composable.
const {
	orders,
	loadingOrders,
	activeOrderTab,
	orderSearchQuery,
	currentPage,
	pageSize,
	totalPages,
	tabCounts,
	masterItems,
	selectedOrderId,
	showOrderDetail,
	showCreateOrderModal,
	selectedOrder,
	currentOrderSearchPlaceholder,
	prevPage,
	nextPage,
	gotoPage,
	handleKeyDown,
	loadOrders,
	loadMasterItems,
	openOrderDetail,
	openCreateOrderModal,
	handleNewOrderCreated,
	onOrderUpdated,
	onOrderDelivery,
	applyTabFromQuery,
	cleanup,
} = useOrdersList();

onMounted(async () => {
	window.addEventListener('keydown', handleKeyDown);

	// S5: set tab từ query TRƯỚC khi load — deep-link ?tab= fetch 1 lần duy nhất.
	const query = route?.query || {};
	const urlParams = new URLSearchParams(window.location.search);

	applyTabFromQuery(query.tab || urlParams.get('tab'));

	await Promise.all([loadOrders(), loadMasterItems()]);

	const orderParam = query.order || urlParams.get('order');
	if (orderParam) {
		// S7: validate tồn tại trong list đã load (như CatalogView) — lạ thì không mở drawer rỗng.
		const found = orders.value.find((o) => o.name === orderParam);
		if (found) {
			selectedOrderId.value = found.name;
			showOrderDetail.value = true;
		}
	}

	const modalParam = query.modal || urlParams.get('modal');
	if (modalParam === 'create') {
		showCreateOrderModal.value = true;
	}
});

onUnmounted(() => {
	cleanup();
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
