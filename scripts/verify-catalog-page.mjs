import fs from 'fs';
import path from 'path';

const ROOT_DIR = process.cwd();
const CLEAN_DATA_DIR = path.join(ROOT_DIR, 'data/clean-data');

function parseCSV(content) {
	if (!content) return [];
	const lines = content.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
	if (lines.length < 2) return [];
	const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
	const rows = [];
	for (let i = 1; i < lines.length; i++) {
		const line = lines[i].trim();
		if (!line) continue;
		const values = [];
		let current = '';
		let inQuotes = false;
		for (let c = 0; c < line.length; c++) {
			const char = line[c];
			if (char === '"') {
				inQuotes = !inQuotes;
			} else if (char === ',' && !inQuotes) {
				values.push(current.trim());
				current = '';
			} else {
				current += char;
			}
		}
		values.push(current.trim());
		const obj = {};
		headers.forEach((h, idx) => {
			let val = values[idx] || '';
			if (val.startsWith('"') && val.endsWith('"')) {
				val = val.slice(1, -1).replace(/""/g, '"');
			}
			obj[h] = val;
		});
		rows.push(obj);
	}
	return rows;
}

const items = parseCSV(fs.readFileSync(path.join(CLEAN_DATA_DIR, 'item_master.csv'), 'utf8'));
const boms = parseCSV(fs.readFileSync(path.join(CLEAN_DATA_DIR, 'bom_master.csv'), 'utf8'));
const bomItems = parseCSV(fs.readFileSync(path.join(CLEAN_DATA_DIR, 'bom_items.csv'), 'utf8'));

const appVue = fs.readFileSync(path.join(ROOT_DIR, 'apps/vanphat_portal/frontend/src/App.vue'), 'utf8');
const catalogVuePath = path.join(ROOT_DIR, 'apps/vanphat_portal/frontend/src/views/CatalogView.vue');
const catalogVue = fs.existsSync(catalogVuePath) ? fs.readFileSync(catalogVuePath, 'utf8') : '';
const ordersVuePath = path.join(ROOT_DIR, 'apps/vanphat_portal/frontend/src/views/OrdersView.vue');
const ordersVue = fs.existsSync(ordersVuePath) ? fs.readFileSync(ordersVuePath, 'utf8') : '';
const portalCssPath = path.join(ROOT_DIR, 'apps/vanphat_portal/frontend/src/assets/portal.css');
const portalCss = fs.existsSync(portalCssPath) ? fs.readFileSync(portalCssPath, 'utf8') : '';
const portalSource = appVue + '\n' + catalogVue + '\n' + ordersVue + '\n' + portalCss;

const drawerVue = fs.readFileSync(path.join(ROOT_DIR, 'apps/vanphat_portal/frontend/src/components/DrawerItemDetail.vue'), 'utf8');
const pythonApi = fs.readFileSync(path.join(ROOT_DIR, 'apps/vanphat_portal/vanphat_portal/api/item.py'), 'utf8');
const serveScript = fs.readFileSync(path.join(ROOT_DIR, 'scripts/serve-portal.mjs'), 'utf8');

console.log('--- 1. MASTER DATA INTEGRITY ---');
console.log(`Items count: ${items.length}`);
console.log(`BOM masters count: ${boms.length}`);
console.log(`BOM items count: ${bomItems.length}`);

const navMenuMatch = appVue.match(/<nav class="nav-menu">([\s\S]*?)<\/nav>/);
const navMenu = navMenuMatch ? navMenuMatch[1] : '';

