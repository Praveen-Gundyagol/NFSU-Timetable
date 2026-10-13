import React, { useState, useEffect } from 'react';
import { Clock, Calendar, CheckCircle2, Save } from 'lucide-react';
import type { InstitutionConfig } from '../../types';
import { api } from '../../api/client';

interface ConfigPanelProps {
  config: InstitutionConfig | null;
  onRefresh: () => void;
}

const ALL_DAYS = [
  { index: 0, label: 'Monday' },
  { index: 1, label: 'Tuesday' },
  { index: 2, label: 'Wednesday' },
  { index: 3, label: 'Thursday' },
  { index: 4, label: 'Friday' },
  { index: 5, label: 'Saturday' },
];

export const ConfigPanel: React.FC<ConfigPanelProps> = ({ config, onRefresh }) => {
  const [name, setName] = useState('National Forensic Sciences University');
  const [workingDays, setWorkingDays] = useState<number[]>([0, 1, 2, 3, 4]);
  const [periodsPerDay, setPeriodsPerDay] = useState<number>(7);
  const [periodDuration, setPeriodDuration] = useState<number>(60);
  const [startTime, setStartTime] = useState<string>('09:00');
  const [lunchPeriod, setLunchPeriod] = useState<number>(4);
  const [saving, setSaving] = useState<boolean>(false);
  const [savedSuccess, setSavedSuccess] = useState<boolean>(false);

  useEffect(() => {
    if (config) {
      setName(config.name);
      setWorkingDays(config.working_days);
      setPeriodsPerDay(config.periods_per_day);
      setPeriodDuration(config.period_duration_minutes);
      setStartTime(config.start_time);
      if (config.break_periods.length > 0) {
        setLunchPeriod(config.break_periods[0]);
      }
    }
  }, [config]);

  const toggleDay = (dayIdx: number) => {
    if (workingDays.includes(dayIdx)) {
      if (workingDays.length > 1) {
        setWorkingDays(workingDays.filter((d) => d !== dayIdx));
      }
    } else {
      setWorkingDays([...workingDays, dayIdx].sort());
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSavedSuccess(false);
    try {
      await api.updateConfig({
        name,
        working_days: workingDays,
        periods_per_day: periodsPerDay,
        period_duration_minutes: periodDuration,
        start_time: startTime,
        break_periods: [lunchPeriod],
      });
      setSavedSuccess(true);
      onRefresh();
      setTimeout(() => setSavedSuccess(false), 3000);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-xl shadow-xs border border-slate-200 overflow-hidden">
      <div className="p-5 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-slate-800 text-sm">University Timetable Configuration</h3>
          <p className="text-xs text-slate-500">Configure university working days, timings, duration, and breaks</p>
        </div>
        <div className="p-2 bg-sky-100 text-sky-700 rounded-lg">
          <Clock className="w-5 h-5" />
        </div>
      </div>

      <form onSubmit={handleSave} className="p-6 space-y-6 text-xs">
        {/* Institution Name */}
        <div>
          <label className="block text-slate-700 font-semibold mb-1">University / Institute Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
            required
          />
        </div>

        {/* Working Days */}
        <div>
          <label className="block text-slate-700 font-semibold mb-2 flex items-center gap-1.5">
            <Calendar className="w-4 h-4 text-slate-500" />
            University Working Days
          </label>
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
            {ALL_DAYS.map((d) => {
              const selected = workingDays.includes(d.index);
              return (
                <button
                  type="button"
                  key={d.index}
                  onClick={() => toggleDay(d.index)}
                  className={`py-2 px-3 rounded-lg border text-center font-medium transition-all cursor-pointer ${
                    selected
                      ? 'bg-sky-50 border-sky-400 text-sky-900 shadow-2xs'
                      : 'bg-slate-50 border-slate-200 text-slate-500 hover:bg-slate-100'
                  }`}
                >
                  <div className="text-[11px]">{d.label.slice(0, 3)}</div>
                  <div className="text-[9px] uppercase font-semibold tracking-wider opacity-70">
                    {selected ? 'Open' : 'Off'}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Timing parameters */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-slate-700 font-semibold mb-1">Day Start Time</label>
            <input
              type="time"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-slate-700 font-semibold mb-1">Periods Per Day</label>
            <input
              type="number"
              min="4"
              max="10"
              value={periodsPerDay}
              onChange={(e) => setPeriodsPerDay(Number(e.target.value))}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-slate-700 font-semibold mb-1">Period Duration (Minutes)</label>
            <input
              type="number"
              min="30"
              max="120"
              step="5"
              value={periodDuration}
              onChange={(e) => setPeriodDuration(Number(e.target.value))}
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
              required
            />
          </div>
        </div>

        {/* Break Slot */}
        <div>
          <label className="block text-slate-700 font-semibold mb-1">Daily Lunch Break Slot</label>
          <select
            value={lunchPeriod}
            onChange={(e) => setLunchPeriod(Number(e.target.value))}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
          >
            {Array.from({ length: periodsPerDay }).map((_, p) => (
              <option key={p} value={p}>
                Period {p + 1} is Lunch Break
              </option>
            ))}
          </select>
          <p className="text-[11px] text-slate-500 mt-1">
            No regular classes or practical labs can be scheduled during this break slot.
          </p>
        </div>

        {/* Submit */}
        <div className="pt-2 flex items-center justify-between">
          {savedSuccess && (
            <span className="text-emerald-700 flex items-center gap-1.5 font-medium text-xs animate-in fade-in">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              Settings saved and time slots recalculated!
            </span>
          )}
          <div className="ml-auto">
            <button
              type="submit"
              disabled={saving}
              className="flex items-center gap-1.5 bg-sky-600 hover:bg-sky-500 text-white font-semibold px-4 py-2 rounded-lg shadow-xs transition-colors cursor-pointer"
            >
              <Save className="w-4 h-4" />
              {saving ? 'Saving...' : 'Save Configuration'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};
