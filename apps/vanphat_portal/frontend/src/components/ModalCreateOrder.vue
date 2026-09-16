<template>
	<BaseModal :open="open || isOpen" label="Tạo Đơn Hàng Mới" @close="$emit('close')">
		<div class="modal-panel">
			<!-- Header -->
			<div class="modal-head">
				<div class="head-left">
					<h3 id="modal-order-title" class="modal-title">Tạo Đơn Hàng Mới</h3>
					<span class="head-badge">{{ groupTabLabel }}</span>
				</div>
				<button type="button" class="btn-close" title="Đóng (Esc)" @click="$emit('close')">
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<line x1="18" y1="6" x2="6" y2="18"></line>
						<line x1="6" y1="6" x2="18" y2="18"></line>
					</svg>
				</button>
			</div>

			<form @submit.prevent="handleSubmit" class="modal-form">
				<OrderCustomerInfo
					:customer-search="customerSearch"
					:customer-results="customerResults"
					:brand="brand"
					:product-groups="productGroups"
					:product-group-key="productGroupKey"
					:delivery-date="deliveryDate"
					:payment-options="paymentOptions"
					:payment-key="paymentKey"
					@customer-search-input="customerSearch = $event; onCustomerSearchInput()"
					@customer-search-focus="onCustomerSearchInput"
					@customer-search-blur="hideCustomerResults"
					@select-customer="selectCustomerResult"
					@update:brand="brand = $event"
					@select-product-group="selectProductGroup"
					@update:delivery-date="deliveryDate = $event"
					@select-payment="selectPayment"
				/>

				<!-- KHỐI 2: THÍCH ỨNG ĐỘNG THEO QUY TRÌNH -->
				<OrderMtoSection
					v-if="isCustomMto"
					:selected-custom-item-code="selectedCustomItemCode"
					:available-custom-items="availableCustomItems"
					:current-custom-item="currentCustomItem"
					:variant-rows="variantRows"
					:has-new-cylinders="hasNewCylinders"
					:cylinder-count="cylinderCount"
					:cylinder-supplier="cylinderSupplier"
					:cylinder-unit-price="cylinderUnitPrice"
					:server-pricing="serverPricing"
					@custom-item-change="selectedCustomItemCode = $event; onCustomItemChange()"
					@variant-field="setVariantField"
					@add-variant-row="addVariantRow"
					@remove-variant-row="removeVariantRow"
					@update:has-new-cylinders="hasNewCylinders = $event"
					@update:cylinder-count="cylinderCount = $event"
					@update:cylinder-supplier="cylinderSupplier = $event"
					@update:cylinder-unit-price="cylinderUnitPrice = $event"
				/>

				<OrderMtsSection
					v-else
					:product-group="productGroup"
					:screen-print-brand="screenPrintBrand"
					:generic-rows="genericRows"
					:available-generic-items="availableGenericItems"
					@update:screen-print-brand="screenPrintBrand = $event"
					@generic-item-change="setGenericItem"
					@generic-field="setGenericField"
					@add-generic-row="addGenericRow"
					@remove-generic-row="removeGenericRow"
				/>

				<OrderFinanceFooter
					:server-pricing="serverPricing"
					:payment-type="paymentType"
					:is-submitting="isSubmitting"
					:is-calculating-price="isCalculatingPrice"
					@close="$emit('close')"
				/>
			</form>
		</div>
	</BaseModal>
</template>

<script setup>
import { watch, toRef, computed } from 'vue';
import BaseModal from './BaseModal.vue';
import { api } from '../composables/useSession';
import { toast } from '../composables/useToast';
import { useCreateOrderForm } from '../composables/useCreateOrderForm';
import OrderCustomerInfo from './order/OrderCustomerInfo.vue';
import OrderMtoSection from './order/OrderMtoSection.vue';
import OrderMtsSection from './order/OrderMtsSection.vue';
import OrderFinanceFooter from './order/OrderFinanceFooter.vue';

const props = defineProps({
	open: { type: Boolean, default: false },
	isOpen: { type: Boolean, default: false },
	initialTab: { type: String, default: 'xuong_sx' },
	masterItems: { type: Array, default: () => [] },
});

// S7: emit contract khớp caller OrdersView (@order-created) — sửa bug khai báo thiếu
const emit = defineEmits(['close', 'order-created', 'update:isOpen', 'update:open']);

// P4c: Dialog lib điều khiển mở/đóng (v-model:open), sync về isOpen + emit close
const dialogOpen = computed({
	get: () => props.isOpen,
	set: (v) => {
		emit('update:isOpen', v);
		if (!v) emit('close');
	},
});

const form = useCreateOrderForm(toRef(props, 'masterItems'));
const {
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
	onCustomItemChange,
	onGenericItemChange,
	addVariantRow,
	removeVariantRow,
	addGenericRow,
	removeGenericRow,
	resetForOpen,
} = form;

// Cầu nối one-way input → row object (giữ edit cụ thể từng dòng, không v-model
// xuyên component — hàng vẫn là object của useCreateOrderForm).
const setVariantField = (idx, field, value) => {
	const row = variantRows.value[idx];
	if (row && field in row) row[field] = value;
};

const setGenericItem = (idx, itemCode) => {
	const row = genericRows.value[idx];
	if (!row) return;
	row.item_code = itemCode;
	onGenericItemChange(row);
};

const setGenericField = (idx, field, value) => {
	const row = genericRows.value[idx];
	if (row && field in row) row[field] = value;
};

