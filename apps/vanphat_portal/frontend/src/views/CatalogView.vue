<template>
	<div class="catalog-view-wrapper">
		<!-- Header Danh Mục Thống Nhất: 6 Tab Buồng Lái Chuẩn SSOT + Sub-filters + Search -->
		<header class="page-head catalog-header-cockpit">
			<div class="order-tabs-bar catalog-tabs-bar">
				<button
					type="button"
					class="order-tab-btn"
					:class="{ active: activeCatalogTab === 'sp' }"
					@click="switchCatalogTab('sp')"
				>
					<span>Sản phẩm</span>
					<span v-if="activeCatalogTab === 'sp'" class="tab-badge">{{ currentTotalRecords }}</span>
				</button>
				<button
					type="button"
					class="order-tab-btn"
					:class="{ active: activeCatalogTab === 'nvl' }"
					@click="switchCatalogTab('nvl')"
				>
					<span>Nguyên vật liệu</span>
					<span v-if="activeCatalogTab === 'nvl'" class="tab-badge">{{ currentTotalRecords }}</span>
				</button>
				<button
					type="button"
					class="order-tab-btn"
					:class="{ active: activeCatalogTab === 'truc' }"
					@click="switchCatalogTab('truc')"
				>
					<span>Trục in</span>
					<span v-if="activeCatalogTab === 'truc'" class="tab-badge">{{ currentTotalRecords }}</span>
				</button>
				<button
					type="button"
					class="order-tab-btn"
					:class="{ active: activeCatalogTab === 'kh' }"
					@click="switchCatalogTab('kh')"
				>
					<span>Khách hàng</span>
					<span class="tab-badge">{{ customers.length }}</span>
				</button>
				<button
					type="button"
					class="order-tab-btn"
					:class="{ active: activeCatalogTab === 'ncc' }"
					@click="switchCatalogTab('ncc')"
				>
					<span>Nhà cung cấp</span>
					<span class="tab-badge">{{ suppliers.length }}</span>
				</button>
				<button
					type="button"
					class="order-tab-btn"
					:class="{ active: activeCatalogTab === 'user' }"
					@click="switchCatalogTab('user')"
				>
					<span>Người dùng</span>
					<span class="tab-badge">{{ users.length }}</span>
				</button>
			</div>

			<!-- Thanh Tìm Kiếm Tức Thời Trực Diện Cùng Hàng Header Cockpit -->
			<div class="catalog-search-cockpit-wrap">
				<div class="search-input-wrap">
					<svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<circle cx="11" cy="11" r="8"></circle>
						<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
					</svg>
					<input
						id="catalog-search-input"
						name="catalog_search"
						type="text"
						class="catalog-search-input"
						v-model="catalogSearchInput"
						:placeholder="currentCatalogSearchPlaceholder"
						aria-label="Tìm kiếm danh mục"
					/>
					<button
						v-if="catalogSearchInput"
						type="button"
						class="btn-clear-search"
						title="Xóa tìm kiếm"
						@click="catalogSearchInput = ''"
					>✕</button>
				</div>
			</div>

			<!-- Nút Hành Động Thêm Mới Chuẩn Cockpit -->
			<button
				type="button"
				class="btn-new-quote whitespace-nowrap flex-shrink-0"
				@click="onAddNew"
			>
				{{ currentAddButtonLabel }}
			</button>
		</header>

		<!-- Bảng Mặt hàng: Sản phẩm, NVL, Trục in -->
		<div
			v-if="activeCatalogTab === 'sp' || activeCatalogTab === 'nvl' || activeCatalogTab === 'truc'"
			:key="activeCatalogTab"
			ref="tableContainerRef"
			class="table-container"
		>
			<table class="data-table">
				<thead>
					<tr>
						<th style="width: 35%;">Tên gọi quen</th>
						<th style="width: 21%;">Chất liệu</th>
						<th style="width: 20%;">Kích thước (R x D x Dày)</th>
						<th style="width: 11%; text-align: center;">Đáy</th>
						<th style="width: 7%; text-align: center;">ĐVT</th>
					</tr>
				</thead>
				<tbody>
					<tr
						v-for="it in filteredMasterItems"
						:key="it.item_code"
						class="table-row cursor-pointer"
						@click="openItemDetail(it)"
					>
						<!-- Tên gọi quen (mã nội bộ + tên pháp lý chỉ tooltip; mã biến thể KH chỉ trong drawer) -->
						<td>
							<div class="font-semibold text-white leading-tight text-[15px]" :title="(it.item_name || '') + ' [' + (it.item_code || '') + ']'">
								{{ it.custom_alias || it.item_name || '—' }}
							</div>
						</td>

						<!-- Chất liệu (Đơn dòng tinh gọn) -->
						<td>
							<div class="text-sm text-amber font-mono font-semibold truncate" :title="it.custom_structure_layers || it.description || '—'">
								{{ it.custom_structure_layers || it.description || '—' }}
							</div>
						</td>

						<!-- Kích thước (R x D x Dày) -->
						<td class="text-sm font-mono">
							<span class="text-white font-medium">{{ getItemDimensionsText(it) }}</span>
						</td>

						<!-- Đáy (Tách riêng cột) -->
						<td class="text-center font-mono text-sm">
							<span v-if="getItemGussetText(it)" class="text-amber font-semibold">
								{{ getItemGussetText(it) }}
							</span>
							<span v-else class="text-secondary/40">—</span>
						</td>

						<!-- ĐVT -->
						<td class="text-center font-mono text-sm text-secondary">
							{{ it.stock_uom || 'Túi' }}
						</td>
					</tr>
					<tr
						v-for="i in (filteredMasterItems.length > 0 ? Math.max(0, pageSize - filteredMasterItems.length) : 0)"
						:key="'it-filler-' + i"
						class="filler-row"
						aria-hidden="true"
					>
						<td colspan="5">&nbsp;</td>
					</tr>
					<tr v-if="filteredMasterItems.length === 0">
						<td colspan="5" class="empty-cell">
							<div v-if="loadingMasterItems" class="cockpit-empty-state">
								<span class="empty-msg">Đang tải danh mục từ ERPNext...</span>
							</div>
							<div v-else-if="itemSearchQuery" class="cockpit-empty-state">
								<span class="empty-msg">Không tìm thấy mặt hàng khớp với "{{ itemSearchQuery }}" trong tab {{ currentTabLabel }}</span>
								<button type="button" class="btn-empty-action" @click="itemSearchQuery = ''">
									✕ Xóa tìm kiếm
								</button>
							</div>
							<div v-else class="cockpit-empty-state">
								<span class="empty-msg">Chưa có dữ liệu trong mục {{ currentTabLabel }}</span>
								<button type="button" class="btn-empty-action btn-empty-primary" @click="onAddNew">
									{{ currentAddButtonLabel }}
								</button>
							</div>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Bảng Khách hàng -->
		<div
			v-else-if="activeCatalogTab === 'kh'"
			:key="activeCatalogTab"
			ref="tableContainerRef"
			class="table-container"
		>
			<table class="data-table">
				<thead>
					<tr>
						<th style="width: 20%;">Tên gọi tắt</th>
						<th style="width: 46%;">Tên pháp nhân</th>
						<th style="width: 16%;">Mã số thuế</th>
						<th style="width: 18%;">Thanh toán</th>
					</tr>
				</thead>
				<tbody>
					<tr
						v-for="c in paginatedCustomers"
						:key="c.name"
						class="table-row cursor-pointer"
						@click="openCustomerDetail(c)"
					>
						<td class="whitespace-nowrap">
							<div class="font-semibold text-white leading-tight text-[15px]" :title="'Mã KH: ' + c.name">
								{{ c.alias || c.customer_name }}
							</div>
						</td>
						<td class="whitespace-nowrap">
							<div class="text-sm text-secondary leading-tight truncate" :title="c.customer_name">
								{{ c.customer_name }}
							</div>
						</td>
						<td class="font-mono text-sm text-slate-300 tabular-nums whitespace-nowrap">
							{{ c.tax_id || '—' }}
						</td>
						<td class="whitespace-nowrap">
							<span v-if="c.payment_terms && (c.payment_terms.includes('30 ngày') || c.payment_terms.toLowerCase().includes('gối đầu'))" class="badge-payment-amber">
								Gối đầu 30 ngày
							</span>
							<span v-else-if="c.payment_terms && c.payment_terms.includes('50%')" class="badge-payment-blue">
								Cọc 50%
							</span>
							<span v-else-if="c.payment_terms" class="badge-payment-blue">
								{{ c.payment_terms }}
							</span>
							<span v-else class="text-secondary/60 text-xs">—</span>
						</td>
					</tr>
					<tr
						v-for="i in (paginatedCustomers.length > 0 ? Math.max(0, pageSize - paginatedCustomers.length) : 0)"
						:key="'kh-filler-' + i"
						class="filler-row"
						aria-hidden="true"
					>
						<td colspan="4">&nbsp;</td>
					</tr>
					<tr v-if="filteredCustomers.length === 0">
						<td colspan="4" class="empty-cell">
							<div v-if="loadingCustomers" class="cockpit-empty-state">
								<span class="empty-msg">Đang tải khách hàng từ ERPNext...</span>
							</div>
							<div v-else-if="customerSearchQuery" class="cockpit-empty-state">
								<span class="empty-msg">Không tìm thấy khách hàng khớp với "{{ customerSearchQuery }}"</span>
								<button type="button" class="btn-empty-action" @click="customerSearchQuery = ''">
									✕ Xóa tìm kiếm
								</button>
							</div>
							<div v-else class="cockpit-empty-state">
								<span class="empty-msg">Chưa có khách hàng nào trên hệ thống</span>
								<button type="button" class="btn-empty-action btn-empty-primary" @click="onAddNew">
									+ Thêm khách hàng
								</button>
							</div>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Bảng Nhà cung cấp -->
		<div
			v-else-if="activeCatalogTab === 'ncc'"
			:key="activeCatalogTab"
			ref="tableContainerRef"
			class="table-container"
		>
			<table class="data-table">
				<thead>
					<tr>
						<th style="width: 20%;">Tên gọi tắt</th>
						<th style="width: 46%;">Tên pháp nhân</th>
						<th style="width: 16%;">Mã số thuế</th>
						<th style="width: 18%;">Thanh toán</th>
					</tr>
				</thead>
				<tbody>
					<tr
						v-for="s in paginatedSuppliers"
						:key="s.name"
						class="table-row cursor-pointer"
						@click="openSupplierDetail(s)"
					>
						<td class="whitespace-nowrap">
							<div class="font-semibold text-white leading-tight text-[15px]" :title="'Mã NCC: ' + s.name + (s.supplier_group ? ' • Nhóm: ' + s.supplier_group : '')">
								{{ s.alias || s.supplier_name }}
							</div>
						</td>
						<td class="whitespace-nowrap">
							<div class="text-sm text-secondary leading-tight truncate" :title="s.supplier_name">
								{{ s.supplier_name }}
							</div>
						</td>
						<td class="font-mono text-sm text-slate-300 tabular-nums whitespace-nowrap">
							{{ s.tax_id || '—' }}
						</td>
						<td class="whitespace-nowrap">
							<span v-if="s.payment_terms && (s.payment_terms.includes('30 ngày') || s.payment_terms.toLowerCase().includes('gối đầu'))" class="badge-payment-amber">
								Gối đầu 30 ngày
							</span>
							<span v-else-if="s.payment_terms && (s.payment_terms.includes('nghiệm thu') || s.payment_terms.includes('giao hàng'))" class="badge-payment-emerald">
								{{ s.payment_terms.replace('Thanh toán ', '') }}
							</span>
							<span v-else-if="s.payment_terms" class="badge-payment-blue">
								{{ s.payment_terms }}
							</span>
							<span v-else class="text-secondary/60 text-xs">—</span>
						</td>
					</tr>
					<tr
						v-for="i in (paginatedSuppliers.length > 0 ? Math.max(0, pageSize - paginatedSuppliers.length) : 0)"
						:key="'ncc-filler-' + i"
						class="filler-row"
						aria-hidden="true"
					>
						<td colspan="4">&nbsp;</td>
					</tr>
					<tr v-if="filteredSuppliers.length === 0">
						<td colspan="4" class="empty-cell">
							<div v-if="loadingSuppliers" class="cockpit-empty-state">
								<span class="empty-msg">Đang tải nhà cung cấp từ ERPNext...</span>
							</div>
							<div v-else-if="supplierSearchQuery" class="cockpit-empty-state">
								<span class="empty-msg">Không tìm thấy nhà cung cấp khớp với "{{ supplierSearchQuery }}"</span>
								<button type="button" class="btn-empty-action" @click="supplierSearchQuery = ''">
									✕ Xóa tìm kiếm
								</button>
							</div>
							<div v-else class="cockpit-empty-state">
								<span class="empty-msg">Chưa có nhà cung cấp nào trên hệ thống</span>
								<button type="button" class="btn-empty-action btn-empty-primary" @click="onAddNew">
									+ Thêm NCC
								</button>
							</div>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Bảng Người dùng -->
		<div
			v-else-if="activeCatalogTab === 'user'"
			:key="activeCatalogTab"
			ref="tableContainerRef"
			class="table-container"
		>
			<table class="data-table">
				<thead>
					<tr>
						<th style="width: 22%;">SĐT đăng nhập</th>
						<th style="width: 24%;">Họ và tên</th>
						<th style="width: 22%;">Phòng ban</th>
						<th style="width: 20%;">Vai trò ERPNext</th>
						<th style="width: 12%; text-align: center;">Trạng thái</th>
					</tr>
				</thead>
				<tbody>
					<tr
						v-for="u in paginatedUsers"
						:key="u.name"
						class="table-row cursor-pointer"
						@click="openUserDetail(u)"
					>
						<td class="whitespace-nowrap">
							<span class="font-mono font-bold text-purple-400 text-[14.5px] tabular-nums" :title="u.email || ''">
								{{ u.mobile_no || u.email }}
							</span>
						</td>
						<td class="whitespace-nowrap">
							<div class="font-semibold text-white leading-tight text-[15px]">
								{{ u.full_name }}
							</div>
						</td>
						<td class="text-sm text-slate-300 whitespace-nowrap">
							{{ u.department || 'Ban Giám Đốc' }}
						</td>
						<td class="whitespace-nowrap">
							<span class="badge-role-user font-mono text-xs" :title="u.designation || ''">
								{{ u.role_profile_name || 'System User' }}
							</span>
						</td>
						<td class="text-center whitespace-nowrap">
							<span v-if="u.enabled" class="font-bold text-[14px] text-emerald">
								Hoạt động
							</span>
							<span v-else class="font-bold text-[14px] text-secondary">
								Đã khóa
							</span>
						</td>
					</tr>
					<tr
						v-for="i in (paginatedUsers.length > 0 ? Math.max(0, pageSize - paginatedUsers.length) : 0)"
						:key="'user-filler-' + i"
						class="filler-row"
						aria-hidden="true"
					>
						<td colspan="5">&nbsp;</td>
					</tr>
					<tr v-if="filteredUsers.length === 0">
						<td colspan="5" class="empty-cell">
							<div v-if="loadingUsers" class="cockpit-empty-state">
								<span class="empty-msg">Đang tải người dùng từ ERPNext...</span>
							</div>
							<div v-else-if="userSearchQuery" class="cockpit-empty-state">
								<span class="empty-msg">Không tìm thấy người dùng khớp với "{{ userSearchQuery }}"</span>
								<button type="button" class="btn-empty-action" @click="userSearchQuery = ''">
									✕ Xóa tìm kiếm
								</button>
							</div>
							<div v-else class="cockpit-empty-state">
								<span class="empty-msg">Chưa có người dùng nào trên hệ thống</span>
								<button type="button" class="btn-empty-action btn-empty-primary" @click="onAddNew">
									+ Thêm người dùng
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
				<span class="text-white font-bold">{{ currentTotalRecords }}</span>
				<span>{{ currentTabLabel.toLowerCase() }}</span>
			</div>
			<div class="cockpit-pagination-right">
				<button
					type="button"
					class="btn-page-nav"
					:disabled="currentPage <= 1 || loadingCurrentTab"
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
					:disabled="currentPage >= totalPages || loadingCurrentTab"
					title="Trang sau (Phím ])"
					@click="nextPage"
				>
					›
				</button>
			</div>
		</div>

		<!-- Slide-over Drawers (S8: async chunk + Suspense, chỉ mount khi mở) -->
		<Suspense v-if="showItemDrawer">
			<DrawerItemDetail
				:is-open="showItemDrawer"
				:open="showItemDrawer"
				:item="selectedMasterItem"
				:bom="selectedMasterBom"
				:loading="loadingItemDetail"
				@close="showItemDrawer = false"
			/>
		</Suspense>

		<Suspense v-if="showCustomerDrawer">
			<DrawerCustomerDetail
				:is-open="showCustomerDrawer"
				:open="showCustomerDrawer"
				:customer="selectedCustomer"
				:master-items="masterItems"
				@close="showCustomerDrawer = false"
			/>
		</Suspense>

		<Suspense v-if="showSupplierDrawer">
			<DrawerSupplierDetail
				:is-open="showSupplierDrawer"
				:open="showSupplierDrawer"
				:supplier="selectedSupplier"
				@close="showSupplierDrawer = false"
			/>
		</Suspense>

		<Suspense v-if="showUserDrawer">
			<DrawerUserDetail
				:is-open="showUserDrawer"
				:open="showUserDrawer"
				:user="selectedUser"
				@close="showUserDrawer = false"
			/>
		</Suspense>
	</div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, defineAsyncComponent } from 'vue';
