// API functions for sequencer
import { API_BASE } from './config';

export async function fetchPlants() {
    const response = await fetch(`${API_BASE}/plants`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    return data.plants || [];
}

export async function fetchSequencer() {
    const response = await fetch(`${API_BASE}/sequencer`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    return data.sequencer || Array(2).fill(null).map(() => Array(12).fill(""));
}

export async function fetchEffects() {
    const response = await fetch(`${API_BASE}/effects`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    return data.effects || Array(2).fill(null).map(() => Array(12).fill(""));
}

export async function fetchSimulationState() {
    const response = await fetch(`${API_BASE}/simulation/state`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
}

export async function updateSequencer(row: number, col: number, plantId: string) {
    const response = await fetch(`${API_BASE}/sequencer`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ row, col, plant_id: plantId }),
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
}

export async function updateEffect(row: number, col: number, effect: string, properties?: Record<string, any>) {
    const response = await fetch(`${API_BASE}/effects`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ row, col, effect, properties }),
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
}

export async function startSimulation() {
    const response = await fetch(`${API_BASE}/simulation/start`, { method: "POST" });
    return await response.json();
}

export async function stopSimulation() {
    const response = await fetch(`${API_BASE}/simulation/pause`, { method: "POST" });
    return await response.json();
}

export async function resetSimulation() {
    const response = await fetch(`${API_BASE}/simulation/reset`, { method: "POST" });
    return await response.json();
}

export async function setSimulationSpeed(speed: number) {
    const response = await fetch(`${API_BASE}/simulation/speed`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ speed }),
    });
    return await response.json();
}

export async function autoPopulatePlants() {
    const response = await fetch(`${API_BASE}/sequencer/auto-populate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
    });
    if (!response.ok) {
        const errText = await response.text();
        let err;
        try { err = JSON.parse(errText); } catch { err = { error: errText }; }
        throw new Error(err.error || "Unknown error");
    }
    return await response.json();
}

export async function autoSetEmEffects() {
    const response = await fetch(`${API_BASE}/em-effects/auto-set`, { method: "POST" });
    return await response.json();
}

export async function clearAllData() {
    const response = await fetch(`${API_BASE}/clear-all`, { method: "POST" });
    return await response.json();
}

export async function fetchEffectProperties(row: number, col: number) {
    const response = await fetch(`${API_BASE}/effects/${row}/${col}/properties`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
}
