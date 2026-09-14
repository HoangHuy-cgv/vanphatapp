<template>
	<Teleport to="body">
		<div v-if="isOpen" class="modal-backdrop" @click.self="$emit('close')">
		<div class="modal-panel" role="dialog" aria-modal="true" aria-labelledby="modal-order-title">
			<!-- Header -->
			<div class="modal-head">
				<div class="head-left">
					<h3 id="modal-order-title" class="modal-title">Tạo Đơn Hàng Mới</h3>
					<span class="head-badge">{{ groupTabLabel }}</span>
				</div>
				<button type="button" class="btn-close" title="Đóng (Esc)" @click="$emit('close')">
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<line x1="18" y1="6" x2="6" y2="18"></line>
						<line x1="6" y1="6" x2="18" y2="18"></line>
					</svg>
				</button>
			</div>

			<form @submit.prevent="handleSubmit" class="modal-form">
				<!-- KHỐI 1: THÔNG TIN KHÁCH & PHÂN LOẠI -->
				<div class="form-section">
					<div class="info-row-1">
						<!-- Chọn khách hàng -->
						<div class="field-col">
							<label class="field-label">Khách hàng</label>
							<select v-model="selectedCustomerId" class="select-input" @change="onCustomerChange" required>
								<option value="" disabled>-- Chọn khách hàng --</option>
								<option v-for="c in customers" :key="c.id" :value="c.id">
									{{ c.alias }} • {{ c.name }}
								</option>
							</select>
						</div>

						<!-- Brand / Thương hiệu -->
						<div class="field-col">
							<label class="field-label">Brand / Nhãn hiệu</label>
							<input
								type="text"
								v-model="brand"
								class="text-input"
								placeholder="VD: BABA, 888, FUSIMI"
								required
							/>
						</div>

						<!-- Nhóm sản phẩm -->
						<div class="field-col">
							<label class="field-label">Nhóm sản phẩm</label>
							<select v-model="productGroup" class="select-input" @change="onProductGroupChange" required>
								<option value="Túi màng ghép">Túi màng ghép (Xưởng SX)</option>
								<option value="Cuộn màng ghép">Cuộn màng ghép (Xưởng SX - Kg)</option>
								<option value="Túi NGCS">Túi NGCS (In lụa phôi có sẵn)</option>
								<option value="Túi màng đơn">Túi màng đơn (Mua ngoài - Kg)</option>
							</select>
						</div>
					</div>

					<div class="info-row-2">
						<!-- Ngày hẹn giao -->
						<div class="field-col">
							<label class="field-label">Ngày hẹn giao</label>
							<input type="date" v-model="deliveryDate" class="text-input font-mono" required />
						</div>

						<!-- Hình thức thanh toán -->
						<div class="field-col">
							<label class="field-label">Hình thức thanh toán</label>
							<select v-model="paymentType" class="select-input">
								<option value="Trả trước">Trả trước (Cọc 50%)</option>
								<option value="Trả sau">Trả sau (Công nợ)</option>
							</select>
						</div>
					</div>
				</div>

				<!-- KHỐI 2: THÍCH ỨNG ĐỘNG THEO QUY TRÌNH -->

				<!-- ============================================================== -->
				<!-- QUY TRÌNH 1: SẢN PHẨM ĐỘC QUYỀN (TÚI MÀNG GHÉP / CUỘN MÀNG GHÉP) -->
				<!-- ============================================================== -->
				<div v-if="isCustomMto" class="form-section mto-section">
					<!-- Chọn sản phẩm của khách -->
					<div class="product-picker-bar">
						<div class="field-col flex-1">
							<label class="field-label">Sản phẩm độc quyền của khách</label>
							<select v-model="selectedCustomItemCode" class="select-input" @change="onCustomItemChange" required>
								<option value="" disabled>-- Chọn quy cách đã lưu của khách --</option>
								<option v-for="item in availableCustomItems" :key="item.item_code" :value="item.item_code">
									{{ item.custom_alias || item.item_name }} ({{ item.dimensions_text }})
								</option>
							</select>
						</div>
					</div>

					<!-- Thông số tự bung -->
					<div v-if="currentCustomItem" class="item-specs-banner">
						<div class="banner-specs">
							<span class="spec-tag">{{ currentCustomItem.dimensions_text }}</span>
							<span class="spec-tag text-cyan">{{ currentCustomItem.accessory }}</span>
							<span class="spec-tag text-purple">{{ currentCustomItem.print_type }}</span>
							<div class="mat-chips-row">
								<span v-for="m in currentCustomItem.materials" :key="m" class="mat-chip-badge">
									{{ m }}
								</span>
							</div>
						</div>
						<div class="banner-price">
							Đơn giá chuẩn: <span class="font-bold text-emerald">{{ formatCurrency(currentCustomItem.base_rate) }}</span> / {{ currentCustomItem.uom }}
						</div>
					</div>

					<!-- Bảng Danh Sách Mẫu In / Hương Vị (Variants) -->
					<div class="table-block">
						<div class="table-block-head">
							<span class="block-title">DANH SÁCH MẪU IN / HƯƠNG VỊ</span>
							<button type="button" class="btn-add-row" @click="addVariantRow">
								+ Thêm mẫu in
							</button>
						</div>

						<table class="form-table">
							<thead>
								<tr>
									<th style="width: 35%;">Tên mẫu in / Hương vị</th>
									<th style="width: 20%; text-align: right;">Số lượng</th>
									<th style="width: 10%; text-align: center;">ĐVT</th>
									<th style="width: 15%; text-align: right;">Đơn giá</th>
									<th style="width: 15%; text-align: right;">Thành tiền</th>
									<th style="width: 5%;"></th>
								</tr>
							</thead>
							<tbody>
								<tr v-for="(row, idx) in variantRows" :key="idx">
									<td>
										<input
											type="text"
											v-model="row.variant_name"
											class="text-input"
											placeholder="VD: Nước phở bò, Màu Hồng..."
											required
										/>
									</td>
									<td>
										<input
											type="number"
											v-model.number="row.qty"
											class="text-input text-right text-num"
											min="1"
											step="1"
											required
										/>
									</td>
									<td class="text-center font-medium text-secondary">
										{{ currentCustomItem ? currentCustomItem.uom : 'Túi' }}
									</td>
									<td>
										<input
											type="number"
											v-model.number="row.rate"
											class="text-input text-right text-num"
											min="0"
											required
										/>
									</td>
									<td class="text-right text-num font-bold text-white">
										{{ formatCurrency(row.qty * row.rate) }}
									</td>
									<td class="text-center">
										<button
											v-if="variantRows.length > 1"
											type="button"
											class="btn-remove-row"
											title="Xóa dòng"
											@click="removeVariantRow(idx)"
										>
											✕
										</button>
									</td>
								</tr>
							</tbody>
						</table>
					</div>

					<!-- Phần Trục In (Nếu có) -->
					<div class="cylinder-block">
						<label class="checkbox-label">
							<input type="checkbox" v-model="hasNewCylinders" />
							<span>Đơn hàng có làm bộ trục in mới</span>
						</label>

						<div v-if="hasNewCylinders" class="cylinder-inputs">
							<div class="cyl-col">
								<label class="field-label-sm">Số cây trục</label>
								<input type="number" v-model.number="cylinderCount" class="text-input text-right text-num" min="1" />
							</div>
							<div class="cyl-col">
								<label class="field-label-sm">Đơn giá trục (VNĐ/cây)</label>
								<input type="number" v-model.number="cylinderRate" class="text-input text-right text-num" min="0" step="1000" />
							</div>
							<div class="cyl-col">
								<label class="field-label-sm">Tiền trục</label>
								<div class="cyl-total-val text-num">{{ formatCurrency(cylinderCount * cylinderRate) }}</div>
							</div>
						</div>
					</div>
				</div>

				<!-- ============================================================== -->
				<!-- QUY TRÌNH 2: PHÔI DÙNG CHUNG (TÚI NGCS & TÚI MÀNG ĐƠN) -->
				<!-- ============================================================== -->
				<div v-else class="form-section generic-section">
					<!-- Tiêu đề in lụa của khách (Nếu là NGCS) -->
					<div v-if="productGroup === 'Túi NGCS'" class="field-col" style="margin-bottom: 16px;">
						<label class="field-label">Nội dung / Tên thương hiệu in lụa</label>
						<input
							type="text"
							v-model="screenPrintBrand"
							class="text-input"
							placeholder="VD: FUSIMI - Nước giặt cao cấp"
							required
						/>
					</div>

					<!-- Bảng Chọn Nhiều Mã Phôi Dùng Chung -->
					<div class="table-block">
						<div class="table-block-head">
							<span class="block-title">DANH SÁCH MÃ PHÔI / TÚI ĐẶT HÀNG</span>
							<button type="button" class="btn-add-row" @click="addGenericRow">
								+ Thêm loại phôi
							</button>
						</div>

						<table class="form-table">
							<thead>
								<tr>
									<th style="width: 40%;">Mã phôi & Quy cách</th>
									<th style="width: 20%; text-align: right;">Số lượng</th>
									<th style="width: 10%; text-align: center;">ĐVT</th>
									<th style="width: 15%; text-align: right;">Đơn giá</th>
									<th style="width: 15%; text-align: right;">Thành tiền</th>
									<th style="width: 5%;"></th>
								</tr>
							</thead>
							<tbody>
								<tr v-for="(row, idx) in genericRows" :key="idx">
									<td>
										<select v-model="row.item_code" class="select-input" @change="onGenericItemChange(row)" required>
											<option value="" disabled>-- Chọn mã phôi có sẵn --</option>
											<option v-for="item in availableGenericItems" :key="item.item_code" :value="item.item_code">
												{{ item.custom_alias || item.item_name }}
											</option>
										</select>
									</td>
									<td>
										<input
											type="number"
											v-model.number="row.qty"
											class="text-input text-right text-num"
											min="1"
											step="1"
											required
										/>
									</td>
									<td class="text-center font-medium text-secondary">
										{{ row.uom || 'Túi' }}
									</td>
									<td>
										<input
											type="number"
											v-model.number="row.rate"
											class="text-input text-right text-num"
											min="0"
											required
										/>
									</td>
									<td class="text-right text-num font-bold text-white">
										{{ formatCurrency(row.qty * row.rate) }}
									</td>
									<td class="text-center">
										<button
											v-if="genericRows.length > 1"
											type="button"
											class="btn-remove-row"
											title="Xóa dòng"
											@click="removeGenericRow(idx)"
										>
											✕
										</button>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>

				<!-- KHỐI 3: ĐỐI SOÁT TÀI CHÍNH TỐI GIẢN & ACTIONS -->
				<div class="finance-footer-card">
					<div class="fin-summary-rows">
						<div class="fin-row">
							<span class="fin-label">Tiền hàng (chưa VAT):</span>
							<span class="fin-val text-num">{{ formatCurrency(netTotal) }}</span>
						</div>
						<div class="fin-row">
							<span class="fin-label">Thuế VAT (8%):</span>
							<span class="fin-val text-num">{{ formatCurrency(vatAmount) }}</span>
						</div>
						<div v-if="cylinderTotal > 0" class="fin-row">
							<span class="fin-label">Tiền trục:</span>
							<span class="fin-val text-num">{{ formatCurrency(cylinderTotal) }}</span>
						</div>
						<div class="fin-row total-row">
							<span class="fin-label-lg">TỔNG THANH TOÁN:</span>
							<span class="fin-val-lg text-num">{{ formatCurrency(grandTotal) }}</span>
						</div>
						<div v-if="paymentType === 'Trả trước'" class="fin-row deposit-row">
							<span class="fin-label">Cọc yêu cầu (50% hàng + 100% trục):</span>
							<span class="fin-val-deposit text-num">{{ formatCurrency(requiredDeposit) }}</span>
						</div>
					</div>

					<div class="form-actions">
						<button type="button" class="btn-cancel" @click="$emit('close')">
							Hủy
						</button>
						<button type="submit" class="btn-submit">
							+ TẠO ĐƠN HÀNG
						</button>
					</div>
				</div>
			</form>
		</div>
		</div>
	</Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { MASTER_CUSTOMERS, MASTER_CATALOG_ITEMS } from '../data/mockData.js';

