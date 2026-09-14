<template>
	<div class="portal-layout">
		<!-- Sidebar Navigation -->
	<aside class="sidebar">
		<div class="brand-block">
			<img :src="logoUrl" alt="Bao Bì Vạn Phát" class="brand-logo" />
			<div class="brand-title">BAO BÌ VẠN PHÁT</div>
		</div>

		<nav class="nav-menu">
			<button type="button" class="nav-btn">
				<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<rect x="3" y="3" width="7" height="7"></rect>
					<rect x="14" y="3" width="7" height="7"></rect>
					<rect x="14" y="14" width="7" height="7"></rect>
					<rect x="3" y="14" width="7" height="7"></rect>
				</svg>
				<span class="nav-text">Tổng quan</span>
			</button>
			<button
				type="button"
				class="nav-btn"
				:class="{ active: view === 'quotes' }"
				@click="view = 'quotes'; loadQuotations()"
			>
				<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
					<polyline points="14 2 14 8 20 8"></polyline>
					<line x1="16" y1="13" x2="8" y2="13"></line>
					<line x1="16" y1="17" x2="8" y2="17"></line>
					<polyline points="10 9 9 9 8 9"></polyline>
				</svg>
				<span class="nav-text">Báo giá</span>
				<span v-if="quotations.length" class="nav-badge">{{ quotations.length }}</span>
			</button>
			<button
				type="button"
				class="nav-btn"
				:class="{ active: view === 'orders' }"
				@click="view = 'orders'; loadOrders()"
			>
				<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<line x1="16.5" y1="9.4" x2="7.5" y2="4.21"></line>
					<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
					<polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
					<line x1="12" y1="22.08" x2="12" y2="12"></line>
				</svg>
				<span class="nav-text">Đơn hàng</span>
				<span v-if="orders.length" class="nav-badge">{{ orders.length }}</span>
			</button>
			<button type="button" class="nav-btn">
				<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
					<polyline points="2 17 12 22 22 17"></polyline>
					<polyline points="2 12 12 17 22 12"></polyline>
				</svg>
				<span class="nav-text">Sản xuất</span>
			</button>
			<button
				type="button"
				class="nav-btn"
				:class="{ active: isCatalogView }"
				@click="view = 'catalog'; loadAllCatalogData()"
			>
				<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
					<line x1="3" y1="9" x2="21" y2="9"></line>
					<line x1="9" y1="21" x2="9" y2="9"></line>
				</svg>
				<span class="nav-text">Danh mục</span>
				<span v-if="catalogTotalCount" class="nav-badge">{{ catalogTotalCount }}</span>
			</button>
		</nav>

		<!-- Bottom User & Logout -->
		<div class="sidebar-footer">
			<div class="user-block" :title="currentUser">
				<div class="user-avatar">
					<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
						<circle cx="12" cy="7" r="4"></circle>
					</svg>
				</div>
				<span class="user-id">{{ currentUser }}</span>
			</div>
			<button
				type="button"
				class="btn-logout"
				title="Đăng xuất"
				@click="handleLogout"
			>
				<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
					<polyline points="16 17 21 12 16 7"></polyline>
					<line x1="21" y1="12" x2="9" y2="12"></line>
				</svg>
			</button>
		</div>
	</aside>

		<!-- Main Content Area -->
		<main class="main-content">
			<!-- Header Báo giá & Đơn hàng -->
			<header v-if="view === 'quotes' || view === 'orders'" class="page-head">
				<h2 class="page-title">{{ view === 'orders' ? 'Đơn hàng' : 'Báo giá' }}</h2>
				<button
					v-if="view === 'quotes'"
					type="button"
					class="btn-new-quote"
					@click="openStep1Modal"
				>
					+ Báo giá
				</button>
				<button
					v-else-if="view === 'orders'"
					type="button"
					class="btn-new-quote"
					@click="showCreateOrderModal = true"
				>
					+ Tạo đơn hàng
				</button>
			</header>

			<!-- Header Danh Mục Thống Nhất: 6 Tab Buồng Lái Chuẩn SSOT + Sub-filters + Search -->
			<header v-else-if="isCatalogView" class="page-head catalog-header-cockpit">
				<div class="order-tabs-bar catalog-tabs-bar">
					<button
						type="button"
						class="order-tab-btn"
						:class="{ active: activeCatalogTab === 'sp' }"
						@click="switchCatalogTab('sp')"
					>
						<span>Sản phẩm</span>
						<span class="tab-badge">{{ productItems.length }}</span>
					</button>
					<button
						type="button"
						class="order-tab-btn"
						:class="{ active: activeCatalogTab === 'nvl' }"
						@click="switchCatalogTab('nvl')"
					>
						<span>Nguyên vật liệu</span>
						<span class="tab-badge">{{ nvlItems.length }}</span>
					</button>
					<button
						type="button"
						class="order-tab-btn"
						:class="{ active: activeCatalogTab === 'truc' }"
						@click="switchCatalogTab('truc')"
					>
						<span>Trục in</span>
						<span class="tab-badge">{{ trucItems.length }}</span>
					</button>
					<button
						type="button"
						class="order-tab-btn"
						:class="{ active: activeCatalogTab === 'kh' }"
						@click="switchCatalogTab('kh')"
					>
						<span>Khách hàng</span>
						<span class="tab-badge">{{ customers.length }}</span>
					</button>
					<button
						type="button"
						class="order-tab-btn"
						:class="{ active: activeCatalogTab === 'ncc' }"
						@click="switchCatalogTab('ncc')"
					>
						<span>Nhà cung cấp</span>
						<span class="tab-badge">{{ suppliers.length }}</span>
					</button>
					<button
						type="button"
						class="order-tab-btn"
						:class="{ active: activeCatalogTab === 'user' }"
						@click="switchCatalogTab('user')"
					>
						<span>Người dùng</span>
						<span class="tab-badge">{{ users.length }}</span>
					</button>
				</div>

				<!-- Cockpit Search Input: Tinh gọn không kèm badge count -->
				<div class="catalog-search-cockpit-wrap">
					<div class="search-input-wrap">
						<svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<circle cx="11" cy="11" r="8"></circle>
							<line x1="21" y1="21" x2="16.65" y2="16.65"></line>
						</svg>
						<input
							type="text"
							id="catalogSearch"
							name="catalog_search"
							v-model="catalogSearchInput"
							class="catalog-search-input"
							:placeholder="currentCatalogSearchPlaceholder"
						/>
						<button
							v-if="catalogSearchInput"
							type="button"
							class="btn-clear-search"
							@click="catalogSearchInput = ''"
						>✕</button>
					</div>
				</div>
			</header>

			<!-- Quotation Table -->
			<div v-if="view === 'quotes'" class="table-container">
				<table class="data-table">
					<thead>
						<tr>
							<th style="width: 11%;">Ngày</th>
							<th style="width: 15%;">Mã báo giá</th>
							<th style="width: 24%;">Khách</th>
							<th style="width: 14%;">Nhóm</th>
							<th style="width: 12%; text-align: right;">Tổng</th>
							<th style="width: 12%; text-align: center;">Trạng thái</th>
							<th style="width: 12%; text-align: center;">Thao tác</th>
						</tr>
					</thead>
					<tbody>
						<tr v-for="q in quotations" :key="q.name" class="table-row">
							<td class="text-secondary font-mono">{{ q.transaction_date || '—' }}</td>
							<td class="font-bold text-primary font-mono">{{ q.name }}</td>
							<td>
								<div class="font-semibold">{{ q.customer_name || '—' }}</div>
								<div v-if="q.pouch_type" class="text-xs text-secondary">{{ q.pouch_type }}</div>
							</td>
							<td>
								<span class="badge-tag-group">{{ q.product_group || 'Túi màng ghép' }}</span>
							</td>
							<td class="text-right font-bold text-num">{{ formatCurrency(q.grand_total) }}</td>
							<td class="text-center">
								<span class="status-badge" :class="statusClass(q.status)">
									{{ q.status || 'Draft' }}
								</span>
							</td>
							<td class="text-center action-cells">
								<button
									v-if="q.status === 'Open'"
									type="button"
									class="row-btn row-btn-primary"
									@click="onMakeOrder(q)"
								>
									Chốt đơn
								</button>
								<button
									v-else-if="q.status === 'Draft'"
									type="button"
									class="row-btn row-btn-primary"
									@click="onSendQuotation(q)"
								>
									Gửi duyệt
								</button>
								<button
									v-if="q.status === 'Draft' || q.status === 'Open'"
									type="button"
									class="row-btn row-btn-danger"
									@click="onMarkLost(q)"
								>
									Rớt
								</button>
								<span v-else class="text-secondary text-xs">—</span>
							</td>
						</tr>
						<tr v-if="quotations.length === 0">
							<td colspan="7" class="empty-cell">
								{{ loading ? 'Đang tải...' : 'Không có dữ liệu' }}
							</td>
						</tr>
					</tbody>
				</table>
			</div>

			<!-- Sales Order View: 3 Tabs (Phương án 2: Theo Nơi Thực Hiện / Phương Thức Cung Ứng) -->
			<div v-else-if="view === 'orders'" class="orders-view-wrapper">
				<!-- Sub-navigation 3 Tabs -->
				<div class="order-tabs-bar">
					<button
						type="button"
						class="order-tab-btn"
						:class="{ active: activeOrderTab === 'xuong_sx' }"
						@click="activeOrderTab = 'xuong_sx'"
					>
						<span>Xưởng sản xuất</span>
						<span class="tab-badge">{{ xuongSxOrders.length }}</span>
					</button>
					<button
						type="button"
						class="order-tab-btn"
						:class="{ active: activeOrderTab === 'ngcs' }"
						@click="activeOrderTab = 'ngcs'"
					>
						<span>Túi NGCS</span>
						<span class="tab-badge">{{ ngcsOrders.length }}</span>
					</button>
					<button
						type="button"
						class="order-tab-btn"
						:class="{ active: activeOrderTab === 'mua_ngoai' }"
						@click="activeOrderTab = 'mua_ngoai'"
					>
						<span>Mua ngoài trọn gói</span>
						<span class="tab-badge">{{ muaNgoaiOrders.length }}</span>
					</button>
				</div>

				<div class="table-container">
					<table class="data-table">
						<!-- TAB 1: XƯỞNG SẢN XUẤT -->
						<thead v-if="activeOrderTab === 'xuong_sx'">
							<tr>
								<th style="width: 10%;">Ngày</th>
								<th style="width: 20%;">Khách</th>
								<th style="width: 25%;">Mặt hàng</th>
								<th style="width: 13%; text-align: right;">Số lượng</th>
								<th style="width: 13%; text-align: right;">Đã cọc</th>
								<th style="width: 17%; text-align: center;">Vật tư & Máy</th>
								<th style="width: 12%; text-align: center;">Trạng thái</th>
							</tr>
						</thead>

						<!-- TAB 2: TÚI NGCS -->
						<thead v-else-if="activeOrderTab === 'ngcs'">
							<tr>
								<th style="width: 10%;">Ngày</th>
								<th style="width: 22%;">Khách</th>
								<th style="width: 26%;">Mặt hàng</th>
								<th style="width: 13%; text-align: right;">Số lượng</th>
								<th style="width: 13%; text-align: right;">Đã cọc</th>
								<th style="width: 16%; text-align: center;">In lụa NCC</th>
								<th style="width: 10%; text-align: center;">Trạng thái</th>
							</tr>
						</thead>

						<!-- TAB 3: MUA NGOÀI TRỌN GÓI -->
						<thead v-else>
							<tr>
								<th style="width: 10%;">Ngày</th>
								<th style="width: 22%;">Khách</th>
								<th style="width: 26%;">Mặt hàng</th>
								<th style="width: 13%; text-align: right;">Số lượng</th>
								<th style="width: 13%; text-align: right;">Đã cọc</th>
								<th style="width: 16%; text-align: center;">Hạn giao NCC</th>
								<th style="width: 10%; text-align: center;">Trạng thái</th>
							</tr>
						</thead>

						<tbody>
							<tr
								v-for="o in currentTabOrders"
								:key="o.name"
								class="table-row cursor-pointer"
								@click="openOrderDetail(o)"
							>
								<td class="text-secondary font-mono">{{ formatDateShort(o.transaction_date) }}</td>
								<td>
									<div class="font-bold text-white">{{ o.customer_alias || o.alias || o.customer || o.customer_name }}</div>
								</td>
								<td class="truncate" :title="o.item_name">
									<span class="font-medium text-white">{{ o.custom_alias || o.item_name || '—' }}</span>
								</td>
								<td class="text-right text-num">
									<span>{{ formatNumber(o.qty) }}</span>
									<span class="text-xs text-secondary" style="margin-left: 4px;">{{ o.uom || o.stock_uom || 'Túi' }}</span>
								</td>
								<td class="text-right">
									<div v-if="o.payment_type === 'Trả sau'" class="text-xs text-secondary font-semibold">
										Trả sau
									</div>
									<div v-else class="deposit-mini-cell">
										<div class="text-num font-bold" :class="o.advance_paid >= (o.required_deposit || o.grand_total * 0.5) ? 'text-emerald' : (o.advance_paid > 0 ? 'text-amber' : 'text-secondary')">
											{{ formatCurrency(o.advance_paid) }}
										</div>
										<div class="mini-bar-track">
											<div
												class="mini-bar-fill"
												:style="{ width: Math.min(100, Math.round((o.advance_paid / (o.required_deposit || (o.grand_total * 0.5))) * 100)) + '%' }"
												:class="o.advance_paid >= (o.required_deposit || (o.grand_total * 0.5)) ? 'bg-emerald' : 'bg-amber'"
											></div>
										</div>
									</div>
								</td>

								<!-- Cột theo Tab: Xưởng SX -->
								<td v-if="activeOrderTab === 'xuong_sx'" class="text-center">
									<div class="factory-status-cell">
										<span class="badge-mat" :class="o.materials_status === 'Đủ màng' ? 'mat-ready' : 'mat-waiting'">
											{{ o.materials_status || 'Chờ màng' }}
										</span>
										<span class="badge-stage">
											{{ o.factory_stage || 'Chờ cọc' }}
										</span>
									</div>
								</td>

								<!-- Cột theo Tab: NGCS In Lụa -->
								<td v-else-if="activeOrderTab === 'ngcs'" class="text-center">
									<div v-if="o.supplier_name" class="sla-cell">
										<span class="sla-supplier">{{ o.supplier_name }}</span>
										<span class="sla-badge" :class="supplierSlaBadge(o.supplier_eta_days).cls">
											{{ supplierSlaBadge(o.supplier_eta_days).text }}
										</span>
									</div>
									<span v-else class="text-secondary text-xs">—</span>
								</td>

								<!-- Cột theo Tab: Mua Ngoài -->
								<td v-else class="text-center">
									<div v-if="o.supplier_name" class="sla-cell">
										<span class="sla-supplier">{{ o.supplier_name }}</span>
										<span class="sla-badge" :class="supplierSlaBadge(o.supplier_eta_days).cls">
											{{ supplierSlaBadge(o.supplier_eta_days).text }}
										</span>
									</div>
									<span v-else class="text-secondary text-xs">—</span>
								</td>

								<!-- Trạng thái chung -->
								<td class="text-center">
									<span class="status-badge" :class="orderStatusClass(o)">
										{{ orderStatusText(o) }}
									</span>
								</td>
							</tr>
							<tr v-if="currentTabOrders.length === 0">
								<td colspan="7" class="empty-cell">
									{{ loadingOrders ? 'Đang tải...' : 'Không có dữ liệu trong tab này' }}
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>

			<!-- Master Catalog View: Elon Musk Minimalist Cockpit (Tất Cả Danh Mục) -->
			<div v-else-if="isCatalogView" class="catalog-view-wrapper">
				<!-- Sub-filter chips cho tab Sản Phẩm (Bỏ filter Tất Cả) -->
				<div v-if="activeCatalogTab === 'sp'" class="catalog-subfilter-bar">
					<div class="sub-filter-chips">
						<button
							type="button"
							class="sub-chip-btn"
							:class="{ active: activeProductSubFilter === 'tp' }"
							@click="activeProductSubFilter = activeProductSubFilter === 'tp' ? 'all' : 'tp'"
						>
							Túi ghép ({{ tpItems.length }})
						</button>
						<button
							type="button"
							class="sub-chip-btn"
							:class="{ active: activeProductSubFilter === 'ngcs' }"
							@click="activeProductSubFilter = activeProductSubFilter === 'ngcs' ? 'all' : 'ngcs'"
						>
							Túi NGCS ({{ ngcsItems.length }})
						</button>
						<button
							type="button"
							class="sub-chip-btn"
							:class="{ active: activeProductSubFilter === 'btp' }"
							@click="activeProductSubFilter = activeProductSubFilter === 'btp' ? 'all' : 'btp'"
						>
							Cuộn màng ({{ btpItems.length }})
						</button>
						<button
							type="button"
							class="sub-chip-btn"
							:class="{ active: activeProductSubFilter === 'tmd' }"
							@click="activeProductSubFilter = activeProductSubFilter === 'tmd' ? 'all' : 'tmd'"
						>
							Màng đơn ({{ tmdItems.length }})
						</button>
					</div>
				</div>

				<!-- Bảng Mặt hàng: Sản phẩm, NVL, Trục in -->
				<div v-if="activeCatalogTab === 'sp' || activeCatalogTab === 'nvl' || activeCatalogTab === 'truc'" class="table-container">
					<table class="data-table">
						<thead>
							<tr>
								<th style="width: 14%;">Mã sản phẩm</th>
								<th style="width: 27%;">Tên sản phẩm</th>
								<th style="width: 21%;">Chất liệu</th>
								<th style="width: 20%;">Kích thước (R x D x Dày)</th>
								<th style="width: 11%; text-align: center;">Đáy</th>
								<th style="width: 7%; text-align: center;">ĐVT</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="it in filteredMasterItems"
								:key="it.item_code"
								class="table-row cursor-pointer"
								@click="openItemDetail(it)"
							>
								<!-- Mã sản phẩm -->
								<td class="font-mono font-bold text-primary text-[14.5px]">
									{{ it.item_code }}
								</td>

								<!-- Tên sản phẩm (chỉ dùng tên ngắn) -->
								<td>
									<div class="font-semibold text-white leading-tight text-[15px]" :title="it.item_name || ''">
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
									<span class="text-white font-medium">{{ getItemDimensionsText(it) }}</span>
								</td>

								<!-- Đáy (Tách riêng cột) -->
								<td class="text-center font-mono text-sm">
									<span v-if="getItemGussetText(it)" class="text-amber font-semibold">
										{{ getItemGussetText(it) }}
									</span>
									<span v-else class="text-secondary/40">—</span>
								</td>

								<!-- ĐVT -->
								<td class="text-center font-mono text-sm text-secondary">
									{{ it.stock_uom || 'Túi' }}
								</td>
							</tr>
							<tr v-if="filteredMasterItems.length === 0">
								<td colspan="6" class="empty-cell" style="padding: 2.5rem 1rem; text-align: center;">
									<div v-if="loadingMasterItems" class="text-secondary">Đang tải danh mục...</div>
									<div v-else-if="itemSearchQuery" class="flex flex-col items-center justify-center gap-2">
										<div class="text-secondary text-sm">
											Không tìm thấy mặt hàng nào khớp với "<strong class="text-white">{{ itemSearchQuery }}</strong>" trong tab {{ currentTabLabel }}.
										</div>
										<button
											type="button"
											class="btn-clear-filter-inline"
											@click="itemSearchQuery = ''"
										>
											✕ Xóa tìm kiếm để xem tất cả {{ currentTabMasterItems.length }} sản phẩm {{ currentTabLabel }}
										</button>
									</div>
									<div v-else class="text-secondary text-sm">Không có mặt hàng nào trong tab này</div>
								</td>
							</tr>
						</tbody>
					</table>
				</div>

				<!-- Bảng Khách hàng -->
				<div v-else-if="activeCatalogTab === 'kh'" class="table-container">
					<table class="data-table">
						<thead>
							<tr>
								<th style="width: 12%;">MÃ KHÁCH</th>
								<th style="width: 22%;">TÊN GỌI TẮT (ALIAS)</th>
								<th style="width: 32%;">TÊN PHÁP NHÂN</th>
								<th style="width: 14%;">KHU VỰC</th>
								<th class="text-right" style="width: 12%;">HẠN MỨC NỢ</th>
								<th style="width: 8%;">THANH TOÁN</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="c in filteredCustomers"
								:key="c.name"
								class="table-row cursor-pointer"
								@click="openCustomerDetail(c)"
							>
								<td class="font-mono font-bold text-primary text-[14.5px]">
									{{ c.name }}
								</td>
								<td>
									<div class="font-semibold text-white leading-tight text-[15px]">
										{{ c.alias || c.customer_name }}
									</div>
								</td>
								<td>
									<div class="text-sm text-secondary truncate max-w-[340px]" :title="c.customer_name">
										{{ c.customer_name }}
									</div>
								</td>
								<td class="text-sm">
									<span class="text-slate-300">{{ c.territory || 'Việt Nam' }}</span>
								</td>
								<td class="text-right font-mono text-sm">
									<span v-if="Number(c.credit_limit) > 0" class="text-emerald font-bold">
										{{ formatCurrency(c.credit_limit) }}
									</span>
									<span v-else class="text-secondary/60">0 đ</span>
								</td>
								<td class="text-sm">
									<span v-if="c.payment_terms && c.payment_terms.includes('30 ngày')" class="text-amber font-mono text-xs">Gối đầu</span>
									<span v-else class="text-secondary text-xs">Cọc 50%</span>
								</td>
							</tr>
							<tr v-if="filteredCustomers.length === 0">
								<td colspan="6" class="empty-cell" style="padding: 2.5rem 1rem; text-align: center;">
									<div v-if="loadingCustomers" class="text-secondary">Đang tải khách hàng...</div>
									<div v-else class="text-secondary text-sm">Không tìm thấy khách hàng nào phù hợp</div>
								</td>
							</tr>
						</tbody>
					</table>
				</div>

				<!-- Bảng Nhà cung cấp -->
				<div v-else-if="activeCatalogTab === 'ncc'" class="table-container">
					<table class="data-table">
						<thead>
							<tr>
								<th style="width: 12%;">MÃ NCC</th>
								<th style="width: 20%;">TÊN GỌI TẮT</th>
								<th style="width: 32%;">TÊN PHÁP NHÂN</th>
								<th style="width: 22%;">NHÓM CUNG ỨNG</th>
								<th style="width: 14%;">MÃ SỐ THUẾ</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="s in filteredSuppliers"
								:key="s.name"
								class="table-row cursor-pointer"
								@click="openSupplierDetail(s)"
							>
								<td class="font-mono font-bold text-sky-400 text-[14.5px]">
									{{ s.name }}
								</td>
								<td>
									<div class="font-semibold text-white leading-tight text-[15px]">
										{{ s.alias || s.supplier_name }}
									</div>
								</td>
								<td>
									<div class="text-sm text-secondary truncate max-w-[340px]" :title="s.supplier_name">
										{{ s.supplier_name }}
									</div>
								</td>
								<td>
									<span class="badge-tag-group text-xs">{{ s.supplier_group || 'NCC' }}</span>
								</td>
								<td class="font-mono text-sm text-slate-300">
									{{ s.tax_id || '—' }}
								</td>
							</tr>
							<tr v-if="filteredSuppliers.length === 0">
								<td colspan="5" class="empty-cell" style="padding: 2.5rem 1rem; text-align: center;">
									<div v-if="loadingSuppliers" class="text-secondary">Đang tải nhà cung cấp...</div>
									<div v-else class="text-secondary text-sm">Không tìm thấy nhà cung cấp nào phù hợp</div>
								</td>
							</tr>
						</tbody>
					</table>
				</div>

				<!-- Bảng Người dùng -->
				<div v-else-if="activeCatalogTab === 'user'" class="table-container">
					<table class="data-table">
						<thead>
							<tr>
								<th style="width: 26%;">EMAIL ĐĂNG NHẬP</th>
								<th style="width: 22%;">HỌ VÀ TÊN</th>
								<th style="width: 18%;">PHÒNG BAN</th>
								<th style="width: 18%;">CHỨC DANH</th>
								<th style="width: 16%;">VAI TRÒ ERPNEXT</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="u in filteredUsers"
								:key="u.name"
								class="table-row cursor-pointer"
								@click="openUserDetail(u)"
							>
								<td class="font-mono font-semibold text-purple-400 text-[14px]">
									{{ u.email }}
								</td>
								<td>
									<div class="font-semibold text-white leading-tight text-[15px]">
										{{ u.full_name }}
									</div>
								</td>
								<td class="text-sm text-slate-300">
									{{ u.department || 'Ban Giám Đốc' }}
								</td>
								<td class="text-sm text-primary">
									{{ u.designation || 'Nhân viên' }}
								</td>
								<td>
									<span class="badge-role-user font-mono text-xs">{{ u.role_profile_name || 'System User' }}</span>
								</td>
							</tr>
							<tr v-if="filteredUsers.length === 0">
								<td colspan="5" class="empty-cell" style="padding: 2.5rem 1rem; text-align: center;">
									<div v-if="loadingUsers" class="text-secondary">Đang tải người dùng...</div>
									<div v-else class="text-secondary text-sm">Không tìm thấy người dùng nào phù hợp</div>
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>
		</main>

		<!-- Step 1: Sale Modal -->
		<ModalStep1Sale
			v-if="showStep1"
			:initial-data="step1Data"
			@close="showStep1 = false"
			@next="onStep1Complete"
		/>

		<!-- Step 2: Director Drawer -->
		<DrawerStep2Director
			v-if="showStep2"
			:form-data="step1Data"
			:preview-figures="figures"
			:saved-data="step2Data"
			@close="showStep2 = false"
			@back="onStep2Back"
			@items-changed="onItemsChanged"
			@submit="onQuotationSubmit"
		/>

		<!-- Modal Tạo Đơn Hàng Mới -->
		<ModalCreateOrder
			v-if="showCreateOrderModal"
			:is-open="showCreateOrderModal"
			:initial-tab="activeOrderTab"
			@close="showCreateOrderModal = false"
			@create-order="handleNewOrderCreated"
		/>

		<!-- Order Detail Drawer (Click Row to Open) -->
		<DrawerOrderDetail
			:order="selectedOrder"
			:order-id="selectedOrderId"
			:is-open="showOrderDetail"
			@close="showOrderDetail = false"
			@update-order="onOrderUpdated"
			@create-delivery="onOrderDelivery"
		/>

		<!-- Master Item Detail Drawer (Click Item Row to Open) -->
		<DrawerItemDetail
			:item="selectedMasterItem"
			:bom="selectedMasterBom"
			:is-open="showItemDrawer"
			:loading="loadingItemDetail"
			@close="showItemDrawer = false"
		/>

		<!-- Customer Detail Drawer -->
		<DrawerCustomerDetail
			:customer="selectedCustomer"
			:master-items="masterItems"
			:is-open="showCustomerDrawer"
			@close="showCustomerDrawer = false"
		/>

		<!-- Supplier Detail Drawer -->
		<DrawerSupplierDetail
			:supplier="selectedSupplier"
			:is-open="showSupplierDrawer"
			@close="showSupplierDrawer = false"
		/>

		<!-- User Detail Drawer -->
		<DrawerUserDetail
			:user="selectedUser"
			:is-open="showUserDrawer"
			@close="showUserDrawer = false"
		/>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import ModalStep1Sale from './components/ModalStep1Sale.vue';
