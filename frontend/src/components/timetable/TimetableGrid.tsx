import React, { useState, useMemo } from 'react';
import { Filter, Users, Building2, BookOpen, AlertCircle, CheckCircle2 } from 'lucide-react';
import type {
  Timetable, Room, Faculty, Programme, Session
} from '../../types';
import { SessionCard } from './SessionCard';
import { ManualMoveModal } from './ManualMoveModal';

interface TimetableGridProps {
  timetable: Timetable | null;
  rooms: Room[];
  faculty: Faculty[];
  programmes: Programme[];
  workingDays: number[];
  periodsPerDay: number;
  breakPeriods: number[];
  onToggleLock: (sessionId: number, currentLock: boolean) => void;
  onRefresh: () => void;
}

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

export const TimetableGrid: React.FC<TimetableGridProps> = ({
  timetable,
  rooms,
  faculty,
  programmes,
  workingDays,
  periodsPerDay,
  breakPeriods,
  onToggleLock,
  onRefresh,
}) => {
  const [viewMode, setViewMode] = useState<'PROGRAMME' | 'FACULTY' | 'ROOM'>('PROGRAMME');
  const [selectedSectionId, setSelectedSectionId] = useState<number | null>(null);
  const [selectedFacultyId, setSelectedFacultyId] = useState<number | null>(null);
  const [selectedRoomId, setSelectedRoomId] = useState<number | null>(null);
  const [movingSession, setMovingSession] = useState<Session | null>(null);

  // Extract all sections
  const allSections = useMemo(() => {
    const list: { id: number; name: string; progName: string; semNum: number }[] = [];
    programmes.forEach((p) => {
      p.semesters.forEach((s) => {
        s.sections.forEach((sec) => {
          list.push({
            id: sec.id,
            name: sec.name,
            progName: p.code,
            semNum: s.semester_number,
          });
        });
      });
    });
    return list;
  }, [programmes]);

  // Set default filter selections
  React.useEffect(() => {
    if (allSections.length > 0 && selectedSectionId === null) {
      setSelectedSectionId(allSections[0].id);
    }
    if (faculty.length > 0 && selectedFacultyId === null) {
      setSelectedFacultyId(faculty[0].id);
    }
    if (rooms.length > 0 && selectedRoomId === null) {
      setSelectedRoomId(rooms[0].id);
    }
  }, [allSections, faculty, rooms, selectedSectionId, selectedFacultyId, selectedRoomId]);

  // Filter sessions according to active perspective
  const filteredSessions = useMemo(() => {
    if (!timetable?.sessions) return [];
    return timetable.sessions.filter((s) => {
      if (viewMode === 'PROGRAMME') {
        return s.section_id === selectedSectionId;
      } else if (viewMode === 'FACULTY') {
        return s.faculty_id === selectedFacultyId;
      } else {
        return s.room_id === selectedRoomId;
      }
    });
  }, [timetable, viewMode, selectedSectionId, selectedFacultyId, selectedRoomId]);

  // Organize sessions into a grid map: (day_index, period_index) -> Session[]
  const gridSessions = useMemo(() => {
    const map = new Map<string, Session[]>();
    filteredSessions.forEach((s) => {
      for (let p = s.period_index; p < s.period_index + s.duration_periods; p++) {
        const key = `${s.day_index}_${p}`;
        if (!map.has(key)) map.set(key, []);
        map.get(key)!.push(s);
      }
    });
    return map;
  }, [filteredSessions]);

  if (!timetable) {
    return (
      <div className="bg-white rounded-xl shadow-xs border border-slate-200 p-12 text-center">
        <div className="w-12 h-12 bg-sky-50 text-sky-600 rounded-full flex items-center justify-center mx-auto mb-3">
          <BookOpen className="w-6 h-6" />
        </div>
        <h3 className="font-semibold text-slate-800 text-base">No Timetable Generated Yet</h3>
        <p className="text-xs text-slate-500 max-w-md mx-auto mt-1 mb-4">
          Click <strong>Generate Timetable</strong> in the top header or load demo data to solve your first clash-free schedule with Google OR-Tools CP-SAT.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* View Switcher & Filter Bar */}
      <div className="bg-white rounded-xl shadow-xs border border-slate-200 p-4 flex flex-wrap items-center justify-between gap-4">
        {/* View Mode Radio Pills */}
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" /> View Perspective:
          </span>
          <div className="flex bg-slate-100 p-1 rounded-lg border border-slate-200">
            <button
              onClick={() => setViewMode('PROGRAMME')}
              className={`flex items-center gap-1.5 px-3 py-1 text-xs font-medium rounded-md transition-all cursor-pointer ${
                viewMode === 'PROGRAMME'
                  ? 'bg-white text-sky-700 shadow-2xs font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              Programme & Section
            </button>
            <button
              onClick={() => setViewMode('FACULTY')}
              className={`flex items-center gap-1.5 px-3 py-1 text-xs font-medium rounded-md transition-all cursor-pointer ${
                viewMode === 'FACULTY'
                  ? 'bg-white text-sky-700 shadow-2xs font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              Faculty-wise
            </button>
            <button
              onClick={() => setViewMode('ROOM')}
              className={`flex items-center gap-1.5 px-3 py-1 text-xs font-medium rounded-md transition-all cursor-pointer ${
                viewMode === 'ROOM'
                  ? 'bg-white text-sky-700 shadow-2xs font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Building2 className="w-3.5 h-3.5" />
              Room / Lab-wise
            </button>
          </div>
        </div>

        {/* Perspective Dropdown Selectors */}
        <div className="flex items-center space-x-3">
          {viewMode === 'PROGRAMME' && (
            <div className="flex items-center space-x-2">
              <label className="text-xs text-slate-600 font-medium">Class / Section:</label>
              <select
                value={selectedSectionId ?? ''}
                onChange={(e) => setSelectedSectionId(Number(e.target.value))}
                className="bg-white border border-slate-300 rounded-lg px-3 py-1.5 text-xs font-medium text-slate-800 focus:ring-2 focus:ring-sky-500 focus:outline-none"
              >
                {allSections.map((sec) => (
                  <option key={sec.id} value={sec.id}>
                    {sec.progName} &bull; Sem {sec.semNum} (Section {sec.name})
                  </option>
                ))}
              </select>
            </div>
          )}

          {viewMode === 'FACULTY' && (
            <div className="flex items-center space-x-2">
              <label className="text-xs text-slate-600 font-medium">Faculty Member:</label>
              <select
                value={selectedFacultyId ?? ''}
                onChange={(e) => setSelectedFacultyId(Number(e.target.value))}
                className="bg-white border border-slate-300 rounded-lg px-3 py-1.5 text-xs font-medium text-slate-800 focus:ring-2 focus:ring-sky-500 focus:outline-none"
              >
                {faculty.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.name} ({f.department})
                  </option>
                ))}
              </select>
            </div>
          )}

          {viewMode === 'ROOM' && (
            <div className="flex items-center space-x-2">
              <label className="text-xs text-slate-600 font-medium">Room / Laboratory:</label>
              <select
                value={selectedRoomId ?? ''}
                onChange={(e) => setSelectedRoomId(Number(e.target.value))}
                className="bg-white border border-slate-300 rounded-lg px-3 py-1.5 text-xs font-medium text-slate-800 focus:ring-2 focus:ring-sky-500 focus:outline-none"
              >
                {rooms.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.code} - {r.name} ({r.room_type}, cap {r.capacity})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Timetable Status Badge */}
          <div className="flex items-center gap-1.5 pl-3 border-l border-slate-200">
            <span
              className={`text-[11px] font-semibold px-2.5 py-1 rounded-full border flex items-center gap-1 ${
                timetable.status === 'PUBLISHED'
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                  : 'bg-amber-50 text-amber-800 border-amber-200'
              }`}
            >
              {timetable.status === 'PUBLISHED' ? (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  Published
                </>
              ) : (
                <>
                  <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                  Draft ({timetable.solver_status || 'Solved'})
                </>
              )}
            </span>
          </div>
        </div>
      </div>

      {/* Main Timetable Matrix Grid */}
      <div className="bg-white rounded-xl shadow-xs border border-slate-200 overflow-x-auto print:shadow-none print:border-none">
        <table className="w-full border-collapse text-left min-w-[900px]">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 text-[11px] uppercase tracking-wider font-semibold">
              <th className="py-3 px-4 w-28 border-r border-slate-200 sticky left-0 bg-slate-50 z-10">Day</th>
              {Array.from({ length: periodsPerDay }).map((_, p) => {
                const isBreak = breakPeriods.includes(p);
                return (
                  <th
                    key={p}
                    className={`py-3 px-3 text-center border-r border-slate-200 ${
                      isBreak ? 'bg-amber-50/70 text-amber-900 w-24' : 'w-44'
                    }`}
                  >
                    <div>Period {p + 1}</div>
                    <div className="text-[10px] font-normal lowercase text-slate-400">
                      {isBreak ? 'Lunch Break' : `Slot ${p + 1}`}
                    </div>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 text-xs">
            {workingDays.map((day) => (
              <tr key={day} className="hover:bg-slate-50/40 transition-colors">
                {/* Day label */}
                <td className="py-4 px-4 font-bold text-slate-800 border-r border-slate-200 bg-slate-50/60 sticky left-0 z-10">
                  {DAY_NAMES[day] || `Day ${day + 1}`}
                </td>

                {/* Periods */}
                {Array.from({ length: periodsPerDay }).map((_, p) => {
                  const isBreak = breakPeriods.includes(p);
                  if (isBreak) {
                    return (
                      <td
                        key={p}
                        className="py-3 px-2 bg-amber-50/40 border-r border-slate-200 text-center text-amber-800 font-medium text-[11px]"
                      >
                        <div className="transform -rotate-90 text-[10px] uppercase font-bold tracking-widest opacity-40">
                          Break
                        </div>
                      </td>
                    );
                  }

                  const cellKey = `${day}_${p}`;
                  const sessionsInCell = gridSessions.get(cellKey) || [];

                  return (
                    <td
                      key={p}
                      className="py-2 px-2 border-r border-slate-200 align-top hover:bg-sky-50/20 transition-colors min-h-[90px]"
                    >
                      {sessionsInCell.length > 0 ? (
                        <div className="space-y-1.5">
                          {sessionsInCell.map((sess) => (
                            <SessionCard
                              key={sess.id}
                              session={sess}
                              onToggleLock={onToggleLock}
                              onOpenMoveModal={(s) => setMovingSession(s)}
                              viewMode={viewMode}
                            />
                          ))}
                        </div>
                      ) : (
                        <div className="h-full min-h-[50px] flex items-center justify-center text-[10px] text-slate-300 select-none">
                          &mdash;
                        </div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Manual Move Modal */}
      {movingSession && (
        <ManualMoveModal
          session={movingSession}
          timetableId={timetable.id}
          rooms={rooms}
          periodsPerDay={periodsPerDay}
          workingDays={workingDays}
          breakPeriods={breakPeriods}
          onClose={() => setMovingSession(null)}
          onSuccess={() => {
            setMovingSession(null);
            onRefresh();
          }}
        />
      )}
    </div>
  );
};
