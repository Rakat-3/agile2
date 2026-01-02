import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, CheckCircle, XCircle, ChevronRight, Calculator, Loader } from 'lucide-react';

const API_BASE = 'http://localhost:8000'; // Adjust if needed, or use proxy

const Dashboard = () => {
    const [stats, setStats] = useState({ submitted: 0, approved: 0, rejected: 0 });
    const [selectedStatus, setSelectedStatus] = useState(null);
    const [contracts, setContracts] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchStats();
        // Poll every 10 seconds for updates
        const interval = setInterval(fetchStats, 10000);
        return () => clearInterval(interval);
    }, []);

    const fetchStats = async () => {
        try {
            const res = await axios.get(`${API_BASE}/stats`);
            setStats(res.data);
        } catch (err) {
            console.error("Failed to fetch stats", err);
        }
    };

    const handleCardClick = async (status) => {
        if (selectedStatus === status) {
            setSelectedStatus(null); // Toggle off
            setContracts([]);
            return;
        }

        setSelectedStatus(status);
        setLoading(true);
        try {
            const res = await axios.get(`${API_BASE}/contracts/${status}`);
            setContracts(res.data);
        } catch (err) {
            console.error("Failed to fetch contracts", err);
        } finally {
            setLoading(false);
        }
    };

    const StatCard = ({ title, count, icon: Icon, color, statusKey }) => (
        <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => handleCardClick(statusKey)}
            className={`glass-panel p-6 cursor-pointer relative overflow-hidden transition-all duration-300 ${selectedStatus === statusKey ? 'ring-2 ring-offset-2 ring-offset-slate-900' : ''
                }`}
            style={{ borderColor: selectedStatus === statusKey ? color : 'rgba(255,255,255,0.05)' }}
        >
            <div className="flex justify-between items-start">
                <div>
                    <p className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-1">{title}</p>
                    <h2 className="text-4xl font-bold text-white">{count}</h2>
                </div>
                <div className={`p-3 rounded-xl bg-opacity-20`} style={{ backgroundColor: color + '33' }}>
                    <Icon className="w-8 h-8" style={{ color: color }} />
                </div>
            </div>

            {/* Decorative Glow */}
            <div
                className="absolute -bottom-4 -right-4 w-24 h-24 rounded-full blur-2xl opacity-20 pointer-events-none"
                style={{ backgroundColor: color }}
            />
        </motion.div>
    );

    return (
        <div className="max-w-7xl mx-auto px-6 pb-12">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                <StatCard
                    title="Submitted Contracts"
                    count={stats.submitted}
                    icon={FileText}
                    color="#3b82f6"
                    statusKey="submitted"
                />
                <StatCard
                    title="Approved Contracts"
                    count={stats.approved}
                    icon={CheckCircle}
                    color="#10b981"
                    statusKey="approved"
                />
                <StatCard
                    title="Rejected Contracts"
                    count={stats.rejected}
                    icon={XCircle}
                    color="#ef4444"
                    statusKey="rejected"
                />
            </div>

            {/* Details Section */}
            <AnimatePresence mode="wait">
                {selectedStatus && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.3 }}
                        className="glass-panel p-6 min-h-[400px]"
                    >
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-2xl font-bold capitalize flex items-center gap-3">
                                <span className={`w-3 h-3 rounded-full`}
                                    style={{
                                        backgroundColor:
                                            selectedStatus === 'submitted' ? '#3b82f6' :
                                                selectedStatus === 'approved' ? '#10b981' : '#ef4444'
                                    }}
                                />
                                {selectedStatus} Contracts
                            </h3>
                            <div className="text-sm text-slate-400">
                                {contracts.length} records found
                            </div>
                        </div>

                        {loading ? (
                            <div className="flex flex-col items-center justify-center h-64 text-slate-400">
                                <Loader className="w-8 h-8 animate-spin mb-4 text-blue-500" />
                                <p>Loading data...</p>
                            </div>
                        ) : contracts.length === 0 ? (
                            <div className="flex flex-col items-center justify-center h-64 text-slate-500">
                                <FileText className="w-12 h-12 mb-4 opacity-50" />
                                <p>No contracts found in this category.</p>
                            </div>
                        ) : (
                            <div className="overflow-x-auto">
                                <table className="table-container">
                                    <thead>
                                        <tr>
                                            <th>Contract Title</th>
                                            <th>Type</th>
                                            {selectedStatus === 'submitted' && <th>Request Type</th>}
                                            {selectedStatus === 'submitted' && <th>Created At</th>}

                                            {selectedStatus === 'approved' && <th>Version</th>}
                                            {selectedStatus === 'approved' && <th>Signed Date</th>}
                                            {selectedStatus === 'approved' && <th>Approved At</th>}

                                            {selectedStatus === 'rejected' && <th>Decision</th>}
                                            {selectedStatus === 'rejected' && <th>Comment</th>}
                                            {selectedStatus === 'rejected' && <th>Rejected At</th>}

                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {contracts.map((contract, idx) => (
                                            <motion.tr
                                                key={contract.ContractId || idx}
                                                initial={{ opacity: 0, x: -10 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                transition={{ delay: idx * 0.05 }}
                                                className="table-row group"
                                            >
                                                <td className="font-medium text-white">{contract.ContractTitle || 'Untitled'}</td>
                                                <td>
                                                    <span className="px-2 py-1 rounded bg-slate-700/50 text-xs border border-white/5">
                                                        {contract.ContractType}
                                                    </span>
                                                </td>

                                                {selectedStatus === 'submitted' && <td>{contract.RequestType}</td>}
                                                {selectedStatus === 'submitted' && <td className="font-mono text-sm text-slate-400">{contract.CreatedAt?.split('T')[0] || contract.CreatedAt}</td>}

                                                {selectedStatus === 'approved' && <td>{contract.VersionNumber}</td>}
                                                {selectedStatus === 'approved' && <td>{contract.SignedDate}</td>}
                                                {selectedStatus === 'approved' && <td className="font-mono text-sm text-slate-400">{contract.ApprovedAt?.split('T')[0]}</td>}

                                                {selectedStatus === 'rejected' && <td><span className="text-red-400">{contract.ApprovalDecision}</span></td>}
                                                {selectedStatus === 'rejected' && <td className="max-w-xs truncate" title={contract.LegalComment}>{contract.LegalComment}</td>}
                                                {selectedStatus === 'rejected' && <td className="font-mono text-sm text-slate-400">{contract.RejectedAt?.split('T')[0]}</td>}

                                                <td>
                                                    <button className="p-2 hover:bg-white/10 rounded-full transition-colors text-slate-400 hover:text-white">
                                                        <ChevronRight className="w-4 h-4" />
                                                    </button>
                                                </td>
                                            </motion.tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default Dashboard;
