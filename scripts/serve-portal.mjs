import http from 'http';
import fs from 'fs';
import path from 'path';

const PORT = 8080;
const ROOT_DIR = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const FRONTEND_DIR = path.join(ROOT_DIR, 'apps/vanphat_portal/vanphat_portal/public/frontend');
const PUBLIC_DIR = path.join(ROOT_DIR, 'apps/vanphat_portal/vanphat_portal/public');
const LOGIN_HTML = path.join(ROOT_DIR, 'apps/vanphat_portal/vanphat_portal/www/login.html');
const PORTAL_HTML = path.join(ROOT_DIR, 'apps/vanphat_portal/vanphat_portal/www/portal.html');
const PROTO_HTML = path.join(ROOT_DIR, 'appvanphat/preview-modal-step1.html');

const MOCK_QUOTATIONS = [
	{
		name: 'BG-2026-0001',
		creation: '2026-09-10 14:30:00',
		party_name: 'Công ty TNHH Nhựa Ánh Dương',
		brand: 'Ánh Dương Pack',
		rounded_total: 18684000,
		status: 'Đã duyệt',
		owner: 'giamdoc@vanphat.com'
	},
	{
		name: 'BG-2026-0002',
		creation: '2026-09-10 10:15:00',
		party_name: 'Công ty CP Bao Bì Nam Long',
		brand: 'Nam Long Eco',
		rounded_total: 8950000,
		status: 'Chờ duyệt',
		owner: 'sale@vanphat.com'
	}
];

const server = http.createServer((req, res) => {
	const url = new URL(req.url, `http://127.0.0.1:${PORT}`);
	const pathname = url.pathname;

	// CORS headers
	res.setHeader('Access-Control-Allow-Origin', '*');
	res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
	res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
	if (req.method === 'OPTIONS') {
		res.statusCode = 204;
		res.end();
		return;
	}

	// APIs
	if (req.method === 'POST') {
		let body = '';
		req.on('data', chunk => body += chunk);
		req.on('end', () => {
			res.setHeader('Content-Type', 'application/json');
			if (pathname === '/api/method/login') {
				res.end(JSON.stringify({ message: 'Logged In' }));
				return;
			}
			if (pathname === '/api/method/logout') {
				res.end(JSON.stringify({ message: 'Logged Out' }));
				return;
			}
			if (pathname === '/api/method/vanphat_portal.api.bao_gia.list_quotations') {
				res.end(JSON.stringify({ message: MOCK_QUOTATIONS }));
				return;
			}
			if (pathname === '/api/method/vanphat_portal.api.bao_gia.create_quotation') {
				let parsed = {};
				try { parsed = JSON.parse(body); } catch (e) { void e; }
				const newDoc = {
					name: 'BG-2026-0003',
					creation: '2026-09-10 16:35:00',
					party_name: parsed.customer || 'Khách Hàng Mới',
					brand: parsed.brand || 'Brand Mới',
					rounded_total: 18684000,
					status: 'Chờ duyệt',
					owner: 'giamdoc@vanphat.com'
				};
				MOCK_QUOTATIONS.unshift(newDoc);
				res.end(JSON.stringify({ message: newDoc }));
				return;
			}
			if (pathname === '/api/method/vanphat_portal.api.bao_gia.get_boot') {
				res.end(JSON.stringify({
					message: {
						user: 'Administrator',
						csrf_token: 'mock_csrf_token',
						company: 'Công ty TNHH Bao Bì Vạn Phát'
					}
				}));
				return;
			}
			if (pathname === '/api/method/vanphat_portal.api.bao_gia.search_customers') {
				res.end(JSON.stringify({
					message: [
						{ name: 'CUST-0001', customer_name: 'Công ty TNHH Mỹ Phẩm DS Cosmetic' },
						{ name: 'CUST-0002', customer_name: 'Công ty CP Khăn Ướt Eco Wipes' }
					]
				}));
				return;
			}
			if (pathname === '/api/method/vanphat_portal.api.bao_gia.calculate_packaging_quotation') {
				let p = {};
				try { p = JSON.parse(body); } catch (e) { void e; }
				const desired_qty = Number(p.desired_qty) || 5000;
				const width = Number(p.width_mm) || 280;
				const length = Number(p.length_mm) || 340;
				const lanes = width <= 360 ? 2 : 1;
				const bags_per_roll = Math.floor((1500.0 * lanes * 0.92) / (length / 1000.0));
				const num_rolls = Math.max(1, Math.ceil(desired_qty / (bags_per_roll || 8000)));
				const q_opt = num_rolls * bags_per_roll;
				const q_surp = Math.max(0, q_opt - desired_qty);
				const cyl_qty = Number(p.cylinder_qty) || 0;
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
			if (pathname === '/api/method/vanphat_portal.api.bao_gia.get_price_preview') {
				let p = {};
				try { p = JSON.parse(body); } catch (e) { void e; }
				const rows = p.lines || [];
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

	// Pages
	if (pathname === '/' || pathname === '/portal') {
		res.setHeader('Content-Type', 'text/html; charset=utf-8');
		res.end(fs.readFileSync(PORTAL_HTML));
		return;
	}
	if (pathname === '/login') {
		res.setHeader('Content-Type', 'text/html; charset=utf-8');
		res.end(fs.readFileSync(LOGIN_HTML));
		return;
	}
	if (pathname === '/preview' || pathname === '/preview-modal-step1.html') {
		res.setHeader('Content-Type', 'text/html; charset=utf-8');
		res.end(fs.readFileSync(PROTO_HTML));
		return;
	}

	// Static assets
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

server.listen(PORT, '0.0.0.0', () => {
	console.log(`[VANPHAT-PORTAL] Serving live portal on http://localhost:${PORT}/portal`);
	console.log(`[VANPHAT-PORTAL] Login page on http://localhost:${PORT}/login`);
	console.log(`[VANPHAT-PORTAL] Prototype Step 1 on http://localhost:${PORT}/preview`);
});
