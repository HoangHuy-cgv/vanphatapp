<template>
	<BaseDrawer :open="isOpen" label="Chi tiết khách hàng" @close="$emit('close')">
		<div class="drawer-panel">
			<!-- Header -->
			<div class="drawer-head">
				<div class="head-left">
					<span class="cust-code-badge font-mono">{{ customer ? customer.name : '' }}</span>
					<span v-if="customer" class="cust-type-badge">
						{{ customer.customer_type === 'Company' ? 'Doanh nghiệp' : 'Cá nhân' }}
					</span>
					<span v-if="customer && customer.payment_terms && customer.payment_terms.toLowerCase().includes('gối đầu')" class="head-credit font-mono text-emerald font-bold">
						Trả sau
					</span>
					<span v-else class="head-credit font-mono text-amber">
						Trả trước
					</span>
				</div>
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

			<!-- Body -->
			<div v-if="customer" class="drawer-body">
				<!-- Hero: Short Name & Full Legal Name -->
				<div class="hero-block">
					<div class="hero-title">
						{{ customer.alias || customer.customer_name }}
					</div>
					<div class="hero-sub text-secondary">
						{{ customer.customer_name }}
					</div>
				</div>

				<!-- Section: Commercial & Credit Specs -->
				<div class="cockpit-card">
					<div class="spec-grid">
						<div class="spec-cell">
							<span class="cell-label">Nhóm khách</span>
							<span class="cell-val text-primary font-medium">{{ customer.customer_group || 'Thương Mại & Phân Phối' }}</span>
						</div>
						<div class="spec-cell">
							<span class="cell-label">Khu vực</span>
							<span class="cell-val">{{ customer.territory || 'Việt Nam' }}</span>
						</div>
						<div class="spec-cell">
							<span class="cell-label">Điều khoản thanh toán</span>
							<span class="cell-val text-amber">{{ customer.payment_terms || 'Cọc trước 50% - Giao hàng 50%' }}</span>
						</div>
						<div class="spec-cell">
							<span class="cell-label">Mã số thuế</span>
							<span class="cell-val font-mono">{{ customer.tax_id || '—' }}</span>
						</div>
					</div>
				</div>

				<!-- Section: Contact & Logistics -->
				<div class="cockpit-card">
					<div class="contact-row">
						<div class="contact-icon">
							<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
								<circle cx="12" cy="10" r="3"></circle>
							</svg>
						</div>
						<div class="contact-info">
							<span class="contact-label">Địa chỉ giao hàng / Trụ sở</span>
							<span class="contact-val">{{ customer.primary_address || 'Chưa cập nhật' }}</span>
						</div>
					</div>
					<div v-if="customer.customer_primary_contact" class="contact-row mt-2">
						<div class="contact-icon">
							<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
								<circle cx="12" cy="7" r="4"></circle>
							</svg>
						</div>
						<div class="contact-info">
							<span class="contact-label">Đại diện giao dịch / Kinh doanh</span>
							<span class="contact-val text-primary font-medium">{{ customer.customer_primary_contact }}</span>
						</div>
					</div>
				</div>

				<!-- Section: Dedicated Pouch Items -->
				<div v-if="dedicatedItems.length" class="cockpit-card">
					<div class="card-head-simple">
						<span>MẶT HÀNG ĐẶT RIÊNG</span>
						<span class="font-mono text-secondary">({{ dedicatedItems.length }})</span>
					</div>
					<div class="dedicated-list">
						<div
							v-for="it in dedicatedItems"
							:key="it.item_code"
							class="dedicated-item"
						>
							<div class="ded-left">
								<span class="font-mono text-primary text-xs">{{ it.item_code }}</span>
								<span class="ded-name font-medium">{{ it.custom_alias || it.item_name }}</span>
							</div>
							<div class="ded-right">
								<span v-if="it.custom_structure_layers" class="layer-pill text-xs font-mono">{{ it.custom_structure_layers }}</span>
								<span v-if="it.standard_rate" class="rate-pill text-emerald font-mono">{{ formatCurrency(it.standard_rate) }} đ</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</BaseDrawer>
</template>

<script setup>
import { computed } from 'vue';
import BaseDrawer from './BaseDrawer.vue';
import { useCockpitFormat } from '../composables/useCockpitFormat';

const props = defineProps({
	isOpen: {
		type: Boolean,
		default: false
	},
	customer: {
		type: Object,
		default: null
	},
	masterItems: {
		type: Array,
		default: () => []
	}
});

const emit = defineEmits(['close']);

// S7c: formatter dùng chung (bản cũ thiếu ' đ' + sai falsy 0 → chuẩn hóa)
const { formatCurrency } = useCockpitFormat();

