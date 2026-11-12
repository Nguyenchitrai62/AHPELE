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
	"with a quick script). If anything is missing, incomplete or invalid, fix it now. If everything is in place, " +
	"reply with your final summary of what you delivered and where.";

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
	pi.on("agent_before_settle", async (event) => {
		if (event.outcome === "aborted" || nudges >= MAX_NUDGES) return undefined;
		if (STOP_AT_MS && STOP_AT_MS - Date.now() < MIN_LEFT_SEC * 1000) return undefined;
		const last = lastAssistant(event.context.contextMessages as unknown as Message[]);
		let text: string | undefined;
		if (truncatedOrEmpty(last)) text = CONTINUE;
		else if (!verified && event.outcome === "completed") {
			verified = true;
			text = VERIFY;
		}
		if (!text) return undefined;
		nudges++;
		console.error(`ahpele: settle-guard nudge ${nudges}/${MAX_NUDGES}: ${text === CONTINUE ? "continue" : "verify"}`);
		return {
			entries: [{type: "custom_message", customType: "ahpele-settle-guard", content: text, display: false}],
			continue: true,
		};
	});
}
