import { useRoute } from 'vue-router';
import { useCatalogData } from './useCatalogData';
import { toast } from './useToast';

const VALID_TABS = ['sp', 'nvl', 'truc', 'kh', 'ncc', 'user'];

/**
 * View-logic cho CatalogView — đều pattern với useOrdersList/useQuotesFlow.
 * Bóc onAddNew + deep-link route (?tab=, ?item=) ra khỏi view;
 * data/table/pagination/drawer vẫn nằm trong useCatalogData.
 * Visual-only: không tiền/thuế/status/config.
 */
export function useCatalogView(emit) {
	const route = useRoute();
	const catalog = useCatalogData();

	function onAddNew() {
		emit('add-new', { tab: catalog.activeCatalogTab.value });
		toast.info('Dữ liệu Sản phẩm được quản lý và tạo mới trực tiếp từ ERPNext Desk.');
	}

	async function init() {
		window.addEventListener('keydown', catalog.handleKeyDown);
		await catalog.loadInitialTabData();

		const query = route?.query || {};
		const urlParams = new URLSearchParams(window.location.search);
		const tabVal = query.tab || urlParams.get('tab');
		if (tabVal && VALID_TABS.includes(tabVal)) {
			catalog.switchCatalogTab(tabVal);
		}

		const itemParam = query.item || urlParams.get('item');
		if (itemParam) {
			const found = catalog.items.value.find((x) => x.item_code === itemParam);
			if (found) catalog.openItemDetail(found);
		}
	}

	function cleanup() {
		window.removeEventListener('keydown', catalog.handleKeyDown);
	}

	return { catalog, onAddNew, init, cleanup };
}
