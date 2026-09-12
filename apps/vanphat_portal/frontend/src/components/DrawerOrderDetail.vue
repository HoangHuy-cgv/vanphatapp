<template>
	<div v-if="isOpen" class="drawer-overlay" @click.self="$emit('close')">
		<aside class="drawer-panel">
			<!-- Header -->
			<div class="drawer-header">
				<div>
					<div class="flex items-center gap-2">
						<span class="order-id">{{ order?.name || orderId }}</span>
						<span class="status-badge" :class="statusClass(order?.status, order?.docstatus)">
							{{ statusText(order?.status, order?.docstatus) }}
						</span>
					</div>
					<div class="customer-subtitle">
						Khách hàng: <b>{{ order?.customer_name || order?.customer || '—' }}</b>
					</div>
				</div>
				<button type="button" class="btn-close" @click="$emit('close')">✕</button>
			</div>

			<!-- Body (Loading / Content) -->
			<div v-if="loading" class="drawer-loading">
				Đang tải thông tin đơn hàng...
			</div>

			<div v-else-if="order" class="drawer-body">
				<!-- 1. Thẻ Tài Chính & Tiến Độ Cọc -->
				<div class="financial-card">
					<div class="financial-row">
						<div>
							<div class="lbl">TỔNG TIỀN (VAT)</div>
							<div class="val text-num">{{ formatCurrency(order.grand_total) }}</div>
						</div>
						<div class="text-right">
							<div class="lbl">ĐÃ CỌC</div>
							<div class="val val-deposit text-num">
								{{ formatCurrency(order.advance_paid) }}
								<span class="pct-badge">({{ order.deposit_pct }}%)</span>
							</div>
						</div>
					</div>

					<!-- Progress bar -->
					<div class="deposit-track">
						<div
							class="deposit-fill"
							:style="{ width: Math.min(100, order.deposit_pct) + '%' }"
							:class="order.deposit_pct >= 30 ? 'bg-emerald' : 'bg-amber'"
						></div>
						<div class="marker-30" title="Mốc cọc tối thiểu 30%"></div>
					</div>
					<div class="flex-between text-xs mt-1 text-secondary">
						<span>Mốc cọc tối thiểu 30% để chạy đơn</span>
						<span class="text-num">Còn nợ: <b class="text-white">{{ formatCurrency(order.outstanding_amount) }}</b></span>
					</div>
				</div>

				<!-- 2. Danh Sách Mặt Hàng Đặt -->
				<div class="section-box">
					<div class="section-title">DANH SÁCH MẶT HÀNG</div>
					<table class="items-table">
						<thead>
							<tr>
								<th>Tên hàng</th>
								<th style="width: 20%; text-align: right;">SL</th>
								<th style="width: 25%; text-align: right;">Đơn giá</th>
								<th style="width: 25%; text-align: right;">Thành tiền</th>
							</tr>
						</thead>
						<tbody>
							<tr v-for="(it, idx) in order.items" :key="idx">
								<td class="font-semibold">{{ it.item_name }}</td>
								<td class="text-right text-num">{{ formatNumber(it.qty) }} {{ it.uom || 'Túi' }}</td>
								<td class="text-right text-num">{{ formatCurrency(it.rate) }}</td>
								<td class="text-right text-num font-bold">{{ formatCurrency(it.amount) }}</td>
							</tr>
							<tr v-if="!order.items || order.items.length === 0">
								<td colspan="4" class="text-center text-secondary py-3">Chưa có chi tiết mặt hàng</td>
							</tr>
						</tbody>
					</table>
				</div>

				<!-- 3. Hộp Ghi Nhận Tiền Cọc (Khi đơn còn ở trạng thái Nháp) -->
				<div v-if="order.docstatus === 0" class="section-box">
					<div class="section-title">XÁC NHẬN TIỀN CỌC</div>

					<div class="deposit-form">
						<div class="input-group">
							<label>Số tiền cọc bổ sung (đ):</label>
							<input
								v-model="depositInput"
								type="number"
								placeholder="Nhập số tiền khách cọc..."
								class="input-dark text-num"
							/>
						</div>

						<div class="checkbox-group">
							<label class="checkbox-label">
								<input v-model="isVipGuarantee" type="checkbox" />
								<span>Khách VIP: Bảo lãnh công nợ gối đầu (cho phép duyệt đơn không cần cọc trước)</span>
							</label>
						</div>

						<div class="input-group mt-2">
							<label>Ghi chú chuyển khoản / biên lai:</label>
							<input
								v-model="depositNote"
								type="text"
								placeholder="Ví dụ: VCB 09:15 ngày 12/09, cọc 50%..."
								class="input-dark"
							/>
						</div>

						<div class="mt-3 flex gap-2">
							<button
								type="button"
								class="btn-action btn-secondary"
								:disabled="savingDeposit || (!depositInput && !isVipGuarantee)"
								@click="handleSaveDeposit"
							>
								{{ savingDeposit ? 'Đang lưu...' : 'Lưu Tiền Cọc' }}
							</button>
						</div>
					</div>
				</div>

				<!-- 4. Hộp Submit Đơn Đặt Hàng -->
				<div v-if="order.docstatus === 0" class="submit-box">
					<div class="submit-info">
						<div v-if="order.can_submit || isVipGuarantee" class="text-emerald text-sm font-semibold">
							✓ Đã đủ điều kiện để kích hoạt đơn hàng chính thức.
						</div>
						<div v-else class="text-amber text-sm font-semibold">
							⚠️ Đơn hàng cần cọc tối thiểu 30% (hoặc duyệt bảo lãnh VIP) để Submit.
						</div>
					</div>
					<button
						type="button"
						class="btn-action btn-primary w-full mt-2"
						:disabled="submitting || (!order.can_submit && !isVipGuarantee)"
						@click="handleSubmitOrder"
					>
						{{ submitting ? 'Đang kích hoạt đơn...' : 'KÍCH HOẠT & SUBMIT ĐƠN HÀNG' }}
					</button>
				</div>

				<div v-else class="submitted-banner">
					<div class="text-emerald font-bold text-sm">✓ ĐƠN HÀNG ĐÃ SUBMIT (CHÍNH THỨC)</div>
					<div class="text-secondary text-xs mt-0.5">Đã sẵn sàng chuyển sang khâu Mua hàng NCC và Lệnh sản xuất xưởng.</div>
				</div>
			</div>
		</aside>
	</div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { INITIAL_ORDERS } from '@/data/mockData';

