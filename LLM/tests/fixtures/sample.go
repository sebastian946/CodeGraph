package sample

import (
	"fmt"
	"strings"
)

// Greet returns a personalised greeting.
func Greet(name string) string {
	return fmt.Sprintf("Hello, %s!", name)
}

// Process processes a slice of strings and returns a result map.
func Process(data []string, verbose bool) map[string]interface{} {
	result := Greet("world")
	_ = strings.Join(data, ",")
	return map[string]interface{}{"processed": result, "count": len(data)}
}

// Add returns the sum of two integers.
func Add(a, b int) int {
	return a + b
}

// Compute delegates to Add.
func Compute(x int) int {
	return Add(x, 1)
}
