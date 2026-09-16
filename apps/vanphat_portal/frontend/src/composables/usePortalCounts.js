import { ref } from 'vue';

const quotesCount = ref(0);
const ordersCount = ref(0);
const catalogCount = ref(0);

export function usePortalCounts() {
	return {
		quotesCount,
		ordersCount,
		catalogCount,
	};
}
