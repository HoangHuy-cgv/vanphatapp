import { toast as libToast } from 'frappe-ui';

/**
 * P4c: Toast qua lib frappe-ui (đã có FrappeUIProvider portals ở App root).
 * Giữ nguyên contract success/error/warning/info/message để không sửa callers.
 * Xóa CockpitToast.vue + singleton ref khi Sếp duyệt (hiện giữ song song 1 round để so sánh).
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
