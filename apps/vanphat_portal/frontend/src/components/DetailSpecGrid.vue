<template>
	<div class="vp-spec-grid">
		<div v-for="(cell, idx) in cells" :key="idx" class="vp-spec-cell">
			<span class="vp-cell-label">{{ cell.label }}</span>
			<span class="vp-cell-val" :class="cell.cls">{{ cell.value }}</span>
		</div>
	</div>
</template>

<script setup>
/* Lưới 2 cột nhãn + giá trị dùng chung 4 Drawer (CSS trong DetailShell).
 * cells: [{ label, value, cls }] — Drawer tự chốt chuỗi hiển thị. */
defineProps({
	cells: { type: Array, default: () => [] },
});
</script>
