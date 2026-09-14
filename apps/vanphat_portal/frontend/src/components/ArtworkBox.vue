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
			:title="imageUrl ? 'Click xem chi tiết ảnh' : 'Click để tải ảnh mẫu'"
			@click="onBoxClick"
		>
			<img
				v-if="imageUrl"
				:src="imageUrl"
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
			v-if="imageUrl"
			type="button"
			class="artwork-change-btn"
			@click.stop="triggerFileInput"
		>
			Đổi ảnh khác
		</button>

		<!-- Lightbox Modal -->
		<div v-if="showLightbox" class="lightbox-overlay" @click.self="showLightbox = false">
			<div class="lightbox-modal">
				<div class="lightbox-head">
					<span class="lightbox-title">File thiết kế (Maquette)</span>
					<button
						type="button"
						class="btn-icon"
						title="Đóng (Esc)"
						@click="showLightbox = false"
					>
						<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<line x1="18" y1="6" x2="6" y2="18"></line>
							<line x1="6" y1="6" x2="18" y2="18"></line>
						</svg>
					</button>
				</div>
				<div class="lightbox-body">
					<img :src="imageUrl" alt="Maquette chi tiết" class="lightbox-full-img" />
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref } from 'vue';

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
		const res = await fetch('/api/method/upload_file', {
			method: 'POST',
			headers: {
				'X-Frappe-CSRF-Token': window.vp_csrf_token || window.frappe_csrf_token || '',
			},
			body: form,
		});
		const json = await res.json();
		if (json && json.message && json.message.file_url) {
			imageUrl.value = json.message.file_url;
			emit('update:modelValue', json.message.file_url);
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
	border: 1px dashed #4ea1e0;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	background: #1a1f27;
	cursor: pointer;
	position: relative;
	overflow: hidden;
	transition: border-color 0.2s;
}

.artwork-box:hover {
	border-color: #38bdf8;
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
	color: #9ca3af;
	text-align: center;
	padding: 8px;
}

.artwork-add-text {
	font-size: 11px;
	font-weight: 600;
	color: #4ea1e0;
}

.artwork-sub-text {
	font-size: 10px;
	color: #9ca3af;
}

.artwork-change-btn {
	background: transparent;
	border: none;
	margin-top: 4px;
	font-size: 11px;
	color: #4ea1e0;
	cursor: pointer;
	font-weight: 600;
	text-align: center;
	padding: 2px 0;
}

.artwork-change-btn:hover {
	text-decoration: underline;
}

/* Lightbox Modal */
.lightbox-overlay {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.75);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
	padding: 24px;
}

.lightbox-modal {
	background: #161b22;
	border: 1px solid #3a424e;
	border-radius: 12px;
	max-width: 90vw;
	max-height: 90vh;
	display: flex;
	flex-direction: column;
	overflow: hidden;
}

.lightbox-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 12px 16px;
	border-bottom: 1px solid #3a424e;
}

.lightbox-title {
	font-size: 14px;
	font-weight: 700;
	color: #eef1f6;
}

.btn-icon {
	background: transparent;
	border: none;
	color: #9da7b5;
	cursor: pointer;
	padding: 4px;
	border-radius: 6px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.btn-icon:hover {
	color: #eef1f6;
	background: rgba(255, 255, 255, 0.05);
}

.lightbox-body {
	padding: 16px;
	overflow: auto;
	display: flex;
	align-items: center;
	justify-content: center;
}

.lightbox-full-img {
	max-width: 100%;
	max-height: 75vh;
	object-fit: contain;
	border-radius: 6px;
}
</style>