const props = defineProps({
	orderId: { type: String, required: true },
	isOpen: { type: Boolean, default: false },
});

const emit = defineEmits(['close', 'order-updated']);

const order = ref(null);
const loading = ref(false);
const savingDeposit = ref(false);
const submitting = ref(false);

const depositInput = ref('');
const isVipGuarantee = ref(false);
const depositNote = ref('');

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

async function fetchOrderDetails() {
	if (!props.orderId) return;
	loading.value = true;
	const data = await api('get_order_details', { name: props.orderId });
	if (data) {
		order.value = data;
		if (data.credit_limit > 0 || data.is_vip_guarantee) {
			isVipGuarantee.value = true;
		}
	} else {
		// Dev / Fallback mode
		const found = INITIAL_ORDERS.find((o) => o.name === props.orderId);
		if (found) {
			order.value = JSON.parse(JSON.stringify(found));
			if (order.value.credit_limit > 0 || order.value.is_vip_guarantee) {
				isVipGuarantee.value = true;
			}
		}
	}
	loading.value = false;
}

watch(
	() => props.isOpen,
	(val) => {
		if (val) {
			depositInput.value = '';
			depositNote.value = '';
			fetchOrderDetails();
		}
	},
	{ immediate: true }
);

async function handleSaveDeposit() {
	if (!depositInput.value && !isVipGuarantee.value) return;
	savingDeposit.value = true;
	const addAmount = Number(depositInput.value) || 0;
	const res = await api('record_order_deposit', {
		name: props.orderId,
		amount: addAmount,
		is_vip_guarantee: isVipGuarantee.value,
		note: depositNote.value,
	});
	savingDeposit.value = false;

	if (res && res.success) {
		depositInput.value = '';
		await fetchOrderDetails();
		emit('order-updated');
	} else {
		// Dev / offline mutation
		if (order.value) {
			order.value.advance_paid += addAmount;
			order.value.outstanding_amount = Math.max(0, order.value.grand_total - order.value.advance_paid);
			order.value.deposit_pct = Math.min(100, Math.round((order.value.advance_paid / order.value.grand_total) * 100));
			if (order.value.deposit_pct >= 30 || isVipGuarantee.value) {
				order.value.can_submit = true;
			}
			if (isVipGuarantee.value) {
				order.value.is_vip_guarantee = 1;
			}
			order.value.comments.unshift({
				comment_type: 'Comment',
				content: `Ghi nhận cọc: ${addAmount.toLocaleString('vi-VN')} đ.${depositNote.value ? ' Ghi chú: ' + depositNote.value : ''}`,
				creation: 'Vừa xong',
				owner: 'Kế toán Thu quỹ',
			});

			// Update in global mock list
			const idx = INITIAL_ORDERS.findIndex((o) => o.name === props.orderId);
			if (idx !== -1) {
				INITIAL_ORDERS[idx] = JSON.parse(JSON.stringify(order.value));
			}
			depositInput.value = '';
			depositNote.value = '';
			emit('order-updated');
		}
	}
}

