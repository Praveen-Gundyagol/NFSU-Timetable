import React from 'react';
import { Lock, Unlock, MoveHorizontal, User, MapPin } from 'lucide-react';
import type { Session } from '../../types';

interface SessionCardProps {
  session: Session;
  onToggleLock: (sessionId: number, currentLock: boolean) => void;
  onOpenMoveModal: (session: Session) => void;
  viewMode: 'PROGRAMME' | 'FACULTY' | 'ROOM';
}

export const SessionCard: React.FC<SessionCardProps> = ({
  session,
  onToggleLock,
  onOpenMoveModal,
  viewMode,
}) => {
  const isPractical = session.session_type === 'PRACTICAL';

  return (
    <div
      className={`relative group rounded-lg p-2.5 text-xs transition-all border shadow-xs ${
        isPractical
          ? 'bg-purple-50/90 hover:bg-purple-50 border-purple-200 text-purple-950'
          : 'bg-sky-50/90 hover:bg-sky-50 border-sky-200 text-sky-950'
      } ${session.is_locked ? 'ring-2 ring-amber-400/80 border-amber-400' : ''}`}
    >
      {/* Top Header: Code, Badges, and Lock Toggle */}
      <div className="flex items-center justify-between gap-1 mb-1.5">
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="font-bold tracking-tight text-[11px] bg-white/80 px-1.5 py-0.5 rounded border border-black/5 shadow-2xs">
            {session.subject_code}
          </span>
          {isPractical && (
            <span className="bg-purple-200/80 text-purple-800 text-[9px] font-semibold px-1.5 py-0.2 rounded">
              Lab ({session.duration_periods}P)
            </span>
          )}
          {session.batch_name && (
            <span className="bg-amber-100 text-amber-800 text-[9px] font-semibold px-1.5 py-0.2 rounded border border-amber-200">
              Batch {session.batch_name}
            </span>
          )}
        </div>

        {/* Lock toggle button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggleLock(session.id, session.is_locked);
          }}
          title={session.is_locked ? "Session Locked (Preserved during generation)" : "Lock Session"}
          className={`p-1 rounded transition-colors cursor-pointer ${
            session.is_locked
              ? 'bg-amber-100 text-amber-700 hover:bg-amber-200'
              : 'text-slate-400 hover:text-slate-600 hover:bg-black/5'
          }`}
        >
          {session.is_locked ? (
            <Lock className="w-3.5 h-3.5" />
          ) : (
            <Unlock className="w-3.5 h-3.5 opacity-60 group-hover:opacity-100" />
          )}
        </button>
      </div>

      {/* Subject Name */}
      <div className="font-semibold text-slate-800 leading-tight mb-1.5 line-clamp-1" title={session.subject_name}>
        {session.subject_name}
      </div>

      {/* Meta Information depending on active View */}
      <div className="space-y-0.5 text-[11px] text-slate-600">
        {viewMode !== 'FACULTY' && (
          <div className="flex items-center gap-1 text-slate-700 truncate" title={session.faculty_name}>
            <User className="w-3 h-3 text-slate-400 shrink-0" />
            <span className="truncate">{session.faculty_name}</span>
          </div>
        )}

        {viewMode !== 'ROOM' && (
          <div className="flex items-center gap-1 text-slate-700 truncate" title={session.room_name}>
            <MapPin className="w-3 h-3 text-slate-400 shrink-0" />
            <span className="truncate font-medium">{session.room_code}</span>
          </div>
        )}

        {viewMode !== 'PROGRAMME' && (
          <div className="text-[10px] text-slate-500 font-medium">
            Sec: {session.section_name} {session.batch_name ? `(${session.batch_name})` : ''}
          </div>
        )}
      </div>

      {/* Manual Move Quick Action */}
      <div className="mt-2 pt-1 border-t border-black/5 flex justify-end">
        <button
          onClick={() => onOpenMoveModal(session)}
          className="flex items-center gap-1 text-[10px] text-slate-500 hover:text-sky-700 font-medium transition-colors cursor-pointer"
          title="Manually adjust slot with live conflict check"
        >
          <MoveHorizontal className="w-3 h-3" />
          Move Slot
        </button>
      </div>
    </div>
  );
};
