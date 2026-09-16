import { ref, computed, watch } from 'vue';
import { api } from './useSession';

/**
 * S7: form state + server pricing cho ModalCreateOrder.
 * Tách từ ModalCreateOrder.vue (1193L) — view chỉ còn template + submit wiring.
 * Mọi tiền/thuế/cọc do backend `order.get_price_preview` trả; client chỉ hiển thị.
 */
/**
 * Giá trị khởi tạo trước khi `order.get_price_preview` trả về.
 * Cố ý KHÔNG hardcode thuế/cọc (ADR-002: VAT doc-driven, cọc theo Payment Terms).
 * Hằng số này bị thiếu từ commit d30fdd6 khiến ModalCreateOrder ném ReferenceError lúc mount.
 */
const serverPricingInitial = {
	net_total: 0,
	vat_rate: 0,
	vat_amount: 0,
	cylinder_count: 0,
	cylinder_rate: 0,
	cylinder_total: 0,
	grand_total: 0,
	required_deposit: 0,
};

export function useCreateOrderForm(masterItemsRef) {
	const customers = ref([]);
	const isSubmitting = ref(false);

	async function fetchCustomers() {
		try {
			// ADR-006: master lists trả envelope page_result — đọc đúng hợp đồng.
			const data = await api('vanphat_portal.api.customer.get_list', {}, { get: true });
			const rows = (data && Array.isArray(data.customers) && data.customers)
				|| (Array.isArray(data) && data) || [];
			if (rows.length > 0) {
				customers.value = rows.map((c) => ({
					id: c.name,
					name: c.customer_name || c.name,
					alias: c.alias || c.customer_name || c.name,
					brand: c.brand || '',
					payment_terms: c.payment_terms || '',
				}));
			}
		} catch (e) {
			customers.value = [];
		}
	}

	const serverPricing = ref({ ...serverPricingInitial });

	// P2 pass-through (Sếp duyệt): giá trục do NCC báo — vỏ chỉ nhập, không chốt số nào.
	const cylinderSupplier = ref('');
	const cylinderUnitPrice = ref(null);

	const catalogItems = computed(() => {
		const masterItems = masterItemsRef?.value ?? [];
		if (masterItems && masterItems.length) {
			return masterItems.map((item) => ({
				item_code: item.item_code,
				item_name: item.item_name,
				custom_alias: item.custom_alias || item.item_name,
				customer_alias: item.customer_alias || item.customer,
				product_group: item.product_group || (
					(item.item_code || '').startsWith('NGCS-') ? 'Túi NGCS' :
					(item.item_code || '').startsWith('TMD-') ? 'Túi màng đơn' :
					(item.item_code || '').startsWith('BTP-') ? 'Cuộn màng ghép' : 'Túi màng ghép'
				),
				product_type: item.product_type || 'Túi đáy đứng',
				dimensions_text: item.dimensions_text || `${item.custom_pouch_width_mm || 0} x ${item.custom_pouch_length_mm || 0} mm`,
				materials: item.materials || (item.custom_structure_layers ? item.custom_structure_layers.split('/') : []),
				accessory: item.accessory || item.custom_accessory_spec || 'Không vòi',
				print_type: item.print_type || item.custom_print_tech || 'In trục',
				cylinder_count: item.cylinder_count || item.custom_cylinder_qty || 0,
				cylinder_rate: null,
				uom: item.stock_uom || item.uom || 'Túi',
				base_rate: item.standard_rate || item.base_rate || 0,
				// Triple rule 2: số lượng tối thiểu từ Item native — UI gợi ý, không hardcode.
				min_order_qty: item.min_order_qty || null,
				artwork_url: item.artwork_url || '',
				is_custom: item.is_custom !== undefined ? item.is_custom : ((item.item_code || '').startsWith('TP-') || !(item.item_code || '').startsWith('NGCS-')),
				default_variants: item.default_variants || [item.custom_alias || item.item_name],
			}));
		}
		return [];
	});

	// Form Fields — triple rule 2: options từ native (Item Group / Payment Terms),
	// visual chỉ render nút click-chọn. productGroup/paymentType giữ để caller cũ
	// (ModalCreateOrder submit) không vỡ — suy từ key native đã chọn.
	// Triple rule 2: qty gợi ý = min_order_qty native của mã đang chọn (hoặc min_qty
	// của nhóm SP); trống khi native không có — không fallback số thương mại.
	function suggestedQty(explicitMinQty) {
		if (explicitMinQty) return explicitMinQty;
		const g = productGroups.value.find((x) => x.key === productGroupKey.value);
		return (g && g.min_qty) || '';
	}
	const selectedCustomerId = ref('');
	const customerSearch = ref('');
	const customerResults = ref([]);
	let customerSearchTimer = null;

	function customerMatches(c, q) {
		const hay = `${c.alias || ''} ${c.name || ''} ${c.id || ''}`.toLowerCase();
		return hay.includes(q);
	}

	function runCustomerSearch() {
		const q = customerSearch.value.trim().toLowerCase();
		if (!q) {
			customerResults.value = customers.value.slice(0, 50);
			return;
		}
		customerResults.value = customers.value.filter((c) => customerMatches(c, q)).slice(0, 50);
	}

	function onCustomerSearchInput() {
		clearTimeout(customerSearchTimer);
		customerSearchTimer = setTimeout(runCustomerSearch, 250);
	}

	function selectCustomerResult(c) {
		selectedCustomerId.value = c.id;
		customerSearch.value = c.alias || c.name;
		customerResults.value = [];
		onCustomerChange();
	}

	function hideCustomerResults() {
		setTimeout(() => { customerResults.value = []; }, 150);
	}
	const brand = ref('');
	const productGroups = ref([]);
	const productGroupKey = ref('');
	const paymentOptions = ref([]);
	const paymentKey = ref('');
	const productGroup = computed(() => {
		const g = productGroups.value.find((x) => x.key === productGroupKey.value);
		return g ? g.label : '';
	});
	const deliveryDate = ref('');
	const paymentType = computed(() => {
		const p = paymentOptions.value.find((x) => x.key === paymentKey.value);
		return p ? p.label : '';
	});

	async function fetchUiConfig() {
		try {
			const pg = await api('item.get_product_groups', {}, { get: true, silent: true });
			if (pg && Array.isArray(pg.product_groups) && pg.product_groups.length) {
				productGroups.value = pg.product_groups;
				if (!productGroupKey.value || !productGroups.value.some((g) => g.key === productGroupKey.value)) {
					productGroupKey.value = productGroups.value[0].key;
				}
			}
		} catch (e) {
			productGroups.value = [];
		}
		try {
			const pay = await api('vanphat_portal.api.customer.get_payment_options', {}, { get: true, silent: true });
			if (pay && Array.isArray(pay.payment_options) && pay.payment_options.length) {
				paymentOptions.value = pay.payment_options;
				if (!paymentKey.value || !paymentOptions.value.some((p) => p.key === paymentKey.value)) {
					paymentKey.value = paymentOptions.value[0].key;
				}
			}
		} catch (e) {
			paymentOptions.value = [];
		}
	}

	function selectProductGroup(key) {
		productGroupKey.value = key;
		onProductGroupChange();
	}

	function selectPayment(key) {
		paymentKey.value = key;
	}

	// MTO state (Màng ghép / Cuộn)
	const selectedCustomItemCode = ref('');
	const variantRows = ref([
		{ variant_name: '', qty: '', rate: 0 },
	]);
	const hasNewCylinders = ref(false);
	const cylinderCount = ref(0);

	// MTS state (NGCS / Màng đơn)
	const screenPrintBrand = ref('');
	const genericRows = ref([
		// ADR-006: qty mặc định là nợ config-native (plan item 13) — để trống để
		// người dùng nhập thật, không fallback số thương mại thay ý họ.
		{ item_code: '', item_name: '', variant_name: '', qty: '', rate: 0, uom: 'Túi' },
	]);

	// Computed logic
	const currentCustomer = computed(() => {
		return customers.value.find((c) => c.id === selectedCustomerId.value) || null;
	});

	const isCustomMto = computed(() => {
		return productGroup.value === 'Túi màng ghép' || productGroup.value === 'Cuộn màng ghép';
	});

	const groupTabLabel = computed(() => {
		if (isCustomMto.value) return 'XƯỞNG SẢN XUẤT (ĐỘC QUYỀN MTO)';
		if (productGroup.value === 'Túi NGCS') return 'TÚI NGCS (IN LỤA PHÔI SẴN)';
		return 'MUA NGOÀI TRỌN GÓI';
	});

	// Filtered custom products for selected customer
	const availableCustomItems = computed(() => {
		if (!currentCustomer.value) return [];
		return catalogItems.value.filter(
			(item) => item.is_custom && item.customer_alias === currentCustomer.value.alias && item.product_group === productGroup.value
		);
	});

	// Currently selected custom item
	const currentCustomItem = computed(() => {
		return catalogItems.value.find((i) => i.item_code === selectedCustomItemCode.value) || null;
	});

	// Available generic items
	const availableGenericItems = computed(() => {
		return catalogItems.value.filter(
			(item) => !item.is_custom && item.product_group === productGroup.value
		);
	});

	const isCalculatingPrice = ref(false);
	let pricePreviewAbortController = null;
	let pricePreviewTimer = null;

	const fetchPricePreview = () => {
		clearTimeout(pricePreviewTimer);
		if (pricePreviewAbortController) {
			pricePreviewAbortController.abort();
		}
		isCalculatingPrice.value = true;

		pricePreviewTimer = setTimeout(async () => {
			pricePreviewAbortController = new AbortController();
			const items = isCustomMto.value
				? variantRows.value.map((v) => ({ qty: Number(v.qty) || 0, rate: Number(v.rate) || 0 }))
				: genericRows.value.map((g) => ({ qty: Number(g.qty) || 0, rate: Number(g.rate) || 0 }));

			try {
				const res = await api(
					'order.get_price_preview',
					{
						customer: currentCustomer.value?.id || '',
						items,
						has_new_cylinders: hasNewCylinders.value,
						cylinder_count: cylinderCount.value,
						// P2: giá NCC nhập tay — trống = pending truthful, không fallback số nào
						cylinder_spec: hasNewCylinders.value ? {
							qty: cylinderCount.value,
							unit_price: cylinderUnitPrice.value,
							supplier: cylinderSupplier.value,
						} : null,
					},
					{
						silent: true,
						signal: pricePreviewAbortController.signal,
					}
				);
				if (res) {
					serverPricing.value = res;
					if (res.payment_type) {
						paymentType.value = res.payment_type;
					}
				}
			} catch (err) {
				// silent fallback / AbortError
			} finally {
				isCalculatingPrice.value = false;
			}
		}, 150);
	};

	watch(
		[variantRows, genericRows, hasNewCylinders, cylinderCount, cylinderSupplier, cylinderUnitPrice, currentCustomer, isCustomMto, productGroup],
		() => {
			fetchPricePreview();
		},
		{ deep: true }
	);

	// Event Handlers
	const onCustomerChange = () => {
		if (!currentCustomer.value) return;
		brand.value = currentCustomer.value.brand || '';
		// Triple rule 2: hình thức thanh toán theo KH — Trả sau khi KH có payment_terms
		// công nợ, còn lại theo option native đầu (không gán label cứng).
		const terms = (currentCustomer.value.payment_terms || '').toLowerCase();
		const payKey = terms.includes('sau') || terms.includes('nợ') || terms.includes('công nợ')
			? 'tra_sau'
			: (paymentOptions.value[0] && paymentOptions.value[0].key) || '';
		if (payKey && paymentOptions.value.some((p) => p.key === payKey)) {
			paymentKey.value = payKey;
		}

		// Reset items
		selectedCustomItemCode.value = '';
		if (availableCustomItems.value.length > 0) {
			selectedCustomItemCode.value = availableCustomItems.value[0].item_code;
			onCustomItemChange();
		}
	};

	const onProductGroupChange = () => {
		if (isCustomMto.value) {
			if (availableCustomItems.value.length > 0) {
				selectedCustomItemCode.value = availableCustomItems.value[0].item_code;
				onCustomItemChange();
			} else {
				selectedCustomItemCode.value = '';
			}
		} else {
			if (availableGenericItems.value.length > 0) {
				const first = availableGenericItems.value[0];
				genericRows.value = [
					{
						item_code: first.item_code,
						item_name: first.item_name,
						variant_name: first.item_name,
						// Triple rule 2: qty gợi ý từ min_order_qty native.
						qty: suggestedQty(first.min_order_qty),
						rate: first.base_rate,
						uom: first.uom,
					},
				];
			}
		}
	};

	const onCustomItemChange = () => {
		if (!currentCustomItem.value) return;
		// Triple rule 2: qty gợi ý từ min_order_qty native của mã đang chọn.
		const defaults = currentCustomItem.value.default_variants || ['Quy cách chuẩn'];
		variantRows.value = defaults.map((name) => ({
			variant_name: name,
			qty: suggestedQty(currentCustomItem.value.min_order_qty),
			rate: currentCustomItem.value.base_rate || 0,
		}));
		cylinderCount.value = currentCustomItem.value.cylinder_count || 0;
	};

	const onGenericItemChange = (row) => {
		const item = catalogItems.value.find((i) => i.item_code === row.item_code);
		if (item) {
			row.item_name = item.item_name;
			row.variant_name = item.item_name;
			row.rate = item.base_rate;
			row.uom = item.uom;
			// Triple rule 2: đổi mã → gợi ý lại qty theo min_order_qty native.
			if (row.qty === '' || row.qty == null) row.qty = suggestedQty(item.min_order_qty);
		}
	};

	const addVariantRow = () => {
		const rate = currentCustomItem.value ? currentCustomItem.value.base_rate : 0;
		variantRows.value.push({
			variant_name: '',
			qty: suggestedQty(currentCustomItem.value && currentCustomItem.value.min_order_qty),
			rate: rate,
		});
	};

	const removeVariantRow = (index) => {
		if (variantRows.value.length > 1) {
			variantRows.value.splice(index, 1);
		}
	};

	const addGenericRow = () => {
		const firstItem = availableGenericItems.value[0] || {};
		genericRows.value.push({
			item_code: firstItem.item_code || '',
			item_name: firstItem.item_name || '',
			variant_name: firstItem.item_name || '',
			// Triple rule 2: qty gợi ý từ min_order_qty native.
			qty: suggestedQty(firstItem.min_order_qty),
			rate: firstItem.base_rate || 0,
			uom: firstItem.uom || 'Túi',
		});
	};

	const removeGenericRow = (index) => {
		if (genericRows.value.length > 1) {
			genericRows.value.splice(index, 1);
		}
	};

	function resetForOpen(initialTab) {
		// Set initial product group according to active tab (key native — triple rule 2).
		const byTab = productGroups.value.find((g) => g.order_tab === initialTab);
		if (byTab) {
			productGroupKey.value = byTab.key;
		} else if (productGroups.value.length) {
			productGroupKey.value = productGroups.value[0].key;
		}
		if (customers.value.length > 0) {
			selectCustomerResult(customers.value[0]);
		} else {
			selectedCustomerId.value = '';
			customerSearch.value = '';
		}
	}

	return {
		customers,
		isSubmitting,
		fetchCustomers,
		fetchUiConfig,
		productGroups,
		productGroupKey,
		paymentOptions,
		paymentKey,
		selectProductGroup,
		selectPayment,
		catalogItems,
		serverPricing,
		isCalculatingPrice,
		fetchPricePreview,
		selectedCustomerId,
		customerSearch,
		customerResults,
		onCustomerSearchInput,
		selectCustomerResult,
		hideCustomerResults,
		brand,
		productGroup,
		deliveryDate,
		paymentType,
		selectedCustomItemCode,
		variantRows,
		hasNewCylinders,
		cylinderCount,
		cylinderSupplier,
		cylinderUnitPrice,
		screenPrintBrand,
		genericRows,
		currentCustomer,
		isCustomMto,
		groupTabLabel,
		availableCustomItems,
		currentCustomItem,
		availableGenericItems,
		onCustomerChange,
		onProductGroupChange,
		onCustomItemChange,
		onGenericItemChange,
		addVariantRow,
		removeVariantRow,
		addGenericRow,
		removeGenericRow,
		resetForOpen,
	};
}
