<template>
	<!-- QUY TRÌNH 1: SẢN PHẨM ĐỘC QUYỀN (TÚI MÀNG GHÉP / CUỘN MÀNG GHÉP) -->
	<div class="form-section mto-section">
		<MtoProductPicker
			:selected-custom-item-code="selectedCustomItemCode"
			:available-custom-items="availableCustomItems"
			:current-custom-item="currentCustomItem"
			@custom-item-change="$emit('custom-item-change', $event)"
		/>

		<MtoVariantsTable
			:variant-rows="variantRows"
			:current-custom-item="currentCustomItem"
			@variant-field="(...args) => $emit('variant-field', ...args)"
			@add-variant-row="$emit('add-variant-row')"
			@remove-variant-row="$emit('remove-variant-row', $event)"
		/>

		<MtoCylinderBlock
			:has-new-cylinders="hasNewCylinders"
			:cylinder-count="cylinderCount"
			:cylinder-supplier="cylinderSupplier"
			:cylinder-unit-price="cylinderUnitPrice"
			:server-pricing="serverPricing"
			@update:has-new-cylinders="$emit('update:hasNewCylinders', $event)"
			@update:cylinder-count="$emit('update:cylinderCount', $event)"
			@update:cylinder-supplier="$emit('update:cylinderSupplier', $event)"
			@update:cylinder-unit-price="$emit('update:cylinderUnitPrice', $event)"
		/>
	</div>
</template>

<script setup>
import MtoProductPicker from './MtoProductPicker.vue';
import MtoVariantsTable from './MtoVariantsTable.vue';
import MtoCylinderBlock from './MtoCylinderBlock.vue';

// Composition mỏng tách từ OrderMtoSection.vue 456 dòng (pattern DrawerStep2Director 761→229).
// Props/emits giữ nguyên — caller ModalCreateOrder.vue không đổi. Tiền chỉ format
// trong con via useCockpitFormat, không math ở vỏ.
defineProps({
	selectedCustomItemCode: { type: String, default: '' },
	availableCustomItems: { type: Array, default: () => [] },
	currentCustomItem: { type: Object, default: null },
	variantRows: { type: Array, default: () => [] },
	hasNewCylinders: { type: Boolean, default: false },
	cylinderCount: { type: [Number, String], default: 0 },
	cylinderSupplier: { type: String, default: '' },
	cylinderUnitPrice: { type: [Number, null], default: null },
	serverPricing: { type: Object, default: () => ({}) },
});

defineEmits([
	'custom-item-change',
	'variant-field',
	'add-variant-row',
	'remove-variant-row',
	'update:hasNewCylinders',
	'update:cylinderCount',
	'update:cylinderSupplier',
	'update:cylinderUnitPrice',
]);
</script>

<style scoped>
.form-section {
	background: var(--surface-card);
	border: 1px solid rgba(255, 255, 255, 0.06);
	border-radius: 8px;
	padding: 16px;
}
</style>
