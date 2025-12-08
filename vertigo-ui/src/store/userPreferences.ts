import { defineStore } from "pinia";

interface UserPreferencesState {
    viewMode: string;
    orderDir: string;
    orderBy: string;
    cardsPerLine: number;
}

export const useUserPreferences = defineStore("userPreferences", {
    state: (): UserPreferencesState => ({
        viewMode: localStorage.getItem('viewMode') || 'card',
        cardsPerLine: Number(localStorage.getItem('cardsPerLine')) || 4,
        orderDir: localStorage.getItem('orderDir') || 'desc',
        orderBy: localStorage.getItem('orderBy') || 'timestamp',
    }),

    actions: {
        setViewMode(viewMode: 'card' | 'list') {
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
            this.setViewMode(localStorage.getItem('viewMode') || 'card');
            this.setorderDir(localStorage.getItem('orderDir') || 'desc');
            this.setorderBy(localStorage.getItem('orderBy') || 'timestamp');
            this.setCardsPerLine(Number(localStorage.getItem('cardsPerLine')) || 6);
        }
    }
});

