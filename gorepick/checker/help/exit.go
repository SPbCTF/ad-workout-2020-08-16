package help

import (
	"fmt"
	"os"
)

type ExitCode int

const (
	OK            ExitCode = 101
	CORRUPT                = 102
	MUMBLE                 = 103
	DOWN                   = 104
	CHECKER_ERROR          = 110
)

func Exit(code ExitCode, public string, private string) {
	if public != "" {
		fmt.Println(public)
	}

	if private != "" {
		_, _ = fmt.Fprintln(os.Stderr, private)
	}

	os.Exit(int(code))
}
