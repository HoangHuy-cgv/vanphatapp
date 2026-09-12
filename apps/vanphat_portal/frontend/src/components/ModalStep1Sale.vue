<template>
	<div class="modal-overlay" @click.self="$emit('close')">
		<div class="modal-card" role="dialog" aria-label="Tạo báo giá">
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
				<!-- CỤM 1: 5 DÁNG SẢN PHẨM -->
				<div class="cluster">
					<div class="switch-row">
						<button
							type="button"
							class="switch-btn switch-btn-50"
							:class="{ on: form.product_type === 'Túi đáy đứng' }"
							@click="setProductType('Túi đáy đứng')"
						>
							Túi đáy đứng
						</button>
						<button
							type="button"
							class="switch-btn switch-btn-50"
							:class="{ on: form.product_type === 'Cuộn màng ghép' }"
							@click="setProductType('Cuộn màng ghép')"
						>
							Cuộn màng ghép
						</button>
					</div>
					<div class="switch-row" style="margin-top: 8px;">
						<button
							type="button"
							class="switch-btn switch-btn-33"
							:class="{ on: form.product_type === 'Túi 3 biên' }"
							@click="setProductType('Túi 3 biên')"
						>
							Túi 3 biên
						</button>
						<button
							type="button"
							class="switch-btn switch-btn-33"
							:class="{ on: form.product_type === 'Túi xếp hông' }"
							@click="setProductType('Túi xếp hông')"
						>
							Túi xếp hông
						</button>
						<button
							type="button"
							class="switch-btn switch-btn-33"
							:class="{ on: form.product_type === 'Túi 8 cạnh' }"
							@click="setProductType('Túi 8 cạnh')"
						>
							Túi 8 cạnh
						</button>
					</div>
				</div>

				<!-- CỤM 2: PHỤ KIỆN (3 nút cố định) -->
				<div class="cluster">
					<div class="switch-row">
						<button
							type="button"
							class="switch-btn switch-btn-33"
							:class="{
								on: form.accessory === 'Có vòi' && !isRoll,
								'is-blocked': isRoll
							}"
							:disabled="isRoll"
							@click="form.accessory = 'Có vòi'"
						>
							Có vòi
						</button>
						<button
							type="button"
							class="switch-btn switch-btn-33"
							:class="{
								on: form.accessory === 'Zipper' && !isRoll,
								'is-blocked': isRoll
							}"
							:disabled="isRoll"
							@click="form.accessory = 'Zipper'"
						>
							Zipper
						</button>
						<button
							type="button"
							class="switch-btn switch-btn-33"
							:class="{
								on: form.accessory === 'Hàn kín' && !isRoll,
								'is-blocked': isRoll
							}"
							:disabled="isRoll"
							@click="form.accessory = 'Hàn kín'"
						>
							Hàn kín
						</button>
					</div>
				</div>

				<!-- CỤM 3: IN ẤN & TRỤC IN -->
				<div class="cluster" style="margin-bottom: 18px;">
					<div class="switch-row">
						<button
							type="button"
							class="switch-btn switch-btn-33"
							:class="{ on: form.print_type === 'In trục' }"
							@click="form.print_type = 'In trục'"
						>
							In trục
						</button>
						<button
							type="button"
							class="switch-btn switch-btn-33"
							:class="{ on: form.print_type === 'In offset' }"
							@click="form.print_type = 'In offset'"
						>
							In offset
						</button>
						<button
							type="button"
							class="switch-btn switch-btn-33"
							:class="{ on: form.print_type === 'Không in' }"
							@click="form.print_type = 'Không in'"
						>
							Không in
						</button>
					</div>
					<div class="switch-row" style="margin-top: 8px;">
						<button
							type="button"
							class="switch-btn switch-btn-50"
							:class="{
								on: form.cylinder_status === 'Đã có trục' && !isNoPrint,
								'is-blocked': isNoPrint
							}"
							:disabled="isNoPrint"
							@click="form.cylinder_status = 'Đã có trục'"
						>
							Đã có trục
						</button>
						<button
							type="button"
							class="switch-btn switch-btn-50"
							:class="{
								on: form.cylinder_status === 'Chưa có trục' && !isNoPrint,
								'is-blocked': isNoPrint
							}"
							:disabled="isNoPrint"
							@click="form.cylinder_status = 'Chưa có trục'"
						>
							Chưa có trục
						</button>
					</div>
				</div>

				<!-- ĐƯỜNG PHÂN CÁCH THỊ GIÁC -->
				<div class="wizard-sep"></div>

				<!-- CỤM 4: KHÁCH HÀNG & THƯƠNG HIỆU -->
				<div class="cust-brand-row">
					<div class="field-cust-wrap" style="position:relative;">
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="cust-search-icon">
							<circle cx="11" cy="11" r="8"></circle>
							<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
						</svg>
						<input
							v-model="form.customer"
							type="text"
							class="form-input cust-input"
							placeholder="Tìm khách hàng có sẵn"
							autocomplete="off"
							@input="onCustomerInput"
							@focus="onCustomerInput"
							@blur="hideCustomerResults"
						/>
						<ul v-if="customerResults.length" class="cust-results" style="position:absolute;z-index:20;left:0;right:0;margin:4px 0 0;padding:0;list-style:none;background:var(--surface-low,#1a1f27);border:1px solid var(--outline,#3a424e);border-radius:8px;overflow:hidden;">
							<li v-for="c in customerResults" :key="c.name" @mousedown.prevent="selectCustomer(c)" style="display:flex;justify-content:space-between;gap:8px;padding:8px 12px;cursor:pointer;">
								<span>{{ c.customer_name || c.name }}</span>
								<span v-if="c.customer_name" style="opacity:.6;">{{ c.name }}</span>
							</li>
						</ul>
					</div>
					<div class="field-brand-wrap">
						<input
							v-model="form.brand"
							type="text"
							class="form-input brand-input"
							placeholder="Brand name"
							autocomplete="off"
						/>
					</div>
				</div>

				<!-- CỤM 5: MÔ TẢ SẢN PHẨM & KÍCH THƯỚC KỸ THUẬT -->
				<div class="spec-input-group">
					<input
						v-model="form.description"
						type="text"
						class="form-input desc-input"
						placeholder="Mô tả sản phẩm (VD: Túi nước giặt đậm đặc 3.2L)"
						autocomplete="off"
					/>
					<div class="dims-grid">
						<input
							v-model.number="form.length"
							type="number"
							class="form-input no-spin text-center"
							:placeholder="lengthPlaceholder"
						/>
						<input
							v-model.number="form.width"
							type="number"
							class="form-input no-spin text-center"
							placeholder="Rộng (mm)"
						/>
						<input
							v-model.number="form.thickness"
							type="number"
							class="form-input no-spin text-center"
							placeholder="Dày (mic)"
						/>
						<input
							v-model.number="form.bottom"
							type="number"
							class="form-input no-spin text-center"
							:class="{ 'is-blocked': isThreeSide }"
							:placeholder="bottomPlaceholder"
							:disabled="isThreeSide"
						/>
					</div>
				</div>

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
						@click="onContinue"
					>
						Tiếp tục ➔
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { reactive, computed, ref } from 'vue';

