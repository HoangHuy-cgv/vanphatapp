<template>
	<BaseDrawer :open="open" :label="label" @close="$emit('close')">
		<div class="vp-detail-panel" :class="{ 'vp-detail-panel--lock': fixedHead, 'vp-detail-panel--compact': compact }" :style="panelStyle">
			<div class="vp-detail-head">
				<div class="vp-detail-head-left">
					<slot name="head" />
				</div>
				<button
					type="button"
					class="vp-detail-close"
					title="Đóng (Esc)"
					aria-label="Đóng chi tiết"
					@click="$emit('close')"
				>
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
						<line x1="18" y1="6" x2="6" y2="18"></line>
						<line x1="6" y1="6" x2="18" y2="18"></line>
					</svg>
				</button>
			</div>
			<div class="vp-detail-body">
				<slot />
			</div>
		</div>
	</BaseDrawer>
</template>

<script setup>
/**
 * Vỏ chung cho 4 Drawer chi tiết (Customer/Supplier/Item/User).
 * Bọc BaseDrawer (native <dialog> lo Esc/backdrop/focus), các Drawer chỉ
 * giữ sections/logic riêng qua slot head + default. CSS dùng chung đặt ở
 * đây (global, prefix vp-) để xóa CSS lặp ở từng Drawer.
 * Accent/panel/head khác nhau giữa các Drawer giữ qua props visual.
 */
import { computed } from 'vue';
import BaseDrawer from './BaseDrawer.vue';

const props = defineProps({
	open: { type: Boolean, default: false },
	label: { type: String, default: 'Chi tiết' },
	accent: { type: String, default: '#4ea1e0' },
	panelBg: { type: String, default: '#161b22' },
	headBg: { type: String, default: '#11151c' },
	fixedHead: { type: Boolean, default: false },
	compact: { type: Boolean, default: false },
});

defineEmits(['close']);

const panelStyle = computed(() => ({
	'--vp-accent': props.accent,
	'--vp-panel-bg': props.panelBg,
	'--vp-head-bg': props.headBg,
}));
</script>

<style>
/* Vỏ + atoms detail dùng chung (global để áp vào nội dung slot). */
.vp-detail-panel {
	width: 100%;
	max-width: 680px;
	height: 100vh;
	background: var(--vp-panel-bg, var(--surface));
	border-left: 1px solid var(--outline);
	box-shadow: -8px 0 32px rgba(0, 0, 0, 0.6);
	display: flex;
	flex-direction: column;
	overflow-y: auto;
	color: var(--ink-bright);
}
.vp-detail-panel--lock {
	height: 100%;
	overflow: hidden;
}
.vp-detail-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 14px 20px;
	background: var(--vp-head-bg, var(--surface-head));
	border-bottom: 1px solid var(--outline);
	flex-shrink: 0;
}
.vp-detail-head-left {
	display: flex;
	align-items: center;
	gap: 10px;
	flex-wrap: wrap;
}
.vp-detail-close {
	background: transparent;
	border: none;
	color: var(--ink-slate);
	cursor: pointer;
	padding: 4px;
	border-radius: 4px;
	display: inline-flex;
	align-items: center;
	justify-content: center;
	transition: color 0.15s;
}
.vp-detail-close:hover {
	color: var(--ink-bright);
}
.vp-detail-body {
	padding: 20px;
	display: flex;
	flex-direction: column;
	gap: 14px;
	flex: 1;
}
.vp-detail-panel--lock .vp-detail-body {
	overflow-y: auto;
	scrollbar-width: thin;
	scrollbar-color: var(--outline) var(--surface);
}
.vp-detail-panel--lock .vp-detail-body::-webkit-scrollbar {
	width: 6px;
}
.vp-detail-panel--lock .vp-detail-body::-webkit-scrollbar-thumb {
	background: var(--outline);
	border-radius: 3px;
}
.vp-detail-panel--compact .vp-detail-head {
	padding: 14px 18px;
}
.vp-detail-panel--compact .vp-detail-body {
	padding: 16px 18px;
	gap: 12px;
}
.vp-detail-panel--compact .vp-hero {
	padding-bottom: 2px;
	border-bottom: none;
	display: flex;
	flex-direction: column;
	gap: 3px;
}
.vp-detail-panel--compact .vp-hero-title {
	font-weight: 800;
	line-height: 1.25;
	letter-spacing: -0.01em;
}
.vp-hero {
	padding-bottom: 12px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.vp-hero-title {
	font-size: 20px;
	font-weight: 700;
	color: var(--ink-bright);
	line-height: 1.3;
}
.vp-hero-sub {
	font-size: 13.5px;
	margin-top: 4px;
	line-height: 1.4;
}
.vp-card {
	background: var(--surface-low);
	border: 1px solid var(--outline);
	border-radius: 6px;
	padding: 14px 16px;
}
.vp-card-head {
	font-size: 12px;
	font-weight: 700;
	color: var(--ink-gray);
	letter-spacing: 0.05em;
	margin-bottom: 10px;
	display: flex;
	gap: 6px;
}
.vp-spec-grid {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 12px;
}
.vp-spec-cell {
	display: flex;
	flex-direction: column;
	gap: 3px;
}
.vp-cell-label {
	font-size: 11.5px;
	text-transform: uppercase;
	color: var(--ink-gray);
	letter-spacing: 0.04em;
	font-weight: 600;
}
.vp-cell-val {
	font-size: 13.5px;
	color: var(--ink-snow);
}
.vp-contact-row {
	display: flex;
	align-items: flex-start;
	gap: 10px;
}
.vp-contact-icon {
	color: var(--vp-accent, var(--primary));
	margin-top: 2px;
	display: inline-flex;
}
.vp-contact-info {
	display: flex;
	flex-direction: column;
	gap: 2px;
}
.vp-contact-label {
	font-size: 11.5px;
	color: var(--ink-gray);
	text-transform: uppercase;
	letter-spacing: 0.04em;
	font-weight: 600;
}
.vp-contact-val {
	font-size: 13.5px;
	color: var(--ink-mist);
	line-height: 1.4;
}
.vp-code-badge {
	padding: 3px 8px;
	border-radius: 4px;
	background: var(--surface-badge);
	color: var(--vp-accent, var(--primary));
	font-weight: 700;
	font-size: 13.5px;
	border: 1px solid rgba(255, 255, 255, 0.12); /* fallback khi browser thiếu color-mix */
	border: 1px solid color-mix(in srgb, var(--vp-accent, var(--primary)) 30%, transparent);
}
.vp-tag-badge {
	padding: 2px 7px;
	border-radius: 4px;
	background: rgba(255, 255, 255, 0.06);
	color: var(--ink-slate);
	font-size: 12px;
	font-weight: 600;
	border: 1px solid rgba(255, 255, 255, 0.1);
}
.vp-head-code {
	font-size: 14.5px;
	font-weight: 700;
	color: var(--vp-accent, var(--primary));
}
.vp-head-credit {
	font-size: 13px;
}
.vp-note {
	color: var(--ink-mist);
	line-height: 1.5;
}
.vp-loading {
	padding: 40px;
	text-align: center;
	color: var(--ink-faint);
	font-size: 14px;
}
.vp-accent {
	color: var(--vp-accent, var(--primary));
}
.vp-text-secondary {
	color: var(--ink-slate);
}
.vp-text-amber {
	color: var(--amber);
}
.vp-text-emerald {
	color: var(--ok);
}
.vp-mono {
	font-family: inherit;
	font-variant-numeric: tabular-nums;
	font-feature-settings: "tnum";
}
</style>
