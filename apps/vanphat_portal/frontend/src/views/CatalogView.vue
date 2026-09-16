<template>
	<div class="catalog-view-wrapper">
		<!-- Header Danh Mục: Tabs + Search + Action (1 dòng) -->
		<header class="page-head catalog-header-cockpit">
			<div class="order-tabs-bar catalog-tabs-bar">
				<button
					type="button"
					class="order-tab-btn"
					:class="{ active: catalog.isProductTab.value }"
					@click="catalog.switchCatalogTab('sp')"
				>
					<span>Sản phẩm</span>
					<span class="tab-badge">{{ catalog.totalRecords.value }}</span>
				</button>
				<button
					v-for="t in catalog.blankTabs.value"
					:key="t.key"
					type="button"
					class="order-tab-btn"
					:class="{ active: catalog.activeCatalogTab.value === t.key }"
					@click="catalog.switchCatalogTab(t.key)"
				>
					<span>{{ t.label }}</span>
				</button>
			</div>

			<!-- Thanh Tìm Kiếm Tức Thời (chỉ tab Sản phẩm; 5 tab còn lại chờ nhân bản) -->
			<div v-if="catalog.isProductTab.value" class="catalog-search-cockpit-wrap">
				<div class="search-input-wrap">
					<svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<circle cx="11" cy="11" r="8"></circle>
						<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
					</svg>
					<input
						id="catalog-search-input"
						name="catalog_search"
						type="text"
						class="catalog-search-input"
						v-model="catalog.searchQuery.value"
						placeholder="Tìm tên gọi, mã biến thể KH..."
						aria-label="Tìm kiếm danh mục"
					/>
					<button
						v-if="catalog.searchQuery.value"
						type="button"
						class="btn-clear-search"
						title="Xóa tìm kiếm"
						aria-label="Xóa tìm kiếm"
						@click="catalog.searchQuery.value = ''"
					>✕</button>
				</div>
			</div>

			<!-- Nút Hành Động Thêm Mới Chuẩn Cockpit -->
			<button
				v-if="catalog.isProductTab.value"
				type="button"
				class="btn-new-quote whitespace-nowrap flex-shrink-0"
				@click="onAddNew"
			>
				+ Thêm sản phẩm
			</button>
		</header>

		<!-- Bảng Sản phẩm (baseline — 5 tab còn lại chờ nhân bản) -->
		<div
			v-if="catalog.isProductTab.value"
			:key="'sp'"
			class="table-container"
		>
			<table class="data-table">
				<thead>
					<tr>
						<th style="width: 35%;">Tên gọi quen</th>
						<th style="width: 21%;">Chất liệu</th>
						<th style="width: 20%;">Kích thước (R x D x Dày)</th>
						<th style="width: 11%; text-align: center;">Đáy</th>
						<th style="width: 7%; text-align: center;">ĐVT</th>
					</tr>
				</thead>
				<tbody>
					<tr
						v-for="it in catalog.items.value"
						:key="it.item_code"
						class="table-row cursor-pointer"
						tabindex="0"
						role="button"
						:aria-label="'Mở chi tiết ' + (it.custom_alias || it.item_name || it.item_code)"
						@click="catalog.openItemDetail(it)"
						@keydown.enter="catalog.openItemDetail(it)"
						@keydown.space.prevent="catalog.openItemDetail(it)"
					>
						<!-- Tên gọi quen (mã nội bộ + tên pháp lý chỉ tooltip; mã biến thể KH chỉ trong drawer) -->
						<td>
							<div class="font-semibold text-white leading-tight text-[15px]" :title="(it.item_name || '') + ' [' + (it.item_code || '') + ']'">
								{{ it.custom_alias || it.item_name || '—' }}
							</div>
						</td>

						<!-- Chất liệu (Đơn dòng tinh gọn) -->
						<td>
							<div class="text-sm text-amber font-mono font-semibold truncate" :title="it.custom_structure_layers || it.description || '—'">
								{{ it.custom_structure_layers || it.description || '—' }}
							</div>
						</td>

						<!-- Kích thước (R x D x Dày) -->
						<td class="text-sm font-mono">
							<span class="text-white font-medium">{{ catalog.getItemDimensionsText(it) }}</span>
						</td>

						<!-- Đáy (Tách riêng cột) -->
						<td class="text-center font-mono text-sm">
							<span v-if="catalog.getItemGussetText(it)" class="text-amber font-semibold">
								{{ catalog.getItemGussetText(it) }}
							</span>
							<span v-else class="text-secondary/40">—</span>
						</td>

						<!-- ĐVT -->
						<td class="text-center font-mono text-sm text-secondary">
							{{ it.stock_uom || 'Túi' }}
						</td>
					</tr>
					<TableFiller
						:shown="catalog.items.value.length"
						:page-size="catalog.pageSize"
						:colspan="5"
						prefix="it"
					/>
					<tr v-if="catalog.items.value.length === 0">
						<td colspan="5" class="empty-cell">
							<div v-if="catalog.loadingItems.value" class="cockpit-empty-state">
								<span class="empty-msg">Đang tải danh mục từ ERPNext...</span>
							</div>
							<div v-else-if="catalog.searchQuery.value" class="cockpit-empty-state">
								<span class="empty-msg">Không tìm thấy mặt hàng khớp với "{{ catalog.searchQuery.value }}"</span>
								<button type="button" class="btn-empty-action" @click="catalog.searchQuery.value = ''">
									✕ Xóa tìm kiếm
								</button>
							</div>
							<div v-else class="cockpit-empty-state">
								<span class="empty-msg">Chưa có dữ liệu trong mục Sản phẩm</span>
								<button type="button" class="btn-empty-action btn-empty-primary" @click="onAddNew">
									+ Thêm sản phẩm
								</button>
							</div>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- 5 tab chờ nhân bản: trắng, truthful -->
		<div
			v-else
			:key="catalog.activeCatalogTab.value"
			class="table-container"
		>
			<table class="data-table">
				<tbody>
					<tr>
						<td class="empty-cell">
							<div class="cockpit-empty-state">
								<span class="empty-msg">Mục {{ catalog.blankTabLabel.value }} đang chờ nhân bản từ tab Sản phẩm.</span>
							</div>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Phân trang tối giản (BasePagination: số căn giữa, không khung) -->
		<div v-if="catalog.isProductTab.value" class="cockpit-pagination-bar">
			<BasePagination
				:page="catalog.currentPage.value"
				:total-pages="catalog.totalPages.value"
				:loading="catalog.loadingItems.value"
				@prev="catalog.prevPage"
				@next="catalog.nextPage"
				@goto="catalog.gotoPage"
			/>
		</div>

		<!-- Slide-over Drawer chi tiết mặt hàng (async chunk + Suspense, chỉ mount khi mở) -->
		<Suspense v-if="catalog.showItemDrawer.value">
			<DrawerItemDetail
				:is-open="catalog.showItemDrawer.value"
				:open="catalog.showItemDrawer.value"
				:item="catalog.selectedItem.value"
				:bom="catalog.selectedBom.value"
				:loading="catalog.loadingDetail.value"
				@close="catalog.showItemDrawer.value = false"
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
const DrawerItemDetail = defineAsyncComponent(() => import('../components/DrawerItemDetail.vue'));
import BasePagination from '../components/BasePagination.vue';
import TableFiller from '../components/TableFiller.vue';
import { useCatalogView } from '../composables/useCatalogView';

const emit = defineEmits(['add-new']);

// View chỉ còn composition + render — logic list/route/toast trong composable.
const { catalog, onAddNew, init, cleanup } = useCatalogView(emit);

onMounted(async () => {
	await init();
});

onUnmounted(() => {
	cleanup();
});

</script>

<style scoped>
.catalog-view-wrapper {
	display: flex;
	flex-direction: column;
	flex: 1;
	min-height: 0;
}
</style>
