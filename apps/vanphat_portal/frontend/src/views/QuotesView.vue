<template>
	<div class="quotes-view-wrapper">
		<!-- Header 1 Dòng Chuẩn Cockpit: 1 Tab Chuẩn + Quick Search + Action Button -->
		<header class="page-head catalog-header-cockpit">
			<div class="order-tabs-bar catalog-tabs-bar">
				<button
					type="button"
					class="order-tab-btn active"
				>
					<span>Báo giá</span>
					<span class="tab-badge">{{ quotations.length }}</span>
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
						type="text"
						v-model="quoteSearchQuery"
						placeholder="Tìm nhanh số báo giá, khách..."
						class="catalog-search-input"
					/>
					<button
						v-if="quoteSearchQuery"
						type="button"
						class="btn-clear-search"
						title="Xóa tìm kiếm"
						@click="quoteSearchQuery = ''"
					>
						✕
					</button>
				</div>
			</div>

			<button
				type="button"
				class="btn-new-quote whitespace-nowrap flex-shrink-0"
				@click="openStep1Modal"
			>
				+ Báo giá
			</button>
		</header>

		<div class="table-container">
			<table class="data-table">
				<thead>
					<tr>
						<th style="width: 18%;">Số báo giá</th>
						<th style="width: 40%;">Khách hàng</th>
						<th style="width: 14%;">Ngày tạo</th>
						<th style="width: 16%; text-align: right;">Tổng tiền</th>
						<th style="width: 12%; text-align: center;">Trạng thái</th>
					</tr>
				</thead>
				<tbody>
					<tr v-if="loading">
						<td colspan="5" class="empty-cell">
							<div class="cockpit-empty-state">
								<span class="empty-msg">Đang tải danh sách báo giá từ ERPNext...</span>
							</div>
						</td>
					</tr>
					<tr v-else-if="!filteredQuotations.length">
						<td colspan="5" class="empty-cell">
							<div v-if="quoteSearchQuery" class="cockpit-empty-state">
								<span class="empty-msg">Không tìm thấy báo giá khớp với từ khóa "{{ quoteSearchQuery }}"</span>
								<button type="button" class="btn-empty-action" @click="quoteSearchQuery = ''">
									✕ Xóa tìm kiếm
								</button>
							</div>
							<div v-else class="cockpit-empty-state">
								<span class="empty-msg">Chưa có phiếu báo giá nào trên hệ thống</span>
								<button type="button" class="btn-empty-action btn-empty-primary" @click="openStep1Modal">
									+ Tạo báo giá R&D
								</button>
							</div>
						</td>
					</tr>
					<tr
						v-for="q in filteredQuotations"
						:key="q.name"
						class="table-row cursor-pointer"
						@click="onRowClick(q)"
					>
						<td class="font-bold text-primary whitespace-nowrap">{{ q.name }}</td>
						<td class="whitespace-nowrap truncate" :title="q.customer_name || q.party_name">
							<span class="font-medium text-white">{{ q.customer_name || q.party_name || 'Khách vãng lai' }}</span>
						</td>
						<td class="text-secondary text-num whitespace-nowrap">{{ q.transaction_date }}</td>
						<td class="text-right font-bold text-num whitespace-nowrap">{{ formatCurrency(q.grand_total) }}</td>
						<td class="text-center whitespace-nowrap">
							<span class="font-bold text-[14px]" :class="quoteStatusColorClass(q.status)">
								{{ quoteStatusLabel(q.status) }}
							</span>
						</td>
					</tr>
					<tr
						v-for="i in (filteredQuotations.length > 0 ? Math.max(0, pageSize - filteredQuotations.length) : 0)"
						:key="'quote-filler-' + i"
						class="filler-row"
						aria-hidden="true"
					>
						<td colspan="5">&nbsp;</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Thanh Phân Trang Sát Đáy Chuẩn Buồng Lái (đồng bộ OrdersView/CatalogView) -->
		<div class="cockpit-pagination-bar">
			<div class="cockpit-pagination-left">
				<span>Hiển thị</span>
				<span class="text-white font-bold">{{ startRecord }}–{{ endRecord }}</span>
				<span>trên tổng số</span>
				<span class="text-white font-bold">{{ totalQuotations }}</span>
				<span>báo giá</span>
			</div>
			<div class="cockpit-pagination-right">
				<button
					type="button"
					class="btn-page-nav"
					:disabled="currentPage <= 1 || loading"
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
					:disabled="currentPage >= totalPages || loading"
					title="Trang sau (Phím ])"
					@click="nextPage"
				>
					›
				</button>
			</div>
		</div>

		<!-- Step 1 & Step 2 Dialogs (S8: Suspense cho async chunk) -->
		<Suspense v-if="showStep1">
			<ModalStep1Sale
				:open="showStep1"
				:initial-data="step1Data"
				@close="showStep1 = false"
				@submit="onStep1Complete"
			/>
		</Suspense>

		<Suspense v-if="showStep2">
			<DrawerStep2Director
				:open="showStep2"
				:form-data="step1Data"
				:saved-data="step2Data"
				:preview-figures="figures"
				:calculation-result="calcResult"
				@close="showStep2 = false"
				@back="onStep2Back"
				@items-changed="onItemsChanged"
				@submit="onQuotationSubmit"
			/>
		</Suspense>
	</div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, defineAsyncComponent } from 'vue';
import { useRouter } from 'vue-router';
import { dialog } from 'frappe-ui';
// S8: drawers/modals nặng async — chunk riêng, render khi mở
const ModalStep1Sale = defineAsyncComponent(() => import('../components/ModalStep1Sale.vue'));
const DrawerStep2Director = defineAsyncComponent(() => import('../components/DrawerStep2Director.vue'));
import { api } from '../composables/useSession';
import { usePortalCounts } from '../composables/usePortalCounts';
import { useCockpitFormat } from '../composables/useCockpitFormat';

