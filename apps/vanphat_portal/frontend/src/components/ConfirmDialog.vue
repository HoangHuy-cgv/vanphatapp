<template>
	<BaseModal :open="dialogState.open" :label="dialogState.title" @close="handleCancel">
		<div class="confirm-card" role="alertdialog" :aria-labelledby="dialogState.type === 'prompt' ? undefined : 'confirm-title'" :aria-describedby="'confirm-msg'" :aria-label="dialogState.type === 'prompt' ? dialogState.title : undefined">
			<div class="confirm-head">
				<h3 id="confirm-title" class="confirm-title">{{ dialogState.title }}</h3>
				<button type="button" class="btn-icon" title="Đóng (Esc)" aria-label="Đóng hộp thoại (Esc)" @click="handleCancel">
					✕
				</button>
			</div>
			<div class="confirm-body">
				<p id="confirm-msg" class="confirm-msg">{{ dialogState.message }}</p>
				<div v-if="dialogState.type === 'prompt'" class="prompt-input-wrap">
					<label class="prompt-label" :for="dialogState.inputId">{{ dialogState.inputPlaceholder || dialogState.message || 'Nhập thông tin' }}</label>
					<input
						:id="dialogState.inputId"
						name="confirm_prompt_value"
						v-model="dialogState.inputValue"
						type="text"
						class="prompt-input"
						:placeholder="dialogState.inputPlaceholder"
						:aria-label="dialogState.inputPlaceholder || dialogState.message || 'Nhập thông tin'"
						autofocus
						@keydown.enter="handleConfirm"
					/>
				</div>
			</div>
			<div class="confirm-actions">
				<button type="button" class="btn-cancel" @click="handleCancel">
					{{ dialogState.cancelLabel }}
				</button>
				<button type="button" class="btn-confirm" @click="handleConfirm">
					{{ dialogState.confirmLabel }}
				</button>
			</div>
		</div>
	</BaseModal>
</template>

<script setup>
import BaseModal from './BaseModal.vue';
import { useConfirmDialog } from '../composables/useConfirmDialog';

const { dialogState, handleConfirm, handleCancel } = useConfirmDialog();
</script>

<style scoped>
.confirm-card {
	width: 420px;
	max-width: 90vw;
	background: #161b22;
	border: 1px solid #3a424e;
	border-radius: 12px;
	box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
	overflow: hidden;
	display: flex;
	flex-direction: column;
}

.confirm-head {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 16px 20px 12px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.confirm-title {
	font-size: 16px;
	font-weight: 700;
	color: #fff;
	margin: 0;
}

.btn-icon {
	background: transparent;
	border: none;
	color: #8b949e;
	cursor: pointer;
	padding: 4px 8px;
	font-size: 14px;
	border-radius: 4px;
}

.btn-icon:hover {
	color: #fff;
}

.confirm-body {
	padding: 18px 20px;
}

.confirm-msg {
	color: #c9d1d9;
	font-size: 14px;
	line-height: 1.5;
	margin: 0;
}

.prompt-input-wrap {
	margin-top: 12px;
}

.prompt-label {
	display: block;
	font-size: 13px;
	font-weight: 600;
	color: #9da7b5;
	margin-bottom: 6px;
}

.prompt-input {
	width: 100%;
	padding: 8px 12px;
	background: #0d1117;
	border: 1px solid #3a424e;
	border-radius: 6px;
	color: #fff;
	font-size: 14px;
	outline: none;
}

.prompt-input:focus {
	border-color: #38bdf8;
}

.confirm-actions {
	display: flex;
	justify-content: flex-end;
	gap: 10px;
	padding: 12px 20px 16px;
	background: #11151c;
	border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.btn-cancel {
	padding: 6px 14px;
	border-radius: 6px;
	background: transparent;
	border: 1px solid #3a424e;
	color: #c9d1d9;
	cursor: pointer;
	font-size: 13px;
	font-weight: 600;
}

.btn-cancel:hover {
	background: rgba(255, 255, 255, 0.05);
	color: #fff;
}

.btn-confirm {
	padding: 6px 16px;
	border-radius: 6px;
	background: #2563eb;
	border: none;
	color: #fff;
	cursor: pointer;
	font-size: 13px;
	font-weight: 600;
}

.btn-confirm:hover {
	background: #1d4ed8;
}
</style>
