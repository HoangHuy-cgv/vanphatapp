import { reactive, computed, ref, onMounted, onUnmounted } from 'vue';
import { api } from './useSession';
import { isRollLabel, isNoPrintLabel, isNoBottomLabel, QUOTE_MATCH_DEFAULTS } from './useQuoteTypeMatch';

/**
 * Task 5: form Step 1 tách khỏi ModalStep1Sale.vue — modal chỉ còn
 * composition + render. Mọi options là props config-native truyền vào.
 * Nhận diện loại dùng matcher chung với Step 2 (useQuoteTypeMatch).
 */
export function useStep1SaleForm(props, emit) {
	const initial = (props && props.initialData) || {};
	const sealedAccessory = (props && props.sealedAccessory) || 'Hàn kín';
	// P1 review: chỉ ép accessory khi list Desk chứa giá trị đó (không submit ngoài list).
	const accessoriesList = (props && props.accessories) || [];
	const form = reactive({
		product_type: initial.product_type || '',
		accessory: initial.accessory || '',
		print_type: initial.print_type || '',
		cylinder_status: initial.cylinder_status || '',
		customer: initial.customer || '',
		customer_id: initial.customer_id || '',
		brand: initial.brand || '',
		description: initial.description || '',
		length: initial.length ?? '',
		width: initial.width ?? '',
		thickness: initial.thickness ?? '',
		bottom: initial.bottom ?? '',
	});

	const isRoll = computed(() => isRollLabel(form.product_type));
	const isNoPrint = computed(() => isNoPrintLabel(form.print_type));
	const isThreeSide = computed(() => isNoBottomLabel(form.product_type));

	const lengthPlaceholder = computed(() => (isRoll.value ? 'Khổ (mm)' : 'Dài (mm)'));

	const bottomPlaceholder = computed(() => {
		if (isThreeSide.value) return '—';
		const t = String(form.product_type || '').toLowerCase();
		if (t.includes('xếp hông') || t.includes('xep hong') || t.includes('gusset') || t.includes('hàn lưng')) return 'Hông (mm)';
		if (t.includes('8 cạnh') || t.includes('8 canh') || t.includes('flat')) return 'Đáy/Hông (mm)';
		return 'Đáy (mm)';
	});

	function setProductType(type) {
		form.product_type = type;
		if (isRollLabel(type) && sealedAccessory && (!accessoriesList.length || accessoriesList.includes(sealedAccessory))) {
			form.accessory = sealedAccessory;
		}
		if (isNoBottomLabel(type)) {
			form.bottom = '';
		}
	}

	const customerResults = ref([]);
	let customerSearchTimer = null;

	async function searchCustomers(q) {
		try {
			// ADR-006: tìm KH đi qua api() — debounce + CSRF + toast thống nhất.
			const data = await api('bao_gia.search_customers', { query: q }, { silent: true });
			customerResults.value = Array.isArray(data) ? data : [];
		} catch (err) {
			customerResults.value = [];
		}
	}

	function onCustomerInput() {
		form.customer_id = '';
		clearTimeout(customerSearchTimer);
		const q = form.customer.trim();
		if (!q) {
			customerResults.value = [];
			return;
		}
		customerSearchTimer = setTimeout(() => searchCustomers(q), 250);
	}

	function selectCustomer(c) {
		form.customer = c.customer_name || c.name;
		form.customer_id = c.name;
		customerResults.value = [];
	}

	function hideCustomerResults() {
		setTimeout(() => { customerResults.value = []; }, 150);
	}

	// Nút Tiếp tục sáng chỉ khi đủ chọn — user biết còn thiếu gì.
	const canContinue = computed(() => {
		if (!form.product_type || !form.accessory || !form.print_type) return false;
		if (!isNoPrint.value && !form.cylinder_status) return false;
		return true;
	});

	function onContinue() {
		if (!canContinue.value) return;
		// ADR-007: 1 contract duy nhất `submit` mang payload form (QuotesView @submit).
		emit('submit', { ...form });
	}

	function handleKeydown(e) {
		if (e.key === 'Escape') {
			emit('close');
		}
	}

	onMounted(() => {
		window.addEventListener('keydown', handleKeydown);
	});

	onUnmounted(() => {
		window.removeEventListener('keydown', handleKeydown);
		clearTimeout(customerSearchTimer);
	});

	return {
		form,
		isRoll,
		isNoPrint,
		isThreeSide,
		lengthPlaceholder,
		bottomPlaceholder,
		setProductType,
		customerResults,
		onCustomerInput,
		selectCustomer,
		hideCustomerResults,
		canContinue,
		onContinue,
	};
}
