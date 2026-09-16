<template>
	<Teleport to="body">
		<dialog
			ref="dlg"
			class="vp-modal"
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
 * ADR-007 BaseModal: modal căn giữa bọc native <dialog> (đồng bộ BaseDrawer.vue).
 * Native cho miễn phí: top-layer (thoát mọi z-index cha), nền inert, Esc đóng modal,
 * focus vào focusable đầu/autofocus, khôi phục focus khi đóng.
 * Pattern: watcher guard dlg.open, sync native close/cancel, backdrop-click e.target === dlg.
 * Nguồn: MDN <dialog>/showModal/top-layer + Vue Teleport.
 */
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue';

const props = defineProps({
	open: { type: Boolean, default: false },
	label: { type: String, default: 'Hộp thoại' },
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
.vp-modal {
	margin: auto;
	padding: 0;
	border: none;
	background: transparent;
	color: var(--ink-bright);
	max-width: 95vw;
	max-height: 94vh;
	overflow: visible;
}
.vp-modal::backdrop {
	background: rgb(0 0 0 / 0.65);
	backdrop-filter: blur(2px);
}
.vp-modal:focus-visible {
	outline: none;
}
</style>
