
import React, { useEffect, useState } from 'react';
import { CheckCircle, Trash2, HardDrive, Inbox, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import StatsCard from '../components/StatsCard';
import { getStats, type Stats } from '../services/api';

const Dashboard: React.FC = () => {
    const [stats, setStats] = useState<Stats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const data = await getStats();
                setStats(data);
            } catch (error) {
                console.error("Failed to fetch stats:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-full space-y-4">
                <div className="text-2xl font-bold animate-pulse text-slate-400">Sketching Interface...</div>
            </div>
        );
    }

    if (!stats) {
        return <div className="text-red-500 p-8 text-xl font-bold border-2 border-red-500 border-dashed rounded-lg m-8 transform rotate-1">⚠ Controller Disconnected! Check Backend.</div>;
    }

    return (
        <div className="p-8 space-y-8 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex justify-between items-end border-b-4 border-slate-800 pb-4 border-double">
                <div>
                    <h1 className="text-5xl font-bold text-slate-800 transform -rotate-1">My Dashboard</h1>
                    <p className="text-slate-500 mt-1 text-xl">Archive Overview (Sketch Mode)</p>
                </div>
                <div className="flex items-center gap-2 px-4 py-1 border-2 border-slate-800 rounded-full bg-green-100">
                    <div className="w-3 h-3 bg-green-500 rounded-full border border-black" />
                    <span className="font-bold text-green-700">ONLINE</span>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatsCard
                    title="Inbox Total"
                    value={stats.total_emails.toLocaleString()}
                    icon={Inbox}
                    color="text-blue-600"
                />
                <StatsCard
                    title="Sorted"
                    value={stats.classified.toLocaleString()}
                    icon={CheckCircle}
                    color="text-emerald-600"
                />
                <StatsCard
                    title="Junk"
                    value={stats.trash_found.toLocaleString()}
                    icon={Trash2}
                    color="text-rose-600"
                />
                <StatsCard
                    title="Avg Size"
                    value={`${stats.avg_size_kb} KB`}
                    icon={HardDrive}
                    color="text-violet-600"
                />
            </div>

            {/* Chart Section */}
            <div className="pencil-card relative min-h-[400px]">
                <div className="absolute top-0 right-0 p-4 transform rotate-2">
                    <span className="bg-yellow-100 px-3 py-1 border-2 border-slate-800 font-bold transform -rotate-3 inline-block shadow-sm">
                        Activity Graph
                    </span>
                </div>

                <div className="flex items-center mb-6 pl-2 pt-2">
                    <Activity className="w-8 h-8 text-slate-700 mr-2" />
                    <h2 className="text-3xl font-bold text-slate-700">Monthly Volume</h2>
                </div>

                <div className="h-80 w-full pr-4">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={stats.chart_data} barSize={60}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" vertical={false} />
                            <XAxis
                                dataKey="month"
                                stroke="#334155"
                                tick={{ fontSize: 14, fontFamily: 'Patrick Hand' }}
                                tickLine={false}
                                axisLine={{ strokeWidth: 2 }}
                                dy={10}
                            />
                            <YAxis
                                stroke="#334155"
                                tick={{ fontSize: 14, fontFamily: 'Patrick Hand' }}
                                tickLine={false}
                                axisLine={{ strokeWidth: 2 }}
                                dx={-10}
                            />
                            <Tooltip
                                cursor={{ fill: '#f1f5f9', opacity: 0.5 }}
                                contentStyle={{
                                    backgroundColor: '#fff',
                                    borderRadius: '255px 15px 225px 15px / 15px 225px 15px 255px',
                                    border: '2px solid #1e293b',
                                    boxShadow: '4px 4px 0px rgba(0,0,0,0.2)',
                                    color: '#334155',
                                    fontFamily: 'Patrick Hand',
                                    fontWeight: 'bold'
                                }}
                            />
                            {/* Pattern for bars to look sketched */}
                            <defs>
                                <pattern id="stripe" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
                                    <rect width="2" height="8" transform="translate(0,0)" fill="currentColor" opacity="0.4"></rect>
                                </pattern>
                            </defs>
                            <Bar
                                dataKey="count"
                                fill="#3b82f6"
                                radius={[4, 4, 0, 0]}
                                shape={(props: any) => {
                                    const { x, y, width, height, fill } = props;
                                    return (
                                        <g>
                                            <rect x={x} y={y} width={width} height={height} fill={fill} stroke="black" strokeWidth="2" rx="2" ry="2" />
                                            <rect x={x} y={y} width={width} height={height} fill="url(#stripe)" className="text-white" />
                                        </g>
                                    );
                                }}
                            />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
