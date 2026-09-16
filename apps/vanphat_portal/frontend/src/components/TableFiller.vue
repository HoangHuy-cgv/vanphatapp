<template>
	<tr
		v-for="i in fillerCount"
		:key="`${prefix}-filler-` + i"
		class="filler-row"
		aria-hidden="true"
	>
		<td :colspan="colspan">&nbsp;</td>
	</tr>
</template>

<script setup>
import { computed } from 'vue';

/**
 * Hàng trống lấp đầy bảng cho đều chiều cao (visual-only, không logic).
 * Dùng chung 3 views Orders/Quotes/Catalog thay copy-paste v-for filler.
 */
const props = defineProps({
	shown: { type: Number, default: 0 },
	pageSize: { type: Number, default: 0 },
	colspan: { type: [Number, String], default: 5 },
	prefix: { type: String, default: 'row' },
});

const fillerCount = computed(() => (
	props.shown > 0 ? Math.max(0, props.pageSize - props.shown) : 0
));
</script>
