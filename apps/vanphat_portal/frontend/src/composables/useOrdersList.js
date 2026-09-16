import { ref, computed, watch } from 'vue';
import { api } from './useSession';
import { usePortalCounts } from './usePortalCounts';
import { useCockpitPagination } from './useCockpitPagination';

/**
 * Task 7: list state + loaders của OrdersView — view chỉ còn composition + render.
 * Abort/debounce/search/tab/pagination giữ nguyên hành vi.
 */
export function useOrdersList() {
	const { ordersCount } = usePortalCounts();

	const orders = ref([]);
	const loadingOrders = ref(false);
	const activeOrderTab = ref('xuong_sx');
	const orderSearchQuery = ref('');

	const currentPage = ref(1);
	const pageSize = ref(15);
	const totalOrders = ref(0);
	const totalPages = ref(1);
	const tabCounts = ref({ xuong_sx: 0, ngcs: 0, mua_ngoai: 0, all: 0 });

	async function loadOrders() {
		// S4: abort request cũ — gõ dồn dập chỉ render kết quả mới nhất (mẫu useCatalogData).
		if (listAborter) listAborter.abort();
		listAborter = typeof AbortController !== 'undefined' ? new AbortController() : null;
		const signal = listAborter ? listAborter.signal : null;
		loadingOrders.value = true;
		try {
			const data = await api('order.list_orders', {
				tab: activeOrderTab.value,
				query: orderSearchQuery.value.trim() || undefined,
				page: currentPage.value,
				page_length: pageSize.value,
			}, { get: true, ...(signal ? { signal } : {}) });
			if (signal && signal.aborted) return;
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
			if (err && err.name === 'AbortError') return;
			console.error('Error loading orders:', err);
			orders.value = [];
		} finally {
			if (signal && signal.aborted) return;
			loadingOrders.value = false;
		}
	}

	const { prevPage, nextPage, gotoPage, handleKeyDown } = useCockpitPagination({
		currentPage,
		totalPages,
		isLoading: loadingOrders,
		onReload: () => loadOrders(),
	});

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

	let searchTimer = null;
	let listAborter = null;
	watch(orderSearchQuery, () => {
		clearTimeout(searchTimer);
		searchTimer = setTimeout(() => {
			currentPage.value = 1;
			loadOrders();
		}, 250);
	});

	const masterItems = ref([]);

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

	const selectedOrderId = ref('');
	const showOrderDetail = ref(false);
	const showCreateOrderModal = ref(false);

	const selectedOrder = computed(() => {
		return orders.value.find((o) => o.name === selectedOrderId.value) || null;
	});

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

	function onOrderDelivery() {
		// ADR-006: trạng thái/số cọc do backend trả qua loadOrders; ở đây chỉ đóng drawer + refresh.
		showOrderDetail.value = false;
		loadOrders();
	}

	function applyTabFromQuery(tabVal) {
		if (tabVal && ['xuong_sx', 'ngcs', 'mua_ngoai'].includes(tabVal)) {
			activeOrderTab.value = tabVal;
		}
	}

	function cleanup() {
		clearTimeout(searchTimer);
		// P2 review: abort request đang bay khi unmount (không mutate refs sau unmount).
		if (listAborter) listAborter.abort();
	}

	return {
		orders,
		loadingOrders,
		activeOrderTab,
		orderSearchQuery,
		currentPage,
		pageSize,
		totalOrders,
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
	};
}
