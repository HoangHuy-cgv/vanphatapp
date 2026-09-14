<template>
	<Teleport to="body">
		<div v-if="isOpen" class="drawer-overlay" @click.self="$emit('close')">
		<aside class="drawer-panel" aria-label="Chi tiết mặt hàng">
			<!-- Minimalist Cockpit Header -->
			<div class="drawer-head">
				<div class="head-left">
					<span class="item-code-badge font-mono">{{ item ? item.item_code : '' }}</span>
					<span v-if="item" class="supply-badge" :class="isMfg ? 'badge-mfg' : 'badge-buy'">
						{{ isMfg ? 'Xưởng SX' : 'Mua ngoài' }}
					</span>
					<span v-if="item && item.standard_rate" class="head-rate font-mono text-emerald font-bold text-num">
						{{ formatCurrency(item.standard_rate) }} <span class="rate-uom font-sans text-secondary font-normal">/ {{ item.stock_uom || 'Túi' }}</span>
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

			<!-- Loading State -->
			<div v-if="loading" class="drawer-loading">
				Đang tải...
			</div>

			<!-- Cockpit Body -->
			<div v-else-if="item" class="drawer-body">
				<!-- Hero: Name, Customer & Brand -->
				<div class="hero-block">
					<div class="hero-title" :title="item.item_name || ''">
						{{ item.custom_alias || item.item_name || '—' }}
					</div>
					<div v-if="item.customer || item.brand" class="hero-meta text-sm">
						<span v-if="item.customer" class="text-primary font-medium">{{ item.customer }}</span>
						<span v-if="item.customer && item.brand" class="meta-dot">•</span>
						<span v-if="item.brand" class="text-secondary">{{ item.brand }}</span>
					</div>
				</div>

				<!-- Section: Technical Packaging Specs (High-Density Cockpit) -->
				<div class="cockpit-card">
					<!-- Structure Badges, Thickness & Film Width -->
					<div class="spec-row-highlight">
						<div v-if="structureLayers.length" class="layer-badges-wrap">
							<span
								v-for="(layer, idx) in structureLayers"
								:key="idx"
								class="layer-badge"
								:class="getLayerBadgeClass(layer)"
							>
								{{ layer }}
							</span>
						</div>
						<div class="spec-pills-wrap">
							<span v-if="item.custom_thickness_mic" class="pill pill-thick font-mono">
								{{ item.custom_thickness_mic }} mic
							</span>
							<span v-if="item.custom_film_width_mm" class="pill pill-dim font-mono">
								Khổ {{ item.custom_film_width_mm }} mm
							</span>
						</div>
					</div>

					<!-- Bag Geometry & Accessories -->
					<div v-if="pouchDimensions || item.custom_cut_length_mm || item.custom_accessory_spec" class="spec-geo-row">
						<div v-if="pouchDimensions" class="geo-item">
							<span class="geo-val font-mono font-bold">{{ pouchDimensions }}</span>
							<span v-if="Number(item.custom_gusset_mm) > 0" class="geo-sub text-amber font-mono">(Đáy {{ item.custom_gusset_mm }} mm)</span>
						</div>
						<div v-if="item.custom_cut_length_mm" class="geo-item">
							<span class="geo-label">Bước dao</span>
							<span class="geo-val font-mono">{{ item.custom_cut_length_mm }} mm</span>
						</div>
						<div v-if="item.custom_accessory_spec" class="geo-item">
							<span class="geo-label">Phụ kiện</span>
							<span class="geo-val text-primary">{{ item.custom_accessory_spec }}</span>
						</div>
					</div>
				</div>

				<!-- Section: Cylinder Tooling (Trục in - No labels, values speak for themselves) -->
				<div v-if="hasCylinder" class="tooling-strip">
					<div class="tooling-icon-wrap" title="Trục in ống đồng">
						<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
							<path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
							<path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
						</svg>
					</div>
					<div class="tooling-items">
						<span v-if="cylinderCode" class="tooling-val font-mono text-primary font-bold">{{ cylinderCode }}</span>
						<span v-if="cylinderCode && cylinderDimensions" class="tooling-dot">•</span>
						<span v-if="cylinderDimensions" class="tooling-val font-mono text-white">{{ cylinderDimensions }}</span>
						<span v-if="(cylinderCode || cylinderDimensions) && Number(item.custom_cylinder_qty) > 0" class="tooling-dot">•</span>
						<span v-if="Number(item.custom_cylinder_qty) > 0" class="tooling-val text-amber font-semibold font-mono">{{ item.custom_cylinder_qty }} cây</span>
						<span v-if="item.custom_print_tech && item.custom_print_tech !== 'Không in'" class="tooling-dot">•</span>
						<span v-if="item.custom_print_tech && item.custom_print_tech !== 'Không in'" class="tooling-val text-secondary">{{ item.custom_print_tech }}</span>
						<span class="tooling-dot">•</span>
						<span class="tooling-val text-emerald/90">{{ item.custom_cylinder_location || 'Kho Vạn Phát' }}</span>
					</div>
				</div>

				<!-- Section: Operational Metrics (Short, High-Density Stats) -->
				<div class="meta-strip">
					<div class="meta-cell">
						<span class="meta-label">Nhóm</span>
						<span class="meta-val truncate" :title="item.item_group || ''">{{ item.item_group || '—' }}</span>
					</div>
					<div class="meta-cell">
						<span class="meta-label">MOQ</span>
						<span class="meta-val font-mono text-num">{{ formatNumber(item.min_order_qty) }} {{ item.stock_uom }}</span>
					</div>
					<div class="meta-cell">
						<span class="meta-label">Tồn an toàn</span>
						<span class="meta-val font-mono text-num">{{ formatNumber(item.safety_stock) }} {{ item.stock_uom }}</span>
					</div>
					<div class="meta-cell">
						<span class="meta-label">Trạng thái</span>
						<span class="meta-val flex items-center gap-1.5" :class="item.disabled == '1' ? 'text-red' : 'text-emerald'">
							<span class="status-dot" :class="item.disabled == '1' ? 'bg-red' : 'bg-emerald'"></span>
							{{ item.disabled == '1' ? 'Ngừng KD' : 'Hoạt động' }}
						</span>
					</div>
				</div>

				<!-- Section: BOM 2 Cấp (Chỉ hiện khi có BOM) -->
				<div v-if="bom && bom.items && bom.items.length" class="bom-cockpit-block">
					<div class="bom-cockpit-head">
						<span class="bom-title font-mono text-primary font-semibold">BOM: {{ bom.master?.bom_no }}</span>
						<span class="bom-basis text-sm text-secondary font-mono">1.000 {{ bom.master?.uom || item.stock_uom || 'Túi' }}</span>
					</div>
					<div class="bom-table-wrap">
						<table class="bom-table">
							<thead>
								<tr>
									<th style="width: 22%;">Vật tư</th>
									<th style="width: 56%;">Tên nguyên liệu</th>
									<th class="text-right" style="width: 22%;">Định mức</th>
								</tr>
							</thead>
							<tbody>
								<tr v-for="(bi, idx) in bom.items" :key="idx" class="bom-row">
									<td class="font-mono text-primary text-sm">{{ bi.item_code }}</td>
									<td class="font-medium text-white text-sm truncate" :title="bi.item_name || ''">
										{{ bi.custom_alias || bi.item_name || bi.item_code }}
									</td>
									<td class="text-right font-bold text-num text-sm">
										{{ formatNumber(bi.qty) }}
										<span class="text-sm text-secondary font-normal">{{ bi.uom }}</span>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>
			</div>
		</aside>
		</div>
	</Teleport>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue';
