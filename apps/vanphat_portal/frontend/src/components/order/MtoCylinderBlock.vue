<template>
	<!-- Phần Trục In (Nếu có) -->
	<div class="cylinder-block">
		<label class="checkbox-label">
			<input
				id="order-has-cylinders"
				name="hasNewCylinders"
				type="checkbox"
				:checked="hasNewCylinders"
				@change="$emit('update:hasNewCylinders', $event.target.checked)"
			/>
			<span>Đơn hàng có làm bộ trục in mới</span>
		</label>

		<div v-if="hasNewCylinders" class="cylinder-inputs">
			<div class="cyl-col">
				<label class="field-label-sm" for="order-cyl-count">Số cây trục</label>
				<input
					id="order-cyl-count"
					name="cylinderCount"
					type="number"
					:value="cylinderCount"
					class="text-input text-right text-num"
					min="1"
					aria-label="Số cây trục"
					@input="$emit('update:cylinderCount', Number($event.target.value) || 0)"
				/>
			</div>
			<div class="cyl-col">
				<label class="field-label-sm" for="order-cyl-supplier">NCC trục</label>
				<input
					id="order-cyl-supplier"
					name="cylinderSupplier"
					type="text"
					:value="cylinderSupplier"
					class="text-input"
					placeholder="VD: Kiến Tâm"
					aria-label="NCC trục"
					@input="$emit('update:cylinderSupplier', $event.target.value)"
				/>
			</div>
			<div class="cyl-col">
				<label class="field-label-sm" for="order-cyl-price">Giá NCC (VNĐ/cây)</label>
				<input
					id="order-cyl-price"
					name="cylinderUnitPrice"
					type="number"
					:value="cylinderUnitPrice"
					class="text-input text-right text-num"
					min="0"
					step="100000"
					placeholder="Giá NCC báo"
					aria-label="Giá NCC (VNĐ/cây)"
					@input="$emit('update:cylinderUnitPrice', Number($event.target.value) || null)"
				/>
			</div>
			<div class="cyl-col">
				<label class="field-label-sm">Tiền trục</label>
				<div v-if="serverPricing.cylinder_pending" class="cyl-total-val text-num text-amber">Chờ giá NCC</div>
				<div v-else class="cyl-total-val text-num">{{ formatCurrency(serverPricing.cylinder_total) }}</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { useCockpitFormat } from '../../composables/useCockpitFormat';

// Tách từ OrderMtoSection.vue — section 3: khối trục in (cylinder_spec, tiền do backend cộng).
defineProps({
	hasNewCylinders: { type: Boolean, default: false },
	cylinderCount: { type: [Number, String], default: 0 },
	cylinderSupplier: { type: String, default: '' },
	cylinderUnitPrice: { type: [Number, null], default: null },
	serverPricing: { type: Object, default: () => ({}) },
});

defineEmits([
	'update:hasNewCylinders',
	'update:cylinderCount',
	'update:cylinderSupplier',
	'update:cylinderUnitPrice',
]);

const { formatCurrency } = useCockpitFormat();
</script>

<style scoped>
.field-label-sm {
	font-size: 12px;
	font-weight: 600;
	color: var(--ink-faint);
}

.text-input {
	height: 38px;
	background: var(--surface);
	border: 1px solid var(--outline);
	border-radius: 6px;
	color: var(--ink-bright);
	padding: 0 12px;
	font-size: 14px;
	font-family: inherit;
	outline: none;
	transition: border-color 0.15s ease;
}

.text-input:focus {
	border-color: var(--primary);
	box-shadow: 0 0 0 1px var(--primary);
}

.cylinder-block {
	margin-top: 14px;
	padding-top: 14px;
	border-top: 1px dashed rgba(255, 255, 255, 0.1);
}

.checkbox-label {
	display: flex;
	align-items: center;
	gap: 8px;
	font-size: 13px;
	font-weight: 600;
	color: var(--ink-strong);
	cursor: pointer;
}

.cylinder-inputs {
	display: grid;
	grid-template-columns: 120px 180px 1fr 140px;
	gap: 12px;
	margin-top: 10px;
	background: var(--surface);
	padding: 12px;
	border-radius: 6px;
	border: 1px solid rgba(255, 255, 255, 0.08);
}

.cyl-total-val {
	height: 38px;
	display: flex;
	align-items: center;
	font-size: 15px;
	font-weight: 700;
	color: var(--ink-strong);
}

/* Utilities */
.text-num {
	font-variant-numeric: tabular-nums;
	font-feature-settings: 'tnum';
}
.text-right {
	text-align: right;
}
.text-amber {
	color: var(--amber);
}
</style>
