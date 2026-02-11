
import React from 'react';
import { Shield, Key, Database } from 'lucide-react';

const Settings: React.FC = () => {
    return (
        <div className="p-8 space-y-6">
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-white">Settings</h1>
                <p className="text-gray-400 mt-1">Configuration and system preferences.</p>
            </div>

            <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden divide-y divide-gray-700">
                <div className="p-6 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="bg-blue-900/50 p-3 rounded-lg text-blue-400">
                            <Key className="w-6 h-6" />
                        </div>
                        <div>
                            <h3 className="text-lg font-medium text-white">API Configuration</h3>
                            <p className="text-gray-400 text-sm">Manage connection to Google Gmail API.</p>
                        </div>
                    </div>
                    <button className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition">
                        Configure
                    </button>
                </div>

                <div className="p-6 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="bg-green-900/50 p-3 rounded-lg text-green-400">
                            <Database className="w-6 h-6" />
                        </div>
                        <div>
                            <h3 className="text-lg font-medium text-white">Database</h3>
                            <p className="text-gray-400 text-sm">Manage local SQLite archives.</p>
                        </div>
                    </div>
                    <button className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition">
                        Backup Now
                    </button>
                </div>

                <div className="p-6 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="bg-purple-900/50 p-3 rounded-lg text-purple-400">
                            <Shield className="w-6 h-6" />
                        </div>
                        <div>
                            <h3 className="text-lg font-medium text-white">Safe Mode</h3>
                            <p className="text-gray-400 text-sm">Require confirmation before bulk actions.</p>
                        </div>
                    </div>
                    <div className="relative inline-block w-12 mr-2 align-middle select-none transition duration-200 ease-in">
                        <input type="checkbox" name="toggle" id="toggle" className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer" defaultChecked />
                        <label htmlFor="toggle" className="toggle-label block overflow-hidden h-6 rounded-full bg-green-500 cursor-pointer"></label>
                    </div>
                </div>
            </div>

            <div className="mt-8 p-4 bg-yellow-900/20 border border-yellow-700/50 rounded-lg text-yellow-200 text-sm">
                <strong>Note:</strong> Most configuration is currently handled via <code>.env</code> file. Restart the backend after changes.
            </div>
        </div>
    );
};

export default Settings;
