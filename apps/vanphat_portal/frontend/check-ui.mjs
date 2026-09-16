// check-ui.mjs — Agent-first UI Design System Guard for Vue 3 SFCs.
// Inspired by @shadcn/lint: inspects Vue template AST via @vue/compiler-sfc.
// Provides precise error locations and actionable suggestions for AI Agents
// to self-correct design system violations in 1 shot.
//
// Run:
//   node check-ui.mjs

import { readdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(join(here, 'package.json'));
const sfc = require('@vue/compiler-sfc');

const FONT_SIZE_MAP = {
	'12px': 'text-xs (12px)',
	'14px': 'text-sm (14px)',
	'16px': 'text-base (16px)',
	'18px': 'text-lg (18px)',
	'20px': 'text-xl (20px)',
	'24px': 'text-2xl (24px)',
	'30px': 'text-3xl (30px)',
};

const COLOR_TOKEN_MAP = {
	'#2563eb': 'bg-primary / text-primary',
	'#1d4ed8': 'bg-primary-hover',
	'#f8fafc': 'bg-surface / bg-surface-low',
	'#ffffff': 'text-white / bg-surface',
	'#fff': 'text-white / bg-surface',
	'#000000': 'text-black',
	'#000': 'text-black',
	'#ef4444': 'bg-destructive / text-destructive',
	'#f59e0b': 'bg-warning / text-warning',
	'#10b981': 'bg-success / text-success',
};

function getAllVueFiles(dir) {
	let files = [];
	for (const entry of readdirSync(dir)) {
		const full = join(dir, entry);
		const stat = statSync(full);
		if (stat.isDirectory()) {
			files = files.concat(getAllVueFiles(full));
		} else if (entry.endsWith('.vue')) {
			files.push(full);
		}
	}
	return files;
}

export function lintVueTemplate(content, filename) {
	const parsed = sfc.parse(content, { filename });
	if (!parsed.descriptor.template) return [];

	const templateContent = parsed.descriptor.template.content;
	const compiled = sfc.compileTemplate({
		source: templateContent,
		id: filename,
		filename,
	});

	if (!compiled.ast) return [];

	const violations = [];

	function walk(node) {
		if (!node) return;

		if (node.props) {
			for (const prop of node.props) {
				// 1. Static class inspection
				if (prop.name === 'class' && prop.value?.content) {
					const classes = prop.value.content.split(/\s+/).filter(Boolean);
					for (const cls of classes) {
						// 1a. Rule: no-arbitrary-values (e.g. p-[13px], w-[350px], text-[17px])
						const arbitraryMatch = cls.match(/^([a-z0-9-]+)-\[([^\]]+)\]$/);
						if (arbitraryMatch) {
							const [, utility, val] = arbitraryMatch;
							let suggestion = 'Sử dụng class chuẩn theo spacing scale (p-2, p-3, p-4, w-full, w-80...)';
							if (utility === 'text' && FONT_SIZE_MAP[val]) {
								suggestion = `Giá trị font-size ${val} có token chuẩn: Hãy dùng "${FONT_SIZE_MAP[val]}".`;
							} else if (val.endsWith('px')) {
								const px = parseFloat(val);
								const step = px / 4;
								const nearest = Math.round(step);
								suggestion = `Giá trị ${val} (bước ${step}). Hãy dùng "${utility}-${nearest}" (${nearest * 4}px) hoặc biến thể chuẩn gần nhất.`;
							}
							violations.push({
								rule: 'design-system/no-arbitrary-values',
								line: prop.loc.start.line,
								target: cls,
								message: `Class arbitrary "${cls}" vi phạm quy chuẩn Design System của Van Phat.`,
								suggestion,
							});
						}

						// 1b. Rule: no-raw-colors (e.g. bg-[#...], text-[#...])
						const hexMatch = cls.match(/^([a-z]+)-\[(#[a-fA-F0-9]+)\]$/);
						if (hexMatch) {
							const [, utility, hex] = hexMatch;
							const mapped = COLOR_TOKEN_MAP[hex.toLowerCase()] || 'token semantic (primary, secondary, surface, outline, destructive)';
							violations.push({
								rule: 'design-system/no-raw-colors',
								line: prop.loc.start.line,
								target: cls,
								message: `Mã màu hex thô "${hex}" bị cấm.`,
								suggestion: `Thay vì "${cls}", hãy dùng token ngữ nghĩa: ${mapped}.`,
							});
						}
					}
				}

				// 2. Inline style inspection (no-inline-styles)
				// Exclude table header width definitions (th style="width: ...")
				if (prop.name === 'style') {
					const isThWidth = node.tag === 'th' || node.tag === 'col';
					if (!isThWidth) {
						const rawStyle = prop.loc.source;
						violations.push({
							rule: 'design-system/no-inline-styles',
							line: prop.loc.start.line,
							target: rawStyle,
							message: `Inline style tĩnh "${rawStyle}" không được phép trong template.`,
							suggestion: 'Chuyển các thuộc tính CSS tĩnh này thành utility class Tailwind tương ứng (ví dụ mt-4, mb-4, ml-1, relative...).',
						});
					}
				}
			}
		}

		if (node.children) {
			for (const child of node.children) {
				walk(child);
			}
		}
	}

	walk(compiled.ast);

	// 3. Scoped style inspection (no-hardcoded-hex-in-style)
	// S3: WARN-ONLY — hex cũ còn nhiều (~100+), gate chỉ cảnh báo để thay dần.
	// Không tính vào violations (không block CI). Khi nào <10 thì chuyển thành fail.
	if (parsed.descriptor.styles) {
		const HEX_RE = /#[0-9a-fA-F]{3,8}\b/g;
		let hexCount = 0;
		for (const style of parsed.descriptor.styles) {
			// Loại var(--x, #fallback) — đã var-hóa, không tính nợ;
			// giữ lại hex đứng một mình (kể cả shorthand border: 1px solid #...).
			const src = (style.content || '').replace(/var\([^)]*\)/g, 'var()');
			const lines = src.split('\n');
			lines.forEach((ln) => {
				const clean = ln.replace(/\/\*.*?\*\//g, '');
				HEX_RE.lastIndex = 0;
				while (HEX_RE.exec(clean) !== null) hexCount++;
			});
		}
		if (hexCount > 0) {
			console.log(`  [warn] ${filename}: ${hexCount} hex cứng trong <style> (thay dần bằng var(--*))`);
		}
	}

	return violations;
}

const srcDir = join(here, 'src');
const vueFiles = getAllVueFiles(srcDir);
let totalErrors = 0;

console.log(`Checking ${vueFiles.length} Vue components for Design System compliance...`);

for (const file of vueFiles) {
	const relPath = relative(here, file);
	const content = readFileSync(file, 'utf8');
	const violations = lintVueTemplate(content, relPath);

	if (violations.length > 0) {
		totalErrors += violations.length;
		console.log(`\n[FAIL] ${relPath} (${violations.length} violations):`);
		for (const v of violations) {
			console.log(`  L${v.line} [${v.rule}] ${v.target}`);
			console.log(`     -> ${v.message}`);
			console.log(`     -> Sửa: ${v.suggestion}`);
		}
	}
}

if (totalErrors === 0) {
	console.log(`\nUI DESIGN SYSTEM: PASS (${vueFiles.length}/${vueFiles.length} components clean)`);
	process.exit(0);
} else {
	console.log(`\nUI DESIGN SYSTEM: FAIL (${totalErrors} violations found across components)`);
	process.exit(1);
}
