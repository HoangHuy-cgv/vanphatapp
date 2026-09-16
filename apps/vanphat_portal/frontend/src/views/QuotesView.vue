<template>
	<div class="quotes-view-wrapper">
		<!-- Header 1 Dòng Chuẩn Cockpit: 1 Tab Chuẩn + Quick Search + Action Button -->
		<header class="page-head catalog-header-cockpit">
			<div class="order-tabs-bar catalog-tabs-bar">
				<button
					type="button"
					class="order-tab-btn active"
				>
					<span>Báo giá</span>
					<span class="tab-badge">{{ totalQuotations }}</span>
				</button>
			</div>

			<!-- Quick Search Tức Thời Cùng Hàng Header Cockpit -->
			<div class="catalog-search-cockpit-wrap">
				<div class="search-input-wrap">
					<svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<circle cx="11" cy="11" r="8"></circle>
						<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
					</svg>
					<input
						id="quote-search-input"
						name="quote_search"
						type="text"
						v-model="quoteSearchQuery"
						placeholder="Tìm nhanh số báo giá, khách..."
						aria-label="Tìm nhanh số báo giá, khách hàng"
						class="catalog-search-input"
					/>
					<button
						v-if="quoteSearchQuery"
						type="button"
						class="btn-clear-search"
						title="Xóa tìm kiếm"
						aria-label="Xóa tìm kiếm"
						@click="quoteSearchQuery = ''"
					>
						✕
					</button>
				</div>
			</div>

			<button
				type="button"
				class="btn-new-quote whitespace-nowrap flex-shrink-0"
				@click="openStep1Modal"
			>
				+ Báo giá
			</button>
		</header>

		<div class="table-container">
			<table class="data-table">
				<thead>
					<tr>
						<th style="width: 18%;">Số báo giá</th>
						<th style="width: 40%;">Khách hàng</th>
						<th style="width: 14%;">Ngày tạo</th>
						<th style="width: 16%; text-align: right;">Tổng tiền</th>
						<th style="width: 12%; text-align: center;">Trạng thái</th>
					</tr>
				</thead>
				<tbody>
					<tr v-if="loading">
						<td colspan="5" class="empty-cell">
							<div class="cockpit-empty-state">
								<span class="empty-msg">Đang tải danh sách báo giá từ ERPNext...</span>
							</div>
						</td>
					</tr>
					<tr v-else-if="!quotations.length">
						<td colspan="5" class="empty-cell">
							<div v-if="quoteSearchQuery" class="cockpit-empty-state">
								<span class="empty-msg">Không tìm thấy báo giá khớp với từ khóa "{{ quoteSearchQuery }}"</span>
								<button type="button" class="btn-empty-action" @click="quoteSearchQuery = ''">
									✕ Xóa tìm kiếm
								</button>
							</div>
							<div v-else class="cockpit-empty-state">
								<span class="empty-msg">Chưa có phiếu báo giá nào trên hệ thống</span>
								<button type="button" class="btn-empty-action btn-empty-primary" @click="openStep1Modal">
									+ Tạo báo giá R&D
								</button>
							</div>
						</td>
					</tr>
					<tr
						v-for="q in quotations"
						:key="q.name"
						class="table-row cursor-pointer"
						tabindex="0"
						role="button"
						:aria-label="'Mở báo giá ' + q.name"
						@click="onRowClick(q)"
						@keydown.enter="onRowClick(q)"
						@keydown.space.prevent="onRowClick(q)"
					>
						<td class="font-bold text-primary whitespace-nowrap">{{ q.name }}</td>
						<td class="whitespace-nowrap truncate" :title="q.customer_name || q.party_name">
							<span class="font-medium text-white">{{ q.customer_name || q.party_name || 'Khách vãng lai' }}</span>
						</td>
						<td class="text-secondary text-num whitespace-nowrap">{{ q.transaction_date }}</td>
						<td class="text-right font-bold text-num whitespace-nowrap">{{ formatCurrency(q.grand_total) }}</td>
						<td class="text-center whitespace-nowrap">
							<span class="font-bold text-sm" :class="quoteStatusColorClass(q.status)">
								{{ quoteStatusLabel(q.status) }}
							</span>
						</td>
					</tr>
					<TableFiller
						:shown="quotations.length"
						:page-size="pageSize"
						:colspan="5"
						prefix="quote"
					/>
				</tbody>
			</table>
		</div>

		<!-- Phân trang tối giản (BasePagination: số căn giữa, không khung) -->
		<div class="cockpit-pagination-bar">
			<BasePagination
				:page="currentPage"
				:total-pages="totalPages"
				:loading="loading"
				@prev="prevPage"
				@next="nextPage"
				@goto="gotoPage"
			/>
		</div>

		<!-- Step 1 & Step 2 Dialogs (S8: Suspense cho async chunk) -->
		<Suspense v-if="showStep1">
			<ModalStep1Sale
				:open="showStep1"
				:initial-data="step1Data"
				:product-types="productTypes"
				:print-techs="printTechs"
				:accessories="accessories"
				@close="showStep1 = false"
				@submit="onStep1Complete"
			/>
			<template #fallback>
				<div class="cockpit-empty-state" aria-busy="true">
					<span class="empty-msg">Đang tải form...</span>
				</div>
			</template>
		</Suspense>

		<Suspense v-if="showStep2">
			<DrawerStep2Director
				:open="showStep2"
				:form-data="step1Data"
				:saved-data="step2Data"
				:preview-figures="figures"
				:calculation-result="calcResult"
				@close="showStep2 = false"
				@back="onStep2Back"
				@items-changed="onItemsChanged"
				@submit="onQuotationSubmit"
			/>
			<template #fallback>
				<div class="cockpit-empty-state" aria-busy="true">
					<span class="empty-msg">Đang tải chi tiết...</span>
				</div>
			</template>
		</Suspense>
	</div>
