<template>
	<!-- KHỐI 1: THÔNG TIN KHÁCH & PHÂN LOẠI -->
	<div class="form-section">
		<div class="info-row-1">
			<!-- Chọn khách hàng: ô Tìm-và-Chọn (danh sách động > 8 — triple rule 3) -->
			<div class="field-col customer-pick-wrap">
				<label class="field-label" for="order-customer-search">Khách hàng</label>
				<input
					id="order-customer-search"
					type="text"
					:model-value="customerSearch"
					class="text-input"
					placeholder="Gõ tên / mã KH để chọn"
					autocomplete="off"
					@input="$emit('customer-search-input', $event.target.value)"
					@focus="$emit('customer-search-focus')"
					@blur="$emit('customer-search-blur')"
				/>
				<ul v-if="customerResults.length" class="cust-results">
					<li v-for="c in customerResults" :key="c.id" @mousedown.prevent="$emit('select-customer', c)">
						<span>{{ c.alias }}</span>
						<span class="cust-code">{{ c.name }}</span>
					</li>
				</ul>
			</div>

			<!-- Brand / Thương hiệu -->
			<div class="field-col">
				<label class="field-label" for="order-brand">Brand / Nhãn hiệu</label>
				<input
					id="order-brand"
					name="brand"
					type="text"
					:model-value="brand"
					class="text-input"
					placeholder="VD: BABA, 888, FUSIMI"
					required
					@input="$emit('update:brand', $event.target.value)"
				/>
			</div>

			<!-- Nhóm sản phẩm: nút click-chọn từ Item Group native (triple rule 2+3) -->
			<div class="field-col">
				<span id="pg-label" class="field-label">Nhóm sản phẩm</span>
				<div class="choice-grid" role="radiogroup" aria-labelledby="pg-label">
					<button
						v-for="g in productGroups"
						:key="g.key"
						type="button"
						class="choice-btn"
						:class="{ on: productGroupKey === g.key }"
						role="radio"
						:aria-checked="productGroupKey === g.key"
						@click="$emit('select-product-group', g.key)"
					>
						<span class="choice-label">{{ g.label }}</span>
						<span class="choice-desc">{{ g.desc }}</span>
					</button>
				</div>
			</div>
		</div>

		<div class="info-row-2">
			<!-- Ngày hẹn giao -->
			<div class="field-col">
				<label class="field-label" for="order-delivery-date">Ngày hẹn giao</label>
				<input
					id="order-delivery-date"
					name="deliveryDate"
					type="date"
					:model-value="deliveryDate"
					class="text-input font-mono"
					required
					@input="$emit('update:deliveryDate', $event.target.value)"
				/>
			</div>

			<!-- Hình thức thanh toán: nút click-chọn từ Payment Terms native -->
			<div class="field-col">
				<span id="pay-label" class="field-label">Hình thức thanh toán</span>
				<div class="choice-grid choice-grid-2" role="radiogroup" aria-labelledby="pay-label">
					<button
						v-for="opt in paymentOptions"
						:key="opt.key"
						type="button"
						class="choice-btn"
						:class="{ on: paymentKey === opt.key }"
						role="radio"
						:aria-checked="paymentKey === opt.key"
						@click="$emit('select-payment', opt.key)"
					>
						<span class="choice-label">{{ opt.label }}</span>
						<span class="choice-desc">{{ opt.desc }}</span>
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
// Tách từ ModalCreateOrder.vue — presentational, options từ Item Group /
// Payment Terms native (triple rule 2), visual chỉ render nút click-chọn.
defineProps({
	customerSearch: { type: String, default: '' },
	customerResults: { type: Array, default: () => [] },
	brand: { type: String, default: '' },
	productGroups: { type: Array, default: () => [] },
	productGroupKey: { type: String, default: '' },
	deliveryDate: { type: String, default: '' },
	paymentOptions: { type: Array, default: () => [] },
	paymentKey: { type: String, default: '' },
});

defineEmits([
	'customer-search-input',
	'customer-search-focus',
	'customer-search-blur',
	'select-customer',
	'update:brand',
	'select-product-group',
	'update:deliveryDate',
	'select-payment',
]);
</script>

<style scoped>
/* Sections */
.form-section {
	background: var(--surface-card);
	border: 1px solid rgba(255, 255, 255, 0.06);
	border-radius: 8px;
	padding: 16px;
}

.info-row-1 {
	display: grid;
	grid-template-columns: 2fr 1.2fr 1.6fr;
	gap: 14px;
	margin-bottom: 12px;
}

.info-row-2 {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 14px;
}

.field-col {
	display: flex;
	flex-direction: column;
	gap: 6px;
}

.field-label {
	font-size: 13px;
	font-weight: 600;
	color: var(--ink-faint);
}

/* Triple rule 3: ô Tìm-và-Chọn KH + nút click-chọn options native */
.customer-pick-wrap {
	position: relative;
}
.cust-results {
	position: absolute;
	z-index: 20;
	left: 0;
	right: 0;
	margin: 4px 0 0;
	padding: 0;
	list-style: none;
	background: var(--surface-low);
	border: 1px solid var(--outline);
	border-radius: 8px;
	overflow: hidden;
	max-height: 240px;
	overflow-y: auto;
}
.cust-results li {
	display: flex;
	justify-content: space-between;
	gap: 8px;
	padding: 8px 12px;
	cursor: pointer;
	font-size: 14px;
	color: var(--ink);
}
.cust-results li:hover {
	background: rgba(78, 161, 224, 0.15);
}
.cust-code {
	opacity: 0.6;
	font-size: 12px;
}

/* Triple rule 3: nút click-chọn cho options native */
.choice-grid {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 8px;
}
.choice-grid-2 {
	grid-template-columns: 1fr 1fr;
}
.choice-btn {
	display: flex;
	flex-direction: column;
	align-items: flex-start;
	gap: 2px;
	min-height: 54px;
	padding: 8px 12px;
	background: var(--surface-low);
	border: 1px solid rgba(255, 255, 255, 0.08);
	border-radius: 10px;
	cursor: pointer;
	text-align: left;
	transition: all 0.15s ease;
}
.choice-btn:hover {
	border-color: rgba(255, 255, 255, 0.2);
}
.choice-btn.on {
	background: rgba(78, 161, 224, 0.15);
	border-color: var(--primary);
}
.choice-label {
	font-size: 14px;
	font-weight: 700;
	color: var(--ink);
}
.choice-desc {
	font-size: 12px;
	font-weight: 500;
	color: var(--ink-secondary);
}
.choice-btn.on .choice-desc {
	color: var(--primary);
}

.text-input {
	height: 38px;
	background: var(--surface);
	border: 1px solid var(--outline);
	border-radius: 6px;
	color: var(--ink-bright);
	padding: 0 12px;
	font-size: 14px;
	font-family: inherit;
	outline: none;
	transition: border-color 0.15s ease;
}

.text-input:focus {
	border-color: var(--primary);
	box-shadow: 0 0 0 1px var(--primary);
}

.font-mono {
	font-family: inherit;
	font-variant-numeric: tabular-nums;
	font-feature-settings: "tnum";
}
</style>
