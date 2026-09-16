<template>
	<div class="vp-contact-row" :class="rowClass">
		<div class="vp-contact-icon" aria-hidden="true">
			<svg v-if="icon === 'user'" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
				<circle cx="12" cy="7" r="4"></circle>
			</svg>
			<svg v-else-if="icon === 'phone'" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
			</svg>
			<svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
				<circle cx="12" cy="10" r="3"></circle>
			</svg>
		</div>
		<div class="vp-contact-info">
			<span class="vp-contact-label">{{ label }}</span>
			<span class="vp-contact-val"><slot /></span>
		</div>
	</div>
</template>

<script setup>
/* Dòng liên hệ (icon + nhãn + giá trị) dùng chung (CSS trong DetailShell). */
defineProps({
	label: { type: String, default: '' },
	icon: { type: String, default: 'pin' },
	rowClass: { type: String, default: '' },
});
</script>