</template>

<script setup>
import { onMounted, onUnmounted, defineAsyncComponent } from 'vue';
import { useRouter } from 'vue-router';
import BasePagination from '../components/BasePagination.vue';
import TableFiller from '../components/TableFiller.vue';
import { dialog } from '../composables/useConfirmDialog';
// S8: drawers/modals nặng async — chunk riêng, render khi mở
const ModalStep1Sale = defineAsyncComponent(() => import('../components/ModalStep1Sale.vue'));
const DrawerStep2Director = defineAsyncComponent(() => import('../components/DrawerStep2Director.vue'));
import { useCockpitFormat } from '../composables/useCockpitFormat';
import { useQuotesFlow } from '../composables/useQuotesFlow';

const router = useRouter();
// S7c: formatter + status helpers dùng chung (xóa bản copy-paste)
const { formatCurrency, quoteStatusLabel, quoteStatusColorClass } = useCockpitFormat();

// Task 7: view chỉ còn composition + render — flow báo giá trong composable.
const {
	quotations,
	loading,
	quoteSearchQuery,
	currentPage,
	pageSize,
	totalQuotations,
	totalPages,
	showStep1,
	showStep2,
	productTypes,
	printTechs,
	accessories,
	step1Data,
	step2Data,
	figures,
	calcResult,
	prevPage,
	nextPage,
	gotoPage,
	handleKeyDown,
	loadQuotations,
	loadQuoteDefaults,
	onRowClick: onRowClickFlow,
	openStep1Modal,
	onStep1Complete,
	onStep2Back,
	onItemsChanged,
	onQuotationSubmit,
	onMakeOrder,
	cleanup,
} = useQuotesFlow(router);

// Wrapper mỏng: template gọi onRowClick(q) — dialog + make-order nối từ view scope.
function onRowClick(q) {
	onRowClickFlow(q, { onMakeOrder, dialog });
}

onMounted(async () => {
	window.addEventListener('keydown', handleKeyDown);
	await Promise.all([loadQuotations(), loadQuoteDefaults()]);
});

onUnmounted(() => {
	cleanup();
	window.removeEventListener('keydown', handleKeyDown);
});

</script>

<style scoped>
.quotes-view-wrapper {
	display: flex;
	flex-direction: column;
	flex: 1;
	min-height: 0;
}
</style>
