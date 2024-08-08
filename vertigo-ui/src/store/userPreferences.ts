import { defineStore } from "pinia";

interface UserPreferencesState {
    viewMode: 'card' | 'list';
    orderdir: 'asc' | 'desc';
    orderby: string;
    cardPerLine: number;
}

export const useUserPreferences = defineStore("userPreferences", {
    state: () => ({
        state:() => ({
            viewMode: 'card',
            cardPerLine: 4,
            orderdir: 'desc',
            orderby: 'name',
        })
    }),

    actions: {
        setViewMode(viewMode: 'card' | 'list') {
            this.viewMode = viewMode;
            localStorage.setItem('viewMode', viewMode);
        },
        setorderdir(orderdir: 'asc' | 'desc') {
            this.orderdir = orderdir;
            localStorage.setItem('orderdir', orderdir);
        },
        setorderby(orderby: string) {
            this.orderby = orderby;
            localStorage.setItem('orderby', orderby);
        },
        setCardsPerLine(cardsPerLine: number) {
            this.cardsPerLine = cardsPerLine;
            localStorage.setItem('cardsPerLine', cardsPerLine.toString());
        },
        loadPreferences() {
            const viewMode = localStorage.getItem('viewMode');
            const orderdir = localStorage.getItem('orderdir');
            const orderby = localStorage.getItem('orderby');
            const cardsPerLine = localStorage.getItem('cardsPerLine');

            if (viewMode) this.viewMode = viewMode as 'card' | 'list';
            if (orderdir) this.orderdir = orderdir as 'asc' | 'desc';
            if (orderby) this.orderby = orderby;
            if (cardsPerLine) this.cardsPerLine = parseInt(cardsPerLine);
        }
    }
});

