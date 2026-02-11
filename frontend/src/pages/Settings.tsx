
import React, { useEffect, useState } from 'react';
import { Shield, Key, Database, RefreshCw, Trash2, CheckCircle } from 'lucide-react';
import { getSettings, updateSettings, getDatabaseStats, clearDatabase, type Settings as SettingsType, type DatabaseStats } from '../services/api';

const Settings: React.FC = () => {
    const [settings, setSettings] = useState<SettingsType | null>(null);
    const [dbStats, setDbStats] = useState<DatabaseStats | null>(null);
    const [apiKey, setApiKey] = useState('');
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState<{ text: string, type: 'success' | 'error' } | null>(null);

    const fetchData = async () => {
        try {
            const [sData, dData] = await Promise.all([getSettings(), getDatabaseStats()]);
            setSettings(sData);
            setDbStats(dData);
            setApiKey(sData.google_api_key);
        } catch (error) {
            console.error("Failed to fetch settings:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleSaveAPI = async () => {
        setSaving(true);
        setMessage(null);
        try {
            await updateSettings({ google_api_key: apiKey });
            setMessage({ text: 'API Key updated successfully!', type: 'success' });
            fetchData();
        } catch (error) {
            setMessage({ text: 'Failed to update API Key.', type: 'error' });
        } finally {
            setSaving(false);
        }
    };

    const handleClearDB = async () => {
        if (!window.confirm("ARE YOU SURE? This will erase all local email archives!")) return;

        try {
            await clearDatabase();
            setMessage({ text: 'Database cleared successfully.', type: 'success' });
            fetchData();
        } catch (error) {
            setMessage({ text: 'Failed to clear database.', type: 'error' });
        }
    };

    if (loading) {
        return <div className="p-8 text-2xl font-bold animate-pulse text-slate-400">Sketching Settings...</div>;
    }

    return (
        <div className="p-8 space-y-8 max-w-4xl mx-auto">
            {/* Header */}
            <div className="border-b-4 border-slate-800 pb-4 border-double mb-8">
                <h1 className="text-4xl font-black text-slate-800 transform -rotate-1">Control Center</h1>
                <p className="text-slate-500 mt-1 text-lg">System tuning & Pencil configuration</p>
            </div>

            {message && (
                <div className={`p-4 border-2 ${message.type === 'success' ? 'bg-green-50 border-green-600 text-green-800' : 'bg-red-50 border-red-600 text-red-800'} font-bold rounded-lg transform rotate-1 transition-all`}>
                    {message.text}
                </div>
            )}

            {/* API Config Card */}
            <div className="pencil-card relative p-6">
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 border-2 border-slate-800 bg-blue-100 rounded-lg">
                        <Key className="w-6 h-6 text-blue-700" />
                    </div>
                    <h2 className="text-2xl font-bold text-slate-800">AI Intelligence</h2>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-black text-slate-700 mb-1 uppercase tracking-wider">Gemini API Key (Google)</label>
                        <div className="flex gap-3">
                            <input
                                type="password"
                                value={apiKey}
                                onChange={(e) => setApiKey(e.target.value)}
                                placeholder="AIzaSy..."
                                className="flex-1 px-4 py-2 border-2 border-slate-800 rounded-lg focus:outline-none focus:ring-4 focus:ring-yellow-200 font-mono"
                            />
                            <button
                                onClick={handleSaveAPI}
                                disabled={saving}
                                className="px-6 py-2 bg-yellow-300 border-2 border-slate-800 font-bold rounded-lg shadow-[4px_4px_0px_rgba(0,0,0,1)] hover:translate-y-[-2px] active:translate-y-[2px] active:shadow-none transition-all disabled:opacity-50"
                            >
                                {saving ? <RefreshCw className="w-5 h-5 animate-spin" /> : "Save"}
                            </button>
                        </div>
                        <p className="mt-2 text-xs text-slate-400 italic font-medium">* This key powers the automated categorization engine.</p>
                    </div>

                    <div className="pt-4 border-t-2 border-slate-100 border-dashed flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Shield className="w-5 h-5 text-slate-400" />
                            <span className="text-sm font-bold text-slate-500">Gmail OAuth Credentials</span>
                        </div>
                        <div className={`flex items-center gap-1 text-sm font-bold ${settings?.has_credentials ? 'text-green-600' : 'text-rose-500'}`}>
                            {settings?.has_credentials ? <CheckCircle className="w-4 h-4" /> : "MISSING"}
                            <span>{settings?.has_credentials ? 'Verified' : 'credentials.json required'}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Database Card */}
            <div className="pencil-card relative p-6 border-slate-400 bg-slate-50">
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-2 border-2 border-slate-800 bg-emerald-100 rounded-lg">
                        <Database className="w-6 h-6 text-emerald-700" />
                    </div>
                    <h2 className="text-2xl font-bold text-slate-800">Local Archive</h2>
                </div>

                <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-white border-2 border-slate-800 p-4 rounded-xl shadow-[4px_4px_0px_rgba(0,0,0,0.05)]">
                        <p className="text-xs font-black text-slate-400 uppercase">Records</p>
                        <p className="text-3xl font-black text-slate-800">{dbStats?.total_records.toLocaleString() || '0'}</p>
                    </div>
                    <div className="bg-white border-2 border-slate-800 p-4 rounded-xl shadow-[4px_4px_0px_rgba(0,0,0,0.05)]">
                        <p className="text-xs font-black text-slate-400 uppercase">File Size</p>
                        <p className="text-3xl font-black text-slate-800">{dbStats?.file_size_mb || '0'} MB</p>
                    </div>
                </div>

                <div className="flex justify-end pt-4 border-t-2 border-slate-200 border-dashed">
                    <button
                        onClick={handleClearDB}
                        className="flex items-center gap-2 px-4 py-2 border-2 border-rose-600 text-rose-600 font-bold rounded-lg hover:bg-rose-50 transition-colors"
                    >
                        <Trash2 className="w-4 h-4" />
                        Wipe Database
                    </button>
                </div>
            </div>

            <div className="text-center">
                <p className="text-xs text-slate-400 font-mono italic">Gmail-AI-Archivist v1.2 • Design by Pencil Engine</p>
            </div>
        </div>
    );
};

export default Settings;
