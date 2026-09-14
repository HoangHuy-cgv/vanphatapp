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
						@click="catalogSearchInput = ''"
					>✕</button>
				</div>
			</div>
		</header>

		<!-- Sub-filter chips cho tab Sản Phẩm (Bỏ filter Tất Cả) -->
		<div v-if="activeCatalogTab === 'sp'" class="catalog-subfilter-bar">
			<div class="sub-filter-chips">
				<button
					type="button"
					class="sub-chip-btn"
					:class="{ active: activeProductSubFilter === 'tp' }"
					@click="activeProductSubFilter = activeProductSubFilter === 'tp' ? 'all' : 'tp'"
				>
					Túi ghép ({{ tpItems.length }})
				</button>
				<button
					type="button"
					class="sub-chip-btn"
					:class="{ active: activeProductSubFilter === 'ngcs' }"
					@click="activeProductSubFilter = activeProductSubFilter === 'ngcs' ? 'all' : 'ngcs'"
				>
					Túi NGCS ({{ ngcsItems.length }})
				</button>
				<button
					type="button"
					class="sub-chip-btn"
					:class="{ active: activeProductSubFilter === 'btp' }"
					@click="activeProductSubFilter = activeProductSubFilter === 'btp' ? 'all' : 'btp'"
				>
					Cuộn màng ({{ btpItems.length }})
				</button>
				<button
					type="button"
					class="sub-chip-btn"
					:class="{ active: activeProductSubFilter === 'tmd' }"
					@click="activeProductSubFilter = activeProductSubFilter === 'tmd' ? 'all' : 'tmd'"
				>
					Màng đơn ({{ tmdItems.length }})
				</button>
			</div>
		</div>

		<!-- Bảng Mặt hàng: Sản phẩm, NVL, Trục in -->
		<div v-if="activeCatalogTab === 'sp' || activeCatalogTab === 'nvl' || activeCatalogTab === 'truc'" class="table-container">
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
						<td colspan="6" class="empty-cell" style="padding: 2.5rem 1rem; text-align: center;">
							<div v-if="loadingMasterItems" class="text-secondary">Đang tải danh mục...</div>
							<div v-else-if="itemSearchQuery" class="flex flex-col items-center justify-center gap-2">
								<div class="text-secondary text-sm">
									Không tìm thấy mặt hàng nào khớp với "<strong class="text-white">{{ itemSearchQuery }}</strong>" trong tab {{ currentTabLabel }}.
								</div>
								<button
									type="button"
									class="btn-clear-filter-inline"
									@click="itemSearchQuery = ''"
								>
									✕ Xóa tìm kiếm để xem tất cả {{ currentTabMasterItems.length }} sản phẩm {{ currentTabLabel }}
								</button>
							</div>
							<div v-else class="text-secondary text-sm">Không có mặt hàng nào trong tab này</div>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Bảng Khách hàng -->
		<div v-else-if="activeCatalogTab === 'kh'" class="table-container">
			<table class="data-table">
				<thead>
					<tr>
						<th style="width: 12%;">MÃ KHÁCH</th>
						<th style="width: 22%;">TÊN GỌI TẮT (ALIAS)</th>
						<th style="width: 32%;">TÊN PHÁP NHÂN</th>
						<th style="width: 14%;">KHU VỰC</th>
						<th class="text-right" style="width: 12%;">HẠN MỨC NỢ</th>
						<th style="width: 8%;">THANH TOÁN</th>
					</tr>
				</thead>
				<tbody>
					<tr
						v-for="c in filteredCustomers"
						:key="c.name"
						class="table-row cursor-pointer"
						@click="openCustomerDetail(c)"
					>
						<td class="font-mono font-bold text-primary text-[14.5px]">
							{{ c.name }}
						</td>
						<td>
							<div class="font-semibold text-white leading-tight text-[15px]">
								{{ c.alias || c.customer_name }}
							</div>
						</td>
						<td>
							<div class="text-sm text-secondary truncate max-w-[340px]" :title="c.customer_name">
								{{ c.customer_name }}
							</div>
						</td>
						<td class="text-sm">
							<span class="text-slate-300">{{ c.territory || 'Việt Nam' }}</span>
						</td>
						<td class="text-right font-mono text-sm">
							<span v-if="Number(c.credit_limit) > 0" class="text-emerald font-bold">
								{{ formatCurrency(c.credit_limit) }}
							</span>
							<span v-else class="text-secondary/60">0 đ</span>
						</td>
						<td class="text-sm">
							<span v-if="c.payment_terms && c.payment_terms.includes('30 ngày')" class="text-amber font-mono text-xs">Gối đầu</span>
							<span v-else class="text-secondary text-xs">Cọc 50%</span>
						</td>
					</tr>
					<tr v-if="filteredCustomers.length === 0">
						<td colspan="6" class="empty-cell" style="padding: 2.5rem 1rem; text-align: center;">
							<div v-if="loadingCustomers" class="text-secondary">Đang tải khách hàng...</div>
							<div v-else class="text-secondary text-sm">Không tìm thấy khách hàng nào phù hợp</div>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Bảng Nhà cung cấp -->
		<div v-else-if="activeCatalogTab === 'ncc'" class="table-container">
			<table class="data-table">
				<thead>
					<tr>
						<th style="width: 12%;">MÃ NCC</th>
						<th style="width: 20%;">TÊN GỌI TẮT</th>
						<th style="width: 32%;">TÊN PHÁP NHÂN</th>
						<th style="width: 22%;">NHÓM CUNG ỨNG</th>
						<th style="width: 14%;">MÃ SỐ THUẾ</th>
					</tr>
				</thead>
				<tbody>
					<tr
						v-for="s in filteredSuppliers"
						:key="s.name"
						class="table-row cursor-pointer"
						@click="openSupplierDetail(s)"
					>
						<td class="font-mono font-bold text-sky-400 text-[14.5px]">
							{{ s.name }}
						</td>
						<td>
							<div class="font-semibold text-white leading-tight text-[15px]">
								{{ s.alias || s.supplier_name }}
							</div>
						</td>
						<td>
							<div class="text-sm text-secondary truncate max-w-[340px]" :title="s.supplier_name">
								{{ s.supplier_name }}
							</div>
						</td>
						<td>
							<span class="badge-tag-group text-xs">{{ s.supplier_group || 'NCC' }}</span>
						</td>
						<td class="font-mono text-sm text-slate-300">
							{{ s.tax_id || '—' }}
						</td>
					</tr>
					<tr v-if="filteredSuppliers.length === 0">
						<td colspan="5" class="empty-cell" style="padding: 2.5rem 1rem; text-align: center;">
							<div v-if="loadingSuppliers" class="text-secondary">Đang tải nhà cung cấp...</div>
							<div v-else class="text-secondary text-sm">Không tìm thấy nhà cung cấp nào phù hợp</div>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Bảng Người dùng -->
		<div v-else-if="activeCatalogTab === 'user'" class="table-container">
			<table class="data-table">
				<thead>
					<tr>
						<th style="width: 26%;">EMAIL ĐĂNG NHẬP</th>
						<th style="width: 22%;">HỌ VÀ TÊN</th>
						<th style="width: 18%;">PHÒNG BAN</th>
						<th style="width: 18%;">CHỨC DANH</th>
						<th style="width: 16%;">VAI TRÒ ERPNEXT</th>
					</tr>
				</thead>
				<tbody>
					<tr
						v-for="u in filteredUsers"
						:key="u.name"
						class="table-row cursor-pointer"
						@click="openUserDetail(u)"
					>
						<td class="font-mono font-semibold text-purple-400 text-[14px]">
							{{ u.email }}
						</td>
						<td>
							<div class="font-semibold text-white leading-tight text-[15px]">
								{{ u.full_name }}
							</div>
						</td>
						<td class="text-sm text-slate-300">
							{{ u.department || 'Ban Giám Đốc' }}
						</td>
						<td class="text-sm text-primary">
							{{ u.designation || 'Nhân viên' }}
						</td>
						<td>
							<span class="badge-role-user font-mono text-xs">{{ u.role_profile_name || 'System User' }}</span>
						</td>
					</tr>
					<tr v-if="filteredUsers.length === 0">
						<td colspan="5" class="empty-cell" style="padding: 2.5rem 1rem; text-align: center;">
							<div v-if="loadingUsers" class="text-secondary">Đang tải người dùng...</div>
							<div v-else class="text-secondary text-sm">Không tìm thấy người dùng nào phù hợp</div>
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
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import DrawerItemDetail from '../components/DrawerItemDetail.vue';
import DrawerCustomerDetail from '../components/DrawerCustomerDetail.vue';
import DrawerSupplierDetail from '../components/DrawerSupplierDetail.vue';
import DrawerUserDetail from '../components/DrawerUserDetail.vue';
import { MASTER_CATALOG_ITEMS } from '../data/mockData';
import { usePortalCounts } from '../composables/usePortalCounts';

