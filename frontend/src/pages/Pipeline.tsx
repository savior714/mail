
import React, { useEffect, useState, useRef } from 'react';
import { RefreshCw, Smartphone, Zap, Play } from 'lucide-react';
import { runPipeline, getLogs, type LogEntry } from '../services/api';

const Pipeline: React.FC = () => {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState('Idle');
    const logsEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const interval = setInterval(async () => {
            const newLogs = await getLogs();
            if (newLogs.length > 0) setLogs(prev => [...prev, ...newLogs].slice(-1000));
        }, 1000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    const handleRun = async (action: 'sync' | 'auto' | 'rules') => {
        setLoading(true);
        setStatus('Working...');
        try {
            await runPipeline(action);
        } catch {
            setStatus('Messed up :(');
        }
        setTimeout(() => { setLoading(false); setStatus('Idle'); }, 2000);
    };

    return (
        <div className="p-10 h-screen flex flex-col max-w-7xl mx-auto space-y-8">
            <div className="flex justify-between items-start">
                <div>
                    <h1 className="text-4xl font-bold text-slate-800 flex items-center gap-2">
                        <div className="p-2 border-2 border-slate-800 bg-slate-200 rounded-lg">
                            <Zap className="w-6 h-6 text-slate-800" fill="currentColor" />
                        </div>
                        The Machine
                    </h1>
                    <p className="text-slate-500 mt-2 font-bold text-lg bg-yellow-100 inline-block px-2 transform rotate-1 border border-slate-300">
                        Danger Zone: Automated Processes
                    </p>
                </div>
                <div className="px-4 py-2 border-2 border-slate-800 rounded-lg bg-white shadow-[2px_2px_0px_#000] font-mono font-bold">
                    STATUS: {status.toUpperCase()}
                </div>
            </div>

            {/* Big Buttons */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {[
                    { id: 'sync', label: 'Sync Emails', sub: 'Fetch from Gmail', icon: RefreshCw, color: 'bg-blue-300' },
                    { id: 'auto', label: 'Full Auto', sub: 'Sync + Sort + Archive', icon: Smartphone, color: 'bg-green-300' },
                    { id: 'rules', label: 'Gen Rules', sub: 'Learn from History', icon: Play, color: 'bg-purple-300' },
                ].map((btn) => (
                    <button
                        key={btn.id}
                        onClick={() => handleRun(btn.id as any)}
                        disabled={loading}
                        className={`group relative border-2 border-slate-800 p-6 rounded-xl text-left transition-all hover:-translate-y-1 hover:shadow-[4px_4px_0px_#000] active:translate-y-0 active:shadow-none disabled:opacity-50 disabled:transform-none bg-white`}
                    >
                        <div className={`absolute top-0 right-0 p-3 border-l-2 border-b-2 border-slate-800 rounded-bl-xl ${btn.color}`}>
                            <btn.icon className={`w-6 h-6 text-slate-900 ${loading && status === 'Working...' ? 'animate-spin' : ''}`} />
                        </div>
                        <h3 className="text-2xl font-bold text-slate-800 group-hover:underline decoration-wavy decoration-2">{btn.label}</h3>
                        <p className="text-slate-500 font-medium mt-1">{btn.sub}</p>
                    </button>
                ))}
            </div>

            {/* Sketchy Terminal */}
            <div className="flex-1 bg-[#1a1a1a] p-4 rounded-sm border-2 border-slate-800 shadow-[6px_6px_0px_rgba(0,0,0,0.2)] flex flex-col font-mono text-sm relative"
                style={{ borderRadius: '4px' }}>

                {/* Terminal Header */}
                <div className="flex gap-2 mb-4 pb-2 border-b border-gray-700">
                    <div className="w-3 h-3 rounded-full bg-red-400"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                    <div className="w-3 h-3 rounded-full bg-green-400"></div>
                    <span className="ml-auto text-gray-500 text-xs">console_output.log</span>
                </div>

                <div className="flex-1 overflow-y-auto space-y-1 text-green-400">
                    {logs.length === 0 && (
                        <div className="text-gray-600 italic">
                            &gt; System ready...<br />
                            &gt; Waiting for command...<span className="animate-pulse">_</span>
                        </div>
                    )}
                    {logs.map((log, i) => (
                        <div key={i} className="break-all font-bold">
                            <span className="text-gray-500 mr-2">[{log.timestamp.split('T')[1].split('.')[0]}]</span>
                            <span className={`${log.level === 'ERROR' ? 'text-red-400 bg-red-900/20 px-1' :
                                log.level === 'WARNING' ? 'text-yellow-400' :
                                    'text-green-400'
                                }`}>
                                &gt; {log.message}
                            </span>
                        </div>
                    ))}
                    <div ref={logsEndRef} />
                </div>
            </div>
        </div>
    );
};

export default Pipeline;
