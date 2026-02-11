
import React, { useEffect, useState } from 'react';
import { Plus, Trash2, Search, PenTool } from 'lucide-react';
import { getRules, addRule, deleteRule, type Rule } from '../services/api';

const Rules: React.FC = () => {
    const [rules, setRules] = useState<Rule[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    const [showAddForm, setShowAddForm] = useState(false);
    const [ruleType, setRuleType] = useState<'sender' | 'subject'>('sender');  // NEW
    const [newSender, setNewSender] = useState('');
    const [newKeyword, setNewKeyword] = useState('');  // NEW
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

        if (ruleType === 'sender' && !newSender) return;
        if (ruleType === 'subject' && !newKeyword) return;

        try {
            const ruleData: Rule = {
                category: newCategory,
                rule_type: ruleType,
                ...(ruleType === 'sender' ? { sender: newSender } : { keyword: newKeyword })
            };
            await addRule(ruleData);
            setNewSender('');
            setNewKeyword('');
            setShowAddForm(false);
            fetchRules();
        } catch (error: any) {
            // Handle duplicate rule error (409 Conflict)
            if (error.response?.status === 409) {
                const existingRule = error.response.data.detail.existing_rule;
                const ruleKey = ruleType === 'sender' ? newSender : newKeyword;
                const confirmed = confirm(
                    `Rule for "${ruleKey}" already exists (Category: ${existingRule.category}).\n\nReplace with new category "${newCategory}"?`
                );

                if (confirmed) {
                    // Delete old rule and add new one
                    try {
                        await deleteRule(existingRule.key);
                        const ruleData: Rule = {
                            category: newCategory,
                            rule_type: ruleType,
                            ...(ruleType === 'sender' ? { sender: newSender } : { keyword: newKeyword })
                        };
                        await addRule(ruleData);
                        setNewSender('');
                        setNewKeyword('');
                        setShowAddForm(false);
                        fetchRules();
                    } catch (replaceError) {
                        alert("Failed to replace rule");
                    }
                }
            } else {
                alert("Failed to add rule");
            }
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
        (r.sender && r.sender.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (r.keyword && r.keyword.toLowerCase().includes(searchTerm.toLowerCase())) ||
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

                    <form onSubmit={handleAddRule} className="space-y-4">
                        {/* Rule Type Selector */}
                        <div className="flex gap-6 pb-2 border-b border-slate-300">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="radio"
                                    value="sender"
                                    checked={ruleType === 'sender'}
                                    onChange={(e) => setRuleType(e.target.value as 'sender')}
                                    className="w-4 h-4 accent-blue-500"
                                />
                                <span className="font-bold text-slate-700">By Sender</span>
                            </label>
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="radio"
                                    value="subject"
                                    checked={ruleType === 'subject'}
                                    onChange={(e) => setRuleType(e.target.value as 'subject')}
                                    className="w-4 h-4 accent-blue-500"
                                />
                                <span className="font-bold text-slate-700">By Subject Keyword</span>
                            </label>
                        </div>

                        <div className="flex gap-4 items-end">
                            <div className="flex-1">
                                <label className="block text-lg font-bold text-slate-700 mb-1">
                                    {ruleType === 'sender' ? 'Sender:' : 'Subject Keyword:'}
                                </label>
                                {ruleType === 'sender' ? (
                                    <input
                                        type="email"
                                        value={newSender}
                                        onChange={(e) => setNewSender(e.target.value)}
                                        className="w-full bg-transparent border-b-2 border-slate-800 px-2 py-1 text-xl font-handwriting focus:border-blue-500 outline-none placeholder:text-slate-400/50"
                                        placeholder="newsletter@sketchy.com"
                                        required
                                        autoFocus
                                    />
                                ) : (
                                    <input
                                        type="text"
                                        value={newKeyword}
                                        onChange={(e) => setNewKeyword(e.target.value)}
                                        className="w-full bg-transparent border-b-2 border-slate-800 px-2 py-1 text-xl font-handwriting focus:border-blue-500 outline-none placeholder:text-slate-400/50"
                                        placeholder="명세서, 영수증, etc."
                                        required
                                        autoFocus
                                    />
                                )}
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
                        </div>
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
                            <th className="px-12 py-3 text-slate-400 font-bold text-sm uppercase tracking-widest pl-16">Rule</th>
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
                            filteredRules.map((rule) => {
                                const ruleKey = rule.sender || `keyword:${rule.keyword}`;
                                const displayText = rule.rule_type === 'subject'
                                    ? `📌 ${rule.keyword}`
                                    : rule.sender || '';

                                return (
                                    <tr key={ruleKey} className="group hover:bg-yellow-50 transition-colors h-12">
                                        <td className="px-12 py-2 text-slate-700 font-bold text-xl pl-16">{displayText}</td>
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
                                                onClick={() => handleDeleteRule(ruleKey)}
                                                className="text-slate-400 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
                                            >
                                                <Trash2 className="w-5 h-5" />
                                            </button>
                                        </td>
                                    </tr>
                                );
                            })
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Rules;
