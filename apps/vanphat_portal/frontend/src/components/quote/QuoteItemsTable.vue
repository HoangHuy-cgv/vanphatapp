<template>
	<!-- BẢNG DANH SÁCH MẪU IN (editable rows) -->
	<div>
		<div class="items-head">
			<span class="section-label">Danh sách mẫu in</span>
			<button
				type="button"
				class="btn-sm-ghost"
				@click="$emit('add-row')"
			>
				+ Thêm mẫu in
			</button>
		</div>

		<div class="items-container">
			<div
				v-for="(row, idx) in rows"
				:key="idx"
				class="item-row"
			>
				<input
					:id="'step2-item-name-' + idx"
					name="step2_item_name"
					:model-value="row.item_name"
					type="text"
					class="form-input"
					placeholder="Mẫu in"
					:aria-label="'Mẫu in dòng ' + (idx + 1)"
					autocomplete="off"
					@input="$emit('row-input', idx, 'item_name', $event.target.value)"
				/>
				<input
					:id="'step2-item-qty-' + idx"
					name="step2_item_qty"
					:model-value="row.qty"
					type="number"
					class="form-input no-spin text-center w-110"
					placeholder="Số lượng"
					:aria-label="'Số lượng dòng ' + (idx + 1)"
					@input="$emit('row-input', idx, 'qty', numOrEmpty($event))"
				/>
				<input
					:id="'step2-item-rate-' + idx"
					name="step2_item_rate"
					:model-value="row.rate"
					type="number"
					class="form-input no-spin text-center w-120"
					placeholder="Giá chưa thuế"
					:aria-label="'Giá chưa thuế dòng ' + (idx + 1)"
					@input="$emit('row-input', idx, 'rate', numOrEmpty($event))"
				/>
				<button
					v-if="rows.length > 1"
					type="button"
					class="btn-icon-del"
					:title="'Xóa dòng ' + (idx + 1)"
					:aria-label="'Xóa dòng ' + (idx + 1)"
					@click="$emit('remove-row', idx)"
				>
					✕
				</button>
			</div>
		</div>
	</div>
</template>

<script setup>
// Tách từ DrawerStep2Director.vue — rows là ref từ composable (one-way xuống,
// mọi sửa emit lên parent gọi composable, không mutate prop).
// P1 review: valueAsNumber → NaN khi xóa trắng (khác v-model.number cũ giữ '') —
// guard về '' để payload preview giữ ngữ nghĩa cũ (trống = chưa nhập).
defineProps({
	rows: { type: Array, default: () => [] },
});

defineEmits(['add-row', 'remove-row', 'row-input']);

function numOrEmpty(e) {
	const v = e.target.valueAsNumber;
	return Number.isNaN(v) ? '' : v;
}
</script>

<style scoped>
.items-head {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 10px;
}
.section-label {
	font-size: 12px;
	font-weight: 700;
	color: var(--ink-faint);
	letter-spacing: 0.5px;
	text-transform: uppercase;
}
.btn-sm-ghost {
	background: transparent;
	border: 1px dashed rgba(78, 161, 224, 0.5);
	color: var(--primary);
	font-size: 12px;
	font-weight: 700;
	padding: 4px 12px;
	border-radius: 6px;
	cursor: pointer;
}
.items-container { display: flex; flex-direction: column; gap: 8px; }
.item-row { display: flex; gap: 8px; align-items: center; }
.form-input {
	flex: 1;
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
.no-spin::-webkit-outer-spin-button, .no-spin::-webkit-inner-spin-button { -webkit-appearance: none; }
.no-spin { -moz-appearance: textfield; appearance: textfield; }
.btn-icon-del {
	background: transparent;
	border: none;
	color: var(--danger-soft);
	font-size: 14px;
	cursor: pointer;
	padding: 4px 8px;
}
</style>
