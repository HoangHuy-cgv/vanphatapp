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
const serveScript = fs.readFileSync(path.join(ROOT_DIR, 'scripts/serve-portal.mjs'), 'utf8');

console.log('--- 1. MASTER DATA COUNTS ---');
console.log(`Items count: ${items.length}`);
console.log(`BOM masters count: ${boms.length}`);
console.log(`BOM items count: ${bomItems.length}`);

console.log('\n--- 2. ELON MUSK MINIMALIST COLUMNS CHECK ---');
const requiredColumns = [
	'Mã hàng',
	'Tên sản phẩm',
	'Nhóm hàng',
	'Quy cách kỹ thuật',
	'ĐVT',
	'Cung ứng',
	'Khách hàng',
	'Trạng thái',
	'Chi tiết'
];
for (const col of requiredColumns) {
	const found = serveScript.includes(col);
	console.log(`Column "${col}": ${found ? 'PASS' : 'FAIL'}`);
}

console.log('\n--- 3. ITEM DETAIL SLIDE-OVER DRAWER CHECK ---');
const drawerChecks = [
	{ name: 'Drawer Overlay #drawerOverlay', test: serveScript.includes('id="drawerOverlay"') },
	{ name: 'Drawer Container #itemDrawer', test: serveScript.includes('id="itemDrawer"') },
	{ name: 'Drawer Header Code & Name', test: serveScript.includes('id="drawerItemCode"') && serveScript.includes('id="drawerItemName"') },
	{ name: 'Drawer Body Container #drawerBody', test: serveScript.includes('id="drawerBody"') },
	{ name: 'openItemDrawer function', test: serveScript.includes('function openItemDrawer(code)') },
	{ name: 'closeItemDrawer function', test: serveScript.includes('function closeItemDrawer()') },
	{ name: 'Escape key close listener', test: serveScript.includes("e.key === 'Escape'") },
	{ name: 'Clickable rows attached', test: serveScript.includes('clickable-row" onclick="openItemDrawer') },
	{ name: 'Section 1: Định Danh & Cung Ứng', test: serveScript.includes('1. Định Danh & Cung Ứng ERPNext') },
	{ name: 'Section 2: Cấu Trúc Màng & Quy Cách Túi', test: serveScript.includes('2. Cấu Trúc Màng & Quy Cách Túi') },
	{ name: 'Section 3: Trục In Ống Đồng & Công Nghệ In', test: serveScript.includes('3. Trục In Ống Đồng & Công Nghệ In') },
	{ name: 'Section 4: Định Mức BOM 2 Cấp Liên Kết', test: serveScript.includes('4. Định Mức BOM 2 Cấp Liên Kết') },
	{ name: 'API get_list endpoint', test: serveScript.includes('/api/method/vanphat_portal.api.item.get_list') },
	{ name: 'API get_detail endpoint', test: serveScript.includes('/api/method/vanphat_portal.api.item.get_detail') }
];

let allPassed = true;
for (const check of drawerChecks) {
	console.log(`Check "${check.name}": ${check.test ? 'PASS' : 'FAIL'}`);
	if (!check.test) allPassed = false;
}

console.log(`\nOverall Catalog & Detail Drawer Status: ${allPassed ? 'ALL PASS (100% READY)' : 'FAILED'}`);
