<template>
	<!-- QUY TRÌNH 2: PHÔI DÙNG CHUNG (TÚI NGCS & TÚI MÀNG ĐƠN) -->
	<div class="form-section generic-section">
		<!-- Tiêu đề in lụa của khách (Nếu là NGCS) -->
		<div v-if="productGroup === 'Túi NGCS'" class="field-col" style="margin-bottom: 16px;">
			<label class="field-label" for="order-screen-brand">Nội dung / Tên thương hiệu in lụa</label>
			<input
				id="order-screen-brand"
				name="screenPrintBrand"
				type="text"
				:value="screenPrintBrand"
				class="text-input"
				placeholder="VD: CÀ PHÊ NGUYÊN CHẤT DAKLAK"
				aria-label="Nội dung / Tên thương hiệu in lụa"
				@input="$emit('update:screenPrintBrand', $event.target.value)"
			/>
		</div>

		<!-- Danh sách biến thể MTS -->
		<div class="table-container">
			<table class="data-table">
				<thead>
					<tr>
						<th>Mặt hàng</th>
						<th class="text-right">Số lượng (cái)</th>
						<th class="text-right">Đơn giá (đ)</th>
						<th class="text-right">Thành tiền</th>
						<th style="width: 48px;"></th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="(row, idx) in genericRows" :key="idx">
						<td>
							<select
								:id="'gen-item-' + idx"
								name="generic_item"
								:value="row.item_code"
								class="select-input select-table"
								aria-label="Mặt hàng"
								@change="$emit('generic-item-change', idx, $event.target.value)"
							>
								<option v-for="item in availableGenericItems" :key="item.item_code" :value="item.item_code">
									{{ item.item_name }} ({{ item.item_code }})
								</option>
							</select>
						</td>
						<td class="text-right">
							<input
								:id="'gen-qty-' + idx"
								name="generic_qty"
								type="number"
								:value="row.qty"
								class="text-input text-right text-num"
								min="1"
								aria-label="Số lượng (cái)"
								@input="$emit('generic-field', idx, 'qty', Number($event.target.value) || '')"
							/>
						</td>
						<td class="text-right">
							<input
								:id="'gen-rate-' + idx"
								name="generic_rate"
								type="number"
								:value="row.rate"
								class="text-input text-right text-num"
								min="0"
								step="100"
								aria-label="Đơn giá (đ)"
								@input="$emit('generic-field', idx, 'rate', Number($event.target.value) || 0)"
							/>
						</td>
						<td class="text-right text-num bold-num">
							{{ formatCurrency((row.qty || 0) * (row.rate || 0)) }}
						</td>
						<td class="text-center">
							<button
								type="button"
								class="btn-icon-del"
								@click="$emit('remove-generic-row', idx)"
								:disabled="genericRows.length <= 1"
							>
								×
							</button>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<div class="generic-actions">
			<button type="button" class="btn-add-row" @click="$emit('add-generic-row')">
				+ Thêm mặt hàng
			</button>
		</div>
	</div>
</template>

<script setup>
import { useCockpitFormat } from '../../composables/useCockpitFormat';

// Tách từ ModalCreateOrder.vue — QUY TRÌNH 2 MTS. Spec/despec theo Item native,
// không nhãn cứng. Thành tiền dòng chỉ hiển thị (tổng do backend chốt).
defineProps({
	productGroup: { type: String, default: '' },
	screenPrintBrand: { type: String, default: '' },
	genericRows: { type: Array, default: () => [] },
	availableGenericItems: { type: Array, default: () => [] },
});

defineEmits([
	'update:screenPrintBrand',
	'generic-item-change',
	'generic-field',
	'add-generic-row',
	'remove-generic-row',
]);

const { formatCurrency } = useCockpitFormat();
</script>

<style scoped>
.form-section {
	background: var(--surface-card);
	border: 1px solid rgba(255, 255, 255, 0.06);
	border-radius: 8px;
	padding: 16px;
}

.field-col {
	display: flex;
	flex-direction: column;
	gap: 6px;
}

.field-label {
	font-size: 13px;
	font-weight: 600;
	color: var(--ink-faint);
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

.table-container {
	overflow-x: auto;
}

.data-table {
	width: 100%;
	border-collapse: collapse;
}

.data-table th {
	font-size: 12px;
	font-weight: 600;
	color: var(--ink-faint);
	padding: 8px;
	border-bottom: 1px solid var(--outline);
}

.data-table td {
	padding: 6px;
	vertical-align: middle;
}

.select-table {
	width: 100%;
}

.btn-icon-del {
	background: transparent;
	border: none;
	color: var(--danger);
	font-size: 18px;
	cursor: pointer;
	padding: 4px 8px;
	border-radius: 4px;
}

.btn-icon-del:hover:not(:disabled) {
	background: rgba(248, 81, 73, 0.1);
}

.btn-icon-del:disabled {
	opacity: 0.3;
	cursor: not-allowed;
}

.generic-actions {
	margin-top: 10px;
	display: flex;
	justify-content: flex-end;
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
.bold-num {
	font-weight: 700;
	color: var(--ink-strong);
}
</style>
