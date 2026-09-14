import http from 'http';
import fs from 'fs';
import path from 'path';

const PORT = parseInt(process.env.PORT || '8080', 10);
const ROOT_DIR = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const CLEAN_DATA_DIR = path.join(ROOT_DIR, 'data/clean-data');
const DATA_DIR = path.join(ROOT_DIR, 'data');
const FRONTEND_DIR = path.join(ROOT_DIR, 'apps/vanphat_portal/vanphat_portal/public/frontend');
const PUBLIC_DIR = path.join(ROOT_DIR, 'apps/vanphat_portal/vanphat_portal/public');
const LOGIN_HTML = path.join(ROOT_DIR, 'apps/vanphat_portal/vanphat_portal/www/login.html');
const PORTAL_HTML = path.join(ROOT_DIR, 'apps/vanphat_portal/vanphat_portal/www/portal.html');
const PROTO_HTML = path.join(ROOT_DIR, 'appvanphat/preview-modal-step1.html');

const QUOTATIONS_FILE = path.join(DATA_DIR, 'local_quotations.json');
const ORDERS_FILE = path.join(DATA_DIR, 'local_orders.json');

// --- CSV Parser ---
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

function safeReadCSV(filename) {
	const p = path.join(CLEAN_DATA_DIR, filename);
	if (fs.existsSync(p)) {
		return parseCSV(fs.readFileSync(p, 'utf8'));
	}
	return [];
}

// --- Load Clean Datasets Nhóm A (Chỉ sử dụng 9 file CSV mới tạo trong session này) ---
const MASTER_ITEMS = safeReadCSV('item_master.csv');
const BOM_MASTERS = safeReadCSV('bom_master.csv');
const BOM_ITEMS = safeReadCSV('bom_items.csv');
const WAREHOUSES = safeReadCSV('warehouse_master.csv');
const SUPPLIERS = safeReadCSV('supplier_master.csv');
const OPERATIONS = safeReadCSV('operation_master.csv');
const WORKSTATIONS = safeReadCSV('workstation_master.csv');
const USERS = safeReadCSV('user_master.csv');
const CUSTOMERS_RAW = safeReadCSV('customer_master.csv');

// Build Unified Customers List from customer_master.csv (SSOT 100% ERPNext Native)
// Sếp chốt: phân loại Trả trước/Trả sau từ payment_terms, KHÔNG dùng credit_limit.
const UNIFIED_CUSTOMERS = CUSTOMERS_RAW.length > 0 ? CUSTOMERS_RAW.map(c => ({
	name: c.name,
	customer_name: c.customer_name,
	alias: c.alias,
	brand: c.alias || '',
	type: c.customer_group || '',
	customer_type: c.customer_type || 'Company',
	primary_address: c.primary_address || '',
	payment_terms: c.payment_terms || ''
})) : [];


// Build BOM grouped hierarchy
const BOM_TREE = new Map();
BOM_MASTERS.forEach(b => {
	BOM_TREE.set(b.bom_no, {
		master: b,
		items: []
	});
});
BOM_ITEMS.forEach(bi => {
	if (BOM_TREE.has(bi.bom_no)) {
		BOM_TREE.get(bi.bom_no).items.push(bi);
	}
});

// Seed quotations if not present
if (!fs.existsSync(QUOTATIONS_FILE)) {
	const initialQuotes = [
		{
			name: 'BG-2609-001',
			creation: '2026-09-12 14:30:00',
			transaction_date: '2026-09-12',
			party_name: 'CÔNG TY TNHH TM-DV HÓA MỸ PHẨM LÂM GIA',
			customer_name: 'CÔNG TY TNHH TM-DV HÓA MỸ PHẨM LÂM GIA',
			brand: 'SuperClean',
			rounded_total: 28450000,
			grand_total: 28450000,
			status: 'Draft',
			owner: 'giamdoc@vanphat.com'
		},
		{
			name: 'BG-2609-002',
			creation: '2026-09-12 10:15:00',
			transaction_date: '2026-09-12',
			party_name: 'CÔNG TY CP QUỐC TẾ VMT GROUP',
			customer_name: 'CÔNG TY CP QUỐC TẾ VMT GROUP',
			brand: 'NEMO',
			rounded_total: 45600000,
			grand_total: 45600000,
			status: 'Open',
			owner: 'sale@vanphat.com'
		},
		{
			name: 'BG-2609-003',
			creation: '2026-09-11 16:45:00',
			transaction_date: '2026-09-11',
			party_name: 'CÔNG TY TNHH SẢN XUẤT MỸ PHẨM AN NHIÊN',
			customer_name: 'CÔNG TY TNHH SẢN XUẤT MỸ PHẨM AN NHIÊN',
			brand: 'AN PERFUN',
			rounded_total: 15200000,
			grand_total: 15200000,
			status: 'Ordered',
			owner: 'sale@vanphat.com'
		}
	];
	fs.writeFileSync(QUOTATIONS_FILE, JSON.stringify(initialQuotes, null, 2), 'utf8');
}

if (!fs.existsSync(ORDERS_FILE)) {
	const initialOrders = [
		{
			name: 'DH-2609-001',
			transaction_date: '2026-09-11',
			customer_name: 'CÔNG TY TNHH SẢN XUẤT MỸ PHẨM AN NHIÊN',
			grand_total: 15200000,
			status: 'To Deliver and Bill'
		}
	];
	fs.writeFileSync(ORDERS_FILE, JSON.stringify(initialOrders, null, 2), 'utf8');
}

function getQuotations() {
	try {
		return JSON.parse(fs.readFileSync(QUOTATIONS_FILE, 'utf8'));
	} catch (e) {
		return [];
	}
}

function saveQuotations(quotes) {
	fs.writeFileSync(QUOTATIONS_FILE, JSON.stringify(quotes, null, 2), 'utf8');
}

function getOrders() {
	try {
		return JSON.parse(fs.readFileSync(ORDERS_FILE, 'utf8'));
	} catch (e) {
		return [];
	}
}

function saveOrders(orders) {
	fs.writeFileSync(ORDERS_FILE, JSON.stringify(orders, null, 2), 'utf8');
}