console.log('\n--- 2. SPA FIRST-CLASS VIEW & ELON MUSK COCKPIT CHECK ---');
const appChecks = [
	{ name: 'Sidebar native SPA button (no external a-tag)', test: (navMenu.includes("view = 'catalog'") || navMenu.includes("navigateTo('catalog')") || navMenu.includes("view = 'items'")) && !appVue.includes('href="/master-data"') },
	{ name: 'Sidebar unified button label is Danh mục', test: navMenu.includes('>Danh mục</span>') && navMenu.includes('catalogTotalCount') },
	{ name: 'Removed individual master data sidebar buttons', test: !navMenu.includes('>Mặt hàng</span>') && !navMenu.includes('>Khách hàng</span>') && !navMenu.includes('>Nhà cung cấp</span>') && !navMenu.includes('>Người dùng</span>') },
	{ name: 'View switching for unified catalog', test: appVue.includes("isCatalogView") },
	{ name: 'Single-line header with tabs and search', test: portalSource.includes('catalog-header-cockpit') && portalSource.includes('catalog-search-cockpit-wrap') },
	{ name: 'Exact 6 Master Catalog tab labels', test: portalSource.includes('<span>Sản phẩm</span>') && portalSource.includes('<span>Nguyên vật liệu</span>') && portalSource.includes('<span>Trục in</span>') && portalSource.includes('<span>Khách hàng</span>') && portalSource.includes('<span>Nhà cung cấp</span>') && portalSource.includes('<span>Người dùng</span>') },
	{ name: 'Instant search bar on same line with tabs', test: portalSource.includes('catalog-search-cockpit-wrap') && portalSource.includes('v-model="catalogSearchInput"') },
	{ name: 'Removed supply filter buttons (Xưởng SX, Mua ngoài)', test: !portalSource.includes('Tất cả cung ứng') && !portalSource.includes('itemSupplyFilter') },
	{ name: 'Table column: Mã sản phẩm', test: portalSource.includes('Mã sản phẩm') },
	{ name: 'Table column: Tên sản phẩm', test: portalSource.includes('Tên sản phẩm') },
	{ name: 'Table uses short name only', test: portalSource.includes('it.custom_alias || it.item_name') },
	{ name: 'Table column: Khách hàng hidden from table', test: !portalSource.includes('<th style="width: 18%;">Khách hàng</th>') },
	{ name: 'Table column: Chất liệu (Single-line)', test: portalSource.includes('Chất liệu') && !portalSource.includes('it.custom_thickness_mic }} mic') },
	{ name: 'Table column: Kích thước (R x D x Dày)', test: portalSource.includes('Kích thước') && portalSource.includes('getItemDimensionsText') },
	{ name: 'Table column: Đáy riêng biệt (Gusset)', test: portalSource.includes('getItemGussetText') },
	{ name: 'Table column: ĐVT', test: portalSource.includes('ĐVT') },
	{ name: 'Hidden columns removed from table', test: !portalSource.includes('Nhóm hàng</th>') && !portalSource.includes('Cung ứng</th>') && !portalSource.includes('Giá niêm yết</th>') },
	{ name: 'Row click triggers openItemDetail', test: portalSource.includes('openItemDetail(it)') },
	{ name: 'DrawerItemDetail integration', test: portalSource.includes('<DrawerItemDetail') }
];

let allAppPassed = true;
for (const check of appChecks) {
	console.log(`App Check "${check.name}": ${check.test ? 'PASS' : 'FAIL'}`);
	if (!check.test) allAppPassed = false;
}

console.log('\n--- 3. DRAWER ITEM DETAIL SPECIFICATION CHECK (ELON MUSK MINIMALISM) ---');
const drawerChecks = [
	{ name: 'Drawer Overlay & Panel', test: drawerVue.includes('drawer-overlay') && drawerVue.includes('drawer-panel') },
	{ name: 'Keyboard Escape listener', test: drawerVue.includes("e.key === 'Escape'") },
	{ name: 'Minimalist identity header (item_code & standard_rate)', test: drawerVue.includes('item-code-badge') && drawerVue.includes('head-rate') },
	{ name: 'Packaging specs card (pills & layer badges)', test: drawerVue.includes('cockpit-card') && drawerVue.includes('spec-row-highlight') },
	{ name: '4 Layer Badges (Sky Blue / Amber / Purple / Emerald)', test: drawerVue.includes('badge-layer-print') && drawerVue.includes('badge-layer-barrier') && drawerVue.includes('badge-layer-pa') && drawerVue.includes('badge-layer-sealant') },
	{ name: 'Cylinder tooling strip without redundant labels', test: drawerVue.includes('tooling-strip') && drawerVue.includes('cylinderDimensions') && drawerVue.includes('Kho Vạn Phát') },
	{ name: 'Operational metrics strip (MOQ, safety stock, status)', test: drawerVue.includes('meta-strip') && drawerVue.includes('min_order_qty') },
	{ name: 'BOM 2-tier table', test: drawerVue.includes('bom-cockpit-block') && drawerVue.includes('bom-table') },
	{ name: 'Zero numbered section headings (Triệt tiêu 1., 2., 3., 4.)', test: !drawerVue.includes('1. ĐỊNH DANH') && !drawerVue.includes('2. CẤU TRÚC') && !drawerVue.includes('3. TRỤC IN') && !drawerVue.includes('4. ĐỊNH MỨC') },
	{ name: 'Zero tutorial prose', test: !drawerVue.includes('Không qua công đoạn sản xuất nội bộ') }
];

