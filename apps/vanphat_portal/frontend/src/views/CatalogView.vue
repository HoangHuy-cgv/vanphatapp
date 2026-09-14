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
					<span class="tab-badge">{{ productItems.length }}</span>
				</button>
				<button
					type="button"
					class="order-tab-btn"
					:class="{ active: activeCatalogTab === 'nvl' }"
					@click="switchCatalogTab('nvl')"
				>
					<span>Nguyên vật liệu</span>
					<span class="tab-badge">{{ nvlItems.length }}</span>
				</button>
				<button
					type="button"
					class="order-tab-btn"
					:class="{ active: activeCatalogTab === 'truc' }"
					@click="switchCatalogTab('truc')"
				>
					<span>Trục in</span>
					<span class="tab-badge">{{ trucItems.length }}</span>
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
						type="text"
						class="catalog-search-input"
						v-model="catalogSearchInput"
						:placeholder="currentCatalogSearchPlaceholder"
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
				@click="handleAddNew"
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
						<th style="width: 14%;">Mã sản phẩm</th>
						<th style="width: 27%;">Tên sản phẩm</th>
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
						<!-- Mã sản phẩm -->
						<td class="font-mono font-bold text-primary text-[14.5px]">
							{{ it.item_code }}
						</td>

						<!-- Tên sản phẩm (chỉ dùng tên ngắn) -->
						<td>
							<div class="font-semibold text-white leading-tight text-[15px]" :title="it.item_name || ''">
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
					<tr v-if="filteredMasterItems.length === 0">
						<td colspan="6" class="empty-cell">
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
								<button type="button" class="btn-empty-action btn-empty-primary" @click="handleAddNew">
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
						v-for="c in filteredCustomers"
						:key="c.name"
						class="table-row cursor-pointer"
						@click="openCustomerDetail(c)"
					>
						<td class="whitespace-nowrap">
							<div class="font-semibold text-white leading-tight text-[15px]" :title="'Mã KH: ' + c.name + (Number(c.credit_limit) > 0 ? ' • Hạn mức: ' + formatCurrency(c.credit_limit) : '')">
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
								<button type="button" class="btn-empty-action btn-empty-primary" @click="handleAddNew">
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
						v-for="s in filteredSuppliers"
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
								<button type="button" class="btn-empty-action btn-empty-primary" @click="handleAddNew">
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
						v-for="u in filteredUsers"
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
								<button type="button" class="btn-empty-action btn-empty-primary" @click="handleAddNew">
									+ Thêm người dùng
								</button>
							</div>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Slide-over Drawer Chi Tiết Mặt Hàng Master Data -->
		<DrawerItemDetail
			:is-open="showItemDrawer"
			:open="showItemDrawer"
			:item="selectedMasterItem"
			:bom="selectedMasterBom"
			:loading="loadingItemDetail"
			@close="showItemDrawer = false"
		/>

		<!-- Slide-over Drawer Chi Tiết Khách Hàng -->
		<DrawerCustomerDetail
			:is-open="showCustomerDrawer"
			:open="showCustomerDrawer"
			:customer="selectedCustomer"
			:master-items="masterItems"
			@close="showCustomerDrawer = false"
		/>

		<!-- Slide-over Drawer Chi Tiết Nhà Cung Cấp -->
		<DrawerSupplierDetail
			:is-open="showSupplierDrawer"
			:open="showSupplierDrawer"
			:supplier="selectedSupplier"
			@close="showSupplierDrawer = false"
		/>

		<!-- Slide-over Drawer Chi Tiết Người Dùng -->
		<DrawerUserDetail
			:is-open="showUserDrawer"
			:open="showUserDrawer"
			:user="selectedUser"
			@close="showUserDrawer = false"
		/>
	</div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import DrawerItemDetail from '../components/DrawerItemDetail.vue';
import DrawerCustomerDetail from '../components/DrawerCustomerDetail.vue';
import DrawerSupplierDetail from '../components/DrawerSupplierDetail.vue';
import DrawerUserDetail from '../components/DrawerUserDetail.vue';
import { usePortalCounts } from '../composables/usePortalCounts';
import { api } from '../composables/useSession';

const route = useRoute();
const { catalogCount } = usePortalCounts();
const emit = defineEmits(['add-new']);

// --- Table Container Ref & Scroll Reset ---
const tableContainerRef = ref(null);

function resetTableScroll() {
	nextTick(() => {
		const container = tableContainerRef.value || document.querySelector('.table-container');
		if (container) {
			container.scrollTop = 0;
			container.scrollLeft = 0;
		}
	});
}

// --- Master Catalog (Items) States ---
const masterItems = ref([]);
const loadingMasterItems = ref(false);
const activeCatalogTab = ref('sp'); // 'sp', 'nvl', 'truc', 'kh', 'ncc', 'user'
const activeItemTab = activeCatalogTab; // backward-compatibility alias
const itemSearchQuery = ref('');

const showItemDrawer = ref(false);
const selectedMasterItem = ref(null);
const selectedMasterBom = ref(null);
const loadingItemDetail = ref(false);

