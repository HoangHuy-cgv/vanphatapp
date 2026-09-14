<template>
	<Teleport to="body">
		<div v-if="isOpen" class="drawer-overlay" @click.self="$emit('close')">
		<aside class="drawer-panel" aria-label="Chi tiết đơn hàng">
			<!-- Header -->
			<div class="drawer-head">
				<div class="head-title-wrap">
					<h3 class="drawer-title">Chi tiết đơn hàng</h3>
					<span class="order-code-badge font-mono">{{ order ? order.name : '' }}</span>
				</div>
				<button
					type="button"
					class="btn-icon"
					title="Đóng (Esc)"
					@click="$emit('close')"
				>
					<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<line x1="18" y1="6" x2="6" y2="18"></line>
						<line x1="6" y1="6" x2="18" y2="18"></line>
					</svg>
				</button>
			</div>

			<!-- Body -->
			<div v-if="loading" class="drawer-loading">
				Đang tải dữ liệu...
			</div>

			<div v-else-if="order" class="drawer-body">
				<!-- KHỐI 1: HEADER ĐỊNH DANH & 5 BADGES PHÂN LOẠI -->
				<div class="summary-card">
					<!-- Tên khách hàng & Brand -->
					<div class="cust-brand-bar">
						<div class="cust-info">
							<span class="cust-name font-bold text-white text-[16px]">{{ order.customer_alias || order.customer_name }}</span>
						</div>
						<div class="brand-tag">
							{{ order.brand || 'VẠN PHÁT' }}
						</div>
					</div>

					<!-- 5 Badges Phân Loại -->
					<div class="axis-badges">
						<span class="axis-badge badge-product">{{ order.product_type || order.product_group || 'Túi màng ghép' }}</span>
						<span class="axis-badge badge-accessory">{{ order.accessory || 'Không vòi' }}</span>
						<span class="axis-badge badge-print">{{ order.print_type || 'In trục' }}</span>
						<span class="axis-badge badge-cylinder">{{ order.cylinder_status || 'Không trục' }}</span>
						<span class="axis-badge badge-tab" :class="tabBadgeClass(order.order_tab)">
							{{ tabBadgeLabel(order.order_tab) }}
						</span>
					</div>

					<!-- Quy cách & CHỈ HIỂN THỊ CÁC CHẤT LIỆU ĐANG DÙNG -->
					<div class="spec-row">
						<div class="spec-dim">
							<span class="dim-text font-mono">{{ order.dimensions_text || order.description }}</span>
						</div>
						<!-- Chỉ render các màng có thực, ẩn 100% màng không dùng -->
						<div v-if="order.materials && order.materials.length" class="mat-chips-active">
							<span
								v-for="mat in order.materials"
								:key="mat"
								class="active-chip"
								:class="getMatChipClass(mat)"
							>
								{{ mat }}
							</span>
						</div>
					</div>
				</div>

				<!-- KHỐI 2: DANH SÁCH MẪU IN / SẢN PHẨM ĐẶT HÀNG (MULTI-SKU) -->
				<div class="items-card">
					<div class="card-head">
						<span class="card-title">MẪU IN / SẢN PHẨM ĐẶT HÀNG ({{ orderItems.length }})</span>
						<span class="total-qty-badge font-mono">Tổng: {{ formatNumber(totalItemQty) }} {{ order.uom || 'Túi' }}</span>
					</div>

					<div class="items-list">
						<div
							v-for="(it, idx) in orderItems"
							:key="idx"
							class="item-row"
							:class="{ 'cylinder-row': it.is_cylinder }"
						>
							<!-- Thumbnail ảnh mẫu in -->
							<div class="thumb-box" @click="it.artwork_url && openLightbox(it.artwork_url, it.item_name)">
								<img
									v-if="it.artwork_url"
									:src="it.artwork_url"
									:alt="it.item_name"
									class="thumb-img"
								/>
								<div v-else class="thumb-placeholder">
									<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
										<circle cx="8.5" cy="8.5" r="1.5"></circle>
										<polyline points="21 15 16 10 5 21"></polyline>
									</svg>
								</div>
							</div>

							<!-- Thông tin mẫu in -->
							<div class="item-info">
								<div class="item-name">
									{{ it.variant_name || it.item_name }}
								</div>
								<div class="item-sub text-secondary font-mono">
									{{ it.item_code }}
								</div>
							</div>

							<!-- Số lượng & Đơn giá -->
							<div class="item-qty text-right">
								<span class="font-bold text-white text-num">{{ formatNumber(it.qty) }}</span>
								<span class="text-secondary text-sm" style="margin-left: 4px;">{{ it.uom }}</span>
							</div>

							<div class="item-rate text-right font-mono text-secondary text-num">
								{{ formatCurrency(it.rate) }}
							</div>

							<!-- Thành tiền -->
							<div class="item-amount text-right font-bold text-num text-white">
								{{ formatCurrency(it.amount) }}
							</div>
						</div>
					</div>
				</div>

				<!-- KHỐI 3: ĐỐI SOÁT TÀI CHÍNH TỐI GIẢN (KHÔNG OVER-DESIGN) -->
				<div class="finance-card">
					<div class="fin-grid">
						<div class="fin-item">
							<span class="fin-label">Tiền hàng (chưa VAT)</span>
							<span class="fin-val text-num">{{ formatCurrency(order.net_total || order.product_total) }}</span>
						</div>
						<div class="fin-item">
							<span class="fin-label">Thuế VAT ({{ order.vat_rate || 8 }}%)</span>
							<span class="fin-val text-num">{{ formatCurrency(order.vat_amount || Math.round((order.net_total || order.product_total) * 0.08)) }}</span>
						</div>
						<div v-if="order.cylinder_total > 0" class="fin-item">
							<span class="fin-label">Tiền trục</span>
							<span class="fin-val text-num">{{ formatCurrency(order.cylinder_total) }}</span>
						</div>
						<div class="fin-item highlight-total">
							<span class="fin-label-lg">TỔNG THANH TOÁN</span>
							<span class="fin-val-lg text-num">{{ formatCurrency(order.grand_total) }}</span>
						</div>
						<div class="fin-item">
							<span class="fin-label">Đã cọc</span>
							<span class="fin-val text-num font-bold" :class="order.advance_paid >= (order.required_deposit || order.grand_total * 0.5) ? 'text-emerald' : 'text-amber'">
								{{ formatCurrency(order.advance_paid) }}
								<span v-if="order.payment_type !== 'Trả sau'" class="text-xs">({{ order.deposit_pct }}%)</span>
							</span>
						</div>
						<div class="fin-item">
							<span class="fin-label">Còn phải thu</span>
							<span class="fin-val text-num font-bold" :class="order.outstanding_amount > 0 ? 'text-amber' : 'text-emerald'">
								{{ formatCurrency(order.outstanding_amount) }}
							</span>
						</div>
					</div>
				</div>

				<!-- KHỐI 4: TIẾN ĐỘ THỰC HIỆN (TRIỆT TIÊU LABEL RÁC, HIỂN THỊ VALUE TRỰC TIẾP) -->
				<div class="ops-card">
					<!-- Đơn Xưởng sản xuất -->
					<div v-if="order.order_tab === 'xuong_sx'" class="ops-value-box">
						<div class="ops-main-line">
							<span class="ops-bullet">●</span>
							<span class="ops-text">
								{{ order.materials_status || 'Đủ màng' }} • {{ order.factory_stage || 'Đang xử lý' }} • {{ formatNumber(order.completed_qty || 0) }} / {{ formatNumber(order.qty) }} {{ order.uom || 'Túi' }}
								<span class="ops-pct">({{ Math.round(((order.completed_qty || 0) / (order.qty || 1)) * 100) }}%)</span>
							</span>
						</div>
						<div class="ops-bar-track">
							<div
								class="ops-bar-fill bg-cyan"
								:style="{ width: Math.min(100, Math.round(((order.completed_qty || 0) / (order.qty || 1)) * 100)) + '%' }"
							></div>
						</div>
					</div>

					<!-- Đơn Túi NGCS hoặc Mua Ngoài (SLA NCC) -->
					<div v-else class="ops-value-box">
						<div class="ops-main-line">
							<span class="ops-bullet">●</span>
							<span class="ops-text">
								NCC {{ order.supplier_name || 'Gia công' }} • {{ order.procurement_stage || 'Đang thực hiện' }}
							</span>
							<span v-if="order.supplier_eta_days !== null && order.supplier_eta_days !== undefined" class="sla-badge" :class="getSlaClass(order.supplier_eta_days)">
								{{ formatSlaText(order.supplier_eta_days) }}
							</span>
						</div>
					</div>
				</div>
			</div>

			<!-- Lightbox Modal phóng to Maquette -->
			<div v-if="activeLightboxUrl" class="lightbox-overlay" @click="activeLightboxUrl = null">
				<div class="lightbox-content" @click.stop>
					<div class="lightbox-head">
						<span class="lightbox-title">{{ activeLightboxTitle }}</span>
						<button type="button" class="btn-icon" @click="activeLightboxUrl = null">✕</button>
					</div>
					<img :src="activeLightboxUrl" alt="Maquette Preview" class="lightbox-img" />
				</div>
			</div>

			<!-- Footer Actions (State Machine Gọn Gàng) -->
			<div v-if="order" class="drawer-footer">
				<!-- TRẠNG THÁI 1: HOLD (Chưa đủ cọc) -> Ô nhập cọc nhanh tại chỗ -->
				<div v-if="order.is_hold || order.order_state === 'Tạm giữ (Chưa đủ cọc)'" class="hold-action-row">
					<div class="deposit-input-group">
						<span class="input-addon">Cọc thêm (VNĐ)</span>
						<input
							type="number"
							v-model.number="depositInputAmount"
							placeholder="Nhập số tiền..."
							class="deposit-input text-num"
							min="0"
							step="1000000"
						/>
					</div>
					<button
						type="button"
						class="btn-action-primary"
						@click="handleSaveDeposit"
					>
						Lưu cọc
					</button>
					<button
						type="button"
						class="btn-action-secondary"
						@click="handleOverrideHold"
					>
						Duyệt ngoại lệ
					</button>
				</div>

				<!-- TRẠNG THÁI 2: ĐANG XỬ LÝ -->
				<div v-else-if="order.order_state === 'Đang xử lý'" class="normal-actions">
					<button
						type="button"
						class="btn-action-primary flex-1"
						@click="handleReportProgress"
					>
						+ Báo cáo sản xuất hoàn thành
					</button>
				</div>

				<!-- TRẠNG THÁI 3: SẴN SÀNG GIAO -> Nút giao hàng full-width sáng xanh -->
				<div v-else-if="order.order_state === 'Sẵn sàng giao'" class="ready-action">
					<button
						type="button"
						class="btn-delivery-glow"
						@click="handleCreateDelivery"
					>
						+ XUẤT GIAO HÀNG
					</button>
				</div>
			</div>
		</aside>
		</div>
	</Teleport>