const props = defineProps({
	isOpen: { type: Boolean, default: false },
	initialTab: { type: String, default: 'xuong_sx' },
});

const emit = defineEmits(['close', 'create-order']);

// Master lists
const customers = ref(MASTER_CUSTOMERS);
const catalogItems = ref(MASTER_CATALOG_ITEMS);

// Form Fields
const selectedCustomerId = ref('');
const brand = ref('');
const productGroup = ref('Túi màng ghép');
const deliveryDate = ref('');
const paymentType = ref('Trả trước');

// MTO state (Màng ghép / Cuộn)
const selectedCustomItemCode = ref('');
const variantRows = ref([
	{ variant_name: '', qty: 10000, rate: 0 },
]);
const hasNewCylinders = ref(false);
const cylinderCount = ref(0);
const cylinderRate = ref(0);

// MTS state (NGCS / Màng đơn)
const screenPrintBrand = ref('');
const genericRows = ref([
	{ item_code: '', item_name: '', variant_name: '', qty: 5000, rate: 0, uom: 'Túi' },
]);

// Computed logic
const currentCustomer = computed(() => {
	return customers.value.find((c) => c.id === selectedCustomerId.value) || null;
});

const isCustomMto = computed(() => {
	return productGroup.value === 'Túi màng ghép' || productGroup.value === 'Cuộn màng ghép';
});