// --- Customers States ---
const customers = ref([]);
const loadingCustomers = ref(false);
const customerSearchQuery = ref('');
const selectedCustomer = ref(null);
const showCustomerDrawer = ref(false);

// --- Suppliers States ---
const suppliers = ref([]);
const loadingSuppliers = ref(false);
const supplierSearchQuery = ref('');
const selectedSupplier = ref(null);
const showSupplierDrawer = ref(false);

// --- Users States ---
const users = ref([]);
const loadingUsers = ref(false);
const userSearchQuery = ref('');
const selectedUser = ref(null);
const showUserDrawer = ref(false);

// --- Unified Catalog Computed & Helpers ---
const catalogTotalCount = computed(() => {
	return masterItems.value.length + customers.value.length + suppliers.value.length + users.value.length;
});

function syncTotalCount() {
	catalogCount.value = catalogTotalCount.value;
}

const currentCatalogSearchPlaceholder = computed(() => {
	switch (activeCatalogTab.value) {
		case 'kh':
			return 'Tìm tên gọi tắt, tên pháp nhân, MST, mã KH...';
		case 'ncc':
			return 'Tìm tên tắt, pháp nhân, MST, nhóm NCC...';
		case 'user':
			return 'Tìm SĐT đăng nhập, họ tên, phòng ban, vai trò...';
		case 'nvl':
			return 'Tìm mã NVL, tên màng, keo, hóa chất...';
		case 'truc':
			return 'Tìm mã trục, quy cách trục, sản phẩm...';
		default:
			return 'Tìm mã, tên, khách hàng, màng...';
	}
});

const currentAddButtonLabel = computed(() => {
	switch (activeCatalogTab.value) {
		case 'sp':
			return '+ Thêm sản phẩm';
		case 'nvl':
			return '+ Thêm NVL';
		case 'truc':
			return '+ Thêm trục in';
		case 'kh':
			return '+ Thêm khách hàng';
		case 'ncc':
			return '+ Thêm NCC';
		case 'user':
			return '+ Thêm người dùng';
		default:
			return '+ Thêm mới';
	}
});

function handleAddNew() {
	emit('add-new', { tab: activeCatalogTab.value });
}

const catalogSearchInput = computed({
	get() {
		if (activeCatalogTab.value === 'kh') return customerSearchQuery.value;
		if (activeCatalogTab.value === 'ncc') return supplierSearchQuery.value;
		if (activeCatalogTab.value === 'user') return userSearchQuery.value;
		return itemSearchQuery.value;
	},
	set(val) {
		if (activeCatalogTab.value === 'kh') customerSearchQuery.value = val;
		else if (activeCatalogTab.value === 'ncc') supplierSearchQuery.value = val;
		else if (activeCatalogTab.value === 'user') userSearchQuery.value = val;
		else itemSearchQuery.value = val;
	}
});

function switchCatalogTab(tabKey) {
	activeCatalogTab.value = tabKey;
}

let itemSearchTimer = null;
watch(itemSearchQuery, () => {
	clearTimeout(itemSearchTimer);
	itemSearchTimer = setTimeout(() => {
		if (['sp', 'nvl', 'truc'].includes(activeCatalogTab.value)) {
			loadMasterItems();
		}
	}, 250);
});

watch(activeCatalogTab, (newTab) => {
	resetTableScroll();
	if (['sp', 'nvl', 'truc'].includes(newTab)) {
		loadMasterItems();
	} else if (newTab === 'kh') {
		loadCustomers();
	} else if (newTab === 'ncc') {
		loadSuppliers();
	} else if (newTab === 'user') {
		loadUsers();
	}
});

function switchItemTab(tabKey) {
	switchCatalogTab(tabKey);
}

const currentTabMasterItems = computed(() => masterItems.value);

const currentTabLabel = computed(() => {
	const map = {
		sp: 'Sản phẩm',
		nvl: 'Nguyên vật liệu',
		truc: 'Trục in'
	};
	return map[activeItemTab.value] || 'mặt hàng';
});

const filteredMasterItems = computed(() => {
	const list = currentTabMasterItems.value;
	const q = itemSearchQuery.value.trim().toLowerCase();
	if (!q) return list;
	return list.filter((it) =>
		(it.item_code && it.item_code.toLowerCase().includes(q)) ||
		(it.item_name && it.item_name.toLowerCase().includes(q)) ||
		(it.custom_alias && it.custom_alias.toLowerCase().includes(q)) ||
		(it.customer && it.customer.toLowerCase().includes(q)) ||
		(it.brand && it.brand.toLowerCase().includes(q)) ||
		(it.custom_structure_layers && it.custom_structure_layers.toLowerCase().includes(q)) ||
		(it.description && it.description.toLowerCase().includes(q))
	);
});

function formatCurrency(val) {
	if (val == null || val === '') return '0 đ';
	if (typeof val === 'string' && isNaN(Number(val))) return val;
	return Number(val).toLocaleString('vi-VN') + ' đ';
}

function formatItemRate(val) {
	if (!val && val !== 0) return '—';
	return new Intl.NumberFormat('vi-VN').format(Math.round(val)) + ' đ';
}

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