import { useRoute } from 'vue-router';
// S8: 4 drawers chi tiết async — chunk riêng, chỉ mount khi mở
const DrawerItemDetail = defineAsyncComponent(() => import('../components/DrawerItemDetail.vue'));
const DrawerCustomerDetail = defineAsyncComponent(() => import('../components/DrawerCustomerDetail.vue'));
const DrawerSupplierDetail = defineAsyncComponent(() => import('../components/DrawerSupplierDetail.vue'));
const DrawerUserDetail = defineAsyncComponent(() => import('../components/DrawerUserDetail.vue'));
import { useCockpitFormat } from '../composables/useCockpitFormat';
import { useCatalogData } from '../composables/useCatalogData';
import { toast } from '../composables/useToast';

const route = useRoute();
// S7c: formatter dùng chung (giữ formatItemRate riêng vì empty '—' khác chuẩn)
const { formatCurrency } = useCockpitFormat();
const emit = defineEmits(['add-new']);

// S7d: master loads + filters + pagination tách composable
const catalog = useCatalogData();
const {
	masterItems,
	loadingMasterItems,
	activeCatalogTab,
	activeItemTab,
	itemSearchQuery,
	currentPage,
	pageSize,
	totalMasterItems,
	loadingCurrentTab,
	currentTotalRecords,
	totalPages,
	startRecord,
	endRecord,
	refreshCurrentTabData,
	prevPage,
	nextPage,
	handleKeyDown,
	showItemDrawer,
	selectedMasterItem,
	selectedMasterBom,
	loadingItemDetail,
	customers,
	loadingCustomers,
	customerSearchQuery,
	selectedCustomer,
	showCustomerDrawer,
	suppliers,
	loadingSuppliers,
	supplierSearchQuery,
	selectedSupplier,
	showSupplierDrawer,
	users,
	loadingUsers,
	userSearchQuery,
	selectedUser,
	showUserDrawer,
	syncTotalCount,
	currentCatalogSearchPlaceholder,
	currentAddButtonLabel,
	catalogSearchInput,
	switchCatalogTab,
	switchItemTab,
	currentTabMasterItems,
	currentTabLabel,
	filteredMasterItems,
	filteredCustomers,
	filteredSuppliers,
	filteredUsers,
	paginatedCustomers,
	paginatedSuppliers,
	paginatedUsers,
	loadMasterItems,
	openItemDetail,
	loadCustomers,
	openCustomerDetail,
	loadSuppliers,
	openSupplierDetail,
	loadUsers,
	openUserDetail,
	loadInitialTabData,
} = catalog;

