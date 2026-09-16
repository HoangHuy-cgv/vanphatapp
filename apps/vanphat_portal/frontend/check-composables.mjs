// Guard không cần framework test: bundle composable bằng chính Vite rồi khởi tạo trong Node.
// Bắt lớp lỗi "dùng biến chưa định nghĩa trong composable" — lớp lỗi mà `vite build` VẪN xanh
// vì Vite chỉ bundle chứ không phân tích phạm vi biến. Đã từng lọt ra production (serverPricingInitial).
//
//   node check-composables.mjs
import { readdir, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import vue from '@vitejs/plugin-vue';
import { build } from 'vite';

const here = dirname(fileURLToPath(import.meta.url));
const outDir = join(here, '.composables-check');
const entryFile = join(here, '.composables-check-entry.js');
const stubFile = join(here, '.composables-check-ui-stub.js');

// Chặn thư viện toast UI: guard này kiểm code của mình, không kéo `vue-sonner` vào Node.
// ADR-007: chỉ còn vue-sonner là external UI dep duy nhất; stub giữ contract tối thiểu.
const UI_STUB = `
const noop = () => {};
export const toast = Object.assign(noop, { success: noop, error: noop, warning: noop, info: noop, dismiss: noop, promise: noop, custom: noop });
`;

const names = (await readdir(join(here, 'src/composables')))
	.filter((file) => file.endsWith('.js'))
	.map((file) => file.replace(/\.js$/, ''));

const entry = `
${names.map((name, index) => `import * as m${index} from './src/composables/${name}.js';`).join('\n')}

process.on('unhandledRejection', () => {}); // vài composable gọi API khi khởi tạo; bỏ qua

const modules = { ${names.map((name, index) => `${JSON.stringify(name)}: m${index}`).join(', ')} };
let failed = 0;

for (const [name, module] of Object.entries(modules)) {
	try {
		// Gọi mọi factory export ra để chạy hết thân hàm; tham số thừa vô hại trong JS.
		const factories = Object.keys(module).filter((key) => key.startsWith('use'));
		// Vừa đóng vai ref (có .value) vừa đóng vai props (có formData/step1Data/savedData).
		const arg = {
			value: { lines: [], materials: [] },
			formData: {},
			step1Data: {},
			savedData: { materials: [], lines: [], cylinder_qty: 0, artwork_url: '' },
		};
		for (const key of factories) module[key](arg, () => {}, () => {});
		console.log('[ok]   ' + name + (factories.length ? ' (' + factories.join(', ') + ')' : ' (chỉ import)'));
	} catch (error) {
		failed += 1;
		console.log('[FAIL] ' + name + ': ' + error.message);
	}
}

console.log(failed ? '\\nCOMPOSABLES: FAIL (' + failed + '/' + Object.keys(modules).length + ')' : '\\nCOMPOSABLES: PASS (' + Object.keys(modules).length + '/' + Object.keys(modules).length + ')');
// KHÔNG process.exit() ở đây: bundle chạy trong chính tiến trình này nên exit sẽ bỏ qua dọn file tạm.
process.exitCode = failed ? 1 : 0;
`;

try {
	await writeFile(entryFile, entry, 'utf8');
	await writeFile(stubFile, UI_STUB, 'utf8');
	await build({
		root: here,
		logLevel: 'error',
		plugins: [vue()],
		resolve: { alias: { 'vue-sonner': stubFile } },
		ssr: { noExternal: true },
		build: {
			ssr: entryFile,
			outDir,
			emptyOutDir: true,
			minify: false,
			rollupOptions: { output: { entryFileNames: 'check.mjs' } },
		},
	});
	await import(pathToFileURL(join(outDir, 'check.mjs')).href);
} catch (error) {
	console.log('[FAIL] không bundle/khởi tạo được composable:', error.message);
	process.exitCode = 1;
} finally {
	await rm(entryFile, { force: true });
	await rm(stubFile, { force: true });
	await rm(outDir, { recursive: true, force: true });
}