let allDrawerPassed = true;
for (const check of drawerChecks) {
	console.log(`Drawer Check "${check.name}": ${check.test ? 'PASS' : 'FAIL'}`);
	if (!check.test) allDrawerPassed = false;
}

console.log('\n--- 4. ENZY & 3-SIDE SEAL POUCH DIMENSION INTEGRITY CHECK ---');
const enzy900 = items.find(it => it.item_code === 'TP-00040');
const enzy450 = items.find(it => it.item_code === 'TP-00041');
const enzy220 = items.find(it => it.item_code === 'TP-00042');
const enzyRacCom = items.find(it => it.item_code === 'TP-00043');
const skxBean = items.find(it => it.item_code === 'TP-00039');
const topgiaMbtp = items.find(it => it.item_code === 'TP-00019');
const pouch888 = items.find(it => it.item_code === 'TP-00001');

const dimChecks = [
	{ name: 'TP-00040 Enzy 900g Gusset is 0 (Túi 3 biên)', test: enzy900 && enzy900.custom_gusset_mm === '0' && enzy900.custom_pouch_width_mm === '250' && enzy900.custom_pouch_length_mm === '300' },
	{ name: 'TP-00041 Enzy 450g Gusset is 0 (Túi 3 biên)', test: enzy450 && enzy450.custom_gusset_mm === '0' && enzy450.custom_pouch_width_mm === '200' && enzy450.custom_pouch_length_mm === '260' },
	{ name: 'TP-00042 Enzy 220g Gusset is 0 (Túi 3 biên)', test: enzy220 && enzy220.custom_gusset_mm === '0' && enzy220.custom_pouch_width_mm === '170' && enzy220.custom_pouch_length_mm === '220' },
	{ name: 'TP-00043 Enzy Rắc Cơm Gusset is 0 (Túi 3 biên)', test: enzyRacCom && enzyRacCom.custom_gusset_mm === '0' && enzyRacCom.custom_pouch_width_mm === '110' && enzyRacCom.custom_pouch_length_mm === '170' },
	{ name: 'TP-00039 SKX Đậu Nành Gusset is 0 (Túi phẳng)', test: skxBean && skxBean.custom_gusset_mm === '0' && skxBean.custom_pouch_width_mm === '160' && skxBean.custom_pouch_length_mm === '235' },
	{ name: 'TP-00019 TopGia MBTP Gusset is 0 (Màng bọc phẳng)', test: topgiaMbtp && topgiaMbtp.custom_gusset_mm === '0' && topgiaMbtp.custom_pouch_width_mm === '200' && topgiaMbtp.custom_pouch_length_mm === '300' },
	{ name: 'TP-00001 888 3.2Kg Gusset is 45 (Doypack đáy đứng có vòi)', test: pouch888 && pouch888.custom_gusset_mm === '45' && pouch888.custom_pouch_width_mm === '280' && pouch888.custom_pouch_length_mm === '340' }
];

let allDimPassed = true;
for (const check of dimChecks) {
	console.log(`Dimension Check "${check.name}": ${check.test ? 'PASS' : 'FAIL'}`);
	if (!check.test) allDimPassed = false;
}

console.log('\n--- 5. BACKEND APIS & REDIRECT CHECK ---');
const backendChecks = [
	{ name: 'Python Frappe API get_list', test: pythonApi.includes('def get_list(') },
	{ name: 'Python Frappe API get_detail', test: pythonApi.includes('def get_detail(') },
	{ name: 'Mock server item.get_list', test: serveScript.includes('/api/method/vanphat_portal.api.item.get_list') },
	{ name: 'Mock server item.get_detail', test: serveScript.includes('/api/method/vanphat_portal.api.item.get_detail') },
	{ name: 'Route /master-data 302 Redirect to /portal?view=items', test: serveScript.includes("Location: '/portal?view=items'") }
];

let allBackendPassed = true;
for (const check of backendChecks) {
	console.log(`Backend Check "${check.name}": ${check.test ? 'PASS' : 'FAIL'}`);
	if (!check.test) allBackendPassed = false;
}

