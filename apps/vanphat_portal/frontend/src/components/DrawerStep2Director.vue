<template>
	<div class="drawer-overlay" @click.self="$emit('close')">
		<aside class="drawer-panel" aria-label="Soạn báo giá">
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

			<!-- Top Summary -->
			<div class="drawer-top-summary">
				<!-- LINE 1: Tên khách hàng & Brand Tag -->
				<div class="cust-brand-bar">
					<div class="cust-info">
						<span class="icon-building">🏢</span>
						<span class="cust-name">{{ formData.customer || 'Khách hàng' }}</span>
					</div>
					<div v-if="formData.brand" class="brand-tag">
						{{ formData.brand }}
					</div>
				</div>

				<!-- LINE 2: 4 Axis Badges 4 màu chuyên biệt -->
				<div class="axis-badges">
					<span class="axis-badge badge-product">{{ formData.product_type }}</span>
					<span v-if="!isRoll" class="axis-badge badge-accessory">{{ formData.accessory }}</span>
					<span class="axis-badge badge-print">{{ formData.print_type }}</span>
					<span v-if="formData.print_type !== 'Không in'" class="axis-badge badge-cylinder">{{ formData.cylinder_status }}</span>
				</div>

				<!-- KHỐI QUY CÁCH KỸ THUẬT CHO GIÁM ĐỐC RA QUYẾT ĐỊNH -->
				<div class="spec-box">
					<!-- LINE 3: Mô tả sản phẩm -->
					<div class="spec-line">
						<span class="spec-icon">📦</span>
						<span class="spec-desc-text">{{ formData.description || 'Chưa có mô tả sản phẩm' }}</span>
					</div>

					<!-- LINE 4: Kích thước biên dịch đầy đủ nhãn & đơn vị đo -->
					<div class="spec-line">
						<span class="spec-icon">📐</span>
						<span class="spec-dim-text">{{ compiledDimensions }}</span>
					</div>

					<!-- LINE 5: 8 Chip chất liệu chia 4 nhóm có vạch ngăn cách -->
					<div class="mat-chips-wrap">
						<!-- Nhóm 1: Màng in (Blue) -->
						<div class="mat-group">
							<button
								type="button"
								class="mat-chip chip-blue"
								:class="{ on: isMaterialSelected('OPP') }"
								@click="toggleMaterial('OPP')"
							>
								OPP
							</button>
							<button
								type="button"
								class="mat-chip chip-blue"
								:class="{ on: isMaterialSelected('PET') }"
								@click="toggleMaterial('PET')"
							>
								PET
							</button>
						</div>

						<div class="mat-divider"></div>

						<!-- Nhóm 2: Màng cản (Amber) -->
						<div class="mat-group">
							<button
								type="button"
								class="mat-chip chip-amber"
								:class="{ on: isMaterialSelected('AL') }"
								@click="toggleMaterial('AL')"
							>
								AL
							</button>
							<button
								type="button"
								class="mat-chip chip-amber"
								:class="{ on: isMaterialSelected('MPET') }"
								@click="toggleMaterial('MPET')"
							>
								MPET
							</button>
						</div>

						<div class="mat-divider"></div>

						<!-- Nhóm 3: Màng dẻo PA (Purple) -->
						<div class="mat-group">
							<button
								type="button"
								class="mat-chip chip-purple"
								:class="{ on: isMaterialSelected('PA') }"
								@click="toggleMaterial('PA')"
							>
								PA
							</button>
						</div>

						<div class="mat-divider"></div>

						<!-- Nhóm 4: Màng hàn dán (Emerald) -->
						<div class="mat-group">
							<button
								type="button"
								class="mat-chip chip-emerald"
								:class="{ on: isMaterialSelected('PE') }"
								@click="toggleMaterial('PE')"
							>
								PE
							</button>
							<button
								type="button"
								class="mat-chip chip-emerald"
								:class="{ on: isMaterialSelected('CPP') }"
								@click="toggleMaterial('CPP')"
							>
								CPP
							</button>
							<button
								type="button"
								class="mat-chip chip-emerald"
								:class="{ on: isMaterialSelected('MCPP') }"
								@click="toggleMaterial('MCPP')"
							>
								MCPP
							</button>
						</div>
					</div>
				</div>
			</div>

			<!-- Body -->
			<div class="drawer-body">
				<!-- BẢNG DANH SÁCH MẪU IN -->
				<div class="items-head">
					<span class="section-label">Danh sách mẫu in</span>
					<button
						type="button"
						class="btn-sm-ghost"
						@click="addItemRow"
					>
						+ Thêm mẫu in
					</button>
				</div>

				<div class="items-container">
					<div
						v-for="(row, idx) in itemRows"
						:key="idx"
						class="item-row"
					>
						<input
							v-model="row.item_name"
							type="text"
							class="form-input"
							placeholder="Mẫu in"
							autocomplete="off"
							@input="onItemChange"
						/>
						<input
							v-model.number="row.qty"
							type="number"
							class="form-input no-spin text-center w-110"
							placeholder="Số lượng"
							@input="onItemChange"
						/>
						<input
							v-model.number="row.rate"
							type="number"
							class="form-input no-spin text-center w-120"
							placeholder="Giá chưa thuế"
							@input="onItemChange"
						/>
						<button
							v-if="itemRows.length > 1"
							type="button"
							class="btn-icon-del"
							title="Xóa dòng"
							@click="removeItemRow(idx)"
						>
							✕
						</button>
					</div>
				</div>

				<!-- Dòng Trục in (nếu Chưa có trục) -->
				<div v-if="needCylinder" class="cylinder-row">
					<div class="cyl-label-wrap">
						<span class="badge-cyl-tag">TRỤC IN</span>
						<span class="cyl-title">Trục in (1 màu = 1 cây)</span>
					</div>
					<input
						v-model.number="cylinderQty"
						type="number"
						class="form-input no-spin text-center w-110"
						placeholder="Số cây"
						@input="onItemChange"
					/>
					<input
						:value="cylinderRateDisplay"
						type="text"
						class="form-input text-center w-120 read-only"
						placeholder="Giá chưa thuế"
						readonly
					/>
				</div>

				<!-- KHỐI ẢNH THIẾT KẾ & TỔNG TIỀN (BỐ CỤC 2 CỘT .fin-section CHUẨN) -->
				<div class="fin-section">
					<!-- Cột trái: Khung ảnh maquette 135px -->
					<ArtworkBox v-model="artworkUrl" @update:modelValue="onItemChange" />

					<!-- Cột phải: Khối tài chính (render số server trả) -->
					<div class="fin-cols">
						<div class="fin-row">
							<span class="fin-label">Tổng số lượng</span>
							<span class="fin-val font-bold">{{ previewFigures.total_qty || '0' }} {{ isRoll ? 'm' : 'Túi' }}</span>
						</div>
						<div class="fin-row">
							<span class="fin-label">Tiền hàng (chưa thuế)</span>
							<span class="fin-val font-bold">{{ previewFigures.subtotal || '0 đ' }}</span>
						</div>
						<div v-if="needCylinder" class="fin-row">
							<span class="fin-label">Tiền trục in</span>
							<span class="fin-val font-bold">{{ previewFigures.cylinder_total || '0 đ' }}</span>
						</div>
						<div class="fin-row">
							<span class="fin-label">Thuế (8%)</span>
							<span class="fin-val">{{ previewFigures.tax_amount || '0 đ' }}</span>
						</div>
						<div class="fin-divider"></div>
						<div class="fin-row">
							<span class="fin-label-total">TỔNG THANH TOÁN</span>
							<span class="fin-val-total">{{ previewFigures.grand_total || '0 đ' }}</span>
						</div>
					</div>
				</div>
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
		</aside>
	</div>