const groupTabLabel = computed(() => {
	if (isCustomMto.value) return 'XƯỞNG SẢN XUẤT (ĐỘC QUYỀN MTO)';
	if (productGroup.value === 'Túi NGCS') return 'TÚI NGCS (IN LỤA PHÔI SẴN)';
	return 'MUA NGOÀI TRỌN GÓI';
});

// Filtered custom products for selected customer
const availableCustomItems = computed(() => {
	if (!currentCustomer.value) return [];
	return catalogItems.value.filter(
		(item) => item.is_custom && item.customer_alias === currentCustomer.value.alias && item.product_group === productGroup.value
	);
});

// Currently selected custom item
const currentCustomItem = computed(() => {
	return catalogItems.value.find((i) => i.item_code === selectedCustomItemCode.value) || null;
});

// Available generic items
const availableGenericItems = computed(() => {
	return catalogItems.value.filter(
		(item) => !item.is_custom && item.product_group === productGroup.value
	);
});

// Financial Computations
const netTotal = computed(() => {
	if (isCustomMto.value) {
		return variantRows.value.reduce((sum, r) => sum + (Number(r.qty) || 0) * (Number(r.rate) || 0), 0);
	} else {
		return genericRows.value.reduce((sum, r) => sum + (Number(r.qty) || 0) * (Number(r.rate) || 0), 0);
	}
});

