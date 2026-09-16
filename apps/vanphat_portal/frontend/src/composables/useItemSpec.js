/**
 * Spec kích thước mặt hàng — SSOT dùng chung bảng Catalog + drawer chi tiết.
 * Nguồn sự thật: Custom Field native (W = custom_pouch_width_mm, L = custom_pouch_length_mm,
 * dày = custom_thickness_mic, đáy = custom_gusset_mm, dao = custom_cut_length_mm).
 * Không logic tiền/config — chỉ chuỗi hiển thị.
 */
export function sizeTextOf(it) {
	if (!it) return '—';
	const w = Number(it.custom_pouch_width_mm) || 0;
	const l = Number(it.custom_pouch_length_mm) || 0;
	const thick = Number(it.custom_thickness_mic) || 0;
	if (w > 0 && l > 0) {
		if (thick > 0) return `R ${w} x D ${l} mm x ${thick} mic`;
		return `R ${w} x D ${l} mm`;
	}
	const rollW = Number(it.custom_film_width_mm) || 0;
	if (rollW > 0) {
		if (thick > 0) return `Khổ ${rollW} mm x ${thick} mic`;
		return `Khổ ${rollW} mm`;
	}
	const cylL = Number(it.custom_cylinder_length_mm) || 0;
	const cylC = Number(it.custom_cylinder_circ_mm) || 0;
	if (cylL > 0 || cylC > 0) return `Dài ${cylL} x CV ${cylC} mm`;
	return it.description || '—';
}

export function gussetTextOf(it) {
	if (!it) return null;
	const g = Number(it.custom_gusset_mm) || 0;
	if (g > 0) return `${g} mm`;
	return null;
}

/** Drawer 4 dòng đúng thứ tự Sếp chốt: Chất liệu · Kích thước · Dao cắt · Mã trục. */
export function detailLinesOf(it) {
	if (!it) return [];
	const lines = [];
	const layers = (it.custom_structure_layers || '').trim();
	if (layers) lines.push({ k: 'Chất liệu', v: layers, cls: 'text-primary' });
	const w = Number(it.custom_pouch_width_mm) || 0;
	const l = Number(it.custom_pouch_length_mm) || 0;
	const thick = Number(it.custom_thickness_mic) || 0;
	const g = Number(it.custom_gusset_mm) || 0;
	if (w > 0 && l > 0) {
		let size = `R ${w} x D ${l} mm`;
		if (thick > 0) size += ` x ${thick} mic`;
		if (g > 0) size += ` · Đáy ${g} mm`;
		lines.push({ k: 'Kích thước', v: size });
	} else {
		const rollW = Number(it.custom_film_width_mm) || 0;
		if (rollW > 0) {
			let size = `Khổ ${rollW} mm`;
			if (thick > 0) size += ` x ${thick} mic`;
			lines.push({ k: 'Kích thước', v: size });
		}
	}
	const cut = Number(it.custom_cut_length_mm) || 0;
	if (cut > 0) lines.push({ k: 'Dao cắt', v: `${cut} mm` });
	const cyl = it.custom_cylinder_item || it.custom_cylinder_code || '';
	if (cyl) lines.push({ k: 'Mã trục', v: cyl, cls: 'text-primary' });
	return lines;
}