const route = useRoute();
const { catalogCount } = usePortalCounts();

// --- Master Catalog (Items) States ---
const masterItems = ref([]);
const loadingMasterItems = ref(false);
const activeCatalogTab = ref('sp'); // 'sp', 'nvl', 'truc', 'kh', 'ncc', 'user'
const activeItemTab = activeCatalogTab; // backward-compatibility alias
const activeProductSubFilter = ref('all'); // 'all', 'tp', 'ngcs', 'btp', 'tmd'
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
			return 'Tìm mã, tên gọi tắt, tên pháp nhân, khu vực...';
		case 'ncc':
			return 'Tìm mã, tên tắt, nhóm NCC, MST...';
		case 'user':
			return 'Tìm tên, email, chức danh, phòng ban...';
		case 'nvl':
			return 'Tìm mã NVL, tên màng, keo, hóa chất...';
		case 'truc':
			return 'Tìm mã trục, quy cách trục, sản phẩm...';
		default:
			return 'Tìm mã, tên, khách hàng, màng...';
	}
});

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
	if (tabKey === 'sp') {
		activeProductSubFilter.value = 'all';
	}
}

function switchItemTab(tabKey) {
	switchCatalogTab(tabKey);
}

const tpItems = computed(() =>
	masterItems.value.filter((i) => (i.item_code || '').startsWith('TP-') || i.item_group === 'Túi Màng Ghép Đặt Riêng')
);
const ngcsItems = computed(() =>
	masterItems.value.filter((i) => (i.item_code || '').startsWith('NGCS-') || i.item_group === 'Túi Nước Giặt Có Sẵn (NGCS)')
);
const tmdItems = computed(() =>
	masterItems.value.filter((i) => (i.item_code || '').startsWith('TMD-') || i.item_group === 'Túi Màng Đơn')
);
const btpItems = computed(() =>
	masterItems.value.filter((i) => (i.item_code || '').startsWith('BTP-') || i.item_group === 'Cuộn Màng Ghép BTP')
);

