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
								<label class="field-label-sm">NCC trục</label>
								<input type="text" v-model="cylinderSupplier" class="text-input" placeholder="VD: Kiến Tâm" />
							</div>
							<div class="cyl-col">
								<label class="field-label-sm">Giá NCC (VNĐ/cây)</label>
								<input type="number" v-model.number="cylinderUnitPrice" class="text-input text-right text-num" min="0" step="100000" placeholder="Giá NCC báo" />
							</div>
							<div class="cyl-col">
								<label class="field-label-sm">Tiền trục</label>
								<div v-if="serverPricing.cylinder_pending" class="cyl-total-val text-num text-amber">Chờ giá NCC</div>
								<div v-else class="cyl-total-val text-num">{{ formatCurrency(serverPricing.cylinder_total) }}</div>
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
							placeholder="VD: CÀ PHÊ NGUYÊN CHẤT DAKLAK"
						/>
					</div>

					<!-- Danh sách biến thể MTS -->
					<div class="table-container">
						<table class="data-table">
							<thead>
								<tr>
									<th>Mặt hàng</th>
									<th class="text-right">Số lượng (cái)</th>
									<th class="text-right">Đơn giá (đ)</th>
									<th class="text-right">Thành tiền</th>
									<th style="width: 48px;"></th>
								</tr>
							</thead>
							<tbody>
								<tr v-for="(row, idx) in genericRows" :key="idx">
									<td>
										<select v-model="row.item_code" class="select-input select-table" @change="onGenericItemChange(row)">
											<option v-for="item in availableGenericItems" :key="item.item_code" :value="item.item_code">
												{{ item.item_name }} ({{ item.item_code }})
											</option>
										</select>
									</td>
									<td class="text-right">
										<input
											type="number"
											v-model.number="row.qty"
											class="text-input text-right text-num"
											min="1"
										/>
									</td>
									<td class="text-right">
										<input
											type="number"
											v-model.number="row.rate"
											class="text-input text-right text-num"
											min="0"
											step="100"
										/>
									</td>
									<td class="text-right text-num bold-num">
										{{ formatCurrency((row.qty || 0) * (row.rate || 0)) }}
									</td>
									<td class="text-center">
										<button
											type="button"
											class="btn-icon-del"
											@click="removeGenericRow(idx)"
											:disabled="genericRows.length <= 1"
										>
											×
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
							<span class="fin-val text-num">{{ formatCurrency(serverPricing.net_total) }}</span>
						</div>
						<div class="fin-row">
							<span class="fin-label">Thuế VAT ({{ serverPricing.vat_rate }}%):</span>
							<span class="fin-val text-num">{{ formatCurrency(serverPricing.vat_amount) }}</span>
						</div>
						<div v-if="serverPricing.cylinder_pending" class="fin-row">
							<span class="fin-label">Tiền trục:</span>
							<span class="fin-val text-num text-amber">Chờ giá NCC</span>
						</div>
						<div v-else-if="serverPricing.cylinder_total > 0" class="fin-row">
							<span class="fin-label">Tiền trục:</span>
							<span class="fin-val text-num">{{ formatCurrency(serverPricing.cylinder_total) }}</span>
						</div>
						<div class="fin-row total-row">
							<span class="fin-label-lg">TỔNG THANH TOÁN:</span>
							<span v-if="serverPricing.cylinder_pending" class="fin-val-lg text-num text-amber">Chưa chốt (chờ trục)</span>
							<span v-else class="fin-val-lg text-num">{{ formatCurrency(serverPricing.grand_total) }}</span>
						</div>
						<div v-if="paymentType === 'Trả trước'" class="fin-row deposit-row">
							<span class="fin-label">Cọc yêu cầu:</span>
							<span v-if="serverPricing.cylinder_pending" class="fin-val-deposit text-num text-amber">Chờ giá NCC</span>
							<span v-else class="fin-val-deposit text-num">{{ formatCurrency(serverPricing.required_deposit) }}</span>
						</div>
					</div>

					<div class="form-actions">
						<button type="button" class="btn-cancel" @click="$emit('close')" :disabled="isSubmitting">
							Hủy
						</button>
						<button
							type="submit"
							class="btn-submit"
							:disabled="isSubmitting || isCalculatingPrice"
							:class="{ 'opacity-60 cursor-not-allowed': isSubmitting || isCalculatingPrice }"
						>
							<span v-if="isSubmitting">ĐANG TẠO ĐƠN...</span>
							<span v-else-if="isCalculatingPrice">ĐANG ĐỐI SOÁT GIÁ...</span>
							<span v-else>+ TẠO ĐƠN HÀNG</span>
						</button>
					</div>
				</div>
			</form>
		</div>
		</div>
	</Teleport>
