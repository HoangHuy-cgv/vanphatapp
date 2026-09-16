<template>
	<!-- KHỐI 3: ĐỐI SOÁT TÀI CHÍNH TỐI GIẢN & ACTIONS -->
	<div class="finance-footer-card">
		<div class="fin-summary-rows">
			<div class="fin-row">
				<span class="fin-label">Tiền hàng (chưa VAT):</span>
				<span class="fin-val text-num">{{ formatCurrency(serverPricing.net_total) }}</span>
			</div>
			<div class="fin-row">
				<span class="fin-label">Thuế VAT ({{ serverPricing.vat_rate }}%):</span>
				<span class="fin-val text-num">{{ formatCurrency(serverPricing.vat_amount) }}</span>
			</div>
			<div v-if="serverPricing.cylinder_pending" class="fin-row">
				<span class="fin-label">Tiền trục:</span>
				<span class="fin-val text-num text-amber">Chờ giá NCC</span>
			</div>
			<div v-else-if="serverPricing.cylinder_total > 0" class="fin-row">
				<span class="fin-label">Tiền trục:</span>
				<span class="fin-val text-num">{{ formatCurrency(serverPricing.cylinder_total) }}</span>
			</div>
			<div class="fin-row total-row">
				<span class="fin-label-lg">TỔNG THANH TOÁN:</span>
				<span v-if="serverPricing.cylinder_pending" class="fin-val-lg text-num text-amber">Chưa chốt (chờ trục)</span>
				<span v-else class="fin-val-lg text-num">{{ formatCurrency(serverPricing.grand_total) }}</span>
			</div>
			<div v-if="paymentType === 'Trả trước'" class="fin-row deposit-row">
				<span class="fin-label">Cọc yêu cầu:</span>
				<span v-if="serverPricing.cylinder_pending" class="fin-val-deposit text-num text-amber">Chờ giá NCC</span>
				<span v-else class="fin-val-deposit text-num">{{ formatCurrency(serverPricing.required_deposit) }}</span>
			</div>
		</div>

		<div class="form-actions">
			<button type="button" class="btn-cancel" @click="$emit('close')" :disabled="isSubmitting">
				Hủy
			</button>
			<button
				type="submit"
				class="btn-submit"
				:disabled="isSubmitting || isCalculatingPrice"
				:class="{ 'opacity-60 cursor-not-allowed': isSubmitting || isCalculatingPrice }"
			>
				<span v-if="isSubmitting">ĐANG TẠO ĐƠN...</span>
				<span v-else-if="isCalculatingPrice">ĐANG ĐỐI SOÁT GIÁ...</span>
				<span v-else>+ TẠO ĐƠN HÀNG</span>
			</button>
		</div>
	</div>
</template>

<script setup>
import { useCockpitFormat } from '../../composables/useCockpitFormat';

// Tách từ ModalCreateOrder.vue — đối soát từ `order.get_price_preview`,
// client chỉ hiển thị, không tự tính tiền/thuế/cọc.
defineProps({
	serverPricing: { type: Object, default: () => ({}) },
	paymentType: { type: String, default: '' },
	isSubmitting: { type: Boolean, default: false },
	isCalculatingPrice: { type: Boolean, default: false },
});

defineEmits(['close']);

const { formatCurrency } = useCockpitFormat();
</script>

<style scoped>
/* Financial Footer Card */
.finance-footer-card {
	background: var(--surface-low);
	border: 1px solid var(--outline);
	border-radius: 8px;
	padding: 16px 20px;
	display: flex;
	justify-content: space-between;
	align-items: flex-end;
}

.fin-summary-rows {
	display: flex;
	flex-direction: column;
	gap: 6px;
	min-width: 320px;
}

.fin-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	font-size: 13px;
	color: var(--ink-faint);
}

.fin-val {
	color: var(--ink-strong);
	font-weight: 600;
}

.total-row {
	border-top: 1px solid rgba(255, 255, 255, 0.1);
	padding-top: 6px;
	margin-top: 4px;
}

.fin-label-lg {
	font-size: 14px;
	font-weight: 700;
	color: var(--ink-bright);
}

.fin-val-lg {
	font-size: 18px;
	font-weight: 800;
	color: var(--primary);
}

.deposit-row {
	font-size: 12px;
	color: var(--amber);
}

.fin-val-deposit {
	font-size: 14px;
	font-weight: 700;
	color: var(--amber);
}

.form-actions {
	display: flex;
	gap: 12px;
}

.btn-cancel {
	background: var(--raised);
	border: 1px solid var(--outline);
	color: var(--ink-pale);
	font-size: 14px;
	font-weight: 600;
	padding: 10px 20px;
	border-radius: 6px;
	cursor: pointer;
	transition: all 0.15s ease;
}

.btn-cancel:hover {
	background: var(--raised-hover);
	color: var(--ink-bright);
}

.btn-submit {
	background: var(--accent-blue);
	border: none;
	color: var(--ink-bright);
	font-size: 14px;
	font-weight: 700;
	padding: 10px 24px;
	border-radius: 6px;
	cursor: pointer;
	box-shadow: 0 2px 8px rgba(2, 132, 199, 0.4);
	transition: all 0.15s ease;
}

.btn-submit:hover {
	background: var(--accent-blue-press);
}

/* Utilities */
.text-num {
	font-variant-numeric: tabular-nums;
	font-feature-settings: 'tnum';
}
.text-amber {
	color: var(--amber);
}
</style>