import DrawerStep2Director from './components/DrawerStep2Director.vue';
import DrawerOrderDetail from './components/DrawerOrderDetail.vue';
import DrawerItemDetail from './components/DrawerItemDetail.vue';
import DrawerCustomerDetail from './components/DrawerCustomerDetail.vue';
import DrawerSupplierDetail from './components/DrawerSupplierDetail.vue';
import DrawerUserDetail from './components/DrawerUserDetail.vue';
import ModalCreateOrder from './components/ModalCreateOrder.vue';
import logoUrl from './assets/logo-vanphat.png';
import { INITIAL_ORDERS, INITIAL_QUOTATIONS, MASTER_CATALOG_ITEMS } from './data/mockData';

const view = ref('orders');
const quotations = ref([]);
const loading = ref(false);
const orders = ref([]);
const loadingOrders = ref(false);
const activeOrderTab = ref('xuong_sx');

// --- Master Catalog (Items) States ---
const masterItems = ref([]);
const loadingMasterItems = ref(false);
const activeCatalogTab = ref('sp'); // 'sp', 'nvl', 'truc', 'kh', 'ncc', 'user'
const activeItemTab = activeCatalogTab; // backward-compatibility alias
const activeProductSubFilter = ref('all'); // 'all', 'tp', 'ngcs', 'btp', 'tmd'
const itemSearchQuery = ref('');

