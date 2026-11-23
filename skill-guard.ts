/**
 * AHPELE skill guard (pi extension, RC-0039).
 *
 * The bundled skills are listed in the system prompt and the agent chooses
 * among them. Agents sometimes start designing without opening any. This
 * extension watches which SKILL.md files are opened (read tool or a shell
 * command) and, at two fixed points in the run, reminds an agent that has
 * neither opened one nor recorded its choice in /tmp/ahpele/skills.md. It never
 * suggests a particular skill, and "none fits" is a valid choice: the skills are
 * general references, not instructions for any task. AHPELE_SKILL_GUARD=0
 * disables it.
 */
import type {ExtensionAPI} from '@earendil-works/pi-coding-agent';
import http from 'node:http';

const RELAY = process.env.TASK_RELAY_URL ?? "";
const ON = (process.env.AHPELE_SKILL_GUARD ?? "1") !== "0";
const CHOICE_FILE = "/tmp/ahpele/skills.md";
const REMIND_AT_TURNS = [8, 25];
const OPEN_RE = /([a-z0-9*-]+)\/SKILL\.md/g;
const READS = /\b(cat|sed|less|more|awk|python3?)\b|\b(head|tail)\b[^|;&]*SKILL\.md/;

const REMINDER =
	"[harness] You have not opened any skill (they are listed in your instructions) and " + CHOICE_FILE + " does not " +
	"exist. Before you plan or design further, consider each part of this work and decide whether a listed skill " +
	"covers it. Read the SKILL.md of every one that does, and write " + CHOICE_FILE + " with, for each, the part of " +
	"the work it is for; if none fits, write that and why. Use a skill only where it fits: the project documents " +
	"always prevail, and an unrelated skill is worse than none. Then continue.";

function choiceRecorded(): Promise<boolean> {
	return new Promise((resolve) => {
		if (!RELAY) return resolve(true);
		const url = new URL(`${RELAY}/exec`);
		const data = Buffer.from(JSON.stringify({command: `[ -s ${CHOICE_FILE} ] && echo YES; true`, timeout_sec: 30}));
		const req = http.request(
			{hostname: url.hostname, port: url.port, path: url.pathname, method: "POST",
			 headers: {"Content-Type": "application/json", "Content-Length": data.length}},
			(res) => {
				const chunks: Buffer[] = [];
				res.on("data", (c) => chunks.push(c));
				res.on("end", () => {
					if (res.statusCode !== 200) return resolve(true); // when the state is unknown, do not nag
					try {
						resolve((JSON.parse(Buffer.concat(chunks).toString() || "{}").output ?? "").includes("YES"));
					} catch {
						resolve(true);
					}
				});
			},
		);
		req.on("error", () => resolve(true));
		req.setTimeout(40_000, () => req.destroy());
		req.end(data);
	});
}

export default function (pi: ExtensionAPI) {
	if (!ON) return;
	const opened = new Set<string>();
	let turns = 0;
	let next = 0;
	pi.on("tool_execution_start", async (event) => {
		// reading is the read tool, or a shell command that prints the file; listing or searching does not count
		const args = (event.args ?? {}) as Record<string, unknown>;
		const text = event.toolName === "read" ? String(args.path ?? args.file_path ?? "")
			: event.toolName === "bash" ? String(args.command ?? "") : "";
		if (!text.includes("skills") || (event.toolName === "bash" && !READS.test(text))) return;
		for (const m of text.matchAll(OPEN_RE)) {
			if (!opened.has(m[1])) {
				opened.add(m[1]);
				console.error(`ahpele: skill-guard opened ${m[1]}`);
			}
		}
	});
	pi.on("turn_end", async (event) => {
		turns++;
		if (next >= REMIND_AT_TURNS.length || turns < REMIND_AT_TURNS[next]) return undefined;
		next++;
		if (opened.size || (await choiceRecorded())) return undefined;
		console.error(`ahpele: skill-guard reminder ${next}/${REMIND_AT_TURNS.length} at turn ${turns}`);
		return {entries: [...event.entries, {type: "custom_message", customType: "ahpele-skill-guard", content: REMINDER, display: false}]};
	});
}
