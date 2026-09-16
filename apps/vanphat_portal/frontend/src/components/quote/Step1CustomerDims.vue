<template>
	<!-- CỤM 4+5: KH + brand + mô tả + kích thước -->
	<div>
		<div class="wizard-sep"></div>

		<!-- CỤM 4: KHÁCH HÀNG & THƯƠNG HIỆU -->
		<div class="cust-brand-row">
			<div class="field-cust-wrap" style="position:relative;">
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="cust-search-icon">
					<circle cx="11" cy="11" r="8"></circle>
					<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
				</svg>
				<input
					id="step1-customer"
					name="customer"
					:model-value="form.customer"
					type="text"
					class="form-input cust-input"
					placeholder="Tìm khách hàng có sẵn"
					aria-label="Tìm khách hàng có sẵn"
					autocomplete="off"
					@input="$emit('customer-input', $event.target.value)"
					@focus="$emit('customer-focus')"
					@blur="$emit('customer-blur')"
				/>
				<ul v-if="customerResults.length" class="cust-results" style="position:absolute;z-index:20;left:0;right:0;margin:4px 0 0;padding:0;list-style:none;background:var(--surface-low,#1a1f27);border:1px solid var(--outline,#3a424e);border-radius:8px;overflow:hidden;">
					<li v-for="c in customerResults" :key="c.name" @mousedown.prevent="$emit('select-customer', c)" style="display:flex;justify-content:space-between;gap:8px;padding:8px 12px;cursor:pointer;">
						<span>{{ c.customer_name || c.name }}</span>
						<span v-if="c.customer_name" style="opacity:.6;">{{ c.name }}</span>
					</li>
				</ul>
			</div>
			<div class="field-brand-wrap">
				<input
					id="step1-brand"
					name="brand"
					:model-value="form.brand"
					type="text"
					class="form-input brand-input"
					placeholder="Brand name"
					aria-label="Brand name"
					autocomplete="off"
					@input="$emit('field-input', 'brand', $event.target.value)"
				/>
			</div>
		</div>

		<!-- CỤM 5: MÔ TẢ SẢN PHẨM & KÍCH THƯỚC KỸ THUẬT -->
		<div class="spec-input-group">
			<input
				id="step1-desc"
				name="description"
				:model-value="form.description"
				type="text"
				class="form-input desc-input"
				placeholder="Mô tả sản phẩm (VD: Túi nước giặt đậm đặc 3.2L)"
				aria-label="Mô tả sản phẩm"
				autocomplete="off"
				@input="$emit('field-input', 'description', $event.target.value)"
			/>
			<div class="dims-grid">
				<input
					id="step1-length"
					name="length"
					:model-value="form.length"
					type="number"
					class="form-input no-spin text-center"
					:placeholder="lengthPlaceholder"
					:aria-label="lengthPlaceholder"
					@input="$emit('field-input', 'length', numField($event))"
				/>
				<input
					id="step1-width"
					name="width"
					:model-value="form.width"
					type="number"
					class="form-input no-spin text-center"
					placeholder="Rộng (mm)"
					aria-label="Rộng (mm)"
					@input="$emit('field-input', 'width', numField($event))"
				/>
				<input
					id="step1-thick"
					name="thickness"
					:model-value="form.thickness"
					type="number"
					class="form-input no-spin text-center"
					placeholder="Dày (mic)"
					aria-label="Dày (mic)"
					@input="$emit('field-input', 'thickness', numField($event))"
				/>
				<input
					id="step1-bottom"
					name="bottom"
					:model-value="form.bottom"
					type="number"
					class="form-input no-spin text-center"
					:class="{ 'is-blocked': isThreeSide }"
					:placeholder="bottomPlaceholder"
					:aria-label="bottomPlaceholder"
					:disabled="isThreeSide"
					@input="$emit('field-input', 'bottom', numField($event))"
				/>
			</div>
		</div>
	</div>
</template>

<script setup>
// Tách từ ModalStep1Sale.vue (Task 5) — inputs one-way, mọi sửa emit lên parent.
// P1 review: number xóa trắng → '' (không NaN) như v-model.number cũ.
defineProps({
	form: { type: Object, required: true },
	customerResults: { type: Array, default: () => [] },
	lengthPlaceholder: { type: String, default: 'Dài (mm)' },
	bottomPlaceholder: { type: String, default: 'Đáy (mm)' },
	isThreeSide: { type: Boolean, default: false },
});

defineEmits(['customer-input', 'customer-focus', 'customer-blur', 'select-customer', 'field-input']);

function numField(e) {
	const v = e.target.valueAsNumber;
	return Number.isNaN(v) ? '' : v;
}
</script>

<style scoped>
.wizard-sep { border-top: 1px solid rgba(255, 255, 255, 0.08); margin: 4px 0 16px; }
.cust-brand-row { display: flex; gap: 10px; margin-bottom: 12px; }
.field-cust-wrap { flex: 2; position: relative; }
.field-brand-wrap { flex: 1; }
.cust-search-icon {
	position: absolute;
	left: 10px;
	top: 50%;
	transform: translateY(-50%);
	color: var(--ink-faint);
	pointer-events: none;
}
.cust-input { padding-left: 32px; }
.form-input {
	width: 100%;
	background: var(--surface-sunken);
	border: 1px solid rgba(255, 255, 255, 0.12);
	border-radius: 6px;
	color: var(--ink-bright);
	font-size: 13px;
	padding: 8px 10px;
	min-width: 0;
}
.spec-input-group { display: flex; flex-direction: column; gap: 10px; }
.dims-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.text-center { text-align: center; }
.is-blocked { opacity: 0.35; }
.no-spin::-webkit-outer-spin-button, .no-spin::-webkit-inner-spin-button { -webkit-appearance: none; }
.no-spin { -moz-appearance: textfield; appearance: textfield; }
</style>
