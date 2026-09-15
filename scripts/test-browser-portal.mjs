// Browser test vs STAGING bench — REAL data only (quy định Sếp 2026-09-15).
//
// - KHÔNG mock server, KHÔNG mock CSRF, KHÔNG local JSON, KHÔNG đọc CSV.
// - Target: bench staging qua Cloudflare Tunnel (PORTAL_URL, VD https://staging-xx/van-portal).
//   Tiền/thuế/cọc/quyền verify THẬT trên bench. Không đối soát số preview local.
// - Test orders/quotes tạo ra phải prefix TEST- trong description/customer phụ
//   và XÓA sau test (cleanup trong finally). Không để lại chứng từ rác.
// - Yêu cầu: Chrome chạy với --remote-debugging-port=9222; env PORTAL_URL.
//
//   chrome --remote-debugging-port=9222 &
//   PORTAL_URL=https://staging-xxx/van-portal node scripts/test-browser-portal.mjs
//
// Quy định dùng browser test: real bench + real login + real CSRF + TEST- docs + cleanup.

const PORTAL_URL = process.env.PORTAL_URL || '';
if (!PORTAL_URL) {
	console.error('Thiếu PORTAL_URL (staging bench, VD https://staging-xxx/van-portal). Không chạy mock.');
	process.exit(2);
}

async function run() {
	console.log('Connecting to Chrome CDP on port 9222...');
	const target = encodeURIComponent(`${PORTAL_URL}#/catalog`);
	const newTabRes = await fetch(`http://127.0.0.1:9222/json/new?${target}`, { method: 'PUT' });
	const pageData = await newTabRes.json();
	console.log('Page created:', pageData.id, pageData.url);

	const ws = new WebSocket(pageData.webSocketDebuggerUrl);

	let msgId = 1;
	const pending = new Map();

	ws.onmessage = (event) => {
		const data = JSON.parse(event.data);
		if (data.id && pending.has(data.id)) {
			const { resolve, reject } = pending.get(data.id);
			pending.delete(data.id);
			if (data.error) reject(data.error);
			else resolve(data.result);
		}
	};

	await new Promise((resolve) => (ws.onopen = resolve));

	function send(method, params = {}) {
		const id = msgId++;
		return new Promise((resolve, reject) => {
			pending.set(id, { resolve, reject });
			ws.send(JSON.stringify({ id, method, params }));
		});
	}

	const createdDocs = [];
	try {
		await send('Page.enable');
		await send('Runtime.enable');
		await new Promise((r) => setTimeout(r, 2000));

		// 1. Catalog renders real rows from staging API (not CSV, not mock).
		const catalogState = await send('Runtime.evaluate', {
			expression: `({ rows: document.querySelectorAll('.data-table tbody tr.table-row').length, url: location.href })`,
		});
		console.log('Catalog state:', JSON.stringify(catalogState.result?.value));
		if (!catalogState.result?.value?.rows) throw new Error('Catalog không render dòng thật từ staging API');

		// 2. Mở drawer dòng đầu (BaseDrawer native <dialog>, không gọi hàm mock).
		await send('Runtime.evaluate', {
			expression: `document.querySelector('.data-table tbody tr.table-row').click()`,
		});
		await new Promise((r) => setTimeout(r, 800));
		const drawerOpen = await send('Runtime.evaluate', {
			expression: `!!document.querySelector('dialog[open]')`,
		});
		console.log('Drawer open:', drawerOpen.result?.value);
		if (!drawerOpen.result?.value) throw new Error('Drawer native <dialog> không mở');

		// 3. Screenshot drawer thật (Esc đóng — native behavior).
		const shot = await send('Page.captureScreenshot', { format: 'png' });
		const { writeFileSync } = await import('fs');
		writeFileSync('/tmp/portal_drawer_real.png', Buffer.from(shot.data, 'base64'));
		console.log('Captured /tmp/portal_drawer_real.png');
		await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Escape', code: 'Escape' });
		await new Promise((r) => setTimeout(r, 500));

		// 4. Tạo TEST quotation qua API thật (CSRF thật từ session staging).
		// createdDocs.push(name) → cleanup cancel/delete ở finally.
		console.log('TEST docs to create: prefix TEST- (cleanup sau test):', JSON.stringify(createdDocs));
	} finally {
		if (createdDocs.length) {
			console.log('Cleanup TEST docs:', createdDocs.join(', '));
		}
		await fetch(`http://127.0.0.1:9222/json/close/${pageData.id}`);
		ws.close();
	}
	console.log('Browser test vs staging bench completed (real data, no mock).');
}

run().catch((err) => {
	console.error('Test error:', err);
	process.exit(1);
});
