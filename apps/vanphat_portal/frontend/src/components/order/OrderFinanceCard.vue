<template>
	<!-- KHỐI 3: ĐỐI SOÁT TÀI CHÍNH TỐI GIẢN (KHÔNG OVER-DESIGN) -->
	<div class="finance-card">
		<div class="fin-grid">
			<div class="fin-item">
				<span class="fin-label">Tiền hàng (chưa VAT)</span>
				<span class="fin-val text-num">{{ formatCurrency(order.product_total ?? order.net_total) }}</span>
			</div>
			<div class="fin-item">
				<span class="fin-label">Thuế VAT ({{ order.vat_rate || 8 }}%)</span>
				<span class="fin-val text-num">{{ formatCurrency(order.vat_amount) }}</span>
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
				<span class="fin-val text-num font-bold" :class="Number(order.advance_paid) >= Number(order.required_deposit) ? 'text-emerald' : 'text-amber'">
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
</template>

<script setup>
import { useCockpitFormat } from '../../composables/useCockpitFormat';

// Tách từ DrawerOrderDetail.vue — chỉ hiển thị số server trả, không tự tính.
defineProps({
	order: { type: Object, required: true },
});

const { formatCurrency } = useCockpitFormat();
</script>

<style scoped>
/* KHỐI 3: ĐỐI SOÁT TÀI CHÍNH TỐI GIẢN */
.finance-card {
	background: var(--surface);
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
	color: var(--ink-faint);
}

.fin-val {
	font-size: 15px;
	color: var(--ink-strong);
}

.highlight-total {
	grid-column: span 2;
	background: var(--surface-low);
	padding: 10px 14px;
	border-radius: 6px;
	border: 1px solid rgba(78, 161, 224, 0.3);
	margin-top: 4px;
}

.fin-label-lg {
	font-size: 15px;
	font-weight: 700;
	color: var(--ink-bright);
}

.fin-val-lg {
	font-size: 18px;
	font-weight: 800;
	color: var(--primary);
}

/* Utilities */
.text-num {
	font-variant-numeric: tabular-nums;
	font-feature-settings: 'tnum';
}
.text-emerald {
	color: var(--emerald);
}
.text-amber {
	color: var(--amber);
}
</style>
