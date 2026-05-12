import java.util.List;
import java.util.Map;
import java.util.HashMap;

/**
 * Sample Java class for AST parser tests.
 */
public class Sample {

    /**
     * Return a personalised greeting.
     */
    public static String greet(String name) {
        return "Hello, " + name + "!";
    }

    public static Map<String, Object> process(List<String> data, boolean verbose) {
        String result = greet("world");
        Map<String, Object> out = new HashMap<>();
        out.put("processed", result);
        out.put("count", data.size());
        return out;
    }

    /**
     * Simple calculator with basic arithmetic.
     */
    static class Calculator {

        /**
         * Return the sum of a and b.
         */
        public int add(int a, int b) {
            return a + b;
        }

        public int subtract(int a, int b) {
            return a - b;
        }
    }
}
