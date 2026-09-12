<template>
	<div class="portal-layout">
		<!-- Sidebar Navigation -->
	<aside class="sidebar">
		<div class="brand-block">
			<img :src="logoUrl" alt="Bao Bì Vạn Phát" class="brand-logo" />
			<div class="brand-title">VẠN PHÁT</div>
		</div>
		<nav class="nav-menu">
			<button type="button" class="nav-btn">Tổng quan</button>
			<button
				type="button"
				class="nav-btn"
				:class="{ active: view === 'quotes' }"
				@click="view = 'quotes'; loadQuotations()"
			>
				Báo giá
			</button>
			<button
				type="button"
				class="nav-btn"
				:class="{ active: view === 'orders' }"
				@click="view = 'orders'; loadOrders()"
			>
				Đơn hàng
			</button>
			<button type="button" class="nav-btn">Sản xuất</button>
		</nav>
	</aside>

		<!-- Main Content Area -->
		<main class="main-content">
			<header class="page-head">
				<h2 class="page-title">{{ view === 'orders' ? 'Danh sách Đơn hàng' : 'Danh sách Báo giá' }}</h2>
				<button
					v-if="view === 'quotes'"
					type="button"
					class="btn-new-quote"
					@click="openStep1Modal"
				>
					+ Báo giá
				</button>
			</header>

			<!-- Quotation Table -->
			<div v-if="view === 'quotes'" class="table-container">
				<table class="data-table">
					<thead>
						<tr>
							<th style="width: 12%;">Ngày</th>
							<th style="width: 16%;">Mã báo giá</th>
							<th style="width: 26%;">Khách hàng & Brand</th>
							<th style="width: 14%; text-align: right;">Tổng tiền</th>
							<th style="width: 14%; text-align: center;">Trạng thái</th>
							<th style="width: 18%; text-align: center;">Thao tác</th>
						</tr>
					</thead>
					<tbody>
						<tr
							v-for="q in quotations"
							:key="q.name"
							class="table-row"
						>
							<td class="text-secondary">{{ q.transaction_date || '—' }}</td>
							<td class="font-bold text-primary">{{ q.name }}</td>
							<td class="font-bold">{{ q.customer_name || '—' }}</td>
							<td class="text-right font-bold text-num">{{ formatCurrency(q.grand_total) }}</td>
							<td class="text-center">
								<span class="status-badge" :class="statusClass(q.status)">{{ q.status || 'Draft' }}</span>
							</td>
							<td class="text-center row-actions">
								<button
									v-if="(q.status || 'Draft') === 'Draft'"
									type="button"
									class="row-btn"
									@click="onSendQuotation(q)"
								>
									Gửi QLSX
								</button>
								<button
									v-if="['Open', 'Partially Ordered'].includes(q.status || '')"
									type="button"
									class="row-btn row-btn-primary"
									@click="onMakeOrder(q)"
								>
									Chốt
								</button>
								<button
									v-if="['Draft', 'Open'].includes(q.status || 'Draft')"
									type="button"
									class="row-btn row-btn-danger"
									@click="onMarkLost(q)"
								>
									Rớt
								</button>
								<span v-else-if="!['Draft', 'Open', 'Partially Ordered'].includes(q.status || 'Draft')" class="text-secondary">—</span>
							</td>
						</tr>
						<tr v-if="quotations.length === 0">
							<td colspan="6" class="empty-cell">
								{{ loading ? 'Đang tải dữ liệu...' : 'Chưa có báo giá nào trong hệ thống.' }}
							</td>
						</tr>
					</tbody>
				</table>
			</div>

			<!-- Sales Order Table -->
			<div v-else class="table-container">
				<table class="data-table">
					<thead>
						<tr>
							<th style="width: 14%;">Ngày</th>
							<th style="width: 18%;">Mã đơn</th>
							<th style="width: 32%;">Khách hàng</th>
							<th style="width: 18%; text-align: right;">Tổng tiền</th>
							<th style="width: 18%; text-align: center;">Trạng thái</th>
						</tr>
					</thead>
					<tbody>
						<tr
							v-for="o in orders"
							:key="o.name"
							class="table-row"
						>
							<td class="text-secondary">{{ o.transaction_date || '—' }}</td>
							<td class="font-bold text-primary">{{ o.name }}</td>
							<td class="font-bold">{{ o.customer || '—' }}</td>
							<td class="text-right font-bold text-num">{{ formatCurrency(o.grand_total) }}</td>
							<td class="text-center">
								<span class="status-badge" :class="statusClass(o.status)">{{ o.status || 'Draft' }}</span>
							</td>
						</tr>
						<tr v-if="orders.length === 0">
							<td colspan="5" class="empty-cell">
								{{ loadingOrders ? 'Đang tải dữ liệu...' : 'Chưa có đơn hàng nào trong hệ thống.' }}
							</td>
						</tr>
					</tbody>
				</table>
			</div>
		</main>

		<!-- Step 1: Sale Modal -->
		<ModalStep1Sale
			v-if="showStep1"
			:initial-data="step1Data"
			@close="showStep1 = false"
			@next="onStep1Complete"
		/>

		<!-- Step 2: Director Drawer -->
	<DrawerStep2Director
		v-if="showStep2"
		:form-data="step1Data"
		:preview-figures="figures"
		:saved-data="step2Data"
		@close="showStep2 = false"
		@back="onStep2Back"
		@items-changed="onItemsChanged"
		@submit="onQuotationSubmit"
	/>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import ModalStep1Sale from './components/ModalStep1Sale.vue';
