import type {
  InstitutionConfig, TimeSlot, Room, Faculty, Programme, Subject,
  Timetable, ValidateMoveResponse
} from '../types';

const BASE_URL = 'http://localhost:8000/api';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    let errorMsg = `HTTP Error ${res.status}`;
    try {
      const errorData = await res.json();
      if (errorData.detail) errorMsg = errorData.detail;
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }

  return res.json();
}

export const api = {
  // Config
  getConfig: () => request<InstitutionConfig>('/config'),
  updateConfig: (data: Partial<InstitutionConfig>) => request<InstitutionConfig>('/config', {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  getTimeSlots: () => request<TimeSlot[]>('/config/slots'),

  // Resources
  getRooms: () => request<Room[]>('/resources/rooms'),
  createRoom: (data: Partial<Room>) => request<Room>('/resources/rooms', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  deleteRoom: (id: number) => request<{ message: string }>(`/resources/rooms/${id}`, {
    method: 'DELETE',
  }),

  getFaculty: () => request<Faculty[]>('/resources/faculty'),
  createFaculty: (data: Partial<Faculty>) => request<Faculty>('/resources/faculty', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  // Academic
  getProgrammes: () => request<Programme[]>('/academic/programmes'),
  getSubjects: () => request<Subject[]>('/academic/subjects'),
  seedSampleData: () => request<{ status: string; message: string }>('/academic/seed-sample-data', {
    method: 'POST',
  }),

  // Timetable
  getLatestTimetable: () => request<Timetable>('/timetable/latest'),
  generateTimetable: (timeLimitSeconds: number = 15) => request<Timetable>('/timetable/generate', {
    method: 'POST',
    body: JSON.stringify({ time_limit_seconds: timeLimitSeconds }),
  }),
  toggleLock: (sessionId: number, isLocked: boolean) => request<{ message: string }>('/timetable/sessions/lock', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, is_locked: isLocked }),
  }),
  validateMove: (timetableId: number, sessionId: number, targetDay: number, targetPeriod: number, targetRoomId?: number) =>
    request<ValidateMoveResponse>('/timetable/validate-move', {
      method: 'POST',
      body: JSON.stringify({
        timetable_id: timetableId,
        session_id: sessionId,
        target_day: targetDay,
        target_period: targetPeriod,
        target_room_id: targetRoomId,
      }),
    }),
  executeMove: (timetableId: number, sessionId: number, targetDay: number, targetPeriod: number, targetRoomId?: number) =>
    request<{ message: string }>('/timetable/sessions/move', {
      method: 'POST',
      body: JSON.stringify({
        timetable_id: timetableId,
        session_id: sessionId,
        target_day: targetDay,
        target_period: targetPeriod,
        target_room_id: targetRoomId,
      }),
    }),
  publishTimetable: (timetableId: number) => request<{ message: string }>(`/timetable/publish?timetable_id=${timetableId}`, {
    method: 'POST',
  }),
  getExportCsvUrl: (timetableId: number) => `${BASE_URL}/timetable/export/csv?timetable_id=${timetableId}`,
};
