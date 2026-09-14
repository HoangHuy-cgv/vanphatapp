import { ref } from 'vue';

const currentUser = ref('giamdoc@vanphat.com');

export function csrfToken() {
	return window.vp_csrf_token || window.frappe_csrf_token || '';
}

/**
 * SSOT API Client for Frappe Framework & Van Phat Portal
 * Auto-prefixes method, binds CSRF token, handles GET/POST and unwraps json.message.
 */
export async function api(method, args = {}, options = {}) {
	try {
		let url = method;
		if (!url.startsWith('http://') && !url.startsWith('https://')) {
			if (url.startsWith('/')) {
				// already an absolute path
			} else if (url.includes('.')) {
				url = `/api/method/${url}`;
			} else {
				url = `/api/method/vanphat_portal.api.bao_gia.${url}`;
			}
		}

		const httpMethod = options.method || (options.get ? 'GET' : 'POST');
		const headers = {
			'X-Frappe-CSRF-Token': csrfToken(),
			...(options.headers || {}),
		};

		const fetchOptions = {
			method: httpMethod,
			headers,
		};

		if (httpMethod === 'POST' || httpMethod === 'PUT') {
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
			return null;
		}
		const json = await res.json();
		return json.message !== undefined ? json.message : json;
	} catch (err) {
		console.warn(`[api] Network error calling ${method}:`, err);
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