const showItemDrawer = ref(false);
const selectedMasterItem = ref(null);
const selectedMasterBom = ref(null);
const loadingItemDetail = ref(false);

// --- Customers States ---
const customers = ref([]);
const loadingCustomers = ref(false);
const customerSearchQuery = ref('');
const selectedCustomer = ref(null);
const showCustomerDrawer = ref(false);

// --- Suppliers States ---
const suppliers = ref([]);
const loadingSuppliers = ref(false);
const supplierSearchQuery = ref('');
const selectedSupplier = ref(null);
const showSupplierDrawer = ref(false);

// --- Users States ---
const users = ref([]);
const loadingUsers = ref(false);
const userSearchQuery = ref('');
const selectedUser = ref(null);
const showUserDrawer = ref(false);

// --- Unified Catalog Computed & Helpers ---
const isCatalogView = computed(() => {
	return view.value === 'catalog' || view.value === 'items' || view.value === 'customers' || view.value === 'suppliers' || view.value === 'users';
});

const catalogTotalCount = computed(() => {
	return masterItems.value.length + customers.value.length + suppliers.value.length + users.value.length;
});

const currentCatalogSearchPlaceholder = computed(() => {
	switch (activeCatalogTab.value) {
		case 'kh':
			return 'Tìm mã, tên gọi tắt, tên pháp nhân, khu vực...';
		case 'ncc':
			return 'Tìm mã, tên tắt, nhóm NCC, MST...';
		case 'user':
			return 'Tìm tên, email, chức danh, phòng ban...';
		case 'nvl':
			return 'Tìm mã NVL, tên màng, keo, hóa chất...';
		case 'truc':
			return 'Tìm mã trục, quy cách trục, sản phẩm...';
		default:
			return 'Tìm mã, tên, khách hàng, màng...';
	}
});