const vatRate = 8;
const vatAmount = computed(() => Math.round(netTotal.value * (vatRate / 100)));

const cylinderTotal = computed(() => {
	if (!isCustomMto.value || !hasNewCylinders.value) return 0;
	return (Number(cylinderCount.value) || 0) * (Number(cylinderRate.value) || 0);
});

const grandTotal = computed(() => netTotal.value + vatAmount.value + cylinderTotal.value);

const requiredDeposit = computed(() => {
	if (paymentType.value === 'Trả sau') return 0;
	// 50% tiền hàng + 100% tiền trục
	return Math.round((netTotal.value + vatAmount.value) * 0.5 + cylinderTotal.value);
});

// Event Handlers
const onCustomerChange = () => {
	if (!currentCustomer.value) return;
	brand.value = currentCustomer.value.brand || '';
	paymentType.value = currentCustomer.value.payment_type || 'Trả trước';
	
	// Reset items
	selectedCustomItemCode.value = '';
	if (availableCustomItems.value.length > 0) {
		selectedCustomItemCode.value = availableCustomItems.value[0].item_code;
		onCustomItemChange();
	}
};

const onProductGroupChange = () => {
	if (isCustomMto.value) {
		if (availableCustomItems.value.length > 0) {
			selectedCustomItemCode.value = availableCustomItems.value[0].item_code;
			onCustomItemChange();
		} else {
			selectedCustomItemCode.value = '';
		}
	} else {
		if (availableGenericItems.value.length > 0) {
			genericRows.value = [
				{
					item_code: availableGenericItems.value[0].item_code,
					item_name: availableGenericItems.value[0].item_name,
					variant_name: availableGenericItems.value[0].item_name,
					qty: productGroup.value === 'Túi màng đơn' ? 100 : 5000,
					rate: availableGenericItems.value[0].base_rate,
					uom: availableGenericItems.value[0].uom,
				},
			];
		}
	}
};

