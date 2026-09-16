<template>
	<BaseDrawer :open="open || isOpen" label="Soạn báo giá" @close="$emit('close')">
		<div class="drawer-panel">
			<!-- Header -->
			<div class="drawer-head">
				<h3 class="drawer-title">Soạn báo giá</h3>
				<button
					type="button"
					class="btn-icon"
					title="Đóng panel (Esc)"
					@click="$emit('close')"
				>
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<line x1="18" y1="6" x2="6" y2="18"></line>
						<line x1="6" y1="6" x2="18" y2="18"></line>
					</svg>
				</button>
			</div>

			<QuoteTopSummary
				:form-data="formData"
				:is-roll="isRoll"
				:has-print="hasPrint"
				:compiled-dimensions="compiledDimensions"
				:material-options="materialOptions"
				:is-selected="isMaterialSelected"
				@toggle-material="toggleMaterial"
			/>

			<!-- Body -->
			<div class="drawer-body">
				<QuoteItemsTable
					:rows="itemRows"
					@add-row="addItemRow"
					@remove-row="removeItemRow"
					@row-input="onRowInput"
				/>

				<QuoteCylinderRow
					:need-cylinder="needCylinder"
					:qty="cylinderQty"
					:rate-display="cylinderRateDisplay"
					@qty-input="onCylinderQtyInput"
				/>

				<QuoteFinanceArtwork
					:artwork-url="artworkUrl"
					:figures="previewFigures"
					:is-roll="isRoll"
					:need-cylinder="needCylinder"
					@artwork-input="onArtworkInput"
				/>
			</div>

			<!-- Footer -->
			<div class="drawer-footer">
				<button
					type="button"
					class="act-btn btn-sec"
					@click="$emit('back')"
				>
					← Quay lại
				</button>
				<button
					type="button"
					class="act-btn btn-pri"
					@click="onSubmit"
				>
					Yêu cầu tính giá
				</button>
			</div>
		</div>
	</BaseDrawer>
</template>

<script setup>
import BaseDrawer from './BaseDrawer.vue';
import QuoteTopSummary from './quote/QuoteTopSummary.vue';
import QuoteItemsTable from './quote/QuoteItemsTable.vue';
import QuoteCylinderRow from './quote/QuoteCylinderRow.vue';
import QuoteFinanceArtwork from './quote/QuoteFinanceArtwork.vue';
import { useStep2DirectorForm } from '../composables/useStep2DirectorForm';

const props = defineProps({
	open: {
		type: Boolean,
		default: false,
	},
	isOpen: {
		type: Boolean,
		default: false,
	},
	formData: {
		type: Object,
		default: () => ({}),
	},
	step1Data: {
		type: Object,
		default: () => ({}),
	},
	previewFigures: {
		type: Object,
		default: () => ({
			total_qty: '0',
			subtotal: '0 đ',
			cylinder_total: '0 đ',
			tax_amount: '0 đ',
			grand_total: '0 đ',
		}),
	},
	savedData: {
		type: Object,
		default: () => ({}),
	},
	calculationResult: {
		type: Object,
		default: null,
	},
});

const emit = defineEmits(['close', 'back', 'submit', 'itemsChanged']);

// Tách Task 3: parent chỉ composition + state (composable), 4 khối UI nằm ở quote/*.
const {
	formData,
	isRoll,
	hasPrint,
	needCylinder,
	materialOptions,
	artworkUrl,
	cylinderQty,
	cylinderRateDisplay,
	itemRows,
	isMaterialSelected,
	toggleMaterial,
	compiledDimensions,
	addItemRow,
	removeItemRow,
	onRowInput,
	onCylinderQtyInput,
	onArtworkInput,
	onSubmit,
} = useStep2DirectorForm(props, emit);
</script>

<style scoped>
.drawer-panel {
	width: 100%;
	max-width: 680px;
	height: 100vh;
	background: var(--surface);
	border-left: 1px solid var(--outline);
	box-shadow: -10px 0 30px rgba(0, 0, 0, 0.5);
	display: flex;
	flex-direction: column;
	overflow: hidden;
}

.drawer-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 16px 22px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.drawer-title {
	font-size: 18px;
	font-weight: 800;
	color: var(--ink);
	margin: 0;
}

.drawer-body {
	flex: 1;
	overflow-y: auto;
	padding: 16px 22px;
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.drawer-footer {
	display: flex;
	justify-content: space-between;
	gap: 12px;
	padding: 14px 22px;
	border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.act-btn {
	flex: 1;
	font-size: 14px;
	font-weight: 700;
	padding: 10px 16px;
	border-radius: 8px;
	cursor: pointer;
	border: 1px solid transparent;
}

.btn-sec {
	background: transparent;
	border-color: rgba(255, 255, 255, 0.15);
	color: var(--ink-strong);
}

.btn-pri {
	background: var(--accent-indigo);
	border-color: var(--accent-indigo);
	color: var(--ink-bright);
}
</style>
