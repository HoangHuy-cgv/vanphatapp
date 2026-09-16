import { ref, watch } from 'vue';
import { api } from './useSession';
import { usePortalCounts } from './usePortalCounts';
import { useCockpitFormat } from './useCockpitFormat';
import { useCockpitPagination } from './useCockpitPagination';
import { useQuoteDefaults, pouchKeyOf } from './useQuoteDefaults';

/**
 * Task 7: toàn bộ flow báo giá của QuotesView (list + step1/step2/preview/submit)
 * — view chỉ còn composition + render.
 */
export function useQuotesFlow(router) {
	const { quotesCount } = usePortalCounts();
	const { formatCurrency } = useCockpitFormat();

	const quotations = ref([]);
	const loading = ref(false);
	const quoteSearchQuery = ref('');

	const currentPage = ref(1);
	const pageSize = ref(15);
	const totalQuotations = ref(0);
	const totalPages = ref(1);

	async function loadQuotations() {
		// S4: abort request cũ — gõ dồn dập chỉ render kết quả mới nhất (mẫu useCatalogData).
		// P2 review: try/catch/finally như useOrdersList — lỗi mạng không kẹt loading.
		if (listAborter) listAborter.abort();
		listAborter = typeof AbortController !== 'undefined' ? new AbortController() : null;
		const signal = listAborter ? listAborter.signal : null;
		loading.value = true;
		try {
			const data = await api('list_quotations', {
				query: quoteSearchQuery.value.trim() || undefined,
				page: currentPage.value,
				page_length: pageSize.value,
			}, { get: true, ...(signal ? { signal } : {}) });
			if (signal && signal.aborted) return;
			if (data && Array.isArray(data.quotations)) {
				quotations.value = data.quotations;
				totalQuotations.value = data.total_count ?? data.quotations.length;
				totalPages.value = data.total_pages || 1;
			} else if (Array.isArray(data)) {
				// Tương thích mock/backend cũ trả mảng trần
				quotations.value = data;
				totalQuotations.value = data.length;
				totalPages.value = Math.ceil(data.length / pageSize.value) || 1;
			} else {
				quotations.value = [];
				totalQuotations.value = 0;
				totalPages.value = 1;
			}
			if (signal && signal.aborted) return;
			quotesCount.value = totalQuotations.value;
		} catch (err) {
			if (err && err.name === 'AbortError') return;
			console.error('Error loading quotations:', err);
			quotations.value = [];
		} finally {
			if (signal && signal.aborted) return;
			loading.value = false;
		}
	}

	const { prevPage, nextPage, gotoPage, handleKeyDown } = useCockpitPagination({
		currentPage,
		totalPages,
		isLoading: loading,
		onReload: () => loadQuotations(),
	});

	let searchTimer = null;
	let listAborter = null;
	watch(quoteSearchQuery, () => {
		clearTimeout(searchTimer);
		searchTimer = setTimeout(() => {
			currentPage.value = 1;
			loadQuotations();
		}, 250);
	});

	const showStep1 = ref(false);
	const showStep2 = ref(false);

	// S2: defaults config-native (get_product_groups/get_print_config), trống thì bắt chọn.
	const { productTypes, printTechs, accessories, loadQuoteDefaults } = useQuoteDefaults();

	const step1Data = ref({
		product_type: '',
		accessory: '',
		print_type: '',
		cylinder_status: '',
		customer: '',
		customer_id: '',
		brand: '',
		description: '',
		length: '',
		width: '',
		thickness: '',
		bottom: '',
	});

	const step2Data = ref({
		lines: [{ item_name: '', qty: '', rate: '' }],
		// ADR-006: vật liệu mặc định là nợ config-native (plan item 13). Tạm để trống —
		// người dùng click-chọn ở Drawer, không mặc định cứng thay ý GĐ.
		materials: [],
		cylinder_qty: 1,
		artwork_url: '',
	});

	const figures = ref({
		total_qty: '—',
		subtotal: '—',
		cylinder_total: '—',
		tax_amount: '—',
		vat_rate: null,
		grand_total: '—',
	});

	const calcResult = ref(null);

	// S5: search 1 lớp duy nhất ở server (loadQuotations gửi query) — bỏ filter client trùng.
	function onRowClick(q, { onMakeOrder, dialog }) {
		if (q.status === 'Draft') {
			// P2 review: spread giữ keys cũ (accessory/print_type/cylinder_status/
			// customer_id) rồi override — gán thay thế làm mất keys, sai cylQty/pouch.
			step1Data.value = {
				...step1Data.value,
				// S2: giữ giá trị draft đã lưu, không default cứng (trống thì Step 1 bắt chọn).
				product_type: q.product_type || '',
				customer: q.customer_name || q.party_name || '',
				brand: q.brand || '',
				description: q.dimensions || '',
				length: '',
				width: '',
				thickness: '',
				bottom: '',
			};
			step2Data.value = {
				lines: q.lines || [{ item_name: q.customer_name || 'Mẫu in', qty: '', rate: '' }],
				materials: q.materials || [],
				cylinder_qty: q.cylinder_qty || 0,
				artwork_url: '',
			};
			showStep2.value = true;
		} else if (q.status === 'Open') {
			dialog.confirm({
				title: 'Tạo đơn hàng',
				message: `Tạo đơn hàng từ báo giá ${q.name}?`,
				confirmLabel: 'Tạo đơn',
				cancelLabel: 'Để sau',
				onConfirm: () => onMakeOrder(q),
			});
		}
	}

	function openStep1Modal() {
		// S2: mở Step 1 với options config-native đã load (trống thì form bắt chọn).
		loadQuoteDefaults();
		showStep1.value = true;
	}

	async function calculatePackaging() {
		// ADR-006: số lượng/tiền do backend tính từ lines thô. Client chỉ gom lines gửi
		// lên — có dòng qty > 0 mới gọi, không tự cộng/fallback số thương mại ở đây.
		const lines = (step2Data.value.lines || [])
			.map((r) => ({
				qty: Number(r.qty) || 0,
				rate: Number(r.rate) || 0,
				item_name: r.item_name || '',
			}))
			.filter((r) => r.qty > 0);
		if (!lines.length) return null;
		// 1 dòng: dùng luôn qty đó. Nhiều dòng: hỏi backend tổng trước (không tự cộng).
		let totalDesiredQty = 0;
		if (lines.length === 1) {
			totalDesiredQty = lines[0].qty;
		} else {
			const preview = await api('bao_gia.get_quotation_price_preview', { lines }, { silent: true });
			totalDesiredQty = Number(preview?.total_qty) || 0;
			if (!totalDesiredQty) return null;
		}
		const isPrintCylinder =
			step1Data.value.print_type === 'In trục' &&
			step1Data.value.cylinder_status === 'Chưa có trục';
		const cylQty = isPrintCylinder ? Number(step2Data.value.cylinder_qty) || 1 : 0;

		const res = await api('calculate_packaging_quotation', {
			// S2: pouch_key kỹ thuật (compute_pouch_area) + KHÔNG gửi target_margin
			// (backend default 0.30 = chuẩn 30% Sếp chốt, skill packaging §3.3).
			pouch_type: pouchKeyOf(step1Data.value.product_type),
			width_mm: step1Data.value.width,
			length_mm: step1Data.value.length,
			gusset_mm: step1Data.value.bottom,
			layers: step2Data.value.materials,
			spout_type: step1Data.value.accessory === 'Có vòi' ? '16mm' : '',
			desired_qty: totalDesiredQty,
			cylinder_qty: cylQty,
		});

		if (res) {
			calcResult.value = res;
			return res;
		}
		return null;
	}

	async function onStep1Complete(payload) {
		step1Data.value = payload;
		showStep1.value = false;
		showStep2.value = true;
		if (!step2Data.value.lines || !step2Data.value.lines.length || !step2Data.value.lines[0].item_name) {
			step2Data.value.lines = [
				{
					item_name: step1Data.value.description || 'Mẫu in chính',
					qty: '',
					rate: '',
				},
			];
		}
		await fetchPricePreview();
	}

	function onStep2Back() {
		showStep2.value = false;
		showStep1.value = true;
	}

	async function fetchPricePreview() {
		const res = await api('bao_gia.get_quotation_price_preview', { quotation: '', lines: step2Data.value.lines });
		const isPrintCylinder =
			step1Data.value.print_type === 'In trục' &&
			step1Data.value.cylinder_status === 'Chưa có trục';
		const cylTotal = isPrintCylinder ? (calcResult.value?.cylinder_quote?.total || 0) : 0;

		if (res) {
			// S1: grand lấy server nguyên, không fallback che invariant
			// product_total + cylinder_total + vat_amount = grand_total (docs/API.md).
			const sub = Number(res.subtotal);
			const tax = Number(res.tax_amount);
			const grand = Number(res.grand_total);
			figures.value = {
				total_qty: String(res.total_qty ?? '—'),
				subtotal: Number.isFinite(sub) ? formatCurrency(sub) : '—',
				cylinder_total: formatCurrency(cylTotal),
				tax_amount: Number.isFinite(tax) ? formatCurrency(tax) : '—',
				vat_rate: res.vat_rate ?? null,
				grand_total: Number.isFinite(grand) ? formatCurrency(grand) : '—',
			};
		} else {
			// Server không trả preview: truthful trống, không số bịa.
			figures.value = {
				total_qty: '—',
				subtotal: '—',
				cylinder_total: '—',
				tax_amount: '—',
				vat_rate: null,
				grand_total: '—',
			};
		}
	}

	let itemsTimer = null;
	async function onItemsChanged(payload = {}) {
		step2Data.value = {
			lines: (payload.lines && payload.lines.length ? payload.lines : step2Data.value.lines).map((r) => ({ ...r })),
			materials: [...(payload.materials || step2Data.value.materials)],
			cylinder_qty: payload.cylinder_qty ?? step2Data.value.cylinder_qty,
			artwork_url: payload.artwork_url ?? step2Data.value.artwork_url,
		};
		// S4: debounce 300ms — sửa dòng dồn dập chỉ tính 1 lần, không 2 API/keystroke.
		clearTimeout(itemsTimer);
		itemsTimer = setTimeout(async () => {
			await calculatePackaging();
			await fetchPricePreview();
		}, 300);
	}

	async function onQuotationSubmit(payload) {
		const res = await api('create_quotation', { payload });
		if (res && res.name) {
			showStep2.value = false;
			await loadQuotations();
		}
	}

	async function onMakeOrder(q) {
		const res = await api('make_order_from_quotation', { name: q.name });
		if (res && res.sales_order) {
			await loadQuotations();
			if (router) {
				router.push({ path: '/orders', query: { order: res.sales_order } });
			} else {
				window.location.hash = `#/orders?order=${encodeURIComponent(res.sales_order)}`;
			}
		}
	}

	function cleanup() {
		clearTimeout(searchTimer);
		clearTimeout(itemsTimer);
		// P2 review: abort request đang bay khi unmount (không mutate refs sau unmount).
		if (listAborter) listAborter.abort();
	}

	return {
		quotations,
		loading,
		quoteSearchQuery,
		currentPage,
		pageSize,
		totalQuotations,
		totalPages,
		showStep1,
		showStep2,
		productTypes,
		printTechs,
		accessories,
		step1Data,
		step2Data,
		figures,
		calcResult,
		prevPage,
		nextPage,
		gotoPage,
		handleKeyDown,
		loadQuotations,
		loadQuoteDefaults,
		onRowClick,
		openStep1Modal,
		calculatePackaging,
		onStep1Complete,
		onStep2Back,
		fetchPricePreview,
		onItemsChanged,
		onQuotationSubmit,
		onMakeOrder,
		cleanup,
	};
}
