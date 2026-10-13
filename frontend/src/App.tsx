import { useState, useEffect, useCallback } from 'react';
import { Header } from './components/common/Header';
import { TimetableGrid } from './components/timetable/TimetableGrid';
import { ResourceManagement } from './components/resources/ResourceManagement';
import { ConfigPanel } from './components/config/ConfigPanel';
import { InfeasibilityReportModal } from './components/timetable/InfeasibilityReportModal';
import type {
  InstitutionConfig, TimeSlot, Room, Faculty, Programme, Subject,
  Timetable, InfeasibilityReport
} from './types';
import { api } from './api/client';
import { AlertCircle, CheckCircle2 } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState<string>('timetable');
  const [config, setConfig] = useState<InstitutionConfig | null>(null);
  const [_timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [faculty, setFaculty] = useState<Faculty[]>([]);
  const [programmes, setProgrammes] = useState<Programme[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [timetable, setTimetable] = useState<Timetable | null>(null);

  const [loading, setLoading] = useState<boolean>(true);
  const [generating, setGenerating] = useState<boolean>(false);
  const [infeasibilityReport, setInfeasibilityReport] = useState<InfeasibilityReport | null>(null);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const showNotification = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 4000);
  };

  const loadAllData = useCallback(async () => {
    try {
      const [cfg, slots, rmList, facList, progList, subjList] = await Promise.all([
        api.getConfig(),
        api.getTimeSlots(),
        api.getRooms(),
        api.getFaculty(),
        api.getProgrammes(),
        api.getSubjects(),
      ]);

      setConfig(cfg);
      setTimeSlots(slots);
      setRooms(rmList);
      setFaculty(facList);
      setProgrammes(progList);
      setSubjects(subjList);

      try {
        const tt = await api.getLatestTimetable();
        setTimetable(tt);
      } catch {
        // No timetable generated yet
      }
    } catch (err: any) {
      showNotification('error', `Failed to load system data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAllData();
  }, [loadAllData]);

  // Handle generation via Google OR-Tools CP-SAT
  const handleGenerate = async () => {
    setGenerating(true);
    setInfeasibilityReport(null);
    try {
      const result = await api.generateTimetable(15);
      setTimetable(result);
      if (result.solver_status === 'INFEASIBLE' && result.infeasibility_report) {
        setInfeasibilityReport(result.infeasibility_report);
        showNotification('error', 'Timetable is infeasible. Click to inspect conflicting constraints.');
      } else {
        showNotification('success', `Timetable successfully generated via CP-SAT (${result.solver_status})!`);
      }
      loadAllData();
    } catch (err: any) {
      showNotification('error', `Generation failed: ${err.message}`);
    } finally {
      setGenerating(false);
    }
  };

  // Handle demo data seeding
  const handleSeedData = async () => {
    if (!confirm('Load realistic NFSU demo dataset? This will configure rooms, faculty, and programmes.')) return;
    setLoading(true);
    try {
      const res = await api.seedSampleData();
      showNotification('success', res.message);
      await loadAllData();
      // Auto trigger generation for convenience
      handleGenerate();
    } catch (err: any) {
      showNotification('error', `Failed to load demo data: ${err.message}`);
      setLoading(false);
    }
  };

  // Handle session locking toggle
  const handleToggleLock = async (sessionId: number, currentLock: boolean) => {
    try {
      await api.toggleLock(sessionId, !currentLock);
      showNotification('success', `Session ${!currentLock ? 'locked' : 'unlocked'}.`);
      // Update local state immediately
      if (timetable) {
        setTimetable({
          ...timetable,
          sessions: timetable.sessions.map((s) =>
            s.id === sessionId ? { ...s, is_locked: !currentLock } : s
          ),
        });
      }
    } catch (err: any) {
      showNotification('error', `Failed to lock session: ${err.message}`);
    }
  };

  // Handle publishing timetable
  const handlePublish = async () => {
    if (!timetable) return;
    try {
      await api.publishTimetable(timetable.id);
      showNotification('success', 'Timetable published successfully!');
      loadAllData();
    } catch (err: any) {
      showNotification('error', err.message);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center space-y-3">
          <div className="w-8 h-8 border-3 border-sky-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs text-slate-600 font-medium">Connecting to NFSU Timetable Engine...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* Top Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        timetable={timetable}
        generating={generating}
        onGenerate={handleGenerate}
        onSeedData={handleSeedData}
        onPublish={handlePublish}
      />

      {/* Floating Notification Banner */}
      {notification && (
        <div className="fixed bottom-5 right-5 z-50 animate-in slide-in-from-bottom-3 duration-200">
          <div
            className={`px-4 py-3 rounded-xl shadow-lg border text-xs font-semibold flex items-center gap-2.5 max-w-md ${
              notification.type === 'success'
                ? 'bg-emerald-950 text-emerald-100 border-emerald-800'
                : 'bg-rose-950 text-rose-100 border-rose-800'
            }`}
          >
            {notification.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            )}
            <span>{notification.message}</span>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'timetable' && (
          <TimetableGrid
            timetable={timetable}
            rooms={rooms}
            faculty={faculty}
            programmes={programmes}
            workingDays={config?.working_days || [0, 1, 2, 3, 4]}
            periodsPerDay={config?.periods_per_day || 7}
            breakPeriods={config?.break_periods || [4]}
            onToggleLock={handleToggleLock}
            onRefresh={loadAllData}
          />
        )}

        {activeTab === 'resources' && (
          <ResourceManagement
            rooms={rooms}
            faculty={faculty}
            programmes={programmes}
            subjects={subjects}
            onRefresh={loadAllData}
          />
        )}

        {activeTab === 'config' && (
          <ConfigPanel config={config} onRefresh={loadAllData} />
        )}
      </main>

      {/* Infeasibility Diagnostic Modal */}
      {infeasibilityReport && (
        <InfeasibilityReportModal
          report={infeasibilityReport}
          onClose={() => setInfeasibilityReport(null)}
          onRetry={handleGenerate}
        />
      )}
    </div>
  );
}