const router = useRouter();
const { quotesCount } = usePortalCounts();
// S7c: formatter dùng chung (xóa bản copy-paste)
const { formatCurrency } = useCockpitFormat();

const quotations = ref([]);
const loading = ref(false);
const quoteSearchQuery = ref('');

// Phân trang server (đồng bộ OrdersView: page 15 dòng, trần backend 100)
const currentPage = ref(1);
const pageSize = ref(15);
const totalQuotations = ref(0);
const totalPages = ref(1);

const startRecord = computed(() => {
	if (totalQuotations.value === 0) return 0;
	return (currentPage.value - 1) * pageSize.value + 1;
});

const endRecord = computed(() => {
	return Math.min(currentPage.value * pageSize.value, totalQuotations.value);
});

function prevPage() {
	if (currentPage.value > 1 && !loading.value) {
		currentPage.value--;
		loadQuotations();
	}
}

function nextPage() {
	if (currentPage.value < totalPages.value && !loading.value) {
		currentPage.value++;
		loadQuotations();
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

let searchTimer = null;
watch(quoteSearchQuery, () => {
	clearTimeout(searchTimer);
	searchTimer = setTimeout(() => {
		currentPage.value = 1;
		loadQuotations();
	}, 250);
});

const showStep1 = ref(false);
const showStep2 = ref(false);

const step1Data = ref({
	product_type: 'Túi đáy đứng',
	accessory: 'Có vòi',
	print_type: 'In trục',
	cylinder_status: 'Đã có trục',
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
	total_qty: '0',
	subtotal: '0 đ',
	cylinder_total: '0 đ',
	tax_amount: '0 đ',
	grand_total: '0 đ',
});

const calcResult = ref(null);

const filteredQuotations = computed(() => {
	const list = quotations.value;
	const q = quoteSearchQuery.value.trim().toLowerCase();
	if (!q) return list;
	return list.filter((item) => {
		const name = (item.name || '').toLowerCase();
		const cust = (item.customer_name || item.party_name || '').toLowerCase();
		return name.includes(q) || cust.includes(q);
	});
});

function quoteStatusLabel(status) {
	switch (status) {
		case 'Open':
		case 'Partially Ordered':
			return 'Chờ duyệt';
		case 'Ordered':
			return 'Đã lên đơn';
		case 'Lost':
			return 'Rớt';
		case 'Expired':
			return 'Hết hạn';
		default:
			return 'Nháp';
	}
}

function quoteStatusColorClass(status) {
	switch (status) {
		case 'Open':
		case 'Partially Ordered':
			return 'text-amber';
		case 'Ordered':
			return 'text-emerald';
		case 'Lost':
		case 'Expired':
			return 'text-rose';
		default:
			return 'text-secondary';
	}
}

function onRowClick(q) {
	if (q.status === 'Draft') {
		step1Data.value = {
			product_type: q.product_type || 'Túi đáy đứng',
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

async function loadQuotations() {
	loading.value = true;
	const data = await api('list_quotations', {
		query: quoteSearchQuery.value.trim() || undefined,
		page: currentPage.value,
		page_length: pageSize.value,
	}, { get: true });
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
	quotesCount.value = totalQuotations.value;
	loading.value = false;
}

function openStep1Modal() {
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
		pouch_type: step1Data.value.product_type,
		width_mm: step1Data.value.width,
		length_mm: step1Data.value.length,
		gusset_mm: step1Data.value.bottom,
		layers: step2Data.value.materials,
		spout_type: step1Data.value.accessory === 'Có vòi' ? '16mm' : '',
		desired_qty: totalDesiredQty,
		cylinder_qty: cylQty,
		target_margin: 0.30,
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
		const sub = Number(res.subtotal) || 0;
		const tax = Number(res.tax_amount) || 0;
		const grand = Number(res.grand_total) || sub;
		figures.value = {
			total_qty: String(res.total_qty ?? '0'),
			subtotal: formatCurrency(sub),
			cylinder_total: formatCurrency(cylTotal),
			tax_amount: formatCurrency(tax),
			grand_total: formatCurrency(grand),
		};
	}
}

async function onSendQuotation(q) {
	const res = await api('submit_quotation', { name: q.name });
	if (res) await loadQuotations();
}

async function onMarkLost(q) {
	dialog.prompt({
		title: 'Rớt báo giá',
		message: `Lý do rớt báo giá ${q.name}?`,
		fields: [{ name: 'reason', label: 'Lý do', type: 'text', required: true }],
		confirmLabel: 'Xác nhận rớt',
		cancelLabel: 'Để sau',
		async onConfirm(values) {
			const res = await api('mark_quotation_lost', { name: q.name, reason: values.reason });
			if (res) await loadQuotations();
		},
	});
}

async function onItemsChanged(payload = {}) {
	step2Data.value = {
		lines: (payload.lines && payload.lines.length ? payload.lines : step2Data.value.lines).map((r) => ({ ...r })),
		materials: [...(payload.materials || step2Data.value.materials)],
		cylinder_qty: payload.cylinder_qty ?? step2Data.value.cylinder_qty,
		artwork_url: payload.artwork_url ?? step2Data.value.artwork_url,
	};
	await calculatePackaging();
	await fetchPricePreview();
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

onMounted(async () => {
	window.addEventListener('keydown', handleKeyDown);
	await loadQuotations();
});

onUnmounted(() => {
	window.removeEventListener('keydown', handleKeyDown);
});

</script>

<style scoped>
.quotes-view-wrapper {
	display: flex;
	flex-direction: column;
	flex: 1;
	min-height: 0;
}
</style>