const catalogSearchInput = computed({
	get() {
		if (activeCatalogTab.value === 'kh') return customerSearchQuery.value;
		if (activeCatalogTab.value === 'ncc') return supplierSearchQuery.value;
		if (activeCatalogTab.value === 'user') return userSearchQuery.value;
		return itemSearchQuery.value;
	},
	set(val) {
		if (activeCatalogTab.value === 'kh') customerSearchQuery.value = val;
		else if (activeCatalogTab.value === 'ncc') supplierSearchQuery.value = val;
		else if (activeCatalogTab.value === 'user') userSearchQuery.value = val;
		else itemSearchQuery.value = val;
	}
});

function switchCatalogTab(tabKey) {
	activeCatalogTab.value = tabKey;
	if (tabKey === 'sp') {
		activeProductSubFilter.value = 'all';
	}
}

function switchItemTab(tabKey) {
	switchCatalogTab(tabKey);
}

async function loadAllCatalogData() {
	await Promise.all([
		loadMasterItems(),
		loadCustomers(),
		loadSuppliers(),
		loadUsers()
	]);
}

const tpItems = computed(() =>
	masterItems.value.filter((i) => (i.item_code || '').startsWith('TP-') || i.item_group === 'Túi Màng Ghép Đặt Riêng')
);
const ngcsItems = computed(() =>
	masterItems.value.filter((i) => (i.item_code || '').startsWith('NGCS-') || i.item_group === 'Túi Nước Giặt Có Sẵn (NGCS)')
);
const tmdItems = computed(() =>
	masterItems.value.filter((i) => (i.item_code || '').startsWith('TMD-') || i.item_group === 'Túi Màng Đơn')
);
const btpItems = computed(() =>
	masterItems.value.filter((i) => (i.item_code || '').startsWith('BTP-') || i.item_group === 'Cuộn Màng Ghép BTP')
);

// Gộp 4 nhóm thành Danh Mục Sản Phẩm (88 mã)
const productItems = computed(() =>
	masterItems.value.filter((i) =>
		(i.item_code || '').startsWith('TP-') ||
		(i.item_code || '').startsWith('NGCS-') ||
		(i.item_code || '').startsWith('TMD-') ||
		(i.item_code || '').startsWith('BTP-') ||
		i.item_group === 'Túi Màng Ghép Đặt Riêng' ||
		i.item_group === 'Túi Nước Giặt Có Sẵn (NGCS)' ||
		i.item_group === 'Túi Màng Đơn' ||
		i.item_group === 'Cuộn Màng Ghép BTP'
	)
);

const nvlItems = computed(() =>
	masterItems.value.filter((i) => (i.item_code || '').startsWith('NVL-') || i.item_group === 'Màng Thô NVL' || i.item_group === 'Màng In Ống Đồng' || i.item_group === 'Hóa Chất & Keo Ghép' || i.item_group === 'Phụ Kiện Bao Bì')
);
const trucItems = computed(() =>
	masterItems.value.filter((i) => (i.item_code || '').startsWith('TRUC-') || i.item_group === 'Trục In Ống Đồng')
);

const currentTabMasterItems = computed(() => {
	if (activeItemTab.value === 'sp') {
		if (activeProductSubFilter.value === 'tp') return tpItems.value;
		if (activeProductSubFilter.value === 'ngcs') return ngcsItems.value;
		if (activeProductSubFilter.value === 'btp') return btpItems.value;
		if (activeProductSubFilter.value === 'tmd') return tmdItems.value;
		return productItems.value;
	}
	if (activeItemTab.value === 'nvl') return nvlItems.value;
	if (activeItemTab.value === 'truc') return trucItems.value;
	return productItems.value;
});

const currentTabLabel = computed(() => {
	const map = {
		sp: 'Sản phẩm',
		nvl: 'Nguyên vật liệu',
		truc: 'Trục in'
	};
	return map[activeItemTab.value] || 'mặt hàng';
});

const filteredMasterItems = computed(() => {
	const list = currentTabMasterItems.value;
	const q = itemSearchQuery.value.trim().toLowerCase();
	if (!q) return list;
	return list.filter((it) =>
		(it.item_code && it.item_code.toLowerCase().includes(q)) ||
		(it.item_name && it.item_name.toLowerCase().includes(q)) ||
		(it.custom_alias && it.custom_alias.toLowerCase().includes(q)) ||
		(it.customer && it.customer.toLowerCase().includes(q)) ||
		(it.brand && it.brand.toLowerCase().includes(q)) ||
		(it.custom_structure_layers && it.custom_structure_layers.toLowerCase().includes(q)) ||
		(it.description && it.description.toLowerCase().includes(q))
	);
});

