
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

export const runPipeline = async (action: 'sync' | 'auto' | 'rules', year?: number): Promise<void> => {
    await api.post('/pipeline', { action, year });
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
