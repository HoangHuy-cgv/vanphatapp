import http from 'http';
import fs from 'fs';
import path from 'path';

const PORT = 8080;
const ROOT_DIR = '/var/home/huy/workspace';
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
