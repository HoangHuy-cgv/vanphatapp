<template>
	<!-- KHỐI TOP-SUMMARY: KH + brand + axis badges + quy cách + chip vật liệu -->
	<div class="drawer-top-summary">
		<!-- LINE 1: Tên khách hàng & Brand Tag -->
		<div class="cust-brand-bar">
			<div class="cust-info">
				<span class="cust-name">{{ formData.customer || 'Khách hàng' }}</span>
			</div>
			<div v-if="formData.brand" class="brand-tag">
				{{ formData.brand }}
			</div>
		</div>

		<!-- LINE 2: badges — hasPrint là boolean-prop (không so tên cứng trong template) -->
		<div class="axis-badges">
			<span class="axis-badge badge-product">{{ formData.product_type }}</span>
			<span v-if="!isRoll" class="axis-badge badge-accessory">{{ formData.accessory }}</span>
			<span class="axis-badge badge-print">{{ formData.print_type }}</span>
			<span v-if="hasPrint" class="axis-badge badge-cylinder">{{ formData.cylinder_status }}</span>
		</div>

		<!-- KHỐI QUY CÁCH KỸ THUẬT CHO GIÁM ĐỐC RA QUYẾT ĐỊNH -->
		<div class="spec-box">
			<!-- LINE 3: Mô tả sản phẩm -->
			<div class="spec-line">
				<span class="spec-desc-text">{{ formData.description || 'Chưa có mô tả sản phẩm' }}</span>
			</div>

			<!-- LINE 4: Kích thước biên dịch đầy đủ nhãn & đơn vị đo -->
			<div class="spec-line">
				<span class="spec-dim-text">{{ compiledDimensions }}</span>
			</div>

			<!-- LINE 5: Chip vật liệu từ cấu trúc màng native (triple rule 2+3) -->
			<div v-if="materialOptions.length" class="mat-chips-wrap" role="radiogroup" aria-label="Vật liệu màng">
				<button
					v-for="m in materialOptions"
					:key="m.code"
					type="button"
					class="mat-chip"
					:class="[m.cls, { on: isSelected(m.code) }]"
					role="radio"
					:aria-checked="isSelected(m.code)"
					@click="$emit('toggle-material', m.code)"
				>
					{{ m.code }}
				</button>
			</div>
		</div>
	</div>
</template>

<script setup>
// Tách từ DrawerStep2Director.vue — presentational, click chip emit lên parent.
defineProps({
	formData: { type: Object, default: () => ({}) },
	isRoll: { type: Boolean, default: false },
	hasPrint: { type: Boolean, default: true },
	compiledDimensions: { type: String, default: '' },
	materialOptions: { type: Array, default: () => [] },
	isSelected: { type: Function, default: () => false },
});

defineEmits(['toggle-material']);
</script>

<style scoped>
.drawer-top-summary {
	padding: 16px 22px 12px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.08);
	display: flex;
	flex-direction: column;
	gap: 10px;
}
.cust-brand-bar {
	display: flex;
	justify-content: space-between;
	align-items: center;
	gap: 10px;
}
.cust-name {
	font-size: 16px;
	font-weight: 700;
	color: var(--ink-bright);
}
.brand-tag {
	font-size: 12px;
	font-weight: 700;
	color: var(--violet);
	background: rgba(192, 132, 252, 0.12);
	border: 1px solid rgba(192, 132, 252, 0.35);
	padding: 2px 10px;
	border-radius: 20px;
}
.axis-badges {
	display: flex;
	flex-wrap: wrap;
	gap: 6px;
}
.axis-badge {
	font-size: 11px;
	font-weight: 700;
	padding: 2px 10px;
	border-radius: 20px;
	border: 1px solid;
}
.badge-product { color: var(--primary); border-color: rgba(78, 161, 224, 0.4); background: rgba(78, 161, 224, 0.1); }
.badge-accessory { color: var(--emerald); border-color: rgba(52, 211, 153, 0.4); background: rgba(52, 211, 153, 0.1); }
.badge-print { color: var(--amber-bright); border-color: rgba(251, 191, 36, 0.4); background: rgba(251, 191, 36, 0.1); }
.badge-cylinder { color: var(--violet); border-color: rgba(192, 132, 252, 0.4); background: rgba(192, 132, 252, 0.1); }
.spec-box {
	background: rgba(255, 255, 255, 0.03);
	border: 1px solid rgba(255, 255, 255, 0.06);
	border-radius: 8px;
	padding: 10px 12px;
	display: flex;
	flex-direction: column;
	gap: 6px;
}
.spec-desc-text { font-size: 13px; color: var(--ink-strong); }
.spec-dim-text { font-size: 12px; color: var(--ink-faint); font-variant-numeric: tabular-nums; }
.mat-chips-wrap { display: flex; flex-wrap: wrap; gap: 6px; }
.mat-chip {
	font-size: 12px;
	font-weight: 700;
	padding: 3px 12px;
	border-radius: 20px;
	border: 1px solid rgba(255, 255, 255, 0.15);
	background: transparent;
	color: var(--ink-faint);
	cursor: pointer;
}
.mat-chip.on { color: var(--ink-bright); border-color: currentColor; }
.chip-blue.on { color: var(--primary); background: rgba(78, 161, 224, 0.15); }
.chip-amber.on { color: var(--amber-bright); background: rgba(251, 191, 36, 0.15); }
.chip-purple.on { color: var(--violet); background: rgba(192, 132, 252, 0.15); }
.chip-emerald.on { color: var(--emerald); background: rgba(52, 211, 153, 0.15); }
</style>
