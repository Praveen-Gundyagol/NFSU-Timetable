import React from 'react';
import { Calendar, Play, Download, Printer, CheckCircle2, Database } from 'lucide-react';
import type { Timetable } from '../../types';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  timetable: Timetable | null;
  generating: boolean;
  onGenerate: () => void;
  onSeedData: () => void;
  onPublish: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  timetable,
  generating,
  onGenerate,
  onSeedData,
  onPublish,
}) => {
  return (
    <header className="bg-slate-900 text-white shadow-md border-b border-slate-800 sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-sky-600 rounded-lg shadow-sm">
              <Calendar className="h-6 w-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-bold tracking-tight">NFSU Timetable Generator</h1>
                <span className="text-[10px] uppercase font-semibold tracking-wider bg-sky-950 text-sky-400 border border-sky-800 px-2 py-0.5 rounded">
                  CP-SAT Powered
                </span>
              </div>
              <p className="text-xs text-slate-400">School of Cyber Security & Digital Forensics</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex space-x-1 bg-slate-800/60 p-1 rounded-lg border border-slate-700/50">
            <button
              onClick={() => setActiveTab('timetable')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                activeTab === 'timetable'
                  ? 'bg-sky-600 text-white shadow-sm'
                  : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              Timetable Matrix
            </button>
            <button
              onClick={() => setActiveTab('resources')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                activeTab === 'resources'
                  ? 'bg-sky-600 text-white shadow-sm'
                  : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              Rooms & Faculty
            </button>
            <button
              onClick={() => setActiveTab('config')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                activeTab === 'config'
                  ? 'bg-sky-600 text-white shadow-sm'
                  : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              University Config
            </button>
          </nav>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            <button
              onClick={onSeedData}
              title="Load realistic NFSU demo dataset (Rooms, Labs, Faculty, Subjects)"
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg transition-colors cursor-pointer"
            >
              <Database className="w-3.5 h-3.5 text-purple-400" />
              Demo Data
            </button>

            {timetable && (
              <>
                <button
                  onClick={() => window.print()}
                  className="p-1.5 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
                  title="Print Timetable"
                >
                  <Printer className="w-4 h-4" />
                </button>
                <a
                  href={`http://localhost:8000/api/timetable/export/csv?timetable_id=${timetable.id}`}
                  download
                  className="p-1.5 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
                  title="Export to CSV"
                >
                  <Download className="w-4 h-4" />
                </a>
                {timetable.status === 'DRAFT' && timetable.solver_status !== 'INFEASIBLE' && (
                  <button
                    onClick={onPublish}
                    className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium bg-emerald-700 hover:bg-emerald-600 text-white rounded-lg transition-colors shadow-sm cursor-pointer"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Publish
                  </button>
                )}
              </>
            )}

            <button
              onClick={onGenerate}
              disabled={generating}
              className={`flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold rounded-lg shadow-sm transition-all cursor-pointer ${
                generating
                  ? 'bg-sky-800 text-sky-200 cursor-not-allowed'
                  : 'bg-sky-600 hover:bg-sky-500 text-white'
              }`}
            >
              {generating ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Solving CP-SAT...
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  Generate Timetable
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