import { useCockpitFormat } from '../composables/useCockpitFormat';

const props = defineProps({
	isOpen: { type: Boolean, default: false },
	item: { type: Object, default: null },
	bom: { type: Object, default: null },
	loading: { type: Boolean, default: false },
});

const emit = defineEmits(['close']);

// S7c: formatter dùng chung; giữ empty '—' cho tiền (đặc thù drawer vật tư)
const { formatNumber } = useCockpitFormat();
const formatCurrency = (val) => {
	if (!val && val !== 0) return '—';
	return new Intl.NumberFormat('vi-VN').format(Math.round(val)) + ' đ';
};

const isMfg = computed(() => {
	if (!props.item) return false;
	const t = props.item.default_material_request_type || '';
	return t === 'Manufacture' || t.toLowerCase().includes('xưởng') || t.toLowerCase().includes('mfg');
});

const cylinderCode = computed(() => {
	if (!props.item) return '';
	return props.item.custom_cylinder_item || props.item.custom_cylinder_code || '';
});

const hasCylinder = computed(() => {
	if (!props.item) return false;
	return Boolean(cylinderCode.value || props.item.custom_cylinder_qty || (props.item.custom_print_tech && props.item.custom_print_tech !== 'Không in'));
});

const cylinderDimensions = computed(() => {
	if (!props.item) return '';
	const l = Number(props.item.custom_cylinder_length_mm) || 0;
	const c = Number(props.item.custom_cylinder_circ_mm) || 0;
	if (l === 0 && c === 0) return '';
	return `${l} x ${c} mm`;
});