const onCustomItemChange = () => {
	if (!currentCustomItem.value) return;
	// Initialize default variants
	const defaults = currentCustomItem.value.default_variants || ['Quy cách chuẩn'];
	variantRows.value = defaults.map((name) => ({
		variant_name: name,
		qty: 10000,
		rate: currentCustomItem.value.base_rate || 0,
	}));
	cylinderCount.value = currentCustomItem.value.cylinder_count || 0;
	cylinderRate.value = currentCustomItem.value.cylinder_rate || 3100000;
};

const onGenericItemChange = (row) => {
	const item = catalogItems.value.find((i) => i.item_code === row.item_code);
	if (item) {
		row.item_name = item.item_name;
		row.variant_name = item.item_name;
		row.rate = item.base_rate;
		row.uom = item.uom;
	}
};

const addVariantRow = () => {
	const rate = currentCustomItem.value ? currentCustomItem.value.base_rate : 0;
	variantRows.value.push({
		variant_name: '',
		qty: 10000,
		rate: rate,
	});
};

const removeVariantRow = (index) => {
	if (variantRows.value.length > 1) {
		variantRows.value.splice(index, 1);
	}
};

const addGenericRow = () => {
	const firstItem = availableGenericItems.value[0] || {};
	genericRows.value.push({
		item_code: firstItem.item_code || '',
		item_name: firstItem.item_name || '',
		variant_name: firstItem.item_name || '',
		qty: productGroup.value === 'Túi màng đơn' ? 100 : 5000,
		rate: firstItem.base_rate || 0,
		uom: firstItem.uom || 'Túi',
	});
};

const removeGenericRow = (index) => {
	if (genericRows.value.length > 1) {
		genericRows.value.splice(index, 1);
	}
};

// Default setup when modal opens
watch(
	() => props.isOpen,
	(val) => {
		if (val) {
			// Set default delivery date (+7 days)
			const d = new Date();
			d.setDate(d.getDate() + 7);
			deliveryDate.value = d.toISOString().split('T')[0];

			// Set initial product group according to active tab
			if (props.initialTab === 'ngcs') {
				productGroup.value = 'Túi NGCS';
				selectedCustomerId.value = 'KH-00005'; // FUSIMI
			} else if (props.initialTab === 'mua_ngoai') {
				productGroup.value = 'Túi màng đơn';
				selectedCustomerId.value = 'KH-00007'; // VẠN AN
			} else {
				productGroup.value = 'Túi màng ghép';
				selectedCustomerId.value = 'KH-00001'; // DS 888
			}

			onCustomerChange();
		}
	},
	{ immediate: true }
);

