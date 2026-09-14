import { ref } from 'vue';
import { toast } from './useToast';

// ADR-006: không identity cứng — sidebar hiện trạng thái đăng nhập thật từ get_boot.
const currentUser = ref('');

export function csrfToken() {
	return window.vp_csrf_token || window.frappe_csrf_token || '';
}

/**
 * SSOT API Client for Frappe Framework & Van Phat Portal
 * Auto-prefixes method, binds CSRF token, handles GET/POST and unwraps json.message.
 * ADR-006: đường fetch DUY NHẤT trong src/ — kể cả upload FormData (không set
 * Content-Type tay để browser gắn boundary, vẫn gắn CSRF + toast + signal).
 */
export async function api(method, args = {}, options = {}) {
	try {
		let url = method;
		if (!url.startsWith('http://') && !url.startsWith('https://')) {
			if (url.startsWith('/')) {
				// already an absolute path
			} else if (
				url.startsWith('order.') ||
				url.startsWith('item.') ||
				url.startsWith('customer.') ||
				url.startsWith('supplier.') ||
				url.startsWith('user.') ||
				url.startsWith('bao_gia.')
			) {
				url = `/api/method/vanphat_portal.api.${url}`;
			} else if (url.includes('.')) {
				url = `/api/method/${url}`;
			} else {
				url = `/api/method/vanphat_portal.api.bao_gia.${url}`;
			}
		}

		const isFormData = typeof FormData !== 'undefined' && args instanceof FormData;
		const httpMethod = options.method || (options.get && !isFormData ? 'GET' : 'POST');
		const headers = {
			'X-Frappe-CSRF-Token': csrfToken(),
			...(options.headers || {}),
		};

		const fetchOptions = {
			method: httpMethod,
			headers,
			...(options.signal ? { signal: options.signal } : {}),
		};

		if (isFormData) {
			// Upload native: FormData đi body trần, browser tự gắn multipart boundary.
			fetchOptions.body = args;
		} else if (httpMethod === 'POST' || httpMethod === 'PUT') {
			headers['Content-Type'] = 'application/json';
			fetchOptions.body = JSON.stringify(args);
		} else if (httpMethod === 'GET' && Object.keys(args).length > 0) {
			const query = new URLSearchParams();
			for (const [k, v] of Object.entries(args)) {
				if (v !== undefined && v !== null) {
					query.append(k, typeof v === 'object' ? JSON.stringify(v) : String(v));
				}
			}
			const sep = url.includes('?') ? '&' : '?';
			url += `${sep}${query.toString()}`;
		}

		const res = await fetch(url, fetchOptions);
		if (!res.ok) {
			const errJson = await res.json().catch(() => ({}));
			console.warn(`[api] HTTP ${res.status} calling ${method}:`, errJson);
			if (!options.silent) {
				let msg = `Lỗi hệ thống (${res.status})`;
				if (errJson._server_messages) {
					try {
						const parsed = JSON.parse(errJson._server_messages);
						if (Array.isArray(parsed) && parsed.length > 0) {
							const item = JSON.parse(parsed[0]);
							msg = item.message || msg;
						}
					} catch (e) {}
				} else if (errJson.exception) {
					msg = errJson.exception.split(':').pop() || msg;
				}
				toast.error(msg);
			}
			return null;
		}
		const json = await res.json();
		return json.message !== undefined ? json.message : json;
	} catch (err) {
		if (err.name === 'AbortError') {
			return null;
		}
		console.warn(`[api] Network error calling ${method}:`, err);
		if (!options.silent) {
			toast.error('Không thể kết nối máy chủ ERP');
		}
		return null;
	}
}

export async function boot() {
	try {
		const data = await api('/api/method/vanphat_portal.api.bao_gia.get_boot', {}, { method: 'GET' });
		if (data) {
			if (data.csrf_token) {
				window.vp_csrf_token = data.csrf_token;
			}
			if (data.user && data.user !== 'Guest') {
				currentUser.value = data.user;
			}
		}
	} catch (err) {
		// keep going with whatever token host page provides
	}
}

export async function handleLogout() {
	try {
		await api('/api/method/logout', {}, { method: 'POST' });
	} catch (err) {
		// ignore
	}
	window.location.href = '/login';
}

export function useSession() {
	return {
		currentUser,
		csrfToken,
		api,
		boot,
		handleLogout,
	};
}
