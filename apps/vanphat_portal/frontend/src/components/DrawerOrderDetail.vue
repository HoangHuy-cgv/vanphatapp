<template>
	<div v-if="isOpen" class="drawer-overlay" @click.self="$emit('close')">
		<aside class="drawer-panel">
			<!-- Header -->
			<div class="drawer-header">
				<div>
					<div class="flex items-center gap-2 flex-wrap">
						<span class="order-id">{{ order?.name || orderId }}</span>
						<span class="badge-cust-type" :class="order?.payment_type === 'Trả sau' ? 'bg-indigo' : 'bg-amber-dim'">
							{{ order?.payment_type || 'Trả trước' }}
						</span>
						<span class="badge-prod-group">
							{{ order?.product_group || 'Túi màng ghép' }}
						</span>
						<span class="status-badge" :class="orderStatusClass(order)">
							{{ order?.order_state || statusText(order?.status, order?.docstatus) }}
						</span>
					</div>
					<div class="customer-subtitle mt-1">
						Khách hàng: <b>{{ order?.customer_name || order?.customer || '—' }}</b>
						<span v-if="order?.pouch_type_detail" class="text-xs text-secondary ml-2">({{ order.pouch_type_detail }})</span>
					</div>
				</div>
				<button type="button" class="btn-close" @click="$emit('close')">✕</button>
			</div>

			<!-- Body (Loading / Content) -->
			<div v-if="loading" class="drawer-loading">
				Đang tải thông tin đơn hàng...
			</div>

			<div v-else-if="order" class="drawer-body">
				<!-- 1. Thẻ Phân Bổ Tiền Hàng, Tiền Trục & Mức Cọc -->
				<div class="financial-card">
					<!-- Khách trả sau -->
					<div v-if="order.payment_type === 'Trả sau'" class="postpaid-banner">
						<div class="flex-between">
							<span class="font-bold text-sm text-indigo-light">KHÁCH TRẢ SAU (HẠN MỨC CÔNG NỢ)</span>
							<span class="text-num text-xs">Hạn mức: <b>{{ formatCurrency(order.credit_limit) }}</b></span>
						</div>
						<div class="text-xs text-secondary mt-1">
							Đơn hàng tự động bypass cọc và submit vào hệ thống để mua hàng & sản xuất.
						</div>
					</div>

					<!-- Khách trả trước: Bóc tách 50% tiền hàng và 100% TIỀN TRỤC -->
					<div v-else class="deposit-breakdown">
						<div class="financial-row">
							<div>
								<div class="lbl">TIỀN HÀNG (TÚI / MÀNG)</div>
								<div class="val text-num">{{ formatCurrency(order.product_total || order.grand_total) }}</div>
								<div class="text-xs text-secondary">Mốc cọc yêu cầu: <b class="text-amber">50%</b></div>
							</div>
							<div class="text-right">
								<div class="lbl">TIỀN TRỤC IN (NẾU CÓ)</div>
								<div class="val text-num" :class="order.cylinder_total > 0 ? 'text-purple' : 'text-secondary'">
									{{ formatCurrency(order.cylinder_total || 0) }}
								</div>
								<div class="text-xs" :class="order.cylinder_total > 0 ? 'text-purple' : 'text-secondary'">
									Thu trước: <b>100%</b>
								</div>
							</div>
						</div>

						<div class="deposit-summary-box mt-3">
							<div class="flex-between text-xs">
								<span class="lbl">YÊU CẦU THU TRƯỚC (50% HÀNG + 100% TRỤC):</span>
								<span class="text-num font-bold text-amber">{{ formatCurrency(order.required_deposit) }}</span>
							</div>
							<div class="flex-between text-xs mt-1">
								<span class="lbl">ĐÃ THU:</span>
								<span class="text-num font-bold text-emerald">{{ formatCurrency(order.advance_paid) }} ({{ order.deposit_pct }}%)</span>
							</div>
						</div>

						<!-- Progress bar với mốc 50% chuẩn -->
						<div class="deposit-track mt-2">
							<div
								class="deposit-fill"
								:style="{ width: Math.min(100, Math.round((order.advance_paid / (order.required_deposit || order.grand_total)) * 100)) + '%' }"
								:class="order.advance_paid >= order.required_deposit ? 'bg-emerald' : 'bg-amber'"
							></div>
							<div class="marker-50" title="Mốc thu đủ để chạy tự động"></div>
						</div>
						<div class="flex-between text-xs mt-1 text-secondary">
							<span>Cần thu tối thiểu 100% mốc yêu cầu</span>
							<span class="text-num">Còn nợ: <b class="text-white">{{ formatCurrency(order.outstanding_amount) }}</b></span>
						</div>
					</div>
				</div>

				<!-- 2. CẢNH BÁO HOLD VÀ HỘP QUYẾT ĐỊNH CỦA KẾ TOÁN (Khi cọc > 0 và < 50%) -->
				<div v-if="order.is_hold && order.docstatus === 0" class="hold-action-card">
					<div class="hold-header">
						<span class="text-amber font-bold text-sm">⚠️ ĐƠN HÀNG ĐANG BỊ HOLD (TẠM GIỮ)</span>
						<span class="hold-tag">THIẾU CỌC</span>
					</div>
					<div class="text-xs text-secondary mt-1">
						Khách đã cọc <b class="text-white">{{ formatCurrency(order.advance_paid) }}</b>, chưa đạt mức thu tối thiểu <b class="text-amber">{{ formatCurrency(order.required_deposit) }}</b>. Toàn bộ khâu Mua hàng NCC và Xưởng sản xuất tạm khóa.
					</div>

					<div class="accountant-box mt-3">
						<div class="text-xs font-semibold text-white mb-1">QUYẾT ĐỊNH CỦA KẾ TOÁN:</div>
						<input
							v-model="accountantNote"
							type="text"
							placeholder="Ghi chú lý do duyệt ngoại lệ (nếu có)..."
							class="input-dark text-xs mb-2"
						/>
						<button
							type="button"
							class="btn-action btn-procurement w-full"
							:disabled="approvingProcurement"
							@click="handleAccountantApproveProcurement"
						>
							{{ approvingProcurement ? 'Đang duyệt chuyển bước...' : '👉 KẾ TOÁN PHÊ DUYỆT: MUA HÀNG NCC' }}
						</button>
						<div class="text-xs text-muted text-center mt-1">
							Chỉ khi Kế toán bấm nút trên, đơn hàng mới được mở khóa để chuyển sang bước Mua hàng NCC.
						</div>
					</div>
				</div>

				<!-- 3. Danh Sách Mặt Hàng Đặt -->
				<div class="section-box">
					<div class="section-title">DANH SÁCH MẶT HÀNG</div>
					<table class="items-table">
						<thead>
							<tr>
								<th>Tên hàng / Trục in</th>
								<th style="width: 15%; text-align: center;">Loại</th>
								<th style="width: 18%; text-align: right;">SL</th>
								<th style="width: 22%; text-align: right;">Đơn giá</th>
								<th style="width: 25%; text-align: right;">Thành tiền</th>
							</tr>
						</thead>
						<tbody>
							<tr v-for="(it, idx) in order.items" :key="idx" :class="{ 'row-cylinder': it.is_cylinder }">
								<td>
									<div class="font-semibold">{{ it.item_name }}</div>
									<div v-if="it.item_code" class="text-xs font-mono text-secondary">{{ it.item_code }}</div>
								</td>
								<td class="text-center">
									<span v-if="it.is_cylinder" class="badge-tag-cyl">Trục in</span>
									<span v-else class="badge-tag-item">Hàng</span>
								</td>
								<td class="text-right text-num">{{ formatNumber(it.qty) }} {{ it.uom || 'Túi' }}</td>
								<td class="text-right text-num">{{ formatCurrency(it.rate) }}</td>
								<td class="text-right text-num font-bold">{{ formatCurrency(it.amount) }}</td>
							</tr>
							<tr v-if="!order.items || order.items.length === 0">
								<td colspan="5" class="text-center text-secondary py-3">Chưa có chi tiết mặt hàng</td>
							</tr>
						</tbody>
					</table>
				</div>

				<!-- 4. Hộp Ghi Nhận Tiền Cọc (Khi đơn chưa submit) -->
				<div v-if="order.docstatus === 0" class="section-box">
					<div class="section-title">GHI NHẬN TIỀN CỌC</div>

					<div class="deposit-form">
						<div class="input-group">
							<label>Số tiền khách chuyển (đ):</label>
							<input
								v-model="depositInput"
								type="number"
								placeholder="Nhập số tiền cọc bổ sung..."
								class="input-dark text-num"
							/>
						</div>

						<div class="input-group mt-2">
							<label>Ghi chú chuyển khoản / biên lai:</label>
							<input
								v-model="depositNote"
								type="text"
								placeholder="Ví dụ: VCB 10:30 ngày 15/08, cọc 50%..."
								class="input-dark"
							/>
						</div>

						<div class="mt-3 flex gap-2">
							<button
								type="button"
								class="btn-action btn-secondary"
								:disabled="savingDeposit || !depositInput"
								@click="handleSaveDeposit"
							>
								{{ savingDeposit ? 'Đang lưu...' : 'Lưu Tiền Cọc' }}
							</button>
						</div>
					</div>
				</div>

				<!-- 5. Trạng Thái Hoàn Tất -->
				<div v-if="order.docstatus === 1" class="submitted-banner">
					<div class="text-emerald font-bold text-sm">✓ ĐƠN HÀNG CHÍNH THỨC (ĐÃ DUYỆT)</div>
					<div class="text-secondary text-xs mt-0.5">
						Đã chuyển sang khâu <b>Trang 2: Mua hàng NCC</b> và lệnh sản xuất xưởng.
					</div>
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
const approvingProcurement = ref(false);

