<template>
	<DetailShell :open="isOpen" label="Chi tiết khách hàng" accent="#4ea1e0" @close="$emit('close')">
		<template #head>
			<span class="vp-code-badge vp-mono">{{ customer ? customer.name : '' }}</span>
			<span v-if="customer" class="vp-tag-badge">
				{{ customer.customer_type === 'Company' ? 'Doanh nghiệp' : 'Cá nhân' }}
			</span>
			<span v-if="customer && customer.payment_terms && customer.payment_terms.toLowerCase().includes('gối đầu')" class="vp-head-credit vp-mono vp-text-emerald font-bold">
				Trả sau
			</span>
			<span v-else class="vp-head-credit vp-mono vp-text-amber">
				Trả trước
			</span>
		</template>

		<div v-if="customer">
			<DetailHero :title="customer.alias || customer.customer_name" :sub="customer.customer_name" sub-class="vp-text-secondary" />

			<DetailCard class="mt-3">
				<DetailSpecGrid :cells="specCells" />
			</DetailCard>

			<DetailCard class="mt-3">
				<DetailContactRow label="Địa chỉ giao hàng / Trụ sở">
					{{ customer.primary_address || 'Chưa cập nhật' }}
				</DetailContactRow>
				<DetailContactRow v-if="customer.customer_primary_contact" label="Đại diện giao dịch / Kinh doanh" icon="user" row-class="mt-2">
					<span class="vp-accent font-medium">{{ customer.customer_primary_contact }}</span>
				</DetailContactRow>
			</DetailCard>

			<DetailCard v-if="dedicatedItems.length" class="mt-3" title="MẶT HÀNG ĐẶT RIÊNG" :count="dedicatedItems.length">
				<div class="dedicated-list">
					<div
						v-for="it in dedicatedItems"
						:key="it.item_code"
						class="dedicated-item"
					>
						<div class="ded-left">
							<span class="vp-mono vp-accent text-xs">{{ it.item_code }}</span>
							<span class="ded-name font-medium">{{ it.custom_alias || it.item_name }}</span>
						</div>
						<div class="ded-right">
							<span v-if="it.custom_structure_layers" class="layer-pill text-xs vp-mono">{{ it.custom_structure_layers }}</span>
							<span v-if="it.standard_rate" class="rate-pill vp-text-emerald vp-mono">{{ formatCurrency(it.standard_rate) }} đ</span>
						</div>
					</div>
				</div>
			</DetailCard>
		</div>
	</DetailShell>
</template>

<script setup>
import { computed } from 'vue';
import DetailShell from './DetailShell.vue';
import DetailHero from './DetailHero.vue';
import DetailCard from './DetailCard.vue';
import DetailSpecGrid from './DetailSpecGrid.vue';
import DetailContactRow from './DetailContactRow.vue';
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

// Spec thương mại/hạn mức — Drawer tự chốt chuỗi hiển thị (visual only).
const specCells = computed(() => {
	const c = props.customer;
	if (!c) return [];
	return [
		{ label: 'Nhóm khách', value: c.customer_group || 'Thương Mại & Phân Phối', cls: 'vp-accent font-medium' },
		{ label: 'Khu vực', value: c.territory || 'Việt Nam' },
		{ label: 'Điều khoản thanh toán', value: c.payment_terms || 'Cọc trước 50% - Giao hàng 50%', cls: 'vp-text-amber' },
		{ label: 'Mã số thuế', value: c.tax_id || '—', cls: 'vp-mono' },
	];
});

const dedicatedItems = computed(() => {
	if (!props.customer || !props.masterItems) return [];
	const cName = (props.customer.customer_name || '').trim().toLowerCase();
	const cAlias = (props.customer.alias || '').trim().toLowerCase();
	if (!cName && !cAlias) return [];
	return props.masterItems.filter(it => {
		// Native: 1 TP = 1 KH qua bảng con customer_items (customer_name);
		// fallback ref customer_code khi detail chưa kèm dòng con.
		const rows = Array.isArray(it.customer_items) ? it.customer_items : [];
		for (const r of rows) {
			const n = (r.customer_name || '').trim().toLowerCase();
			if (n && (n === cName || (cAlias && n === cAlias))) return true;
		}
		return false;
	});
});

// P4b: BaseDrawer native <dialog> lo Esc/focus/inert
</script>

<style scoped>
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
	background: var(--surface-inset);
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
	color: var(--ink-crisp);
}

.ded-right {
	display: flex;
	align-items: center;
	gap: 8px;
}

.layer-pill {
	padding: 2px 6px;
	border-radius: 3px;
	background: var(--surface-pill);
	color: var(--ink-slate);
}

.rate-pill {
	font-size: 13px;
	font-weight: 700;
}
</style>