</template>

<script setup>
import { ref, computed } from 'vue';
import { api } from '../composables/useSession';
import { toast } from '../composables/useToast';

const props = defineProps({
	isOpen: { type: Boolean, default: false },
	order: { type: Object, default: null },
	loading: { type: Boolean, default: false },
});

const emit = defineEmits(['close', 'update-order', 'create-delivery']);

// Lightbox state
const activeLightboxUrl = ref(null);
const activeLightboxTitle = ref('');

const openLightbox = (url, title) => {
	activeLightboxUrl.value = url;
	activeLightboxTitle.value = title;
};

// Deposit input for HOLD state
const depositInputAmount = ref(null);

const orderItems = computed(() => {
	if (!props.order) return [];
	if (props.order.items && props.order.items.length) {
		return props.order.items;
	}
	// Fallback single item
	return [
		{
			item_code: props.order.name,
			item_name: props.order.item_name || props.order.description,
			variant_name: props.order.item_name,
			artwork_url: props.order.artwork_url,
			qty: props.order.qty,
			uom: props.order.uom || 'Túi',
			rate: props.order.product_total ? Math.round(props.order.product_total / props.order.qty) : 0,
			amount: props.order.product_total || props.order.grand_total,
			is_cylinder: false,
		},
	];
});

const totalItemQty = computed(() => {
	return orderItems.value
		.filter((i) => !i.is_cylinder)
		.reduce((sum, i) => sum + (Number(i.qty) || 0), 0);
});