const ngcsOrders = computed(() =>
	orders.value.filter((o) => o.order_tab === 'ngcs' || o.product_group === 'Túi NGCS')
);
const xuongSxOrders = computed(() =>
	orders.value.filter(
		(o) =>
			o.order_tab === 'xuong_sx' ||
			(!o.order_tab && o.product_group === 'Túi màng ghép' && o.payment_type !== 'Trả sau')
	)
);
const muaNgoaiOrders = computed(() =>
	orders.value.filter(
		(o) =>
			o.order_tab === 'mua_ngoai' ||
			o.product_group === 'Túi màng đơn' ||
			o.product_group === 'Cuộn màng ghép' ||
			o.payment_type === 'Trả sau'
	)
);

const currentTabOrders = computed(() => {
	if (activeOrderTab.value === 'ngcs') return ngcsOrders.value;
	if (activeOrderTab.value === 'xuong_sx') return xuongSxOrders.value;
	return muaNgoaiOrders.value;
});

function supplierSlaBadge(days) {
	if (days == null) return { text: '—', cls: 'sla-none' };
	if (days < 0) return { text: 'Trễ ' + Math.abs(days) + ' ngày', cls: 'sla-overdue' };
	if (days === 0) return { text: 'Hôm nay giao', cls: 'sla-today' };
	return { text: 'Còn ' + days + ' ngày', cls: 'sla-ontime' };
}

const selectedOrderId = ref('');
const showOrderDetail = ref(false);
const showCreateOrderModal = ref(false);

const selectedOrder = computed(() => {
	return orders.value.find((o) => o.name === selectedOrderId.value) || null;
});

const showStep1 = ref(false);
const showStep2 = ref(false);

const step1Data = ref({
	product_type: 'Túi đáy đứng',
	accessory: 'Có vòi',
	print_type: 'In trục',
	cylinder_status: 'Đã có trục',
	customer: '',
	customer_id: '',
	brand: '',
	description: '',
	length: '',
	width: '',
	thickness: '',
	bottom: '',
});
const step2Data = ref({
	lines: [{ item_name: '', qty: '', rate: '' }],
	materials: ['OPP', 'PE sữa'],
	cylinder_qty: 1,
	artwork_url: '',
});

const figures = ref({
	total_qty: '0',
	subtotal: '0 đ',
	cylinder_total: '0 đ',
	tax_amount: '0 đ',
	grand_total: '0 đ',
});

const calcResult = ref(null);
const currentUser = ref('giamdoc@vanphat.com');

// API Caller wrapper
function csrfToken() {
	return window.vp_csrf_token || window.frappe_csrf_token || '';
}

