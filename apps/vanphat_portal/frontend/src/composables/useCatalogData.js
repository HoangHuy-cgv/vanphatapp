import { ref, computed, watch } from 'vue';
import { api } from './useSession';
import { usePortalCounts } from './usePortalCounts';
import { useCockpitPagination } from './useCockpitPagination';
import { sizeTextOf, gussetTextOf } from './useItemSpec';

/**
 * Catalog baseline theo tab Sản phẩm (sp) — SSOT để nhân bản ra 6 tab.
 * 5 tab còn lại (nvl/truc/kh/ncc/user) đã xoá trắng, chờ nhân pattern này.
 * Items paginate + search server, envelope page_result.
 */
const PAGE_SIZE = 15;
const SEARCH_DEBOUNCE_MS = 250;
const PRODUCT_CATEGORY = 'sp';

export function useCatalogData() {
	const { catalogCount } = usePortalCounts();

	// Tab đang mở: 'sp' + 5 tab xoá trắng chờ nhân bản.
	const activeCatalogTab = ref('sp');
	const blankTabs = ref([
		{ key: 'nvl', label: 'Nguyên vật liệu' },
		{ key: 'truc', label: 'Trục in' },
		{ key: 'kh', label: 'Khách hàng' },
		{ key: 'ncc', label: 'Nhà cung cấp' },
		{ key: 'user', label: 'Người dùng' },
	]);

	// Dữ liệu Sản phẩm (server paginate).
	const items = ref([]);
	const loadingItems = ref(false);
	const searchQuery = ref('');
	const currentPage = ref(1);
	const totalRecords = ref(0);

	// Drawer chi tiết mặt hàng.
	const selectedItem = ref(null);
	const selectedBom = ref(null);
	const loadingDetail = ref(false);
	const showItemDrawer = ref(false);

	let searchTimer = null;
	let listAborter = null;

	const isProductTab = computed(() => activeCatalogTab.value === PRODUCT_CATEGORY);
	const totalPages = computed(() => Math.max(1, Math.ceil(totalRecords.value / PAGE_SIZE)));
	const blankTabLabel = computed(
		() => blankTabs.value.find((t) => t.key === activeCatalogTab.value)?.label || ''
	);

	function resetTableScroll() {
		if (typeof document === 'undefined') return;
		const container = document.querySelector('.table-container');
		if (container) {
			container.scrollTop = 0;
			container.scrollLeft = 0;
		}
	}

	async function loadItems() {
		// Abort request cũ: gõ search dồn dập chỉ render kết quả mới nhất.
		if (listAborter) listAborter.abort();
		listAborter = typeof AbortController !== 'undefined' ? new AbortController() : null;
		const signal = listAborter ? listAborter.signal : null;
		loadingItems.value = true;
		try {
			const data = await api('item.get_list', {
				category: PRODUCT_CATEGORY,
				query: searchQuery.value.trim() || undefined,
				page: currentPage.value,
				page_length: PAGE_SIZE,
			}, { get: true, ...(signal ? { signal } : {}) });
			if (signal && signal.aborted) return;
			if (data && Array.isArray(data.items)) {
				items.value = data.items;
				totalRecords.value = data.total_count ?? data.items.length;
				currentPage.value = data.page ?? currentPage.value;
			} else if (Array.isArray(data)) {
				items.value = data;
				totalRecords.value = data.length;
			}
		} catch (err) {
			console.error('Error loading master items:', err);
		}
		if (signal && signal.aborted) return;
		catalogCount.value = totalRecords.value;
		loadingItems.value = false;
	}

	function refreshItems() {
		resetTableScroll();
		if (isProductTab.value) loadItems();
	}

	// S8c: pagination dùng chung (xóa copy-paste prev/next/goto/keydown).
	const { prevPage, nextPage, gotoPage, handleKeyDown } = useCockpitPagination({
		currentPage,
		totalPages,
		isLoading: loadingItems,
		onReload: () => refreshItems(),
	});

	function switchCatalogTab(tabKey) {
		if (tabKey === activeCatalogTab.value) return;
		activeCatalogTab.value = tabKey;
	}

	watch(searchQuery, () => {
		clearTimeout(searchTimer);
		searchTimer = setTimeout(() => {
			currentPage.value = 1;
			refreshItems();
		}, SEARCH_DEBOUNCE_MS);
	});

	watch(activeCatalogTab, () => {
		currentPage.value = 1;
		resetTableScroll();
		if (isProductTab.value) loadItems();
	});

	async function openItemDetail(item) {
		selectedItem.value = item;
		selectedBom.value = null;
		showItemDrawer.value = true;
		loadingDetail.value = true;
		try {
			const data = await api('vanphat_portal.api.item.get_detail', { item_code: item.item_code }, { get: true });
			if (data) {
				if (data.item) selectedItem.value = data.item;
				selectedBom.value = data.bom || null;
			}
		} catch (e) {
			// keep selected item
		}
		loadingDetail.value = false;
	}

	async function loadInitialTabData() {
		if (isProductTab.value) await loadItems();
	}

	// Helpers hiển thị thuần tuý (SSOT trong useItemSpec — không logic tiền/config).
	const getItemDimensionsText = sizeTextOf;
	const getItemGussetText = gussetTextOf;

	return {
		activeCatalogTab,
		blankTabs,
		isProductTab,
		blankTabLabel,
		items,
		loadingItems,
		searchQuery,
		currentPage,
		pageSize: PAGE_SIZE,
		totalRecords,
		totalPages,
		prevPage,
		nextPage,
		gotoPage,
		handleKeyDown,
		switchCatalogTab,
		showItemDrawer,
		selectedItem,
		selectedBom,
		loadingDetail,
		getItemDimensionsText,
		getItemGussetText,
		loadItems,
		openItemDetail,
		loadInitialTabData,
	};
}