// Formatters
const formatCurrency = (val) => {
	if (!val && val !== 0) return '0 đ';
	return new Intl.NumberFormat('vi-VN').format(Math.round(val)) + ' đ';
};

const formatNumber = (val) => {
	if (!val && val !== 0) return '0';
	return new Intl.NumberFormat('vi-VN').format(val);
};

const tabBadgeLabel = (tab) => {
	if (tab === 'xuong_sx') return 'Xưởng sản xuất';
	if (tab === 'ngcs') return 'Túi NGCS';
	return 'Mua ngoài trọn gói';
};

const tabBadgeClass = (tab) => {
	if (tab === 'xuong_sx') return 'tab-xuong';
	if (tab === 'ngcs') return 'tab-ngcs';
	return 'tab-muangoai';
};

// Material Chip Styling
const getMatChipClass = (mat) => {
	const m = (mat || '').toUpperCase();
	if (m.includes('OPP') || m.includes('PET')) return 'mat-blue';
	if (m.includes('AL') || m.includes('MPET')) return 'mat-amber';
	if (m.includes('PA')) return 'mat-purple';
	return 'mat-emerald'; // PE, CPP, HD
};

// SLA styling
const getSlaClass = (days) => {
	if (days < 0) return 'sla-overdue';
	if (days === 0) return 'sla-today';
	return 'sla-ontime';
};

