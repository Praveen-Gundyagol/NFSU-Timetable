import React, { useState } from 'react';
import { Building2, Users, BookOpen, Plus, Trash2 } from 'lucide-react';
import type { Room, Faculty, Programme, Subject } from '../../types';
import { api } from '../../api/client';

interface ResourceManagementProps {
  rooms: Room[];
  faculty: Faculty[];
  programmes: Programme[];
  subjects: Subject[];
  onRefresh: () => void;
}

export const ResourceManagement: React.FC<ResourceManagementProps> = ({
  rooms,
  faculty,
  programmes: _programmes,
  subjects,
  onRefresh,
}) => {
  const [subTab, setSubTab] = useState<'rooms' | 'faculty' | 'curriculum'>('rooms');

  // Room Form State
  const [roomCode, setRoomCode] = useState('');
  const [roomName, setRoomName] = useState('');
  const [roomType, setRoomType] = useState('CLASSROOM');
  const [roomCapacity, setRoomCapacity] = useState(60);
  const [creatingRoom, setCreatingRoom] = useState(false);

  // Faculty Form State
  const [facEmpId, setFacEmpId] = useState('');
  const [facName, setFacName] = useState('');
  const [facEmail, setFacEmail] = useState('');
  const [facDept, setFacDept] = useState('Cyber Security');
  const [creatingFaculty, setCreatingFaculty] = useState(false);

  const handleCreateRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!roomCode || !roomName) return;
    setCreatingRoom(true);
    try {
      await api.createRoom({
        code: roomCode,
        name: roomName,
        room_type: roomType,
        capacity: roomCapacity,
        is_active: true,
      });
      setRoomCode('');
      setRoomName('');
      onRefresh();
    } finally {
      setCreatingRoom(false);
    }
  };

  const handleDeleteRoom = async (id: number) => {
    if (!confirm('Are you sure you want to delete this room?')) return;
    await api.deleteRoom(id);
    onRefresh();
  };

  const handleCreateFaculty = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!facEmpId || !facName) return;
    setCreatingFaculty(true);
    try {
      await api.createFaculty({
        employee_id: facEmpId,
        name: facName,
        email: facEmail,
        department: facDept,
        max_weekly_periods: 16,
        max_daily_periods: 4,
        is_active: true,
      });
      setFacEmpId('');
      setFacName('');
      setFacEmail('');
      onRefresh();
    } finally {
      setCreatingFaculty(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Navigation Sub-Tabs */}
      <div className="flex space-x-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setSubTab('rooms')}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors cursor-pointer ${
            subTab === 'rooms'
              ? 'bg-sky-600 text-white shadow-xs'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <Building2 className="w-3.5 h-3.5" />
          Rooms & Labs ({rooms.length})
        </button>
        <button
          onClick={() => setSubTab('faculty')}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors cursor-pointer ${
            subTab === 'faculty'
              ? 'bg-sky-600 text-white shadow-xs'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <Users className="w-3.5 h-3.5" />
          Faculty Matrix ({faculty.length})
        </button>
        <button
          onClick={() => setSubTab('curriculum')}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors cursor-pointer ${
            subTab === 'curriculum'
              ? 'bg-sky-600 text-white shadow-xs'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          <BookOpen className="w-3.5 h-3.5" />
          Programmes & Subjects ({subjects.length})
        </button>
      </div>

      {/* --- ROOMS & LABS --- */}
      {subTab === 'rooms' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Room List Table */}
          <div className="lg:col-span-2 bg-white rounded-xl shadow-xs border border-slate-200 overflow-hidden">
            <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
              <h3 className="font-semibold text-slate-800 text-sm">Classrooms & Laboratories</h3>
              <span className="text-xs text-slate-500">{rooms.length} facilities registered</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 font-semibold">
                  <tr>
                    <th className="py-2.5 px-4">Code</th>
                    <th className="py-2.5 px-4">Facility Name</th>
                    <th className="py-2.5 px-4">Facility Type</th>
                    <th className="py-2.5 px-4 text-center">Capacity</th>
                    <th className="py-2.5 px-4 text-center">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {rooms.map((r) => (
                    <tr key={r.id} className="hover:bg-slate-50/50">
                      <td className="py-2.5 px-4 font-bold text-slate-800">{r.code}</td>
                      <td className="py-2.5 px-4 text-slate-700">{r.name}</td>
                      <td className="py-2.5 px-4">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                            r.room_type === 'CLASSROOM'
                              ? 'bg-sky-100 text-sky-800'
                              : 'bg-purple-100 text-purple-800'
                          }`}
                        >
                          {r.room_type}
                        </span>
                      </td>
                      <td className="py-2.5 px-4 text-center font-medium text-slate-700">{r.capacity}</td>
                      <td className="py-2.5 px-4 text-center">
                        <button
                          onClick={() => handleDeleteRoom(r.id)}
                          className="text-slate-400 hover:text-rose-600 transition-colors cursor-pointer"
                          title="Delete room"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Add Room Card */}
          <div className="bg-white rounded-xl shadow-xs border border-slate-200 p-5 h-fit">
            <h3 className="font-semibold text-slate-800 text-sm mb-3">Add Room or Laboratory</h3>
            <form onSubmit={handleCreateRoom} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-600 font-medium mb-1">Room Code</label>
                <input
                  type="text"
                  placeholder="e.g. LAB-CYBER-2"
                  value={roomCode}
                  onChange={(e) => setRoomCode(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg px-3 py-1.5 text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-600 font-medium mb-1">Room Name</label>
                <input
                  type="text"
                  placeholder="e.g. Malware Analysis Lab"
                  value={roomName}
                  onChange={(e) => setRoomName(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg px-3 py-1.5 text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-600 font-medium mb-1">Facility Type</label>
                <select
                  value={roomType}
                  onChange={(e) => setRoomType(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg px-3 py-1.5 text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
                >
                  <option value="CLASSROOM">CLASSROOM (Lecture Hall)</option>
                  <option value="LAB_COMPUTER">LAB_COMPUTER (Computing Lab)</option>
                  <option value="LAB_CYBER">LAB_CYBER (Cyber Security Lab)</option>
                  <option value="LAB_FORENSIC">LAB_FORENSIC (Digital Forensics Lab)</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-600 font-medium mb-1">Seating Capacity</label>
                <input
                  type="number"
                  min="10"
                  max="200"
                  value={roomCapacity}
                  onChange={(e) => setRoomCapacity(Number(e.target.value))}
                  className="w-full border border-slate-300 rounded-lg px-3 py-1.5 text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={creatingRoom}
                className="w-full flex items-center justify-center gap-1.5 bg-sky-600 hover:bg-sky-500 text-white font-semibold py-2 rounded-lg transition-colors shadow-xs mt-2 cursor-pointer"
              >
                <Plus className="w-4 h-4" />
                {creatingRoom ? 'Adding...' : 'Add Facility'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* --- FACULTY MATRIX --- */}
      {subTab === 'faculty' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white rounded-xl shadow-xs border border-slate-200 overflow-hidden">
            <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
              <h3 className="font-semibold text-slate-800 text-sm">Faculty Members</h3>
              <span className="text-xs text-slate-500">{faculty.length} faculty members</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 font-semibold">
                  <tr>
                    <th className="py-2.5 px-4">Employee ID</th>
                    <th className="py-2.5 px-4">Name</th>
                    <th className="py-2.5 px-4">Department</th>
                    <th className="py-2.5 px-4 text-center">Max Weekly</th>
                    <th className="py-2.5 px-4 text-center">Max Daily</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {faculty.map((f) => (
                    <tr key={f.id} className="hover:bg-slate-50/50">
                      <td className="py-2.5 px-4 font-mono font-medium text-slate-600">{f.employee_id}</td>
                      <td className="py-2.5 px-4 font-bold text-slate-800">{f.name}</td>
                      <td className="py-2.5 px-4 text-slate-700">{f.department}</td>
                      <td className="py-2.5 px-4 text-center font-medium text-slate-700">{f.max_weekly_periods} hrs</td>
                      <td className="py-2.5 px-4 text-center font-medium text-slate-700">{f.max_daily_periods} hrs</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-xs border border-slate-200 p-5 h-fit">
            <h3 className="font-semibold text-slate-800 text-sm mb-3">Register Faculty Member</h3>
            <form onSubmit={handleCreateFaculty} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-600 font-medium mb-1">Employee ID</label>
                <input
                  type="text"
                  placeholder="e.g. NFSU-FAC-06"
                  value={facEmpId}
                  onChange={(e) => setFacEmpId(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg px-3 py-1.5 text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-600 font-medium mb-1">Full Name</label>
                <input
                  type="text"
                  placeholder="e.g. Dr. Rajesh Kumar"
                  value={facName}
                  onChange={(e) => setFacName(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg px-3 py-1.5 text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-600 font-medium mb-1">Email Address</label>
                <input
                  type="email"
                  placeholder="rkumar@nfsu.ac.in"
                  value={facEmail}
                  onChange={(e) => setFacEmail(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg px-3 py-1.5 text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-600 font-medium mb-1">Department</label>
                <input
                  type="text"
                  value={facDept}
                  onChange={(e) => setFacDept(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg px-3 py-1.5 text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={creatingFaculty}
                className="w-full flex items-center justify-center gap-1.5 bg-sky-600 hover:bg-sky-500 text-white font-semibold py-2 rounded-lg transition-colors shadow-xs mt-2 cursor-pointer"
              >
                <Plus className="w-4 h-4" />
                {creatingFaculty ? 'Registering...' : 'Register Faculty'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* --- PROGRAMMES & SUBJECTS --- */}
      {subTab === 'curriculum' && (
        <div className="bg-white rounded-xl shadow-xs border border-slate-200 overflow-hidden">
          <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
            <h3 className="font-semibold text-slate-800 text-sm">Academic Programmes & Subject Curriculum</h3>
            <span className="text-xs text-slate-500">{subjects.length} subjects registered</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 font-semibold">
                <tr>
                  <th className="py-2.5 px-4">Subject Code</th>
                  <th className="py-2.5 px-4">Subject Name</th>
                  <th className="py-2.5 px-4">Type</th>
                  <th className="py-2.5 px-4 text-center">Weekly Theory</th>
                  <th className="py-2.5 px-4 text-center">Weekly Practical</th>
                  <th className="py-2.5 px-4">Required Room Type</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {subjects.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50/50">
                    <td className="py-2.5 px-4 font-bold text-slate-800">{s.code}</td>
                    <td className="py-2.5 px-4 text-slate-700">{s.name}</td>
                    <td className="py-2.5 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-800">
                        {s.subject_type}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-center font-medium">{s.weekly_theory_periods} periods</td>
                    <td className="py-2.5 px-4 text-center font-medium">
                      {s.weekly_practical_sessions > 0
                        ? `${s.weekly_practical_sessions} session (${s.practical_duration_periods} hrs)`
                        : 'None'}
                    </td>
                    <td className="py-2.5 px-4 font-medium text-purple-700">{s.required_room_type}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
