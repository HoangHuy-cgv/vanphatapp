import { toast as libToast } from 'vue-sonner';

/**
 * ADR-007: Toast qua `vue-sonner` trực tiếp (zero-dep, ~10KB gzip lib + CSS).
 * Giữ nguyên contract success/error/warning/info/message để không sửa callers.
 * Root `App.vue` mount duy nhất 1 `<Toaster theme="dark" position="top-right" rich-colors />`.
 */
function show(message, type = 'info') {
	if (type === 'success') return libToast.success(message);
	if (type === 'error') return libToast.error(message);
	if (type === 'warning') return libToast.warning(message);
	return libToast(message);
}

export function useToast() {
	return {
		show,
		dismiss: (id) => { try { libToast.dismiss(id); } catch (e) { /* noop */ } },
		success: (msg) => show(msg, 'success'),
		error: (msg) => show(msg, 'error'),
		warning: (msg) => show(msg, 'warning'),
		info: (msg) => show(msg, 'info'),
	};
}

export const toast = {
	show: (msg, type) => show(msg, type),
	success: (msg) => show(msg, 'success'),
	error: (msg) => show(msg, 'error'),
	warning: (msg) => show(msg, 'warning'),
	info: (msg) => show(msg, 'info'),
};
