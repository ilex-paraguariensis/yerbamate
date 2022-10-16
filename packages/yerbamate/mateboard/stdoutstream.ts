
import EventEmitter from "https://deno.land/std@0.79.0/node/events.ts";
export class stdOutStream extends EventEmitter {
		cwd:string;
    constructor(cwd:string=".") {
        super();
				this.cwd = cwd;
    }
    public async run(...command: Array<string>): Promise<void> {
        const p = Deno.run({
            cmd: command,
						cwd: this.cwd,
            stdout: "piped",
						stderr: "piped",
        });
				const textDecoder = new TextDecoder();
        for await (const rawLine of readableStreamFromReader(p.stdout)) {
						const line = textDecoder.decode(rawLine);
            if (line.trim()) super.emit("stdout", line);
        }
        for await (const rawLine of readableStreamFromReader(p.stderr)) {
						const line = textDecoder.decode(rawLine);
            if (line.trim()) super.emit("stderr", line);
        }
        super.emit('end', await p.status());
        p.close();
        return;
    }
}
