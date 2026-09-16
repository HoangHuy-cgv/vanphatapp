import { computed } from 'vue';

/**
 * S7: allowlist scheme cho URL ảnh server trả — chặn javascript:/data: lạ.
 * Cho phép: http(s), /files nội bộ, /assets, data:image (preview upload).
 */
const SAFE_URL_RE = /^(https?:\/\/|\/files\/|\/assets\/|\/api\/|data:image\/)/i;

export function isSafeArtworkUrl(url) {
	if (typeof url !== 'string' || !url.trim()) return false;
	return SAFE_URL_RE.test(url.trim());
}

export function useSafeArtworkUrl(getter) {
	return computed(() => {
		const url = typeof getter === 'function' ? getter() : getter;
		return isSafeArtworkUrl(url) ? url : '';
	});
}