function onAddNew() {
	emit('add-new', catalog.handleAddNew());
	toast.info(`Dữ liệu ${currentTabLabel.value || 'danh mục'} được quản lý và tạo mới trực tiếp từ ERPNext Desk.`);
}

// Khôi phục từ bản pre-S7d (commit 1356141^): 2 helpers này bị rơi khi tách
// composable, khiến template vỡ render (TypeError ... is not a function).
function getItemDimensionsText(it) {
	if (!it) return '—';
	const w = Number(it.custom_pouch_width_mm) || 0;
	const l = Number(it.custom_pouch_length_mm) || 0;
	const thick = Number(it.custom_thickness_mic) || 0;
	if (w > 0 && l > 0) {
		if (thick > 0) return `${w} x ${l} mm x ${thick} mic`;
		return `${w} x ${l} mm`;
	}
	const rollW = Number(it.custom_film_width_mm) || 0;
	if (rollW > 0) {
		if (thick > 0) return `Khổ ${rollW} mm x ${thick} mic`;
		return `Khổ ${rollW} mm`;
	}
	const cylL = Number(it.custom_cylinder_length_mm) || 0;
	const cylC = Number(it.custom_cylinder_circ_mm) || 0;
	if (cylL > 0 || cylC > 0) return `Dài ${cylL} x CV ${cylC} mm`;
	return it.description || '—';
}