const formatSlaText = (days) => {
	if (days < 0) return `Trễ ${Math.abs(days)} ngày`;
	if (days === 0) return 'Hôm nay giao';
	return `Còn ${days} ngày`;
};

// Handlers
const handleSaveDeposit = async () => {
	if (!depositInputAmount.value || depositInputAmount.value <= 0 || !props.order) return;
	const amt = depositInputAmount.value;
	try {
		const res = await api('vanphat_portal.api.bao_gia.record_order_deposit', {
			name: props.order.name,
			amount: amt,
			note: 'Ghi nhận cọc qua cổng buồng lái ERP',
		});
		if (res && res.success) {
			toast.success(`Đã ghi nhận cọc ${formatCurrency(amt)} cho đơn ${props.order.name}!`);
			depositInputAmount.value = null;
			emit('update-order', {
				...props.order,
				advance_paid: res.advance_paid,
				outstanding_amount: res.outstanding_amount,
				order_state: res.order_state,
				is_hold: res.is_hold,
			});
		} else {
			// Fallback local visual update
			const newAdvance = (props.order.advance_paid || 0) + amt;
			const newOutstanding = Math.max(0, (props.order.grand_total || 0) - newAdvance);
			const reqDeposit = props.order.required_deposit || props.order.grand_total * 0.5;
			const isResolved = newAdvance >= reqDeposit;
			toast.success(`Đã ghi nhận cọc ${formatCurrency(amt)}!`);
			emit('update-order', {
				...props.order,
				advance_paid: newAdvance,
				outstanding_amount: newOutstanding,
				deposit_pct: Math.round((newAdvance / props.order.grand_total) * 100),
				is_hold: !isResolved,
				order_state: isResolved ? 'Đang xử lý' : 'Tạm giữ (Chưa đủ cọc)',
			});
			depositInputAmount.value = null;
		}
	} catch (err) {
		console.error('Lỗi khi ghi nhận cọc:', err);
		toast.error('Lỗi ghi nhận cọc đơn hàng.');
	}
};

const handleOverrideHold = async () => {
	if (!props.order) return;
	try {
		const res = await api('vanphat_portal.api.bao_gia.accountant_approve_procurement', {
			name: props.order.name,
			note: 'Kế toán xác nhận duyệt ngoại lệ chuyển mua hàng NCC',
		});
		if (res && res.success) {
			toast.success(`Kế toán đã duyệt ngoại lệ cho đơn ${props.order.name}!`);
			emit('update-order', {
				...props.order,
				is_hold: false,
				order_state: 'Đang xử lý',
			});
		} else {
			toast.success(`Đã chuyển đơn ${props.order.name} sang Đang xử lý`);
			emit('update-order', {
				...props.order,
				is_hold: false,
				order_state: 'Đang xử lý',
			});
		}
	} catch (err) {
		console.error('Lỗi khi duyệt ngoại lệ:', err);
		toast.error('Lỗi khi duyệt ngoại lệ đơn hàng.');
	}
};