const dedicatedItems = computed(() => {
	if (!props.customer || !props.masterItems) return [];
	const cAlias = (props.customer.alias || '').trim().toLowerCase();
	const cName = (props.customer.customer_name || '').trim().toLowerCase();
	return props.masterItems.filter(it => {
		const itCust = (it.customer || '').trim().toLowerCase();
		return (cAlias && itCust === cAlias) || (cName && itCust === cName);
	});
});

// P4b: BaseDrawer native <dialog> lo Esc/focus/inert
</script>

<style scoped>
.drawer-panel {
	width: 540px;
	max-width: 100vw;
	height: 100vh;
	background: #161b22;
	border-left: 1px solid #3a424e;
	box-shadow: -8px 0 32px rgba(0, 0, 0, 0.6);
	display: flex;
	flex-direction: column;
	overflow-y: auto;
}

.drawer-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 14px 20px;
	background: #11151c;
	border-bottom: 1px solid #3a424e;
	flex-shrink: 0;
}

.head-left {
	display: flex;
	align-items: center;
	gap: 10px;
}

.cust-code-badge {
	padding: 3px 8px;
	border-radius: 4px;
	background: #1a2333;
	color: #4ea1e0;
	font-weight: 700;
	font-size: 13.5px;
	border: 1px solid rgba(78, 161, 224, 0.3);
}

.cust-type-badge {
	padding: 2px 7px;
	border-radius: 4px;
	background: rgba(255, 255, 255, 0.06);
	color: #94a3b8;
	font-size: 12px;
	font-weight: 600;
	border: 1px solid rgba(255, 255, 255, 0.1);
}

.head-credit {
	font-size: 13px;
}

.btn-icon {
	background: transparent;
	border: none;
	color: #94a3b8;
	cursor: pointer;
	padding: 4px;
	border-radius: 4px;
	display: inline-flex;
	align-items: center;
	justify-content: center;
	transition: color 0.15s;
}

.btn-icon:hover {
	color: #ffffff;
}

.drawer-body {
	padding: 20px;
	display: flex;
	flex-direction: column;
	gap: 14px;
	flex: 1;
}

.hero-block {
	padding-bottom: 12px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.hero-title {
	font-size: 20px;
	font-weight: 700;
	color: #ffffff;
	line-height: 1.3;
}

.hero-sub {
	font-size: 13.5px;
	margin-top: 4px;
	line-height: 1.4;
}

.cockpit-card {
	background: #1a1f27;
	border: 1px solid #3a424e;
	border-radius: 6px;
	padding: 14px 16px;
}

.spec-grid {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 12px;
}

.spec-cell {
	display: flex;
	flex-direction: column;
	gap: 3px;
}

.cell-label {
	font-size: 11.5px;
	text-transform: uppercase;
	color: #9ca3af;
	letter-spacing: 0.04em;
	font-weight: 600;
}

.cell-val {
	font-size: 13.5px;
	color: #e2e8f0;
}

.contact-row {
	display: flex;
	align-items: flex-start;
	gap: 10px;
}

.contact-icon {
	color: #4ea1e0;
	margin-top: 2px;
}

.contact-info {
	display: flex;
	flex-direction: column;
	gap: 2px;
}

.contact-label {
	font-size: 11.5px;
	color: #9ca3af;
	text-transform: uppercase;
	letter-spacing: 0.04em;
	font-weight: 600;
}

.contact-val {
	font-size: 13.5px;
	color: #cbd5e1;
	line-height: 1.4;
}

.card-head-simple {
	font-size: 12px;
	font-weight: 700;
	color: #9ca3af;
	letter-spacing: 0.05em;
	margin-bottom: 10px;
	display: flex;
	gap: 6px;
}

.dedicated-list {
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.dedicated-item {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 8px 10px;
	background: #141820;
	border: 1px solid rgba(255, 255, 255, 0.06);
	border-radius: 4px;
}

.ded-left {
	display: flex;
	align-items: center;
	gap: 8px;
}

.ded-name {
	font-size: 13.5px;
	color: #f1f5f9;
}

.ded-right {
	display: flex;
	align-items: center;
	gap: 8px;
}

.layer-pill {
	padding: 2px 6px;
	border-radius: 3px;
	background: #1e293b;
	color: #94a3b8;
}

.rate-pill {
	font-size: 13px;
	font-weight: 700;
}

.text-primary {
	color: #4ea1e0;
}

.text-secondary {
	color: #94a3b8;
}

.text-amber {
	color: #f59e0b;
}

.text-emerald {
	color: #10b981;
}

.font-mono {
	font-family: inherit;
	font-variant-numeric: tabular-nums;
	font-feature-settings: "tnum";
}

.font-bold {
	font-weight: 700;
}
</style>