// Gộp 4 nhóm thành Danh Mục Sản Phẩm (88 mã)
const productItems = computed(() =>
	masterItems.value.filter((i) =>
		(i.item_code || '').startsWith('TP-') ||
		(i.item_code || '').startsWith('NGCS-') ||
		(i.item_code || '').startsWith('TMD-') ||
		(i.item_code || '').startsWith('BTP-') ||
		i.item_group === 'Túi Màng Ghép Đặt Riêng' ||
		i.item_group === 'Túi Nước Giặt Có Sẵn (NGCS)' ||
		i.item_group === 'Túi Màng Đơn' ||
		i.item_group === 'Cuộn Màng Ghép BTP'
	)
);

const nvlItems = computed(() =>
	masterItems.value.filter((i) => (i.item_code || '').startsWith('NVL-') || i.item_group === 'Màng Thô NVL' || i.item_group === 'Màng In Ống Đồng' || i.item_group === 'Hóa Chất & Keo Ghép' || i.item_group === 'Phụ Kiện Bao Bì')
);
const trucItems = computed(() =>
	masterItems.value.filter((i) => (i.item_code || '').startsWith('TRUC-') || i.item_group === 'Trục In Ống Đồng')
);

const currentTabMasterItems = computed(() => {
	if (activeItemTab.value === 'sp') {
		if (activeProductSubFilter.value === 'tp') return tpItems.value;
		if (activeProductSubFilter.value === 'ngcs') return ngcsItems.value;
		if (activeProductSubFilter.value === 'btp') return btpItems.value;
		if (activeProductSubFilter.value === 'tmd') return tmdItems.value;
		return productItems.value;
	}
	if (activeItemTab.value === 'nvl') return nvlItems.value;
	if (activeItemTab.value === 'truc') return trucItems.value;
	return productItems.value;
});

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
		const res = await fetch('/api/method/vanphat_portal.api.item.get_list');
		const json = await res.json();
		if (json && Array.isArray(json.message) && json.message.length > 0) {
			masterItems.value = json.message;
		} else if (masterItems.value.length === 0) {
			masterItems.value = [...(MASTER_CATALOG_ITEMS || [])];
		}
	} catch (err) {
		if (masterItems.value.length === 0) {
			masterItems.value = [...(MASTER_CATALOG_ITEMS || [])];
		}
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
		const res = await fetch(`/api/method/vanphat_portal.api.item.get_detail?item_code=${encodeURIComponent(item.item_code)}`);
		const json = await res.json();
		if (json && json.message) {
			if (json.message.item) selectedMasterItem.value = json.message.item;
			selectedMasterBom.value = json.message.bom || null;
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
		const res = await fetch('/api/method/vanphat_portal.api.customer.get_list');
		const json = await res.json();
		if (json && Array.isArray(json.message)) {
			customers.value = json.message;
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
		(c.tax_id && c.tax_id.toLowerCase().includes(q))
	);
});