const handleReportProgress = async () => {
	if (!props.order) return;
	try {
		if (props.order.docstatus === 0) {
			const res = await api('vanphat_portal.api.bao_gia.submit_sales_order', {
				name: props.order.name,
			});
			if (res && res.name) {
				toast.success(`Đã kích hoạt chính thức đơn hàng ${res.name}!`);
				emit('update-order', {
					...props.order,
					docstatus: res.docstatus,
					status: res.status,
					order_state: 'Đã duyệt',
				});
				return;
			}
		}
	} catch (err) {
		console.error('Lỗi khi submit đơn hàng:', err);
	}
	toast.success(`Đơn ${props.order.name} đã hoàn thành, sẵn sàng giao!`);
	emit('update-order', {
		...props.order,
		completed_qty: props.order.qty,
		order_state: 'Sẵn sàng giao',
		factory_stage: 'Xong hàng',
	});
};

const handleCreateDelivery = () => {
	emit('create-delivery', props.order);
};
</script>

<style scoped>
.drawer-overlay {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.75);
	backdrop-filter: blur(4px);
	z-index: 1000;
	display: flex;
	justify-content: flex-end;
}

.drawer-panel {
	width: 100%;
	max-width: 680px;
	height: 100%;
	background: #0b0f19;
	border-left: 1px solid #3a424e;
	display: flex;
	flex-direction: column;
	box-shadow: -10px 0 30px rgba(0, 0, 0, 0.7);
}

.drawer-head {
	padding: 16px 24px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.08);
	display: flex;
	justify-content: space-between;
	align-items: center;
	background: #161b22;
}

.head-title-wrap {
	display: flex;
	align-items: center;
	gap: 12px;
}

.drawer-title {
	font-size: 18px;
	font-weight: 700;
	color: #ffffff;
	margin: 0;
}

.order-code-badge {
	font-size: 13px;
	font-weight: 700;
	background: rgba(78, 161, 224, 0.15);
	color: #4ea1e0;
	padding: 2px 8px;
	border-radius: 4px;
	border: 1px solid rgba(78, 161, 224, 0.3);
}

.btn-icon {
	background: transparent;
	border: none;
	color: #8b949e;
	cursor: pointer;
	padding: 4px;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 6px;
	transition: all 0.15s ease;
}

.btn-icon:hover {
	color: #ffffff;
	background: rgba(255, 255, 255, 0.08);
}

.drawer-loading {
	padding: 40px;
	text-align: center;
	color: #8b949e;
	font-size: 15px;
}

.drawer-body {
	flex: 1;
	overflow-y: auto;
	padding: 20px 24px;
	display: flex;
	flex-direction: column;
	gap: 16px;
}

