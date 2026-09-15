import { ref, computed, watch } from 'vue';
import { api } from './useSession';
import { usePortalCounts } from './usePortalCounts';

/**
 * S7d: master loads + filters + pagination cho CatalogView (6 tabs: sp/nvl/truc/kh/ncc/user).
 * Tách từ CatalogView.vue (989L) — view giữ template + URL sync + expose.
 * Items paginate server; kh/ncc/user filter client trên dataset đã load (S5/S6 get_list).
 */
export function useCatalogData() {
	const { catalogCount } = usePortalCounts();

	// --- Master Catalog (Items) States ---
	const masterItems = ref([]);
	const loadingMasterItems = ref(false);
	const activeCatalogTab = ref('sp'); // 'sp', 'nvl', 'truc', 'kh', 'ncc', 'user'
	const activeItemTab = activeCatalogTab; // backward-compatibility alias
	const itemSearchQuery = ref('');

	// --- Pagination State (Zero-Scroll 1080p: locked to 15 lines) ---
	const currentPage = ref(1);
	const pageSize = ref(15);
	const totalMasterItems = ref(0);

	// --- Customers / Suppliers / Users States (khai báo sớm cho computed dùng) ---
	const customers = ref([]);
	const loadingCustomers = ref(false);
	const customerSearchQuery = ref('');
	const selectedCustomer = ref(null);
	const showCustomerDrawer = ref(false);

	const suppliers = ref([]);
	const loadingSuppliers = ref(false);
	const supplierSearchQuery = ref('');
	const selectedSupplier = ref(null);
	const showSupplierDrawer = ref(false);

	const users = ref([]);
	const loadingUsers = ref(false);
	const userSearchQuery = ref('');
	const selectedUser = ref(null);
	const showUserDrawer = ref(false);

	const showItemDrawer = ref(false);
	const selectedMasterItem = ref(null);
	const selectedMasterBom = ref(null);
	const loadingItemDetail = ref(false);

	const loadingCurrentTab = computed(() => {
		if (['sp', 'nvl', 'truc'].includes(activeCatalogTab.value)) return loadingMasterItems.value;
		if (activeCatalogTab.value === 'kh') return loadingCustomers.value;
		if (activeCatalogTab.value === 'ncc') return loadingSuppliers.value;
		return loadingUsers.value;
	});

	// Triple rule 1+2: KH/NCC/User paginate + search server như Items
	// (không tải một lần rồi filter client). Envelope page_result thống nhất.
	const totalCustomers = ref(0);
	const totalSuppliers = ref(0);
	const totalUsers = ref(0);

	const filteredCustomers = computed(() => customers.value);
	const filteredSuppliers = computed(() => suppliers.value);
	const filteredUsers = computed(() => users.value);

	const currentTotalRecords = computed(() => {
		if (['sp', 'nvl', 'truc'].includes(activeCatalogTab.value)) return totalMasterItems.value;
		if (activeCatalogTab.value === 'kh') return totalCustomers.value;
		if (activeCatalogTab.value === 'ncc') return totalSuppliers.value;
		return totalUsers.value;
	});

	const totalPages = computed(() => {
		return Math.max(1, Math.ceil(currentTotalRecords.value / pageSize.value));
	});

	const startRecord = computed(() => {
		if (currentTotalRecords.value === 0) return 0;
		return (currentPage.value - 1) * pageSize.value + 1;
	});

	const endRecord = computed(() => {
		return Math.min(currentPage.value * pageSize.value, currentTotalRecords.value);
	});

	function resetTableScroll() {
		const container = document.querySelector('.table-container');
		if (container) {
			container.scrollTop = 0;
			container.scrollLeft = 0;
		}
	}

	function refreshCurrentTabData() {
		resetTableScroll();
		const tab = activeCatalogTab.value;
		if (['sp', 'nvl', 'truc'].includes(tab)) {
			loadMasterItems();
		} else if (tab === 'kh') {
			loadCustomers();
		} else if (tab === 'ncc') {
			loadSuppliers();
		} else if (tab === 'user') {
			loadUsers();
		}
	}

	function prevPage() {
		if (currentPage.value > 1 && !loadingCurrentTab.value) {
			currentPage.value--;
			refreshCurrentTabData();
		}
	}

	function nextPage() {
		if (currentPage.value < totalPages.value && !loadingCurrentTab.value) {
			currentPage.value++;
			refreshCurrentTabData();
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
				return 'Tìm tên gọi, mã biến thể KH...';
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

	function handleAddNew(ctx) {
		return { tab: activeCatalogTab.value, ...ctx };
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
			currentPage.value = 1;
			if (['sp', 'nvl', 'truc'].includes(activeCatalogTab.value)) {
				loadMasterItems();
			}
		}, 250);
	});

	let pickerSearchTimer = null;
	function schedulePickerReload() {
		clearTimeout(pickerSearchTimer);
		pickerSearchTimer = setTimeout(() => {
			currentPage.value = 1;
			refreshCurrentTabData();
		}, 250);
	}

	watch([customerSearchQuery, supplierSearchQuery, userSearchQuery], () => {
		if (['kh', 'ncc', 'user'].includes(activeCatalogTab.value)) {
			schedulePickerReload();
		} else {
			currentPage.value = 1;
		}
	});

	watch(activeCatalogTab, (newTab) => {
		currentPage.value = 1;
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
			truc: 'Trục in',
			kh: 'Khách hàng',
			ncc: 'Nhà cung cấp',
			user: 'Người dùng',
		};
		return map[activeCatalogTab.value] || 'mặt hàng';
	});

	const filteredMasterItems = computed(() => masterItems.value);

	const paginatedCustomers = computed(() => customers.value);

	const paginatedSuppliers = computed(() => suppliers.value);

	const paginatedUsers = computed(() => users.value);

	async function loadMasterItems() {
		loadingMasterItems.value = true;
		try {
			const data = await api('item.get_list', {
				category: activeItemTab.value,
				query: itemSearchQuery.value.trim() || undefined,
				page: currentPage.value,
				page_length: pageSize.value,
			}, { get: true });
			if (data && Array.isArray(data.items)) {
				masterItems.value = data.items;
				totalMasterItems.value = data.total_count ?? data.items.length;
				currentPage.value = data.page ?? currentPage.value;
			} else if (Array.isArray(data)) {
				masterItems.value = data;
				totalMasterItems.value = data.length;
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

	async function loadCustomers() {
		loadingCustomers.value = true;
		try {
			// Triple rule 1+2: search + paginate server, envelope page_result.
			const data = await api('vanphat_portal.api.customer.get_list', {
				query: customerSearchQuery.value.trim() || undefined,
				page: currentPage.value,
				page_length: pageSize.value,
			}, { get: true });
			if (data && Array.isArray(data.customers)) {
				customers.value = data.customers;
				totalCustomers.value = data.total_count ?? data.customers.length;
				currentPage.value = data.page ?? currentPage.value;
			} else if (Array.isArray(data)) {
				customers.value = data;
				totalCustomers.value = data.length;
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

	async function loadSuppliers() {
		loadingSuppliers.value = true;
		try {
			// Triple rule 1+2: search + paginate server, envelope page_result.
			const data = await api('vanphat_portal.api.supplier.get_list', {
				query: supplierSearchQuery.value.trim() || undefined,
				page: currentPage.value,
				page_length: pageSize.value,
			}, { get: true });
			if (data && Array.isArray(data.suppliers)) {
				suppliers.value = data.suppliers;
				totalSuppliers.value = data.total_count ?? data.suppliers.length;
				currentPage.value = data.page ?? currentPage.value;
			} else if (Array.isArray(data)) {
				suppliers.value = data;
				totalSuppliers.value = data.length;
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

	async function loadUsers() {
		loadingUsers.value = true;
		try {
			// Triple rule 1+2: search + paginate server, envelope page_result.
			const data = await api('vanphat_portal.api.user.get_list', {
				query: userSearchQuery.value.trim() || undefined,
				page: currentPage.value,
				page_length: pageSize.value,
			}, { get: true });
			if (data && Array.isArray(data.users)) {
				users.value = data.users;
				totalUsers.value = data.total_count ?? data.users.length;
				currentPage.value = data.page ?? currentPage.value;
			} else if (Array.isArray(data)) {
				users.value = data;
				totalUsers.value = data.length;
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

	async function loadAllCatalogData() {
		await Promise.all([
			loadMasterItems(),
			loadCustomers(),
			loadSuppliers(),
			loadUsers()
		]);
		syncTotalCount();
	}

	return {
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
		resetTableScroll,
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
		catalogTotalCount,
		syncTotalCount,
		currentCatalogSearchPlaceholder,
		currentAddButtonLabel,
		handleAddNew,
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
		loadAllCatalogData,
	};
}
