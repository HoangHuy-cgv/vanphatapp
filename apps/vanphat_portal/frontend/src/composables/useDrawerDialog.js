import { onMounted, onUnmounted, ref } from 'vue';

/**
 * S10: drawer dialog semantics dùng chung (ADR-001 + AGENTS.md §3 Pillar 5).
 * - `role=dialog aria-modal` do template khai báo (không gán qua JS).
 * - Esc đóng + click backdrop đóng (backdrop đã có @click.self ở template).
 * - Mở: focus vào panel; đóng: restore focus về nút trigger đã mở.
 */
export function useDrawerDialog(isOpenRef, emit) {
	const panelRef = ref(null);
	let triggerEl = null;

	function focusPanel() {
		const el = panelRef.value;
		if (!el) return;
		if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '-1');
		el.focus({ preventScroll: true });
	}

	function handleKeydown(e) {
		if (e.key === 'Escape') {
			emit('close');
		}
		// Focus trap tối giản: giữ Tab trong panel
		if (e.key === 'Tab' && panelRef.value) {
			const focusables = panelRef.value.querySelectorAll(
				'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
			);
			if (!focusables.length) return;
			const first = focusables[0];
			const last = focusables[focusables.length - 1];
			if (e.shiftKey && document.activeElement === first) {
				e.preventDefault();
				last.focus();
			} else if (!e.shiftKey && document.activeElement === last) {
				e.preventDefault();
				first.focus();
			}
		}
	}

	onMounted(() => {
		triggerEl = document.activeElement;
		window.addEventListener('keydown', handleKeydown);
		focusPanel();
	});

	onUnmounted(() => {
		window.removeEventListener('keydown', handleKeydown);
		if (triggerEl && document.contains(triggerEl)) {
			triggerEl.focus({ preventScroll: true });
		}
	});

	return { panelRef };
}
