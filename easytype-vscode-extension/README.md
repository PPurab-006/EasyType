# EasyType VS Code Extension

This is the official Visual Studio Code and Antigravity IDE extension for EasyType, a beginner-friendly English-syntax language that transpiles to Python.

## Features

- **Syntax Highlighting**: Full highlighting for EasyType keywords, operators, and types.
- **Run Button**: A convenient play button in the editor title bar to quickly run your `.esy` scripts.
- **Diagnostics**: Real-time error checking for common typos like unmatched quotes or variable name collisions with keywords.
- **Auto-formatting**: Proper indentation auto-completion for `if`, `repeat`, and `else` blocks.

## Usage

1. Create a file with a `.esy` extension.
2. Write some EasyType code:
   ```easytype
   * This is a simple game *
   score equals 10
   repeat 5 times
       score equals score plus 5
       type "Your score is:", score
   ```
3. Click the Play button in the top right, or run `EasyType: Run File` from the Command Palette!

## Bundled Transpiler

This extension comes bundled with the `easytype.py` transpiler out of the box, meaning it works immediately with zero configuration required.
