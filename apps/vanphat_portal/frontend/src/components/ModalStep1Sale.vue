<template>
	<BaseModal :open="open" label="Tạo báo giá" @close="$emit('close')">
		<div class="modal-card">
			<!-- Header with title & close button -->
			<div class="modal-header">
				<h3 class="modal-title">Tạo báo giá</h3>
				<button
					type="button"
					class="btn-icon"
					title="Đóng (Esc)"
					@click="$emit('close')"
				>
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<line x1="18" y1="6" x2="6" y2="18"></line>
						<line x1="6" y1="6" x2="18" y2="18"></line>
					</svg>
				</button>
			</div>

			<div class="modal-body">
				<Step1OptionClusters
					:form="form"
					:product-types="productTypes"
					:print-techs="printTechs"
					:accessories="accessories"
					:cylinder-statuses="cylinderStatuses"
					:is-roll="isRoll"
					:is-no-print="isNoPrint"
					@select-type="setProductType"
					@select-accessory="form.accessory = $event"
					@select-print="form.print_type = $event"
					@select-cylinder="form.cylinder_status = $event"
				/>

				<Step1CustomerDims
					:form="form"
					:customer-results="customerResults"
					:length-placeholder="lengthPlaceholder"
					:bottom-placeholder="bottomPlaceholder"
					:is-three-side="isThreeSide"
					@customer-input="onCustomerSearch"
					@customer-focus="onCustomerInput"
					@customer-blur="hideCustomerResults"
					@select-customer="selectCustomer"
					@field-input="onFieldInput"
				/>

				<!-- CỤM 6: NÚT HÀNH ĐỘNG -->
				<div class="act-btn-row">
					<button
						type="button"
						class="act-btn btn-sec"
						@click="$emit('close')"
					>
						Hủy
					</button>
					<button
						type="button"
						class="act-btn btn-pri"
						:disabled="!canContinue"
						:title="canContinue ? '' : 'Chọn đủ loại túi, phụ kiện, kiểu in (và trục nếu in)'"
						@click="onContinue"
					>
						Tiếp tục ➔
					</button>
				</div>
			</div>
		</div>
	</BaseModal>
</template>

<script setup>
import BaseModal from './BaseModal.vue';
import Step1OptionClusters from './quote/Step1OptionClusters.vue';
import Step1CustomerDims from './quote/Step1CustomerDims.vue';
import { useStep1SaleForm } from '../composables/useStep1SaleForm';
import { QUOTE_MATCH_DEFAULTS } from '../composables/useQuoteTypeMatch';

const props = defineProps({
	initialData: {
		type: Object,
		default: () => ({}),
	},
	open: { type: Boolean, default: true },
	// S2 + Task 4: options config-native từ QuotesView
	// (get_product_groups/get_print_config). Trống → ẩn khối truthful.
	productTypes: { type: Array, default: () => [] },
	printTechs: { type: Array, default: () => [] },
	accessories: { type: Array, default: () => [] },
	// Chuẩn nhận diện loại dùng matcher chung Step 1 + Step 2
	// (useQuoteTypeMatch): cuộn = label bắt đầu "Cuộn/Roll" (không token 'kg'
	// mù — 'Túi 25kg' không thành cuộn); không-in / 3-biên match chuỗi con.
	// Desk đổi label giữ từ khóa đầu là 2 step hiểu giống nhau.
	rollMatch: { type: Array, default: () => [...QUOTE_MATCH_DEFAULTS.rollKeys] },
	noPrintMatch: { type: Array, default: () => [...QUOTE_MATCH_DEFAULTS.noPrintKeys] },
	noBottomMatch: { type: Array, default: () => [...QUOTE_MATCH_DEFAULTS.noBottomKeys] },
	sealedAccessory: { type: String, default: 'Hàn kín' },
	// Cặp trạng thái trục là nghiệp vụ cố định (có/chưa), để prop để test
	// và reuse — không phải option Desk như 3 cụm trên.
	cylinderStatuses: { type: Array, default: () => ['Đã có trục', 'Chưa có trục'] },
});

const emit = defineEmits(['close', 'submit', 'update:open']);

// Task 5: parent chỉ composition + render; form state trong composable.
const {
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
} = useStep1SaleForm(props, emit);

// Bridge one-way cho child Step1CustomerDims (form là reactive của composable).
function onCustomerSearch(value) {
	form.customer = value;
	onCustomerInput();
}

function onFieldInput(field, value) {
	form[field] = value;
}
</script>

<style scoped>
.modal-card {
	width: 440px;
	max-width: 100%;
	max-height: 92vh;
	display: flex;
	flex-direction: column;
	background: var(--surface);
	border: 1px solid var(--outline);
	border-radius: 16px;
	box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
	overflow: hidden;
}

.modal-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20px 24px 14px;
}

.modal-title {
	font-size: 18px;
	font-weight: 800;
	color: var(--ink);
	letter-spacing: -0.01em;
	margin: 0;
}

.modal-body {
	padding: 0 24px 24px;
	overflow-y: auto;
	flex: 1;
}

.act-btn-row {
	display: flex;
	gap: 8px;
	width: 100%;
	margin-top: 4px;
}

.act-btn {
	height: 54px;
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: center;
	font-family: inherit;
	font-size: 15.5px;
	font-weight: 700;
	border-radius: 10px;
	cursor: pointer;
	border: 1px solid var(--outline);
	transition: all 0.15s ease;
	box-sizing: border-box;
}

.btn-sec {
	background: var(--surface-low);
	border: 1px solid var(--outline);
	color: var(--ink-secondary);
}

.btn-sec:hover {
	color: var(--ink);
	border-color: rgba(255, 255, 255, 0.25);
	background: rgba(255, 255, 255, 0.05);
}

.btn-pri {
	background: var(--primary);
	border: 1px solid var(--primary);
	color: var(--ink-bright);
	box-shadow: 0 4px 14px rgba(78, 161, 224, 0.25);
}

.btn-pri:hover {
	background: var(--primary-press);
	border-color: var(--primary-press);
}

.btn-pri:disabled {
	opacity: 0.4;
	cursor: not-allowed;
}
</style>