console.log('\n--- 6. FILM STRUCTURE & MATERIAL NAMING STANDARD CHECK ---');
const doubleSlashItems = items.filter(it => it.custom_structure_layers && it.custom_structure_layers.includes('//'));
const pesItems = items.filter(it => it.custom_structure_layers && /\bPES\b/i.test(it.custom_structure_layers));
const lldpeItems = items.filter(it => it.custom_structure_layers && /\bLLDPE\b/i.test(it.custom_structure_layers));
const barePeItems = items.filter(it => it.custom_structure_layers && it.custom_structure_layers.endsWith('/PE'));

const materialChecks = [
	{ name: 'Zero items containing "//" delimiter in structure layers', test: doubleSlashItems.length === 0 },
	{ name: 'Zero items containing "PES" (must be "PE sữa")', test: pesItems.length === 0 },
	{ name: 'Zero items containing "LLDPE" (must be "PE trong")', test: lldpeItems.length === 0 },
	{ name: 'Zero items ending with bare "/PE" without sữa/trong qualifier', test: barePeItems.length === 0 }
];

let allMaterialPassed = true;
for (const check of materialChecks) {
	console.log(`Material Check "${check.name}": ${check.test ? 'PASS' : 'FAIL'}`);
	if (!check.test) allMaterialPassed = false;
}

console.log('\n--- 7. FIXED COCKPIT & STICKY HEADER CHECK ---');
const stickyChecks = [
	{ name: 'Fixed viewport layout (portal-layout height: 100vh)', test: portalSource.includes('height: 100vh') && portalSource.includes('.portal-layout') },
	{ name: 'Fixed header with flex-shrink: 0 (catalog-header-cockpit)', test: portalSource.includes('.catalog-header-cockpit') && portalSource.includes('flex-shrink: 0') },
	{ name: 'Scrollable table-container (overflow-y: auto)', test: portalSource.includes('.table-container') && portalSource.includes('overflow-y: auto') },
	{ name: 'Sticky table header th (position: sticky; top: 0)', test: portalSource.includes('.data-table th') && portalSource.includes('position: sticky') && portalSource.includes('top: 0') }
];

let allStickyPassed = true;
for (const check of stickyChecks) {
	console.log(`Sticky Check "${check.name}": ${check.test ? 'PASS' : 'FAIL'}`);
	if (!check.test) allStickyPassed = false;
}

console.log('\n--- 8. SHORT ALIAS ENFORCEMENT & ZERO VERBOSE LEGAL NAMES IN UI ---');
const aliasEmptyBoms = bomItems.filter(bi => !bi.custom_alias || !bi.custom_alias.trim());
const verboseAliasBoms = bomItems.filter(bi =>
	bi.custom_alias && (
		bi.custom_alias.startsWith('Cuộn màng PET in ống đồng') ||
		bi.custom_alias.startsWith('Dung môi công nghiệp') ||
		bi.custom_alias.startsWith('Keo ghép màng Polyurethane') ||
		bi.custom_alias.startsWith('Chất đóng rắn keo ghép')
	)
);

const aliasChecks = [
	{ name: 'Drawer BOM table prioritizes bi.custom_alias over legal item_name', test: drawerVue.includes('bi.custom_alias') },
	{ name: 'Zero legal name duplication in Drawer hero-sub', test: !drawerVue.includes('hero-sub') },
	{ name: '100% BOM item rows in CSV have non-empty custom_alias', test: aliasEmptyBoms.length === 0 },
	{ name: 'Zero verbose legal prefixes in BOM custom_alias (PET in, Keo D-9700, Dung Môi EA)', test: verboseAliasBoms.length === 0 },
	{ name: 'Orders table prioritizes custom_alias', test: portalSource.includes('o.custom_alias') },
	{ name: 'ModalCreateOrder prioritizes custom_alias in item dropdowns', test: fs.readFileSync(path.join(ROOT_DIR, 'apps/vanphat_portal/frontend/src/components/ModalCreateOrder.vue'), 'utf8').includes('item.custom_alias') }
];

let allAliasPassed = true;
for (const check of aliasChecks) {
	console.log(`Alias Check "${check.name}": ${check.test ? 'PASS' : 'FAIL'}`);
	if (!check.test) allAliasPassed = false;
}

