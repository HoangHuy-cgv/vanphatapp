<template>
	<div v-if="isOpen" class="drawer-overlay" @click.self="$emit('close')">
		<aside class="drawer-panel">
			<!-- Header: Tối Giản & Bỏ Code Rác -->
			<div class="drawer-header">
				<div>
					<div class="customer-title">
						{{ order?.customer_alias || order?.customer_name || 'Khách hàng' }}
					</div>
					<div class="product-subtitle">
						<span class="font-semibold text-white">{{ order?.item_name || 'Sản phẩm' }}</span>
						<span class="text-secondary ml-2 text-num">({{ formatNumber(order?.qty) }} {{ order?.uom || 'Túi' }})</span>
					</div>
					<div class="flex items-center gap-2 flex-wrap mt-2">
						<span class="badge-tab-type" :class="tabBadgeClass(order?.order_tab)">
							{{ tabBadgeLabel(order?.order_tab) }}
						</span>
						<span class="badge-cust-type" :class="order?.payment_type === 'Trả sau' ? 'bg-indigo' : 'bg-amber-dim'">
							{{ order?.payment_type || 'Trả trước' }}
						</span>
						<span class="status-badge" :class="orderStatusClass(order)">
							{{ order?.order_state || 'Chờ cọc' }}
						</span>
					</div>
				</div>
				<button type="button" class="btn-close" title="Đóng" @click="$emit('close')">✕</button>
			</div>

			<!-- Body (Loading / Content) -->
			<div v-if="loading" class="drawer-loading">
				Đang tải...
			</div>

			<div v-else-if="order" class="drawer-body">
				<!-- 1. Thẻ Tài Chính & Cọc -->
				<div class="financial-card">
					<!-- Khách trả sau -->
					<div v-if="order.payment_type === 'Trả sau'" class="postpaid-banner">
						<div class="flex-between">
							<span class="font-bold text-xs text-indigo-light">TRẢ SAU (CÔNG NỢ GỐI ĐẦU)</span>
							<span class="text-num text-xs">Hạn mức nợ: <b>{{ formatCurrency(order.credit_limit || 200000000) }}</b></span>
						</div>
					</div>

					<!-- Khách trả trước: 50% tiền hàng và 100% trục -->
					<div v-else class="deposit-breakdown">
						<div class="financial-row">
							<div>
								<div class="lbl">HÀNG (CỌC 50%)</div>
								<div class="val text-num">{{ formatCurrency(order.product_total || order.grand_total) }}</div>
							</div>
							<div class="text-right">
								<div class="lbl">TRỤC IN (100%)</div>
								<div class="val text-num" :class="order.cylinder_total > 0 ? 'text-purple font-bold' : 'text-secondary'">
									{{ formatCurrency(order.cylinder_total || 0) }}
								</div>
							</div>
						</div>

						<div class="deposit-summary-box mt-2">
							<div class="flex-between text-xs">
								<span class="lbl">CẦN CỌC:</span>
								<span class="text-num font-bold text-amber">{{ formatCurrency(order.required_deposit) }}</span>
							</div>
							<div class="flex-between text-xs mt-1">
								<span class="lbl">ĐÃ CỌC:</span>
								<span class="text-num font-bold text-emerald">{{ formatCurrency(order.advance_paid) }} ({{ order.deposit_pct }}%)</span>
							</div>
						</div>

						<!-- Progress bar -->
						<div class="deposit-track mt-2">
							<div
								class="deposit-fill"
								:style="{ width: Math.min(100, Math.round((order.advance_paid / (order.required_deposit || order.grand_total)) * 100)) + '%' }"
								:class="order.advance_paid >= order.required_deposit ? 'bg-emerald' : 'bg-amber'"
							></div>
							<div class="marker-50"></div>
						</div>
						<div class="flex-between text-xs mt-1 text-secondary">
							<span>Tiến độ cọc</span>
							<span class="text-num">Còn thiếu: <b class="text-white">{{ formatCurrency(order.outstanding_amount) }}</b></span>
						</div>
					</div>
				</div>

				<!-- 2. STATE MACHINE ACTION HUB (Trình tự bước tuần tự) -->
				<!-- BƯỚC A: ĐƠN BỊ HOLD (Thiếu Cọc / Nợ Trục) -->
				<div v-if="order.is_hold" class="action-card hold-card">
					<div class="card-head text-amber">
						<span>⚠️ TRẠNG THÁI HOLD (THIẾU CỌC)</span>
					</div>
					<div class="text-xs text-secondary mt-1">
						Đơn hàng chưa đủ 50% cọc hoặc nợ 100% tiền trục. Khóa mua hàng & sản xuất.
					</div>

					<!-- Ghi nhận cọc -->
					<div class="deposit-form mt-3">
						<div class="input-group">
							<label>Số tiền nộp thêm (đ):</label>
							<input
								v-model="depositInput"
								type="number"
								placeholder="Nhập số tiền..."
								class="input-dark text-num"
							/>
						</div>
						<div class="input-group mt-2">
							<label>Ghi chú / Mã GD:</label>
							<input
								v-model="depositNote"
								type="text"
								placeholder="UNC / Biên lai ngân hàng..."
								class="input-dark"
							/>
						</div>
						<div class="flex gap-2 mt-3">
							<button
								type="button"
								class="btn-action btn-primary flex-1"
								:disabled="savingDeposit || !depositInput"
								@click="handleSaveDeposit"
							>
								{{ savingDeposit ? 'Đang lưu...' : 'Lưu cọc' }}
							</button>
							<button
								type="button"
								class="btn-action btn-warning flex-1"
								:disabled="approvingProcurement"
								@click="handleAccountantApproveProcurement"
							>
								{{ approvingProcurement ? 'Đang duyệt...' : 'Duyệt ngoại lệ' }}
							</button>
						</div>
					</div>
				</div>

				<!-- BƯỚC B: ĐÃ ĐỦ CỌC - QUẢN LÝ CUNG ỨNG & SẢN XUẤT THEO TAB -->
				<div v-else class="action-card process-card">
					<!-- 1. Luồng Túi NGCS (In lụa) -->
					<div v-if="order.order_tab === 'ngcs'">
						<div class="card-head text-primary">
							<span>TIẾN ĐỘ IN LỤA NCC</span>
							<span class="badge-stage">{{ order.order_state }}</span>
						</div>
						<div class="info-grid mt-2">
							<div class="info-row">
								<span class="lbl">Phôi túi kho:</span>
								<span class="val text-emerald">✓ Sẵn sàng {{ formatNumber(order.qty) }} túi</span>
							</div>
							<div class="info-row">
								<span class="lbl">NCC In lụa:</span>
								<span class="val font-bold text-white">{{ order.supplier_name || 'ANH TÙNG' }}</span>
							</div>
							<div class="info-row">
								<span class="lbl">Mẫu in / Màu:</span>
								<span class="val text-white">{{ order.screen_brand || 'Mẫu chuẩn' }} (2 mặt)</span>
							</div>
							<div class="info-row">
								<span class="lbl">Hạn giao NCC:</span>
								<span class="sla-badge" :class="supplierSlaBadge(order.supplier_eta_days).cls">
									{{ supplierSlaBadge(order.supplier_eta_days).text }}
								</span>
							</div>
						</div>

						<!-- Nút bấm theo trạng thái NGCS -->
						<div class="mt-3">
							<button
								v-if="order.order_state === 'Sẵn sàng'"
								type="button"
								class="btn-action btn-primary w-full"
								@click="triggerNextStage('Đang xử lý', 'Đã gửi đơn in lụa sang NCC')"
							>
								+ Gửi in lụa NCC ({{ order.supplier_name }})
							</button>
							<button
								v-else-if="order.order_state === 'Đang xử lý'"
								type="button"
								class="btn-action btn-success w-full"
								@click="triggerNextStage('Sẵn sàng giao', 'Nhập kho thành phẩm in lụa')"
							>
								Xác nhận nhận hàng in lụa về kho
							</button>
							<button
								v-else-if="order.order_state === 'Sẵn sàng giao'"
								type="button"
								class="btn-action btn-delivery w-full"
								@click="triggerNextStage('Đã giao', 'Xuất kho giao khách')"
							>
								+ Xuất giao hàng
							</button>
							<div v-else-if="order.order_state === 'Đã giao'" class="text-center text-emerald font-bold py-2">
								✓ Đơn hàng đã giao thành công
							</div>
						</div>
					</div>

					<!-- 2. Luồng Xưởng Sản Xuất (Ghép -> Cắt -> Vòi) -->
					<div v-else-if="order.order_tab === 'xuong_sx'">
						<div class="card-head text-primary">
							<span>VẬN HÀNH XƯỞNG NỘI BỘ</span>
							<span class="badge-stage">{{ order.factory_stage || order.order_state }}</span>
						</div>
						<div class="info-grid mt-2">
							<div class="info-row">
								<span class="lbl">Vật tư màng & keo:</span>
								<span class="val font-bold" :class="order.materials_status === 'Đủ màng' ? 'text-emerald' : 'text-amber'">
									{{ order.materials_status || 'Chờ màng' }}
								</span>
							</div>
							<div class="info-row">
								<span class="lbl">Công đoạn hiện tại:</span>
								<span class="val font-bold text-white">{{ order.factory_stage || 'Lên chuyền' }}</span>
							</div>
							<div v-if="order.completed_qty" class="info-row">
								<span class="lbl">Sản lượng hoàn thành:</span>
								<span class="val text-num text-emerald">{{ formatNumber(order.completed_qty) }} / {{ formatNumber(order.qty) }}</span>
							</div>
						</div>

						<!-- Nút bấm tuần tự Xưởng SX -->
						<div class="mt-3">
							<button
								v-if="order.materials_status !== 'Đủ màng'"
								type="button"
								class="btn-action btn-warning w-full"
								@click="order.materials_status = 'Đủ màng'; triggerNextStage('Sẵn sàng', 'Đã chuẩn bị đủ màng')"
							>
								+ Mua màng & Trục NCC
							</button>
							<button
								v-else-if="order.factory_stage !== 'Xong hàng' && order.order_state !== 'Sẵn sàng giao'"
								type="button"
								class="btn-action btn-primary w-full"
								@click="triggerNextStage('Sẵn sàng giao', 'Xưởng hoàn thành 100% sản lượng')"
							>
								+ Báo cáo hoàn thành xưởng (Nhập kho TP)
							</button>
							<button
								v-else-if="order.order_state === 'Sẵn sàng giao' || order.factory_stage === 'Xong hàng'"
								type="button"
								class="btn-action btn-delivery w-full"
								@click="triggerNextStage('Đã giao', 'Xuất kho giao khách')"
							>
								+ Xuất giao hàng
							</button>
							<div v-else-if="order.order_state === 'Đã giao'" class="text-center text-emerald font-bold py-2">
								✓ Đơn hàng đã giao thành công
							</div>
						</div>
					</div>

					<!-- 3. Luồng Mua Ngoài Trọn Gói (Túi màng đơn / Mua đứt NCC) -->
					<div v-else>
						<div class="card-head text-primary">
							<span>TIẾN ĐỘ MUA NGOÀI NCC</span>
							<span class="badge-stage">{{ order.order_state }}</span>
						</div>
						<div class="info-grid mt-2">
							<div class="info-row">
								<span class="lbl">Nhà cung cấp:</span>
								<span class="val font-bold text-white">{{ order.supplier_name || 'NCC NGOÀI' }}</span>
							</div>
							<div class="info-row">
								<span class="lbl">Hạn giao NCC:</span>
								<span class="sla-badge" :class="supplierSlaBadge(order.supplier_eta_days).cls">
									{{ supplierSlaBadge(order.supplier_eta_days).text }}
								</span>
							</div>
							<div class="info-row">
								<span class="lbl">Trạng thái giao:</span>
								<span class="val text-white">{{ order.procurement_stage || 'Đang chờ hàng' }}</span>
							</div>
						</div>

						<!-- Nút bấm tuần tự Mua Ngoài -->
						<div class="mt-3">
							<button
								v-if="order.order_state === 'Sẵn sàng'"
								type="button"
								class="btn-action btn-primary w-full"
								@click="triggerNextStage('Đang xử lý', 'Đã phát hành đơn mua NCC')"
							>
								+ Gửi đơn mua NCC ({{ order.supplier_name }})
							</button>
							<button
								v-else-if="order.order_state === 'Đang xử lý'"
								type="button"
								class="btn-action btn-success w-full"
								@click="triggerNextStage('Sẵn sàng giao', 'NCC đã giao đủ hàng về kho')"
							>
								Xác nhận nhận hàng NCC về kho
							</button>
							<button
								v-else-if="order.order_state === 'Sẵn sàng giao'"
								type="button"
								class="btn-action btn-delivery w-full"
								@click="triggerNextStage('Đã giao', 'Xuất kho giao khách')"
							>
								+ Xuất giao hàng
							</button>
							<div v-else-if="order.order_state === 'Đã giao'" class="text-center text-emerald font-bold py-2">
								✓ Đơn hàng đã giao thành công
							</div>
						</div>
					</div>
				</div>

				<!-- 3. Mặt hàng trong đơn -->
				<div class="section-box">
					<div class="section-title">CHI TIẾT MẶT HÀNG</div>
					<table class="items-table">
						<thead>
							<tr>
								<th>Tên mặt hàng / Quy cách</th>
								<th style="width: 20%; text-align: right;">Số lượng</th>
								<th style="width: 25%; text-align: right;">Đơn giá</th>
								<th style="width: 25%; text-align: right;">Thành tiền</th>
							</tr>
						</thead>
						<tbody>
							<tr v-for="(it, idx) in order.items" :key="idx" :class="{ 'row-cylinder': it.is_cylinder }">
								<td>
									<div class="font-semibold text-white">{{ it.item_name }}</div>
									<span v-if="it.is_cylinder" class="badge-tag-cyl">Trục in</span>
								</td>
								<td class="text-right text-num">{{ formatNumber(it.qty) }} {{ it.uom || 'Túi' }}</td>
								<td class="text-right text-num">{{ formatCurrency(it.rate) }}</td>
								<td class="text-right text-num font-bold">{{ formatCurrency(it.amount) }}</td>
							</tr>
						</tbody>
					</table>
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

