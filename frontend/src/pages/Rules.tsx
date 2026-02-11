
import React, { useEffect, useState } from 'react';
import { Plus, Trash2, Search, PenTool } from 'lucide-react';
import { getRules, addRule, deleteRule, type Rule } from '../services/api';

const Rules: React.FC = () => {
    const [rules, setRules] = useState<Rule[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    const [showAddForm, setShowAddForm] = useState(false);
    const [newSender, setNewSender] = useState('');
    const [newCategory, setNewCategory] = useState('💰 Finance');

    const fetchRules = async () => {
        setLoading(true);
        try {
            const data = await getRules();
            setRules(data);
        } catch (error) {
            console.error("Failed to fetch rules:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRules();
    }, []);

    const handleAddRule = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newSender) return;

        try {
            await addRule({ sender: newSender, category: newCategory });
            setNewSender('');
            setShowAddForm(false);
            fetchRules();
        } catch (error) {
            alert("Failed to add rule (maybe duplicate?)");
        }
    };

    const handleDeleteRule = async (sender: string) => {
        if (!confirm(`Scrap rule for ${sender}?`)) return;
        try {
            await deleteRule(sender);
            fetchRules();
        } catch (error) {
            alert("Failed to delete rule");
        }
    };

    const filteredRules = rules.filter(r =>
        r.sender.toLowerCase().includes(searchTerm.toLowerCase()) ||
        r.category.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="p-10 space-y-8 max-w-7xl mx-auto font-sans">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-4xl font-bold text-slate-800 flex items-center gap-3">
                        <PenTool className="w-8 h-8 transform -rotate-45" />
                        Logic Notebook
                    </h1>
                    <p className="text-slate-500 mt-2 font-medium ml-1">My classification rules (Do not touch!)</p>
                </div>
                <button
                    onClick={() => setShowAddForm(!showAddForm)}
                    className="pencil-button flex items-center gap-2 text-lg font-bold bg-yellow-300 hover:bg-yellow-400 text-slate-900"
                >
                    <Plus className="w-5 h-5" />
                    <span>New Rule</span>
                </button>
            </div>

            {/* Add Rule Form (Notebook Note) */}
            {showAddForm && (
                <div className="bg-[#fff9c4] p-6 border-2 border-slate-800 shadow-[4px_4px_0px_rgba(0,0,0,1)] transform rotate-1 relative">
                    <div className="absolute top-0 left-1/2 -mt-3 w-4 h-4 rounded-full bg-slate-800 blur-[1px]"></div>

                    <h3 className="text-xl font-bold text-slate-800 mb-4 scribble-underline decoration-wavy">Drafting New Rule</h3>

                    <form onSubmit={handleAddRule} className="flex gap-4 items-end">
                        <div className="flex-1">
                            <label className="block text-lg font-bold text-slate-700 mb-1">Sender:</label>
                            <input
                                type="email"
                                value={newSender}
                                onChange={(e) => setNewSender(e.target.value)}
                                className="w-full bg-transparent border-b-2 border-slate-800 px-2 py-1 text-xl font-handwriting focus:border-blue-500 outline-none placeholder:text-slate-400/50"
                                placeholder="newsletter@sketchy.com"
                                required
                                autoFocus
                            />
                        </div>
                        <div className="w-1/3">
                            <label className="block text-lg font-bold text-slate-700 mb-1">Category:</label>
                            <select
                                value={newCategory}
                                onChange={(e) => setNewCategory(e.target.value)}
                                className="w-full bg-transparent border-b-2 border-slate-800 px-2 py-1 text-xl font-handwriting focus:border-blue-500 outline-none cursor-pointer"
                            >
                                <option>💰_Finance</option>
                                <option>🛒_Shopping_Checkout</option>
                                <option>🛒_Shopping_Promo</option>
                                <option>💻_Dev_Tech</option>
                                <option>🏥_Medical_Work</option>
                                <option>🚗_Car_Life</option>
                                <option>🏢_Notice_Privacy</option>
                                <option>🏠_Personal_Life</option>
                                <option>🔒_Auth_System</option>
                                <option>🚫_Spam</option>
                            </select>
                        </div>
                        <button type="submit" className="pencil-button bg-green-400 hover:bg-green-500 text-slate-900 font-bold">
                            Pin It
                        </button>
                    </form>
                </div>
            )}

            {/* Search */}
            <div className="relative max-w-md">
                <input
                    type="text"
                    placeholder="Find a rule..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full bg-white border-2 border-slate-800 rounded-full pl-11 pr-4 py-3 text-lg focus:outline-none focus:ring-4 focus:ring-blue-200 transition-all shadow-sm font-bold text-slate-600"
                />
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5 pointer-events-none" />
            </div>

            {/* Notebook Table */}
            <div className="bg-white border-2 border-slate-800 relative py-2" style={{
                backgroundImage: 'linear-gradient(#e2e8f0 1px, transparent 1px)',
                backgroundSize: '100% 3rem'
            }}>
                <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-red-400/50"></div>

                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr>
                            <th className="px-12 py-3 text-slate-400 font-bold text-sm uppercase tracking-widest pl-16">Sender</th>
                            <th className="px-8 py-3 text-slate-400 font-bold text-sm uppercase tracking-widest">Tag</th>
                            <th className="px-8 py-3 text-right"></th>
                        </tr>
                    </thead>
                    <tbody className="">
                        {loading ? (
                            [...Array(3)].map((_, i) => (
                                <tr key={i}><td colSpan={3} className="px-12 py-4 h-12 text-slate-400 pl-16">Thinking...</td></tr>
                            ))
                        ) : filteredRules.length === 0 ? (
                            <tr><td colSpan={3} className="px-12 py-4 text-center text-slate-500 h-12 pl-16 font-bold text-xl transform -rotate-1">Nothing written here yet!</td></tr>
                        ) : (
                            filteredRules.map((rule) => (
                                <tr key={rule.sender} className="group hover:bg-yellow-50 transition-colors h-12">
                                    <td className="px-12 py-2 text-slate-700 font-bold text-xl pl-16">{rule.sender}</td>
                                    <td className="px-8 py-2">
                                        <span className={`px-2 py-0.5 border-2 border-slate-800 rounded-lg text-sm font-bold shadow-sm transform group-hover:rotate-1 transition-transform inline-block ${rule.category.includes('Shopping') ? 'bg-amber-200' :
                                            rule.category.includes('Finance') ? 'bg-emerald-200' :
                                                rule.category.includes('Read') ? 'bg-blue-200' :
                                                    'bg-slate-200'
                                            }`}>
                                            {rule.category}
                                        </span>
                                    </td>
                                    <td className="px-8 py-2 text-right">
                                        <button
                                            onClick={() => handleDeleteRule(rule.sender)}
                                            className="text-slate-400 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
                                        >
                                            <Trash2 className="w-5 h-5" />
                                        </button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Rules;
