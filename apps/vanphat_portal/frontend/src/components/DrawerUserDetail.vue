<template>
	<Teleport to="body">
		<div v-if="isOpen" class="drawer-overlay" @click.self="$emit('close')">
		<aside class="drawer-panel" aria-label="Chi tiết người dùng">
			<!-- Header -->
			<div class="drawer-head">
				<div class="head-left">
					<span class="user-role-badge font-mono">{{ user ? user.role_profile_name : '' }}</span>
					<span v-if="user && user.enabled" class="badge-status-active">
						● Hoạt động
					</span>
				</div>
				<button
					type="button"
					class="btn-icon"
					title="Đóng (Esc)"
					@click="$emit('close')"
				>
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<line x1="18" y1="6" x2="6" y2="18"></line>
						<line x1="6" y1="6" x2="18" y2="18"></line>
					</svg>
				</button>
			</div>

			<!-- Body -->
			<div v-if="user" class="drawer-body">
				<!-- Hero -->
				<div class="hero-block">
					<div class="hero-title">
						{{ user.full_name }}
					</div>
					<div class="hero-sub font-mono text-primary">
						{{ user.email }}
					</div>
				</div>

				<!-- Section: Department & Role -->
				<div class="cockpit-card">
					<div class="spec-grid">
						<div class="spec-cell">
							<span class="cell-label">Phòng ban</span>
							<span class="cell-val text-white font-medium">{{ user.department || 'Nội bộ' }}</span>
						</div>
						<div class="spec-cell">
							<span class="cell-label">Chức danh</span>
							<span class="cell-val text-primary font-medium">{{ user.designation || 'Nhân viên' }}</span>
						</div>
						<div class="spec-cell">
							<span class="cell-label">Số điện thoại</span>
							<span class="cell-val font-mono">{{ user.mobile_no || '—' }}</span>
						</div>
						<div class="spec-cell">
							<span class="cell-label">Loại tài khoản</span>
							<span class="cell-val font-mono">{{ user.user_type || 'System User' }}</span>
						</div>
					</div>
				</div>

				<!-- Section: ERPNext Native Roles -->
				<div class="cockpit-card">
					<div class="card-head-simple">
						<span>VAI TRÒ & PHÂN QUYỀN ERPNEXT NATIVE</span>
					</div>
					<div class="roles-wrap">
						<span
							v-for="(r, idx) in parsedRoles"
							:key="idx"
							class="role-pill font-mono"
						>
							{{ r }}
						</span>
					</div>
				</div>

				<!-- Section: Aliases for system mapping -->
				<div v-if="user.alias" class="cockpit-card">
					<div class="card-head-simple">
						<span>BÍ DANH NHẬN DIỆN (ALIASES)</span>
					</div>
					<div class="aliases-wrap">
						<span
							v-for="(a, idx) in user.alias.split('|')"
							:key="idx"
							class="alias-pill"
						>
							{{ a }}
						</span>
					</div>
				</div>
			</div>
		</aside>
		</div>
	</Teleport>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({
	isOpen: {
		type: Boolean,
		default: false
	},
	user: {
		type: Object,
		default: null
	}
});

const emit = defineEmits(['close']);

const parsedRoles = computed(() => {
	if (!props.user) return [];
	const r = props.user.roles || props.user.role || '';
	return r.split(',').map(x => x.trim()).filter(Boolean);
});

function handleKeydown(e) {
	if (e.key === 'Escape' && props.isOpen) {
		emit('close');
	}
}

onMounted(() => {
	window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
	window.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
.drawer-overlay {
	position: fixed;
	inset: 0;
	z-index: 999;
	background: rgba(0, 0, 0, 0.65);
	backdrop-filter: blur(2px);
	display: flex;
	justify-content: flex-end;
}

.drawer-panel {
	width: 500px;
	max-width: 100vw;
	height: 100vh;
	background: #161b22;
	border-left: 1px solid #3a424e;
	box-shadow: -8px 0 32px rgba(0, 0, 0, 0.6);
	display: flex;
	flex-direction: column;
	animation: slideInRight 0.22s ease-out;
	overflow-y: auto;
}

@keyframes slideInRight {
	from {
		transform: translateX(100%);
	}
	to {
		transform: translateX(0);
	}
}

.drawer-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 14px 20px;
	background: #11151c;
	border-bottom: 1px solid #3a424e;
	flex-shrink: 0;
}

.head-left {
	display: flex;
	align-items: center;
	gap: 10px;
}

.user-role-badge {
	padding: 3px 8px;
	border-radius: 4px;
	background: #1a2333;
	color: #a78bfa;
	font-weight: 700;
	font-size: 13px;
	border: 1px solid rgba(167, 139, 250, 0.3);
}

.badge-status-active {
	color: #10b981;
	font-size: 12px;
	font-weight: 600;
}

.btn-icon {
	background: transparent;
	border: none;
	color: #94a3b8;
	cursor: pointer;
	padding: 4px;
	border-radius: 4px;
	display: inline-flex;
	align-items: center;
	justify-content: center;
	transition: color 0.15s;
}

.btn-icon:hover {
	color: #ffffff;
}

.drawer-body {
	padding: 20px;
	display: flex;
	flex-direction: column;
	gap: 14px;
	flex: 1;
}

.hero-block {
	padding-bottom: 12px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.hero-title {
	font-size: 20px;
	font-weight: 700;
	color: #ffffff;
	line-height: 1.3;
}

.hero-sub {
	font-size: 13.5px;
	margin-top: 4px;
}

.cockpit-card {
	background: #1a1f27;
	border: 1px solid #3a424e;
	border-radius: 6px;
	padding: 14px 16px;
}

.spec-grid {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 12px;
}

.spec-cell {
	display: flex;
	flex-direction: column;
	gap: 3px;
}

.cell-label {
	font-size: 11.5px;
	text-transform: uppercase;
	color: #64748b;
	letter-spacing: 0.04em;
	font-weight: 600;
}

.cell-val {
	font-size: 13.5px;
	color: #e2e8f0;
}

.card-head-simple {
	font-size: 12px;
	font-weight: 700;
	color: #64748b;
	letter-spacing: 0.05em;
	margin-bottom: 10px;
}

.roles-wrap {
	display: flex;
	flex-wrap: wrap;
	gap: 6px;
}

.role-pill {
	font-size: 14px;
	font-weight: 700;
	color: #c4b5fd;
}

.aliases-wrap {
	display: flex;
	flex-wrap: wrap;
	gap: 10px;
}

.alias-pill {
	font-size: 14px;
	font-weight: 600;
	color: #94a3b8;
}

.text-primary {
	color: #a78bfa;
}

.text-secondary {
	color: #94a3b8;
}

.font-mono {
	font-family: inherit;
	font-variant-numeric: tabular-nums;
	font-feature-settings: "tnum";
}
</style>
