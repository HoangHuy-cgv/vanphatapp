import { ref, computed, watch } from 'vue';
import { useCockpitFormat } from './useCockpitFormat';
import { isRollLabel, isNoPrintLabel, isNoBottomLabel } from './useQuoteTypeMatch';

/**
 * S7c: M2 director form state (vật liệu, artwork, trục, dòng hàng).
 * Tách từ DrawerStep2Director.vue (935L) — view chỉ còn template + props/emit.
 * Client chỉ soạn dòng hàng thô; mọi tiền/thuế do backend preview (S1/S4).
 * Nhận diện loại dùng matcher chung với Step 1 (Desk đổi label vẫn khớp).
 */
export function useStep2DirectorForm(props, emit) {
	const { formatCurrency } = useCockpitFormat();

	const formData = computed(() => {
		if (props.formData && Object.keys(props.formData).length) return props.formData;
		return props.step1Data || {};
	});

	const isRoll = computed(() => isRollLabel(formData.value.product_type));
	// P1 review: badge trục hiện khi có in — boolean-prop thay vì so chuỗi trong template.
	const hasPrint = computed(() => {
		const p = formData.value.print_type || '';
		return p !== '' && !isNoPrintLabel(p);
	});
	const needCylinder = computed(() => formData.value.print_type === 'In trục' && formData.value.cylinder_status === 'Chưa có trục');

	// Triple rule 2: vật liệu từ cấu trúc màng native (BOM/layers của mã đang báo giá),
	// không chip cứng. Màu chip theo nhóm vật liệu (giữ chuẩn cockpit cũ).
	function matCls(code) {
		const m = (code || '').toUpperCase();
		if (m.includes('OPP') || m.includes('PET')) return 'chip-blue';
		if (m.includes('AL') || m.includes('MPET')) return 'chip-amber';
		if (m.includes('PA')) return 'chip-purple';
		return 'chip-emerald';
	}

	function splitLayers(raw) {
		if (Array.isArray(raw)) return raw.map((x) => String(x).trim()).filter(Boolean);
		return String(raw || '').split('/').map((x) => x.trim()).filter(Boolean);
	}

	const materialOptions = computed(() => {
		const saved = props.savedData.materials;
		const fromSaved = Array.isArray(saved) && saved.length ? saved : null;
		const fd = formData.value || {};
		const fromForm = fd.materials || fd.custom_structure_layers || fd.layers;
		const layers = fromSaved || splitLayers(fromForm);
		return layers.map((code) => ({ code, cls: matCls(code) }));
	});

	// M2 state — restored from App-held savedData so Quay lại không mất dữ liệu.
	// Triple rule 2: mặc định chọn hết lớp native (spec màng của mã đó); trống khi
	// native không có — người dùng click-chọn ở Drawer, không default cứng.
	const selectedMaterials = ref([
		...(props.savedData.materials && props.savedData.materials.length
			? props.savedData.materials
			: splitLayers(
				(props.step1Data || {}).materials
				|| (props.step1Data || {}).custom_structure_layers
				|| (props.step1Data || {}).layers
			)),
	]);
	const artworkUrl = ref(props.savedData.artwork_url || '');
	const cylinderQty = ref(props.savedData.cylinder_qty ?? 1);
	const cylinderRateDisplay = computed(() => {
		if (props.calculationResult?.cylinder_quote?.unit_price) {
			return formatCurrency(props.calculationResult.cylinder_quote.unit_price) + '/cây';
		}
		return 'Chờ giá NCC';
	});

	// Print item rows
	const itemRows = ref(
		(props.savedData.lines && props.savedData.lines.length
			? props.savedData.lines
			: [{ item_name: '', qty: '', rate: '' }]
		).map((r) => ({ item_name: r.item_name || '', qty: r.qty ?? '', rate: r.rate ?? '' })),
	);

	watch(
		() => props.savedData.lines,
		(newLines) => {
			if (newLines && newLines.length) {
				itemRows.value = newLines.map((r) => ({
					item_name: r.item_name || '',
					qty: r.qty ?? '',
					rate: r.rate ?? '',
				}));
			}
		},
		{ deep: true },
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
		onItemChange();
	}

	// Line 4 compiled dimensions with explicit units mm and mic
	const compiledDimensions = computed(() => {
		const fd = formData.value;
		if (!fd.length && !fd.width && !fd.thickness) {
			return 'Chưa nhập kích thước kỹ thuật';
		}

		const lenPart = fd.length ? (isRoll.value ? `Khổ ${fd.length} mm` : `Dài ${fd.length} mm`) : 'Dài — mm';
		const widPart = fd.width ? `Rộng ${fd.width} mm` : 'Rộng — mm';
		const thickPart = fd.thickness ? `Dày ${fd.thickness} mic` : 'Dày — mic';

		if (isNoBottomLabel(fd.product_type)) {
			return `${lenPart}  ×  ${widPart}  ×  ${thickPart}`;
		}

		const t = String(fd.product_type || '').toLowerCase();
		let botLabel = 'Đáy';
		if (t.includes('xếp hông') || t.includes('xep hong') || t.includes('gusset') || t.includes('hàn lưng')) botLabel = 'Hông';
		else if (t.includes('8 cạnh') || t.includes('8 canh') || t.includes('flat')) botLabel = 'Đáy/Hông';

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

	// Bridge cho children one-way (QuoteItemsTable/QuoteCylinderRow/QuoteFinanceArtwork):
	// child emit giá trị thô → cập nhật ref + phát itemsChanged như input trực tiếp.
	function onRowInput(idx, field, value) {
		const row = itemRows.value[idx];
		if (!row) return;
		row[field] = value;
		onItemChange();
	}

	function onCylinderQtyInput(value) {
		cylinderQty.value = value;
		onItemChange();
	}

	function onArtworkInput(value) {
		artworkUrl.value = value;
		onItemChange();
	}

	function onSubmit() {
		emit('submit', {
			...formData.value,
			lines: itemRows.value,
			materials: selectedMaterials.value,
			artwork_url: artworkUrl.value,
			cylinder_qty: cylinderQty.value,
		});
	}


	return {
		formatCurrency,
		formData,
		isRoll,
		hasPrint,
		needCylinder,
		materialOptions,
		selectedMaterials,
		artworkUrl,
		cylinderQty,
		cylinderRateDisplay,
		itemRows,
		isMaterialSelected,
		toggleMaterial,
		compiledDimensions,
		addItemRow,
		removeItemRow,
		onItemChange,
		onRowInput,
		onCylinderQtyInput,
		onArtworkInput,
		onSubmit,
	};
}
