import { ref } from 'vue';

/**
 * Industrial Toast Notification Composable (Singleton)
 * Minimalist, high-density feedback without blocking operations.
 */
const toasts = ref([]);
let nextId = 1;

export function useToast() {
	function show(message, type = 'info', duration = 2800) {
		const id = nextId++;
		const toast = {
			id,
			message,
			type, // 'success' | 'error' | 'warning' | 'info'
		};

		// Limit max 2 toasts on screen simultaneously to avoid clutter
		if (toasts.value.length >= 2) {
			toasts.value.shift();
		}

		toasts.value.push(toast);

		if (duration > 0) {
			setTimeout(() => {
				dismiss(id);
			}, duration);
		}
		return id;
	}

	function dismiss(id) {
		const idx = toasts.value.findIndex((t) => t.id === id);
		if (idx !== -1) {
			toasts.value.splice(idx, 1);
		}
	}

	return {
		toasts,
		show,
		dismiss,
		success: (msg, dur) => show(msg, 'success', dur),
		error: (msg, dur) => show(msg, 'error', dur || 3500),
		warning: (msg, dur) => show(msg, 'warning', dur),
		info: (msg, dur) => show(msg, 'info', dur),
	};
}

export const toast = {
	show: (msg, type, dur) => useToast().show(msg, type, dur),
	success: (msg, dur) => useToast().success(msg, dur),
	error: (msg, dur) => useToast().error(msg, dur),
	warning: (msg, dur) => useToast().warning(msg, dur),
	info: (msg, dur) => useToast().info(msg, dur),
};