const pouchDimensions = computed(() => {
	if (!props.item) return '';
	const w = Number(props.item.custom_pouch_width_mm) || 0;
	const l = Number(props.item.custom_pouch_length_mm) || 0;
	if (w === 0 && l === 0) return '';
	return `${w} x ${l} mm`;
});

const structureLayers = computed(() => {
	if (!props.item || !props.item.custom_structure_layers) return [];
	return props.item.custom_structure_layers
		.split('/')
		.map((s) => s.trim())
		.filter(Boolean);
});

// Layer Badge Coloring per AGENTS.md:
// Sky Blue (print), Amber (barrier), Purple (PA), Emerald (sealant)
const getLayerBadgeClass = (layer) => {
	const l = layer.toUpperCase();
	if (l.includes('PET') || l.includes('OPP') || l.includes('BOPP') || l.includes('KRAFT')) {
		return 'badge-layer-print'; // Sky Blue
	}
	if (l.includes('AL') || l.includes('MPET') || l.includes('MCPP') || l.includes('K-PET')) {
		return 'badge-layer-barrier'; // Amber
	}
	if (l.includes('PA') || l.includes('NYLON') || l.includes('ONY')) {
		return 'badge-layer-pa'; // Purple
	}
	return 'badge-layer-sealant'; // Emerald (PE, CPP, LDPE, HDPE)
};

// Keyboard listener for Escape
const onKeyDown = (e) => {
	if (e.key === 'Escape' && props.isOpen) {
		emit('close');
	}
};

onMounted(() => {
	window.addEventListener('keydown', onKeyDown);
});

onUnmounted(() => {
	window.removeEventListener('keydown', onKeyDown);
});
</script>

<style scoped>
.drawer-overlay {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.75);
	backdrop-filter: blur(4px);
	z-index: 999;
	display: flex;
	justify-content: flex-end;
}

.drawer-panel {
	width: 100%;
	max-width: 580px;
	height: 100%;
	background: #0b0f19;
	border-left: 1px solid #3a424e;
	display: flex;
	flex-direction: column;
	box-shadow: -10px 0 30px rgba(0, 0, 0, 0.7);
	animation: slideIn 0.2s ease-out;
}

@keyframes slideIn {
	from { transform: translateX(100%); }
	to { transform: translateX(0); }
}

.drawer-head {
	padding: 14px 18px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.08);
	display: flex;
	justify-content: space-between;
	align-items: center;
	background: #161b22;
	flex-shrink: 0;
}

.head-left {
	display: flex;
	align-items: center;
	gap: 10px;
	flex-wrap: wrap;
}

.item-code-badge {
	font-size: 14.5px;
	font-weight: 700;
	background: rgba(78, 161, 224, 0.15);
	color: #4ea1e0;
	padding: 2px 8px;
	border-radius: 4px;
	border: 1px solid rgba(78, 161, 224, 0.3);
}

.supply-badge {
	font-size: 12.5px;
	font-weight: 600;
	padding: 2px 8px;
	border-radius: 4px;
}

.badge-mfg {
	background: rgba(56, 189, 248, 0.15);
	color: #38bdf8;
	border: 1px solid rgba(56, 189, 248, 0.3);
}

.badge-buy {
	background: rgba(163, 113, 247, 0.15);
	color: #a371f7;
	border: 1px solid rgba(163, 113, 247, 0.3);
}

.head-rate {
	font-size: 16px;
	padding-left: 4px;
}

.rate-uom {
	font-size: 13px;
}

.btn-icon {
	background: transparent;
	border: none;
	color: #8b949e;
	cursor: pointer;
	padding: 6px;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 6px;
	transition: all 0.15s ease;
}

.btn-icon:hover {
	color: #ffffff;
	background: rgba(255, 255, 255, 0.08);
}

.drawer-loading {
	padding: 40px;
	text-align: center;
	color: #8b949e;
	font-size: 14px;
}

.drawer-body {
	flex: 1;
	overflow-y: auto;
	padding: 16px 18px;
	display: flex;
	flex-direction: column;
	gap: 12px;
	scrollbar-width: thin;
	scrollbar-color: #3a424e #161b22;
}

.drawer-body::-webkit-scrollbar {
	width: 6px;
}

.drawer-body::-webkit-scrollbar-thumb {
	background: #3a424e;
	border-radius: 3px;
}

/* Hero Block */
.hero-block {
	display: flex;
	flex-direction: column;
	gap: 3px;
	padding-bottom: 2px;
}

.hero-title {
	font-size: 20px;
	font-weight: 800;
	color: #ffffff;
	line-height: 1.25;
	letter-spacing: -0.01em;
}

.hero-meta {
	display: flex;
	align-items: center;
	gap: 6px;
	margin-top: 2px;
}

