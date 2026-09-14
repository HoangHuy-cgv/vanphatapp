<template>
	<div class="quotes-view-wrapper">
		<header class="page-head">
			<h2 class="page-title">Báo giá</h2>
			<button
				type="button"
				class="btn-new-quote"
				@click="openStep1Modal"
			>
				+ Báo giá
			</button>
		</header>

		<div class="table-container">
			<table class="data-table">
				<thead>
					<tr>
						<th style="width: 14%;">Số báo giá</th>
						<th style="width: 18%;">Khách hàng</th>
						<th style="width: 11%;">Ngày tạo</th>
						<th style="width: 15%; text-align: right;">Tổng tiền</th>
						<th style="width: 12%; text-align: center;">Trạng thái</th>
						<th style="width: 30%;">Thao tác</th>
					</tr>
				</thead>
				<tbody>
					<tr v-if="loading">
						<td colspan="6" style="text-align: center; padding: 40px 0; color: #9da7b5;">
							Đang tải danh sách báo giá...
						</td>
					</tr>
					<tr v-else-if="!quotations.length">
						<td colspan="6" style="text-align: center; padding: 40px 0; color: #9da7b5;">
							Chưa có báo giá nào. Bấm <b>+ Báo giá</b> để tạo mới.
						</td>
					</tr>
					<tr v-for="q in quotations" :key="q.name" class="table-row">
						<td class="font-bold text-primary">{{ q.name }}</td>
						<td>{{ q.customer_name || q.party_name || 'Khách vãng lai' }}</td>
						<td class="text-secondary text-num">{{ q.transaction_date }}</td>
						<td class="text-right font-bold text-num">{{ formatCurrency(q.grand_total) }}</td>
						<td class="text-center">
							<span class="status-badge" :class="statusClass(q.status)">
								{{ q.status || 'Draft' }}
							</span>
						</td>
						<td class="row-actions">
							<button
								v-if="q.status === 'Draft'"
								type="button"
								class="row-btn row-btn-primary"
								@click="onSendQuotation(q)"
							>
								Gửi
							</button>
							<button
								v-if="q.status === 'Open'"
								type="button"
								class="row-btn row-btn-primary"
								@click="onMakeOrder(q)"
							>
								Tạo ĐH
							</button>
							<button
								v-if="q.status === 'Open'"
								type="button"
								class="row-btn row-btn-danger"
								@click="onMarkLost(q)"
							>
								Rớt
							</button>
							<span v-if="q.status === 'Ordered'" class="text-secondary" style="font-size: 13px;">
								✓ Đã lên đơn
							</span>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Step 1 & Step 2 Dialogs -->
		<ModalStep1Sale
			v-if="showStep1"
			:open="showStep1"
			:initial-data="step1Data"
			@close="showStep1 = false"
			@submit="onStep1Complete"
		/>

		<DrawerStep2Director
			v-if="showStep2"
			:open="showStep2"
			:step1-data="step1Data"
			:initial-lines="step2Data.lines"
			:initial-materials="step2Data.materials"
			:initial-cylinder-qty="step2Data.cylinder_qty"
			:initial-artwork-url="step2Data.artwork_url"
			:figures="figures"
			:calc-result="calcResult"
			@close="showStep2 = false"
			@back="onStep2Back"
			@items-changed="onItemsChanged"
			@submit="onQuotationSubmit"
		/>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import ModalStep1Sale from '../components/ModalStep1Sale.vue';
import DrawerStep2Director from '../components/DrawerStep2Director.vue';
import { INITIAL_QUOTATIONS } from '../data/mockData';
import { api } from '../composables/useSession';
import { usePortalCounts } from '../composables/usePortalCounts';

const router = useRouter();
const { quotesCount } = usePortalCounts();

const quotations = ref([]);
const loading = ref(false);

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
	materials: ['OPP', 'PE sữa'],
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

function formatCurrency(val) {
	if (val == null || val === '') return '0 đ';
	if (typeof val === 'string' && isNaN(Number(val))) return val;
	return Number(val).toLocaleString('vi-VN') + ' đ';
}

function statusClass(status) {
	switch (status || 'Draft') {
		case 'Open':
		case 'Partially Ordered':
			return 'status-open';
		case 'Ordered':
			return 'status-ordered';
		case 'Lost':
			return 'status-lost';
		case 'Expired':
			return 'status-expired';
		default:
			return 'status-draft';
	}
}

async function loadQuotations() {
	loading.value = true;
	const data = await api('list_quotations');
	if (Array.isArray(data) && data.length > 0) {
		quotations.value = data;
	} else if (quotations.value.length === 0) {
		quotations.value = [...INITIAL_QUOTATIONS];
	}
	quotesCount.value = quotations.value.length;
	loading.value = false;
}

function openStep1Modal() {
	showStep1.value = true;
}

async function calculatePackaging() {
	const totalDesiredQty =
		step2Data.value.lines.reduce((s, r) => s + (Number(r.qty) || 0), 0) || 5000;
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
				qty: 5000,
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
	const res = await api('get_price_preview', { quotation: '', lines: step2Data.value.lines });
	const isPrintCylinder =
		step1Data.value.print_type === 'In trục' &&
		step1Data.value.cylinder_status === 'Chưa có trục';
	const cylTotal = isPrintCylinder ? (calcResult.value?.cylinder_quote?.total || 0) : 0;

	if (res) {
		const sub = Number(res.subtotal) || 0;
		const tax = Number(res.tax_amount) || Math.round(sub * 0.08);
		const grand = Number(res.grand_total) || (sub + cylTotal + tax);
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
	const reason = window.prompt(`Lý do rớt báo giá ${q.name}?`, '');
	if (reason === null) return;
	const res = await api('mark_quotation_lost', { name: q.name, reason });
	if (res) await loadQuotations();
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
	await loadQuotations();
});

defineExpose({
	loadQuotations,
	openStep1Modal,
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
