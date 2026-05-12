import { readFileSync } from "fs";
import path from "path";

/** Return a personalised greeting. */
function greet(name: string): string {
    return `Hello, ${name}!`;
}

function process(data: string[], verbose: boolean = false): Record<string, unknown> {
    const result = greet("world");
    return { processed: result, count: data.length };
}

/** Simple calculator with basic arithmetic. */
class Calculator {
    /** Return the sum of a and b. */
    add(a: number, b: number): number {
        return a + b;
    }

    subtract(a: number, b: number): number {
        return a - b;
    }

    compute(x: number): number {
        return this.add(x, 1);
    }
}