console.log('\n--- 9. BOM TABLE ALIGNMENT CHECK (MÉP PHẢI ĐỊNH MỨC & ĐƠN GIÁ) ---');
const alignmentChecks = [
	{ name: 'Drawer BOM table header Định mức has class text-right', test: drawerVue.includes('<th class="text-right" style="width: 17%;">Định mức</th>') },
	{ name: 'Drawer BOM table header Đơn giá has class text-right', test: drawerVue.includes('<th class="text-right" style="width: 17%;">Đơn giá</th>') },
	{ name: 'Drawer BOM table body td Định mức has class text-right', test: drawerVue.includes('td class="text-right font-bold text-num text-sm"') },
	{ name: 'Drawer BOM table body td Đơn giá has class text-right', test: drawerVue.includes('td class="text-right text-num text-secondary text-sm"') },
	{ name: 'Drawer scoped styles define .text-right { text-align: right; }', test: drawerVue.includes('.text-right { text-align: right; }') },
	{ name: 'Drawer scoped styles enforce .bom-table th.text-right, .bom-table td.text-right', test: drawerVue.includes('.bom-table th.text-right') && drawerVue.includes('.bom-table td.text-right') }
];

let allAlignmentPassed = true;
for (const check of alignmentChecks) {
	console.log(`Alignment Check "${check.name}": ${check.test ? 'PASS' : 'FAIL'}`);
	if (!check.test) allAlignmentPassed = false;
}

