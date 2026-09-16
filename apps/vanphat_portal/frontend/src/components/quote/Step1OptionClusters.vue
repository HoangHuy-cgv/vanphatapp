<template>
	<!-- CỤM 1+2+3: options config-native (v-for props).
		P1 review: config rỗng → empty-state truthful hướng về Desk (không kẹt im lặng). -->
	<div>
		<div v-if="!productTypes.length && !accessories.length && !printTechs.length" class="cfg-empty">
			Chưa cấu hình loại túi / in ấn ở Desk (Item Group + Custom Field) — liên hệ quản trị.
		</div>
		<div v-if="productTypes.length" class="cluster">
			<div class="switch-row">
				<button
					v-for="t in productTypes"
					:key="t"
					type="button"
					class="switch-btn"
					:class="{ on: form.product_type === t }"
					@click="$emit('select-type', t)"
				>
					{{ t }}
				</button>
			</div>
		</div>

		<div v-if="accessories.length" class="cluster">
			<div class="switch-row">
				<button
					v-for="a in accessories"
					:key="a"
					type="button"
					class="switch-btn"
					:class="{
						on: form.accessory === a && !isRoll,
						'is-blocked': isRoll
					}"
					:disabled="isRoll"
					@click="$emit('select-accessory', a)"
				>
					{{ a }}
				</button>
			</div>
		</div>

		<div v-if="printTechs.length" class="cluster" style="margin-bottom: 18px;">
			<div class="switch-row">
				<button
					v-for="p in printTechs"
					:key="p"
					type="button"
					class="switch-btn"
					:class="{ on: form.print_type === p }"
					@click="$emit('select-print', p)"
				>
					{{ p }}
				</button>
			</div>
			<div class="switch-row" style="margin-top: 8px;">
				<button
					v-for="s in cylinderStatuses"
					:key="s"
					type="button"
					class="switch-btn"
					:class="{
						on: form.cylinder_status === s && !isNoPrint,
						'is-blocked': isNoPrint
					}"
					:disabled="isNoPrint"
					@click="$emit('select-cylinder', s)"
				>
					{{ s }}
				</button>
			</div>
		</div>
	</div>
</template>

<script setup>
// Tách từ ModalStep1Sale.vue (Task 5) — presentational, mọi chọn emit lên parent.
defineProps({
	form: { type: Object, required: true },
	productTypes: { type: Array, default: () => [] },
	printTechs: { type: Array, default: () => [] },
	accessories: { type: Array, default: () => [] },
	cylinderStatuses: { type: Array, default: () => [] },
	isRoll: { type: Boolean, default: false },
	isNoPrint: { type: Boolean, default: false },
});

defineEmits(['select-type', 'select-accessory', 'select-print', 'select-cylinder']);
</script>

<style scoped>
.cluster { margin-bottom: 14px; }
.cfg-empty {
	font-size: 13px;
	color: var(--amber-bright);
	background: rgba(251, 191, 36, 0.08);
	border: 1px dashed rgba(251, 191, 36, 0.4);
	border-radius: 8px;
	padding: 10px 12px;
	margin-bottom: 14px;
}
.switch-row {
	display: flex;
	flex-wrap: wrap;
	gap: 8px;
}
.switch-btn {
	flex: 1 1 auto;
	font-size: 13px;
	font-weight: 600;
	padding: 9px 12px;
	border-radius: 8px;
	border: 1px solid rgba(255, 255, 255, 0.15);
	background: transparent;
	color: var(--ink-strong);
	cursor: pointer;
	white-space: nowrap;
}
.switch-btn.on {
	border-color: var(--accent-indigo);
	background: rgba(31, 111, 235, 0.15);
	color: var(--primary);
}
.switch-btn.is-blocked { opacity: 0.35; }
.switch-btn:disabled { cursor: not-allowed; }
</style>