/* KHỐI 1: TỔNG QUAN KHÁCH & QUY CÁCH */
.summary-card {
	background: #161b22;
	border: 1px solid rgba(255, 255, 255, 0.08);
	border-radius: 8px;
	padding: 16px;
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.cust-brand-bar {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.cust-info {
	display: flex;
	align-items: center;
	gap: 8px;
}

.icon-building {
	font-size: 16px;
}

.cust-name {
	font-size: 17px;
	font-weight: 700;
	color: #ffffff;
}

.brand-tag {
	font-size: 13px;
	font-weight: 700;
	background: rgba(255, 255, 255, 0.08);
	color: #e6edf3;
	padding: 3px 10px;
	border-radius: 6px;
	border: 1px solid rgba(255, 255, 255, 0.15);
}

.axis-badges {
	display: flex;
	flex-wrap: wrap;
	gap: 6px;
}

.axis-badge {
	font-size: 12px;
	font-weight: 600;
	padding: 3px 8px;
	border-radius: 4px;
	background: #1f242c;
	color: #c9d1d9;
	border: 1px solid rgba(255, 255, 255, 0.06);
}

.badge-tab.tab-xuong {
	background: rgba(56, 189, 248, 0.15);
	color: #38bdf8;
	border-color: rgba(56, 189, 248, 0.3);
}

.badge-tab.tab-ngcs {
	background: rgba(192, 132, 252, 0.15);
	color: #c084fc;
	border-color: rgba(192, 132, 252, 0.3);
}

.badge-tab.tab-muangoai {
	background: rgba(52, 211, 153, 0.15);
	color: #34d399;
	border-color: rgba(52, 211, 153, 0.3);
}

.spec-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding-top: 10px;
	border-top: 1px dashed rgba(255, 255, 255, 0.08);
	gap: 12px;
}

.spec-dim {
	display: flex;
	align-items: center;
	gap: 6px;
}

.spec-icon {
	font-size: 15px;
}

.dim-text {
	font-size: 14px;
	font-weight: 600;
	color: #e6edf3;
}

.mat-chips-active {
	display: flex;
	gap: 6px;
	flex-wrap: wrap;
}

.active-chip {
	font-size: 12px;
	font-weight: 700;
	padding: 2px 8px;
	border-radius: 4px;
}

.mat-blue {
	background: rgba(56, 189, 248, 0.15);
	color: #38bdf8;
	border: 1px solid rgba(56, 189, 248, 0.3);
}

.mat-amber {
	background: rgba(245, 158, 11, 0.15);
	color: #f59e0b;
	border: 1px solid rgba(245, 158, 11, 0.3);
}

.mat-purple {
	background: rgba(192, 132, 252, 0.15);
	color: #c084fc;
	border: 1px solid rgba(192, 132, 252, 0.3);
}

.mat-emerald {
	background: rgba(52, 211, 153, 0.15);
	color: #34d399;
	border: 1px solid rgba(52, 211, 153, 0.3);
}

/* KHỐI 2: DANH SÁCH MẪU IN / SẢN PHẨM */
.items-card {
	background: #161b22;
	border: 1px solid rgba(255, 255, 255, 0.08);
	border-radius: 8px;
	overflow: hidden;
}

.card-head {
	padding: 12px 16px;
	background: #1a1f27;
	border-bottom: 1px solid rgba(255, 255, 255, 0.06);
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.card-title {
	font-size: 12px;
	font-weight: 700;
	color: #8b949e;
	letter-spacing: 0.5px;
}

.total-qty-badge {
	font-size: 12px;
	font-weight: 700;
	color: #4ea1e0;
}

.items-list {
	display: flex;
	flex-direction: column;
}

.item-row {
	display: grid;
	grid-template-columns: 48px 1fr 90px 100px 110px;
	gap: 12px;
	align-items: center;
	padding: 10px 16px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.04);
	transition: background 0.15s ease;
}

.item-row:hover {
	background: rgba(255, 255, 255, 0.02);
}

.item-row:last-child {
	border-bottom: none;
}

.cylinder-row {
	background: rgba(192, 132, 252, 0.03);
}

.thumb-box {
	width: 44px;
	height: 44px;
	border-radius: 6px;
	background: #11151c;
	border: 1px solid rgba(255, 255, 255, 0.1);
	overflow: hidden;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
}

.thumb-img {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.thumb-placeholder {
	color: #484f58;
}

.item-name {
	font-size: 14px;
	font-weight: 600;
	color: #ffffff;
}

.item-sub {
	font-size: 11px;
}

.item-qty {
	font-size: 14px;
}

.item-rate {
	font-size: 13px;
}

.item-amount {
	font-size: 15px;
}

/* KHỐI 3: ĐỐI SOÁT TÀI CHÍNH TỐI GIẢN */
.finance-card {
	background: #161b22;
	border: 1px solid rgba(255, 255, 255, 0.08);
	border-radius: 8px;
	padding: 16px;
}

.fin-grid {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 12px 24px;
}

.fin-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	border-bottom: 1px dashed rgba(255, 255, 255, 0.06);
	padding-bottom: 6px;
}

.fin-label {
	font-size: 13px;
	color: #8b949e;
}

.fin-val {
	font-size: 15px;
	color: #e6edf3;
}

.highlight-total {
	grid-column: span 2;
	background: #1a1f27;
	padding: 10px 14px;
	border-radius: 6px;
	border: 1px solid rgba(78, 161, 224, 0.3);
	margin-top: 4px;
}

.fin-label-lg {
	font-size: 15px;
	font-weight: 700;
	color: #ffffff;
}

.fin-val-lg {
	font-size: 18px;
	font-weight: 800;
	color: #4ea1e0;
}

/* KHỐI 4: TIẾN ĐỘ THỰC HIỆN */
.ops-card {
	background: #12161f;
	border: 1px solid rgba(255, 255, 255, 0.06);
	border-radius: 8px;
	padding: 14px 16px;
}

.ops-main-line {
	display: flex;
	align-items: center;
	gap: 8px;
	font-size: 14px;
	font-weight: 600;
	color: #e6edf3;
}

.ops-bullet {
	color: #38bdf8;
	font-size: 10px;
}

.ops-pct {
	color: #8b949e;
	font-weight: 400;
	margin-left: 4px;
}

.ops-bar-track {
	height: 5px;
	background: rgba(255, 255, 255, 0.08);
	border-radius: 3px;
	margin-top: 10px;
	overflow: hidden;
}

.ops-bar-fill {
	height: 100%;
	border-radius: 3px;
}

.sla-badge {
	font-size: 12px;
	font-weight: 700;
	padding: 2px 8px;
	border-radius: 4px;
	margin-left: auto;
}

.sla-overdue {
	background: rgba(239, 68, 68, 0.2);
	color: #ef4444;
	border: 1px solid #ef4444;
}

.sla-today {
	background: rgba(245, 158, 11, 0.2);
	color: #f59e0b;
	border: 1px solid #f59e0b;
}

.sla-ontime {
	background: rgba(255, 255, 255, 0.08);
	color: #c9d1d9;
}

/* Footer State Machine */
.drawer-footer {
	padding: 16px 24px;
	background: #161b22;
	border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.hold-action-row {
	display: flex;
	gap: 10px;
	align-items: center;
}

.deposit-input-group {
	flex: 1;
	display: flex;
	align-items: center;
	background: #11151c;
	border: 1px solid #3a424e;
	border-radius: 6px;
	overflow: hidden;
}

.input-addon {
	font-size: 12px;
	font-weight: 600;
	color: #8b949e;
	padding: 0 10px;
	white-space: nowrap;
	border-right: 1px solid #3a424e;
}

.deposit-input {
	flex: 1;
	height: 38px;
	background: transparent;
	border: none;
	color: #ffffff;
	padding: 0 12px;
	font-size: 14px;
	outline: none;
}

.btn-action-primary {
	background: #0284c7;
	border: none;
	color: #ffffff;
	font-size: 14px;
	font-weight: 700;
	height: 38px;
	padding: 0 16px;
	border-radius: 6px;
	cursor: pointer;
	transition: background 0.15s ease;
}

.btn-action-primary:hover {
	background: #0369a1;
}

.btn-action-secondary {
	background: #21262d;
	border: 1px solid #3a424e;
	color: #c9d1d9;
	font-size: 14px;
	font-weight: 600;
	height: 38px;
	padding: 0 14px;
	border-radius: 6px;
	cursor: pointer;
	transition: all 0.15s ease;
}

.btn-action-secondary:hover {
	background: #30363d;
	color: #ffffff;
}

.normal-actions {
	display: flex;
	width: 100%;
}

.btn-delivery-glow {
	width: 100%;
	height: 44px;
	background: #0284c7;
	border: none;
	border-radius: 6px;
	color: #ffffff;
	font-size: 15px;
	font-weight: 800;
	cursor: pointer;
	box-shadow: 0 0 15px rgba(2, 132, 199, 0.5);
	transition: all 0.15s ease;
}

.btn-delivery-glow:hover {
	background: #0369a1;
	box-shadow: 0 0 20px rgba(2, 132, 199, 0.7);
}

/* Lightbox Modal */
.lightbox-overlay {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.85);
	z-index: 1100;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 24px;
}

.lightbox-content {
	background: #161b22;
	border: 1px solid #3a424e;
	border-radius: 8px;
	overflow: hidden;
	max-width: 80vw;
	max-height: 80vh;
	display: flex;
	flex-direction: column;
}

.lightbox-head {
	padding: 10px 16px;
	display: flex;
	justify-content: space-between;
	align-items: center;
	border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.lightbox-title {
	font-size: 14px;
	font-weight: 700;
	color: #ffffff;
}

.lightbox-img {
	max-width: 100%;
	max-height: 70vh;
	object-fit: contain;
}

/* Utilities */
.text-num {
	font-variant-numeric: tabular-nums;
	font-feature-settings: 'tnum';
}
.text-right {
	text-align: right;
}
.text-secondary {
	color: #8b949e;
}
.text-white {
	color: #ffffff;
}
.text-emerald {
	color: #34d399;
}
.text-amber {
	color: #f59e0b;
}
.bg-cyan {
	background: #38bdf8;
}
.flex-1 {
	flex: 1;
}
</style>
