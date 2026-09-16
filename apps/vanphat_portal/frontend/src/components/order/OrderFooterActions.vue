<template>
	<!-- Footer Actions (State Machine Gọn Gàng) -->
	<div class="drawer-footer">
		<!-- TRẠNG THÁI 1: HOLD (Chưa đủ cọc) -> Ô nhập cọc nhanh tại chỗ -->
		<div v-if="order.is_hold || order.order_state === 'Tạm giữ (Chưa đủ cọc)'" class="hold-action-row">
			<div class="deposit-input-group">
				<span class="input-addon">Cọc thêm (VNĐ)</span>
				<input
					type="number"
					:model-value="depositInputAmount"
					placeholder="Nhập số tiền..."
					class="deposit-input text-num"
					min="0"
					step="1000000"
					@input="$emit('update:depositInputAmount', Number($event.target.value) || null)"
				/>
			</div>
			<button
				type="button"
				class="btn-action-primary"
				@click="$emit('save-deposit')"
			>
				Lưu cọc
			</button>
			<button
				type="button"
				class="btn-action-secondary"
				@click="$emit('override-hold')"
			>
				Duyệt ngoại lệ
			</button>
		</div>

		<!-- TRẠNG THÁI 2: ĐANG XỬ LÝ -->
		<div v-else-if="order.order_state === 'Đang xử lý'" class="normal-actions">
			<button
				type="button"
				class="btn-action-primary flex-1"
				@click="$emit('report-progress')"
			>
				+ Báo cáo sản xuất hoàn thành
			</button>
		</div>

		<!-- TRẠNG THÁI 3: SẴN SÀNG GIAO -> Nút giao hàng full-width sáng xanh -->
		<div v-else-if="order.order_state === 'Sẵn sàng giao'" class="ready-action">
			<button
				type="button"
				class="btn-delivery-glow"
				@click="$emit('create-delivery')"
			>
				+ XUẤT GIAO HÀNG
			</button>
		</div>
	</div>
</template>

<script setup>
// Tách từ DrawerOrderDetail.vue — footer chạy theo order_state server (state machine).
defineProps({
	order: { type: Object, required: true },
	depositInputAmount: { type: [Number, null], default: null },
});

defineEmits([
	'update:depositInputAmount',
	'save-deposit',
	'override-hold',
	'report-progress',
	'create-delivery',
]);
</script>

<style scoped>
/* Footer State Machine */
.drawer-footer {
	padding: 16px 24px;
	background: var(--surface);
	border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.hold-action-row {
	display: flex;
	gap: 10px;
	align-items: center;
}

.deposit-input-group {
	flex: 1;
	display: flex;
	align-items: center;
	background: var(--surface-head);
	border: 1px solid var(--outline);
	border-radius: 6px;
	overflow: hidden;
}

.input-addon {
	font-size: 12px;
	font-weight: 600;
	color: var(--ink-faint);
	padding: 0 10px;
	white-space: nowrap;
	border-right: 1px solid var(--outline);
}

.deposit-input {
	flex: 1;
	height: 38px;
	background: transparent;
	border: none;
	color: var(--ink-bright);
	padding: 0 12px;
	font-size: 14px;
	outline: none;
}

.btn-action-primary {
	background: var(--accent-blue);
	border: none;
	color: var(--ink-bright);
	font-size: 14px;
	font-weight: 700;
	height: 38px;
	padding: 0 16px;
	border-radius: 6px;
	cursor: pointer;
	transition: background 0.15s ease;
}

.btn-action-primary:hover {
	background: var(--accent-blue-press);
}

.btn-action-secondary {
	background: var(--raised);
	border: 1px solid var(--outline);
	color: var(--ink-pale);
	font-size: 14px;
	font-weight: 600;
	height: 38px;
	padding: 0 14px;
	border-radius: 6px;
	cursor: pointer;
	transition: all 0.15s ease;
}

.btn-action-secondary:hover {
	background: var(--raised-hover);
	color: var(--ink-bright);
}

.normal-actions {
	display: flex;
	width: 100%;
}

.btn-delivery-glow {
	width: 100%;
	height: 44px;
	background: var(--accent-blue);
	border: none;
	border-radius: 6px;
	color: var(--ink-bright);
	font-size: 15px;
	font-weight: 800;
	cursor: pointer;
	box-shadow: 0 0 15px rgba(2, 132, 199, 0.5);
	transition: all 0.15s ease;
}

.btn-delivery-glow:hover {
	background: var(--accent-blue-press);
	box-shadow: 0 0 20px rgba(2, 132, 199, 0.7);
}

/* Utilities */
.text-num {
	font-variant-numeric: tabular-nums;
	font-feature-settings: 'tnum';
}
.flex-1 {
	flex: 1;
}
</style>
