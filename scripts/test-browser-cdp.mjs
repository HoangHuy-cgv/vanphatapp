import fs from 'fs';

async function run() {
	console.log('Connecting to Chrome CDP on port 9222...');
	const newTabRes = await fetch('http://127.0.0.1:9222/json/new?http://localhost:8080/master-data', { method: 'PUT' });
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

	await new Promise((resolve) => ws.onopen = resolve);

	function send(method, params = {}) {
		const id = msgId++;
		return new Promise((resolve, reject) => {
			pending.set(id, { resolve, reject });
			ws.send(JSON.stringify({ id, method, params }));
		});
	}

	await send('Page.enable');
	await send('Runtime.enable');
	await send('Emulation.setDeviceMetricsOverride', {
		width: 1600,
		height: 1000,
		deviceScaleFactor: 1,
		mobile: false
	});

	// Wait for DOM
	await new Promise(r => setTimeout(r, 1000));

	// 1. Screenshot of NGCS-00001 Drawer
	console.log('Opening drawer for NGCS-00001...');
	await send('Runtime.evaluate', {
		expression: `openItemDrawer('NGCS-00001');`
	});
	await new Promise(r => setTimeout(r, 500));
	let shot = await send('Page.captureScreenshot', { format: 'png' });
	fs.writeFileSync('/tmp/drawer_ngcs_00001.png', Buffer.from(shot.data, 'base64'));
	console.log('Captured /tmp/drawer_ngcs_00001.png');

	// 2. Screenshot of TP-00001 Drawer
	console.log('Opening drawer for TP-00001...');
	await send('Runtime.evaluate', {
		expression: `openItemDrawer('TP-00001');`
	});
	await new Promise(r => setTimeout(r, 500));
	shot = await send('Page.captureScreenshot', { format: 'png' });
	fs.writeFileSync('/tmp/drawer_tp_00001.png', Buffer.from(shot.data, 'base64'));
	console.log('Captured /tmp/drawer_tp_00001.png');

	// 3. Screenshot of BOMs Tab
	console.log('Switching to BOMs tab...');
	await send('Runtime.evaluate', {
		expression: `closeItemDrawer(); switchTab('boms');`
	});
	await new Promise(r => setTimeout(r, 500));
	shot = await send('Page.captureScreenshot', { format: 'png' });
	fs.writeFileSync('/tmp/tab_boms.png', Buffer.from(shot.data, 'base64'));
	console.log('Captured /tmp/tab_boms.png');

	// 4. Close page
	await fetch(`http://127.0.0.1:9222/json/close/${pageData.id}`);
	ws.close();
	console.log('All browser test captures completed successfully!');
}

run().catch(err => {
	console.error('Test error:', err);
	process.exit(1);
});
