
import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, ScrollText, PlayCircle, Settings, Mail } from 'lucide-react';

const Sidebar: React.FC = () => {
    const menuItems = [
        { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { path: '/rules', label: 'Rules', icon: ScrollText },
        { path: '/pipeline', label: 'Pipeline', icon: PlayCircle },
        { path: '/settings', label: 'Settings', icon: Settings },
    ];

    return (
        <div className="w-64 h-full bg-slate-50 border-r-2 border-slate-800 flex flex-col z-50 shrink-0">
            <div className="p-8">
                <div className="flex items-center space-x-3 mb-6 transform -rotate-2">
                    <div className="p-2 border-2 border-slate-800 bg-blue-500 rounded-lg shadow-[2px_2px_0px_rgba(0,0,0,1)]">
                        <Mail className="w-6 h-6 text-white" strokeWidth={3} />
                    </div>
                    <div>
                        <h1 className="text-2xl font-black text-slate-800 tracking-tight leading-none">MAIL<br />ARCHIVIST</h1>
                    </div>
                </div>
                <div className="w-full h-0.5 bg-slate-800 rounded-full mb-2"></div>
            </div>

            <nav className="flex-1 px-4 space-y-4">
                {menuItems.map((item) => {
                    const Icon = item.icon;

                    return (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) => `
                w-full flex items-center space-x-3 px-4 py-3 text-lg font-bold transition-all duration-200 border-2 
                ${isActive
                                    ? 'bg-yellow-300 text-slate-900 border-slate-900 shadow-[4px_4px_0px_rgba(0,0,0,1)] transform -translate-y-1 -rotate-1'
                                    : 'bg-transparent text-slate-500 border-transparent hover:border-slate-300 hover:bg-slate-100 hover:text-slate-700'
                                }
              `}
                            style={({ isActive }) => ({
                                borderRadius: isActive ? '255px 15px 225px 15px / 15px 225px 15px 255px' : '10px'
                            })}
                        >
                            {({ isActive }) => (
                                <>
                                    <Icon className={`w-6 h-6 ${isActive ? 'text-slate-900' : 'text-slate-400'}`} strokeWidth={2.5} />
                                    <span>{item.label}</span>
                                </>
                            )}
                        </NavLink>
                    );
                })}
            </nav>

            <div className="p-6 bg-slate-100 border-t-2 border-slate-800">
                <div className="border-2 border-slate-400 border-dashed p-4 rounded-xl bg-white opacity-80">
                    <p className="text-sm font-bold text-slate-500 text-center mb-1">Storage</p>
                    <div className="w-full h-3 border-2 border-slate-800 rounded-full bg-white overflow-hidden">
                        <div className="h-full bg-blue-500 w-[45%] border-r-2 border-slate-800"
                            style={{ backgroundImage: 'linear-gradient(45deg, rgba(255,255,255,.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,.15) 50%, rgba(255,255,255,.15) 75%, transparent 75%, transparent)', backgroundSize: '1rem 1rem' }}>
                        </div>
                    </div>
                    <p className="text-xs text-center mt-2 font-mono text-slate-400">v1.2 (Pencil)</p>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