const props = defineProps({
	initialData: {
		type: Object,
		default: () => ({}),
	},
});

const emit = defineEmits(['close', 'next']);

const form = reactive({
	product_type: props.initialData.product_type || 'Túi đáy đứng',
	accessory: props.initialData.accessory || 'Có vòi',
	print_type: props.initialData.print_type || 'In trục',
	cylinder_status: props.initialData.cylinder_status || 'Đã có trục',
	customer: props.initialData.customer || '',
	customer_id: props.initialData.customer_id || '',
	brand: props.initialData.brand || '',
	description: props.initialData.description || '',
	length: props.initialData.length ?? '',
	width: props.initialData.width ?? '',
	thickness: props.initialData.thickness ?? '',
	bottom: props.initialData.bottom ?? '',
});

const isRoll = computed(() => form.product_type === 'Cuộn màng ghép');
const isNoPrint = computed(() => form.print_type === 'Không in');
const isThreeSide = computed(() => form.product_type === 'Túi 3 biên');

const lengthPlaceholder = computed(() => (isRoll.value ? 'Khổ (mm)' : 'Dài (mm)'));

const bottomPlaceholder = computed(() => {
	if (isThreeSide.value) return '—';
	if (form.product_type === 'Túi xếp hông') return 'Hông (mm)';
	if (form.product_type === 'Túi 8 cạnh') return 'Đáy/Hông (mm)';
	return 'Đáy (mm)';
});

function setProductType(type) {
	form.product_type = type;
	if (type === 'Cuộn màng ghép') {
		form.accessory = 'Hàn kín';
	}
	if (type === 'Túi 3 biên') {
		form.bottom = '';
	}
}
const customerResults = ref([]);
let customerSearchTimer = null;

async function searchCustomers(q) {
	try {
		const res = await fetch('/api/method/vanphat_portal.api.bao_gia.search_customers', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-Frappe-CSRF-Token': window.frappe_csrf_token || '',
			},
			body: JSON.stringify({ query: q }),
		});
		const json = await res.json();
		customerResults.value = Array.isArray(json.message) ? json.message : [];
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

