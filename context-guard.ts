/**
 * AHPELE context guard (pi extension).
 *
 * Before each model call, keep image blocks only in the most recent
 * KEEP_IMAGE_MESSAGES messages that carry images; replace every older image
 * block with a short text note naming the file it came from. Pi's `context`
 * event changes only what is sent to the model, never the stored conversation.
 *
 * Why: every image the agent has read is otherwise re-sent on every turn, so
 * requests grow without bound (6.6 MB after ~30 minutes on a task full of
 * scanned PDFs), latency climbs to minutes and providers start dropping the
 * connection. With Claude it also multiplies cost. The replacement is
 * deterministic, so an image that has aged out produces the same text on every
 * later turn and the prompt-cache prefix stays stable after that point.
 */
import type {ExtensionAPI} from '@earendil-works/pi-coding-agent';

const KEEP_IMAGE_MESSAGES = Number(process.env.AHPELE_KEEP_IMAGE_MESSAGES ?? "2");

type Block = {type: string; [key: string]: unknown};
type Message = {role: string; content?: unknown; toolCallId?: string; [key: string]: unknown};

function hasImage(message: Message): boolean {
	return Array.isArray(message.content) && (message.content as Block[]).some((b) => b?.type === "image");
}

/** Maps tool-call ids to the file path they read, from assistant tool calls. */
function readPaths(messages: Message[]): Map<string, string> {
	const paths = new Map<string, string>();
	for (const m of messages) {
		if (m.role !== "assistant" || !Array.isArray(m.content)) continue;
		for (const b of m.content as Block[]) {
			if (b?.type !== "toolCall") continue;
			const args = (b.arguments ?? {}) as Record<string, unknown>;
			const p = args.path ?? args.file_path ?? args.file;
			if (typeof p === "string" && typeof b.id === "string") paths.set(b.id, p);
		}
	}
	return paths;
}

function note(path: string | undefined): Block {
	const where = path ? ` (${path})` : "";
	return {
		type: "text",
		text:
			`[image${where} omitted from context to save space. Re-read the file if you need to see it again;` +
			` write down what you learn from images in your notes.]`,
	};
}

export default function (pi: ExtensionAPI) {
	pi.on("context", async (event) => {
		const messages = event.messages as unknown as Message[];
		const withImages: number[] = [];
		messages.forEach((m, i) => {
			if (hasImage(m)) withImages.push(i);
		});
		if (withImages.length <= KEEP_IMAGE_MESSAGES) return undefined;
		const prune = new Set(withImages.slice(0, withImages.length - KEEP_IMAGE_MESSAGES));
		const paths = readPaths(messages);
		const out = messages.map((m, i) => {
			if (!prune.has(i)) return m;
			const path = m.toolCallId ? paths.get(m.toolCallId) : undefined;
			const content = (m.content as Block[]).map((b) => (b?.type === "image" ? note(path) : b));
			return {...m, content};
		});
		return {messages: out as unknown as typeof event.messages};
	});
}
