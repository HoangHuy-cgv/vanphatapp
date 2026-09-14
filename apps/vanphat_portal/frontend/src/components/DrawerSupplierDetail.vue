<template>
	<Teleport to="body">
		<div v-if="isOpen" class="drawer-overlay" @click.self="$emit('close')">
		<aside class="drawer-panel" aria-label="Chi tiết nhà cung cấp">
			<!-- Header -->
			<div class="drawer-head">
				<div class="head-left">
					<span class="supp-code-badge font-mono">{{ supplier ? supplier.name : '' }}</span>
					<span v-if="supplier" class="supp-group-badge">
						{{ supplier.supplier_group || 'Nhà Cung Cấp' }}
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
			<div v-if="supplier" class="drawer-body">
				<!-- Hero -->
				<div class="hero-block">
					<div class="hero-title">
						{{ supplier.alias || supplier.supplier_name }}
					</div>
					<div class="hero-sub text-secondary">
						{{ supplier.supplier_name }}
					</div>
				</div>

				<!-- Section: Commercial Terms -->
				<div class="cockpit-card">
					<div class="spec-grid">
						<div class="spec-cell">
							<span class="cell-label">Mã số thuế</span>
							<span class="cell-val font-mono">{{ supplier.tax_id || '—' }}</span>
						</div>
						<div class="spec-cell">
							<span class="cell-label">Điều khoản thanh toán</span>
							<span class="cell-val text-amber">{{ supplier.payment_terms || 'Công nợ gối đầu' }}</span>
						</div>
						<div class="spec-cell">
							<span class="cell-label">Tiền tệ</span>
							<span class="cell-val font-mono">{{ supplier.default_currency || 'VND' }}</span>
						</div>
						<div class="spec-cell">
							<span class="cell-label">Quốc gia</span>
							<span class="cell-val">{{ supplier.country || 'Việt Nam' }}</span>
						</div>
					</div>
				</div>

				<!-- Section: Address & Contact -->
				<div class="cockpit-card">
					<div class="contact-row">
						<div class="contact-icon">
							<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
								<circle cx="12" cy="10" r="3"></circle>
							</svg>
						</div>
						<div class="contact-info">
							<span class="contact-label">Địa chỉ xưởng / Nhà máy</span>
							<span class="contact-val">{{ supplier.primary_address || 'Chưa cập nhật' }}</span>
						</div>
					</div>
					<div v-if="supplier.supplier_primary_contact || supplier.supplier_primary_phone" class="contact-row mt-2">
						<div class="contact-icon">
							<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
							</svg>
						</div>
						<div class="contact-info">
							<span class="contact-label">Liên hệ đặt hàng</span>
							<span class="contact-val">
								<span v-if="supplier.supplier_primary_contact" class="text-primary font-medium">{{ supplier.supplier_primary_contact }}</span>
								<span v-if="supplier.supplier_primary_contact && supplier.supplier_primary_phone"> • </span>
								<span v-if="supplier.supplier_primary_phone" class="font-mono">{{ supplier.supplier_primary_phone }}</span>
							</span>
						</div>
					</div>
				</div>

				<!-- Section: Special Notes / Material Supply -->
				<div v-if="supplier.note" class="cockpit-card">
					<div class="card-head-simple">
						<span>DANH MỤC VẬT TƯ & DỊCH VỤ CUNG CẤP</span>
					</div>
					<p class="note-text text-sm">{{ supplier.note }}</p>
				</div>
			</div>
		</aside>
		</div>
	</Teleport>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';

const props = defineProps({
	isOpen: {
		type: Boolean,
		default: false
	},
	supplier: {
		type: Object,
		default: null
	}
});

const emit = defineEmits(['close']);

function handleKeydown(e) {
	if (e.key === 'Escape' && props.isOpen) {
		emit('close');
	}
}

onMounted(() => {
	window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
	window.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
.drawer-overlay {
	position: fixed;
	inset: 0;
	z-index: 999;
	background: rgba(0, 0, 0, 0.65);
	backdrop-filter: blur(2px);
	display: flex;
	justify-content: flex-end;
}

.drawer-panel {
	width: 520px;
	max-width: 100vw;
	height: 100vh;
	background: #161b22;
	border-left: 1px solid #3a424e;
	box-shadow: -8px 0 32px rgba(0, 0, 0, 0.6);
	display: flex;
	flex-direction: column;
	animation: slideInRight 0.22s ease-out;
	overflow-y: auto;
}

@keyframes slideInRight {
	from {
		transform: translateX(100%);
	}
	to {
		transform: translateX(0);
	}
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

.supp-code-badge {
	padding: 3px 8px;
	border-radius: 4px;
	background: #1a2333;
	color: #38bdf8;
	font-weight: 700;
	font-size: 13.5px;
	border: 1px solid rgba(56, 189, 248, 0.3);
}

.supp-group-badge {
	padding: 2px 8px;
	border-radius: 4px;
	background: rgba(255, 255, 255, 0.06);
	color: #94a3b8;
	font-size: 12px;
	font-weight: 600;
	border: 1px solid rgba(255, 255, 255, 0.1);
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
	color: #64748b;
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
	color: #38bdf8;
	margin-top: 2px;
}

.contact-info {
	display: flex;
	flex-direction: column;
	gap: 2px;
}

.contact-label {
	font-size: 11.5px;
	color: #64748b;
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
	color: #64748b;
	letter-spacing: 0.05em;
	margin-bottom: 8px;
}

.note-text {
	color: #cbd5e1;
	line-height: 1.5;
}

.text-primary {
	color: #38bdf8;
}

.text-secondary {
	color: #94a3b8;
}

.text-amber {
	color: #f59e0b;
}

.font-mono {
	font-family: inherit;
	font-variant-numeric: tabular-nums;
	font-feature-settings: "tnum";
}
</style>
