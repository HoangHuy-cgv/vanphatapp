import { ref } from 'vue';

// ADR-007: Confirm/Prompt thay `frappe-ui/dialog` bằng native <dialog> (ConfirmDialog.vue).
// Contract: callback-based (KHÔNG phải Promise) — giữ nguyên shape `dialog.confirm/prompt`
// của frappe-ui để không sửa callers (QuotesView chỉ đổi import path).
// Caller: dialog.confirm({ title, message, confirmLabel, cancelLabel, onConfirm }).

const dialogState = ref({
	open: false,
	title: '',
	message: '',
	confirmLabel: 'Xác nhận',
	cancelLabel: 'Hủy',
	type: 'confirm', // 'confirm' | 'prompt'
	inputValue: '',
	inputPlaceholder: '',
	inputId: 'confirm-prompt-input',
	onConfirm: null,
	onCancel: null,
});

export function useConfirmDialog() {
	function confirm({ title = 'Xác nhận', message = '', confirmLabel = 'Xác nhận', cancelLabel = 'Hủy', onConfirm = null }) {
		dialogState.value = {
			open: true,
			title,
			message,
			confirmLabel,
			cancelLabel,
			type: 'confirm',
			inputValue: '',
			inputPlaceholder: '',
			inputId: 'confirm-prompt-input',
			onConfirm,
			onCancel: null,
		};
	}

	function prompt({ title = 'Nhập thông tin', message = '', fields = [], confirmLabel = 'Đồng ý', cancelLabel = 'Hủy', onConfirm = null }) {
		const placeholder = fields && fields[0] ? (fields[0].label || '') : '';
		dialogState.value = {
			open: true,
			title,
			message,
			confirmLabel,
			cancelLabel,
			type: 'prompt',
			inputValue: '',
			inputPlaceholder: placeholder,
			inputId: 'confirm-prompt-input',
			onConfirm: (val) => {
				if (onConfirm) {
					onConfirm({ reason: val, value: val });
				}
			},
			onCancel: null,
		};
	}

	function close() {
		dialogState.value.open = false;
	}

	function handleConfirm() {
		const cb = dialogState.value.onConfirm;
		const val = dialogState.value.inputValue;
		close();
		if (cb) {
			if (dialogState.value.type === 'prompt') cb(val);
			else cb();
		}
	}

	function handleCancel() {
		close();
	}

	return {
		dialogState,
		confirm,
		prompt,
		close,
		handleConfirm,
		handleCancel,
	};
}

export const dialog = {
	confirm(opts) {
		const { confirm } = useConfirmDialog();
		confirm(opts);
	},
	prompt(opts) {
		const { prompt } = useConfirmDialog();
		prompt(opts);
	},
};
