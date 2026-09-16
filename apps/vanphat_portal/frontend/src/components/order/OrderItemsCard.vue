<template>
	<!-- KHỐI 2: DANH SÁCH MẪU IN / SẢN PHẨM ĐẶT HÀNG (MULTI-SKU) -->
	<div class="items-card">
		<div class="card-head">
			<span class="card-title">MẪU IN / SẢN PHẨM ĐẶT HÀNG ({{ items.length }})</span>
			<span class="total-qty-badge font-mono">Tổng: {{ formatNumber(qty) }} {{ uom }}</span>
		</div>

		<div class="items-list">
			<div
				v-for="(it, idx) in items"
				:key="idx"
				class="item-row"
				:class="{ 'cylinder-row': it.is_cylinder }"
			>
				<!-- Thumbnail ảnh mẫu in -->
				<div class="thumb-box" @click="safeArtwork(it.artwork_url) && $emit('preview', it.artwork_url, it.item_name)">
					<img
						v-if="safeArtwork(it.artwork_url)"
						:src="it.artwork_url"
						:alt="it.item_name"
						class="thumb-img"
					/>
					<div v-else class="thumb-placeholder">
						<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
							<circle cx="8.5" cy="8.5" r="1.5"></circle>
							<polyline points="21 15 16 10 5 21"></polyline>
						</svg>
					</div>
				</div>

				<!-- Thông tin mẫu in -->
				<div class="item-info">
					<div class="item-name">
						{{ it.variant_name || it.item_name }}
					</div>
					<div class="item-sub text-secondary font-mono">
						{{ it.item_code }}
					</div>
				</div>

				<!-- Số lượng & Đơn giá -->
				<div class="item-qty text-right">
					<span class="font-bold text-white text-num">{{ formatNumber(it.qty) }}</span>
					<span class="text-secondary text-sm" style="margin-left: 4px;">{{ it.uom }}</span>
				</div>

				<div class="item-rate text-right font-mono text-secondary text-num">
					{{ formatCurrency(it.rate) }}
				</div>

				<!-- Thành tiền -->
				<div class="item-amount text-right font-bold text-num text-white">
					{{ formatCurrency(it.amount) }}
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { useCockpitFormat } from '../../composables/useCockpitFormat';
import { isSafeArtworkUrl as safeArtwork } from '../../composables/useSafeUrl';

// Tách từ DrawerOrderDetail.vue — presentational, mọi số do server trả.
defineProps({
	items: { type: Array, required: true },
	qty: { type: [Number, String], default: 0 },
	uom: { type: String, default: 'Túi' },
});

defineEmits(['preview']);

const { formatCurrency, formatNumber } = useCockpitFormat();
</script>

<style scoped>
/* KHỐI 2: DANH SÁCH MẪU IN / SẢN PHẨM */
.items-card {
	background: var(--surface);
	border: 1px solid rgba(255, 255, 255, 0.08);
	border-radius: 8px;
	overflow: hidden;
}

.card-head {
	padding: 12px 16px;
	background: var(--surface-low);
	border-bottom: 1px solid rgba(255, 255, 255, 0.06);
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.card-title {
	font-size: 12px;
	font-weight: 700;
	color: var(--ink-faint);
	letter-spacing: 0.5px;
}

.total-qty-badge {
	font-size: 12px;
	font-weight: 700;
	color: var(--primary);
}

.items-list {
	display: flex;
	flex-direction: column;
}

.item-row {
	display: grid;
	grid-template-columns: 48px 1fr 90px 100px 110px;
	gap: 12px;
	align-items: center;
	padding: 10px 16px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.04);
	transition: background 0.15s ease;
}

.item-row:hover {
	background: rgba(255, 255, 255, 0.02);
}

.item-row:last-child {
	border-bottom: none;
}

.cylinder-row {
	background: rgba(192, 132, 252, 0.03);
}

.thumb-box {
	width: 44px;
	height: 44px;
	border-radius: 6px;
	background: var(--surface-head);
	border: 1px solid rgba(255, 255, 255, 0.1);
	overflow: hidden;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
}

.thumb-img {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.thumb-placeholder {
	color: var(--ink-ghost);
}

.item-name {
	font-size: 14px;
	font-weight: 600;
	color: var(--ink-bright);
}

.item-sub {
	font-size: 11px;
}

.item-qty {
	font-size: 14px;
}

.item-rate {
	font-size: 13px;
}

.item-amount {
	font-size: 15px;
}

/* Utilities */
.font-mono {
	font-family: inherit;
	font-variant-numeric: tabular-nums;
	font-feature-settings: "tnum";
}
.text-num {
	font-variant-numeric: tabular-nums;
	font-feature-settings: 'tnum';
}
.text-right {
	text-align: right;
}
.text-secondary {
	color: var(--ink-faint);
}
.text-white {
	color: var(--ink-bright);
}
</style>