// --- HTTP Server ---
const server = http.createServer((req, res) => {
	const url = new URL(req.url, `http://127.0.0.1:${PORT}`);
	const pathname = url.pathname;

	// CORS headers
	res.setHeader('Access-Control-Allow-Origin', '*');
	res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
	res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Frappe-CSRF-Token');
	if (req.method === 'OPTIONS') {
		res.statusCode = 204;
		res.end();
		return;
	}

	// APIs
	if (pathname.startsWith('/api/method/') || req.method === 'POST') {
		let body = '';
		req.on('data', chunk => body += chunk);
		req.on('end', () => {
			res.setHeader('Content-Type', 'application/json');
			let parsed = {};
			try { parsed = JSON.parse(body); } catch (e) { void e; }
			for (const [k, v] of url.searchParams.entries()) {
				if (parsed[k] === undefined) parsed[k] = v;
			}

			// 1. Auth & Session
			if (pathname === '/api/method/login') {
				res.end(JSON.stringify({ message: 'Logged In' }));
				return;
			}
			if (pathname === '/api/method/logout') {
				res.end(JSON.stringify({ message: 'Logged Out' }));
				return;
			}
			if (pathname === '/api/method/vanphat_portal.api.bao_gia.get_boot') {
				res.end(JSON.stringify({
					message: {
						user: 'Administrator',
						csrf_token: 'mock_csrf_token',
						company: 'Công ty TNHH Bao Bì Vạn Phát',
						master_counts: {
							items: MASTER_ITEMS.length,
							specs: MASTER_ITEMS.length,
							boms: BOM_MASTERS.length,
							customers: UNIFIED_CUSTOMERS.length,
							warehouses: WAREHOUSES.length,
							suppliers: SUPPLIERS.length,
							operations: OPERATIONS.length,
							workstations: WORKSTATIONS.length,
							users: USERS.length
						}
					}
				}));
				return;
			}

			// 1.1 Item APIs: List Items (shape khớp item.py: {items,page,total_count,total_pages};
			// category sp/nvl/truc lọc prefix như backend Python)
			if (pathname === '/api/method/vanphat_portal.api.item.get_list') {
				const q = (parsed.query || '').trim().toLowerCase();
				const grp = (parsed.item_group || '').trim();
				const supply = (parsed.supply_type || '').trim();
				const cat = (parsed.category || '').trim().toLowerCase();
				const p = Math.max(1, Number(parsed.page) || 1);
				const pl = Math.min(100, Math.max(1, Number(parsed.page_length) || 15));
				let items = safeReadCSV('item_master.csv');
			// SPEC native 2026-09-15: mock tự join customer_items.csv → customer_code
			// (trên bench thật ERPNext tự join qua fill_customer_code).
			const ciRows = safeReadCSV('customer_items.csv');
			const ciMap = new Map(ciRows.map(r => [r.item_code, r]));
			items = items.map(it => {
				const ci = ciMap.get(it.item_code);
				return { ...it, customer_code: ci ? ci.ref_code : '', customer_items: ci ? [ci] : [] };
			});
				if (cat === 'sp') items = items.filter(it => it.item_code.startsWith('TP-'));
				else if (cat === 'nvl') items = items.filter(it => it.item_code.startsWith('NVL-'));
				else if (cat === 'truc') items = items.filter(it => it.item_code.startsWith('TRUC-'));
				if (grp) {
					items = items.filter(it => it.item_group === grp);
				}
				if (supply) {
					items = items.filter(it => it.default_material_request_type === supply);
				}
				if (q) {
					items = items.filter(it =>
						it.item_code.toLowerCase().includes(q) ||
						(it.item_name && it.item_name.toLowerCase().includes(q)) ||
						(it.custom_alias && it.custom_alias.toLowerCase().includes(q)) ||
						(it.customer_code && it.customer_code.toLowerCase().includes(q)) ||
						(it.custom_structure_layers && it.custom_structure_layers.toLowerCase().includes(q))
					);
				}
				const total = items.length;
				res.end(JSON.stringify({ message: {
					items: items.slice((p - 1) * pl, p * pl),
					page: p, page_length: pl,
					total_count: total,
					total_pages: Math.max(1, Math.ceil(total / pl)),
				} }));
				return;
			}

			// 1.2 Item APIs: Item Detail with Associated BOM
			if (pathname === '/api/method/vanphat_portal.api.item.get_detail') {
				const code = (parsed.item_code || '').trim();
				const currentItems = safeReadCSV('item_master.csv');
				const item = currentItems.find(it => it.item_code === code);
				if (!item) {
					res.statusCode = 404;
					res.end(JSON.stringify({ error: 'Item not found' }));
					return;
				}
				const itemAliasMap = new Map();
				currentItems.forEach(it => {
					itemAliasMap.set(it.item_code, it.custom_alias || it.item_name);
				});
				const currentBOMMasters = safeReadCSV('bom_master.csv');
				const currentBOMItems = safeReadCSV('bom_items.csv');
				const bomMaster = currentBOMMasters.find(b => b.item === code);
				let bom = null;
				if (bomMaster) {
					const items = currentBOMItems
						.filter(bi => bi.bom_no === bomMaster.bom_no)
						.map(bi => ({
							...bi,
							custom_alias: bi.custom_alias || itemAliasMap.get(bi.item_code) || bi.item_name
						}));
					bom = { master: bomMaster, items };
				}
				res.end(JSON.stringify({ message: { item, bom } }));
				return;
			}

			// 1.3 Customer APIs
			if (pathname === '/api/method/vanphat_portal.api.customer.get_list') {
				const q = (parsed.query || '').trim().toLowerCase();
				let custs = safeReadCSV('customer_master.csv');
				if (q) {
					custs = custs.filter(c =>
						(c.name && c.name.toLowerCase().includes(q)) ||
						(c.customer_name && c.customer_name.toLowerCase().includes(q)) ||
						(c.alias && c.alias.toLowerCase().includes(q)) ||
						(c.territory && c.territory.toLowerCase().includes(q)) ||
						(c.customer_group && c.customer_group.toLowerCase().includes(q))
					);
				}
				res.end(JSON.stringify({ message: custs }));
				return;
			}

			if (pathname === '/api/method/vanphat_portal.api.customer.get_detail') {
				const name = (parsed.name || '').trim();
				const custs = safeReadCSV('customer_master.csv');
				const found = custs.find(c => c.name === name || c.customer_name === name || c.alias === name);
				if (!found) {
					res.statusCode = 404;
					res.end(JSON.stringify({ error: 'Customer not found' }));
					return;
				}
				res.end(JSON.stringify({ message: found }));
				return;
			}

			// 1.4 Supplier APIs
			if (pathname === '/api/method/vanphat_portal.api.supplier.get_list') {
				const q = (parsed.query || '').trim().toLowerCase();
				const grp = (parsed.supplier_group || '').trim();
				let supps = safeReadCSV('supplier_master.csv');
				if (grp) {
					supps = supps.filter(s => s.supplier_group === grp);
				}
				if (q) {
					supps = supps.filter(s =>
						(s.name && s.name.toLowerCase().includes(q)) ||
						(s.supplier_name && s.supplier_name.toLowerCase().includes(q)) ||
						(s.alias && s.alias.toLowerCase().includes(q)) ||
						(s.supplier_group && s.supplier_group.toLowerCase().includes(q)) ||
						(s.tax_id && s.tax_id.toLowerCase().includes(q))
					);
				}
				res.end(JSON.stringify({ message: supps }));
				return;
			}

			if (pathname === '/api/method/vanphat_portal.api.supplier.get_detail') {
				const name = (parsed.name || '').trim();
				const supps = safeReadCSV('supplier_master.csv');
				const found = supps.find(s => s.name === name || s.supplier_name === name || s.alias === name);
				if (!found) {
					res.statusCode = 404;
					res.end(JSON.stringify({ error: 'Supplier not found' }));
					return;
				}
				res.end(JSON.stringify({ message: found }));
				return;
			}

			// 1.5 User APIs
			if (pathname === '/api/method/vanphat_portal.api.user.get_list') {
				const q = (parsed.query || '').trim().toLowerCase();
				const dept = (parsed.department || '').trim();
				let users = safeReadCSV('user_master.csv');
				if (dept) {
					users = users.filter(u => u.department === dept);
				}
				if (q) {
					users = users.filter(u =>
						(u.name && u.name.toLowerCase().includes(q)) ||
						(u.full_name && u.full_name.toLowerCase().includes(q)) ||
						(u.email && u.email.toLowerCase().includes(q)) ||
						(u.mobile_no && u.mobile_no.includes(q)) ||
						(u.department && u.department.toLowerCase().includes(q)) ||
						(u.designation && u.designation.toLowerCase().includes(q)) ||
						(u.role_profile_name && u.role_profile_name.toLowerCase().includes(q))
					);
				}
				res.end(JSON.stringify({ message: users }));
				return;
			}

			// 2. Customer Autocomplete from Master Data
			if (pathname === '/api/method/vanphat_portal.api.bao_gia.search_customers') {
				const q = (parsed.query || '').trim().toLowerCase();
				let matched = UNIFIED_CUSTOMERS;
				if (q) {
					matched = UNIFIED_CUSTOMERS.filter(c =>
						c.customer_name.toLowerCase().includes(q) ||
						(c.brand && c.brand.toLowerCase().includes(q))
					);
				}
				res.end(JSON.stringify({ message: matched.slice(0, 15) }));
				return;
			}

			// 3. List Quotations (shape khớp bao_gia.list_quotations: server paging + search)
			if (pathname === '/api/method/vanphat_portal.api.bao_gia.list_quotations') {
				const all = getQuotations();
				const q = (parsed.query || '').trim().toLowerCase();
				const p = Math.max(1, Number(parsed.page) || 1);
				const pl = Math.min(100, Math.max(1, Number(parsed.page_length) || 15));
				let filtered = all;
				if (q) {
					filtered = all.filter(o =>
						(o.name && o.name.toLowerCase().includes(q)) ||
						(o.customer_name && o.customer_name.toLowerCase().includes(q)) ||
						(o.party_name && o.party_name.toLowerCase().includes(q))
					);
				}
				const total = filtered.length;
				res.end(JSON.stringify({ message: {
					quotations: filtered.slice((p - 1) * pl, p * pl),
					page: p, page_length: pl,
					total_count: total,
					total_pages: Math.max(1, Math.ceil(total / pl)),
				} }));
				return;
			}

			// 4. Create Quotation (End-to-End Persistence)
			if (pathname === '/api/method/vanphat_portal.api.bao_gia.create_quotation') {
				const payload = parsed.payload || parsed;
				const quotes = getQuotations();
				const nextIndex = quotes.length + 1;
				const docCode = `BG-2609-${String(nextIndex).padStart(3, '0')}`;
				const now = new Date();
				const dateStr = now.toISOString().slice(0, 10);
				const timeStr = now.toTimeString().slice(0, 8);

				const rows = payload.lines || [];
				let linesSubtotal = 0;
				rows.forEach(r => {
					linesSubtotal += (Number(r.qty) || 0) * (Number(r.rate) || 0);
				});

				const isPrintCylinder = payload.print_type === 'In trục' && payload.cylinder_status === 'Chưa có trục';
				const cylQty = isPrintCylinder ? (Number(payload.cylinder_qty) || 1) : 0;
				const cylinderTotal = cylQty * 3500000;

				const grandTotal = Math.round((linesSubtotal + cylinderTotal) * 1.08);

				const newDoc = {
					name: docCode,
					creation: `${dateStr} ${timeStr}`,
					transaction_date: dateStr,
					party_name: payload.customer || 'Khách hàng mới',
					customer_name: payload.customer || 'Khách hàng mới',
					brand: payload.brand || '',
					product_type: payload.product_type || 'Túi đáy đứng',
					accessory: payload.accessory || 'Có vòi',
					print_type: payload.print_type || 'In trục',
					cylinder_status: payload.cylinder_status || 'Chưa có trục',
					dimensions: `${payload.width || 280} x ${payload.length || 340} + ${payload.bottom || 40} mm`,
					materials: payload.materials || ['PET', 'PE sữa'],
					cylinder_qty: cylQty,
					lines: rows,
					subtotal: linesSubtotal,
					cylinder_total: cylinderTotal,
					grand_total: grandTotal,
					rounded_total: grandTotal,
					status: 'Draft',
					owner: 'giamdoc@vanphat.com'
				};

				quotes.unshift(newDoc);
				saveQuotations(quotes);
				res.end(JSON.stringify({ message: newDoc }));
				return;
			}

			// 5. Submit Quotation (Gửi QLSX)
			if (pathname === '/api/method/vanphat_portal.api.bao_gia.submit_quotation') {
				const quotes = getQuotations();
				const doc = quotes.find(q => q.name === parsed.name);
				if (doc) {
					doc.status = 'Open';
					saveQuotations(quotes);
					res.end(JSON.stringify({ message: doc }));
				} else {
					res.statusCode = 404;
					res.end(JSON.stringify({ error: 'Quotation not found' }));
				}
				return;
			}

			// 6. Mark Lost (Rớt báo giá)
			if (pathname === '/api/method/vanphat_portal.api.bao_gia.mark_quotation_lost') {
				const quotes = getQuotations();
				const doc = quotes.find(q => q.name === parsed.name);
				if (doc) {
					doc.status = 'Lost';
					doc.lost_reason = parsed.reason || '';
					saveQuotations(quotes);
					res.end(JSON.stringify({ message: doc }));
				} else {
					res.statusCode = 404;
					res.end(JSON.stringify({ error: 'Quotation not found' }));
				}
				return;
			}

			// 7. Make Order from Quotation (Chốt đơn hàng)
			if (pathname === '/api/method/vanphat_portal.api.bao_gia.make_order_from_quotation') {
				const quotes = getQuotations();
				const orders = getOrders();
				const doc = quotes.find(q => q.name === parsed.name);
				if (doc) {
					doc.status = 'Ordered';
					saveQuotations(quotes);

					const nextSo = `DH-2609-${String(orders.length + 1).padStart(3, '0')}`;
					const now = new Date();
					const soDoc = {
						name: nextSo,
						quotation_ref: doc.name,
						transaction_date: now.toISOString().slice(0, 10),
						customer_name: doc.customer_name,
						grand_total: doc.grand_total,
						status: 'To Deliver and Bill'
					};
					orders.unshift(soDoc);
					saveOrders(orders);

					res.end(JSON.stringify({ message: { sales_order: nextSo } }));
				} else {
					res.statusCode = 404;
					res.end(JSON.stringify({ error: 'Quotation not found' }));
				}
				return;
			}

			// 8. List Orders (mock local; shape khớp order.list_orders cho OrdersView)
			// Frontend gọi vanphat_portal.api.order.list_orders (Order doc-driven);
			// mock alias cũ bao_gia.list_orders giữ tương thích.
			if (pathname === '/api/method/vanphat_portal.api.order.list_orders'
				|| pathname === '/api/method/vanphat_portal.api.bao_gia.list_orders') {
				const all = getOrders();
				const q = (parsed.query || '').trim().toLowerCase();
				const p = Math.max(1, Number(parsed.page) || 1);
				const pl = Math.min(100, Math.max(1, Number(parsed.page_length) || 15));
				let filtered = all;
				if (q) {
					filtered = all.filter(o =>
						(o.name && o.name.toLowerCase().includes(q)) ||
						(o.customer_name && o.customer_name.toLowerCase().includes(q))
					);
				}
				const total = filtered.length;
				const slice = filtered.slice((p - 1) * pl, p * pl);
				res.end(JSON.stringify({
					message: {
						orders: slice,
						total_count: total,
						total_pages: Math.max(1, Math.ceil(total / pl)),
						page: p,
						tab_counts: { all: all.length },
					}
				}));
				return;
			}

			// 9. Packaging Technical Calculation Engine (SSOT AGENTS.md)
			if (pathname === '/api/method/vanphat_portal.api.bao_gia.calculate_packaging_quotation') {
				const desired_qty = Number(parsed.desired_qty) || 5000;
				const width = Number(parsed.width_mm) || 280;
				const length = Number(parsed.length_mm) || 340;
				const cut_length_m = (length || 340) / 1000.0;
				const lanes = width <= 360 ? 2 : 1;
				const bags_per_roll = Math.floor((1500.0 * lanes * 0.92) / (cut_length_m || 0.34));
				const num_rolls = Math.max(1, Math.ceil(desired_qty / (bags_per_roll || 8000)));
				const q_opt = num_rolls * bags_per_roll;
				const q_surp = Math.max(0, q_opt - desired_qty);

				const isPrintCyl = parsed.print_type === 'In trục' && parsed.cylinder_status === 'Chưa có trục';
				const cyl_qty = isPrintCyl ? (Number(parsed.cylinder_qty) || 1) : 0;
				const opt_rate = 4965;
				const req_rate = desired_qty >= q_opt ? 4965 : 5258;

				res.end(JSON.stringify({
					message: {
						lanes,
						bags_per_roll,
						scenarios: {
							optimal_whole_roll: {
								rolls: num_rolls,
								qty: q_opt,
								rate: opt_rate,
								total: opt_rate * q_opt,
								label: `Tròn ${num_rolls} cuộn (${q_opt.toLocaleString()} túi) — ĐƠN GIÁ TỐT NHẤT`
							},
							requested_qty: {
								rolls_required: num_rolls,
								qty: desired_qty,
								surplus_bags_warehouse: q_surp,
								rate: req_rate,
								total: req_rate * desired_qty,
								label: `Đúng số lượng yêu cầu (${desired_qty.toLocaleString()} túi) — ĐƠN GIÁ CAO HƠN`
							}
						},
						cylinder_quote: {
							qty: cyl_qty,
							unit_price: 3500000,
							total: cyl_qty * 3500000
						},
						upsell_recommendation: {
							extra_cost_to_get_full_batch: Math.max(0, opt_rate * q_opt - req_rate * desired_qty),
							extra_bags_received: q_surp,
							unit_price_savings: Math.max(0, req_rate - opt_rate),
							pitch: `Khách chỉ cần thêm ${(Math.max(0, opt_rate * q_opt - req_rate * desired_qty)).toLocaleString()} đ là nhận thêm trọn vẹn ${q_surp.toLocaleString()} túi với đơn giá rẻ hơn ${Math.max(0, req_rate - opt_rate).toLocaleString()} đ/túi!`
						}
					}
				}));
				return;
			}

			// 10. Price Preview
			if (pathname === '/api/method/vanphat_portal.api.bao_gia.get_price_preview') {
				const rows = parsed.lines || [];
				let total_qty = 0;
				let subtotal = 0;
				for (const r of rows) {
					const q = Number(r.qty) || 0;
					const rt = Number(r.rate) || 0;
					total_qty += q;
					subtotal += q * rt;
				}
				res.end(JSON.stringify({
					message: {
						total_qty,
						subtotal,
						cylinder_total: 0,
						tax_amount: Math.round(subtotal * 0.08),
						grand_total: Math.round(subtotal * 1.08)
					}
				}));
				return;
			}

			res.statusCode = 404;
			res.end(JSON.stringify({ error: 'Not Found' }));
		});
		return;
	}

	// --- Pages & UI Routing ---

	// Main Portal Page
	if (pathname === '/' || pathname === '/portal') {
		res.setHeader('Content-Type', 'text/html; charset=utf-8');
		res.end(fs.readFileSync(PORTAL_HTML));
		return;
	}

	// Login Page
	if (pathname === '/login') {
		res.setHeader('Content-Type', 'text/html; charset=utf-8');
		res.end(fs.readFileSync(LOGIN_HTML));
		return;
	}

	// Prototype Preview
	if (pathname === '/preview' || pathname === '/preview-modal-step1.html') {
		res.setHeader('Content-Type', 'text/html; charset=utf-8');
		res.end(fs.readFileSync(PROTO_HTML));
		return;
	}

	// Master Data: Redirect seamlessly to integrated SPA cockpit
	if (pathname === '/master-data' || pathname === '/review') {
		res.writeHead(302, { Location: '/portal?view=items' });
		res.end();
		return;
	}

	// Static assets from frontend build
	if (pathname.startsWith('/assets/vanphat_portal/frontend/')) {
		const rel = pathname.replace('/assets/vanphat_portal/frontend/', '');
		const fullPath = path.join(FRONTEND_DIR, rel);
		if (fs.existsSync(fullPath)) {
			if (rel.endsWith('.js')) res.setHeader('Content-Type', 'application/javascript');
			else if (rel.endsWith('.css')) res.setHeader('Content-Type', 'text/css');
			res.end(fs.readFileSync(fullPath));
			return;
		}
	}

	// Static assets from public folder
	if (pathname.startsWith('/assets/vanphat_portal/')) {
		const rel = pathname.replace('/assets/vanphat_portal/', '');
		const fullPath = path.join(PUBLIC_DIR, rel);
		if (fs.existsSync(fullPath)) {
			if (rel.endsWith('.webp')) res.setHeader('Content-Type', 'image/webp');
			else if (rel.endsWith('.png')) res.setHeader('Content-Type', 'image/png');
			else if (rel.endsWith('.css')) res.setHeader('Content-Type', 'text/css');
			res.end(fs.readFileSync(fullPath));
			return;
		}
	}

	res.statusCode = 404;
	res.end('Not found: ' + pathname);
});

