<template>
	<!-- KHỐI ẢNH THIẾT KẾ & TỔNG TIỀN (BỐ CỤC 2 CỘT .fin-section CHUẨN) -->
	<div class="fin-section">
		<!-- Cột trái: Khung ảnh maquette 135px -->
		<ArtworkBox :model-value="artworkUrl" @update:model-value="$emit('artwork-input', $event)" />

		<!-- Cột phải: Khối tài chính (render số server trả) -->
		<div class="fin-cols">
			<div class="fin-row">
				<span class="fin-label">Tổng số lượng</span>
				<span class="fin-val font-bold">{{ figures.total_qty || '0' }} {{ isRoll ? 'm' : 'Túi' }}</span>
			</div>
			<div class="fin-row">
				<span class="fin-label">Tiền hàng (chưa thuế)</span>
				<span class="fin-val font-bold">{{ figures.subtotal || '0 đ' }}</span>
			</div>
			<div v-if="needCylinder" class="fin-row">
				<span class="fin-label">Tiền trục in</span>
				<span class="fin-val font-bold">{{ figures.cylinder_total || '0 đ' }}</span>
			</div>
			<div class="fin-row">
				<span class="fin-label">Thuế ({{ taxLabel }})</span>
				<span class="fin-val">{{ figures.tax_amount || '0 đ' }}</span>
			</div>
			<div class="fin-divider"></div>
			<div class="fin-row">
				<span class="fin-label-total">TỔNG THANH TOÁN</span>
				<span class="fin-val-total">{{ figures.grand_total || '0 đ' }}</span>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed } from 'vue';
import ArtworkBox from '../ArtworkBox.vue';

// Tách từ DrawerStep2Director.vue — client chỉ hiển thị số server, không tự tính.
// P1 review: nhãn thuế dùng vat_rate server (không cứng 8%); thiếu → '—'.
const props = defineProps({
	artworkUrl: { type: String, default: '' },
	figures: { type: Object, default: () => ({}) },
	isRoll: { type: Boolean, default: false },
	needCylinder: { type: Boolean, default: false },
});

defineEmits(['artwork-input']);

const taxLabel = computed(() => {
	const r = Number(props.figures && props.figures.vat_rate);
	return Number.isFinite(r) ? r + '%' : '—';
});
</script>

<style scoped>
.fin-section {
	display: grid;
	grid-template-columns: 135px 1fr;
	gap: 14px;
	margin-top: 14px;
}
.fin-cols { display: flex; flex-direction: column; gap: 6px; }
.fin-row { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; }
.fin-label { font-size: 12px; color: var(--ink-faint); }
.fin-val { font-size: 13px; color: var(--ink-strong); font-variant-numeric: tabular-nums; }
.font-bold { font-weight: 700; }
.fin-divider { border-top: 1px solid rgba(255, 255, 255, 0.08); margin: 4px 0; }
.fin-label-total { font-size: 12px; font-weight: 800; color: var(--ink-bright); }
.fin-val-total { font-size: 16px; font-weight: 800; color: var(--emerald); font-variant-numeric: tabular-nums; }
</style>
