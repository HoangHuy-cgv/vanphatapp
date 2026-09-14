import { ref, computed, watch } from 'vue';
import { api } from './useSession';

/**
 * S7: form state + server pricing cho ModalCreateOrder.
 * Tách từ ModalCreateOrder.vue (1193L) — view chỉ còn template + submit wiring.
 * Mọi tiền/thuế/cọc do backend `order.get_price_preview` trả; client chỉ hiển thị.
 */
export function useCreateOrderForm(masterItemsRef) {
	const customers = ref([]);
	const isSubmitting = ref(false);

	async function fetchCustomers() {
		try {
			const data = await api('vanphat_portal.api.customer.get_list', {}, { get: true });
			if (Array.isArray(data) && data.length > 0) {
				customers.value = data.map((c) => ({
					id: c.name,
					name: c.customer_name || c.name,
					alias: c.alias || c.customer_name || c.name,
					brand: c.brand || '',
					payment_type: (c.payment_terms && c.payment_terms.toLowerCase().includes('sau')) ? 'Trả sau' : 'Trả trước',
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
				artwork_url: item.artwork_url || '',
				is_custom: item.is_custom !== undefined ? item.is_custom : ((item.item_code || '').startsWith('TP-') || !(item.item_code || '').startsWith('NGCS-')),
				default_variants: item.default_variants || [item.custom_alias || item.item_name],
			}));
		}
		return [];
	});

	// Form Fields
	const selectedCustomerId = ref('');
	const brand = ref('');
	const productGroup = ref('Túi màng ghép');
	const deliveryDate = ref('');
	const paymentType = ref('Trả trước');

	// MTO state (Màng ghép / Cuộn)
	const selectedCustomItemCode = ref('');
	const variantRows = ref([
		{ variant_name: '', qty: 10000, rate: 0 },
	]);
	const hasNewCylinders = ref(false);
	const cylinderCount = ref(0);

	// MTS state (NGCS / Màng đơn)
	const screenPrintBrand = ref('');
	const genericRows = ref([
		{ item_code: '', item_name: '', variant_name: '', qty: 5000, rate: 0, uom: 'Túi' },
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
		paymentType.value = currentCustomer.value.payment_type || 'Trả trước';

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
				genericRows.value = [
					{
						item_code: availableGenericItems.value[0].item_code,
						item_name: availableGenericItems.value[0].item_name,
						variant_name: availableGenericItems.value[0].item_name,
						qty: productGroup.value === 'Túi màng đơn' ? 100 : 5000,
						rate: availableGenericItems.value[0].base_rate,
						uom: availableGenericItems.value[0].uom,
					},
				];
			}
		}
	};

	const onCustomItemChange = () => {
		if (!currentCustomItem.value) return;
		// Initialize default variants
		const defaults = currentCustomItem.value.default_variants || ['Quy cách chuẩn'];
		variantRows.value = defaults.map((name) => ({
			variant_name: name,
			qty: 10000,
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
		}
	};

	const addVariantRow = () => {
		const rate = currentCustomItem.value ? currentCustomItem.value.base_rate : 0;
		variantRows.value.push({
			variant_name: '',
			qty: 10000,
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
			qty: productGroup.value === 'Túi màng đơn' ? 100 : 5000,
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
		// Set initial product group according to active tab
		if (initialTab === 'ngcs') {
			productGroup.value = 'Túi NGCS';
		} else if (initialTab === 'mua_ngoai') {
			productGroup.value = 'Túi màng đơn';
		} else {
			productGroup.value = 'Túi màng ghép';
		}
		if (customers.value.length > 0) {
			selectedCustomerId.value = customers.value[0].id;
			onCustomerChange();
		}
	}

	return {
		customers,
		isSubmitting,
		fetchCustomers,
		catalogItems,
		serverPricing,
		isCalculatingPrice,
		fetchPricePreview,
		selectedCustomerId,
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
