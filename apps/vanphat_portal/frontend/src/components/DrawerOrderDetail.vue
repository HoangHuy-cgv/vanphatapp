<template>
	<div v-if="isOpen" class="drawer-overlay" @click.self="$emit('close')">
		<aside class="drawer-panel" aria-label="Chi tiết đơn hàng">
			<!-- Header -->
			<div class="drawer-head">
				<h3 class="drawer-title">Chi tiết đơn hàng</h3>
				<button
					type="button"
					class="btn-icon"
					title="Đóng (Esc)"
					@click="$emit('close')"
				>
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<line x1="18" y1="6" x2="6" y2="18"></line>
						<line x1="6" y1="6" x2="18" y2="18"></line>
					</svg>
				</button>
			</div>

			<!-- Top Summary: Chuẩn 100% Drawer 2 Báo Giá -->
			<div v-if="order" class="drawer-top-summary">
				<!-- LINE 1: Tên khách hàng & Brand Tag -->
				<div class="cust-brand-bar">
					<div class="cust-info">
						<span class="icon-building">🏢</span>
						<span class="cust-name">{{ order.customer_alias || order.customer_name }}</span>
					</div>
					<div class="brand-tag">
						{{ order.brand || 'VẠN PHÁT' }}
					</div>
				</div>

				<!-- LINE 2: 5 Badges màu nhận diện -->
				<div class="axis-badges">
					<span class="axis-badge badge-product">{{ order.product_type || order.product_group || 'Túi màng ghép' }}</span>
					<span class="axis-badge badge-accessory">{{ order.accessory || 'Không vòi' }}</span>
					<span class="axis-badge badge-print">{{ order.print_type || 'In trục' }}</span>
					<span class="axis-badge badge-cylinder">{{ order.cylinder_status || 'Không trục' }}</span>
					<span class="axis-badge badge-tab" :class="tabBadgeClass(order.order_tab)">
						{{ tabBadgeLabel(order.order_tab) }}
					</span>
				</div>

				<!-- KHỐI QUY CÁCH KỸ THUẬT -->
				<div class="spec-box">
					<!-- LINE 3: Mô tả sản phẩm -->
					<div class="spec-line">
						<span class="spec-icon">📦</span>
						<span class="spec-desc-text">{{ order.description || order.item_name }}</span>
					</div>

					<!-- LINE 4: Kích thước & Độ dày -->
					<div class="spec-line">
						<span class="spec-icon">📐</span>
						<span class="spec-dim-text">{{ order.dimensions_text || 'Quy cách chuẩn' }}</span>
					</div>

					<!-- LINE 5: 4 Nhóm Chips chất liệu chuẩn công nghiệp -->
					<div class="mat-chips-wrap">
						<!-- Nhóm 1: Màng in (Blue) -->
						<div class="mat-group">
							<span class="mat-chip chip-blue" :class="{ on: isMat('OPP') }">OPP</span>
							<span class="mat-chip chip-blue" :class="{ on: isMat('PET') }">PET</span>
						</div>

						<div class="mat-divider"></div>

						<!-- Nhóm 2: Màng cản (Amber) -->
						<div class="mat-group">
							<span class="mat-chip chip-amber" :class="{ on: isMat('AL') }">AL</span>
							<span class="mat-chip chip-amber" :class="{ on: isMat('MPET') }">MPET</span>
						</div>

						<div class="mat-divider"></div>

						<!-- Nhóm 3: Màng dẻo PA (Purple) -->
						<div class="mat-group">
							<span class="mat-chip chip-purple" :class="{ on: isMat('PA') }">PA</span>
						</div>

						<div class="mat-divider"></div>

						<!-- Nhóm 4: Màng hàn dán (Emerald) -->
						<div class="mat-group">
							<span class="mat-chip chip-emerald" :class="{ on: isMat('PE sữa') }">PE sữa</span>
							<span class="mat-chip chip-emerald" :class="{ on: isMat('PE trong') }">PE trong</span>
							<span class="mat-chip chip-emerald" :class="{ on: isMat('CPP') }">CPP</span>
							<span class="mat-chip chip-emerald" :class="{ on: isMat('HD') }">HD</span>
						</div>
					</div>
				</div>
			</div>

			<!-- Body -->
			<div v-if="loading" class="drawer-loading">
				Đang tải dữ liệu...
			</div>

			<div v-else-if="order" class="drawer-body">
				<!-- BỐ CỤC 2 CỘT: ẢNH THIẾT KẾ (TRÁI) & TÀI CHÍNH CỌC (PHẢI) -->
				<div class="fin-section">
					<!-- Cột trái: Khung ảnh maquette 135px vuông, click bung lightbox -->
					<ArtworkBox v-model="order.artwork_url" />

					<!-- Cột phải: Khối tài chính & Tiến độ cọc -->
					<div class="fin-cols">
						<div class="fin-row">
							<span class="fin-label">Số lượng đặt</span>
							<span class="fin-val text-num font-bold">{{ formatNumber(order.qty) }} {{ order.uom || 'Túi' }}</span>
						</div>
						<div class="fin-row">
							<span class="fin-label">Tiền hàng (cọc 50%)</span>
							<span class="fin-val text-num font-bold">{{ formatCurrency(order.product_total || order.grand_total) }}</span>
						</div>
						<div v-if="order.cylinder_total > 0" class="fin-row">
							<span class="fin-label text-purple">Trục in (100% riêng)</span>
							<span class="fin-val text-purple text-num font-bold">{{ formatCurrency(order.cylinder_total) }}</span>
						</div>

						<div class="fin-divider"></div>

						<!-- Box tóm tắt cọc -->
						<div v-if="order.payment_type === 'Trả sau'" class="postpaid-tag-box">
							<div class="flex-between">
								<span class="font-bold text-xs text-indigo-light">TRẢ SAU (CÔNG NỢ GỐI ĐẦU)</span>
								<span class="text-num text-xs">Hạn mức: <b>{{ formatCurrency(order.credit_limit || 200000000) }}</b></span>
							</div>
						</div>
						<div v-else class="deposit-box">
							<div class="flex-between text-xs">
								<span class="lbl">CẦN CỌC:</span>
								<span class="text-num font-bold text-amber">{{ formatCurrency(order.required_deposit) }}</span>
							</div>
							<div class="flex-between text-xs mt-1">
								<span class="lbl">ĐÃ CỌC:</span>
								<span class="text-num font-bold text-emerald">{{ formatCurrency(order.advance_paid) }} ({{ order.deposit_pct }}%)</span>
							</div>
							<!-- Thanh progress bar -->
							<div class="deposit-track mt-1">
								<div
									class="deposit-fill"
									:style="{ width: Math.min(100, Math.round((order.advance_paid / (order.required_deposit || order.grand_total)) * 100)) + '%' }"
									:class="order.advance_paid >= order.required_deposit ? 'bg-emerald' : 'bg-amber'"
								></div>
								<div class="marker-50"></div>
							</div>
							<div class="flex-between text-xs mt-1 text-secondary">
								<span>Còn thiếu</span>
								<span class="text-num font-bold text-white">{{ formatCurrency(order.outstanding_amount) }}</span>
							</div>
						</div>
					</div>
				</div>

				<!-- KHỐI TRẠNG THÁI VẬN HÀNH (GỌN GÀNG 1 HÀNG) -->
				<div class="ops-card">
					<div class="ops-title">TIẾN ĐỘ THỰC HIỆN</div>
					<div class="ops-grid">
						<template v-if="order.order_tab === 'ngcs'">
							<div class="ops-col">
								<span class="ops-lbl">NCC IN LỤA</span>
								<span class="ops-val font-bold text-white">{{ order.supplier_name || 'ANH TÙNG' }}</span>
							</div>
							<div class="ops-col">
								<span class="ops-lbl">HẠN GIAO NCC</span>
								<span class="sla-badge" :class="supplierSlaBadge(order.supplier_eta_days).cls">
									{{ supplierSlaBadge(order.supplier_eta_days).text }}
								</span>
							</div>
							<div class="ops-col">
								<span class="ops-lbl">PHÔI TÚI</span>
								<span class="ops-val text-emerald font-bold">✓ Đủ trong kho</span>
							</div>
						</template>

						<template v-else-if="order.order_tab === 'xuong_sx'">
							<div class="ops-col">
								<span class="ops-lbl">VẬT TƯ MÀNG</span>
								<span class="ops-val font-bold" :class="order.materials_status === 'Đủ màng' ? 'text-emerald' : 'text-amber'">
									{{ order.materials_status || 'Chờ màng' }}
								</span>
							</div>
							<div class="ops-col">
								<span class="ops-lbl">CÔNG ĐOẠN MÁY</span>
								<span class="ops-val font-bold text-white">{{ order.factory_stage || 'Chờ lên chuyền' }}</span>
							</div>
							<div class="ops-col">
								<span class="ops-lbl">SẢN LƯỢNG</span>
								<span class="ops-val text-num text-emerald font-bold">
									{{ order.completed_qty ? formatNumber(order.completed_qty) + ' / ' + formatNumber(order.qty) : '0 / ' + formatNumber(order.qty) }}
								</span>
							</div>
						</template>

						<template v-else>
							<div class="ops-col">
								<span class="ops-lbl">NHÀ CUNG CẤP</span>
								<span class="ops-val font-bold text-white">{{ order.supplier_name || 'TRANG TÍN' }}</span>
							</div>
							<div class="ops-col">
								<span class="ops-lbl">HẠN GIAO NCC</span>
								<span class="sla-badge" :class="supplierSlaBadge(order.supplier_eta_days).cls">
									{{ supplierSlaBadge(order.supplier_eta_days).text }}
								</span>
							</div>
							<div class="ops-col">
								<span class="ops-lbl">TRẠNG THÁI</span>
								<span class="ops-val font-bold text-white">{{ order.procurement_stage || 'Đang chờ hàng' }}</span>
							</div>
						</template>
					</div>
				</div>
			</div>

			<!-- Footer: Cụm Nút Hành Động 1-Chạm Theo Đúng Bước -->
			<div v-if="order" class="drawer-footer">
				<!-- TRƯỜNG HỢP 1: ĐƠN BỊ HOLD (Thiếu Cọc) - Nhập nhanh cọc ngay tại nút -->
				<div v-if="order.is_hold" class="hold-action-row">
					<div class="hold-inline-form">
						<input
							v-model.number="depositInput"
							type="number"
							class="deposit-input-inline"
							placeholder="Nhập số tiền nộp cọc thêm (đ)..."
						/>
						<button
							type="button"
							class="btn-act-deposit"
							:disabled="!depositInput || savingDeposit"
							@click="handleSaveDeposit"
						>
							{{ savingDeposit ? 'Đang lưu...' : 'Lưu cọc' }}
						</button>
					</div>
					<button
						type="button"
						class="btn-act-override"
						:disabled="approvingProcurement"
						title="Kế toán duyệt ngoại lệ cho phép mua hàng / chạy máy"
						@click="handleAccountantApproveProcurement"
					>
						{{ approvingProcurement ? 'Đang duyệt...' : 'Duyệt ngoại lệ' }}
					</button>
				</div>

				<!-- TRƯỜNG HỢP 2: ĐANG XỬ LÝ / SẴN SÀNG (Nút tương ứng duy nhất) -->
				<div v-else-if="order.order_state !== 'Sẵn sàng giao' && order.order_state !== 'Đã giao'" class="w-full">
					<!-- NGCS -->
					<button
						v-if="order.order_tab === 'ngcs' && order.order_state === 'Sẵn sàng'"
						type="button"
						class="act-btn-main btn-blue"
						@click="triggerNextStage('Đang xử lý', 'Đã gửi in lụa NCC')"
					>
						+ Gửi in lụa NCC ({{ order.supplier_name }})
					</button>
					<button
						v-else-if="order.order_tab === 'ngcs' && order.order_state === 'Đang xử lý'"
						type="button"
						class="act-btn-main btn-green"
						@click="triggerNextStage('Sẵn sàng giao', 'Đã nhận hàng in lụa về kho')"
					>
						Xác nhận nhận hàng in lụa về kho
					</button>

					<!-- Xưởng SX -->
					<button
						v-else-if="order.order_tab === 'xuong_sx' && order.materials_status !== 'Đủ màng'"
						type="button"
						class="act-btn-main btn-amber"
						@click="order.materials_status = 'Đủ màng'; triggerNextStage('Sẵn sàng', 'Đã chuẩn bị đủ màng')"
					>
						+ Đặt mua màng & Trục NCC
					</button>
					<button
						v-else-if="order.order_tab === 'xuong_sx'"
						type="button"
						class="act-btn-main btn-blue"
						@click="triggerNextStage('Sẵn sàng giao', 'Xưởng báo cáo hoàn thành 100%')"
					>
						+ Báo cáo hoàn thành xưởng (Nhập kho TP)
					</button>

					<!-- Mua ngoài -->
					<button
						v-else-if="order.order_tab === 'mua_ngoai' && order.order_state === 'Sẵn sàng'"
						type="button"
						class="act-btn-main btn-blue"
						@click="triggerNextStage('Đang xử lý', 'Đã gửi đơn mua NCC')"
					>
						+ Gửi đơn mua NCC ({{ order.supplier_name }})
					</button>
					<button
						v-else-if="order.order_tab === 'mua_ngoai' && order.order_state === 'Đang xử lý'"
						type="button"
						class="act-btn-main btn-green"
						@click="triggerNextStage('Sẵn sàng giao', 'Đã nhận hàng NCC về kho')"
					>
						Xác nhận nhận hàng NCC về kho
					</button>
				</div>

				<!-- TRƯỜNG HỢP 3: SẴN SÀNG GIAO (Sáng xanh toàn chiều ngang) -->
				<button
					v-else-if="order.order_state === 'Sẵn sàng giao'"
					type="button"
					class="act-btn-main btn-delivery"
					@click="triggerNextStage('Đã giao', 'Xuất kho giao khách')"
				>
					<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<rect x="1" y="3" width="15" height="13"></rect>
						<polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
						<circle cx="5.5" cy="18.5" r="2.5"></circle>
						<circle cx="18.5" cy="18.5" r="2.5"></circle>
					</svg>
					<span>+ XUẤT GIAO HÀNG</span>
				</button>

				<!-- TRƯỜNG HỢP 4: ĐÃ GIAO -->
				<div v-else class="w-full text-center text-emerald font-bold py-2">
					✓ ĐƠN HÀNG ĐÃ GIAO THÀNH CÔNG
				</div>
			</div>
		</aside>
	</div>
