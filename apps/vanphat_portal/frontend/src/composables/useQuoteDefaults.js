import { ref } from 'vue';
import { api } from './useSession';

/**
 * S2: mapping label Việt → pouch_key kỹ thuật (backend compute_pouch_area)
 * + defaults config-native từ get_product_groups/get_print_config.
 * DB trống → list rỗng truthful, form bắt chọn (không default cứng).
 */
const POUCH_KEY_MAP = [
	{ match: ['3 biên', '3 bien', 'three'], key: '3_bien' },
	{ match: ['xếp hông', 'xep hong', 'gusset', 'hàn lưng', 'han lung'], key: 'xep_hong' },
	{ match: ['8 cạnh', '8 canh', 'flat'], key: '8_canh' },
	{ match: ['đáy đứng', 'day dung', 'doypack', 'đứng'], key: 'day_dung_co_voi' },
];

export function pouchKeyOf(label) {
	const s = String(label || '').toLowerCase();
	for (const m of POUCH_KEY_MAP) {
		if (m.match.some((k) => s.includes(k))) return m.key;
	}
	// Backend default cũng là Doypack — trả rỗng để backend quyết, không bịa key.
	return s.trim() ? 'day_dung_co_voi' : '';
}

export function useQuoteDefaults() {
	const productTypes = ref([]);
	const printTechs = ref([]);
	const accessories = ref([]);
	const loaded = ref(false);

	async function load() {
		if (loaded.value) return;
		try {
			const [groups, printCfg] = await Promise.all([
				api('item.get_product_groups', {}, { get: true, silent: true }),
				api('item.get_print_config', {}, { get: true, silent: true }),
			]);
			const rows = (groups && Array.isArray(groups.product_groups) && groups.product_groups) || [];
			// Chỉ nhóm túi màng ghép (có pouch mapping) làm loại túi báo giá.
			productTypes.value = rows
				.filter((g) => ['tui_mang_ghep', 'tui_ngcs'].includes(g.key) && (g.count ?? 0) > 0)
				.map((g) => g.label);
			printTechs.value = (printCfg && Array.isArray(printCfg.print_techs) && printCfg.print_techs) || [];
			accessories.value = (printCfg && Array.isArray(printCfg.accessories) && printCfg.accessories) || [];
		} catch (e) {
			productTypes.value = [];
			printTechs.value = [];
			accessories.value = [];
		}
		loaded.value = true;
	}

	return { productTypes, printTechs, accessories, loaded, loadQuoteDefaults: load, pouchKeyOf };
}