function getItemGussetText(it) {
	if (!it) return null;
	const g = Number(it.custom_gusset_mm) || 0;
	if (g > 0) return `${g} mm`;
	return null;
}

// --- Table Container Ref (scroll reset nằm trong useCatalogData) ---
const tableContainerRef = ref(null);

onMounted(async () => {
	window.addEventListener('keydown', handleKeyDown);
	await loadInitialTabData();

	// Read URL query params
	const query = route?.query || {};
	const urlParams = new URLSearchParams(window.location.search);

	const tabVal = query.tab || urlParams.get('tab');
	if (tabVal) {
		if (['sp', 'nvl', 'truc', 'kh', 'ncc', 'user'].includes(tabVal)) {
			activeCatalogTab.value = tabVal;
		} else if (tabVal === 'khach-hang' || tabVal === 'customers') {
			activeCatalogTab.value = 'kh';
		} else if (tabVal === 'nha-cung-cap' || tabVal === 'suppliers') {
			activeCatalogTab.value = 'ncc';
		} else if (tabVal === 'nguoi-dung' || tabVal === 'users') {
			activeCatalogTab.value = 'user';
		}
	}

	const itemTabVal = query.item_tab || urlParams.get('item_tab');
	if (itemTabVal && ['sp', 'nvl', 'truc', 'kh', 'ncc', 'user'].includes(itemTabVal)) {
		activeCatalogTab.value = itemTabVal;
	}

	const itemParam = query.item || urlParams.get('item');
	if (itemParam) {
		const found = masterItems.value.find(x => x.item_code === itemParam);
		if (found) openItemDetail(found);
	}

	const custParam = query.customer || urlParams.get('customer');
	if (custParam) {
		const cust = customers.value.find(c => c.name === custParam);
		if (cust) openCustomerDetail(cust);
	}

	const supParam = query.supplier || urlParams.get('supplier');
	if (supParam) {
		const sup = suppliers.value.find(s => s.name === supParam);
		if (sup) openSupplierDetail(sup);
	}

	const userParam = query.user_detail || urlParams.get('user_detail');
	if (userParam) {
		const usr = users.value.find(u => u.name === userParam);
		if (usr) openUserDetail(usr);
	}
});

onUnmounted(() => {
	window.removeEventListener('keydown', handleKeyDown);
});

</script>

<style scoped>
.catalog-view-wrapper {
	display: flex;
	flex-direction: column;
	flex: 1;
	min-height: 0;
}
</style>
