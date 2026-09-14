<template>
	<Teleport to="body">
		<div class="cockpit-toast-container" aria-live="polite" aria-atomic="true">
			<TransitionGroup name="cockpit-toast-slide">
				<div
					v-for="t in toasts"
					:key="t.id"
					class="cockpit-toast-item"
					:class="`toast-${t.type}`"
				>
					<span class="toast-indicator"></span>
					<span class="toast-message">{{ t.message }}</span>
					<button
						type="button"
						class="toast-btn-close"
						title="Đóng"
						@click="dismiss(t.id)"
					>
						✕
					</button>
				</div>
			</TransitionGroup>
		</div>
	</Teleport>
</template>

<script setup>
import { useToast } from '../composables/useToast';

const { toasts, dismiss } = useToast();
</script>

<style scoped>
.cockpit-toast-container {
	position: fixed;
	top: 18px;
	right: 20px;
	z-index: 99999;
	display: flex;
	flex-direction: column;
	gap: 8px;
	pointer-events: none;
}

.cockpit-toast-item {
	pointer-events: auto;
	display: inline-flex;
	align-items: center;
	gap: 10px;
	min-height: 38px;
	max-width: 420px;
	padding: 8px 14px;
	border-radius: 6px;
	background: rgba(11, 15, 25, 0.95);
	backdrop-filter: blur(10px);
	box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
	font-size: 13.5px;
	font-weight: 600;
	letter-spacing: -0.01em;
	transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-indicator {
	width: 7px;
	height: 7px;
	border-radius: 50%;
	flex-shrink: 0;
}

.toast-message {
	flex: 1;
	color: #f1f5f9;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.toast-btn-close {
	background: transparent;
	border: none;
	color: #9ca3af;
	cursor: pointer;
	font-size: 12px;
	padding: 2px 4px;
	margin-left: 4px;
	border-radius: 4px;
	transition: color 0.15s ease;
	line-height: 1;
}

.toast-btn-close:hover {
	color: #ffffff;
}

/* Variants */
.toast-success {
	border: 1px solid rgba(110, 231, 183, 0.35);
}
.toast-success .toast-indicator {
	background: #6ee7b7;
	box-shadow: 0 0 8px #6ee7b7;
}

.toast-error {
	border: 1px solid rgba(248, 113, 113, 0.4);
}
.toast-error .toast-indicator {
	background: #f87171;
	box-shadow: 0 0 8px #f87171;
}

.toast-warning {
	border: 1px solid rgba(251, 191, 36, 0.35);
}
.toast-warning .toast-indicator {
	background: #fbbf24;
	box-shadow: 0 0 8px #fbbf24;
}

.toast-info {
	border: 1px solid rgba(78, 161, 224, 0.35);
}
.toast-info .toast-indicator {
	background: #7dd3fc;
	box-shadow: 0 0 8px #7dd3fc;
}

/* Animations */
.cockpit-toast-slide-enter-active,
.cockpit-toast-slide-leave-active {
	transition: all 0.22s ease-out;
}

.cockpit-toast-slide-enter-from {
	opacity: 0;
	transform: translateY(-10px) scale(0.96);
}

.cockpit-toast-slide-leave-to {
	opacity: 0;
	transform: translateX(20px) scale(0.96);
}
</style>
