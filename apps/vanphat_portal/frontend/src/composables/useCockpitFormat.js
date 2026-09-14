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
	return { formatCurrency, formatNumber };
}
