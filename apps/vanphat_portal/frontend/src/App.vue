<template>
	<div class="portal-layout">
		<!-- Sidebar Navigation -->
	<aside class="sidebar">
		<div class="brand-block">
			<img :src="logoUrl" alt="Bao Bì Vạn Phát" class="brand-logo" />
			<div class="brand-title">BAO BÌ VẠN PHÁT</div>
		</div>

		<nav class="nav-menu">
			<button type="button" class="nav-btn">
				<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<rect x="3" y="3" width="7" height="7"></rect>
					<rect x="14" y="3" width="7" height="7"></rect>
					<rect x="14" y="14" width="7" height="7"></rect>
					<rect x="3" y="14" width="7" height="7"></rect>
				</svg>
				<span class="nav-text">Tổng quan</span>
			</button>
			<button
				type="button"
				class="nav-btn"
				:class="{ active: view === 'quotes' }"
				@click="view = 'quotes'; loadQuotations()"
			>
				<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
					<polyline points="14 2 14 8 20 8"></polyline>
					<line x1="16" y1="13" x2="8" y2="13"></line>
					<line x1="16" y1="17" x2="8" y2="17"></line>
					<polyline points="10 9 9 9 8 9"></polyline>
				</svg>
				<span class="nav-text">Báo giá</span>
				<span v-if="quotations.length" class="nav-badge">{{ quotations.length }}</span>
			</button>
			<button
				type="button"
				class="nav-btn"
				:class="{ active: view === 'orders' }"
				@click="view = 'orders'; loadOrders()"
			>
				<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<line x1="16.5" y1="9.4" x2="7.5" y2="4.21"></line>
					<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
					<polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
					<line x1="12" y1="22.08" x2="12" y2="12"></line>
				</svg>
				<span class="nav-text">Đơn hàng</span>
				<span v-if="orders.length" class="nav-badge">{{ orders.length }}</span>
			</button>
			<button type="button" class="nav-btn">
				<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
					<polyline points="2 17 12 22 22 17"></polyline>
					<polyline points="2 12 12 17 22 12"></polyline>
				</svg>
				<span class="nav-text">Sản xuất</span>
			</button>
		</nav>

		<!-- Bottom User & Logout -->
		<div class="sidebar-footer">
			<div class="user-block" :title="currentUser">
				<div class="user-avatar">
					<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
						<circle cx="12" cy="7" r="4"></circle>
					</svg>
				</div>
				<span class="user-id">{{ currentUser }}</span>
			</div>
			<button
				type="button"
				class="btn-logout"
				title="Đăng xuất"
				@click="handleLogout"
			>
				<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
					<polyline points="16 17 21 12 16 7"></polyline>
					<line x1="21" y1="12" x2="9" y2="12"></line>
				</svg>
			</button>
		</div>
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
const currentUser = ref('giamdoc@vanphat.com');

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
		if (json && json.message) {
			if (json.message.csrf_token) {
				window.vp_csrf_token = json.message.csrf_token;
			}
			if (json.message.user && json.message.user !== 'Guest') {
				currentUser.value = json.message.user;
			}
		}
	} catch (err) {
		// keep going with whatever token the host page provides
	}
}

async function handleLogout() {
	try {
		await fetch('/api/method/logout', {
			method: 'POST',
			headers: {
				'X-Frappe-CSRF-Token': csrfToken(),
			},
		});
	} catch (err) {
		// ignore
	}
	window.location.href = '/login';
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
	width: 216px;
	height: 100vh;
	position: sticky;
	top: 0;
	flex-shrink: 0;
	background: #161b22;
	border-right: 1px solid #2d333b;
	padding: 14px 10px;
	display: flex;
	flex-direction: column;
	gap: 6px;
	z-index: 10;
}

.brand-block {
	display: flex;
	align-items: center;
	gap: 9px;
	padding: 4px 6px 12px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.07);
	margin-bottom: 6px;
}

.brand-logo {
	height: 24px;
	width: auto;
	max-width: 36px;
	object-fit: contain;
	background: transparent;
	filter: drop-shadow(0 2px 6px rgba(237, 28, 36, 0.35));
}

.brand-title {
	font-weight: 800;
	letter-spacing: 0.03em;
	color: #ffffff;
	font-size: 14px;
	white-space: nowrap;
}

.nav-menu {
	display: flex;
	flex-direction: column;
	gap: 4px;
	flex: 1;
}

.nav-btn {
	display: flex;
	align-items: center;
	gap: 10px;
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
	transition: all 0.15s ease;
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

.nav-icon {
	width: 18px;
	height: 18px;
	flex-shrink: 0;
	opacity: 0.85;
}

.nav-btn.active .nav-icon {
	opacity: 1;
	stroke: #4ea1e0;
}

.nav-text {
	flex: 1;
}

.nav-badge {
	font-size: 11.5px;
	font-weight: 700;
	padding: 1px 7px;
	border-radius: 10px;
	background: rgba(255, 255, 255, 0.08);
	color: #9da7b5;
}

.nav-btn.active .nav-badge {
	background: rgba(78, 161, 224, 0.25);
	color: #4ea1e0;
}

.sidebar-footer {
	margin-top: auto;
	padding-top: 12px;
	border-top: 1px solid rgba(255, 255, 255, 0.07);
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 6px;
	padding-left: 4px;
	padding-right: 2px;
}

.user-block {
	display: flex;
	align-items: center;
	gap: 8px;
	min-width: 0;
	flex: 1;
}

.user-avatar {
	width: 28px;
	height: 28px;
	border-radius: 50%;
	background: #1f2937;
	border: 1px solid #374151;
	display: flex;
	align-items: center;
	justify-content: center;
	color: #9ca3af;
	flex-shrink: 0;
}

.user-id {
	font-size: 13px;
	font-weight: 600;
	color: #cbd5e1;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.btn-logout {
	width: 30px;
	height: 30px;
	border-radius: 6px;
	border: none;
	background: transparent;
	color: #94a3b8;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.15s ease;
	flex-shrink: 0;
}

.btn-logout:hover {
	color: #f87171;
	background: rgba(239, 68, 68, 0.12);
}

.main-content {
	flex: 1;
	min-width: 0;
	padding: 26px 36px;
}

.page-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 22px;
}

.page-title {
	font-size: 22px;
	font-weight: 800;
	color: #eef1f6;
	letter-spacing: -0.01em;
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
	padding: 11px 22px;
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
	font-size: 15px;
}

.data-table th {
	text-align: left;
	font-size: 13.5px;
	font-weight: 700;
	text-transform: uppercase;
	letter-spacing: 0.04em;
	color: #9da7b5;
	padding: 14px 18px;
	border-bottom: 1px solid #3a424e;
	background: #1a1f27;
}

.data-table td {
	padding: 14px 18px;
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
	font-size: 13px;
	font-weight: 700;
	padding: 4px 10px;
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
	font-size: 13px;
	font-weight: 700;
	color: #4ea1e0;
	background: rgba(78, 161, 224, 0.12);
	border: 1px solid rgba(78, 161, 224, 0.4);
	border-radius: 6px;
	padding: 5px 12px;
	margin: 0 2px;
	cursor: pointer;
	transition: all 0.15s;
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