console.log('\n--- 10. CYLINDER TITLE PURITY CHECK (KHÔNG LẶP LẠI MÃ TRỤC TRONG TÊN) ---');
const cylinderItems = items.filter(it => it.item_code.startsWith('TRUC-'));
const cylindersWithCodeInAlias = cylinderItems.filter(it => /\([GZE]\d+/.test(it.custom_alias));
const cylindersWithCodeInName = cylinderItems.filter(it => /\([GZE]\d+/.test(it.item_name));

const cylinderPurityChecks = [
	{ name: '100% 157 cylinder items do NOT contain bracketed cylinder code in custom_alias', test: cylindersWithCodeInAlias.length === 0 },
	{ name: '100% 157 cylinder items do NOT contain bracketed cylinder code in item_name', test: cylindersWithCodeInName.length === 0 },
	{ name: 'TRUC-G4006940 distinctive fragrance alias "Trục 888 3.2Kg Hương Phấn Thơm Hồng"', test: items.some(it => it.item_code === 'TRUC-G4006940' && it.custom_alias === 'Trục 888 3.2Kg Hương Phấn Thơm Hồng') },
	{ name: 'TRUC-G4010806 clean alias "Trục Sachpoong 3.2Kg"', test: items.some(it => it.item_code === 'TRUC-G4010806' && it.custom_alias === 'Trục Sachpoong 3.2Kg') }
];

let allCylPurityPassed = true;
for (const check of cylinderPurityChecks) {
	console.log(`Cylinder Check "${check.name}": ${check.test ? 'PASS' : 'FAIL'}`);
	if (!check.test) allCylPurityPassed = false;
}

console.log('\n--- 11. MASTER DATA VIEWS & NAVIGATION CHECK (SẢN PHẨM GỘP, KHÁCH HÀNG, NCC, NGƯỜI DÙNG) ---');
const customerVueExists = fs.existsSync(path.join(ROOT_DIR, 'apps/vanphat_portal/frontend/src/components/DrawerCustomerDetail.vue'));
const supplierVueExists = fs.existsSync(path.join(ROOT_DIR, 'apps/vanphat_portal/frontend/src/components/DrawerSupplierDetail.vue'));
const userVueExists = fs.existsSync(path.join(ROOT_DIR, 'apps/vanphat_portal/frontend/src/components/DrawerUserDetail.vue'));

const customerApiExists = fs.existsSync(path.join(ROOT_DIR, 'apps/vanphat_portal/vanphat_portal/api/customer.py'));
const supplierApiExists = fs.existsSync(path.join(ROOT_DIR, 'apps/vanphat_portal/vanphat_portal/api/supplier.py'));
const userApiExists = fs.existsSync(path.join(ROOT_DIR, 'apps/vanphat_portal/vanphat_portal/api/user.py'));

const masterDataChecks = [
	{ name: 'Sidebar has single unified Danh mục button', test: appVue.includes("isCatalogView") && appVue.includes('>Danh mục</span>') },
	{ name: 'Unified 6-tab cockpit (SP, NVL, Trục, KH, NCC, User)', test: portalSource.includes("activeCatalogTab === 'sp'") && portalSource.includes("activeCatalogTab === 'kh'") && portalSource.includes("activeCatalogTab === 'ncc'") && portalSource.includes("activeCatalogTab === 'user'") },
	{ name: 'Sub-filter chips for Sản phẩm (Tất cả, Túi ghép, NGCS, Cuộn màng, Màng đơn)', test: portalSource.includes('sub-filter-chips') && portalSource.includes("activeProductSubFilter === 'tp'") },
	{ name: 'Customer table with credit limit and alias inside catalog', test: portalSource.includes("activeCatalogTab === 'kh'") && portalSource.includes('c.credit_limit') },
	{ name: 'Supplier table with tax ID and group inside catalog', test: portalSource.includes("activeCatalogTab === 'ncc'") && portalSource.includes('s.tax_id') },
	{ name: 'User table with ERPNext native roles inside catalog', test: portalSource.includes("activeCatalogTab === 'user'") && portalSource.includes('u.role_profile_name') },
	{ name: 'DrawerCustomerDetail component created & integrated', test: customerVueExists && portalSource.includes('<DrawerCustomerDetail') },
	{ name: 'DrawerSupplierDetail component created & integrated', test: supplierVueExists && portalSource.includes('<DrawerSupplierDetail') },
	{ name: 'DrawerUserDetail component created & integrated', test: userVueExists && portalSource.includes('<DrawerUserDetail') },
	{ name: 'Backend API customer.py created', test: customerApiExists },
	{ name: 'Backend API supplier.py created', test: supplierApiExists },
	{ name: 'Backend API user.py created', test: userApiExists }
];

let allMasterDataPassed = true;
for (const check of masterDataChecks) {
	console.log(`Master Data Check "${check.name}": ${check.test ? 'PASS' : 'FAIL'}`);
	if (!check.test) allMasterDataPassed = false;
}

console.log('\n--- 12. CATALOG TABLE REFINEMENT: SINGLE-LINE HEADERS, KH & NCC RESTRUCTURING, USER PHONE LOGIN ---');
const refinementChecks = [
	{ name: 'Single-line header locking (nowrap, overflow hidden, ellipsis, user-select none)', test: portalSource.includes('white-space: nowrap !important') && portalSource.includes('text-overflow: ellipsis') && portalSource.includes('user-select: none') },
	{ name: 'Customer table has Tax ID column and c.tax_id rendering', test: catalogVue.includes('Mã số thuế') && catalogVue.includes('c.tax_id') },
	{ name: 'Customer table has Payment Terms column and c.payment_terms rendering', test: catalogVue.includes('Thanh toán') && catalogVue.includes('c.payment_terms') },
	{ name: 'Customer code merged as subtle subtext under alias (no separate Mã KH column)', test: !catalogVue.includes('MÃ KHÁCH') && catalogVue.includes('Mã KH: ') },
	{ name: 'Supplier table has Tax ID and Payment Terms columns (s.tax_id, s.payment_terms)', test: catalogVue.includes('s.tax_id') && catalogVue.includes('s.payment_terms') },
	{ name: 'Supplier code merged as subtle subtext under alias (no separate Mã NCC column)', test: !catalogVue.includes('MÃ NCC') && catalogVue.includes('Mã NCC: ') },
	{ name: 'User table has SĐT đăng nhập column with mobile_no', test: catalogVue.includes('SĐT đăng nhập') && catalogVue.includes('u.mobile_no') },
	{ name: 'User table de-duplicated designation and roles into unified column', test: catalogVue.includes('Vai trò ERPNext') && !catalogVue.includes('EMAIL ĐĂNG NHẬP') },
	{ name: 'User table has Active/Inactive status column', test: catalogVue.includes('Trạng thái') && catalogVue.includes('badge-status-pill') }
];

let allRefinementPassed = true;
for (const check of refinementChecks) {
	console.log(`Refinement Check "${check.name}": ${check.test ? 'PASS' : 'FAIL'}`);
	if (!check.test) allRefinementPassed = false;
}

const totalChecksCount = appChecks.length + drawerChecks.length + dimChecks.length + backendChecks.length + materialChecks.length + stickyChecks.length + aliasChecks.length + alignmentChecks.length + cylinderPurityChecks.length + masterDataChecks.length + refinementChecks.length;
const finalStatus = allAppPassed && allDrawerPassed && allDimPassed && allBackendPassed && allMaterialPassed && allStickyPassed && allAliasPassed && allAlignmentPassed && allCylPurityPassed && allMasterDataPassed && allRefinementPassed;
console.log(`\n======================================================`);
console.log(`OVERALL STATUS: ${finalStatus ? `ALL ${totalChecksCount} CHECKS PASSED (100% READY)` : 'SOME CHECKS FAILED'}`);
console.log(`======================================================`);

if (!finalStatus) process.exit(1);



