
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});
export interface Stats {
    total_emails: number;
    classified: number;
    trash_found: number;
    avg_size_kb: number;
    chart_data: { month: string; count: number }[];
}

export interface Settings {
    google_api_key: string;
    has_credentials: boolean;
}

export interface DatabaseStats {
    file_size_mb: number;
    total_records: number;
}

export interface Rule {
    sender: string;
    category: string;
    keywords?: string;
}

export const getStats = async (): Promise<Stats> => {
    const response = await api.get('/stats');
    return response.data;
};

export const getRules = async (): Promise<Rule[]> => {
    const response = await api.get('/rules');
    return response.data;
};

export const addRule = async (rule: Rule): Promise<void> => {
    await api.post('/rules', rule);
};

export const deleteRule = async (sender: string): Promise<void> => {
    await api.delete(`/rules/${sender}`);
};

export type PipelineActionType = 'sync' | 'auto' | 'rules' | 'classify' | 'archive';

export const runPipeline = async (
    action: PipelineActionType,
    params?: { year?: number; after?: string; before?: string }
): Promise<void> => {
    await api.post('/pipeline', { action, ...params });
};

export interface LogEntry {
    timestamp: string;
    level: string;
    message: string;
}

export const getLogs = async (): Promise<LogEntry[]> => {
    const response = await api.get('/logs');
    return response.data;
};

export const getSettings = async (): Promise<Settings> => {
    const response = await api.get('/settings');
    return response.data;
};

export const updateSettings = async (settings: Partial<Settings>): Promise<void> => {
    await api.post('/settings', settings);
};

export const getDatabaseStats = async (): Promise<DatabaseStats> => {
    const response = await api.get('/database/stats');
    return response.data;
};

export const clearDatabase = async (): Promise<void> => {
    await api.post('/database/clear');
};
