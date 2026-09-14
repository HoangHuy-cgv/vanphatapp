#!/usr/bin/env node
/**
 * Browser test cho Van Phat Portal qua puppeteer-core + Chrome hệ thống.
 * Dùng: node scripts/browser-test.mjs [url] [--shot-prefix=...]
 * Không cần MCP server, chạy trực tiếp headless Chrome đã cài.
 */
import { createRequire } from 'module';
const require = createRequire('/tmp/package.json');
const puppeteer = require('puppeteer-core');
import fs from 'fs';
import path from 'path';

const CHROME = process.env.CHROME_BIN || '/var/home/huy/.local/bin/chromium';
const BASE_URL = process.argv[2] || 'http://127.0.0.1:8080/portal';
const shotPrefix = (process.argv.find(a => a.startsWith('--shot-prefix=')) || '').split('=')[1] || '/tmp/vp';

const browser = await puppeteer.launch({
	executablePath: CHROME,
	headless: 'shell',
	args: ['--no-sandbox', '--disable-gpu', '--window-size=1600,1000'],
});

const failed404 = [];
const pageErrors = [];
const consoleErrors = [];

try {
	const page = await browser.newPage();
	await page.setViewport({ width: 1600, height: 1000 });
	page.on('response', (res) => {
		if (res.status() === 404) failed404.push(`${res.status()} ${res.url()}`);
	});
	page.on('pageerror', (err) => pageErrors.push(String(err).split('\n')[0]));
	page.on('console', (msg) => {
		if (msg.type() === 'error') consoleErrors.push(msg.text().slice(0, 300));
	});

	await page.goto(BASE_URL, { waitUntil: 'networkidle0', timeout: 30000 });
	await new Promise(r => setTimeout(r, 2500));

	const state = await page.evaluate(() => ({
		title: document.title,
		hash: location.hash,
		appMounted: !!document.querySelector('#app')?.children.length,
		bodyText: document.body.innerText.slice(0, 400),
		tables: document.querySelectorAll('table').length,
		rows: document.querySelectorAll('tbody tr').length,
		vueError: document.body.innerText.includes('productItems') ? 'productItems leak' : null,
	}));

	// Chụp trang hiện tại
	await page.screenshot({ path: `${shotPrefix}-current.png` });

	// Điều hướng tới #/catalog nếu chưa ở đó
	if (!state.hash.includes('catalog')) {
		await page.goto(BASE_URL + '#/catalog', { waitUntil: 'networkidle0', timeout: 30000 });
		await new Promise(r => setTimeout(r, 2500));
	}
	const catalog = await page.evaluate(() => ({
		hash: location.hash,
		tabBadges: [...document.querySelectorAll('.tab-badge')].map(b => b.textContent.trim()),
		rows: document.querySelectorAll('tbody tr').length,
		firstRow: document.querySelector('tbody tr td')?.textContent.trim().slice(0, 60) || null,
		emptyMsg: document.querySelector('.empty-msg')?.textContent.trim().slice(0, 120) || null,
		apiRequests: performance.getEntriesByType('resource').filter(r => r.name.includes('/api/method/')).map(r => r.name.split('/api/method/')[1].split('?')[0]),
	}));
	await page.screenshot({ path: `${shotPrefix}-catalog.png` });

	console.log(JSON.stringify({ state, catalog, failed404, pageErrors, consoleErrors: consoleErrors.slice(0, 10) }, null, 2));

	const fail = failed404.length > 0 || pageErrors.length > 0;
	process.exitCode = fail ? 1 : 0;
} finally {
	await browser.close();
}