async function handleSubmitOrder() {
	submitting.value = true;
	const res = await api('submit_sales_order', {
		name: props.orderId,
		is_vip_guarantee: isVipGuarantee.value,
	});
	submitting.value = false;

	if (res && res.name) {
		await fetchOrderDetails();
		emit('order-updated');
	} else {
		// Dev / offline mutation
		if (order.value) {
			order.value.docstatus = 1;
			order.value.status = 'To Deliver and Bill';
			order.value.can_submit = false;
			order.value.comments.unshift({
				comment_type: 'Comment',
				content: 'Đã duyệt Đơn đặt hàng chính thức và chuyển sang lệnh mua hàng / sản xuất.',
				creation: 'Vừa xong',
				owner: 'Giám đốc Vạn Phát',
			});
			const idx = INITIAL_ORDERS.findIndex((o) => o.name === props.orderId);
			if (idx !== -1) {
				INITIAL_ORDERS[idx] = JSON.parse(JSON.stringify(order.value));
			}
			emit('order-updated');
		}
	}
}

function statusText(status, docstatus) {
	if (docstatus === 0) return 'Đơn Nháp (Chờ cọc)';
	if (docstatus === 1) return 'Chính thức (Đã submit)';
	return status || 'Draft';
}

function statusClass(status, docstatus) {
	if (docstatus === 0) return 'badge-draft';
	if (docstatus === 1) return 'badge-submitted';
	return 'badge-draft';
}

function formatCurrency(val) {
	if (val == null || val === '') return '0 đ';
	return Number(val).toLocaleString('vi-VN') + ' đ';
}

function formatNumber(val) {
	if (val == null || val === '') return '0';
	return Number(val).toLocaleString('vi-VN');
}
</script>

<style scoped>
.drawer-overlay {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.65);
	z-index: 50;
	display: flex;
	justify-content: flex-end;
}

.drawer-panel {
	width: 100%;
	max-width: 560px;
	height: 100vh;
	background: #161b22;
	border-left: 1px solid #3a424e;
	display: flex;
	flex-direction: column;
	overflow: hidden;
	box-shadow: -8px 0 24px rgba(0, 0, 0, 0.5);
}

.drawer-header {
	padding: 16px 20px;
	background: #141820;
	border-bottom: 1px solid #262c37;
	display: flex;
	align-items: flex-start;
	justify-content: space-between;
}

.order-id {
	font-family: 'JetBrains Mono', monospace;
	font-size: 16px;
	font-weight: 800;
	color: #4ea1e0;
}

.customer-subtitle {
	font-size: 13px;
	color: #9da7b5;
	margin-top: 4px;
}

.btn-close {
	background: transparent;
	border: 0;
	color: #9da7b5;
	font-size: 18px;
	cursor: pointer;
	padding: 4px 8px;
	border-radius: 4px;
}

.btn-close:hover {
	color: #fff;
	background: rgba(255, 255, 255, 0.08);
}

.drawer-loading {
	padding: 40px;
	text-align: center;
	color: #9da7b5;
	font-size: 14px;
}

.drawer-body {
	padding: 20px;
	flex: 1;
	overflow-y: auto;
	display: flex;
	flex-direction: column;
	gap: 16px;
}