// Default setup when modal opens — options native tải trước rồi mới reset theo tab
watch(
	() => props.isOpen,
	async (val) => {
		if (val) {
			await Promise.all([fetchCustomers(), fetchUiConfig()]);

			// Set default delivery date (+7 days)
			const d = new Date();
			d.setDate(d.getDate() + 7);
			deliveryDate.value = d.toISOString().split('T')[0];

			resetForOpen(props.initialTab);
		}
	},
	{ immediate: true }
);

// Submit order to ERPNext native Sales Order
const handleSubmit = async () => {
	if (!currentCustomer.value || isSubmitting.value) return;
	if (isCalculatingPrice.value) {
		toast.warning('Đang đối soát giá từ ERPNext, vui lòng chờ trong giây lát...');
		return;
	}

	let orderTab = 'xuong_sx';
	const selectedGroup = productGroups.value.find((g) => g.key === productGroupKey.value);
	if (selectedGroup && selectedGroup.order_tab) {
		orderTab = selectedGroup.order_tab;
	} else if (productGroup.value === 'Túi NGCS') orderTab = 'ngcs';
	else if (productGroup.value === 'Túi màng đơn') orderTab = 'mua_ngoai';

	let builtItems = [];
	let mats = [];
	// Triple rule 1: ảnh/despec do Item native quyết (artwork_url); rỗng thì không gửi.
	let artworkUrl = '';

	if (isCustomMto.value && currentCustomItem.value) {
		mats = currentCustomItem.value.materials;
		artworkUrl = currentCustomItem.value.artwork_url;

		variantRows.value.forEach((v) => {
			builtItems.push({
				item_code: currentCustomItem.value.item_code,
				item_name: `${currentCustomItem.value.item_name} - ${v.variant_name}`,
				variant_name: v.variant_name,
				artwork_url: artworkUrl,
				qty: Number(v.qty) || 0,
				uom: currentCustomItem.value.uom,
				rate: Number(v.rate) || 0,
				amount: (Number(v.qty) || 0) * (Number(v.rate) || 0),
				is_cylinder: false,
			});
		});

		// P2 pass-through: dòng trục do backend cộng từ cylinder_spec (giá NCC).
		// Vỏ không tự build dòng trục nữa — chỉ gửi spec, backend quyết.
	} else {
		// Generic MTS — spec/despec theo Item native tìm được, không nhãn cứng.
		genericRows.value.forEach((g) => {
			const itemDef = catalogItems.value.find((i) => i.item_code === g.item_code) || {};
			mats = itemDef.materials || [];

			builtItems.push({
				item_code: g.item_code,
				item_name: `${itemDef.item_name || g.item_code} (${brand.value})`,
				variant_name: itemDef.item_name || g.item_code,
				artwork_url: artworkUrl,
				qty: Number(g.qty) || 0,
				uom: g.uom,
				rate: Number(g.rate) || 0,
				amount: (Number(g.qty) || 0) * (Number(g.rate) || 0),
				is_cylinder: false,
			});
		});
	}

	const orderPayload = {
		customer: currentCustomer.value.id,
		customer_name: currentCustomer.value.name,
		brand: brand.value,
		delivery_date: deliveryDate.value,
		payment_type: paymentType.value,
		order_tab: orderTab,
		product_group: productGroup.value,
		has_new_cylinders: hasNewCylinders.value,
		cylinder_count: cylinderCount.value,
		// P2: giá trục NCC quyết — Vạn Phát chỉ mua đi bán lại, không chốt số nào
		cylinder_spec: hasNewCylinders.value ? {
			qty: cylinderCount.value,
			unit_price: cylinderUnitPrice.value,
			supplier: cylinderSupplier.value,
		} : null,
		items: builtItems,
	};

	isSubmitting.value = true;
	try {
		const res = await api('order.create_sales_order', { payload: orderPayload });
		if (res && res.name) {
			toast.success(`Đã tạo đơn hàng ${res.name} thành công!`);
			emit('order-created', {
				name: res.name,
				order_tab: orderTab,
				...orderPayload,
			});
			emit('close');
		} else {
			toast.error('Không thể tạo đơn hàng trên hệ thống.');
		}
	} catch (err) {
		console.error('Error creating sales order:', err);
		toast.error('Lỗi kết nối khi tạo đơn hàng.');
	} finally {
		isSubmitting.value = false;
	}
};
</script>

<style scoped>
.modal-panel {
	background: var(--surface);
	border: 1px solid var(--outline);
	border-radius: 12px;
	width: 100%;
	max-width: 960px;
	max-height: 90vh;
	display: flex;
	flex-direction: column;
	box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
	overflow: hidden;
}

.modal-head {
	padding: 16px 20px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.08);
	display: flex;
	justify-content: space-between;
	align-items: center;
	background: var(--surface-low);
}

.head-left {
	display: flex;
	align-items: center;
	gap: 12px;
}

.modal-title {
	font-size: 18px;
	font-weight: 700;
	color: var(--ink-bright);
	margin: 0;
}

.head-badge {
	font-size: 11px;
	font-weight: 700;
	text-transform: uppercase;
	padding: 2px 8px;
	border-radius: 4px;
	background: rgba(78, 161, 224, 0.15);
	color: var(--primary);
	border: 1px solid rgba(78, 161, 224, 0.3);
}

.btn-close {
	background: transparent;
	border: none;
	color: var(--ink-faint);
	cursor: pointer;
	padding: 4px;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 6px;
	transition: all 0.15s ease;
}

.btn-close:hover {
	color: var(--ink-bright);
	background: rgba(255, 255, 255, 0.08);
}

.modal-form {
	padding: 20px;
	overflow-y: auto;
	overflow-x: hidden;
	display: flex;
	flex-direction: column;
	gap: 20px;
}
</style>
