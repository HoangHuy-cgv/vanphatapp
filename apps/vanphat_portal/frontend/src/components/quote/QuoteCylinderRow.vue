<template>
	<!-- Dòng Trục in (nếu Chưa có trục) -->
	<div v-if="needCylinder" class="cylinder-row">
		<div class="cyl-label-wrap">
			<span class="badge-cyl-tag">TRỤC IN</span>
			<span class="cyl-title">Trục in (1 màu = 1 cây)</span>
		</div>
		<input
			id="step2-cylinder-qty"
			name="step2_cylinder_qty"
			:model-value="qty"
			type="number"
			class="form-input no-spin text-center w-110"
			placeholder="Số cây"
			aria-label="Số cây trục in"
			@input="$emit('qty-input', qtyOrEmpty($event))"
		/>
		<input
			id="step2-cylinder-rate"
			name="step2_cylinder_rate"
			:value="rateDisplay"
			type="text"
			class="form-input text-center w-120 read-only"
			placeholder="Giá chưa thuế"
			aria-label="Giá trục chưa thuế (từ NCC)"
			readonly
		/>
	</div>
</template>

<script setup>
// Tách từ DrawerStep2Director.vue — presentational, giá trục read-only từ NCC.
// P1 review: qty xóa trắng → '' (không NaN) như v-model.number cũ.
defineProps({
	needCylinder: { type: Boolean, default: false },
	qty: { type: [Number, String], default: 1 },
	rateDisplay: { type: String, default: 'Chờ giá NCC' },
});

defineEmits(['qty-input']);

function qtyOrEmpty(e) {
	const v = e.target.valueAsNumber;
	return Number.isNaN(v) ? '' : v;
}
</script>

<style scoped>
.cylinder-row {
	display: flex;
	gap: 8px;
	align-items: center;
	margin-top: 10px;
	padding: 10px 12px;
	background: rgba(192, 132, 252, 0.05);
	border: 1px dashed rgba(192, 132, 252, 0.35);
	border-radius: 8px;
}
.cyl-label-wrap { flex: 1; display: flex; align-items: center; gap: 8px; min-width: 0; }
.badge-cyl-tag {
	font-size: 10px;
	font-weight: 800;
	color: var(--violet);
	background: rgba(192, 132, 252, 0.15);
	padding: 2px 8px;
	border-radius: 4px;
	letter-spacing: 0.5px;
}
.cyl-title { font-size: 12px; color: var(--ink-faint); }
.form-input {
	background: var(--surface-sunken);
	border: 1px solid rgba(255, 255, 255, 0.12);
	border-radius: 6px;
	color: var(--ink-bright);
	font-size: 13px;
	padding: 8px 10px;
	min-width: 0;
}
.w-110 { flex: 0 0 110px; }
.w-120 { flex: 0 0 120px; }
.text-center { text-align: center; }
.read-only { opacity: 0.7; }
.no-spin::-webkit-outer-spin-button, .no-spin::-webkit-inner-spin-button { -webkit-appearance: none; }
.no-spin { -moz-appearance: textfield; appearance: textfield; }
</style>