</template>

<script setup>
import { ref, watch } from 'vue';
import ArtworkBox from './ArtworkBox.vue';
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

function isMat(mat) {
	if (!order.value || !order.value.materials) return false;
	return order.value.materials.includes(mat);
}

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
			return 'badge-tab-ngcs';
		case 'xuong_sx':
			return 'badge-tab-xuong';
		case 'mua_ngoai':
			return 'badge-tab-ngoai';
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

.drawer-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 14px 20px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.08);
	background: #141820;
}

.drawer-title {
	font-size: 16px;
	font-weight: 800;
	color: #eef1f6;
	letter-spacing: -0.01em;
}

.btn-icon {
	background: transparent;
	border: none;
	color: #9da7b5;
	cursor: pointer;
	padding: 4px;
	display: flex;
	align-items: center;
	border-radius: 6px;
}

.btn-icon:hover {
	color: #fff;
	background: rgba(255, 255, 255, 0.08);
}

/* Top Summary - Chuẩn Drawer 2 Báo Giá */
.drawer-top-summary {
	padding: 14px 20px 12px;
	background: #13171f;
	border-bottom: 1px solid rgba(255, 255, 255, 0.08);
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.cust-brand-bar {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 8px;
}

.cust-info {
	display: flex;
	align-items: center;
	gap: 8px;
	min-width: 0;
}

.icon-building {
	font-size: 15px;
	flex-shrink: 0;
}

.cust-name {
	font-size: 15px;
	font-weight: 800;
	color: #eef1f6;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.brand-tag {
	font-size: 12px;
	font-weight: 800;
	color: #0284c7;
	background: rgba(2, 132, 199, 0.14);
	border: 1px solid rgba(2, 132, 199, 0.3);
	padding: 2px 8px;
	border-radius: 6px;
	flex-shrink: 0;
}

.axis-badges {
	display: flex;
	gap: 6px;
	flex-wrap: wrap;
}

.axis-badge {
	font-size: 11px;
	font-weight: 700;
	padding: 3px 8px;
	border-radius: 5px;
}

.badge-product {
	color: #38bdf8;
	background: rgba(56, 189, 248, 0.12);
	border: 1px solid rgba(56, 189, 248, 0.25);
}

.badge-accessory {
	color: #c084fc;
	background: rgba(192, 132, 252, 0.12);
	border: 1px solid rgba(192, 132, 252, 0.25);
}

.badge-print {
	color: #94a3b8;
	background: rgba(148, 163, 184, 0.12);
	border: 1px solid rgba(148, 163, 184, 0.25);
}

.badge-cylinder {
	color: #f59e0b;
	background: rgba(245, 158, 11, 0.12);
	border: 1px solid rgba(245, 158, 11, 0.25);
}

.badge-tab {
	color: #34d399;
	background: rgba(52, 211, 153, 0.12);
	border: 1px solid rgba(52, 211, 153, 0.25);
}

.badge-tab-ngcs { color: #fbbf24; background: rgba(245, 158, 11, 0.15); border-color: rgba(245, 158, 11, 0.3); }
.badge-tab-xuong { color: #4ea1e0; background: rgba(78, 161, 224, 0.15); border-color: rgba(78, 161, 224, 0.3); }
.badge-tab-ngoai { color: #c084fc; background: rgba(168, 85, 247, 0.15); border-color: rgba(168, 85, 247, 0.3); }

.spec-box {
	display: flex;
	flex-direction: column;
	gap: 4px;
	margin-top: 2px;
}

.spec-line {
	display: flex;
	align-items: center;
	gap: 6px;
}

.spec-icon {
	font-size: 13px;
	flex-shrink: 0;
}

.spec-desc-text {
	font-size: 12.5px;
	font-weight: 700;
	color: #eef1f6;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.spec-dim-text {
	font-size: 12.5px;
	font-weight: 700;
	color: #94a3b8;
	font-variant-numeric: tabular-nums;
}

.mat-chips-wrap {
	display: flex;
	gap: 2px;
	align-items: center;
	padding: 3px 0 1px;
}

.mat-group {
	display: flex;
	gap: 2px;
}

.mat-divider {
	width: 1px;
	height: 12px;
	background: rgba(255, 255, 255, 0.15);
	margin: 0 3px;
}

.mat-chip {
	font-size: 10px;
	font-weight: 700;
	padding: 2px 6px;
	border-radius: 4px;
	background: #1c222b;
	color: #64748b;
}

.chip-blue.on { color: #38bdf8; background: rgba(56, 189, 248, 0.2); }
.chip-amber.on { color: #fbbf24; background: rgba(245, 158, 11, 0.2); }
.chip-purple.on { color: #c084fc; background: rgba(192, 132, 252, 0.2); }
.chip-emerald.on { color: #34d399; background: rgba(52, 211, 153, 0.2); }

/* Body: 2 Cột chuẩn */
.drawer-loading {
	padding: 40px;
	text-align: center;
	color: #9da7b5;
	font-size: 14px;
}

.drawer-body {
	padding: 16px 20px;
	flex: 1;
	overflow-y: auto;
	display: flex;
	flex-direction: column;
	gap: 14px;
}

.fin-section {
	display: flex;
	gap: 16px;
	align-items: flex-start;
}

.fin-cols {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 6px;
}

.fin-row {
	display: flex;
	justify-content: space-between;
	align-items: baseline;
}

.fin-label {
	font-size: 12px;
	color: #9da7b5;
	font-weight: 500;
}

.fin-val {
	font-size: 13.5px;
	color: #eef1f6;
	font-variant-numeric: tabular-nums;
}

.fin-divider {
	height: 1px;
	background: rgba(255, 255, 255, 0.08);
	margin: 3px 0;
}

.deposit-box {
	background: rgba(0, 0, 0, 0.3);
	border: 1px solid rgba(255, 255, 255, 0.06);
	border-radius: 6px;
	padding: 8px 10px;
}

.postpaid-tag-box {
	background: rgba(99, 102, 241, 0.08);
	border: 1px solid rgba(99, 102, 241, 0.25);
	border-radius: 6px;
	padding: 8px 10px;
}

.deposit-track {
	width: 100%;
	height: 5px;
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

.lbl {
	font-size: 10px;
	font-weight: 700;
	color: #94a3b8;
}

/* Khối Vận Hành Ops Card */
.ops-card {
	background: #1a1f27;
	border: 1px solid #3a424e;
	border-radius: 8px;
	padding: 12px 14px;
}

.ops-title {
	font-size: 10.5px;
	font-weight: 800;
	color: #94a3b8;
	letter-spacing: 0.5px;
	margin-bottom: 8px;
}

.ops-grid {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: 8px;
}

.ops-col {
	display: flex;
	flex-direction: column;
	gap: 3px;
}

.ops-lbl {
	font-size: 9.5px;
	font-weight: 700;
	color: #64748b;
}

.ops-val {
	font-size: 12px;
}

.sla-badge {
	display: inline-block;
	font-size: 10.5px;
	font-weight: 700;
	padding: 2px 6px;
	border-radius: 4px;
	white-space: nowrap;
	width: fit-content;
}

.sla-ontime { background: rgba(148, 163, 184, 0.15); color: #94a3b8; }
.sla-today { background: rgba(245, 158, 11, 0.18); color: #fbbf24; }
.sla-overdue { background: rgba(239, 68, 68, 0.25); color: #fca5a5; }

/* Footer Action */
.drawer-footer {
	padding: 14px 20px;
	border-top: 1px solid rgba(255, 255, 255, 0.08);
	background: #13171f;
}

.hold-action-row {
	display: flex;
	gap: 10px;
	width: 100%;
}

.hold-inline-form {
	flex: 1;
	display: flex;
	gap: 6px;
}

.deposit-input-inline {
	flex: 1;
	height: 40px;
	padding: 0 10px;
	background: #1a1f27;
	border: 1px solid #3a424e;
	border-radius: 6px;
	color: #f1f5f9;
	font-size: 13px;
	font-variant-numeric: tabular-nums;
	outline: none;
}

.deposit-input-inline:focus {
	border-color: #f59e0b;
}

.btn-act-deposit {
	height: 40px;
	padding: 0 14px;
	background: #f59e0b;
	color: #0b0f19;
	font-weight: 700;
	font-size: 12.5px;
	border: none;
	border-radius: 6px;
	cursor: pointer;
	white-space: nowrap;
}

.btn-act-deposit:disabled {
	opacity: 0.5;
	cursor: not-allowed;
}

.btn-act-override {
	height: 40px;
	padding: 0 14px;
	background: rgba(245, 158, 11, 0.15);
	color: #fbbf24;
	border: 1px solid rgba(245, 158, 11, 0.4);
	font-weight: 700;
	font-size: 12.5px;
	border-radius: 6px;
	cursor: pointer;
	white-space: nowrap;
}

.act-btn-main {
	width: 100%;
	height: 44px;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8px;
	font-size: 13.5px;
	font-weight: 800;
	border-radius: 8px;
	cursor: pointer;
	border: none;
	transition: all 0.15s ease;
}

.btn-blue {
	background: #4ea1e0;
	color: #0b0f19;
}

.btn-blue:hover {
	background: #60a5fa;
}

.btn-green {
	background: rgba(52, 211, 153, 0.2);
	color: #34d399;
	border: 1px solid rgba(52, 211, 153, 0.4);
}

.btn-amber {
	background: rgba(245, 158, 11, 0.2);
	color: #fbbf24;
	border: 1px solid rgba(245, 158, 11, 0.4);
}

.btn-delivery {
	background: #0284c7;
	color: #ffffff;
	box-shadow: 0 0 14px rgba(2, 132, 199, 0.4);
}

.btn-delivery:hover {
	background: #0369a1;
}

.text-num { font-variant-numeric: tabular-nums; }
.text-emerald { color: #34d399; }
.text-amber { color: #fbbf24; }
.text-purple { color: #c084fc; }
.text-secondary { color: #94a3b8; }
.bg-emerald { background-color: #34d399; }
.bg-amber { background-color: #fbbf24; }
</style>
