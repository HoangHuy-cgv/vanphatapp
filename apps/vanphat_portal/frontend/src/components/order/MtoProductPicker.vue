<template>
	<!-- Chọn sản phẩm của khách + thông số tự bung -->
	<div>
		<div class="product-picker-bar">
			<div class="field-col flex-1">
				<label class="field-label">Sản phẩm độc quyền của khách</label>
				<select
					:value="selectedCustomItemCode"
					class="select-input"
					@change="$emit('custom-item-change', $event.target.value)"
					required
				>
					<option value="" disabled>-- Chọn quy cách đã lưu của khách --</option>
					<option v-for="item in availableCustomItems" :key="item.item_code" :value="item.item_code">
						{{ item.custom_alias || item.item_name }} ({{ item.dimensions_text }})
					</option>
				</select>
			</div>
		</div>

		<div v-if="currentCustomItem" class="item-specs-banner">
			<div class="banner-specs">
				<span class="spec-tag">{{ currentCustomItem.dimensions_text }}</span>
				<span class="spec-tag text-cyan">{{ currentCustomItem.accessory }}</span>
				<span class="spec-tag text-purple">{{ currentCustomItem.print_type }}</span>
				<div class="mat-chips-row">
					<span v-for="m in currentCustomItem.materials" :key="m" class="mat-chip-badge">
						{{ m }}
					</span>
				</div>
			</div>
			<div class="banner-price">
				Đơn giá chuẩn: <span class="font-bold text-emerald">{{ formatCurrency(currentCustomItem.base_rate) }}</span> / {{ currentCustomItem.uom }}
			</div>
		</div>
	</div>
</template>

<script setup>
import { useCockpitFormat } from '../../composables/useCockpitFormat';

// Tách từ OrderMtoSection.vue — section 1: product-picker + specs banner (thuần hiển thị).
defineProps({
	selectedCustomItemCode: { type: String, default: '' },
	availableCustomItems: { type: Array, default: () => [] },
	currentCustomItem: { type: Object, default: null },
});

defineEmits(['custom-item-change']);

const { formatCurrency } = useCockpitFormat();
</script>

<style scoped>
.field-col {
	display: flex;
	flex-direction: column;
	gap: 6px;
}

.flex-1 {
	flex: 1;
}

.field-label {
	font-size: 13px;
	font-weight: 600;
	color: var(--ink-faint);
}

.product-picker-bar {
	display: flex;
	gap: 12px;
}

.text-input,
.select-input {
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

.text-input:focus,
.select-input:focus {
	border-color: var(--primary);
	box-shadow: 0 0 0 1px var(--primary);
}

.item-specs-banner {
	display: flex;
	justify-content: space-between;
	align-items: center;
	background: var(--surface-low);
	border: 1px solid rgba(78, 161, 224, 0.2);
	border-radius: 6px;
	padding: 10px 14px;
	margin-top: 14px;
	margin-bottom: 14px;
}

.banner-specs {
	display: flex;
	align-items: center;
	gap: 8px;
	flex-wrap: wrap;
}

.spec-tag {
	font-size: 12px;
	font-weight: 600;
	color: var(--ink-strong);
	background: rgba(255, 255, 255, 0.08);
	padding: 2px 8px;
	border-radius: 4px;
}

.mat-chips-row {
	display: flex;
	gap: 4px;
}

.mat-chip-badge {
	font-size: 11px;
	font-weight: 700;
	background: rgba(56, 189, 248, 0.15);
	color: var(--info);
	padding: 2px 6px;
	border-radius: 4px;
	border: 1px solid rgba(56, 189, 248, 0.3);
}

.banner-price {
	font-size: 13px;
	color: var(--ink-faint);
}

.text-cyan {
	color: var(--info);
}
.text-purple {
	color: var(--violet);
}
.text-emerald {
	color: var(--emerald);
}
</style>