async function api(method, args = {}) {
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

async function boot() {
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

async function handleLogout() {
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

async function loadQuotations() {
	loading.value = true;
	const data = await api('list_quotations');
	if (Array.isArray(data) && data.length > 0) {
		quotations.value = data;
	} else if (quotations.value.length === 0) {
		quotations.value = [...INITIAL_QUOTATIONS];
	}
	loading.value = false;
}

function openStep1Modal() {
	showStep1.value = true;
}

async function calculatePackaging() {
	const totalDesiredQty =
		step2Data.value.lines.reduce((s, r) => s + (Number(r.qty) || 0), 0) || 5000;
	const isPrintCylinder =
		step1Data.value.print_type === 'In trục' &&
		step1Data.value.cylinder_status === 'Chưa có trục';
	const cylQty = isPrintCylinder ? Number(step2Data.value.cylinder_qty) || 1 : 0;

	const res = await api('calculate_packaging_quotation', {
		pouch_type: step1Data.value.product_type,
		width_mm: step1Data.value.width,
		length_mm: step1Data.value.length,
		gusset_mm: step1Data.value.bottom,
		layers: step2Data.value.materials,
		spout_type: step1Data.value.accessory === 'Có vòi' ? '16mm' : '',
		desired_qty: totalDesiredQty,
		cylinder_qty: cylQty,
		target_margin: 0.30,
	});

	if (res) {
		calcResult.value = res;
		return res;
	}
	return null;
}

async function onStep1Complete(payload) {
	step1Data.value = payload;
	showStep1.value = false;
	showStep2.value = true;
	if (!step2Data.value.lines || !step2Data.value.lines.length || !step2Data.value.lines[0].item_name) {
		step2Data.value.lines = [
			{
				item_name: step1Data.value.description || 'Mẫu in chính',
				qty: 5000,
				rate: '',
			},
		];
	}
	await fetchPricePreview();
}

function onStep2Back() {
	showStep2.value = false;
	showStep1.value = true;
}

async function fetchPricePreview() {
	const res = await api('get_price_preview', { quotation: '', lines: step2Data.value.lines });
	const isPrintCylinder =
		step1Data.value.print_type === 'In trục' &&
		step1Data.value.cylinder_status === 'Chưa có trục';
	const cylTotal = isPrintCylinder ? (calcResult.value?.cylinder_quote?.total || 0) : 0;

	if (res) {
		const sub = Number(res.subtotal) || 0;
		const tax = Number(res.tax_amount) || Math.round(sub * 0.08);
		const grand = Number(res.grand_total) || (sub + cylTotal + tax);
		figures.value = {
			total_qty: String(res.total_qty ?? '0'),
			subtotal: formatCurrency(sub),
			cylinder_total: formatCurrency(cylTotal),
			tax_amount: formatCurrency(tax),
			grand_total: formatCurrency(grand),
		};
	}
}
function statusClass(status) {
	switch (status || 'Draft') {
		case 'Open':
		case 'Partially Ordered':
			return 'status-open';
		case 'Ordered':
			return 'status-ordered';
		case 'Lost':
			return 'status-lost';
		case 'Expired':
			return 'status-expired';
		default:
			return 'status-draft';
	}
}

async function onSendQuotation(q) {
	const res = await api('submit_quotation', { name: q.name });
	if (res) await loadQuotations();
}

async function onMarkLost(q) {
	const reason = window.prompt(`Lý do rớt báo giá ${q.name}?`, '');
	if (reason === null) return;
	const res = await api('mark_quotation_lost', { name: q.name, reason });
	if (res) await loadQuotations();
}

async function onItemsChanged(payload = {}) {
	step2Data.value = {
		lines: (payload.lines && payload.lines.length ? payload.lines : step2Data.value.lines).map((r) => ({ ...r })),
		materials: [...(payload.materials || step2Data.value.materials)],
		cylinder_qty: payload.cylinder_qty ?? step2Data.value.cylinder_qty,
		artwork_url: payload.artwork_url ?? step2Data.value.artwork_url,
	};
	await calculatePackaging();
	await fetchPricePreview();
}

async function onQuotationSubmit(payload) {
	const res = await api('create_quotation', { payload });
	if (res && res.name) {
		showStep2.value = false;
		await loadQuotations();
	}
}

async function loadOrders() {
	loadingOrders.value = true;
	const data = await api('list_orders');
	if (Array.isArray(data) && data.length > 0) {
		orders.value = data;
	} else {
		orders.value = [...INITIAL_ORDERS];
	}
	loadingOrders.value = false;
}

function openOrderDetail(o) {
	selectedOrderId.value = o.name;
	showOrderDetail.value = true;
}

function handleNewOrderCreated(newOrder) {
	orders.value.unshift(newOrder);
	activeOrderTab.value = newOrder.order_tab;
	selectedOrderId.value = newOrder.name;
	showOrderDetail.value = true;
}

function onOrderUpdated(updatedOrder) {
	const idx = orders.value.findIndex((o) => o.name === updatedOrder.name);
	if (idx !== -1) {
		orders.value[idx] = { ...updatedOrder };
	}
}

function onOrderDelivery(order) {
	const idx = orders.value.findIndex((o) => o.name === order.name);
	if (idx !== -1) {
		orders.value[idx].order_state = 'Đã giao hàng';
		orders.value[idx].outstanding_amount = 0;
		orders.value[idx].advance_paid = orders.value[idx].grand_total;
	}
	showOrderDetail.value = false;
}

function orderStatusText(o) {
	if (o.is_hold || o.order_state?.includes('HOLD')) return 'HOLD';
	if (o.payment_type === 'Trả sau' && o.docstatus === 1) return 'Trả sau';
	if (o.docstatus === 1) return 'Đã duyệt';
	if (o.advance_paid > 0 && o.advance_paid < (o.required_deposit || o.grand_total * 0.5)) return 'HOLD';
	return 'Chờ cọc';
}

function orderStatusClass(o) {
	if (o.is_hold || o.order_state?.includes('HOLD')) return 'status-hold';
	if (o.docstatus === 1 || o.order_state?.includes('Chính thức')) return 'status-ordered';
	if (o.advance_paid > 0) return 'status-hold';
	return 'status-draft';
}

function formatNumber(val) {
	if (val == null || val === '') return '0';
	return Number(val).toLocaleString('vi-VN');
}

function formatDateShort(val) {
	if (!val) return '—';
	const parts = String(val).split('-');
	if (parts.length === 3) {
		return `${parts[2]}/${parts[1]}`;
	}
	return val;
}

async function onMakeOrder(q) {
	const res = await api('make_order_from_quotation', { name: q.name });
	if (res && res.sales_order) {
		await loadQuotations();
		view.value = 'orders';
		await loadOrders();
	}
}
function formatCurrency(val) {
	if (val == null || val === '') return '0 đ';
	if (typeof val === 'string' && isNaN(Number(val))) return val;
	return Number(val).toLocaleString('vi-VN') + ' đ';
}

function formatItemRate(val) {
	if (!val && val !== 0) return '—';
	return new Intl.NumberFormat('vi-VN').format(Math.round(val)) + ' đ';
}

function getItemDimensionsText(it) {
	if (!it) return '—';
	const w = Number(it.custom_pouch_width_mm) || 0;
	const l = Number(it.custom_pouch_length_mm) || 0;
	const thick = Number(it.custom_thickness_mic) || 0;
	if (w > 0 && l > 0) {
		if (thick > 0) return `${w} x ${l} mm x ${thick} mic`;
		return `${w} x ${l} mm`;
	}
	const rollW = Number(it.custom_film_width_mm) || 0;
	if (rollW > 0) {
		if (thick > 0) return `Khổ ${rollW} mm x ${thick} mic`;
		return `Khổ ${rollW} mm`;
	}
	const cylL = Number(it.custom_cylinder_length_mm) || 0;
	const cylC = Number(it.custom_cylinder_circ_mm) || 0;
	if (cylL > 0 || cylC > 0) return `Dài ${cylL} x CV ${cylC} mm`;
	return it.description || '—';
}

function getItemGussetText(it) {
	if (!it) return null;
	const g = Number(it.custom_gusset_mm) || 0;
	if (g > 0) return `${g} mm`;
	return null;
}

function getItemPouchDims(it) {
	return getItemDimensionsText(it);
}

async function loadMasterItems() {
	loadingMasterItems.value = true;
	try {
		const res = await fetch('/api/method/vanphat_portal.api.item.get_list');
		const json = await res.json();
		if (json && Array.isArray(json.message) && json.message.length > 0) {
			masterItems.value = json.message;
		} else if (masterItems.value.length === 0) {
			masterItems.value = [...(MASTER_CATALOG_ITEMS || [])];
		}
	} catch (err) {
		if (masterItems.value.length === 0) {
			masterItems.value = [...(MASTER_CATALOG_ITEMS || [])];
		}
	}
	loadingMasterItems.value = false;
}

async function openItemDetail(item) {
	selectedMasterItem.value = item;
	selectedMasterBom.value = null;
	showItemDrawer.value = true;
	loadingItemDetail.value = true;
	try {
		const res = await fetch(`/api/method/vanphat_portal.api.item.get_detail?item_code=${encodeURIComponent(item.item_code)}`);
		const json = await res.json();
		if (json && json.message) {
			if (json.message.item) selectedMasterItem.value = json.message.item;
			selectedMasterBom.value = json.message.bom || null;
		}
	} catch (e) {
		// keep selected item
	}
	loadingItemDetail.value = false;
}

// --- Customer Methods ---
async function loadCustomers() {
	loadingCustomers.value = true;
	try {
		const res = await fetch('/api/method/vanphat_portal.api.customer.get_list');
		const json = await res.json();
		if (json && Array.isArray(json.message)) {
			customers.value = json.message;
		}
	} catch (e) {
		console.error('Error loading customers:', e);
	}
	loadingCustomers.value = false;
}

function openCustomerDetail(c) {
	selectedCustomer.value = c;
	showCustomerDrawer.value = true;
}

const filteredCustomers = computed(() => {
	const q = customerSearchQuery.value.trim().toLowerCase();
	if (!q) return customers.value;
	return customers.value.filter(c =>
		(c.name && c.name.toLowerCase().includes(q)) ||
		(c.customer_name && c.customer_name.toLowerCase().includes(q)) ||
		(c.alias && c.alias.toLowerCase().includes(q)) ||
		(c.customer_group && c.customer_group.toLowerCase().includes(q)) ||
		(c.territory && c.territory.toLowerCase().includes(q)) ||
		(c.tax_id && c.tax_id.toLowerCase().includes(q))
	);
});

// --- Supplier Methods ---
async function loadSuppliers() {
	loadingSuppliers.value = true;
	try {
		const res = await fetch('/api/method/vanphat_portal.api.supplier.get_list');
		const json = await res.json();
		if (json && Array.isArray(json.message)) {
			suppliers.value = json.message;
		}
	} catch (e) {
		console.error('Error loading suppliers:', e);
	}
	loadingSuppliers.value = false;
}

function openSupplierDetail(s) {
	selectedSupplier.value = s;
	showSupplierDrawer.value = true;
}

const filteredSuppliers = computed(() => {
	const q = supplierSearchQuery.value.trim().toLowerCase();
	if (!q) return suppliers.value;
	return suppliers.value.filter(s =>
		(s.name && s.name.toLowerCase().includes(q)) ||
		(s.supplier_name && s.supplier_name.toLowerCase().includes(q)) ||
		(s.alias && s.alias.toLowerCase().includes(q)) ||
		(s.supplier_group && s.supplier_group.toLowerCase().includes(q)) ||
		(s.tax_id && s.tax_id.toLowerCase().includes(q))
	);
});

// --- User Methods ---
async function loadUsers() {
	loadingUsers.value = true;
	try {
		const res = await fetch('/api/method/vanphat_portal.api.user.get_list');
		const json = await res.json();
		if (json && Array.isArray(json.message)) {
			users.value = json.message;
		}
	} catch (e) {
		console.error('Error loading users:', e);
	}
	loadingUsers.value = false;
}

function openUserDetail(u) {
	selectedUser.value = u;
	showUserDrawer.value = true;
}

const filteredUsers = computed(() => {
	const q = userSearchQuery.value.trim().toLowerCase();
	if (!q) return users.value;
	return users.value.filter(u =>
		(u.name && u.name.toLowerCase().includes(q)) ||
		(u.full_name && u.full_name.toLowerCase().includes(q)) ||
		(u.email && u.email.toLowerCase().includes(q)) ||
		(u.department && u.department.toLowerCase().includes(q)) ||
		(u.designation && u.designation.toLowerCase().includes(q)) ||
		(u.role_profile_name && u.role_profile_name.toLowerCase().includes(q))
	);
});

onMounted(async () => {
	await boot();
	await Promise.all([
		loadOrders(),
		loadQuotations(),
		loadMasterItems(),
		loadCustomers(),
		loadSuppliers(),
		loadUsers()
	]);
	const urlParams = new URLSearchParams(window.location.search);
	const urlView = urlParams.get('view');
	if (urlView) {
		if (urlView === 'customers') {
			view.value = 'catalog';
			activeCatalogTab.value = 'kh';
		} else if (urlView === 'suppliers') {
			view.value = 'catalog';
			activeCatalogTab.value = 'ncc';
		} else if (urlView === 'users') {
			view.value = 'catalog';
			activeCatalogTab.value = 'user';
		} else if (urlView === 'items') {
			view.value = 'catalog';
			activeCatalogTab.value = 'sp';
		} else {
			view.value = urlView;
		}
	}
	if (urlParams.get('tab')) {
		const tabVal = urlParams.get('tab');
		if (['sp', 'nvl', 'truc', 'kh', 'ncc', 'user'].includes(tabVal)) {
			activeCatalogTab.value = tabVal;
		} else if (tabVal === 'khach-hang' || tabVal === 'customers') {
			activeCatalogTab.value = 'kh';
		} else if (tabVal === 'nha-cung-cap' || tabVal === 'suppliers') {
			activeCatalogTab.value = 'ncc';
		} else if (tabVal === 'nguoi-dung' || tabVal === 'users') {
			activeCatalogTab.value = 'user';
		} else {
			activeOrderTab.value = tabVal;
		}
	}
	if (urlParams.get('item_tab')) {
		const itab = urlParams.get('item_tab');
		if (['sp', 'nvl', 'truc', 'kh', 'ncc', 'user'].includes(itab)) {
			activeCatalogTab.value = itab;
		}
	}
	if (urlParams.get('item')) {
		const targetCode = urlParams.get('item');
		const found = masterItems.value.find(x => x.item_code === targetCode);
		if (found) openItemDetail(found);
	}
	if (urlParams.get('customer')) {
		const cust = customers.value.find(c => c.name === urlParams.get('customer'));
		if (cust) openCustomerDetail(cust);
	}
	if (urlParams.get('supplier')) {
		const sup = suppliers.value.find(s => s.name === urlParams.get('supplier'));
		if (sup) openSupplierDetail(sup);
	}
	if (urlParams.get('user_detail')) {
		const usr = users.value.find(u => u.name === urlParams.get('user_detail'));
		if (usr) openUserDetail(usr);
	}
	if (urlParams.get('order')) {
		selectedOrderId.value = urlParams.get('order');
		showOrderDetail.value = true;
	}
	if (urlParams.get('modal') === 'create') {
		showCreateOrderModal.value = true;
	}
});
</script>

<style>
:root {
	--canvas: #12151a;
	--surface: #161b22;
	--surface-low: #1a1f27;
	--outline: #3a424e;
	--outline-focus: #4ea1e0;
	--ink: #eef1f6;
	--ink-secondary: #9da7b5;
	--ink-muted: #64748b;
	--primary: #4ea1e0;
	--primary-press: #3b8ac4;
	--blocked: #f97066;
	--ok: #51cf66;
	--warn: #fec84b;
	--font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

*, *::before, *::after {
	box-sizing: border-box;
	margin: 0;
	padding: 0;
}

html, body {
	height: 100%;
	font-family: var(--font-sans);
	background: var(--canvas);
	color: var(--ink);
	-webkit-font-smoothing: antialiased;
	overflow: hidden;
}

.orders-view-wrapper,
.catalog-view-wrapper {
	display: flex;
	flex-direction: column;
	flex: 1;
	min-height: 0;
}

.catalog-header-cockpit {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 16px;
	margin-bottom: 14px;
	flex-wrap: nowrap;
	flex-shrink: 0;
}

.catalog-header-cockpit .catalog-tabs-bar {
	margin-bottom: 0;
	border-bottom: none;
	padding-bottom: 0;
	flex: 1;
	min-width: 0;
	overflow-x: auto;
	scrollbar-width: none;
	-ms-overflow-style: none;
}

.catalog-header-cockpit .catalog-tabs-bar::-webkit-scrollbar {
	display: none;
}

.catalog-subfilter-bar {
	display: flex;
	align-items: center;
	margin-bottom: 14px;
	flex-shrink: 0;
}

.catalog-search-cockpit-wrap {
	display: flex;
	align-items: center;
	gap: 10px;
	flex-shrink: 0;
}

.search-input-wrap {
	position: relative;
	width: 250px;
	display: flex;
	align-items: center;
}

.search-icon {
	position: absolute;
	left: 12px;
	width: 16px;
	height: 16px;
	color: #8b949e;
	pointer-events: none;
}

.catalog-search-input {
	width: 100%;
	padding: 8px 32px 8px 36px;
	background: #161b22;
	border: 1px solid #3a424e;
	border-radius: 6px;
	color: #f1f5f9;
	font-size: 14.5px;
	outline: none;
	transition: border-color 0.15s ease;
}

.catalog-search-input:focus {
	border-color: #4ea1e0;
	box-shadow: 0 0 0 2px rgba(78, 161, 224, 0.15);
}

.btn-clear-search {
	position: absolute;
	right: 10px;
	background: transparent;
	border: none;
	color: #8b949e;
	cursor: pointer;
	font-size: 13px;
	padding: 2px 4px;
	border-radius: 4px;
}

.btn-clear-search:hover {
	color: #ffffff;
}

.btn-clear-filter-inline {
	margin-top: 6px;
	padding: 6px 14px;
	background: rgba(78, 161, 224, 0.12);
	border: 1px solid rgba(78, 161, 224, 0.3);
	border-radius: 6px;
	color: #4ea1e0;
	font-size: 13px;
	font-weight: 500;
	cursor: pointer;
	transition: all 0.15s ease;
}

.btn-clear-filter-inline:hover {
	background: rgba(78, 161, 224, 0.22);
	border-color: #4ea1e0;
	color: #ffffff;
}

.order-tabs-bar {
	display: flex;
	gap: 6px;
	margin-bottom: 12px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.08);
	padding-bottom: 10px;
	flex-shrink: 0;
}

.order-tab-btn {
	display: inline-flex;
	align-items: center;
	gap: 7px;
	padding: 6px 13px;
	border-radius: 8px;
	border: 1px solid transparent;
	background: transparent;
	color: #94a3b8;
	font-size: 13.5px;
	font-weight: 600;
	cursor: pointer;
	white-space: nowrap !important;
	flex-shrink: 0;
	transition: all 0.15s ease;
}

.order-tab-btn span {
	white-space: nowrap !important;
}

.order-tab-btn:hover {
	background: rgba(255, 255, 255, 0.04);
	color: #f1f5f9;
}

.order-tab-btn.active {
	background: #161b22;
	border-color: #3a424e;
	color: #4ea1e0;
	font-weight: 700;
}

.tab-badge {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	min-width: 20px;
	height: 19px;
	padding: 0 6px;
	border-radius: 10px;
	font-size: 12.5px;
	font-weight: 700;
	background: rgba(255, 255, 255, 0.08);
	color: #94a3b8;
	font-variant-numeric: tabular-nums;
}

.order-tab-btn.active .tab-badge {
	background: rgba(78, 161, 224, 0.2);
	color: #4ea1e0;
}

.sla-cell {
	display: inline-flex;
	flex-direction: column;
	align-items: center;
	gap: 2px;
}

.sla-supplier {
	font-size: 10.5px;
	font-weight: 700;
	color: #cbd5e1;
	letter-spacing: 0.3px;
}

.sla-badge {
	font-size: 10.5px;
	font-weight: 700;
	padding: 2px 7px;
	border-radius: 4px;
	white-space: nowrap;
}

.sla-ontime {
	background: rgba(148, 163, 184, 0.15);
	color: #94a3b8;
	border: 1px solid rgba(148, 163, 184, 0.3);
}

.sla-today {
	background: rgba(245, 158, 11, 0.18);
	color: #fbbf24;
	border: 1px solid rgba(245, 158, 11, 0.4);
}

.sla-overdue {
	background: rgba(239, 68, 68, 0.25);
	color: #fca5a5;
	border: 1px solid rgba(239, 68, 68, 0.5);
	animation: pulse-red 2s infinite;
}

@keyframes pulse-red {
	0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
	50% { box-shadow: 0 0 0 4px rgba(239, 68, 68, 0); }
}

.factory-status-cell {
	display: inline-flex;
	align-items: center;
	gap: 6px;
	justify-content: center;
}

.badge-mat {
	font-size: 10.5px;
	font-weight: 700;
	padding: 2px 6px;
	border-radius: 4px;
}

.mat-ready {
	background: rgba(52, 211, 153, 0.15);
	color: #34d399;
	border: 1px solid rgba(52, 211, 153, 0.3);
}

.mat-waiting {
	background: rgba(245, 158, 11, 0.15);
	color: #fbbf24;
	border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-stage {
	font-size: 11px;
	font-weight: 600;
	color: #93c5fd;
	background: rgba(78, 161, 224, 0.12);
	border: 1px solid rgba(78, 161, 224, 0.3);
	padding: 2px 6px;
	border-radius: 4px;
}

</style>

<style scoped>
.portal-layout {
	display: flex;
	height: 100vh;
	overflow: hidden;
}

.sidebar {
	width: 216px;
	height: 100%;
	flex-shrink: 0;
	background: #161b22;
	border-right: 1px solid #2d333b;
	padding: 14px 10px;
	display: flex;
	flex-direction: column;
	gap: 6px;
	z-index: 10;
}

.brand-block {
	display: flex;
	align-items: center;
	gap: 9px;
	padding: 4px 6px 12px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.07);
	margin-bottom: 6px;
}

.brand-logo {
	height: 24px;
	width: auto;
	max-width: 36px;
	object-fit: contain;
	background: transparent;
	filter: drop-shadow(0 2px 6px rgba(237, 28, 36, 0.35));
}

.brand-title {
	font-weight: 800;
	letter-spacing: 0.03em;
	color: #ffffff;
	font-size: 14px;
	white-space: nowrap;
}

.nav-menu {
	display: flex;
	flex-direction: column;
	gap: 4px;
	flex: 1;
}

.nav-btn {
	display: flex;
	align-items: center;
	gap: 10px;
	width: 100%;
	text-align: left;
	background: transparent;
	border: 0;
	border-radius: 8px;
	color: #9da7b5;
	font-size: 14.5px;
	font-weight: 600;
	padding: 9px 12px;
	cursor: pointer;
	transition: all 0.15s ease;
}

.nav-btn:hover {
	color: #eef1f6;
	background: rgba(255, 255, 255, 0.04);
}

.nav-btn.active {
	background: rgba(78, 161, 224, 0.14);
	color: #4ea1e0;
	font-weight: 700;
}

.nav-icon {
	width: 18px;
	height: 18px;
	flex-shrink: 0;
	opacity: 0.85;
}

.nav-btn.active .nav-icon {
	opacity: 1;
	stroke: #4ea1e0;
}

.nav-text {
	flex: 1;
}

.nav-badge {
	font-size: 11.5px;
	font-weight: 700;
	padding: 1px 7px;
	border-radius: 10px;
	background: rgba(255, 255, 255, 0.08);
	color: #9da7b5;
}

.nav-btn.active .nav-badge {
	background: rgba(78, 161, 224, 0.25);
	color: #4ea1e0;
}

.sidebar-footer {
	margin-top: auto;
	padding-top: 12px;
	border-top: 1px solid rgba(255, 255, 255, 0.07);
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 6px;
	padding-left: 4px;
	padding-right: 2px;
}

.user-block {
	display: flex;
	align-items: center;
	gap: 8px;
	min-width: 0;
	flex: 1;
}

.user-avatar {
	width: 28px;
	height: 28px;
	border-radius: 50%;
	background: #1f2937;
	border: 1px solid #374151;
	display: flex;
	align-items: center;
	justify-content: center;
	color: #9ca3af;
	flex-shrink: 0;
}

.user-id {
	font-size: 13px;
	font-weight: 600;
	color: #cbd5e1;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.btn-logout {
	width: 30px;
	height: 30px;
	border-radius: 6px;
	border: none;
	background: transparent;
	color: #94a3b8;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.15s ease;
	flex-shrink: 0;
}

.btn-logout:hover {
	color: #f87171;
	background: rgba(239, 68, 68, 0.12);
}

.main-content {
	flex: 1;
	min-width: 0;
	height: 100vh;
	display: flex;
	flex-direction: column;
	overflow: hidden;
	padding: 20px 32px 24px;
}

.page-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 16px;
	flex-shrink: 0;
}

.page-title {
	font-size: 22px;
	font-weight: 800;
	color: #eef1f6;
	letter-spacing: -0.01em;
}

.btn-new-quote {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	font-family: inherit;
	font-size: 15px;
	font-weight: 700;
	color: #ffffff;
	background: #4ea1e0;
	border: 0;
	border-radius: 8px;
	padding: 11px 22px;
	cursor: pointer;
	transition: background 0.15s;
}

.btn-new-quote:hover {
	background: #3b8ac4;
}

.table-container {
	flex: 1;
	min-height: 0;
	background: #161b22;
	border: 1px solid #3a424e;
	border-radius: 12px;
	overflow-y: auto;
	overflow-x: auto;
	position: relative;
	scrollbar-width: thin;
	scrollbar-color: #3a424e #161b22;
}

.table-container::-webkit-scrollbar {
	width: 8px;
	height: 8px;
}

.table-container::-webkit-scrollbar-track {
	background: #161b22;
}

.table-container::-webkit-scrollbar-thumb {
	background: #3a424e;
	border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb:hover {
	background: #4ea1e0;
}

.data-table {
	width: 100%;
	border-collapse: collapse;
	font-size: 15px;
}

.data-table th {
	text-align: left;
	font-size: 14.5px;
	font-weight: 700;
	text-transform: uppercase;
	letter-spacing: 0.04em;
	color: #9da7b5;
	padding: 14px 18px;
	border-bottom: 1px solid #3a424e;
	background: #1a1f27;
	position: sticky;
	top: 0;
	z-index: 5;
	box-shadow: 0 1px 0 #3a424e;
}

.data-table td {
	padding: 14px 18px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.05);
	color: #eef1f6;
}

.table-row:hover {
	background: rgba(255, 255, 255, 0.02);
}

.text-secondary {
	color: #9da7b5;
}

.text-primary {
	color: #4ea1e0;
}

.font-bold {
	font-weight: 700;
}

.text-right {
	text-align: right;
}

.text-center {
	text-align: center;
}

.text-num {
	font-variant-numeric: tabular-nums;
}

.status-badge {
	display: inline-block;
	font-size: 13px;
	font-weight: 700;
	padding: 4px 10px;
	border-radius: 6px;
}

.status-open {
	background: rgba(254, 200, 75, 0.14);
	color: #fec84b;
}

.status-draft {
	background: rgba(157, 167, 181, 0.14);
	color: #9da7b5;
}

.status-ordered {
	background: rgba(81, 207, 102, 0.14);
	color: #51cf66;
}

.status-lost {
	background: rgba(100, 116, 139, 0.2);
	color: #64748b;
}

.status-expired {
	background: rgba(249, 112, 102, 0.14);
	color: #f97066;
}

.row-actions {
	white-space: nowrap;
}

.row-btn {
	display: inline-block;
	font-family: inherit;
	font-size: 13px;
	font-weight: 700;
	color: #4ea1e0;
	background: rgba(78, 161, 224, 0.12);
	border: 1px solid rgba(78, 161, 224, 0.4);
	border-radius: 6px;
	padding: 5px 12px;
	margin: 0 2px;
	cursor: pointer;
	transition: all 0.15s;
}

.row-btn-danger {
	color: #f97066;
	background: rgba(249, 112, 102, 0.1);
	border-color: rgba(249, 112, 102, 0.4);
}

.row-btn-primary {
	color: #ffffff;
	background: #4ea1e0;
	border-color: #4ea1e0;
}

.cursor-pointer {
	cursor: pointer;
	transition: all 0.15s ease;
}

.sub-filter-chips {
	display: flex;
	align-items: center;
	gap: 6px;
	flex-shrink: 0;
}

.sub-chip-btn {
	background: #161b22;
	border: 1px solid #3a424e;
	color: #94a3b8;
	font-size: 12.5px;
	padding: 4px 10px;
	border-radius: 9999px;
	cursor: pointer;
	white-space: nowrap;
	transition: all 0.15s ease;
}

.sub-chip-btn:hover {
	color: #ffffff;
	border-color: #64748b;
}

.sub-chip-btn.active {
	background: rgba(78, 161, 224, 0.15);
	border-color: #4ea1e0;
	color: #4ea1e0;
	font-weight: 600;
}

.badge-role-user {
	padding: 2px 7px;
	border-radius: 4px;
	background: #1e1b4b;
	color: #c4b5fd;
	border: 1px solid rgba(196, 181, 253, 0.25);
}

.table-row.cursor-pointer:hover {
	background: rgba(78, 161, 224, 0.08) !important;
}

.status-hold {
	background: rgba(239, 68, 68, 0.2);
	color: #f87171;
	border: 1px solid rgba(239, 68, 68, 0.4);
}

.badge-tag-cust {
	display: inline-block;
	font-size: 11px;
	font-weight: 700;
	padding: 2px 6px;
	border-radius: 4px;
}

.tag-postpaid {
	background: rgba(99, 102, 241, 0.2);
	color: #a5b4fc;
	border: 1px solid rgba(99, 102, 241, 0.4);
}

.tag-prepaid {
	background: rgba(245, 158, 11, 0.15);
	color: #fbbf24;
	border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-tag-group {
	display: inline-block;
	font-size: 11.5px;
	font-weight: 600;
	padding: 3px 8px;
	border-radius: 5px;
	background: #1c222d;
	color: #93c5fd;
	border: 1px solid #334155;
}

.text-emerald {
	color: #34d399;
}

.text-amber {
	color: #f59e0b;
}

.font-mono {
	font-family: 'JetBrains Mono', monospace;
}

.truncate {
	max-width: 220px;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.deposit-mini-cell {
	display: flex;
	flex-direction: column;
	align-items: flex-end;
	gap: 3px;
}

.mini-bar-track {
	width: 100%;
	max-width: 80px;
	height: 3px;
	background: rgba(255, 255, 255, 0.08);
	border-radius: 2px;
	overflow: hidden;
}

.mini-bar-fill {
	height: 100%;
	transition: width 0.3s ease;
}

.bg-emerald {
	background-color: #34d399;
}

.bg-amber {
	background-color: #f59e0b;
}

.orders-view-wrapper {
	display: flex;
	flex-direction: column;
}


.sla-cell {
	display: inline-flex;
	flex-direction: column;
	align-items: center;
	gap: 2px;
}

.sla-supplier {
	font-size: 10.5px;
	font-weight: 700;
	color: #cbd5e1;
	letter-spacing: 0.3px;
}

.sla-badge {
	font-size: 10.5px;
	font-weight: 700;
	padding: 2px 7px;
	border-radius: 4px;
	white-space: nowrap;
}

.sla-ontime {
	background: rgba(148, 163, 184, 0.15);
	color: #94a3b8;
	border: 1px solid rgba(148, 163, 184, 0.3);
}

.sla-today {
	background: rgba(245, 158, 11, 0.18);
	color: #fbbf24;
	border: 1px solid rgba(245, 158, 11, 0.4);
}

.sla-overdue {
	background: rgba(239, 68, 68, 0.25);
	color: #fca5a5;
	border: 1px solid rgba(239, 68, 68, 0.5);
	animation: pulse-red 2s infinite;
}

@keyframes pulse-red {
	0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
	50% { box-shadow: 0 0 0 4px rgba(239, 68, 68, 0); }
}

.factory-status-cell {
	display: inline-flex;
	align-items: center;
	gap: 6px;
	justify-content: center;
}

.badge-mat {
	font-size: 10.5px;
	font-weight: 700;
	padding: 2px 6px;
	border-radius: 4px;
}

.mat-ready {
	background: rgba(52, 211, 153, 0.15);
	color: #34d399;
	border: 1px solid rgba(52, 211, 153, 0.3);
}

.mat-waiting {
	background: rgba(245, 158, 11, 0.15);
	color: #fbbf24;
	border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-stage {
	font-size: 11px;
	font-weight: 600;
	color: #93c5fd;
	background: rgba(78, 161, 224, 0.12);
	border: 1px solid rgba(78, 161, 224, 0.3);
	padding: 2px 6px;
	border-radius: 4px;
}

</style>
