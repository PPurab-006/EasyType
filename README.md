# EasyType Transpiler

EasyType is a V1 implementation of a Domain-Specific Language (DSL) designed for absolute beginners. It allows writing programming logic in plain English syntax, which is then transpiled to valid Python code and executed.

## Usage

You can run an EasyType script (a `.esy` file) via the CLI.

```bash
python easytype.py script.esy
```

### Debug Mode

If you'd like to see the translated Python code before it is executed, you can append the `--debug` flag:

```bash
python easytype.py script.esy --debug
```

## Syntax Rules

EasyType uses a 1-to-1 mapping with Python syntax.

### 1. Comments
* **EasyType:** `* This is a comment *`
* **Python:** `# This is a comment`

### 2. Variables & Printing
* **EasyType:** `kachori equals 15` -> **Python:** `kachori = 15`
* **EasyType:** `type "Hello", kachori` -> **Python:** `print("Hello", kachori)`

### 3. User Input (Type-Safe)
* **EasyType:** `ask "What is your name?"` -> **Python:** `input("What is your name?")`
* **EasyType:** `ask number "Age?"` -> **Python:** `int(input("Age?"))`
* **EasyType:** `ask decimal "Price?"` -> **Python:** `float(input("Price?"))`

### 4. Math Operations
* `plus` -> `+`
* `minus` -> `-`
* `times` -> `*`
* `divided-by` -> `/`
* `power` -> `**`
* `remainder of` -> `%`
* `percent of` -> `* 0.01 *` (e.g., `10 percent of 50` -> `10 * 0.01 * 50`)

### 5. Logic & Control Flow
* `more-than` -> `>`
* `less-than` -> `<`
* `and` -> `and`
* `or` -> `or`
* **EasyType:** `if x more-than 5` -> **Python:** `if x > 5:`
* **EasyType:** `what-if x equals 5` -> **Python:** `elif x == 5:`
* **EasyType:** `else` -> **Python:** `else:`

*(Note: EasyType preserves Python-style indentation, so use whitespace appropriately).*

### 6. Loops
* **EasyType:** `repeat 5 times` -> **Python:** `for _ in range(5):`
* **EasyType:** `repeat while x less-than 10` -> **Python:** `while x < 10:`

### 7. Lists (1-indexed in EasyType)
EasyType handles 1-based indexing to make lists intuitive for beginners.

* **EasyType:** `scores equals list 10, 20, 30` -> **Python:** `scores = [10, 20, 30]`
* **EasyType:** `position 1 in scores` -> **Python:** `scores[0]`
* **EasyType:** `insert 99 at position 2 in scores` -> **Python:** `scores.insert(1, 99)`
* **EasyType:** `remove position 3 from scores` -> **Python:** `scores.pop(2)`
* **EasyType:** `size of scores` -> **Python:** `len(scores)`

## Example
Create a file named `game.esy`:
```text
* Simple Game Logic *
score equals 0
repeat 3 times
    score equals score plus 10
    type "Score is now:", score

if score more-than 20
    type "You win!"
else
    type "Keep trying!"
```

Run it:
```bash
python easytype.py game.esy
```

Output:
```
Score is now: 10
Score is now: 20
Score is now: 30
You win!
```
