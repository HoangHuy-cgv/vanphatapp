<template>
	<DetailShell :open="isOpen" label="Chi tiết nhà cung cấp" accent="#38bdf8" @close="$emit('close')">
		<template #head>
			<span class="vp-code-badge vp-mono">{{ supplier ? supplier.name : '' }}</span>
			<span v-if="supplier" class="vp-tag-badge">
				{{ supplier.supplier_group || 'Nhà Cung Cấp' }}
			</span>
		</template>

		<div v-if="supplier">
			<DetailHero :title="supplier.alias || supplier.supplier_name" :sub="supplier.supplier_name" sub-class="vp-text-secondary" />

			<DetailCard class="mt-3">
				<DetailSpecGrid :cells="specCells" />
			</DetailCard>

			<DetailCard class="mt-3">
				<DetailContactRow label="Địa chỉ xưởng / Nhà máy">
					{{ supplier.primary_address || 'Chưa cập nhật' }}
				</DetailContactRow>
				<DetailContactRow v-if="supplier.supplier_primary_contact || supplier.mobile_no" label="Liên hệ đặt hàng" icon="phone" row-class="mt-2">
					<span v-if="supplier.supplier_primary_contact" class="vp-accent font-medium">{{ supplier.supplier_primary_contact }}</span>
					<span v-if="supplier.supplier_primary_contact && supplier.mobile_no"> • </span>
					<span v-if="supplier.mobile_no" class="vp-mono">{{ supplier.mobile_no }}</span>
				</DetailContactRow>
			</DetailCard>

			<DetailCard v-if="supplier.note" class="mt-3" title="DANH MỤC VẬT TƯ & DỊCH VỤ CUNG CẤP">
				<p class="vp-note text-sm">{{ supplier.note }}</p>
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

// Spec điều khoản thương mại — Drawer tự chốt chuỗi hiển thị (visual only).
const specCells = computed(() => {
	const s = props.supplier;
	if (!s) return [];
	return [
		{ label: 'Mã số thuế', value: s.tax_id || '—', cls: 'vp-mono' },
		{ label: 'Điều khoản thanh toán', value: s.payment_terms || 'Công nợ gối đầu', cls: 'vp-text-amber' },
		{ label: 'Tiền tệ', value: s.default_currency || 'VND', cls: 'vp-mono' },
		{ label: 'Quốc gia', value: s.country || 'Việt Nam' },
	];
});

// P4b: BaseDrawer native <dialog> lo Esc/focus/inert
</script>
