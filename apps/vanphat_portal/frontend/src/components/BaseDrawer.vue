<template>
	<Teleport to="body">
		<dialog
			ref="dlg"
			class="vp-drawer"
			:aria-label="label"
			@close="onNativeClose"
			@cancel="onNativeCancel"
			@click="onBackdropClick"
		>
			<slot />
		</dialog>
	</Teleport>
</template>

<script setup>
/**
 * P4 BaseDrawer: slide-over phải bọc native <dialog> (Sếp duyệt, thay aside + useDrawerDialog).
 * Native cho miễn phí: top-layer (thoát z-index/transform cha), nền inert, Esc đóng modal,
 * focus vào focusable đầu/autofocus. Pattern: watcher guard dlg.open (tránh InvalidStateError),
 * sync sự kiện native close/cancel (kẻo Esc lệch state), backdrop-click e.target === dlg.
 * Nguồn: MDN <dialog>/showModal/top-layer + Vue Teleport.
 */
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue';

const props = defineProps({
	open: { type: Boolean, default: false },
	label: { type: String, default: 'Chi tiết' },
	closeOnBackdrop: { type: Boolean, default: true },
});
const emit = defineEmits(['close', 'update:open']);

const dlg = ref(null);
let triggerEl = null;

function sync(open) {
	const el = dlg.value;
	if (!el) return;
	if (open) {
		if (!el.open) {
			triggerEl = document.activeElement;
			el.showModal();
		}
	} else {
		if (el.open) el.close();
	}
}

function onNativeClose() {
	emit('update:open', false);
	emit('close');
	if (triggerEl && document.contains(triggerEl)) {
		triggerEl.focus({ preventScroll: true });
		triggerEl = null;
	}
}

function onNativeCancel() {
	// Esc: để browser đóng modal, sync state qua sự kiện close
}

function onBackdropClick(e) {
	if (props.closeOnBackdrop && e.target === dlg.value) {
		dlg.value.close();
	}
}

watch(() => props.open, (v) => sync(v));

onMounted(async () => {
	await nextTick();
	sync(props.open);
});
onUnmounted(() => {
	if (dlg.value?.open) dlg.value.close();
});

defineExpose({ dialog: dlg });
</script>

<style scoped>
.vp-drawer {
	margin: 0 0 0 auto;
	padding: 0;
	border: none;
	height: 100dvh;
	max-height: none;
	width: min(680px, 100vw);
	background: #0b0f19;
	color: #fff;
}
.vp-drawer::backdrop {
	background: rgb(0 0 0 / 0.65);
	backdrop-filter: blur(2px);
}
@media (max-width: 768px) {
	.vp-drawer {
		width: 100vw;
		height: 100dvh;
		max-height: none;
	}
}
@media (prefers-reduced-motion: reduce) {
	.vp-drawer {
		transition: none;
	}
}
</style>