// Submit order
const handleSubmit = () => {
	if (!currentCustomer.value) return;

	let orderTab = 'xuong_sx';
	if (productGroup.value === 'Túi NGCS') orderTab = 'ngcs';
	else if (productGroup.value === 'Túi màng đơn') orderTab = 'mua_ngoai';

	const timestampSuffix = Math.floor(Math.random() * 900) + 100;
	const orderName = `DH-2609-${timestampSuffix}`;

	let builtItems = [];
	let totalQty = 0;
	let orderDesc = '';
	let dimsText = '';
	let mats = [];
	let accessoryText = 'Không vòi';
	let printTypeText = 'In trục';
	let cylinderStatusText = 'Không trục';
	let artworkUrl = '/samples/baba.jpg';

	if (isCustomMto.value && currentCustomItem.value) {
		orderDesc = currentCustomItem.value.item_name;
		dimsText = currentCustomItem.value.dimensions_text;
		mats = currentCustomItem.value.materials;
		accessoryText = currentCustomItem.value.accessory;
		printTypeText = currentCustomItem.value.print_type;
		artworkUrl = currentCustomItem.value.artwork_url;
		cylinderStatusText = hasNewCylinders.value ? `${cylinderCount.value} cây` : 'Có sẵn trục';

		variantRows.value.forEach((v) => {
			totalQty += Number(v.qty) || 0;
			builtItems.push({
				item_code: currentCustomItem.value.item_code,
				item_name: `${currentCustomItem.value.item_name} - ${v.variant_name}`,
				variant_name: v.variant_name,
				artwork_url: artworkUrl,
				qty: Number(v.qty) || 0,
				uom: currentCustomItem.value.uom,
				rate: Number(v.rate) || 0,
				amount: (Number(v.qty) || 0) * (Number(v.rate) || 0),
				is_cylinder: false,
			});
		});

		if (hasNewCylinders.value && cylinderCount.value > 0) {
			builtItems.push({
				item_code: `TRUC-${currentCustomItem.value.item_code}`,
				item_name: `Bộ trục ${currentCustomItem.value.item_name} (${cylinderCount.value} cây)`,
				variant_name: 'Trục in ống đồng',
				artwork_url: null,
				qty: cylinderCount.value,
				uom: 'Cây',
				rate: cylinderRate.value,
				amount: cylinderTotal.value,
				is_cylinder: true,
			});
		}
	} else {
		// Generic MTS
		if (productGroup.value === 'Túi NGCS') {
			orderDesc = `Túi NGCS in lụa ${screenPrintBrand.value || brand.value}`;
			printTypeText = 'In lụa';
			artworkUrl = '/samples/ngcs.jpg';
		} else {
			orderDesc = `Túi màng đơn ${brand.value}`;
			printTypeText = 'Không in';
			artworkUrl = '/samples/mangdon.jpg';
		}

		genericRows.value.forEach((g) => {
			const itemDef = catalogItems.value.find((i) => i.item_code === g.item_code) || {};
			dimsText = itemDef.dimensions_text || '';
			mats = itemDef.materials || [];
			accessoryText = itemDef.accessory || 'Không quai';
			totalQty += Number(g.qty) || 0;

			builtItems.push({
				item_code: g.item_code,
				item_name: `${itemDef.item_name || g.item_code} (${brand.value})`,
				variant_name: itemDef.item_name || g.item_code,
				artwork_url: artworkUrl,
				qty: Number(g.qty) || 0,
				uom: g.uom,
				rate: Number(g.rate) || 0,
				amount: (Number(g.qty) || 0) * (Number(g.rate) || 0),
				is_cylinder: false,
			});
		});
	}

	const newOrder = {
		name: orderName,
		transaction_date: new Date().toISOString().split('T')[0],
		customer: currentCustomer.value.name,
		customer_name: currentCustomer.value.name,
		customer_alias: currentCustomer.value.alias,
		brand: brand.value,
		payment_type: paymentType.value,
		order_tab: orderTab,
		product_group: productGroup.value,
		product_type: isCustomMto.value ? currentCustomItem.value?.product_type : 'Túi có sẵn',
		accessory: accessoryText,
		print_type: printTypeText,
		cylinder_status: cylinderStatusText,
		description: orderDesc,
		dimensions_text: dimsText,
		materials: mats,
		artwork_url: artworkUrl,
		item_name: builtItems[0]?.item_name || orderDesc,
		qty: totalQty,
		uom: builtItems[0]?.uom || 'Túi',
		net_total: netTotal.value,
		vat_rate: vatRate,
		vat_amount: vatAmount.value,
		cylinder_total: cylinderTotal.value,
		grand_total: grandTotal.value,
		required_deposit: requiredDeposit.value,
		advance_paid: 0,
		outstanding_amount: grandTotal.value,
		deposit_pct: 0,
		order_state: paymentType.value === 'Trả sau' ? 'Đang xử lý' : 'Tạm giữ (Chưa đủ cọc)',
		is_hold: paymentType.value !== 'Trả sau',
		status: 'To Deliver and Bill',
		docstatus: 1,
		materials_status: isCustomMto.value ? 'Chờ cọc' : 'Có sẵn phôi',
		factory_stage: isCustomMto.value ? 'Chờ cọc' : 'Chờ in lụa',
		completed_qty: 0,
		supplier_name: orderTab === 'ngcs' ? 'MỘC ẤN' : (orderTab === 'mua_ngoai' ? 'ANH TÙNG' : null),
		supplier_eta_days: orderTab === 'xuong_sx' ? null : 3,
		procurement_stage: orderTab === 'xuong_sx' ? null : 'Chờ giao việc NCC',
		items: builtItems,
	};

	emit('create-order', newOrder);
	emit('close');
};

