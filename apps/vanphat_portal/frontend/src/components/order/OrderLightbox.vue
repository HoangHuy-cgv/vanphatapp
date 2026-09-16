<template>
	<!-- Lightbox Modal phóng to Maquette -->
	<div v-if="safeArtwork(url)" class="lightbox-overlay" @click="$emit('close')">
		<div class="lightbox-content" @click.stop>
			<div class="lightbox-head">
				<span class="lightbox-title">{{ title }}</span>
				<button type="button" class="btn-icon" title="Đóng (Esc)" @click="$emit('close')">
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<line x1="18" y1="6" x2="6" y2="18"></line>
						<line x1="6" y1="6" x2="18" y2="18"></line>
					</svg>
				</button>
			</div>
			<img :src="url" alt="Maquette Preview" class="lightbox-img" />
		</div>
	</div>
</template>

<script setup>
import { isSafeArtworkUrl as safeArtwork } from '../../composables/useSafeUrl';

// Tách từ DrawerOrderDetail.vue — lightbox artwork allowlist (S7).
defineProps({
	url: { type: [String, null], default: null },
	title: { type: String, default: '' },
});

defineEmits(['close']);
</script>

<style scoped>
/* Lightbox Modal */
.lightbox-overlay {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.85);
	z-index: 1100;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 24px;
}

.lightbox-content {
	background: var(--surface);
	border: 1px solid var(--outline);
	border-radius: 8px;
	overflow: hidden;
	max-width: 80vw;
	max-height: 80vh;
	display: flex;
	flex-direction: column;
}

.lightbox-head {
	padding: 10px 16px;
	display: flex;
	justify-content: space-between;
	align-items: center;
	border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.lightbox-title {
	font-size: 14px;
	font-weight: 700;
	color: var(--ink-bright);
}

.lightbox-img {
	max-width: 100%;
	max-height: 70vh;
	object-fit: contain;
}
</style>
