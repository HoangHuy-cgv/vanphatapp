<template>
	<div class="vp-hero">
		<div class="vp-hero-title" :title="titleAttr || undefined">
			{{ title }}
		</div>
		<div v-if="sub" class="vp-hero-sub" :class="subClass">
			{{ sub }}
		</div>
		<slot />
	</div>
</template>

<script setup>
/* Hero tên + tên đầy đủ dùng chung 4 Drawer (CSS trong DetailShell). */
defineProps({
	title: { type: String, default: '' },
	sub: { type: String, default: '' },
	subClass: { type: String, default: '' },
	titleAttr: { type: String, default: '' },
});
</script>