function tabBadgeLabel(tab) {
	switch (tab) {
		case 'ngcs':
			return 'TÚI NGCS';
		case 'xuong_sx':
			return 'XƯỞNG SẢN XUẤT';
		case 'mua_ngoai':
			return 'MUA NGOÀI';
		default:
			return 'ĐƠN HÀNG';
	}
}

function tabBadgeClass(tab) {
	switch (tab) {
		case 'ngcs':
			return 'tab-badge-ngcs';
		case 'xuong_sx':
			return 'tab-badge-xuong';
		case 'mua_ngoai':
			return 'tab-badge-ngoai';
		default:
			return '';
	}
}

function supplierSlaBadge(days) {
	if (days == null) return { text: '—', cls: 'sla-none' };
	if (days < 0) return { text: `Trễ ${Math.abs(days)} ngày`, cls: 'sla-overdue' };
	if (days === 0) return { text: 'Hôm nay giao', cls: 'sla-today' };
	return { text: `Còn ${days} ngày`, cls: 'sla-ontime' };
}

async function fetchOrderDetails() {
	if (!props.orderId) return;
	loading.value = true;
	const found = INITIAL_ORDERS.find((o) => o.name === props.orderId);
	if (found) {
		order.value = JSON.parse(JSON.stringify(found));
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
	if (!depositInput.value) return;
	savingDeposit.value = true;
	const addAmount = Number(depositInput.value) || 0;

	if (order.value) {
		order.value.advance_paid += addAmount;
		order.value.outstanding_amount = Math.max(0, order.value.grand_total - order.value.advance_paid);
		order.value.deposit_pct = Math.min(100, Math.round((order.value.advance_paid / order.value.grand_total) * 100));

		if (order.value.advance_paid >= (order.value.required_deposit || order.value.grand_total * 0.5)) {
			order.value.docstatus = 1;
			order.value.is_hold = false;
			order.value.order_state = 'Sẵn sàng';
		}

		const idx = INITIAL_ORDERS.findIndex((o) => o.name === props.orderId);
		if (idx !== -1) {
			INITIAL_ORDERS[idx] = JSON.parse(JSON.stringify(order.value));
		}
		depositInput.value = '';
		depositNote.value = '';
		emit('order-updated');
	}
	savingDeposit.value = false;
}

async function handleAccountantApproveProcurement() {
	approvingProcurement.value = true;
	if (order.value) {
		order.value.docstatus = 1;
		order.value.is_hold = false;
		order.value.order_state = 'Sẵn sàng';
		const idx = INITIAL_ORDERS.findIndex((o) => o.name === props.orderId);
		if (idx !== -1) {
			INITIAL_ORDERS[idx] = JSON.parse(JSON.stringify(order.value));
		}
		emit('order-updated');
	}
	approvingProcurement.value = false;
}

function triggerNextStage(newState, desc) {
	if (order.value) {
		order.value.order_state = newState;
		if (newState === 'Sẵn sàng giao') {
			if (order.value.factory_stage) order.value.factory_stage = 'Xong hàng';
		}
		const idx = INITIAL_ORDERS.findIndex((o) => o.name === props.orderId);
		if (idx !== -1) {
			INITIAL_ORDERS[idx] = JSON.parse(JSON.stringify(order.value));
		}
		emit('order-updated');
	}
}

function orderStatusClass(o) {
	if (!o) return 'badge-draft';
	if (o.is_hold || o.order_state?.includes('Hold')) return 'badge-hold';
	if (o.order_state === 'Sẵn sàng giao') return 'badge-ready-delivery';
	if (o.order_state === 'Đã giao') return 'badge-delivered';
	if (o.order_state === 'Đang xử lý') return 'badge-in-process';
	return 'badge-submitted';
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
	max-width: 540px;
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

.customer-title {
	font-size: 18px;
	font-weight: 800;
	color: #ffffff;
}

.product-subtitle {
	font-size: 13.5px;
	color: #94a3b8;
	margin-top: 2px;
}

.badge-tab-type {
	font-size: 10.5px;
	font-weight: 700;
	padding: 2px 7px;
	border-radius: 4px;
}

.tab-badge-ngcs {
	background: rgba(245, 158, 11, 0.15);
	color: #fbbf24;
	border: 1px solid rgba(245, 158, 11, 0.3);
}

.tab-badge-xuong {
	background: rgba(78, 161, 224, 0.15);
	color: #4ea1e0;
	border: 1px solid rgba(78, 161, 224, 0.3);
}

.tab-badge-ngoai {
	background: rgba(168, 85, 247, 0.15);
	color: #c084fc;
	border: 1px solid rgba(168, 85, 247, 0.3);
}

.badge-cust-type {
	font-size: 10.5px;
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
	background: rgba(245, 158, 11, 0.1);
	color: #fbbf24;
}

.status-badge {
	font-size: 10.5px;
	font-weight: 700;
	padding: 2px 7px;
	border-radius: 4px;
}

.badge-hold {
	background: rgba(239, 68, 68, 0.2);
	color: #fca5a5;
	border: 1px solid rgba(239, 68, 68, 0.4);
}

.badge-in-process {
	background: rgba(59, 130, 246, 0.18);
	color: #93c5fd;
	border: 1px solid rgba(59, 130, 246, 0.3);
}

.badge-ready-delivery {
	background: rgba(52, 211, 153, 0.2);
	color: #34d399;
	border: 1px solid rgba(52, 211, 153, 0.4);
}

.badge-delivered {
	background: rgba(148, 163, 184, 0.15);
	color: #94a3b8;
}

.badge-submitted {
	background: rgba(78, 161, 224, 0.15);
	color: #4ea1e0;
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

.drawer-loading {
	padding: 40px;
	text-align: center;
	color: #9da7b5;
	font-size: 14px;
}

.drawer-body {
	padding: 16px;
	flex: 1;
	overflow-y: auto;
	display: flex;
	flex-direction: column;
	gap: 14px;
}

.financial-card {
	background: #1a1f27;
	border: 1px solid #3a424e;
	border-radius: 8px;
	padding: 14px;
}

.postpaid-banner {
	background: rgba(99, 102, 241, 0.08);
	border: 1px solid rgba(99, 102, 241, 0.25);
	border-radius: 6px;
	padding: 10px 12px;
}

.financial-row {
	display: flex;
	justify-content: space-between;
}

.lbl {
	font-size: 10.5px;
	font-weight: 700;
	color: #94a3b8;
	text-transform: uppercase;
}

.val {
	font-size: 13.5px;
	font-weight: 700;
	color: #f1f5f9;
}

.deposit-summary-box {
	background: rgba(0, 0, 0, 0.25);
	border-radius: 6px;
	padding: 8px 10px;
}

.deposit-track {
	width: 100%;
	height: 6px;
	background: rgba(255, 255, 255, 0.08);
	border-radius: 3px;
	overflow: hidden;
	position: relative;
}

.deposit-fill {
	height: 100%;
	transition: width 0.3s ease;
}

.marker-50 {
	position: absolute;
	left: 50%;
	top: 0;
	bottom: 0;
	width: 2px;
	background: rgba(255, 255, 255, 0.3);
}

.flex-between {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.action-card {
	background: #1a1f27;
	border-radius: 8px;
	padding: 14px;
	border: 1px solid #3a424e;
}

.hold-card {
	border-color: rgba(245, 158, 11, 0.4);
	background: rgba(245, 158, 11, 0.04);
}

.process-card {
	border-color: rgba(78, 161, 224, 0.3);
}

.card-head {
	display: flex;
	justify-content: space-between;
	align-items: center;
	font-size: 12px;
	font-weight: 800;
	letter-spacing: 0.5px;
}

.info-grid {
	display: flex;
	flex-direction: column;
	gap: 6px;
}

.info-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	font-size: 12px;
}

.sla-badge {
	font-size: 10.5px;
	font-weight: 700;
	padding: 2px 7px;
	border-radius: 4px;
}

.sla-ontime {
	background: rgba(148, 163, 184, 0.15);
	color: #94a3b8;
}

.sla-today {
	background: rgba(245, 158, 11, 0.18);
	color: #fbbf24;
}

.sla-overdue {
	background: rgba(239, 68, 68, 0.25);
	color: #fca5a5;
	border: 1px solid rgba(239, 68, 68, 0.5);
}

.badge-stage {
	font-size: 11px;
	font-weight: 600;
	padding: 2px 6px;
	border-radius: 4px;
	background: rgba(78, 161, 224, 0.12);
	color: #93c5fd;
	border: 1px solid rgba(78, 161, 224, 0.3);
}

.deposit-form .input-group label {
	display: block;
	font-size: 11px;
	font-weight: 700;
	color: #94a3b8;
	margin-bottom: 4px;
}

.input-dark {
	width: 100%;
	background: #11141a;
	border: 1px solid #3a424e;
	color: #f1f5f9;
	padding: 7px 10px;
	border-radius: 6px;
	font-size: 13px;
	box-sizing: border-box;
}

.input-dark:focus {
	outline: none;
	border-color: #4ea1e0;
}

.btn-action {
	padding: 9px 14px;
	border-radius: 6px;
	font-weight: 700;
	font-size: 12.5px;
	cursor: pointer;
	transition: all 0.15s ease;
	border: 1px solid transparent;
}

.btn-primary {
	background: #4ea1e0;
	color: #0b0f19;
}

.btn-primary:hover {
	background: #60a5fa;
}

.btn-warning {
	background: rgba(245, 158, 11, 0.2);
	color: #fbbf24;
	border-color: rgba(245, 158, 11, 0.4);
}

.btn-success {
	background: rgba(52, 211, 153, 0.2);
	color: #34d399;
	border-color: rgba(52, 211, 153, 0.4);
}

.btn-delivery {
	background: #0284c7;
	color: #ffffff;
	font-size: 13.5px;
	padding: 10px 16px;
	box-shadow: 0 0 12px rgba(2, 132, 199, 0.4);
}

.btn-delivery:hover {
	background: #0369a1;
}

.section-box {
	background: #1a1f27;
	border: 1px solid #3a424e;
	border-radius: 8px;
	padding: 12px;
}

.section-title {
	font-size: 11px;
	font-weight: 700;
	color: #94a3b8;
	margin-bottom: 8px;
	letter-spacing: 0.5px;
}

.items-table {
	width: 100%;
	border-collapse: collapse;
	font-size: 12px;
}

.items-table th {
	text-align: left;
	color: #64748b;
	font-size: 11px;
	padding: 6px 4px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.items-table td {
	padding: 8px 4px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.badge-tag-cyl {
	display: inline-block;
	font-size: 10px;
	font-weight: 700;
	padding: 1px 5px;
	border-radius: 4px;
	background: rgba(168, 85, 247, 0.2);
	color: #d8b4fe;
	border: 1px solid rgba(168, 85, 247, 0.3);
}

.text-num {
	font-variant-numeric: tabular-nums;
}
.text-emerald { color: #34d399; }
.text-amber { color: #fbbf24; }
.text-purple { color: #c084fc; }
.text-secondary { color: #94a3b8; }
.bg-emerald { background-color: #34d399; }
.bg-amber { background-color: #fbbf24; }
</style>
