import { defineStore } from "pinia";

export type ViewMode = "card" | "list";

interface UserPreferencesState {
    viewMode: ViewMode;
    orderDir: string;
    orderBy: string;
    cardsPerLine: number;
}

function storedViewMode(): ViewMode {
    return localStorage.getItem('viewMode') === 'list' ? 'list' : 'card';
}

function storedOrderDir(): 'asc' | 'desc' {
    return localStorage.getItem('orderDir') === 'asc' ? 'asc' : 'desc';
}

export const useUserPreferences = defineStore("userPreferences", {
    state: (): UserPreferencesState => ({
        viewMode: storedViewMode(),
        cardsPerLine: Number(localStorage.getItem('cardsPerLine')) || 4,
        orderDir: storedOrderDir(),
        orderBy: localStorage.getItem('orderBy') || 'timestamp',
    }),

    actions: {
        setViewMode(viewMode: ViewMode) {
            if (this.viewMode === viewMode) return;
            this.viewMode = viewMode;
            localStorage.setItem('viewMode', viewMode);
        },
        setorderDir(orderDir: 'asc' | 'desc') {
            this.orderDir = orderDir;
            localStorage.setItem('orderDir', orderDir);
        },
        setorderBy(orderBy: string) {
            this.orderBy = orderBy;
            localStorage.setItem('orderBy', orderBy);
        },
        setCardsPerLine(cardsPerLine: number) { 
            this.cardsPerLine = cardsPerLine;
            localStorage.setItem('cardsPerLine', cardsPerLine.toString());
        },
        loadPreferences() {
            this.setViewMode(storedViewMode());
            this.setorderDir(storedOrderDir());
            this.setorderBy(localStorage.getItem('orderBy') || 'timestamp');
            this.setCardsPerLine(Number(localStorage.getItem('cardsPerLine')) || 6);
        }
    }
});