// --- Master Data Reviewer HTML Generator ---
function renderMasterDataReviewerHtml() {
	return `<!DOCTYPE html>
<html lang="vi">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Rà Soát Master Data Nhóm A — Bao Bì Vạn Phát</title>
	<link rel="preconnect" href="https://fonts.googleapis.com">
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
	<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
	<style>
		* { box-sizing: border-box; margin: 0; padding: 0; }
		body {
			font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
			background: #0d1117;
			color: #e6edf3;
			min-height: 100vh;
			display: flex;
			flex-direction: column;
		}
		header {
			background: #161b22;
			border-bottom: 1px solid #30363d;
			padding: 16px 28px;
			display: flex;
			justify-content: space-between;
			align-items: center;
			position: sticky;
			top: 0;
			z-index: 50;
		}
		.brand {
			display: flex;
			align-items: center;
			gap: 14px;
		}
		.brand img {
			height: 38px;
			object-fit: contain;
			filter: drop-shadow(0 2px 6px rgba(237, 28, 36, 0.4));
		}
		.brand h1 {
			font-size: 17px;
			font-weight: 800;
			letter-spacing: 0.5px;
			color: #ffffff;
		}
		.brand span {
			font-size: 13px;
			color: #8b949e;
			font-weight: 500;
		}
		.actions {
			display: flex;
			gap: 12px;
		}
		.btn {
			display: inline-flex;
			align-items: center;
			gap: 6px;
			padding: 8px 16px;
			border-radius: 6px;
			font-size: 13.5px;
			font-weight: 600;
			text-decoration: none;
			cursor: pointer;
			transition: all 0.2s;
			border: 1px solid transparent;
		}
		.btn-primary {
			background: #ED1C24;
			color: #ffffff;
		}
		.btn-primary:hover {
			background: #d61920;
		}
		.btn-secondary {
			background: #21262d;
			color: #c9d1d9;
			border-color: #30363d;
		}
		.btn-secondary:hover {
			background: #30363d;
			color: #fff;
		}
		main {
			flex: 1;
			max-width: 1400px;
			width: 100%;
			margin: 0 auto;
			padding: 24px 28px;
		}
		.metrics-grid {
			display: grid;
			grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
			gap: 16px;
			margin-bottom: 24px;
		}
		.metric-card {
			background: #161b22;
			border: 1px solid #30363d;
			border-radius: 8px;
			padding: 16px;
		}
		.metric-val {
			font-size: 26px;
			font-weight: 800;
			color: #58a6ff;
			line-height: 1.2;
		}
		.metric-card:nth-child(1) .metric-val { color: #f78166; }
		.metric-card:nth-child(2) .metric-val { color: #58a6ff; }
		.metric-card:nth-child(3) .metric-val { color: #7ee787; }
		.metric-card:nth-child(4) .metric-val { color: #d2a8ff; }
		.metric-card:nth-child(5) .metric-val { color: #ffa657; }
		.metric-card:nth-child(6) .metric-val { color: #79c0ff; }
		.metric-lbl {
			font-size: 13px;
			color: #8b949e;
			margin-top: 4px;
			font-weight: 500;
		}
		.nav-tabs {
			display: flex;
			gap: 8px;
			border-bottom: 1px solid #30363d;
			margin-bottom: 20px;
			overflow-x: auto;
		}
		.tab-btn {
			background: transparent;
			border: none;
			border-bottom: 2px solid transparent;
			color: #8b949e;
			font-size: 14.5px;
			font-weight: 600;
			padding: 10px 16px;
			cursor: pointer;
			white-space: nowrap;
		}
		.tab-btn:hover { color: #e6edf3; }
		.tab-btn.active {
			color: #58a6ff;
			border-bottom-color: #58a6ff;
		}
		.search-bar {
			display: flex;
			gap: 12px;
			margin-bottom: 16px;
		}
		.search-input {
			flex: 1;
			max-width: 450px;
			background: #0d1117;
			border: 1px solid #30363d;
			border-radius: 6px;
			padding: 10px 14px;
			color: #e6edf3;
			font-size: 14px;
			outline: none;
		}
		.search-input:focus {
			border-color: #58a6ff;
			box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.2);
		}
		.table-box {
			background: #161b22;
			border: 1px solid #30363d;
			border-radius: 8px;
			overflow: hidden;
		}
		table {
			width: 100%;
			border-collapse: collapse;
			text-align: left;
			font-size: 14px;
		}
		th {
			background: #1c2128;
			color: #8b949e;
			font-weight: 600;
			padding: 12px 14px;
			border-bottom: 1px solid #30363d;
			white-space: nowrap;
		}
		td {
			padding: 11px 14px;
			border-bottom: 1px solid #21262d;
			color: #c9d1d9;
		}
		tr:hover td {
			background: #1f242c;
		}
		.badge {
			display: inline-block;
			padding: 3px 8px;
			border-radius: 12px;
			font-size: 12px;
			font-weight: 600;
		}
		.badge-tp { background: rgba(247, 129, 102, 0.15); color: #f78166; }
		.badge-btp { background: rgba(210, 168, 255, 0.15); color: #d2a8ff; }
		.badge-nvl { background: rgba(126, 231, 135, 0.15); color: #7ee787; }
		.badge-truc { background: rgba(88, 166, 255, 0.15); color: #58a6ff; }
		.bom-item-line {
			margin-left: 20px;
			color: #8b949e;
			font-size: 13px;
			display: flex;
			gap: 8px;
			padding: 2px 0;
		}
		.clickable-row {
			cursor: pointer;
			transition: background 0.15s ease;
		}
		.clickable-row:hover td {
			background: #21262d !important;
		}
		.badge-mfg { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
		.badge-buy { background: rgba(163, 113, 247, 0.15); color: #a371f7; border: 1px solid rgba(163, 113, 247, 0.3); }
		.badge-alias { background: rgba(255, 255, 255, 0.08); color: #8b949e; font-size: 11px; margin-top: 3px; display: inline-block; }
		.btn-detail {
			background: #21262d;
			border: 1px solid #30363d;
			color: #58a6ff;
			padding: 4px 10px;
			border-radius: 5px;
			font-size: 12px;
			font-weight: 600;
			cursor: pointer;
		}
		.btn-detail:hover {
			background: #30363d;
			color: #79c0ff;
		}

		/* Slide-Over Drawer */
		.drawer-overlay {
			position: fixed;
			top: 0; left: 0; right: 0; bottom: 0;
			background: rgba(0, 0, 0, 0.75);
			backdrop-filter: blur(4px);
			z-index: 999;
			opacity: 0;
			pointer-events: none;
			transition: opacity 0.25s ease;
		}
		.drawer-overlay.open {
			opacity: 1;
			pointer-events: auto;
		}
		.item-drawer {
			position: fixed;
			top: 0; right: 0; bottom: 0;
			width: 620px;
			max-width: 95vw;
			background: #161b22;
			border-left: 1px solid #3a424e;
			z-index: 1000;
			transform: translateX(100%);
			transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
			display: flex;
			flex-direction: column;
			box-shadow: -12px 0 40px rgba(0, 0, 0, 0.75);
		}
		.item-drawer.open {
			transform: translateX(0);
		}
		.drawer-header {
			padding: 18px 24px;
			background: #0d1117;
			border-bottom: 1px solid #30363d;
			display: flex;
			align-items: flex-start;
			justify-content: space-between;
			gap: 16px;
		}
		.drawer-title-box {
			display: flex;
			flex-direction: column;
			gap: 4px;
		}
		.drawer-code {
			font-family: monospace;
			font-size: 18px;
			font-weight: 800;
			color: #58a6ff;
			letter-spacing: 0.5px;
		}
		.drawer-name {
			font-size: 15px;
			font-weight: 700;
			color: #f0f6fc;
			line-height: 1.3;
		}
		.drawer-body {
			flex: 1;
			padding: 20px 24px;
			overflow-y: auto;
			display: flex;
			flex-direction: column;
			gap: 18px;
		}
		.drawer-section {
			background: #0d1117;
			border: 1px solid #30363d;
			border-radius: 8px;
			padding: 16px;
		}
		.drawer-section-title {
			font-size: 12px;
			font-weight: 700;
			text-transform: uppercase;
			letter-spacing: 0.6px;
			color: #58a6ff;
			margin-bottom: 12px;
			display: flex;
			align-items: center;
			gap: 8px;
		}
		.spec-grid {
			display: grid;
			grid-template-columns: repeat(2, 1fr);
			gap: 10px;
		}
		.spec-box {
			background: #161b22;
			border: 1px solid rgba(255, 255, 255, 0.06);
			border-radius: 6px;
			padding: 9px 12px;
		}
		.spec-label {
			font-size: 11px;
			color: #8b949e;
			margin-bottom: 3px;
			font-weight: 500;
		}
		.spec-val {
			font-size: 13.5px;
			font-weight: 600;
			color: #e6edf3;
			font-variant-numeric: tabular-nums;
		}
		.btn-close-drawer {
			background: #21262d;
			border: 1px solid #30363d;
			color: #c9d1d9;
			width: 34px;
			height: 34px;
			border-radius: 6px;
			cursor: pointer;
			display: flex;
			align-items: center;
			justify-content: center;
			font-size: 18px;
			font-weight: 700;
			transition: all 0.2s;
			flex-shrink: 0;
		}
		.btn-close-drawer:hover {
			background: #30363d;
			color: #fff;
		}
	</style>
</head>
<body>
	<header>
		<div class="brand">
			<img src="/assets/vanphat_portal/frontend/assets/logo-vanphat-WKCGA4lf.png" alt="Logo">
			<div>
				<h1>BAO BÌ VẠN PHÁT</h1>
				<span>Bảng Rà Soát Dữ Liệu Nền Tảng (Master Data Nhóm A)</span>
			</div>
		</div>
		<div class="actions">
			<a href="/portal" class="btn btn-primary">🚀 Mở Portal Báo Giá</a>
			<a href="/login" class="btn btn-secondary">Đăng Nhập</a>
		</div>
	</header>

	<main>
		<!-- Metrics Header -->
		<div class="metrics-grid">
			<div class="metric-card">
				<div class="metric-val">${MASTER_ITEMS.length}</div>
				<div class="metric-lbl">Mặt Hàng (Item Master)</div>
			</div>
			<div class="metric-card">
				<div class="metric-val">${BOM_MASTERS.length} / ${BOM_ITEMS.length}</div>
				<div class="metric-lbl">BOM 2 Cấp & Chi Tiết Vật Tư</div>
			</div>
			<div class="metric-card">
				<div class="metric-val">${WAREHOUSES.length} Kho / ${OPERATIONS.length} Trạm</div>
				<div class="metric-lbl">Kho Bãi & Máy Móc (${WORKSTATIONS.length} Trạm)</div>
			</div>
			<div class="metric-card">
				<div class="metric-val">${SUPPLIERS.length} NCC</div>
				<div class="metric-lbl">Nhà Cung Cấp & Liên Doanh</div>
			</div>
			<div class="metric-card">
				<div class="metric-val">${UNIFIED_CUSTOMERS.length} Đối Tác</div>
				<div class="metric-lbl">Khách Hàng Chuẩn Hóa</div>
			</div>
			<div class="metric-card">
				<div class="metric-val">${USERS.length} Tài Khoản</div>
				<div class="metric-lbl">Người Dùng & Phân Quyền</div>
			</div>
		</div>

		<!-- Navigation Tabs -->
		<div class="nav-tabs">
			<button class="tab-btn active" onclick="switchTab('items')">🏷️ Mặt Hàng (${MASTER_ITEMS.length})</button>
			<button class="tab-btn" onclick="switchTab('boms')">⚙️ Định Mức BOM (${BOM_MASTERS.length})</button>
			<button class="tab-btn" onclick="switchTab('warehouses')">🏭 Kho & Công Đoạn (${WAREHOUSES.length}/${OPERATIONS.length})</button>
			<button class="tab-btn" onclick="switchTab('suppliers')">🤝 Nhà Cung Cấp (${SUPPLIERS.length})</button>
			<button class="tab-btn" onclick="switchTab('customers')">👥 Khách Hàng (${UNIFIED_CUSTOMERS.length})</button>
			<button class="tab-btn" onclick="switchTab('users')">👤 Người Dùng & Quyền (${USERS.length})</button>
		</div>

		<!-- Search Bar -->
		<div class="search-bar">
			<input type="text" id="searchInput" class="search-input" placeholder="🔍 Tìm kiếm nhanh mã hàng, tên khách hàng, thông số..." oninput="filterCurrentTable()">
		</div>

		<!-- Content Containers -->
		<div id="itemsContainer" class="table-box">
			<table>
				<thead>
					<tr>
						<th style="width: 12%;">Mã hàng (Code)</th>
						<th style="width: 22%;">Tên sản phẩm & Tên gọi tắt</th>
						<th style="width: 14%;">Nhóm hàng</th>
						<th style="width: 25%;">Quy cách kỹ thuật (Cấu trúc / Kích thước)</th>
						<th style="width: 5%; text-align: center;">ĐVT</th>
						<th style="width: 8%; text-align: center;">Cung ứng</th>
						<th style="width: 12%;">Khách hàng</th>
						<th style="width: 7%; text-align: center;">Trạng thái</th>
						<th style="width: 5%; text-align: center;">Chi tiết</th>
					</tr>
				</thead>
				<tbody id="itemsBody">
					${MASTER_ITEMS.map(it => {
						const pouchDims = (it.custom_pouch_width_mm && it.custom_pouch_length_mm)
							? `${it.custom_pouch_width_mm}x${it.custom_pouch_length_mm}${it.custom_gusset_mm ? '+' + it.custom_gusset_mm : ''}mm`
							: '';
						let specSummary = '—';
						if (it.item_code.startsWith('TP-') || it.item_code.startsWith('NGCS-')) {
							specSummary = `${it.custom_structure_layers || 'Màng ghép'} • ${it.custom_thickness_mic ? it.custom_thickness_mic + 'mic' : ''} • ${pouchDims} ${it.custom_accessory_spec ? '• ' + it.custom_accessory_spec : ''}`;
						} else if (it.item_code.startsWith('BTP-')) {
							specSummary = `${it.custom_structure_layers || 'Cuộn BTP'} • ${it.custom_thickness_mic ? it.custom_thickness_mic + 'mic' : ''} • Khổ ${it.custom_film_width_mm || '—'}mm`;
						} else if (it.item_code.startsWith('TRUC-')) {
							specSummary = `Dài ${it.custom_cylinder_length_mm || '—'} x Chu vi ${it.custom_cylinder_circ_mm || '—'} mm • ${it.custom_cylinder_qty || 1} cây (Kho ${it.custom_cylinder_location || 'VP'})`;
						} else if (it.item_code.startsWith('NVL-')) {
							specSummary = `${it.custom_thickness_mic ? it.custom_thickness_mic + 'mic • ' : ''}${it.custom_film_width_mm ? 'Khổ ' + it.custom_film_width_mm + 'mm • ' : ''}${it.custom_accessory_spec || it.item_name}`;
						} else {
							specSummary = pouchDims || it.description || '—';
						}

						const isMfg = it.default_material_request_type === 'Manufacture';
						return `
						<tr class="clickable-row" onclick="openItemDrawer('${it.item_code}')">
							<td>
								<span style="font-weight: 700; font-family: monospace; color: #58a6ff;">${it.item_code}</span>
							</td>
							<td>
								<div style="font-weight: 600; color: #f0f6fc;">${it.item_name}</div>
								${it.custom_alias ? `<div class="badge badge-alias">${it.custom_alias}</div>` : ''}
							</td>
							<td>
								<span class="badge ${it.item_code.startsWith('TP-') || it.item_code.startsWith('NGCS-') ? 'badge-tp' : it.item_code.startsWith('BTP-') ? 'badge-btp' : it.item_code.startsWith('NVL-') ? 'badge-nvl' : 'badge-truc'}">${it.item_group}</span>
							</td>
							<td style="font-size: 12.5px; color: #c9d1d9;">${specSummary}</td>
							<td style="text-align: center; font-weight: 600;">${it.stock_uom}</td>
							<td style="text-align: center;">
								<span class="badge ${isMfg ? 'badge-mfg' : 'badge-buy'}">${isMfg ? 'Xưởng SX' : 'Mua ngoài'}</span>
							</td>
							<td style="font-size: 12px; color: #8b949e;">${it.customer || it.brand || 'Bán chung'}</td>
							<td style="text-align: center;">
								${it.disabled == '1' ? '<span style="color: #f85149; font-weight: 600; font-size: 12px;">Ngừng bán</span>' : '<span style="color: #3fb950; font-weight: 600; font-size: 12px;">Hoạt động</span>'}
							</td>
							<td style="text-align: center;">
								<button type="button" class="btn-detail" onclick="event.stopPropagation(); openItemDrawer('${it.item_code}')">👁️ Xem</button>
							</td>
						</tr>
					`}).join('')}
				</tbody>
			</table>
		</div>

		<div id="bomsContainer" class="table-box" style="display: none;">
			<table>
				<thead>
					<tr>
						<th>Mã BOM</th>
						<th>Sản phẩm thành phẩm</th>
						<th>Cơ số sản xuất</th>
						<th>Chi tiết thành phần vật tư (BOM Items)</th>
					</tr>
				</thead>
				<tbody id="bomsBody">
					${Array.from(BOM_TREE.values()).map(b => `
						<tr>
							<td style="font-weight: 700; font-family: monospace; vertical-align: top;">${b.master.bom_no}</td>
							<td style="vertical-align: top; font-weight: 600;">
								${b.master.item}
								<div style="font-size: 12px; color: #8b949e;">${b.master.item_name}</div>
							</td>
							<td style="vertical-align: top;">${Number(b.master.quantity).toLocaleString()} ${b.master.uom}</td>
							<td>
								${b.items.map(bi => `
									<div class="bom-item-line">
										<span style="font-family: monospace; color: #58a6ff;">${bi.item_code}</span>
										<span>${bi.item_name}</span>
										<strong style="color: #e6edf3;">${Number(bi.qty).toLocaleString()} ${bi.uom}</strong>
										<span style="color: #6e7681; font-style: italic;">(${bi.note || ''})</span>
									</div>
								`).join('')}
							</td>
						</tr>
					`).join('')}
				</tbody>
			</table>
		</div>

		<div id="warehousesContainer" class="table-box" style="display: none;">
			<table>
				<thead>
					<tr>
						<th>Mã Kho</th>
						<th>Tên Kho Bãi</th>
						<th>Loại Kho (ERPNext)</th>
						<th>Tài Khoản Kế Toán</th>
						<th>Mặt Hàng & Quy Cách Lưu Trữ Thực Tế</th>
					</tr>
				</thead>
				<tbody>
					${WAREHOUSES.map(w => `
						<tr>
							<td style="font-weight: 700; font-family: monospace; color: #4ea1e0;">${w.warehouse_code || w.name || ''}</td>
							<td style="font-weight: 600; color: #f0f6fc;">${w.warehouse_name || ''}</td>
							<td><span class="badge badge-info">${w.warehouse_type || 'Stores'}</span></td>
							<td style="font-family: monospace; color: #7ee787;">${w.account || '-'}</td>
							<td style="font-size: 12px; color: #8b949e;">${w.description || w.desc || ''}</td>
						</tr>
					`).join('')}
				</tbody>
			</table>
			<div style="padding: 16px; background: #1c2128; border-top: 1px solid #30363d; font-weight: 700; color: #58a6ff;">
				⚙️ Công Đoạn Sản Xuất & Trạm Máy Xưởng (${OPERATIONS.length} Công đoạn):
			</div>
			<table>
				<thead>
					<tr>
						<th>Mã Công Đoạn</th>
						<th>Tên Công Đoạn</th>
						<th>Trạm Máy Thực Hiện</th>
						<th>Chức Năng & Quy Trình Kỹ Thuật</th>
					</tr>
				</thead>
				<tbody>
					${OPERATIONS.map(op => `
						<tr>
							<td style="font-weight: 700; font-family: monospace; color: #4ea1e0;">${op.name || ''}</td>
							<td style="font-weight: 600; color: #f0f6fc;">${op.operation_name || op.operation || ''}</td>
							<td><span class="badge badge-info">${op.workstation || ''}</span></td>
							<td style="font-size: 12px; color: #8b949e;">${op.description || ''}</td>
						</tr>
					`).join('')}
				</tbody>
			</table>
		</div>

		<div id="suppliersContainer" class="table-box" style="display: none;">
			<table>
				<thead>
					<tr>
						<th>Mã NCC</th>
						<th>Tên Pháp Nhân</th>
						<th>Tên Gọi Tắt</th>
						<th>Nhóm Cung Ứng</th>
						<th>Mã Số Thuế</th>
						<th>Địa Chỉ Xưởng / Trụ Sở</th>
						<th>Liên Hệ / SĐT</th>
					</tr>
				</thead>
				<tbody id="suppliersBody">
					${SUPPLIERS.map(s => `
						<tr>
							<td style="font-family: monospace; color: #4ea1e0;">${s.name || ''}</td>
							<td style="font-weight: 600; color: #f0f6fc;">${s.supplier_name || ''}</td>
							<td><span class="badge badge-info">${s.alias || ''}</span></td>
							<td>${s.supplier_group || ''}</td>
							<td style="font-family: monospace;">${s.tax_id || '-'}</td>
							<td style="font-size: 11px; color: #8b949e;">${s.primary_address || '-'}</td>
							<td style="font-size: 11px;">${s.supplier_primary_contact ? s.supplier_primary_contact + (s.mobile_no ? ' (' + s.mobile_no + ')' : '') : (s.mobile_no || '-')}</td>
						</tr>
					`).join('')}
				</tbody>
			</table>
		</div>

		<div id="customersContainer" class="table-box" style="display: none;">
			<table>
				<thead>
					<tr>
						<th>Mã KH</th>
						<th>Tên Pháp Nhân Khách Hàng</th>
						<th>Tên Gọi Tắt (Alias)</th>
						<th>Nhóm Khách Hàng</th>
						<th>Loại Hình</th>
						<th>Hình Thức</th>
						<th>Địa Chỉ Thực Tế</th>
					</tr>
				</thead>
				<tbody id="customersBody">
					${UNIFIED_CUSTOMERS.map(c => `
						<tr>
							<td style="font-weight: 700; font-family: monospace; color: #4ea1e0;">${c.name}</td>
							<td style="font-weight: 600; color: #f0f6fc;">${c.customer_name}</td>
							<td><span class="badge badge-info">${c.alias || '—'}</span></td>
							<td>${c.type || '—'}</td>
							<td>${c.customer_type || 'Company'}</td>
							<td style="font-family: monospace; color: ${(c.payment_terms || '').toLowerCase().includes('gối đầu') ? '#3fb950; font-weight: 700;' : '#8b949e;'}">
								${(c.payment_terms || '').toLowerCase().includes('gối đầu') ? 'Trả sau' : 'Trả trước'}
							</td>
							<td style="font-size: 11px; color: #8b949e;">${c.primary_address || '—'}</td>
						</tr>
					`).join('')}
				</tbody>
			</table>
		</div>

		<div id="usersContainer" class="table-box" style="display: none;">
			<table>
				<thead>
					<tr>
						<th>Tài Khoản (Email)</th>
						<th>Họ và Tên</th>
						<th>Phòng Ban</th>
						<th>Chức Danh Tác Nghiệp</th>
						<th>Vai Trò Phân Quyền (ERPNext Roles)</th>
						<th>Số Điện Thoại</th>
						<th>Trạng Thái</th>
					</tr>
				</thead>
				<tbody id="usersBody">
					${USERS.map(u => `
						<tr>
							<td style="font-family: monospace; color: #4ea1e0; font-weight: 600;">${u.email}</td>
							<td style="font-weight: 600; color: #f0f6fc;">${u.full_name}</td>
							<td><span class="badge badge-info">${u.department || '—'}</span></td>
							<td style="color: #c9d1d9;">${u.designation || '—'}</td>
							<td>
								${(u.roles || '').split(',').map(r => `<span style="display: inline-block; padding: 2px 6px; margin: 2px; font-size: 11px; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border-radius: 4px; border: 1px solid rgba(56, 189, 248, 0.3); font-family: monospace;">${r.trim()}</span>`).join('')}
							</td>
							<td style="font-family: monospace;">${u.mobile_no || '—'}</td>
							<td><span class="badge badge-success">Hoạt động</span></td>
						</tr>
					`).join('')}
				</tbody>
			</table>
		</div>
	</main>

	<!-- Slide-Over Drawer for Item Detail -->
	<div id="drawerOverlay" class="drawer-overlay" onclick="closeItemDrawer()"></div>
	<div id="itemDrawer" class="item-drawer">
		<div class="drawer-header">
			<div class="drawer-title-box">
				<div style="display: flex; align-items: center; gap: 8px;">
					<span id="drawerItemCode" class="drawer-code"></span>
					<span id="drawerItemGroupBadge" class="badge"></span>
				</div>
				<div id="drawerItemName" class="drawer-name"></div>
				<div id="drawerItemAlias" style="font-size: 12px; color: #8b949e; margin-top: 2px;"></div>
			</div>
			<button type="button" class="btn-close-drawer" onclick="closeItemDrawer()" title="Đóng (Esc)">✕</button>
		</div>
		<div id="drawerBody" class="drawer-body">
			<!-- Populated via JavaScript -->
		</div>
	</div>

	<script>
		// Serialized Master Items & BOM Data
		const ITEMS_DATA = ${JSON.stringify(MASTER_ITEMS)};
		const BOMS_DATA = ${JSON.stringify(Array.from(BOM_TREE.entries()).map(([k, v]) => ({ bom_no: k, master: v.master, items: v.items })))};

		const ITEMS_MAP = new Map(ITEMS_DATA.map(it => [it.item_code, it]));
		const BOMS_BY_ITEM = new Map();
		BOMS_DATA.forEach(b => {
			if (b.master && b.master.item) {
				BOMS_BY_ITEM.set(b.master.item, b);
			}
		});

		function formatVND(val) {
			if (val === undefined || val === null || val === '') return '—';
			const n = Number(val);
			if (isNaN(n)) return val;
			return n.toLocaleString('vi-VN') + ' đ';
		}

		function formatNum(val, unit = '') {
			if (val === undefined || val === null || val === '') return '—';
			const n = Number(val);
			if (isNaN(n)) return val;
			return n.toLocaleString('vi-VN') + (unit ? ' ' + unit : '');
		}

		function openItemDrawer(code) {
			const item = ITEMS_MAP.get(code);
			if (!item) return;

			const isMfg = item.default_material_request_type === 'Manufacture';
			const bom = BOMS_BY_ITEM.get(code);

			// Header
			document.getElementById('drawerItemCode').textContent = item.item_code;
			document.getElementById('drawerItemName').textContent = item.item_name;
			document.getElementById('drawerItemAlias').textContent = item.custom_alias ? 'Tên gọi tắt: ' + item.custom_alias : '';

			const badge = document.getElementById('drawerItemGroupBadge');
			badge.textContent = item.item_group || 'Mặt hàng';
			badge.className = 'badge ' + (
				item.item_code.startsWith('TP-') || item.item_code.startsWith('NGCS-') ? 'badge-tp' :
				item.item_code.startsWith('BTP-') ? 'badge-btp' :
				item.item_code.startsWith('NVL-') ? 'badge-nvl' : 'badge-truc'
			);

			const pouchDims = (item.custom_pouch_width_mm && item.custom_pouch_length_mm)
				? (item.custom_pouch_width_mm + ' x ' + item.custom_pouch_length_mm + (item.custom_gusset_mm ? ' +' + item.custom_gusset_mm : '') + ' mm')
				: '—';

			const cylDims = (item.custom_cylinder_length_mm || item.custom_cylinder_circ_mm)
				? (item.custom_cylinder_length_mm + ' x ' + item.custom_cylinder_circ_mm + ' mm')
				: '—';

			let bomSectionHtml = '';
			if (bom) {
				const rowsHtml = bom.items.map(function(bi) {
					return '<tr>' +
						'<td style="padding: 6px 8px; font-family: monospace; color: #58a6ff;">' + bi.item_code + '</td>' +
						'<td style="padding: 6px 8px; color: #c9d1d9;">' + bi.item_name + '</td>' +
						'<td style="padding: 6px 8px; text-align: right; font-weight: 600; color: #f0f6fc;">' + Number(bi.qty).toLocaleString('vi-VN') + '</td>' +
						'<td style="padding: 6px 8px; text-align: center; color: #8b949e;">' + bi.uom + '</td>' +
					'</tr>';
				}).join('');

				bomSectionHtml =
					'<div style="background: #161b22; border-radius: 6px; padding: 10px 12px; margin-bottom: 12px; border: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-between; align-items: center;">' +
						'<div>' +
							'<div style="font-size: 11px; color: #8b949e;">Mã BOM Định Mức:</div>' +
							'<div style="font-family: monospace; font-weight: 700; color: #58a6ff;">' + bom.master.bom_no + '</div>' +
						'</div>' +
						'<div style="text-align: right;">' +
							'<div style="font-size: 11px; color: #8b949e;">Cơ Số Sản Xuất:</div>' +
							'<div style="font-weight: 700; color: #3fb950;">' + formatNum(bom.master.quantity) + ' ' + bom.master.uom + '</div>' +
						'</div>' +
					'</div>' +
					'<table style="font-size: 12px; width: 100%; border-collapse: collapse;">' +
						'<thead>' +
							'<tr>' +
								'<th style="padding: 6px 8px; font-size: 11px;">Mã NVL / BTP</th>' +
								'<th style="padding: 6px 8px; font-size: 11px;">Tên Vật Tư</th>' +
								'<th style="padding: 6px 8px; font-size: 11px; text-align: right;">Định Mức</th>' +
								'<th style="padding: 6px 8px; font-size: 11px; text-align: center;">ĐVT</th>' +
							'</tr>' +
						'</thead>' +
						'<tbody>' + rowsHtml + '</tbody>' +
					'</table>';
			} else {
				bomSectionHtml = '<div style="padding: 12px; background: rgba(163, 113, 247, 0.08); border: 1px dashed rgba(163, 113, 247, 0.3); border-radius: 6px; font-size: 12.5px; color: #d2a8ff; text-align: center;">' +
					'📦 Hàng mua ngoài trực tiếp / Nguyên vật liệu gốc / Trục in — Không qua công đoạn sản xuất nội bộ (Không có BOM).' +
				'</div>';
			}

			const html =
				'<div class="drawer-section">' +
					'<div class="drawer-section-title">📋 1. Định Danh & Cung Ứng ERPNext</div>' +
					'<div class="spec-grid">' +
						'<div class="spec-box"><div class="spec-label">Khách Hàng Sở Hữu</div><div class="spec-val" style="color: #58a6ff;">' + (item.customer || 'Dùng chung / Bán lẻ') + '</div></div>' +
						'<div class="spec-box"><div class="spec-label">Thương Hiệu (Brand)</div><div class="spec-val">' + (item.brand || '—') + '</div></div>' +
						'<div class="spec-box"><div class="spec-label">Phương Thức Cung Ứng</div><div class="spec-val"><span class="badge ' + (isMfg ? 'badge-mfg' : 'badge-buy') + '">' + (isMfg ? '🏭 Xưởng SX Vạn Phát' : '🛒 Mua ngoài (Thương mại)') + '</span></div></div>' +
						'<div class="spec-box"><div class="spec-label">Đơn Vị Tính Chuẩn (UOM)</div><div class="spec-val">' + item.stock_uom + '</div></div>' +
						'<div class="spec-box"><div class="spec-label">Đơn Giá Chuẩn (Standard Rate)</div><div class="spec-val" style="color: #7ee787;">' + formatVND(item.standard_rate) + '</div></div>' +
						'<div class="spec-box"><div class="spec-label">Đặt Hàng Tối Thiểu (MOQ)</div><div class="spec-val">' + formatNum(item.min_order_qty, item.stock_uom) + '</div></div>' +
						'<div class="spec-box"><div class="spec-label">Mức Tồn Kho An Toàn</div><div class="spec-val">' + formatNum(item.safety_stock, item.stock_uom) + '</div></div>' +
						'<div class="spec-box"><div class="spec-label">Trạng Thái Kinh Doanh</div><div class="spec-val">' + (item.disabled == '1' ? '<span style="color: #f85149;">⛔ Ngừng kinh doanh</span>' : '<span style="color: #3fb950;">✅ Đang hoạt động</span>') + '</div></div>' +
					'</div>' +
				'</div>' +

				'<div class="drawer-section">' +
					'<div class="drawer-section-title">📐 2. Cấu Trúc Màng & Quy Cách Túi</div>' +
					'<div class="spec-grid">' +
						'<div class="spec-box" style="grid-column: span 2;"><div class="spec-label">Cấu Trúc Lớp Ghép (Structure Layers)</div><div class="spec-val" style="color: #f78166; font-weight: 700;">' + (item.custom_structure_layers || '—') + '</div></div>' +
						'<div class="spec-box"><div class="spec-label">Độ Dày Tổng Màng (Thickness)</div><div class="spec-val">' + (item.custom_thickness_mic ? item.custom_thickness_mic + ' mic (µm)' : '—') + '</div></div>' +
						'<div class="spec-box"><div class="spec-label">Khổ Màng Ghép / In (Width)</div><div class="spec-val">' + (item.custom_film_width_mm ? item.custom_film_width_mm + ' mm' : '—') + '</div></div>' +
						'<div class="spec-box"><div class="spec-label">Kích Thước Túi (W x L + G)</div><div class="spec-val">' + pouchDims + '</div></div>' +
						'<div class="spec-box"><div class="spec-label">Bước Dao Cắt Túi (Cut Length)</div><div class="spec-val">' + (item.custom_cut_length_mm ? item.custom_cut_length_mm + ' mm' : '—') + '</div></div>' +
						'<div class="spec-box" style="grid-column: span 2;"><div class="spec-label">Phụ Kiện Miệng Túi / Vòi / Zipper</div><div class="spec-val" style="color: #d2a8ff;">' + (item.custom_accessory_spec || 'Không có phụ kiện') + '</div></div>' +
					'</div>' +
				'</div>' +

				'<div class="drawer-section">' +
					'<div class="drawer-section-title">🖨️ 3. Trục In Ống Đồng & Công Nghệ In</div>' +
					'<div class="spec-grid">' +
						'<div class="spec-box"><div class="spec-label">Công Nghệ In</div><div class="spec-val">' + (item.custom_print_tech || '—') + '</div></div>' +
						'<div class="spec-box"><div class="spec-label">Số Lượng Màu / Cây Trục</div><div class="spec-val" style="color: #79c0ff; font-weight: 700;">' + (item.custom_cylinder_qty ? item.custom_cylinder_qty + ' cây' : '—') + '</div></div>' +
						'<div class="spec-box"><div class="spec-label">Mã Bộ Trục / Item Trục</div><div class="spec-val" style="font-family: monospace;">' + (item.custom_cylinder_item || item.custom_cylinder_code || '—') + '</div></div>' +
						'<div class="spec-box"><div class="spec-label">Kích Thước Trục (Dài x Chu Vi)</div><div class="spec-val">' + cylDims + '</div></div>' +
						'<div class="spec-box" style="grid-column: span 2;"><div class="spec-label">Vị Trí Lưu Trữ Trục Xưởng</div><div class="spec-val">' + (item.custom_cylinder_location || 'Kho Trục Vạn Phát') + '</div></div>' +
					'</div>' +
				'</div>' +

				'<div class="drawer-section">' +
					'<div class="drawer-section-title">⚙️ 4. Định Mức BOM 2 Cấp Liên Kết</div>' +
					bomSectionHtml +
				'</div>';

			document.getElementById('drawerBody').innerHTML = html;
			document.getElementById('drawerOverlay').classList.add('open');
			document.getElementById('itemDrawer').classList.add('open');
			document.body.style.overflow = 'hidden';
		}

		function closeItemDrawer() {
			const overlay = document.getElementById('drawerOverlay');
			const drawer = document.getElementById('itemDrawer');
			if (overlay) overlay.classList.remove('open');
			if (drawer) drawer.classList.remove('open');
			document.body.style.overflow = '';
		}

		// Keyboard event: ESC to close
		window.addEventListener('keydown', (e) => {
			if (e.key === 'Escape') closeItemDrawer();
		});

		let currentTab = 'items';
		const tabs = ['items', 'boms', 'warehouses', 'suppliers', 'customers', 'users'];

		function switchTab(tab) {
			currentTab = tab;
			tabs.forEach(t => {
				const container = document.getElementById(t + 'Container');
				if (container) container.style.display = t === tab ? 'block' : 'none';
			});
			document.querySelectorAll('.tab-btn').forEach(btn => {
				btn.classList.toggle('active', btn.getAttribute('onclick').includes(tab));
			});
			filterCurrentTable();
		}

		function filterCurrentTable() {
			const q = document.getElementById('searchInput').value.trim().toLowerCase();
			const activeContainer = document.getElementById(currentTab + 'Container');
			if (!activeContainer) return;
			const rows = activeContainer.querySelectorAll('tbody tr');
			rows.forEach(r => {
				const text = r.innerText.toLowerCase();
				r.style.display = text.includes(q) ? '' : 'none';
			});
		}
	</script>
</body>
</html>`;
}

// Start Server
server.listen(PORT, '0.0.0.0', () => {
	console.log(`[VANPHAT-PORTAL] Serving live portal on http://localhost:${PORT}/portal`);
	console.log(`[VANPHAT-PORTAL] Master Data Reviewer on http://localhost:${PORT}/master-data`);
	console.log(`[VANPHAT-PORTAL] Login page on http://localhost:${PORT}/login`);
});

export { renderMasterDataReviewerHtml };