function getItemPouchDims(it) {
	return getItemDimensionsText(it);
}

async function loadMasterItems() {
	loadingMasterItems.value = true;
	try {
		const data = await api('item.get_list', {
			category: activeItemTab.value,
			query: itemSearchQuery.value.trim() || undefined,
		}, { get: true });
		if (Array.isArray(data)) {
			masterItems.value = data;
		}
	} catch (err) {
		console.error('Error loading master items:', err);
	}
	syncTotalCount();
	loadingMasterItems.value = false;
}

async function openItemDetail(item) {
	selectedMasterItem.value = item;
	selectedMasterBom.value = null;
	showItemDrawer.value = true;
	loadingItemDetail.value = true;
	try {
		const data = await api('vanphat_portal.api.item.get_detail', { item_code: item.item_code }, { get: true });
		if (data) {
			if (data.item) selectedMasterItem.value = data.item;
			selectedMasterBom.value = data.bom || null;
		}
	} catch (e) {
		// keep selected item
	}
	loadingItemDetail.value = false;
}

// --- Customer Methods ---
async function loadCustomers() {
	loadingCustomers.value = true;
	try {
		const data = await api('vanphat_portal.api.customer.get_list', {}, { get: true });
		if (Array.isArray(data)) {
			customers.value = data;
		}
	} catch (e) {
		console.error('Error loading customers:', e);
	}
	syncTotalCount();
	loadingCustomers.value = false;
}

function openCustomerDetail(c) {
	selectedCustomer.value = c;
	showCustomerDrawer.value = true;
}

const filteredCustomers = computed(() => {
	const q = customerSearchQuery.value.trim().toLowerCase();
	if (!q) return customers.value;
	return customers.value.filter(c =>
		(c.name && c.name.toLowerCase().includes(q)) ||
		(c.customer_name && c.customer_name.toLowerCase().includes(q)) ||
		(c.alias && c.alias.toLowerCase().includes(q)) ||
		(c.customer_group && c.customer_group.toLowerCase().includes(q)) ||
		(c.territory && c.territory.toLowerCase().includes(q)) ||
		(c.payment_terms && c.payment_terms.toLowerCase().includes(q)) ||
		(c.tax_id && c.tax_id.toLowerCase().includes(q))
	);
});

// --- Supplier Methods ---
async function loadSuppliers() {
	loadingSuppliers.value = true;
	try {
		const data = await api('vanphat_portal.api.supplier.get_list', {}, { get: true });
		if (Array.isArray(data)) {
			suppliers.value = data;
		}
	} catch (e) {
		console.error('Error loading suppliers:', e);
	}
	syncTotalCount();
	loadingSuppliers.value = false;
}

function openSupplierDetail(s) {
	selectedSupplier.value = s;
	showSupplierDrawer.value = true;
}

const filteredSuppliers = computed(() => {
	const q = supplierSearchQuery.value.trim().toLowerCase();
	if (!q) return suppliers.value;
	return suppliers.value.filter(s =>
		(s.name && s.name.toLowerCase().includes(q)) ||
		(s.supplier_name && s.supplier_name.toLowerCase().includes(q)) ||
		(s.alias && s.alias.toLowerCase().includes(q)) ||
		(s.supplier_group && s.supplier_group.toLowerCase().includes(q)) ||
		(s.payment_terms && s.payment_terms.toLowerCase().includes(q)) ||
		(s.tax_id && s.tax_id.toLowerCase().includes(q))
	);
});

// --- User Methods ---
async function loadUsers() {
	loadingUsers.value = true;
	try {
		const data = await api('vanphat_portal.api.user.get_list', {}, { get: true });
		if (Array.isArray(data)) {
			users.value = data;
		}
	} catch (e) {
		console.error('Error loading users:', e);
	}
	syncTotalCount();
	loadingUsers.value = false;
}

function openUserDetail(u) {
	selectedUser.value = u;
	showUserDrawer.value = true;
}

const filteredUsers = computed(() => {
	const q = userSearchQuery.value.trim().toLowerCase();
	if (!q) return users.value;
	return users.value.filter(u =>
		(u.name && u.name.toLowerCase().includes(q)) ||
		(u.full_name && u.full_name.toLowerCase().includes(q)) ||
		(u.email && u.email.toLowerCase().includes(q)) ||
		(u.mobile_no && u.mobile_no.includes(q)) ||
		(u.department && u.department.toLowerCase().includes(q)) ||
		(u.designation && u.designation.toLowerCase().includes(q)) ||
		(u.role_profile_name && u.role_profile_name.toLowerCase().includes(q))
	);
});

async function loadAllCatalogData() {
	await Promise.all([
		loadMasterItems(),
		loadCustomers(),
		loadSuppliers(),
		loadUsers()
	]);
	syncTotalCount();
}

onMounted(async () => {
	await loadAllCatalogData();

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

defineExpose({
	activeCatalogTab,
	switchCatalogTab,
	loadAllCatalogData,
	openItemDetail,
	openCustomerDetail,
	openSupplierDetail,
	openUserDetail,
	handleAddNew,
	currentAddButtonLabel,
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
