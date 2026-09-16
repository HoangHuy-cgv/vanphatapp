<template>
	<div class="artwork-container">
		<input
			ref="fileInput"
			type="file"
			accept="image/*"
			class="hidden-file-input"
			@change="onFileSelected"
		/>
		<div
			class="artwork-box"
			:title="safeImageUrl ? 'Click xem chi tiết ảnh' : 'Click để tải ảnh mẫu'"
			@click="onBoxClick"
		>
			<img
				v-if="safeImageUrl"
				:src="safeImageUrl"
				alt="Ảnh thiết kế"
				class="artwork-img"
			/>
			<div v-else class="artwork-empty">
				<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
					<rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
					<circle cx="8.5" cy="8.5" r="1.5"></circle>
					<polyline points="21 15 16 10 5 21"></polyline>
				</svg>
				<span class="artwork-add-text">+ Tải ảnh mẫu</span>
				<span class="artwork-sub-text">Market / File in</span>
			</div>
		</div>
		<button
			v-if="safeImageUrl"
			type="button"
			class="artwork-change-btn"
			@click.stop="triggerFileInput"
		>
			Đổi ảnh khác
		</button>

		<!-- Lightbox Modal (dùng chung OrderLightbox) -->
		<OrderLightbox
			v-if="showLightbox"
			:url="safeImageUrl"
			title="File thiết kế (Maquette)"
			@close="showLightbox = false"
		/>
	</div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { api } from '../composables/useSession';
import { isSafeArtworkUrl } from '../composables/useSafeUrl';
import OrderLightbox from './order/OrderLightbox.vue';

const props = defineProps({
	modelValue: {
		type: String,
		default: '',
	},
});

const emit = defineEmits(['update:modelValue']);

const fileInput = ref(null);
const imageUrl = ref(props.modelValue);
const showLightbox = ref(false);
// S7: :src chỉ render URL qua allowlist scheme (chặn javascript:/data: lạ).
const safeImageUrl = computed(() => (isSafeArtworkUrl(imageUrl.value) ? imageUrl.value : ''));

function triggerFileInput() {
	if (fileInput.value) {
		fileInput.value.click();
	}
}

function onBoxClick() {
	if (imageUrl.value) {
		showLightbox.value = true;
	} else {
		triggerFileInput();
	}
}

function onFileSelected(e) {
	const file = e.target.files && e.target.files[0];
	if (!file) return;

	// Instant local preview; replaced by the native /files/ URL after upload.
	const reader = new FileReader();
	reader.onload = (evt) => {
		imageUrl.value = evt.target.result;
	};
	reader.readAsDataURL(file);
	uploadArtwork(file);
}

async function uploadArtwork(file) {
	try {
		const form = new FormData();
		form.append('file', file, file.name);
		form.append('is_private', '0');
		// ADR-006: upload đi qua api() — CSRF + toast + signal thống nhất, không fetch lẻ.
		const json = await api('/api/method/upload_file', form, { method: 'POST' });
		if (json && json.file_url) {
			imageUrl.value = json.file_url;
			emit('update:modelValue', json.file_url);
			return;
		}
	} catch (err) {
		// keep local preview; backend ignores non-/files/ URLs on submit
	}
	emit('update:modelValue', imageUrl.value);
}
</script>

<style scoped>
.artwork-container {
	flex: 0 0 135px;
	width: 135px;
	display: flex;
	flex-direction: column;
}

.hidden-file-input {
	display: none;
}

.artwork-box {
	width: 100%;
	height: 100%;
	min-height: 156px;
	border-radius: 10px;
	border: 1px dashed var(--primary);
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	background: var(--surface-low);
	cursor: pointer;
	position: relative;
	overflow: hidden;
	transition: border-color 0.2s;
}

.artwork-box:hover {
	border-color: var(--info);
}

.artwork-img {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.artwork-empty {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 4px;
	color: var(--ink-gray);
	text-align: center;
	padding: 8px;
}

.artwork-add-text {
	font-size: 11px;
	font-weight: 600;
	color: var(--primary);
}

.artwork-sub-text {
	font-size: 10px;
	color: var(--ink-gray);
}

.artwork-change-btn {
	background: transparent;
	border: none;
	margin-top: 4px;
	font-size: 11px;
	color: var(--primary);
	cursor: pointer;
	font-weight: 600;
	text-align: center;
	padding: 2px 0;
}

.artwork-change-btn:hover {
	text-decoration: underline;
}

/* Lightbox Modal — overlay/content/head dùng chung OrderLightbox */
</style>
