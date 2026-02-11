
import { type LucideIcon } from 'lucide-react';

interface StatsCardProps {
    title: string;
    value: string | number;
    icon: LucideIcon;
    color: string; // Expecting tailwind text classes like 'text-blue-500'
    trend?: string;
}

const StatsCard: React.FC<StatsCardProps> = ({ title, value, icon: Icon, color, trend }) => {
    // Map color class to specific border/scribble colors if needed
    // For now relying on text color

    return (
        <div className="pencil-card group relative overflow-hidden">
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-slate-500 text-lg font-bold leading-none mb-2">{title}</p>
                    <h3 className={`text-4xl font-bold ${color} drop-shadow-sm`}>{value}</h3>
                </div>

                <div className={`transform group-hover:rotate-12 transition-transform duration-300 ${color}`}>
                    <Icon strokeWidth={2.5} size={32} />
                </div>
            </div>

            {trend && (
                <div className="mt-3 text-sm font-semibold text-slate-400 border-t-2 border-dashed border-slate-200 pt-2">
                    {trend}
                </div>
            )}

            {/* Scribble decoration */}
            <div className="absolute -bottom-4 -right-4 opacity-10 pointer-events-none">
                <Icon size={80} strokeWidth={1} />
            </div>
        </div>
    );
};

export default StatsCard;
