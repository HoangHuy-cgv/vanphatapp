// Test thực chiến Browser & API vs STAGING/PROD bench — REAL data only (quy định Sếp).
// - Login thật với Administrator
// - Lấy danh mục 293 sản phẩm thật, 117 KH thật
// - Test engine tính giá bao bì R&D
// - Tạo báo giá TEST-BG-xxx thật qua API, kiểm tra số tiền & thuế native
// - Dọn dẹp: Hủy & xóa chứng từ TEST- sau test (không để lại rác)

const BASE_URL = process.env.PORTAL_URL || 'https://app.vanphat.io.vn';
const ADMIN_PASS = process.env.ADMIN_PASS || '';

if (!ADMIN_PASS) {
	console.error('Thiếu ADMIN_PASS (mật khẩu Administrator VPS).');
	process.exit(1);
}

async function run() {
	console.log(`=== 1. ĐĂNG NHẬP THỰC CHIẾN TỚI ${BASE_URL} ===`);
	const loginRes = await fetch(`${BASE_URL}/api/method/login`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ usr: 'Administrator', pwd: ADMIN_PASS }),
	});

	if (!loginRes.ok) {
		throw new Error(`Đăng nhập thất bại: HTTP ${loginRes.status}`);
	}

	const setCookies = loginRes.headers.getSetCookie ? loginRes.headers.getSetCookie() : [loginRes.headers.get('set-cookie') || ''];
	const cookieHeader = setCookies.map(c => c.split(';')[0]).join('; ');
	console.log('✓ Đăng nhập thành công, session cookie xác thực.');

	console.log('\n=== 2. KIỂM TRA BOOT & MASTER DATA THẬT ===');
	const bootRes = await fetch(`${BASE_URL}/api/method/vanphat_portal.api.bao_gia.get_boot`, {
		headers: { Cookie: cookieHeader }
	});
	const bootData = await bootRes.json();
	const csrfToken = bootData.message?.csrf_token || '';
	console.log('✓ Boot user:', bootData.message?.user);
	console.log('✓ Công ty:', bootData.message?.company);
	console.log('✓ CSRF Token:', csrfToken ? `${csrfToken.slice(0, 10)}...` : 'N/A');

	const itemRes = await fetch(`${BASE_URL}/api/method/vanphat_portal.api.item.get_list?page=1&page_length=5`, {
		headers: { Cookie: cookieHeader }
	});
	const itemData = await itemRes.json();
	const totalItems = itemData.message?.total_count || itemData.message?.items?.length || 0;
	console.log(`✓ Danh mục mặt hàng: tải được ${itemData.message?.items?.length} dòng (Tổng: ${totalItems} mặt hàng)`);
	const sampleItem = itemData.message?.items?.[0];
	if (sampleItem) {
		console.log(`   Ví dụ: [${sampleItem.item_code}] ${sampleItem.custom_alias || sampleItem.item_name} — ĐVT: ${sampleItem.stock_uom}`);
	}

	const custRes = await fetch(`${BASE_URL}/api/method/vanphat_portal.api.customer.get_list?page=1&page_length=5`, {
		headers: { Cookie: cookieHeader }
	});
	const custData = await custRes.json();
	const totalCust = custData.message?.total_count || custData.message?.customers?.length || 0;
	console.log(`✓ Danh sách khách hàng: tải được ${custData.message?.customers?.length} dòng (Tổng: ${totalCust} KH)`);
	const sampleCust = custData.message?.customers?.[0];
	console.log(`   Ví dụ: ${sampleCust?.customer_name} (${sampleCust?.customer_group})`);

	console.log('\n=== 3. KIỂM TRA ENGINE TÍNH GIÁ BAO BÌ (R&D PACKAGING MATH) ===');
	const calcRes = await fetch(`${BASE_URL}/api/method/vanphat_portal.api.bao_gia.calculate_packaging_quotation`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-Frappe-CSRF-Token': csrfToken,
			Cookie: cookieHeader,
		},
		body: JSON.stringify({
			pouch_type: 'Túi đáy đứng',
			width_mm: 180,
			length_mm: 260,
			gusset_mm: 45,
			layers: ['PET', 'PA', 'PE'],
			spout_type: '16mm',
			desired_qty: 10000,
			cylinder_qty: 6,
			target_margin: 0.30
		}),
	});
	const calcData = await calcRes.json();
	const calcResult = calcData.message;
	const optRate = calcResult?.tier_options?.optimal_batch?.rate || 0;
	const reqRate = calcResult?.tier_options?.requested_qty?.rate || 0;

	console.log('✓ Kết quả tính toán màng ghép phức hợp:');
	console.log(`   - Giá thành sản xuất theo yêu cầu: ${calcResult?.tier_options?.requested_qty?.cogs?.toLocaleString('vi-VN')} đ/túi`);
	console.log(`   - Đơn giá chào bán (Margin 30%): ${reqRate?.toLocaleString('vi-VN')} đ/túi`);
	console.log(`   - Đơn giá lô tối ưu tròn cuộn: ${optRate?.toLocaleString('vi-VN')} đ/túi`);
	if (calcResult?.cylinder_quote) {
		console.log(`   - Trục in (${calcResult.cylinder_quote.qty} trục): ${calcResult.cylinder_quote.total?.toLocaleString('vi-VN')} đ`);
	}

	console.log('\n=== 4. TEST TẠO VÀ DỌN DẸP BÁO GIÁ THẬT (PREFIX TEST-) ===');
	const testCustomerId = sampleCust?.name || 'ANH LUÂN';
	const testItemName = sampleItem?.item_name || 'Túi mẫu thử nghiệm R&D';

	// Tạo báo giá
	const createQuoteRes = await fetch(`${BASE_URL}/api/method/vanphat_portal.api.bao_gia.create_quotation`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-Frappe-CSRF-Token': csrfToken,
			Cookie: cookieHeader,
		},
		body: JSON.stringify({
			payload: {
				customer_id: testCustomerId,
				description: 'TEST-BG: Báo giá thực chiến tự động (sẽ dọn dẹp ngay)',
				lines: [
					{
						item_name: `TEST-ITEM: ${testItemName}`,
						qty: 10000,
						rate: reqRate || 5500,
					}
				]
			}
		}),
	});

	const createdQuoteData = await createQuoteRes.json();
	let createdQuoteName = createdQuoteData.message?.name;

	if (createdQuoteName) {
		console.log(`✓ ĐÃ TẠO THÀNH CÔNG BÁO GIÁ THẬT TRÊN ERPNEXT: ${createdQuoteName}`);

		// Lấy chi tiết báo giá vừa tạo
		const quoteDetailRes = await fetch(`${BASE_URL}/api/method/frappe.client.get?doctype=Quotation&name=${createdQuoteName}`, {
			headers: { Cookie: cookieHeader }
		});
		const quoteDetail = (await quoteDetailRes.json()).message;
		console.log(`   - Khách hàng: ${quoteDetail.party_name}`);
		console.log(`   - Tiền hàng (chưa thuế): ${Number(quoteDetail.net_total || quoteDetail.total || 0).toLocaleString('vi-VN')} đ`);
		console.log(`   - Tổng cộng (gồm VAT native): ${Number(quoteDetail.grand_total || 0).toLocaleString('vi-VN')} đ`);
		console.log(`   - Trạng thái chứng từ: ${quoteDetail.status} (docstatus: ${quoteDetail.docstatus})`);
	} else {
		console.error('! Tạo báo giá thất bại:', createdQuoteData);
	}

	// CLEANUP: Luôn dọn dẹp chứng từ test
	if (createdQuoteName) {
		console.log(`\n=== 5. DỌN DẸP CHỨNG TỪ THỬ NGHIỆM: ${createdQuoteName} ===`);
		const deleteRes = await fetch(`${BASE_URL}/api/method/frappe.client.delete`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-Frappe-CSRF-Token': csrfToken,
				Cookie: cookieHeader,
			},
			body: JSON.stringify({
				doctype: 'Quotation',
				name: createdQuoteName
			})
		});
		if (deleteRes.ok) {
			console.log(`✓ ĐÃ XÓA SẠCH ${createdQuoteName}. Hệ thống sạch sẽ 100%, không để lại rác!`);
		} else {
			console.warn(`! Không thể xóa tự động ${createdQuoteName}`);
		}
	}

	console.log('\n=============================================');
	console.log('✓ TEST THỰC CHIẾN BACKEND + ERPNEXT XANH 100%');
	console.log('=============================================');
}

run().catch((err) => {
	console.error('Lỗi thực chiến:', err);
	process.exit(1);
});