const formatCurrency = (val) => {
	if (!val && val !== 0) return '0 đ';
	return new Intl.NumberFormat('vi-VN').format(Math.round(val)) + ' đ';
};
</script>

<style scoped>
.modal-backdrop {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.75);
	backdrop-filter: blur(4px);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1050;
	padding: 16px;
}

.modal-panel {
	background: #161b22;
	border: 1px solid #3a424e;
	border-radius: 12px;
	width: 100%;
	max-width: 960px;
	max-height: 90vh;
	display: flex;
	flex-direction: column;
	box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
	overflow: hidden;
}

.modal-head {
	padding: 16px 20px;
	border-bottom: 1px solid rgba(255, 255, 255, 0.08);
	display: flex;
	justify-content: space-between;
	align-items: center;
	background: #1a1f27;
}

.head-left {
	display: flex;
	align-items: center;
	gap: 12px;
}

.modal-title {
	font-size: 18px;
	font-weight: 700;
	color: #ffffff;
	margin: 0;
}

.head-badge {
	font-size: 11px;
	font-weight: 700;
	text-transform: uppercase;
	padding: 2px 8px;
	border-radius: 4px;
	background: rgba(78, 161, 224, 0.15);
	color: #4ea1e0;
	border: 1px solid rgba(78, 161, 224, 0.3);
}

.btn-close {
	background: transparent;
	border: none;
	color: #8b949e;
	cursor: pointer;
	padding: 4px;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 6px;
	transition: all 0.15s ease;
}

.btn-close:hover {
	color: #ffffff;
	background: rgba(255, 255, 255, 0.08);
}

.modal-form {
	padding: 20px;
	overflow-y: auto;
	overflow-x: hidden;
	display: flex;
	flex-direction: column;
	gap: 20px;
}

/* Sections */
.form-section {
	background: #12161f;
	border: 1px solid rgba(255, 255, 255, 0.06);
	border-radius: 8px;
	padding: 16px;
}

.info-row-1 {
	display: grid;
	grid-template-columns: 2fr 1.2fr 1.6fr;
	gap: 14px;
	margin-bottom: 12px;
}

.info-row-2 {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 14px;
}

.field-col {
	display: flex;
	flex-direction: column;
	gap: 6px;
}

.flex-1 {
	flex: 1;
}

.field-label {
	font-size: 13px;
	font-weight: 600;
	color: #8b949e;
}

.field-label-sm {
	font-size: 12px;
	font-weight: 600;
	color: #8b949e;
}

.text-input,
.select-input {
	height: 38px;
	background: #161b22;
	border: 1px solid #3a424e;
	border-radius: 6px;
	color: #ffffff;
	padding: 0 12px;
	font-size: 14px;
	font-family: inherit;
	outline: none;
	transition: border-color 0.15s ease;
}

.text-input:focus,
.select-input:focus {
	border-color: #4ea1e0;
	box-shadow: 0 0 0 1px #4ea1e0;
}

.item-specs-banner {
	display: flex;
	justify-content: space-between;
	align-items: center;
	background: #1a1f27;
	border: 1px solid rgba(78, 161, 224, 0.2);
	border-radius: 6px;
	padding: 10px 14px;
	margin-top: 14px;
	margin-bottom: 14px;
}

.banner-specs {
	display: flex;
	align-items: center;
	gap: 8px;
	flex-wrap: wrap;
}

.spec-tag {
	font-size: 12px;
	font-weight: 600;
	color: #e6edf3;
	background: rgba(255, 255, 255, 0.08);
	padding: 2px 8px;
	border-radius: 4px;
}

.mat-chips-row {
	display: flex;
	gap: 4px;
}

.mat-chip-badge {
	font-size: 11px;
	font-weight: 700;
	background: rgba(56, 189, 248, 0.15);
	color: #38bdf8;
	padding: 2px 6px;
	border-radius: 4px;
	border: 1px solid rgba(56, 189, 248, 0.3);
}

.banner-price {
	font-size: 13px;
	color: #8b949e;
}

