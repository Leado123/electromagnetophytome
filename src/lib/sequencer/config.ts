// Sequencer configuration and constants
export const API_BASE = "http://localhost:5000/api";

export const EFFECT_COLORS = {
    AC: { bg: "bg-orange-100", border: "border-orange-400", text: "text-orange-700", icon: "⚡" },
    DC: { bg: "bg-red-100", border: "border-red-400", text: "text-red-700", icon: "🔋" },
    AMF: { bg: "bg-purple-100", border: "border-purple-400", text: "text-purple-700", icon: "🧲" },
    CMF: { bg: "bg-indigo-100", border: "border-indigo-400", text: "text-indigo-700", icon: "🧭" },
};

export const ROBOT_STATES = {
    idle: { color: "bg-gray-400", label: "Idle" },
    moving_to_pickup: { color: "bg-blue-500", label: "Moving to Pickup" },
    picking_up: { color: "bg-yellow-500", label: "Picking Up" },
    moving_to_target: { color: "bg-blue-500", label: "Moving to Target" },
    putting_down: { color: "bg-yellow-500", label: "Putting Down" },
    observing: { color: "bg-green-500", label: "Observing" },
    moving_to_observe: { color: "bg-cyan-500", label: "Moving to Observe" },
};

// Grid constants
export const GRID_ROWS = 2;
export const GRID_COLS = 12;
export const STORAGE_COLS = [0, 1, 2, 3, 4, 5, 6, 7];
export const EM_EXPOSURE_COLS = [8, 9, 10, 11];
