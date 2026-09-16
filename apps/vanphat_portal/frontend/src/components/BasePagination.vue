<template>
	<nav v-if="totalPages > 1" class="vp-pager" aria-label="Phân trang">
		<button
			type="button"
			class="vp-pager-nav"
			:disabled="page <= 1 || loading"
			title="Trang trước (Phím [)"
			aria-label="Trang trước"
			@click="emit('prev')"
		>
			<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
				<polyline points="15 18 9 12 15 6"></polyline>
			</svg>
		</button>
		<template v-for="(p, i) in pages" :key="i">
			<span v-if="p === '…'" class="vp-pager-gap" aria-hidden="true">…</span>
			<button
				v-else
				type="button"
				class="vp-pager-num"
				:class="{ active: p === page }"
				:aria-current="p === page ? 'page' : undefined"
				:aria-label="`Trang ${p}`"
				:disabled="loading"
				@click="emit('goto', p)"
			>
				{{ p }}
			</button>
		</template>
		<button
			type="button"
			class="vp-pager-nav"
			:disabled="page >= totalPages || loading"
			title="Trang sau (Phím ])"
			aria-label="Trang sau"
			@click="emit('next')"
		>
			<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
				<polyline points="9 18 15 12 9 6"></polyline>
			</svg>
		</button>
	</nav>
</template>

<script setup>
/**
 * BasePagination: phân trang tối giản dùng chung (Quotes/Orders/Catalog).
 * Chỉ render + emit (prev/next/goto) — view giữ load data. Ẩn khi 1 trang.
 * Dãy số rút gọn: ≤7 hiện hết, >7 hiện đầu/cuối/current±1 + '…'.
 */
import { computed } from 'vue';

const props = defineProps({
	page: { type: Number, default: 1 },
	totalPages: { type: Number, default: 1 },
	loading: { type: Boolean, default: false },
});
const emit = defineEmits(['prev', 'next', 'goto']);

const pages = computed(() => {
	const total = Math.max(1, props.page);
	const last = Math.max(1, props.totalPages);
	if (last <= 7) {
		return Array.from({ length: last }, (_, i) => i + 1);
	}
	const cur = Math.min(Math.max(1, total), last);
	const set = new Set([1, last, cur - 1, cur, cur + 1]);
	const nums = [...set].filter((n) => n >= 1 && n <= last).sort((a, b) => a - b);
	const out = [];
	let prev = 0;
	for (const n of nums) {
		if (n - prev > 1) out.push('…');
		out.push(n);
		prev = n;
	}
	return out;
});
</script>
