<template>
	<BaseDrawer :open="isOpen" label="Chi tiết đơn hàng" @close="$emit('close')">
		<div class="drawer-panel">
			<!-- Header -->
			<div class="drawer-head">
				<div class="head-title-wrap">
					<h3 class="drawer-title">Chi tiết đơn hàng</h3>
					<span class="order-code-badge font-mono">{{ order ? order.name : '' }}</span>
				</div>
				<button
					type="button"
					class="btn-icon"
					title="Đóng (Esc)"
					@click="$emit('close')"
				>
					<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<line x1="18" y1="6" x2="6" y2="18"></line>
						<line x1="6" y1="6" x2="18" y2="18"></line>
					</svg>
				</button>
			</div>

			<!-- Body -->
			<div v-if="loading" class="drawer-loading">
				Đang tải dữ liệu...
			</div>

			<div v-else-if="order" class="drawer-body">
				<OrderSummaryCard :order="order" />
				<OrderItemsCard
					:items="orderItems"
					:qty="order.qty"
					:uom="order.uom || 'Túi'"
					@preview="openLightbox"
				/>
				<OrderFinanceCard :order="order" />
				<OrderProgressCard :order="order" />
			</div>

			<OrderLightbox
				:url="activeLightboxUrl"
				:title="activeLightboxTitle"
				@close="activeLightboxUrl = null"
			/>

			<OrderFooterActions
				v-if="order"
				:order="order"
				:deposit-input-amount="depositInputAmount"
				@update:deposit-input-amount="depositInputAmount = $event"
				@save-deposit="handleSaveDeposit"
				@override-hold="handleOverrideHold"
				@report-progress="handleReportProgress"
				@create-delivery="handleCreateDelivery"
			/>
		</div>
	</BaseDrawer>
</template>

<script setup>
import { ref, computed, toRef } from 'vue';
import { useOrderDeposit } from '../composables/useOrderDeposit';
import BaseDrawer from './BaseDrawer.vue';
import OrderSummaryCard from './order/OrderSummaryCard.vue';
import OrderItemsCard from './order/OrderItemsCard.vue';
import OrderFinanceCard from './order/OrderFinanceCard.vue';
import OrderProgressCard from './order/OrderProgressCard.vue';
import OrderFooterActions from './order/OrderFooterActions.vue';
import OrderLightbox from './order/OrderLightbox.vue';

const props = defineProps({
	isOpen: { type: Boolean, default: false },
	order: { type: Object, default: null },
	loading: { type: Boolean, default: false },
});

const emit = defineEmits(['close', 'update-order', 'create-delivery']);

// Deposit/lifecycle handlers — mọi số cọc/trạng thái do backend trả (useOrderDeposit).
const {
	depositInputAmount,
	handleSaveDeposit,
	handleOverrideHold,
	handleReportProgress,
	handleCreateDelivery,
} = useOrderDeposit(toRef(props, 'order'), emit);

// Lightbox state
const activeLightboxUrl = ref(null);
const activeLightboxTitle = ref('');

const openLightbox = (url, title) => {
	activeLightboxUrl.value = url;
	activeLightboxTitle.value = title;
};

const orderItems = computed(() => {
	if (!props.order) return [];
	if (props.order.items && props.order.items.length) {
		return props.order.items;
	}
	// Fallback single item — chỉ hiển thị, không tự tính rate/amount (ADR-006).
	return [
		{
			item_code: props.order.name,
			item_name: props.order.item_name || props.order.description,
			variant_name: props.order.item_name,
			artwork_url: props.order.artwork_url,
			qty: props.order.qty,
			uom: props.order.uom || 'Túi',
			rate: 0,
			amount: props.order.product_total || props.order.grand_total,
			is_cylinder: false,
		},
	];
});
</script>

<style scoped>
.drawer-panel {
	width: 100%;
	max-width: 680px;
	height: 100%;
	background: var(--canvas-deep);
	border-left: 1px solid var(--outline);
	display: flex;
	flex-direction: column;
	box-shadow: -10px 0 30px rgba(0, 0, 0, 0.7);
}

.drawer-head {
	padding: 16px 24px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.08);
	display: flex;
	justify-content: space-between;
	align-items: center;
	background: var(--surface);
}

.head-title-wrap {
	display: flex;
	align-items: center;
	gap: 12px;
}

.drawer-title {
	font-size: 18px;
	font-weight: 700;
	color: var(--ink-bright);
	margin: 0;
}

.order-code-badge {
	font-size: 13px;
	font-weight: 700;
	background: rgba(78, 161, 224, 0.15);
	color: var(--primary);
	padding: 2px 8px;
	border-radius: 4px;
	border: 1px solid rgba(78, 161, 224, 0.3);
}

.drawer-loading {
	padding: 40px;
	text-align: center;
	color: var(--ink-faint);
	font-size: 15px;
}

.drawer-body {
	flex: 1;
	overflow-y: auto;
	padding: 20px 24px;
	display: flex;
	flex-direction: column;
	gap: 16px;
}

/* Utilities */
.font-mono {
	font-family: inherit;
	font-variant-numeric: tabular-nums;
	font-feature-settings: "tnum";
}
</style>
