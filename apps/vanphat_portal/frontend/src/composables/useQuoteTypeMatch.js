/**
 * Task 4/5 review: MỘT matcher loại túi dùng chung cho Step 1 + Step 2.
 * Desk đổi label (mục tiêu config-native) thì 2 step hiểu giống nhau.
 *
 * Không substring mù: 'cuộn' chỉ match ở đầu label (loại "Cuộn ..."),
 * bỏ token 'kg' (reviewer bắt false-positive 'Túi 25kg' → cuộn).
 */
const ROLL_KEYS = ['cuộn', 'roll'];
const NO_PRINT_KEYS = ['không in', 'khong in', 'no print'];
const NO_BOTTOM_KEYS = ['3 biên', '3 bien', 'three'];

function norm(label) {
	return String(label || '').toLowerCase().trim();
}

function includesAny(label, keys) {
	const s = norm(label);
	return keys.some((k) => s.includes(k));
}

export function isRollLabel(label) {
	const s = norm(label);
	return ROLL_KEYS.some((k) => s === k || s.startsWith(k + ' ') || s.startsWith(k + '-'));
}

export function isNoPrintLabel(label) {
	return includesAny(label, NO_PRINT_KEYS);
}

export function isNoBottomLabel(label) {
	return includesAny(label, NO_BOTTOM_KEYS);
}

export const QUOTE_MATCH_DEFAULTS = {
	rollKeys: ROLL_KEYS,
	noPrintKeys: NO_PRINT_KEYS,
	noBottomKeys: NO_BOTTOM_KEYS,
};