.financial-card {
	background: #1a1f27;
	border: 1px solid #3a424e;
	border-radius: 10px;
	padding: 16px;
}

.financial-row {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	margin-bottom: 14px;
}

.lbl {
	font-size: 11px;
	font-weight: 700;
	color: #9da7b5;
	letter-spacing: 0.03em;
}

.val {
	font-size: 17px;
	font-weight: 800;
	color: #ffffff;
	margin-top: 3px;
}

.val-deposit {
	color: #34d399;
}

.pct-badge {
	font-size: 12px;
	font-weight: 700;
	color: #38bdf8;
	margin-left: 4px;
}

.deposit-track {
	position: relative;
	width: 100%;
	height: 7px;
	background: #12151a;
	border-radius: 4px;
	overflow: hidden;
}

.deposit-fill {
	height: 100%;
	transition: width 0.3s ease;
}

.bg-emerald {
	background: #34d399;
}

.bg-amber {
	background: #f59e0b;
}

.marker-30 {
	position: absolute;
	left: 30%;
	top: 0;
	bottom: 0;
	width: 2px;
	background: #ffffff;
	opacity: 0.7;
}

.section-box {
	background: #141820;
	border: 1px solid #262c37;
	border-radius: 10px;
	padding: 14px;
}

.section-title {
	font-size: 11px;
	font-weight: 800;
	letter-spacing: 0.04em;
	color: #9da7b5;
	margin-bottom: 10px;
	border-bottom: 1px solid #262c37;
	padding-bottom: 6px;
}

.items-table {
	width: 100%;
	border-collapse: collapse;
	font-size: 13px;
}

.items-table th {
	text-align: left;
	color: #9da7b5;
	font-size: 11px;
	font-weight: 700;
	padding: 6px 8px;
	background: #10141d;
	border-bottom: 1px solid #262c37;
}

.items-table td {
	padding: 8px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.05);
	color: #eef1f6;
}

.deposit-form {
	display: flex;
	flex-direction: column;
	gap: 10px;
}

.input-group label {
	display: block;
	font-size: 12px;
	color: #9da7b5;
	margin-bottom: 4px;
}

.input-dark {
	width: 100%;
	background: #10141d;
	border: 1px solid #3a424e;
	border-radius: 6px;
	padding: 8px 12px;
	font-size: 13px;
	color: #fff;
	outline: none;
}

.input-dark:focus {
	border-color: #4ea1e0;
}

.checkbox-label {
	display: flex;
	align-items: center;
	gap: 8px;
	font-size: 12px;
	color: #cbd5e1;
	cursor: pointer;
}

.btn-action {
	padding: 10px 16px;
	border-radius: 6px;
	font-size: 13px;
	font-weight: 700;
	cursor: pointer;
	border: 0;
	transition: background 0.15s;
}

.btn-secondary {
	background: #262c37;
	color: #eef1f6;
}

.btn-secondary:hover:not(:disabled) {
	background: #323946;
}

.btn-primary {
	background: #4ea1e0;
	color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
	background: #3b8ac4;
}

.btn-action:disabled {
	opacity: 0.4;
	cursor: not-allowed;
}

.submit-box {
	background: #141820;
	border: 1px solid #262c37;
	border-radius: 10px;
	padding: 14px;
}

.submitted-banner {
	background: rgba(52, 211, 153, 0.1);
	border: 1px solid rgba(52, 211, 153, 0.3);
	border-radius: 10px;
	padding: 14px;
	text-align: center;
}

.status-badge {
	font-size: 11px;
	font-weight: 700;
	padding: 3px 8px;
	border-radius: 4px;
}

.badge-draft {
	background: rgba(245, 158, 11, 0.14);
	color: #f59e0b;
}

.badge-submitted {
	background: rgba(52, 211, 153, 0.14);
	color: #34d399;
}

.text-num {
	font-variant-numeric: tabular-nums;
	font-family: 'JetBrains Mono', monospace;
}

.flex-between {
	display: flex;
	justify-content: space-between;
}

.text-secondary {
	color: #9da7b5;
}

.text-emerald {
	color: #34d399;
}

.text-amber {
	color: #f59e0b;
}

.text-right {
	text-align: right;
}

.font-bold {
	font-weight: 700;
}

.w-full {
	width: 100%;
}
</style>