</template>

<script setup>
import { ref, computed } from 'vue';
import ArtworkBox from './ArtworkBox.vue';

const props = defineProps({
	formData: {
		type: Object,
		required: true,
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
});

const emit = defineEmits(['close', 'back', 'submit', 'itemsChanged']);

const isRoll = computed(() => props.formData.product_type === 'Cuộn màng ghép');
const needCylinder = computed(() => props.formData.print_type === 'In trục' && props.formData.cylinder_status === 'Chưa có trục');

// M2 state — restored from App-held savedData so Quay lại không mất dữ liệu
const selectedMaterials = ref([...(props.savedData.materials || ['OPP', 'PE'])]);
const artworkUrl = ref(props.savedData.artwork_url || '');
const cylinderQty = ref(props.savedData.cylinder_qty ?? 1);
const cylinderRateDisplay = ref('Chờ báo giá');

// Print item rows
const itemRows = ref(
	(props.savedData.lines && props.savedData.lines.length
		? props.savedData.lines
		: [{ item_name: '', qty: '', rate: '' }]
	).map((r) => ({ item_name: r.item_name || '', qty: r.qty ?? '', rate: r.rate ?? '' })),
);

function isMaterialSelected(code) {
	return selectedMaterials.value.includes(code);
}

function toggleMaterial(code) {
	const idx = selectedMaterials.value.indexOf(code);
	if (idx > -1) {
		selectedMaterials.value.splice(idx, 1);
	} else {
		selectedMaterials.value.push(code);
	}
}

// Line 4 compiled dimensions with explicit units mm and mic
const compiledDimensions = computed(() => {
	const fd = props.formData;
	if (!fd.length && !fd.width && !fd.thickness) {
		return 'Chưa nhập kích thước kỹ thuật';
	}

	const lenPart = fd.length ? (isRoll.value ? `Khổ ${fd.length} mm` : `Dài ${fd.length} mm`) : 'Dài — mm';
	const widPart = fd.width ? `Rộng ${fd.width} mm` : 'Rộng — mm';
	const thickPart = fd.thickness ? `Dày ${fd.thickness} mic` : 'Dày — mic';

	if (fd.product_type === 'Túi 3 biên') {
		return `${lenPart}  ×  ${widPart}  ×  ${thickPart}`;
	}

	let botLabel = 'Đáy';
	if (fd.product_type === 'Túi xếp hông') botLabel = 'Hông';
	else if (fd.product_type === 'Túi 8 cạnh') botLabel = 'Đáy/Hông';

	const botPart = fd.bottom ? `${botLabel} ${fd.bottom} mm` : `${botLabel} — mm`;

	return `${lenPart}  ×  ${widPart}  ×  ${thickPart}  ×  ${botPart}`;
});

function addItemRow() {
	itemRows.value.push({ item_name: '', qty: '', rate: '' });
	onItemChange();
}

function removeItemRow(idx) {
	itemRows.value.splice(idx, 1);
	onItemChange();
}

function onItemChange() {
	emit('itemsChanged', {
		lines: itemRows.value.map((r) => ({ ...r })),
		materials: [...selectedMaterials.value],
		cylinder_qty: cylinderQty.value,
		artwork_url: artworkUrl.value,
	});
}

function onSubmit() {
	emit('submit', {
		...props.formData,
		lines: itemRows.value,
		materials: selectedMaterials.value,
		artwork_url: artworkUrl.value,
		cylinder_qty: cylinderQty.value,
	});
}
</script>

<style scoped>
.drawer-overlay {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.6);
	z-index: 90;
	display: flex;
	justify-content: flex-end;
}

