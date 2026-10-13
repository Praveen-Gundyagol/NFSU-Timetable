import React from 'react';
import { X, AlertOctagon, Info, Lightbulb, RefreshCw } from 'lucide-react';
import type { InfeasibilityReport } from '../../types';

interface InfeasibilityReportModalProps {
  report: InfeasibilityReport;
  onClose: () => void;
  onRetry: () => void;
}

export const InfeasibilityReportModal: React.FC<InfeasibilityReportModalProps> = ({
  report,
  onClose,
  onRetry,
}) => {
  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full border border-rose-200 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="px-6 py-4 bg-rose-50 border-b border-rose-200 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-rose-600 rounded-lg text-white">
              <AlertOctagon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-rose-950 text-sm">Schedule Infeasible &bull; Conflict Diagnostics</h3>
              <p className="text-xs text-rose-700">
                Google OR-Tools CP-SAT proved no schedule satisfies 100% of the active hard constraints
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-rose-400 hover:text-rose-600 p-1 rounded-lg hover:bg-rose-100 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Diagnostic Breakdown */}
        <div className="p-6 space-y-4 max-h-[70vh] overflow-y-auto text-xs">
          {/* Summary Box */}
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-700">
              <Info className="w-4 h-4 text-sky-600" />
              <span>
                Unscheduled Sessions: <strong className="text-rose-600">{report.unscheduled_count}</strong>
              </span>
            </div>
            <span className="text-[11px] text-slate-500">
              Solver Time: {report.solver_time_seconds}s
            </span>
          </div>

          {/* Conflict List */}
          <div>
            <h4 className="font-semibold text-slate-800 mb-2">Identified Resource Bottlenecks & Conflicts:</h4>
            <div className="space-y-2">
              {report.conflict_explanations.map((exp, index) => (
                <div
                  key={index}
                  className="p-3 rounded-lg bg-rose-50/70 border border-rose-100 text-rose-900 leading-relaxed font-mono text-[11px]"
                >
                  {exp}
                </div>
              ))}
            </div>
          </div>

          {/* Recommendations Box */}
          <div className="p-4 bg-amber-50/80 border border-amber-200 rounded-lg text-amber-900 space-y-1.5">
            <div className="flex items-center gap-1.5 font-semibold text-amber-950">
              <Lightbulb className="w-4 h-4 text-amber-600" />
              Architect Recommendations:
            </div>
            <ul className="list-disc list-inside space-y-1 text-[11px] text-amber-800 pl-1">
              <li>Increase faculty availability in the Faculty Matrix or reduce assigned weekly hours.</li>
              <li>Add or activate an additional laboratory matching the required specialty.</li>
              <li>Check for conflicting locked sessions that monopolize critical lab hours.</li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex justify-between items-center">
          <span className="text-[11px] text-slate-500">
            Mandatory constraints are strictly enforced to guarantee zero double-booking.
          </span>
          <div className="flex space-x-2">
            <button
              onClick={onClose}
              className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-800 rounded-lg transition-colors cursor-pointer"
            >
              Dismiss
            </button>
            <button
              onClick={onRetry}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white rounded-lg transition-colors cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Retry Solver
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