import DrawerStep2Director from './components/DrawerStep2Director.vue';
import logoUrl from './assets/logo-vanphat.png';

const view = ref('quotes');
const quotations = ref([]);
const loading = ref(false);
const orders = ref([]);
const loadingOrders = ref(false);

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
	materials: ['OPP', 'PE'],
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

// API Caller wrapper
function csrfToken() {
	return window.vp_csrf_token || window.frappe_csrf_token || '';
}

async function api(method, args = {}) {
	try {
		const res = await fetch(`/api/method/vanphat_portal.api.bao_gia.${method}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-Frappe-CSRF-Token': csrfToken(),
			},
			body: JSON.stringify(args),
		});
		const json = await res.json();
		return json.message;
	} catch (err) {
		return null;
	}
}

async function boot() {
	try {
		const res = await fetch('/api/method/vanphat_portal.api.bao_gia.get_boot');
		const json = await res.json();
		if (json && json.message && json.message.csrf_token) {
			window.vp_csrf_token = json.message.csrf_token;
		}
	} catch (err) {
		// keep going with whatever token the host page provides
	}
}

async function loadQuotations() {
	loading.value = true;
	const data = await api('list_quotations');
	if (Array.isArray(data)) {
		quotations.value = data;
	}
	loading.value = false;
}

function openStep1Modal() {
	showStep1.value = true;
}

function onStep1Complete(payload) {
	step1Data.value = payload;
	showStep1.value = false;
	showStep2.value = true;
	fetchPricePreview();
}

function onStep2Back() {
	showStep2.value = false;
	showStep1.value = true;
}

async function fetchPricePreview() {
	const res = await api('get_price_preview', { quotation: '', lines: step2Data.value.lines });
	if (res) {
		figures.value = {
			total_qty: String(res.total_qty ?? '0'),
			subtotal: formatCurrency(res.subtotal),
			cylinder_total: formatCurrency(res.cylinder_total),
			tax_amount: formatCurrency(res.tax_amount),
			grand_total: formatCurrency(res.grand_total),
		};
	}
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

function onItemsChanged(payload = {}) {
	step2Data.value = {
		lines: (payload.lines && payload.lines.length ? payload.lines : step2Data.value.lines).map((r) => ({ ...r })),
		materials: [...(payload.materials || step2Data.value.materials)],
		cylinder_qty: payload.cylinder_qty ?? step2Data.value.cylinder_qty,
		artwork_url: payload.artwork_url ?? step2Data.value.artwork_url,
	};
	fetchPricePreview();
}

async function onQuotationSubmit(payload) {
	const res = await api('create_quotation', { payload });
	if (res && res.name) {
		showStep2.value = false;
		await loadQuotations();
	}
}

async function loadOrders() {
	loadingOrders.value = true;
	const data = await api('list_orders');
	if (Array.isArray(data)) {
		orders.value = data;
	}
	loadingOrders.value = false;
}

async function onMakeOrder(q) {
	const res = await api('make_order_from_quotation', { name: q.name });
	if (res && res.sales_order) {
		await loadQuotations();
		view.value = 'orders';
		await loadOrders();
	}
}
function formatCurrency(val) {
	if (val == null || val === '') return '0 đ';
	if (typeof val === 'string' && isNaN(Number(val))) return val;
	return Number(val).toLocaleString('vi-VN') + ' đ';
}

onMounted(async () => {
	await boot();
	loadQuotations();
});
</script>

<style>
:root {
	--canvas: #12151a;
	--surface: #161b22;
	--surface-low: #1a1f27;
	--outline: #3a424e;
	--outline-focus: #4ea1e0;
	--ink: #eef1f6;
	--ink-secondary: #9da7b5;
	--ink-muted: #64748b;
	--primary: #4ea1e0;
	--primary-press: #3b8ac4;
	--blocked: #f97066;
	--ok: #51cf66;
	--warn: #fec84b;
	--font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

*, *::before, *::after {
	box-sizing: border-box;
	margin: 0;
	padding: 0;
}

html, body {
	height: 100%;
	font-family: var(--font-sans);
	background: var(--canvas);
	color: var(--ink);
	-webkit-font-smoothing: antialiased;
}
</style>

<style scoped>
.portal-layout {
	display: flex;
	min-height: 100vh;
}

.sidebar {
	width: 200px;
	flex-shrink: 0;
	background: #161b22;
	border-right: 1px solid #3a424e;
	padding: 18px 12px;
	display: flex;
	flex-direction: column;
	gap: 6px;
}
.brand-block {
	display: flex;
	align-items: center;
	gap: 10px;
	padding: 4px 10px 14px;
}

.brand-logo {
	width: 36px;
	height: 36px;
	object-fit: contain;
	border-radius: 8px;
	background: #ffffff;
	padding: 3px;
}

.brand-title {
	font-weight: 800;
	letter-spacing: 0.04em;
	color: #eef1f6;
	font-size: 16px;
}

.nav-btn {
	display: block;
	width: 100%;
	text-align: left;
	background: transparent;
	border: 0;
	border-radius: 8px;
	color: #9da7b5;
	font-size: 14.5px;
	font-weight: 600;
	padding: 9px 12px;
	cursor: pointer;
	transition: all 0.15s;
}

.nav-btn:hover {
	color: #eef1f6;
	background: rgba(255, 255, 255, 0.04);
}

.nav-btn.active {
	background: rgba(78, 161, 224, 0.14);
	color: #4ea1e0;
	font-weight: 700;
}

.main-content {
	flex: 1;
	min-width: 0;
	padding: 24px 32px;
}

.page-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 20px;
}

.page-title {
	font-size: 20px;
	font-weight: 800;
	color: #eef1f6;
}

.btn-new-quote {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	font-family: inherit;
	font-size: 15px;
	font-weight: 700;
	color: #ffffff;
	background: #4ea1e0;
	border: 0;
	border-radius: 8px;
	padding: 10px 20px;
	cursor: pointer;
	transition: background 0.15s;
}

.btn-new-quote:hover {
	background: #3b8ac4;
}

.table-container {
	background: #161b22;
	border: 1px solid #3a424e;
	border-radius: 12px;
	overflow: hidden;
}

.data-table {
	width: 100%;
	border-collapse: collapse;
	font-size: 14.5px;
}

.data-table th {
	text-align: left;
	font-size: 12.5px;
	font-weight: 700;
	text-transform: uppercase;
	letter-spacing: 0.04em;
	color: #9da7b5;
	padding: 12px 16px;
	border-bottom: 1px solid #3a424e;
	background: #1a1f27;
}

.data-table td {
	padding: 12px 16px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.05);
	color: #eef1f6;
}

.table-row:hover {
	background: rgba(255, 255, 255, 0.02);
}

.text-secondary {
	color: #9da7b5;
}

.text-primary {
	color: #4ea1e0;
}

.font-bold {
	font-weight: 700;
}

.text-right {
	text-align: right;
}

.text-center {
	text-align: center;
}

.text-num {
	font-variant-numeric: tabular-nums;
}

.status-badge {
	display: inline-block;
	font-size: 12.5px;
	font-weight: 700;
	padding: 3px 8px;
	border-radius: 6px;
}

.status-open {
	background: rgba(254, 200, 75, 0.14);
	color: #fec84b;
}

.status-draft {
	background: rgba(157, 167, 181, 0.14);
	color: #9da7b5;
}

.status-ordered {
	background: rgba(81, 207, 102, 0.14);
	color: #51cf66;
}

.status-lost {
	background: rgba(100, 116, 139, 0.2);
	color: #64748b;
}

.status-expired {
	background: rgba(249, 112, 102, 0.14);
	color: #f97066;
}

.row-actions {
	white-space: nowrap;
}

.row-btn {
	display: inline-block;
	font-family: inherit;
	font-size: 12px;
	font-weight: 700;
	color: #4ea1e0;
	background: rgba(78, 161, 224, 0.12);
	border: 1px solid rgba(78, 161, 224, 0.4);
	border-radius: 6px;
	padding: 4px 10px;
	margin: 0 2px;
	cursor: pointer;
}

.row-btn-danger {
	color: #f97066;
	background: rgba(249, 112, 102, 0.1);
	border-color: rgba(249, 112, 102, 0.4);
}

.row-btn-primary {
	color: #ffffff;
	background: #4ea1e0;
	border-color: #4ea1e0;
}
</style>