.drawer-panel {
	width: 560px;
	max-width: 94vw;
	height: 100vh;
	background: #161b22;
	border-left: 1px solid #3a424e;
	box-shadow: -10px 0 30px rgba(0, 0, 0, 0.5);
	display: flex;
	flex-direction: column;
	overflow: hidden;
}

.drawer-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 14px 20px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.drawer-title {
	font-size: 16px;
	font-weight: 800;
	color: #eef1f6;
	margin: 0;
}

.btn-icon {
	background: transparent;
	border: none;
	color: #9da7b5;
	cursor: pointer;
	padding: 4px;
	border-radius: 6px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.btn-icon:hover {
	color: #eef1f6;
}

.drawer-top-summary {
	padding: 16px 20px 10px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.08);
	display: flex;
	flex-direction: column;
}

.cust-brand-bar {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 12px;
	margin-bottom: 12px;
	background: #1a1f27;
	border-radius: 10px;
	padding: 9px 14px;
	min-height: 40px;
	box-sizing: border-box;
}

.cust-info {
	display: flex;
	align-items: center;
	gap: 8px;
	min-width: 0;
	flex: 1;
}

.icon-building {
	font-size: 14px;
	flex-shrink: 0;
}

.cust-name {
	font-size: 15px;
	font-weight: 800;
	color: #eef1f6;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.brand-tag {
	font-size: 12.5px;
	font-weight: 700;
	color: #0284c7;
	background: rgba(2, 132, 199, 0.12);
	border: 1px solid rgba(2, 132, 199, 0.25);
	padding: 3px 10px;
	border-radius: 6px;
	white-space: nowrap;
	flex-shrink: 0;
}

