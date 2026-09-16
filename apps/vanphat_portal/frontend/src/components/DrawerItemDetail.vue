<template>
	<DetailShell :open="isOpen" label="Chi tiết mặt hàng" accent="#4ea1e0" panel-bg="#0b0f19" head-bg="#161b22" :compact="true" :fixed-head="true" @close="$emit('close')">
		<template #head>
			<span class="vp-head-code vp-mono" :title="'Mã nội bộ: ' + (item ? item.item_code : '')">{{ headCode }}</span>
		</template>

		<div v-if="loading" class="vp-loading">
			Đang tải...
		</div>

		<div v-else-if="item">
			<DetailHero :title="item.custom_alias || item.item_name || '—'" :title-attr="(item.item_name || '') + ' [' + (item.item_code || '') + ']'" />

			<div v-if="detailLines.length" class="spec-lines text-sm">
				<div v-for="(line, idx) in detailLines" :key="idx" class="spec-line vp-mono">
					<span class="spec-k">{{ line.k }}</span>
					<span class="spec-v" :class="line.cls || 'text-white'">{{ line.v }}</span>
				</div>
			</div>

			<div v-if="bom && bom.items && bom.items.length" class="bom-cockpit-block mt-3">
				<div class="bom-cockpit-head">
					<span class="bom-title vp-mono vp-accent font-semibold">BOM: {{ bom.master?.bom_no }}</span>
					<span class="bom-basis text-sm vp-text-secondary vp-mono">1.000 {{ bom.master?.uom || item.stock_uom || 'Túi' }}</span>
				</div>
				<div class="bom-table-wrap">
					<table class="bom-table">
						<thead>
							<tr>
								<th style="width: 22%;">Vật tư</th>
								<th style="width: 56%;">Tên nguyên liệu</th>
								<th class="text-right" style="width: 22%;">Định mức</th>
							</tr>
						</thead>
						<tbody>
							<tr v-for="(bi, idx) in bom.items" :key="idx" class="bom-row">
								<td class="vp-mono vp-accent text-sm">{{ bi.item_code }}</td>
								<td class="font-medium text-white text-sm truncate" :title="bi.item_name || ''">
									{{ bi.custom_alias || bi.item_name || bi.item_code }}
								</td>
								<td class="text-right font-bold text-num text-sm">
									{{ formatNumber(bi.qty) }}
									<span class="text-sm vp-text-secondary font-normal">{{ bi.uom }}</span>
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>
		</div>
	</DetailShell>
</template>

<script setup>
import { computed } from 'vue';
import DetailShell from './DetailShell.vue';
import DetailHero from './DetailHero.vue';
import { useCockpitFormat } from '../composables/useCockpitFormat';
import { detailLinesOf } from '../composables/useItemSpec';

const props = defineProps({
	isOpen: { type: Boolean, default: false },
	item: { type: Object, default: null },
	bom: { type: Object, default: null },
	loading: { type: Boolean, default: false },
});

const emit = defineEmits(['close']);

// S7c: formatter dùng chung.
const { formatNumber } = useCockpitFormat();

// Elon-trim: mỗi dữ kiện xuất hiện đúng 1 lần.
// Header = mã duy nhất (ưu tiên mã biến thể KH; mã nội bộ vào tooltip).
const headCode = computed(() => {
	if (!props.item) return '';
	return props.item.customer_code
		|| (Array.isArray(props.item.customer_items) && props.item.customer_items.length
			? (props.item.customer_items[0].ref_code || props.item.customer_items[0].customer_name || '')
			: '')
		|| props.item.custom_alias
		|| props.item.item_code
		|| '';
});

// Drawer 4 dòng đúng thứ tự Sếp chốt (logic SSOT trong useItemSpec).
const detailLines = computed(() => detailLinesOf(props.item));

// P4b: BaseDrawer native <dialog> lo Esc/focus/inert
</script>

<style scoped>
.spec-lines {
	display: flex;
	flex-direction: column;
	gap: 4px;
	margin-top: 6px;
}

.spec-line {
	display: flex;
	gap: 8px;
	align-items: baseline;
	font-size: 14px;
}

.spec-k {
	min-width: 72px;
	color: var(--ink-faint);
	font-size: 12.5px;
}

.spec-v {
	font-weight: 600;
}

.bom-cockpit-block {
	background: var(--surface);
	border: 1px solid rgba(255, 255, 255, 0.08);
	border-radius: 8px;
	overflow: hidden;
}

.bom-cockpit-head {
	padding: 8px 12px;
	background: var(--surface-low);
	border-bottom: 1px solid var(--outline);
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.bom-title {
	font-size: 13.5px;
}

.bom-table-wrap {
	overflow-x: auto;
}

.bom-table {
	width: 100%;
	border-collapse: collapse;
}

.bom-table th {
	background: rgba(0, 0, 0, 0.2);
	color: var(--ink-faint);
	font-weight: 600;
	font-size: 12.5px;
	padding: 7px 10px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.05);
	text-align: left;
}

.bom-table td {
	padding: 7px 10px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.bom-row:hover td {
	background: rgba(255, 255, 255, 0.02);
}

.text-num { font-variant-numeric: tabular-nums; }
.truncate {
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}
.text-right { text-align: right; }
.bom-table th.text-right,
.bom-table td.text-right {
	text-align: right;
}
</style>