function onContinue() {
	emit('next', { ...form });
}
</script>

<style scoped>
.modal-overlay {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.65);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 100;
	padding: 16px;
}

.modal-card {
	width: 440px;
	max-width: 100%;
	max-height: 92vh;
	display: flex;
	flex-direction: column;
	background: #161b22;
	border: 1px solid #3a424e;
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
	color: #eef1f6;
	letter-spacing: -0.01em;
	margin: 0;
}

.btn-icon {
	background: transparent;
	border: none;
	color: #9da7b5;
	cursor: pointer;
	padding: 4px;
	border-radius: 6px;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: color 0.15s;
}

.btn-icon:hover {
	color: #eef1f6;
}

.modal-body {
	padding: 0 24px 24px;
	overflow-y: auto;
	flex: 1;
}

.cluster {
	margin-bottom: 16px;
}

.switch-row {
	display: flex;
	gap: 8px;
	width: 100%;
}

.switch-btn {
	height: 54px;
	font-family: inherit;
	font-size: 14.5px;
	font-weight: 600;
	color: #9da7b5;
	background: #1a1f27;
	border: 1px solid rgba(255, 255, 255, 0.08);
	border-radius: 10px;
	cursor: pointer;
	padding: 0 8px;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.15s ease;
	white-space: nowrap;
}

.switch-btn:hover:not(.is-blocked) {
	color: #eef1f6;
	border-color: rgba(255, 255, 255, 0.2);
}

.switch-btn.on {
	background: #4ea1e0;
	border-color: #4ea1e0;
	color: #ffffff;
	font-weight: 700;
}

.switch-btn.is-blocked {
	opacity: 0.35;
	cursor: not-allowed;
	pointer-events: none;
}

.switch-btn-50 {
	flex: 1;
}

.switch-btn-33 {
	flex: 1;
}

.wizard-sep {
	height: 1px;
	background: rgba(255, 255, 255, 0.08);
	margin: 0 0 16px;
}

.cust-brand-row {
	margin-bottom: 12px;
	display: flex;
	gap: 8px;
	width: 100%;
}

.field-cust-wrap {
	position: relative;
	flex: 1;
}

.cust-search-icon {
	position: absolute;
	left: 12px;
	top: 50%;
	transform: translateY(-50%);
	color: #9da7b5;
	pointer-events: none;
}

.form-input {
	width: 100%;
	height: 44px;
	padding: 0 12px;
	background: #1a1f27;
	border: 1px solid #3a424e;
	border-radius: 10px;
	font-family: inherit;
	font-size: 14.5px;
	font-weight: 500;
	color: #eef1f6;
	outline: none;
	box-sizing: border-box;
	transition: border-color 0.15s, box-shadow 0.15s;
}

.form-input:focus {
	border-color: #4ea1e0;
	box-shadow: 0 0 0 2px rgba(78, 161, 224, 0.2);
}

.form-input::placeholder {
	color: #64748b;
	font-size: 13.5px;
}

.cust-input {
	padding-left: 34px;
}

.field-brand-wrap {
	width: 120px;
	flex-shrink: 0;
}

.spec-input-group {
	margin-bottom: 18px;
	display: flex;
	flex-direction: column;
	gap: 8px;
	width: 100%;
}

.desc-input {
	font-weight: 600;
}

.dims-grid {
	display: grid;
	grid-template-columns: repeat(4, 1fr);
	gap: 8px;
	width: 100%;
	box-sizing: border-box;
}

.text-center {
	text-align: center;
	font-weight: 700;
	padding: 0 6px;
}

.form-input.is-blocked {
	opacity: 0.35;
	cursor: not-allowed;
	pointer-events: none;
}

.no-spin::-webkit-inner-spin-button,
.no-spin::-webkit-outer-spin-button {
	-webkit-appearance: none;
	margin: 0;
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
	border: 1px solid #3a424e;
	transition: all 0.15s ease;
	box-sizing: border-box;
}

.btn-sec {
	background: #1a1f27;
	border: 1px solid #3a424e;
	color: #9da7b5;
}

.btn-sec:hover {
	color: #eef1f6;
	border-color: rgba(255, 255, 255, 0.25);
	background: rgba(255, 255, 255, 0.05);
}

.btn-pri {
	background: #4ea1e0;
	border: 1px solid #4ea1e0;
	color: #ffffff;
	box-shadow: 0 4px 14px rgba(78, 161, 224, 0.25);
}

.btn-pri:hover {
	background: #3b8ac4;
	border-color: #3b8ac4;
}
</style>