.meta-dot {
	color: #4b5563;
}

/* Cockpit Card: Packaging Specs */
.cockpit-card {
	background: #161b22;
	border: 1px solid rgba(255, 255, 255, 0.08);
	border-radius: 8px;
	padding: 12px 14px;
	display: flex;
	flex-direction: column;
	gap: 10px;
}

.spec-row-highlight {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 10px;
	flex-wrap: wrap;
	padding-bottom: 8px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.layer-badges-wrap {
	display: flex;
	flex-wrap: wrap;
	gap: 6px;
	align-items: center;
}

.layer-badge {
	font-size: 14px;
	font-weight: 700;
	padding: 0;
	letter-spacing: 0.2px;
}

.spec-pills-wrap {
	display: flex;
	align-items: center;
	gap: 10px;
}

.pill {
	font-size: 14px;
	padding: 0;
	font-weight: 700;
}

.pill-thick {
	color: #fbbf24;
}

.pill-dim {
	color: #cbd5e1;
}

.spec-geo-row {
	display: flex;
	align-items: center;
	gap: 16px;
	flex-wrap: wrap;
}

.geo-item {
	display: flex;
	align-items: center;
	gap: 6px;
	font-size: 15px;
}

.geo-val {
	color: #ffffff;
}

.geo-sub {
	font-size: 13.5px;
}

.geo-label {
	font-size: 12px;
	color: #8b949e;
	text-transform: uppercase;
	letter-spacing: 0.03em;
}

/* Tooling Strip (Trục in - No labels, values speak for themselves) */
.tooling-strip {
	background: #161b22;
	border: 1px solid rgba(255, 255, 255, 0.08);
	border-radius: 8px;
	padding: 10px 14px;
	display: flex;
	align-items: center;
	gap: 10px;
}

.tooling-icon-wrap {
	color: #8b949e;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
}

.tooling-items {
	display: flex;
	align-items: center;
	gap: 8px;
	flex-wrap: wrap;
	font-size: 14px;
}

.tooling-dot {
	color: #4b5563;
}

/* Operational Meta Strip */
.meta-strip {
	display: grid;
	grid-template-columns: repeat(4, 1fr);
	gap: 8px;
	background: #161b22;
	border: 1px solid rgba(255, 255, 255, 0.08);
	border-radius: 8px;
	padding: 10px 12px;
}

.meta-cell {
	display: flex;
	flex-direction: column;
	gap: 2px;
	min-width: 0;
}

.meta-label {
	font-size: 12px;
	color: #8b949e;
	text-transform: uppercase;
	letter-spacing: 0.04em;
	font-weight: 600;
}

.meta-val {
	font-size: 14px;
	color: #e6edf3;
	font-weight: 600;
}

.status-dot {
	width: 6px;
	height: 6px;
	border-radius: 50%;
	display: inline-block;
}

.bg-emerald { background: #34d399; }
.bg-red { background: #f87171; }

/* BOM Block */
.bom-cockpit-block {
	background: #161b22;
	border: 1px solid rgba(255, 255, 255, 0.08);
	border-radius: 8px;
	overflow: hidden;
}

.bom-cockpit-head {
	padding: 8px 12px;
	background: #1a1f27;
	border-bottom: 1px solid #3a424e;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.bom-title {
	font-size: 13.5px;
}

.bom-table-wrap {
	overflow-x: auto;
}

.bom-table {
	width: 100%;
	border-collapse: collapse;
}

.bom-table th {
	background: rgba(0, 0, 0, 0.2);
	color: #8b949e;
	font-weight: 600;
	font-size: 12.5px;
	padding: 7px 10px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.05);
	text-align: left;
}

.bom-table td {
	padding: 7px 10px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.bom-row:hover td {
	background: rgba(255, 255, 255, 0.02);
}

/* 4 Layer Badges Palette */
.badge-layer-print {
	color: #4ea1e0;
}

.badge-layer-barrier {
	color: #f59e0b;
}

.badge-layer-pa {
	color: #c084fc;
}

.badge-layer-sealant {
	color: #34d399;
}

/* Utilities */
.text-primary { color: #4ea1e0; }
.text-secondary { color: #8b949e; }
.text-emerald { color: #34d399; }
.text-amber { color: #f59e0b; }
.font-mono {
	font-family: inherit;
	font-variant-numeric: tabular-nums;
	font-feature-settings: "tnum";
}
.text-num { font-variant-numeric: tabular-nums; }
.truncate {
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}
.flex { display: flex; }
.items-center { align-items: center; }
.gap-1\.5 { gap: 6px; }
.text-right { text-align: right; }
.bom-table th.text-right,
.bom-table td.text-right {
	text-align: right;
}
</style>
