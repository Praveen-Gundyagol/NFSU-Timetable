import React, { useState, useEffect } from 'react';
import { X, AlertTriangle, CheckCircle2, ArrowRight } from 'lucide-react';
import type { Session, Room, ValidateMoveResponse } from '../../types';
import { api } from '../../api/client';

interface ManualMoveModalProps {
  session: Session;
  timetableId: number;
  rooms: Room[];
  periodsPerDay: number;
  workingDays: number[];
  breakPeriods: number[];
  onClose: () => void;
  onSuccess: () => void;
}

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

export const ManualMoveModal: React.FC<ManualMoveModalProps> = ({
  session,
  timetableId,
  rooms,
  periodsPerDay,
  workingDays,
  breakPeriods,
  onClose,
  onSuccess,
}) => {
  const [targetDay, setTargetDay] = useState<number>(session.day_index);
  const [targetPeriod, setTargetPeriod] = useState<number>(session.period_index);
  const [targetRoomId, setTargetRoomId] = useState<number>(session.room_id);
  const [validation, setValidation] = useState<ValidateMoveResponse | null>(null);
  const [validating, setValidating] = useState<boolean>(false);
  const [moving, setMoving] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Run live validation whenever target coordinates change
  useEffect(() => {
    let isMounted = true;
    setValidating(true);
    setErrorMsg(null);

    const timer = setTimeout(async () => {
      try {
        const res = await api.validateMove(
          timetableId,
          session.id,
          targetDay,
          targetPeriod,
          targetRoomId
        );
        if (isMounted) {
          setValidation(res);
          setValidating(false);
        }
      } catch (err: any) {
        if (isMounted) {
          setErrorMsg(err.message);
          setValidating(false);
        }
      }
    }, 200);

    return () => {
      isMounted = false;
      clearTimeout(timer);
    };
  }, [targetDay, targetPeriod, targetRoomId, session.id, timetableId]);

  const handleConfirmMove = async () => {
    if (!validation?.valid) return;
    setMoving(true);
    try {
      await api.executeMove(
        timetableId,
        session.id,
        targetDay,
        targetPeriod,
        targetRoomId
      );
      onSuccess();
    } catch (err: any) {
      setErrorMsg(err.message);
      setMoving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-lg w-full border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-slate-800 text-sm">Manual Slot Adjustment</h3>
            <p className="text-xs text-slate-500">Live hard-constraint validation will verify your move</p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-200/50 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4 text-xs">
          {/* Selected Session Info */}
          <div className="p-3 rounded-lg bg-sky-50 border border-sky-100 flex items-center justify-between">
            <div>
              <span className="font-bold text-sky-950">{session.subject_code}</span> - {session.subject_name}
              <div className="text-[11px] text-sky-800 mt-0.5">
                Instructor: {session.faculty_name} &bull; Section: {session.section_name} {session.batch_name ? `(${session.batch_name})` : ''}
              </div>
            </div>
            <span className="text-[10px] font-semibold bg-sky-200 text-sky-800 px-2 py-0.5 rounded">
              {session.duration_periods} Period{session.duration_periods > 1 ? 's' : ''}
            </span>
          </div>

          {/* Target Coordinate Selectors */}
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block font-medium text-slate-700 mb-1">Target Day</label>
              <select
                value={targetDay}
                onChange={(e) => setTargetDay(Number(e.target.value))}
                className="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
              >
                {workingDays.map((d) => (
                  <option key={d} value={d}>
                    {DAY_NAMES[d] || `Day ${d + 1}`}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Start Period</label>
              <select
                value={targetPeriod}
                onChange={(e) => setTargetPeriod(Number(e.target.value))}
                className="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
              >
                {Array.from({ length: periodsPerDay }).map((_, p) => (
                  <option key={p} value={p}>
                    Period {p + 1} {breakPeriods.includes(p) ? '(Lunch)' : ''}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-medium text-slate-700 mb-1">Target Room</label>
              <select
                value={targetRoomId}
                onChange={(e) => setTargetRoomId(Number(e.target.value))}
                className="w-full border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
              >
                {rooms.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.code} ({r.room_type}, cap {r.capacity})
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Immediate Conflict Validation Feedback */}
          <div className="pt-2">
            {validating ? (
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-slate-500 flex items-center gap-2">
                <div className="w-3.5 h-3.5 border-2 border-slate-400 border-t-transparent rounded-full animate-spin" />
                Validating hard constraints...
              </div>
            ) : validation?.valid ? (
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-800 flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold">Valid Move &bull; Zero Conflicts</div>
                  <div className="text-[11px] text-emerald-700 mt-0.5">
                    Faculty, room capacity, and student batches are all free with no overlap.
                  </div>
                </div>
              </div>
            ) : validation && !validation.valid ? (
              <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-800 space-y-1.5">
                <div className="flex items-center gap-1.5 font-semibold text-rose-900">
                  <AlertTriangle className="w-4 h-4 text-rose-600" />
                  Constraint Conflicts Detected:
                </div>
                <ul className="list-disc list-inside space-y-1 text-[11px] text-rose-700 pl-1">
                  {validation.conflicts.map((c, i) => (
                    <li key={i}>{c.message}</li>
                  ))}
                </ul>
              </div>
            ) : null}

            {errorMsg && (
              <div className="p-2 text-rose-600 bg-rose-50 rounded text-[11px] border border-rose-200 mt-2">
                {errorMsg}
              </div>
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex justify-end space-x-2">
          <button
            onClick={onClose}
            className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-800 rounded-lg transition-colors cursor-pointer"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirmMove}
            disabled={!validation?.valid || moving}
            className={`flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold rounded-lg shadow-xs transition-all cursor-pointer ${
              validation?.valid && !moving
                ? 'bg-sky-600 hover:bg-sky-500 text-white'
                : 'bg-slate-200 text-slate-400 cursor-not-allowed'
            }`}
          >
            {moving ? 'Moving...' : 'Confirm Move'}
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
