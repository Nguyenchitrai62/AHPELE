/**
 * AHPELE settle guard (pi extension).
 *
 * Pi ends a run when the model's turn contains no tool call. That also happens
 * when a turn is cut off at max_tokens while still reasoning (no text, no tool
 * call) or comes back empty, which ended a task with hours left and no
 * deliverable written. At `agent_before_settle` this extension can append one
 * message and ask for one more model request:
 *
 *   (a) the last turn was truncated or empty  -> tell the agent to continue;
 *   (b) the agent is finishing normally       -> once, ask it to verify that
 *       every deliverable the instruction names exists and is complete.
 *
 * Nudges are generic (never task-specific), capped per task, and skipped when
 * the run was aborted or less than MIN_LEFT_SEC remain before the harness stops pi.
 */
import type {ExtensionAPI} from '@earendil-works/pi-coding-agent';

const MAX_NUDGES = Number(process.env.AHPELE_MAX_NUDGES ?? "6");
const STOP_AT_MS = Number(process.env.AHPELE_STOP_AT_EPOCH ?? "0") * 1000;
const MIN_LEFT_SEC = 300;

const CONTINUE =
	"[harness] Your previous response was cut off or empty, so nothing was done in that turn. Continue the task " +
	"from where you were. Keep your reasoning brief and act through tools. If the deliverable files the instruction " +
	"asks for do not exist yet, write a complete first version of them now, then keep improving them.";

const VERIFY =
	"[harness] Before you finish: check that every deliverable file the instruction asks for exists at the exact " +
	"path and in the exact format it specifies, and that it is complete (list the files and validate their contents " +
	"with a quick script, and with python3 /tmp/ahpele/bin/ahpele_check.py <paths> when it exists), and that every hard requirement is met " +
	"(python3 /tmp/ahpele/bin/ahpele_reqscan.py --check, when it exists, lists requirement candidates you never " +
	"reviewed). If anything is " +
	"missing, incomplete or invalid, fix it now. If everything is in place, " +
	"reply with your final summary of what you delivered and where.";

// AHPELE RC-0011: agents often declare completion with much of their time left.
// While more than REVIEW_MIN_LEFT of the time remains, a normal finish gets a
// review pass first (at most MAX_REVIEWS). AHPELE_REVIEW=0 disables it.
const REVIEW_ON = (process.env.AHPELE_REVIEW ?? "1") !== "0";
const REVIEW_MIN_LEFT = 0.4;
const MAX_REVIEWS = 2;
const START_MS = Date.now();
function review(minutesLeft: number, pctLeft: number): string {
	return (
		`[harness] You still have about ${minutesLeft} minutes (${pctLeft}% of your time). Use it before finishing: ` +
		"do an independent review pass of your work. Re-read the instruction and your checklist line by line and confirm " +
		"each item is satisfied in the files on disk. Re-check every hard requirement (limits, codes, permits, capacities, " +
		"deadlines, document status) against your numbers with a script; run python3 /tmp/ahpele/bin/ahpele_reqscan.py " +
			"--check if it exists and resolve every unreviewed candidate; and look for anything you have not examined: " +
		"documents you skimmed, conditions you assumed were met, conflicts between documents, dates and deadlines, items " +
		"that need someone to act. If the task asks whether anything stands in the way, check every requirement and every " +
		"record for issues before concluding there are none. Fix what you find, improve the weakest part of the " +
		"deliverable, re-run your checks, then give your final summary."
	);
}

type Block = {type: string; text?: string};
type Message = {role: string; content?: unknown; stopReason?: string};

function lastAssistant(messages: Message[]): Message | undefined {
	for (let i = messages.length - 1; i >= 0; i--) if (messages[i]?.role === "assistant") return messages[i];
	return undefined;
}

function truncatedOrEmpty(m: Message | undefined): boolean {
	if (!m) return false;
	if (m.stopReason === "length") return true;
	const blocks = Array.isArray(m.content) ? (m.content as Block[]) : [];
	const text = blocks.filter((b) => b.type === "text").map((b) => b.text ?? "").join("").trim();
	const toolCalls = blocks.filter((b) => b.type === "toolCall").length;
	return !text && toolCalls === 0;
}

export default function (pi: ExtensionAPI) {
	let nudges = 0;
	let verified = false;
	let reviews = 0;
	pi.on("agent_before_settle", async (event) => {
		if (event.outcome === "aborted" || nudges >= MAX_NUDGES) return undefined;
		if (STOP_AT_MS && STOP_AT_MS - Date.now() < MIN_LEFT_SEC * 1000) return undefined;
		const last = lastAssistant(event.context.contextMessages as unknown as Message[]);
		let text: string | undefined;
		const total = STOP_AT_MS > START_MS ? STOP_AT_MS - START_MS : 0;
		const leftFrac = total ? (STOP_AT_MS - Date.now()) / total : 0;
		if (truncatedOrEmpty(last)) text = CONTINUE;
		else if (event.outcome === "completed" && REVIEW_ON && reviews < MAX_REVIEWS && leftFrac > REVIEW_MIN_LEFT) {
			reviews++;
			text = review(Math.round((STOP_AT_MS - Date.now()) / 60000), Math.round(leftFrac * 100));
		} else if (!verified && event.outcome === "completed") {
			verified = true;
			text = VERIFY;
		}
		if (!text) return undefined;
		nudges++;
		console.error(`ahpele: settle-guard nudge ${nudges}/${MAX_NUDGES}: ${text === CONTINUE ? "continue" : text === VERIFY ? "verify" : "review"}`);
		return {
			entries: [{type: "custom_message", customType: "ahpele-settle-guard", content: text, display: false}],
			continue: true,
		};
	});
}
