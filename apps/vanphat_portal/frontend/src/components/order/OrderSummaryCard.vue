<template>
	<!-- KHỐI 1: HEADER ĐỊNH DANH & 5 BADGES PHÂN LOẠI -->
	<div class="summary-card">
		<!-- Tên khách hàng & Brand -->
		<div class="cust-brand-bar">
			<div class="cust-info">
				<span class="cust-name font-bold text-white text-base">{{ order.customer_alias || order.customer_name }}</span>
			</div>
			<div class="brand-tag">
				{{ order.brand || 'VẠN PHÁT' }}
			</div>
		</div>

		<!-- 5 Badges Phân Loại -->
		<div class="axis-badges">
			<span class="axis-badge badge-product">{{ order.product_type || order.product_group || 'Túi màng ghép' }}</span>
			<span class="axis-badge badge-accessory">{{ order.accessory || 'Không vòi' }}</span>
			<span class="axis-badge badge-print">{{ order.print_type || 'In trục' }}</span>
			<span class="axis-badge badge-cylinder">{{ order.cylinder_status || 'Không trục' }}</span>
			<span class="axis-badge badge-tab" :class="tabBadgeClass(order.order_tab)">
				{{ tabBadgeLabel(order.order_tab) }}
			</span>
		</div>

		<!-- Quy cách & CHỈ HIỂN THỊ CÁC CHẤT LIỆU ĐANG DÙNG -->
		<div class="spec-row">
			<div class="spec-dim">
				<span class="dim-text font-mono">{{ order.dimensions_text || order.description }}</span>
			</div>
			<!-- Chỉ render các màng có thực, ẩn 100% màng không dùng -->
			<div v-if="order.materials && order.materials.length" class="mat-chips-active">
				<span
					v-for="mat in order.materials"
					:key="mat"
					class="active-chip"
					:class="getMatChipClass(mat)"
				>
					{{ mat }}
				</span>
			</div>
		</div>
	</div>
</template>

<script setup>
// Tách từ DrawerOrderDetail.vue — presentational, chỉ đọc prop order (server SSOT).
const props = defineProps({
	order: { type: Object, required: true },
});

const tabBadgeLabel = (tab) => {
	if (tab === 'xuong_sx') return 'Xưởng sản xuất';
	if (tab === 'ngcs') return 'Túi NGCS';
	return 'Mua ngoài trọn gói';
};

const tabBadgeClass = (tab) => {
	if (tab === 'xuong_sx') return 'tab-xuong';
	if (tab === 'ngcs') return 'tab-ngcs';
	return 'tab-muangoai';
};

// Material Chip Styling
const getMatChipClass = (mat) => {
	const m = (mat || '').toUpperCase();
	if (m.includes('OPP') || m.includes('PET')) return 'mat-blue';
	if (m.includes('AL') || m.includes('MPET')) return 'mat-amber';
	if (m.includes('PA')) return 'mat-purple';
	return 'mat-emerald'; // PE, CPP, HD
};
</script>

<style scoped>
/* KHỐI 1: TỔNG QUAN KHÁCH & QUY CÁCH */
.summary-card {
	background: var(--surface);
	border: 1px solid rgba(255, 255, 255, 0.08);
	border-radius: 8px;
	padding: 16px;
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.cust-brand-bar {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.cust-info {
	display: flex;
	align-items: center;
	gap: 8px;
}

.cust-name {
	font-size: 17px;
	font-weight: 700;
	color: var(--ink-bright);
}

.brand-tag {
	font-size: 13px;
	font-weight: 700;
	background: rgba(255, 255, 255, 0.08);
	color: var(--ink-strong);
	padding: 3px 10px;
	border-radius: 6px;
	border: 1px solid rgba(255, 255, 255, 0.15);
}

.axis-badges {
	display: flex;
	flex-wrap: wrap;
	gap: 6px;
}

.axis-badge {
	font-size: 12px;
	font-weight: 600;
	padding: 3px 8px;
	border-radius: 4px;
	background: var(--surface-chip);
	color: var(--ink-pale);
	border: 1px solid rgba(255, 255, 255, 0.06);
}

.badge-tab.tab-xuong {
	background: rgba(56, 189, 248, 0.15);
	color: var(--info);
	border-color: rgba(56, 189, 248, 0.3);
}

.badge-tab.tab-ngcs {
	background: rgba(192, 132, 252, 0.15);
	color: var(--violet);
	border-color: rgba(192, 132, 252, 0.3);
}

.badge-tab.tab-muangoai {
	background: rgba(52, 211, 153, 0.15);
	color: var(--emerald);
	border-color: rgba(52, 211, 153, 0.3);
}

.spec-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding-top: 10px;
	border-top: 1px dashed rgba(255, 255, 255, 0.08);
	gap: 12px;
}

.spec-dim {
	display: flex;
	align-items: center;
	gap: 6px;
}

.dim-text {
	font-size: 14px;
	font-weight: 600;
	color: var(--ink-strong);
}

.mat-chips-active {
	display: flex;
	gap: 6px;
	flex-wrap: wrap;
}

.active-chip {
	font-size: 12px;
	font-weight: 700;
	padding: 2px 8px;
	border-radius: 4px;
}

.mat-blue {
	background: rgba(56, 189, 248, 0.15);
	color: var(--info);
	border: 1px solid rgba(56, 189, 248, 0.3);
}

.mat-amber {
	background: rgba(245, 158, 11, 0.15);
	color: var(--amber);
	border: 1px solid rgba(245, 158, 11, 0.3);
}

.mat-purple {
	background: rgba(192, 132, 252, 0.15);
	color: var(--violet);
	border: 1px solid rgba(192, 132, 252, 0.3);
}

.mat-emerald {
	background: rgba(52, 211, 153, 0.15);
	color: var(--emerald);
	border: 1px solid rgba(52, 211, 153, 0.3);
}

/* Utilities (giữ scoped để không phụ thuộc Tailwind) */
.font-mono {
	font-family: inherit;
	font-variant-numeric: tabular-nums;
	font-feature-settings: "tnum";
}
.text-white {
	color: var(--ink-bright);
}
</style>
