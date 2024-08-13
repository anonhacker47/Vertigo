export interface ApiResponse<T> {
    data: T;
    pagination: Pagination; 
}

export interface Pagination {
    count: number;
    limit: number;
    offset: number;
    total: number;
}

