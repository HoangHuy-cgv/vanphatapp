<template>
	<!-- KHỐI 4: TIẾN ĐỘ THỰC HIỆN (TRIỆT TIÊU LABEL RÁC, HIỂN THỊ VALUE TRỰC TIẾP) -->
	<div class="ops-card">
		<!-- Đơn Xưởng sản xuất -->
		<div v-if="order.order_tab === 'xuong_sx'" class="ops-value-box">
			<div class="ops-main-line">
				<span class="ops-text">
					{{ order.materials_status || 'Đủ màng' }} • {{ order.factory_stage || 'Đang xử lý' }} • {{ formatNumber(order.completed_qty || 0) }} / {{ formatNumber(order.qty) }} {{ order.uom || 'Túi' }}
					<span class="ops-pct">({{ progressPct }}%)</span>
				</span>
			</div>
			<div class="ops-bar-track">
				<div
					class="ops-bar-fill bg-cyan"
					:style="{ width: Math.min(100, progressPct) + '%' }"
				></div>
			</div>
		</div>

		<!-- Đơn Túi NGCS hoặc Mua Ngoài (SLA NCC) -->
		<div v-else class="ops-value-box">
			<div class="ops-main-line">
				<span class="ops-text">
					NCC {{ order.supplier_name || 'Gia công' }} • {{ order.procurement_stage || 'Đang thực hiện' }}
				</span>
				<span v-if="order.supplier_eta_days !== null && order.supplier_eta_days !== undefined" class="sla-badge" :class="getSlaClass(order.supplier_eta_days)">
					{{ formatSlaText(order.supplier_eta_days) }}
				</span>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed } from 'vue';
import { useCockpitFormat } from '../../composables/useCockpitFormat';

// Tách từ DrawerOrderDetail.vue — % tiến độ suy từ số server, không nhập tay.
const props = defineProps({
	order: { type: Object, required: true },
});

const { formatNumber } = useCockpitFormat();

const progressPct = computed(() =>
	Math.round(((props.order.completed_qty || 0) / (props.order.qty || 1)) * 100),
);

// SLA styling
const getSlaClass = (days) => {
	if (days < 0) return 'sla-overdue';
	if (days === 0) return 'sla-today';
	return 'sla-ontime';
};

const formatSlaText = (days) => {
	if (days < 0) return `Trễ ${Math.abs(days)} ngày`;
	if (days === 0) return 'Hôm nay giao';
	return `Còn ${days} ngày`;
};
</script>

<style scoped>
/* KHỐI 4: TIẾN ĐỘ THỰC HIỆN */
.ops-card {
	background: var(--surface-card);
	border: 1px solid rgba(255, 255, 255, 0.06);
	border-radius: 8px;
	padding: 14px 16px;
}

.ops-main-line {
	display: flex;
	align-items: center;
	gap: 8px;
	font-size: 14px;
	font-weight: 600;
	color: var(--ink-strong);
}

.ops-pct {
	color: var(--ink-faint);
	font-weight: 400;
	margin-left: 4px;
}

.ops-bar-track {
	height: 5px;
	background: rgba(255, 255, 255, 0.08);
	border-radius: 3px;
	margin-top: 10px;
	overflow: hidden;
}

.ops-bar-fill {
	height: 100%;
	border-radius: 3px;
}

.sla-badge {
	font-size: 12px;
	font-weight: 700;
	padding: 2px 8px;
	border-radius: 4px;
	margin-left: auto;
}

.sla-overdue {
	background: rgba(239, 68, 68, 0.2);
	color: var(--danger-bright);
	border: 1px solid var(--danger-bright);
}

.sla-today {
	background: rgba(245, 158, 11, 0.2);
	color: var(--amber);
	border: 1px solid var(--amber);
}

.sla-ontime {
	background: rgba(255, 255, 255, 0.08);
	color: var(--ink-pale);
}

.bg-cyan {
	background: var(--info);
}
</style>
