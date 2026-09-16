<template>
	<div class="vp-card">
		<div v-if="title" class="vp-card-head">
			<span>{{ title }}</span>
			<span v-if="count != null" class="vp-mono vp-text-secondary">({{ count }})</span>
		</div>
		<slot />
	</div>
</template>

<script setup>
/* Thẻ cockpit-card dùng chung 4 Drawer (CSS trong DetailShell). */
defineProps({
	title: { type: String, default: '' },
	count: { type: [Number, String], default: null },
});
</script>