.axis-badges {
	display: flex;
	gap: 8px;
	flex-wrap: wrap;
	margin-bottom: 14px;
}

.axis-badge {
	font-size: 12px;
	font-weight: 700;
	padding: 4px 10px;
	border-radius: 6px;
}

.badge-product {
	color: #38bdf8;
	background: rgba(56, 189, 248, 0.12);
	border: 1px solid rgba(56, 189, 248, 0.25);
}

.badge-accessory {
	color: #c084fc;
	background: rgba(192, 132, 252, 0.12);
	border: 1px solid rgba(192, 132, 252, 0.25);
}

.badge-print {
	color: #94a3b8;
	background: rgba(148, 163, 184, 0.12);
	border: 1px solid rgba(148, 163, 184, 0.25);
}

.badge-cylinder {
	color: #f59e0b;
	background: rgba(245, 158, 11, 0.12);
	border: 1px solid rgba(245, 158, 11, 0.25);
}

.spec-box {
	background: #1a1f27;
	border-radius: 12px;
	padding: 12px 14px;
	display: flex;
	flex-direction: column;
	gap: 10px;
}

.spec-line {
	display: flex;
	align-items: center;
	gap: 10px;
	background: #161b22;
	border: 1px solid rgba(255, 255, 255, 0.08);
	border-radius: 8px;
	padding: 8px 12px;
	min-height: 38px;
	box-sizing: border-box;
}

.spec-icon {
	font-size: 14px;
	flex-shrink: 0;
}

.spec-desc-text {
	font-size: 13px;
	font-weight: 700;
	color: #eef1f6;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.spec-dim-text {
	font-size: 13px;
	font-weight: 700;
	color: #eef1f6;
	letter-spacing: 0.01em;
	font-variant-numeric: tabular-nums;
}

.mat-chips-wrap {
	display: flex;
	gap: 6px;
	align-items: center;
	width: 100%;
	box-sizing: border-box;
}

.mat-group {
	display: flex;
	gap: 4px;
}

.mat-divider {
	width: 1px;
	height: 20px;
	background: rgba(255, 255, 255, 0.15);
	margin: 0 2px;
}

.mat-chip {
	font-family: inherit;
	font-size: 12px;
	font-weight: 700;
	padding: 5px 8px;
	border-radius: 6px;
	background: #161b22;
	border: 1px solid rgba(255, 255, 255, 0.08);
	color: #9da7b5;
	cursor: pointer;
	transition: all 0.15s;
}

.mat-chip.chip-blue.on {
	background: rgba(56, 189, 248, 0.18);
	border-color: #38bdf8;
	color: #38bdf8;
}

.mat-chip.chip-amber.on {
	background: rgba(245, 158, 11, 0.18);
	border-color: #f59e0b;
	color: #f59e0b;
}

.mat-chip.chip-purple.on {
	background: rgba(192, 132, 252, 0.18);
	border-color: #c084fc;
	color: #c084fc;
}

.mat-chip.chip-emerald.on {
	background: rgba(52, 211, 153, 0.18);
	border-color: #34d399;
	color: #34d399;
}

.drawer-body {
	padding: 14px 20px;
	overflow-y: auto;
	flex: 1;
}

.items-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 8px;
}

.section-label {
	font-size: 12px;
	font-weight: 800;
	text-transform: uppercase;
	letter-spacing: 0.04em;
	color: #9da7b5;
}

