import { readFileSync } from "fs";
import path from "path";

/** Return a personalised greeting. */
function greet(name) {
    return `Hello, ${name}!`;
}

function process(data, verbose = false) {
    const result = greet("world");
    return { processed: result, count: data.length };
}

/** Simple calculator with basic arithmetic. */
class Calculator {
    /** Return the sum of a and b. */
    add(a, b) {
        return a + b;
    }

    subtract(a, b) {
        return a - b;
    }

    compute(x) {
        return this.add(x, 1);
    }
}