const depositInput = ref('');
const depositNote = ref('');
const accountantNote = ref('');

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
	} else {
		// Dev / Fallback mode
		const found = INITIAL_ORDERS.find((o) => o.name === props.orderId);
		if (found) {
			order.value = JSON.parse(JSON.stringify(found));
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
			accountantNote.value = '';
			fetchOrderDetails();
		}
	},
	{ immediate: true }
);

async function handleSaveDeposit() {
	if (!depositInput.value) return;
	savingDeposit.value = true;
	const addAmount = Number(depositInput.value) || 0;
	const res = await api('record_order_deposit', {
		name: props.orderId,
		amount: addAmount,
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

			// Kiểm tra điều kiện cọc 50% hàng + 100% trục
			if (order.value.advance_paid >= (order.value.required_deposit || order.value.grand_total * 0.5)) {
				order.value.docstatus = 1;
				order.value.status = 'To Deliver and Bill';
				order.value.order_state = 'Chính thức (Đã cọc >=50%)';
				order.value.is_hold = false;
				order.value.can_submit = false;
			} else if (order.value.advance_paid > 0) {
				order.value.is_hold = true;
				order.value.order_state = 'HOLD (Thiếu cọc)';
			}

			order.value.comments.unshift({
				comment_type: 'Comment',
				content: `Ghi nhận cọc: ${addAmount.toLocaleString('vi-VN')} đ.${depositNote.value ? ' Ghi chú: ' + depositNote.value : ''}`,
				creation: 'Vừa xong',
				owner: 'Kế toán Thu quỹ',
			});

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

async function handleAccountantApproveProcurement() {
	approvingProcurement.value = true;
	const res = await api('accountant_approve_procurement', {
		name: props.orderId,
		note: accountantNote.value,
	});
	approvingProcurement.value = false;

	if (res && res.success) {
		await fetchOrderDetails();
		emit('order-updated');
	} else {
		// Dev / offline mutation
		if (order.value) {
			order.value.docstatus = 1;
			order.value.is_hold = false;
			order.value.status = 'To Deliver and Bill';
			order.value.order_state = 'Đã chuyển Mua hàng NCC';
			order.value.comments.unshift({
				comment_type: 'Comment',
				content: `Kế toán phê duyệt Mua hàng NCC (chuyển bước tiếp theo dù thiếu cọc): ${accountantNote.value || 'Đã xác nhận cho chạy'}`,
				creation: 'Vừa xong',
				owner: 'Kế toán Trưởng',
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
	if (docstatus === 0) return 'Đơn Nháp';
	if (docstatus === 1) return 'Chính thức';
	return status || 'Draft';
}

function orderStatusClass(o) {
	if (!o) return 'badge-draft';
	if (o.is_hold) return 'badge-hold';
	if (o.docstatus === 1) return 'badge-submitted';
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

.badge-hold {
	background: rgba(239, 68, 68, 0.2);
	color: #f87171;
	border: 1px solid rgba(239, 68, 68, 0.4);
}

.badge-cust-type {
	font-size: 11px;
	font-weight: 700;
	padding: 2px 7px;
	border-radius: 4px;
}

.bg-indigo {
	background: rgba(99, 102, 241, 0.2);
	color: #a5b4fc;
	border: 1px solid rgba(99, 102, 241, 0.4);
}

.bg-amber-dim {
	background: rgba(245, 158, 11, 0.15);
	color: #fbbf24;
	border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-prod-group {
	font-size: 11px;
	font-weight: 600;
	padding: 2px 7px;
	border-radius: 4px;
	background: #202735;
	color: #93c5fd;
	border: 1px solid #334155;
}

.postpaid-banner {
	background: rgba(99, 102, 241, 0.1);
	border: 1px solid rgba(99, 102, 241, 0.3);
	border-radius: 8px;
	padding: 12px;
}

.text-indigo-light {
	color: #c7d2fe;
}

.text-purple {
	color: #c084fc;
}

.deposit-summary-box {
	background: #11151d;
	border: 1px solid #232936;
	border-radius: 6px;
	padding: 10px 12px;
}

.marker-50 {
	position: absolute;
	left: 50%;
	top: -2px;
	bottom: -2px;
	width: 2px;
	background: #ffffff;
	box-shadow: 0 0 6px #fff;
}

.hold-action-card {
	background: rgba(239, 68, 68, 0.08);
	border: 1px solid rgba(239, 68, 68, 0.35);
	border-radius: 10px;
	padding: 14px;
	margin-bottom: 14px;
}

.hold-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.hold-tag {
	font-size: 10px;
	font-weight: 800;
	padding: 2px 6px;
	background: #ef4444;
	color: #fff;
	border-radius: 3px;
	letter-spacing: 0.5px;
}

.accountant-box {
	background: #131722;
	border: 1px solid rgba(245, 158, 11, 0.3);
	border-radius: 8px;
	padding: 12px;
}

.btn-procurement {
	background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
	color: #ffffff;
	font-size: 13px;
	font-weight: 800;
	box-shadow: 0 2px 8px rgba(234, 88, 12, 0.4);
}

.btn-procurement:hover:not(:disabled) {
	background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
}

.row-cylinder {
	background: rgba(192, 132, 252, 0.04);
}

.badge-tag-cyl {
	font-size: 10px;
	font-weight: 700;
	padding: 2px 5px;
	border-radius: 3px;
	background: rgba(192, 132, 252, 0.15);
	color: #d8b4fe;
	border: 1px solid rgba(192, 132, 252, 0.3);
}

.badge-tag-item {
	font-size: 10px;
	font-weight: 600;
	padding: 2px 5px;
	border-radius: 3px;
	background: rgba(78, 161, 224, 0.12);
	color: #7dd3fc;
}

.text-muted {
	color: #64748b;
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
