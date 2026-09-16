<template>
	<DetailShell :open="isOpen" label="Chi tiết người dùng" accent="#a78bfa" @close="$emit('close')">
		<template #head>
			<span class="vp-code-badge vp-mono">{{ user ? user.role_profile_name : '' }}</span>
			<span v-if="user && user.enabled" class="badge-status-active">
				Hoạt động
			</span>
		</template>

		<div v-if="user">
			<DetailHero :title="user.full_name" :sub="user.email" sub-class="vp-mono vp-accent" />

			<DetailCard class="mt-3">
				<DetailSpecGrid :cells="specCells" />
			</DetailCard>

			<DetailCard class="mt-3" title="VAI TRÒ & PHÂN QUYỀN ERPNEXT NATIVE">
				<div class="roles-wrap">
					<span
						v-for="(r, idx) in parsedRoles"
						:key="idx"
						class="role-pill vp-mono"
					>
						{{ r }}
					</span>
				</div>
			</DetailCard>

			<DetailCard v-if="user.alias" class="mt-3" title="BÍ DANH NHẬN DIỆN (ALIASES)">
				<div class="aliases-wrap">
					<span
						v-for="(a, idx) in user.alias.split('|')"
						:key="idx"
						class="alias-pill"
					>
						{{ a }}
					</span>
				</div>
			</DetailCard>
		</div>
	</DetailShell>
</template>

<script setup>
import { computed } from 'vue';
import DetailShell from './DetailShell.vue';
import DetailHero from './DetailHero.vue';
import DetailCard from './DetailCard.vue';
import DetailSpecGrid from './DetailSpecGrid.vue';

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

// Spec phòng ban/chức danh — Drawer tự chốt chuỗi hiển thị (visual only).
const specCells = computed(() => {
	const u = props.user;
	if (!u) return [];
	return [
		{ label: 'Phòng ban', value: u.department || 'Nội bộ', cls: 'text-white font-medium' },
		{ label: 'Chức danh', value: u.designation || 'Nhân viên', cls: 'vp-accent font-medium' },
		{ label: 'Số điện thoại', value: u.mobile_no || '—', cls: 'vp-mono' },
		{ label: 'Loại tài khoản', value: u.user_type || 'System User', cls: 'vp-mono' },
	];
});

const parsedRoles = computed(() => {
	if (!props.user) return [];
	const r = props.user.roles || props.user.role || '';
	return r.split(',').map(x => x.trim()).filter(Boolean);
});

// P4 thí điểm: BaseDrawer native <dialog> lo Esc/focus/inert — xóa composable thủ công
</script>

<style scoped>
.badge-status-active {
	color: var(--ok);
	font-size: 12px;
	font-weight: 600;
}

.roles-wrap {
	display: flex;
	flex-wrap: wrap;
	gap: 6px;
}

.role-pill {
	font-size: 14px;
	font-weight: 700;
	color: var(--violet-pale);
}

.aliases-wrap {
	display: flex;
	flex-wrap: wrap;
	gap: 10px;
}

.alias-pill {
	font-size: 14px;
	font-weight: 600;
	color: var(--ink-slate);
}
</style>
