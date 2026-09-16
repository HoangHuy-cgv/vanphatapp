/**
 * S7b: formatters buồng lái dùng chung (chuẩn AGENTS.md §3 Pillar 4).
 * Chuẩn duy nhất: `Intl.NumberFormat('vi-VN')`, số right tabular-nums ở template.
 * Thay 11 bản copy-paste trong views/components (Quotes/Orders/Catalog,
 * ModalCreateOrder, DrawerOrderDetail/ItemDetail/Step2Director/CustomerDetail).
 */
export function formatCurrency(val) {
	if (val == null || val === '') return '0 đ';
	if (typeof val === 'string' && isNaN(Number(val))) return val;
	return new Intl.NumberFormat('vi-VN').format(Math.round(Number(val))) + ' đ';
}

export function formatNumber(val) {
	if (val == null || val === '') return '0';
	if (typeof val === 'string' && isNaN(Number(val))) return val;
	return new Intl.NumberFormat('vi-VN').format(Number(val));
}

export function useCockpitFormat() {
	return {
		formatCurrency,
		formatNumber,
		orderStatusText,
		orderStatusColorClass,
		quoteStatusLabel,
		quoteStatusColorClass,
		depositColorClass,
		formatDateShort,
		supplierSlaColorClass,
		supplierSlaText,
	};
}

/**
 * S8a/b: status/color helpers dùng chung Orders/Quotes (rút từ views >500L).
 * Label server (order_status_label/class) là SSOT; fallback client thu gọn.
 */
export function orderStatusText(o) {
	if (o.order_status_label) return o.order_status_label;
	if (o.docstatus === 1) return 'Đã duyệt';
	return 'Chờ cọc';
}

export function orderStatusColorClass(o) {
	if (o.order_status_class) {
		if (o.order_status_class.includes('hold')) return 'text-rose';
		if (o.order_status_class.includes('ordered')) return 'text-emerald';
		if (o.order_status_class.includes('draft')) return 'text-amber';
	}
	if (o.docstatus === 1) return 'text-emerald';
	return 'text-amber';
}

export function quoteStatusLabel(status) {
	switch (status) {
		case 'Open':
		case 'Partially Ordered':
			return 'Chờ duyệt';
		case 'Ordered':
			return 'Đã lên đơn';
		case 'Lost':
			return 'Rớt';
		case 'Expired':
			return 'Hết hạn';
		default:
			return 'Nháp';
	}
}

export function quoteStatusColorClass(status) {
	switch (status) {
		case 'Open':
		case 'Partially Ordered':
			return 'text-amber';
		case 'Ordered':
			return 'text-emerald';
		case 'Lost':
		case 'Expired':
			return 'text-rose';
		default:
			return 'text-secondary';
	}
}

export function depositColorClass(o) {
	const req = Number(o.required_deposit) || 0;
	if (!req) return 'text-secondary';
	if (o.advance_paid >= req) return 'text-emerald';
	if (o.advance_paid > 0) return 'text-amber';
	return 'text-secondary';
}

export function formatDateShort(val) {
	if (!val) return '—';
	const parts = String(val).split('-');
	if (parts.length === 3) {
		return `${parts[2]}/${parts[1]}`;
	}
	return val;
}

// Task 7: SLA NCC dùng chung (rút từ OrdersView) — thuần hiển thị.
export function supplierSlaColorClass(days) {
	if (days == null) return 'text-secondary';
	if (days < 0) return 'text-rose';
	if (days === 0) return 'text-amber';
	return 'text-emerald';
}

export function supplierSlaText(days) {
	if (days == null) return '—';
	if (days < 0) return `Trễ ${Math.abs(days)} ngày`;
	if (days === 0) return 'Hôm nay';
	return `Còn ${days} ngày`;
}
