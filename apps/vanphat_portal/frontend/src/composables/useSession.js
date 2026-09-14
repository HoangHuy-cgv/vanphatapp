import { ref } from 'vue';

const currentUser = ref('giamdoc@vanphat.com');

export function csrfToken() {
	return window.vp_csrf_token || window.frappe_csrf_token || '';
}

export async function api(method, args = {}) {
	try {
		const res = await fetch(`/api/method/vanphat_portal.api.bao_gia.${method}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-Frappe-CSRF-Token': csrfToken(),
			},
			body: JSON.stringify(args),
		});
		const json = await res.json();
		return json.message;
	} catch (err) {
		return null;
	}
}

export async function boot() {
	try {
		const res = await fetch('/api/method/vanphat_portal.api.bao_gia.get_boot');
		const json = await res.json();
		if (json && json.message) {
			if (json.message.csrf_token) {
				window.vp_csrf_token = json.message.csrf_token;
			}
			if (json.message.user && json.message.user !== 'Guest') {
				currentUser.value = json.message.user;
			}
		}
	} catch (err) {
		// keep going with whatever token the host page provides
	}
}

export async function handleLogout() {
	try {
		await fetch('/api/method/logout', {
			method: 'POST',
			headers: {
				'X-Frappe-CSRF-Token': csrfToken(),
			},
		});
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