.btn-sm-ghost {
	background: #1a1f27;
	border: 1px solid #3a424e;
	border-radius: 6px;
	font-size: 12px;
	font-weight: 600;
	color: #eef1f6;
	padding: 4px 10px;
	cursor: pointer;
}

.items-container {
	display: flex;
	flex-direction: column;
	gap: 8px;
	margin-bottom: 12px;
}

.item-row {
	display: flex;
	gap: 8px;
	align-items: center;
}

.form-input {
	height: 36px;
	padding: 0 10px;
	background: #1a1f27;
	border: 1px solid #3a424e;
	border-radius: 8px;
	color: #eef1f6;
	font-size: 13px;
	font-family: inherit;
	box-sizing: border-box;
	outline: none;
	flex: 1;
}

.form-input:focus {
	border-color: #4ea1e0;
}

.form-input::placeholder {
	color: #64748b;
	font-size: 12.5px;
}

.w-110 {
	flex: 0 0 110px;
	width: 110px;
}

.w-120 {
	flex: 0 0 120px;
	width: 120px;
}

.text-center {
	text-align: center;
	font-weight: 700;
}

.read-only {
	background: #12151a;
	color: #9da7b5;
	cursor: not-allowed;
}

.btn-icon-del {
	background: transparent;
	border: none;
	color: #f97066;
	cursor: pointer;
	font-size: 13px;
	padding: 4px 6px;
}

.cylinder-row {
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 8px 0;
	border-bottom: 1px solid rgba(255, 255, 255, 0.08);
	margin-bottom: 12px;
}

.cyl-label-wrap {
	flex: 1;
	display: flex;
	align-items: center;
	height: 36px;
	padding: 0 10px;
	background: rgba(245, 158, 11, 0.08);
	border: 1px solid rgba(245, 158, 11, 0.25);
	border-radius: 8px;
	gap: 8px;
}

.badge-cyl-tag {
	font-size: 10px;
	font-weight: 800;
	color: #f59e0b;
	background: rgba(245, 158, 11, 0.15);
	padding: 2px 6px;
	border-radius: 4px;
}

.cyl-title {
	font-size: 12px;
	font-weight: 700;
	color: #eef1f6;
}

/* 2-Column Finance section */
.fin-section {
	display: flex;
	gap: 16px;
	align-items: stretch;
	margin-top: 14px;
}

.fin-cols {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.fin-row {
	display: flex;
	justify-content: space-between;
	align-items: baseline;
}

.fin-label {
	font-size: 13px;
	color: #9da7b5;
}

.fin-val {
	font-size: 13.5px;
	color: #eef1f6;
	font-variant-numeric: tabular-nums;
}

.font-bold {
	font-weight: 700;
}

.fin-divider {
	height: 1px;
	background: rgba(255, 255, 255, 0.08);
	margin: 4px 0 6px;
}

.fin-label-total {
	font-size: 13.5px;
	font-weight: 800;
	color: #eef1f6;
	text-transform: uppercase;
}

.fin-val-total {
	font-size: 18px;
	font-weight: 900;
	color: #4ea1e0;
	font-variant-numeric: tabular-nums;
	letter-spacing: -0.02em;
}

.drawer-footer {
	padding: 14px 20px;
	border-top: 1px solid rgba(255, 255, 255, 0.08);
	display: flex;
	gap: 12px;
}

.act-btn {
	height: 40px;
	padding: 0 18px;
	font-family: inherit;
	font-size: 14px;
	font-weight: 700;
	border-radius: 8px;
	cursor: pointer;
	border: none;
	transition: all 0.15s;
}

.btn-sec {
	background: transparent;
	border: 1px solid #3a424e;
	color: #9da7b5;
	min-width: 120px;
}

.btn-sec:hover {
	color: #eef1f6;
	border-color: rgba(255, 255, 255, 0.2);
}

.btn-pri {
	background: #4ea1e0;
	color: #ffffff;
	flex: 1;
}

.btn-pri:hover {
	background: #3b8ac4;
}

.no-spin::-webkit-inner-spin-button,
.no-spin::-webkit-outer-spin-button {
	-webkit-appearance: none;
	margin: 0;
}
</style>