</template>

<script setup>
import { watch, toRef } from 'vue';
import { api } from '../composables/useSession';
import { toast } from '../composables/useToast';
import { useCreateOrderForm } from '../composables/useCreateOrderForm';
import { useCockpitFormat } from '../composables/useCockpitFormat';

const props = defineProps({
	isOpen: { type: Boolean, default: false },
	initialTab: { type: String, default: 'xuong_sx' },
	masterItems: { type: Array, default: () => [] },
});

// S7: emit contract khớp caller OrdersView (@order-created) — sửa bug khai báo thiếu
const emit = defineEmits(['close', 'order-created']);

const form = useCreateOrderForm(toRef(props, 'masterItems'));
const {
	customers,
	isSubmitting,
	fetchCustomers,
	catalogItems,
	serverPricing,
	isCalculatingPrice,
	selectedCustomerId,
	brand,
	productGroup,
	deliveryDate,
	paymentType,
	selectedCustomItemCode,
	variantRows,
	hasNewCylinders,
	cylinderCount,
	cylinderSupplier,
	cylinderUnitPrice,
	screenPrintBrand,
	genericRows,
	currentCustomer,
	isCustomMto,
	groupTabLabel,
	availableCustomItems,
	currentCustomItem,
	availableGenericItems,
	onCustomerChange,
	onProductGroupChange,
	onCustomItemChange,
	onGenericItemChange,
	addVariantRow,
	removeVariantRow,
	addGenericRow,
	removeGenericRow,
	resetForOpen,
} = form;

// S7c: formatter dùng chung (xóa bản copy-paste)
const { formatCurrency } = useCockpitFormat();

// Default setup when modal opens
watch(
	() => props.isOpen,
	async (val) => {
		if (val) {
			await fetchCustomers();

			// Set default delivery date (+7 days)
			const d = new Date();
			d.setDate(d.getDate() + 7);
			deliveryDate.value = d.toISOString().split('T')[0];

			resetForOpen(props.initialTab);
		}
	},
	{ immediate: true }
);

// Submit order to ERPNext native Sales Order
const handleSubmit = async () => {
	if (!currentCustomer.value || isSubmitting.value) return;
	if (isCalculatingPrice.value) {
		toast.warning('Đang đối soát giá từ ERPNext, vui lòng chờ trong giây lát...');
		return;
	}

	let orderTab = 'xuong_sx';
	if (productGroup.value === 'Túi NGCS') orderTab = 'ngcs';
	else if (productGroup.value === 'Túi màng đơn') orderTab = 'mua_ngoai';

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
			// P2 pass-through: dòng trục do backend cộng từ cylinder_spec (giá NCC).
			// Vỏ không tự build dòng trục nữa — chỉ gửi spec, backend quyết.
			cylinderStatusText = `${cylinderCount.value} cây (NCC ${cylinderSupplier.value || 'chờ báo giá'})`;
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

	const orderPayload = {
		customer: currentCustomer.value.id,
		customer_name: currentCustomer.value.name,
		brand: brand.value,
		delivery_date: deliveryDate.value,
		payment_type: paymentType.value,
		order_tab: orderTab,
		product_group: productGroup.value,
		has_new_cylinders: hasNewCylinders.value,
		cylinder_count: cylinderCount.value,
		// P2: giá trục NCC quyết — Vạn Phát chỉ mua đi bán lại, không chốt số nào
		cylinder_spec: hasNewCylinders.value ? {
			qty: cylinderCount.value,
			unit_price: cylinderUnitPrice.value,
			supplier: cylinderSupplier.value,
		} : null,
		items: builtItems,
	};

	isSubmitting.value = true;
	try {
		const res = await api('order.create_sales_order', { payload: orderPayload });
		if (res && res.name) {
			toast.success(`Đã tạo đơn hàng ${res.name} thành công!`);
			emit('order-created', {
				name: res.name,
				order_tab: orderTab,
				...orderPayload,
			});
			emit('close');
		} else {
			toast.error('Không thể tạo đơn hàng trên hệ thống.');
		}
	} catch (err) {
		console.error('Error creating sales order:', err);
		toast.error('Lỗi kết nối khi tạo đơn hàng.');
	} finally {
		isSubmitting.value = false;
	}
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
	font-family: inherit;
	font-variant-numeric: tabular-nums;
	font-feature-settings: "tnum";
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
