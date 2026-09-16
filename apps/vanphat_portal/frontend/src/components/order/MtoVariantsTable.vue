<template>
	<!-- Bảng Danh Sách Mẫu In / Hương Vị (Variants) -->
	<div class="table-block">
		<div class="table-block-head">
			<span class="block-title">DANH SÁCH MẪU IN / HƯƠNG VỊ</span>
			<button type="button" class="btn-add-row" @click="$emit('add-variant-row')">
				+ Thêm mẫu in
			</button>
		</div>

		<table class="form-table">
			<thead>
				<tr>
					<th style="width: 35%;">Tên mẫu in / Hương vị</th>
					<th style="width: 20%; text-align: right;">Số lượng</th>
					<th style="width: 10%; text-align: center;">ĐVT</th>
					<th style="width: 15%; text-align: right;">Đơn giá</th>
					<th style="width: 15%; text-align: right;">Thành tiền</th>
					<th style="width: 5%;"></th>
				</tr>
			</thead>
			<tbody>
				<tr v-for="(row, idx) in variantRows" :key="idx">
					<td>
						<input
							:id="'var-name-' + idx"
							name="variant_name"
							type="text"
							:value="row.variant_name"
							class="text-input"
							placeholder="VD: Nước phở bò, Màu Hồng..."
							aria-label="Tên mẫu in / biến thể"
							required
							@input="$emit('variant-field', idx, 'variant_name', $event.target.value)"
						/>
					</td>
					<td>
						<input
							:id="'var-qty-' + idx"
							name="qty"
							type="number"
							:value="row.qty"
							class="text-input text-right text-num"
							min="1"
							step="1"
							aria-label="Số lượng (cái)"
							required
							@input="$emit('variant-field', idx, 'qty', Number($event.target.value) || '')"
						/>
					</td>
					<td class="text-center font-medium text-secondary">
						{{ currentCustomItem ? currentCustomItem.uom : 'Túi' }}
					</td>
					<td>
						<input
							:id="'var-rate-' + idx"
							name="rate"
							type="number"
							:value="row.rate"
							class="text-input text-right text-num"
							min="0"
							aria-label="Đơn giá (đ)"
							required
							@input="$emit('variant-field', idx, 'rate', Number($event.target.value) || 0)"
						/>
					</td>
					<td class="text-right text-num font-bold text-white">
						{{ formatCurrency(row.qty * row.rate) }}
					</td>
					<td class="text-center">
						<button
							v-if="variantRows.length > 1"
							type="button"
							class="btn-remove-row"
							title="Xóa dòng"
							@click="$emit('remove-variant-row', idx)"
						>
							✕
						</button>
					</td>
				</tr>
			</tbody>
		</table>
	</div>
</template>

<script setup>
import { useCockpitFormat } from '../../composables/useCockpitFormat';

// Tách từ OrderMtoSection.vue — section 2: bảng variants (thu input + hiển thị, không math).
defineProps({
	variantRows: { type: Array, default: () => [] },
	currentCustomItem: { type: Object, default: null },
});

defineEmits([
	'variant-field',
	'add-variant-row',
	'remove-variant-row',
]);

const { formatCurrency } = useCockpitFormat();
</script>

<style scoped>
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

.table-block {
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.table-block-head {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.block-title {
	font-size: 12px;
	font-weight: 700;
	letter-spacing: 0.5px;
	color: var(--ink-faint);
}

.btn-add-row {
	background: rgba(78, 161, 224, 0.1);
	border: 1px solid rgba(78, 161, 224, 0.3);
	color: var(--primary);
	font-size: 12px;
	font-weight: 600;
	padding: 4px 10px;
	border-radius: 4px;
	cursor: pointer;
	transition: all 0.15s ease;
}

.btn-add-row:hover {
	background: var(--primary);
	color: var(--canvas-deep);
}

.form-table {
	width: 100%;
	border-collapse: collapse;
}

.form-table th {
	font-size: 12px;
	font-weight: 600;
	color: var(--ink-faint);
	padding: 8px;
	border-bottom: 1px solid var(--outline);
}

.form-table td {
	padding: 6px;
	vertical-align: middle;
}

.btn-remove-row {
	background: transparent;
	border: none;
	color: var(--danger);
	font-size: 14px;
	cursor: pointer;
	padding: 4px;
}

.btn-remove-row:hover {
	color: var(--danger-light);
}

/* Utilities */
.text-num {
	font-variant-numeric: tabular-nums;
	font-feature-settings: 'tnum';
}
.text-right {
	text-align: right;
}
.text-center {
	text-align: center;
}
.text-secondary {
	color: var(--ink-faint);
}
.text-white {
	color: var(--ink-bright);
}
</style>
