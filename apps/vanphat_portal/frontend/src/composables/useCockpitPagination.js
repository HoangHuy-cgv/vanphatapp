/**
 * S8c: pagination + keyboard dùng chung 3 views (Orders/Quotes/Catalog).
 * Gộp prev/next/goto/handleKeyDown copy-paste — mỗi view truyền reload riêng.
 */
export function useCockpitPagination({ currentPage, totalPages, isLoading, onReload }) {
	function go(n) {
		n = Number(n) || 1;
		if (n !== currentPage.value && n >= 1 && n <= totalPages.value && !isLoading.value) {
			currentPage.value = n;
			onReload();
		}
	}

	function prevPage() {
		if (currentPage.value > 1 && !isLoading.value) {
			currentPage.value -= 1;
			onReload();
		}
	}

	function nextPage() {
		if (currentPage.value < totalPages.value && !isLoading.value) {
			currentPage.value += 1;
			onReload();
		}
	}

	function handleKeyDown(e) {
		if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target?.tagName)) return;
		if (e.key === '[') {
			prevPage();
		} else if (e.key === ']') {
			nextPage();
		}
	}

	return { prevPage, nextPage, gotoPage: go, handleKeyDown };
}