/* Table block */
.table-block {
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.table-block-head {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.block-title {
	font-size: 12px;
	font-weight: 700;
	letter-spacing: 0.5px;
	color: #8b949e;
}

.btn-add-row {
	background: rgba(78, 161, 224, 0.1);
	border: 1px solid rgba(78, 161, 224, 0.3);
	color: #4ea1e0;
	font-size: 12px;
	font-weight: 600;
	padding: 4px 10px;
	border-radius: 4px;
	cursor: pointer;
	transition: all 0.15s ease;
}

.btn-add-row:hover {
	background: #4ea1e0;
	color: #0b0f19;
}

.form-table {
	width: 100%;
	border-collapse: collapse;
}

.form-table th {
	font-size: 12px;
	font-weight: 600;
	color: #8b949e;
	padding: 8px;
	border-bottom: 1px solid #3a424e;
}

.form-table td {
	padding: 6px;
	vertical-align: middle;
}

.btn-remove-row {
	background: transparent;
	border: none;
	color: #f85149;
	font-size: 14px;
	cursor: pointer;
	padding: 4px;
}

.btn-remove-row:hover {
	color: #ff7b72;
}

/* Cylinder block */
.cylinder-block {
	margin-top: 14px;
	padding-top: 14px;
	border-top: 1px dashed rgba(255, 255, 255, 0.1);
}

.checkbox-label {
	display: flex;
	align-items: center;
	gap: 8px;
	font-size: 13px;
	font-weight: 600;
	color: #e6edf3;
	cursor: pointer;
}

.cylinder-inputs {
	display: grid;
	grid-template-columns: 120px 180px 1fr;
	gap: 12px;
	margin-top: 10px;
	background: #161b22;
	padding: 12px;
	border-radius: 6px;
	border: 1px solid rgba(255, 255, 255, 0.08);
}

.cyl-total-val {
	height: 38px;
	display: flex;
	align-items: center;
	font-size: 15px;
	font-weight: 700;
	color: #e6edf3;
}

/* Financial Footer Card */
.finance-footer-card {
	background: #1a1f27;
	border: 1px solid #3a424e;
	border-radius: 8px;
	padding: 16px 20px;
	display: flex;
	justify-content: space-between;
	align-items: flex-end;
}

.fin-summary-rows {
	display: flex;
	flex-direction: column;
	gap: 6px;
	min-width: 320px;
}

.fin-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	font-size: 13px;
	color: #8b949e;
}

.fin-val {
	color: #e6edf3;
	font-weight: 600;
}

.total-row {
	border-top: 1px solid rgba(255, 255, 255, 0.1);
	padding-top: 6px;
	margin-top: 4px;
}

.fin-label-lg {
	font-size: 14px;
	font-weight: 700;
	color: #ffffff;
}

.fin-val-lg {
	font-size: 18px;
	font-weight: 800;
	color: #4ea1e0;
}

.deposit-row {
	font-size: 12px;
	color: #f59e0b;
}

.fin-val-deposit {
	font-size: 14px;
	font-weight: 700;
	color: #f59e0b;
}

.form-actions {
	display: flex;
	gap: 12px;
}

.btn-cancel {
	background: #21262d;
	border: 1px solid #3a424e;
	color: #c9d1d9;
	font-size: 14px;
	font-weight: 600;
	padding: 10px 20px;
	border-radius: 6px;
	cursor: pointer;
	transition: all 0.15s ease;
}

.btn-cancel:hover {
	background: #30363d;
	color: #ffffff;
}

.btn-submit {
	background: #0284c7;
	border: none;
	color: #ffffff;
	font-size: 14px;
	font-weight: 700;
	padding: 10px 24px;
	border-radius: 6px;
	cursor: pointer;
	box-shadow: 0 2px 8px rgba(2, 132, 199, 0.4);
	transition: all 0.15s ease;
}

.btn-submit:hover {
	background: #0369a1;
}

/* Utilities */
.text-num {
	font-variant-numeric: tabular-nums;
	font-feature-settings: 'tnum';
}
.text-right {
	text-align: right;
}
.text-center {
	text-align: center;
}
.font-mono {
	font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}
.text-cyan {
	color: #38bdf8;
}
.text-purple {
	color: #c084fc;
}
.text-emerald {
	color: #34d399;
}
</style>
