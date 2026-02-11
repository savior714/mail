
import React, { useEffect, useState, useRef } from 'react';
import { RefreshCw, Zap, Play } from 'lucide-react';
import { runPipeline, getLogs, type LogEntry } from '../services/api';

const Pipeline: React.FC = () => {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState('Idle');
    const [targetMonth, setTargetMonth] = useState(() => {
        const d = new Date();
        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
    });
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

    const handleRun = async (action: 'sync' | 'auto' | 'rules' | 'classify' | 'archive') => {
        setLoading(true);
        setStatus('Working...');
        try {
            const params: any = {};
            if (action === 'sync' && targetMonth) {
                const [year, month] = targetMonth.split('-').map(Number);
                const afterDate = new Date(year, month - 1, 1);
                const beforeDate = new Date(year, month, 1);

                params.after = afterDate.toISOString().split('T')[0].replace(/-/g, '/');
                params.before = beforeDate.toISOString().split('T')[0].replace(/-/g, '/');
            }
            await runPipeline(action as any, params);
        } catch {
            setStatus('Messed up :(');
        }
        setTimeout(() => { setLoading(false); setStatus('Idle'); }, 2000);
    };

    return (
        <div className="p-10 h-screen flex flex-col max-w-7xl mx-auto space-y-8 overflow-hidden">
            <div className="flex justify-between items-start">
                <div>
                    <h1 className="text-4xl font-bold text-slate-800 flex items-center gap-2 font-mono uppercase italic tracking-tighter">
                        <Zap className="w-8 h-8 text-yellow-500" fill="currentColor" />
                        Automated Pipeline
                    </h1>
                    <p className="text-slate-500 mt-2 font-bold text-lg bg-yellow-100 inline-block px-2 transform -rotate-1 border border-slate-300">
                        Granular Control Mode / Step-by-Step
                    </p>
                </div>
                <div className="px-5 py-3 border-2 border-slate-800 rounded-lg bg-white shadow-[4px_4px_0px_#000] font-mono font-black text-xl flex flex-col items-center">
                    <span className="text-[10px] text-slate-400 leading-none">SYSTEM_STATUS</span>
                    {status.toUpperCase()}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Step 1: FETCH */}
                <div className="border-2 border-slate-800 p-5 rounded-xl bg-white shadow-[4px_4px_0px_#000] space-y-4">
                    <div className="flex items-center gap-2 mb-2">
                        <span className="bg-slate-800 text-white w-6 h-6 rounded-full flex items-center justify-center font-bold">1</span>
                        <h2 className="text-xl font-black uppercase">Phase 1: Fetch</h2>
                    </div>
                    <div className="space-y-4">
                        <div className="flex flex-col">
                            <label className="text-[10px] font-bold text-slate-400 uppercase">Target Month</label>
                            <input
                                type="month"
                                value={targetMonth}
                                onChange={(e) => setTargetMonth(e.target.value)}
                                className="border-2 border-slate-800 p-2 rounded-lg font-mono text-lg bg-slate-50 focus:bg-white outline-none w-full"
                            />
                        </div>
                    </div>
                    <button
                        disabled={loading}
                        onClick={() => handleRun('sync')}
                        className="w-full bg-blue-300 hover:bg-blue-400 border-2 border-slate-800 p-3 rounded-xl flex items-center justify-center gap-2 font-black uppercase transition-all active:translate-y-1 active:shadow-none shadow-[2px_2px_0px_#000] disabled:opacity-50"
                    >
                        <RefreshCw className={`w-5 h-5 ${loading && status === 'Working...' ? 'animate-spin' : ''}`} />
                        Fetch Mail
                    </button>
                </div>

                {/* Step 2: CLASSIFY */}
                <div className="border-2 border-slate-800 p-5 rounded-xl bg-white shadow-[4px_4px_0px_#000] space-y-4 flex flex-col justify-between">
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <span className="bg-slate-800 text-white w-6 h-6 rounded-full flex items-center justify-center font-bold">2</span>
                            <h2 className="text-xl font-black uppercase">Phase 2: AI</h2>
                        </div>
                        <p className="text-xs text-slate-500 font-medium">Scan local DB for new senders and classify via Gemini Flash.</p>
                    </div>

                    <div className="space-y-2">
                        <button
                            disabled={loading}
                            onClick={() => handleRun('rules')}
                            className="w-full bg-purple-200 hover:bg-purple-300 border-2 border-slate-800 p-3 rounded-xl flex items-center justify-center gap-2 font-black uppercase transition-all active:translate-y-1 active:shadow-none shadow-[2px_2px_0px_#000] disabled:opacity-50"
                        >
                            <Zap className="w-5 h-5" />
                            Learn Rules
                        </button>
                        <button
                            disabled={loading}
                            onClick={() => handleRun('classify')}
                            className="w-full bg-slate-200 hover:bg-slate-300 border-2 border-slate-800 p-3 rounded-xl flex items-center justify-center gap-2 font-black uppercase transition-all active:translate-y-1 active:shadow-none shadow-[2px_2px_0px_#000] disabled:opacity-50 text-xs"
                        >
                            Update DB
                        </button>
                    </div>
                </div>

                {/* Step 3: ARCHIVE */}
                <div className="border-2 border-slate-800 p-5 rounded-xl bg-white shadow-[4px_4px_0px_#000] space-y-4 flex flex-col justify-between">
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <span className="bg-slate-800 text-white w-6 h-6 rounded-full flex items-center justify-center font-bold">3</span>
                            <h2 className="text-xl font-black uppercase">Phase 3: Apply</h2>
                        </div>
                        <p className="text-xs text-slate-500 font-medium">Push labels to Gmail cloud and archive from Inbox.</p>
                    </div>
                    <button
                        disabled={loading}
                        onClick={() => handleRun('archive')}
                        className="w-full bg-green-200 hover:bg-green-300 border-2 border-slate-800 p-3 rounded-xl flex items-center justify-center gap-2 font-black uppercase transition-all active:translate-y-1 active:shadow-none shadow-[2px_2px_0px_#000] disabled:opacity-50"
                    >
                        <Play className="w-5 h-5" />
                        Run Cloud
                    </button>
                </div>

                {/* THE MACHINE (Full Auto) */}
                <div className="border-2 border-slate-800 p-5 rounded-xl bg-slate-100 shadow-[4px_4px_0px_#000] space-y-4 border-dashed relative overflow-hidden">
                    <div className="absolute -top-4 -right-4 bg-red-500 text-white px-8 py-1 rotate-45 text-[10px] font-black">LEGACY</div>
                    <div>
                        <h2 className="text-xl font-black uppercase text-slate-400">Shortcut</h2>
                        <p className="text-[10px] text-slate-400 italic">Sequential One-Click</p>
                    </div>
                    <button
                        disabled={loading}
                        onClick={() => handleRun('auto')}
                        className="w-full h-full max-h-[80px] bg-red-100 grayscale hover:grayscale-0 border-2 border-slate-200 p-3 rounded-xl flex items-center justify-center gap-2 font-black uppercase transition-all active:translate-y-1 active:shadow-none shadow-[2px_2px_0px_#ccc] disabled:opacity-50"
                    >
                        Full Auto
                    </button>
                </div>
            </div>

            {/* Sketchy Terminal */}
            <div className="flex-1 bg-[#1a1a1a] p-4 rounded-sm border-2 border-slate-800 shadow-[6px_6px_0px_rgba(0,0,0,0.2)] flex flex-col font-mono text-sm relative overflow-hidden"
                style={{ borderRadius: '4px' }}>

                <div className="flex gap-2 mb-4 pb-2 border-b border-gray-700">
                    <div className="w-3 h-3 rounded-full bg-red-400"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                    <div className="w-3 h-3 rounded-full bg-green-400"></div>
                    <span className="ml-auto text-gray-500 text-xs">PIPELINE_STREAMS.LOG</span>
                </div>

                <div className="flex-1 overflow-y-auto space-y-1 text-green-400">
                    {logs.length === 0 && (
                        <div className="text-gray-600 italic">
                            &gt; System ready for discrete commands...<br />
                            &gt; Select Phase 1-3 to begin.<span className="animate-pulse">_</span>
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
