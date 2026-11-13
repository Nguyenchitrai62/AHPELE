/**
 * AHPELE phase guard (pi extension, H3).
 *
 * Agents tend to spend all their time reading and analysing and write the
 * deliverables late or never. At fixed fractions of the available time this
 * extension checks, through the task relay, which file paths named in the
 * instruction (AHPELE_DELIVERABLES, extracted by harness.py) do not exist yet,
 * and appends a short reminder at the next turn boundary. Near the end it asks
 * the agent to finalise. Generic: it never knows anything about a task beyond
 * the paths its instruction names.
 */
import type {ExtensionAPI} from '@earendil-works/pi-coding-agent';
import http from 'node:http';

const RELAY = process.env.TASK_RELAY_URL ?? "";
const STOP_AT_MS = Number(process.env.AHPELE_STOP_AT_EPOCH ?? "0") * 1000;
const PATHS: string[] = (() => {
	try {
		return JSON.parse(process.env.AHPELE_DELIVERABLES ?? "[]");
	} catch {
		return [];
	}
})();
const MARKS = [0.3, 0.6, 0.85];
// AHPELE RC-0015: constraint gate. If a deliverable is written before the
// requirements table exists, remind once that constraints come first.
const REQ_TABLE = "/tmp/ahpele/requirements.csv";
const GATE_ON = (process.env.AHPELE_REQ_GATE ?? "1") !== "0";
const GATE_EVERY_MS = 90_000;
const GATE =
	"[harness] A deliverable file already exists but there is no requirements table yet (" + REQ_TABLE + " is " +
	"missing or nearly empty). Constraints come first: before you go further with the design, extract every hard " +
	"requirement of the governing documents into that table (document, clause, value), review the candidates in " +
	"/tmp/ahpele/req_candidates.md if it exists (python3 /tmp/ahpele/bin/ahpele_reqscan.py --check lists the " +
	"unreviewed ones), then check the deliverable against every requirement and fix it.";

function relayExec(command: string): Promise<{exit_code?: number; output?: string}> {
	return new Promise((resolve) => {
		if (!RELAY) return resolve({});
		const url = new URL(`${RELAY}/exec`);
		const data = Buffer.from(JSON.stringify({command, timeout_sec: 30}));
		const req = http.request(
			{hostname: url.hostname, port: url.port, path: url.pathname, method: "POST",
			 headers: {"Content-Type": "application/json", "Content-Length": data.length}},
			(res) => {
				const chunks: Buffer[] = [];
				res.on("data", (c) => chunks.push(c));
				res.on("end", () => {
					try {
						resolve(JSON.parse(Buffer.concat(chunks).toString() || "{}"));
					} catch {
						resolve({});
					}
				});
			},
		);
		req.on("error", () => resolve({}));
		req.end(data);
	});
}

function quote(s: string): string {
	return `'${s.replace(/'/g, `'\\''`)}'`;
}

async function missing(): Promise<string[]> {
	if (!PATHS.length) return [];
	const cmd = PATHS.map((p) => `[ -s ${quote(p)} ] || echo ${quote(p)}`).join("; ");
	const r = await relayExec(cmd);
	return (r.output ?? "").split("\n").map((s) => s.trim()).filter(Boolean);
}

async function gateNeeded(): Promise<boolean> {
	if (!PATHS.length) return false;
	const any = PATHS.map((p) => `[ -s ${quote(p)} ]`).join(" || ");
	const r = await relayExec(`if ${any}; then n=$(wc -l < ${REQ_TABLE} 2>/dev/null || echo 0); [ "$n" -lt 3 ] && echo GATE; fi; true`);
	return (r.output ?? "").includes("GATE");
}

export default function (pi: ExtensionAPI) {
	const start = Date.now();
	const total = STOP_AT_MS > start ? STOP_AT_MS - start : 0;
	let next = 0;
	let gateSent = !GATE_ON;
	let gateCheckedAt = 0;
	pi.on("turn_end", async () => {
		if (!gateSent && Date.now() - gateCheckedAt > GATE_EVERY_MS) {
			gateCheckedAt = Date.now();
			if (await gateNeeded()) {
				gateSent = true;
				console.error("ahpele: phase-guard constraint gate");
				return {entries: [{type: "custom_message", customType: "ahpele-phase-guard", content: GATE, display: false}]};
			}
		}
		if (!total || next >= MARKS.length) return undefined;
		const frac = (Date.now() - start) / total;
		if (frac < MARKS[next]) return undefined;
		while (next < MARKS.length && frac >= MARKS[next]) next++;
		const pct = Math.round(frac * 100);
		const left = Math.max(0, Math.round((STOP_AT_MS - Date.now()) / 60000));
		const absent = await missing();
		let text: string;
		if (absent.length) {
			text =
				`[harness] Time check: ${pct}% of your time is used (about ${left} minutes left). These files named in ` +
				`the instruction do not exist yet (or are empty): ${absent.join(", ")}. If any of them is a deliverable, ` +
				`write a complete first version of it now, then keep improving it in place.`;
		} else if (next >= MARKS.length) {
			text =
				`[harness] Time check: ${pct}% of your time is used (about ${left} minutes left). Finalise now: make sure ` +
				`every deliverable on disk is complete and consistent, run your checks and ` +
				`python3 /tmp/ahpele/bin/ahpele_check.py on them, fix any problem, and keep a valid version on disk at all times.`;
		} else {
			return undefined;
		}
		console.error(`ahpele: phase-guard at ${pct}%: ${absent.length ? "missing " + absent.length : "finalise"}`);
		return {entries: [{type: "custom_message", customType: "ahpele-phase-guard", content: text, display: false}]};
	});
}
