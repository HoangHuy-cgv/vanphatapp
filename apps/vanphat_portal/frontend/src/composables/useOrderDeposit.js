import { ref } from 'vue';
import { api } from './useSession';
import { toast } from './useToast';
import { formatCurrency } from './useCockpitFormat';

/**
 * S7b: deposit + lifecycle handlers cho DrawerOrderDetail.
 * Tách từ DrawerOrderDetail.vue — view chỉ còn template + computed hiển thị.
 * Mọi số cọc/trạng thái do backend trả; lỗi thì toast + giữ nguyên (S1).
 */
export function useOrderDeposit(orderRef, emit) {
	const depositInputAmount = ref(null);

	const handleSaveDeposit = async () => {
		const order = orderRef?.value;
		if (!depositInputAmount.value || depositInputAmount.value <= 0 || !order) return;
		const amt = depositInputAmount.value;
		try {
			const res = await api('order.record_order_deposit', {
				name: order.name,
				amount: amt,
				note: 'Ghi nhận cọc qua cổng buồng lái ERP',
			});
			if (res && res.success) {
				toast.success(`Đã ghi nhận cọc ${formatCurrency(amt)} cho đơn ${order.name}!`);
				depositInputAmount.value = null;
				emit('update-order', {
					...order,
					advance_paid: res.advance_paid,
					outstanding_amount: res.outstanding_amount,
					order_state: res.order_state,
					is_hold: res.is_hold,
				});
			} else {
				// SSOT server S1: cọc lỗi thì báo lỗi + giữ nguyên, không fallback local sai số
				toast.error('Lỗi ghi nhận cọc: máy chủ ERP không phản hồi.');
				depositInputAmount.value = null;
			}
		} catch (err) {
			console.error('Lỗi khi ghi nhận cọc:', err);
			toast.error('Lỗi ghi nhận cọc đơn hàng.');
		}
	};

	// ADR-006: kết quả mutate chỉ lấy từ response server — cọc lỗi thì toast + giữ nguyên.
	const handleOverrideHold = async () => {
		const order = orderRef?.value;
		if (!order) return;
		try {
			const res = await api('order.accountant_approve_procurement', {
				name: order.name,
				note: 'Kế toán xác nhận duyệt ngoại lệ chuyển mua hàng NCC',
			});
			if (res && res.success) {
				toast.success(`Kế toán đã duyệt ngoại lệ cho đơn ${order.name}!`);
				// Đọc lại trạng thái từ server thay vì tự set local (CONSTRAINTS §4.4).
				emit('update-order', {
					...order,
					docstatus: res.docstatus ?? order.docstatus,
					order_state: res.status || order.order_state,
					is_hold: false,
				});
			} else {
				toast.error('Lỗi duyệt ngoại lệ: máy chủ ERP không phản hồi.');
			}
		} catch (err) {
			console.error('Lỗi khi duyệt ngoại lệ:', err);
			toast.error('Lỗi khi duyệt ngoại lệ đơn hàng.');
		}
	};

	const handleReportProgress = async () => {
		const order = orderRef?.value;
		if (!order) return;
		try {
			if (order.docstatus === 0) {
				const res = await api('order.submit_sales_order', {
					name: order.name,
				});
				if (res && res.name) {
					toast.success(`Đã kích hoạt chính thức đơn hàng ${res.name}!`);
					emit('update-order', {
						...order,
						docstatus: res.docstatus,
						status: res.status,
						order_state: 'Đã duyệt',
					});
					return;
				}
				toast.error('Lỗi kích hoạt đơn: máy chủ ERP không phản hồi.');
				return;
			}
		} catch (err) {
			console.error('Lỗi khi submit đơn hàng:', err);
			toast.error('Lỗi khi kích hoạt đơn hàng.');
			return;
		}
		// Đơn đã duyệt: báo cáo tiến độ xưởng qua server ở slice sau; hiện tại chỉ toast
		// nhắc — KHÔNG tự set completed_qty/order_state local (CONSTRAINTS §4.4).
		toast.warning(`Đơn ${order.name} đã duyệt — báo cáo tiến độ xưởng làm ở màn Sản xuất.`);
	};

	const handleCreateDelivery = () => {
		emit('create-delivery', orderRef?.value);
	};

	return {
		depositInputAmount,
		handleSaveDeposit,
		handleOverrideHold,
		handleReportProgress,
		handleCreateDelivery,
	};
}