// --- Supplier Methods ---
async function loadSuppliers() {
	loadingSuppliers.value = true;
	try {
		const res = await fetch('/api/method/vanphat_portal.api.supplier.get_list');
		const json = await res.json();
		if (json && Array.isArray(json.message)) {
			suppliers.value = json.message;
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
		(s.tax_id && s.tax_id.toLowerCase().includes(q))
	);
});

// --- User Methods ---
async function loadUsers() {
	loadingUsers.value = true;
	try {
		const res = await fetch('/api/method/vanphat_portal.api.user.get_list');
		const json = await res.json();
		if (json && Array.isArray(json.message)) {
			users.value = json.message;
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
});
</script>

<style scoped>
.catalog-view-wrapper {
	display: flex;
	flex-direction: column;
	flex: 1;
	min-height: 0;
}

.catalog-header-cockpit {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 16px;
	margin-bottom: 14px;
	flex-wrap: nowrap;
	flex-shrink: 0;
}

.catalog-header-cockpit .catalog-tabs-bar {
	margin-bottom: 0;
	border-bottom: none;
	padding-bottom: 0;
	flex: 1;
	min-width: 0;
	overflow-x: auto;
	scrollbar-width: none;
	-ms-overflow-style: none;
}

.catalog-header-cockpit .catalog-tabs-bar::-webkit-scrollbar {
	display: none;
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

.catalog-subfilter-bar {
	display: flex;
	align-items: center;
	margin-bottom: 14px;
	flex-shrink: 0;
}

.sub-filter-chips {
	display: flex;
	align-items: center;
	gap: 6px;
	flex-shrink: 0;
}

.sub-chip-btn {
	background: #161b22;
	border: 1px solid #3a424e;
	color: #94a3b8;
	font-size: 12.5px;
	padding: 4px 10px;
	border-radius: 9999px;
	cursor: pointer;
	white-space: nowrap;
	transition: all 0.15s ease;
}

.sub-chip-btn:hover {
	color: #ffffff;
	border-color: #64748b;
}

.sub-chip-btn.active {
	background: rgba(78, 161, 224, 0.15);
	border-color: #4ea1e0;
	color: #4ea1e0;
	font-weight: 600;
}

.catalog-search-cockpit-wrap {
	display: flex;
	align-items: center;
	gap: 10px;
	flex-shrink: 0;
}

.search-input-wrap {
	position: relative;
	width: 250px;
	display: flex;
	align-items: center;
}

.search-icon {
	position: absolute;
	left: 12px;
	width: 16px;
	height: 16px;
	color: #8b949e;
	pointer-events: none;
}

.catalog-search-input {
	width: 100%;
	padding: 8px 32px 8px 36px;
	background: #161b22;
	border: 1px solid #3a424e;
	border-radius: 6px;
	color: #f1f5f9;
	font-size: 14.5px;
	outline: none;
	transition: border-color 0.15s ease;
}

.catalog-search-input:focus {
	border-color: #4ea1e0;
	box-shadow: 0 0 0 2px rgba(78, 161, 224, 0.15);
}

.btn-clear-search {
	position: absolute;
	right: 10px;
	background: transparent;
	border: none;
	color: #8b949e;
	cursor: pointer;
	font-size: 13px;
	padding: 2px 4px;
	border-radius: 4px;
}

.btn-clear-search:hover {
	color: #ffffff;
}

.btn-clear-filter-inline {
	margin-top: 6px;
	padding: 6px 14px;
	background: rgba(78, 161, 224, 0.12);
	border: 1px solid rgba(78, 161, 224, 0.3);
	border-radius: 6px;
	color: #4ea1e0;
	font-size: 13px;
	font-weight: 500;
	cursor: pointer;
	transition: all 0.15s ease;
}

.btn-clear-filter-inline:hover {
	background: rgba(78, 161, 224, 0.22);
	border-color: #4ea1e0;
	color: #ffffff;
}

.badge-tag-cust {
	display: inline-block;
	font-size: 11px;
	font-weight: 700;
	padding: 2px 6px;
	border-radius: 4px;
}

.badge-tag-group {
	display: inline-block;
	font-size: 11.5px;
	font-weight: 600;
	padding: 3px 8px;
	border-radius: 5px;
	background: #1c222d;
	color: #93c5fd;
	border: 1px solid #334155;
}

.badge-role-user {
	padding: 2px 7px;
	border-radius: 4px;
	background: #1e1b4b;
	color: #c4b5fd;
	border: 1px solid rgba(196, 181, 253, 0.25);
}

.text-emerald {
	color: #34d399;
}

.text-amber {
	color: #f59e0b;
}

.font-mono {
	font-family: 'JetBrains Mono', monospace;
}
</style>
