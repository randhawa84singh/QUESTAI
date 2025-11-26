import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests


MODEL = os.environ.get("OLLAMA_MODEL", "llama3")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
HISTORY_PATH = Path("quiz_history.json")


class OllamaError(Exception):
    pass


def call_ollama(messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "temperature": temperature,
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=90)
    except requests.RequestException as exc:  # type: ignore[reportGeneralTypeIssues]
        raise OllamaError(f"Failed to reach Ollama API: {exc}") from exc

    if response.status_code != 200:
        raise OllamaError(f"Ollama API returned status {response.status_code}: {response.text}")

    data = response.json()
    message = data.get("message") or {}
    content = message.get("content")
    if not content:
        raise OllamaError("Empty response content from Ollama API")
    return content.strip()


def load_history() -> List[Dict[str, Any]]:
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text())
        except json.JSONDecodeError:
            print("History file was corrupt. Starting with an empty history.")
            return []
    return []


def save_history(history: List[Dict[str, Any]]) -> None:
    HISTORY_PATH.write_text(json.dumps(history, indent=2))


def format_history_context(history: List[Dict[str, Any]], limit: int = 8) -> str:
    if not history:
        return ""
    recent = history[-limit:]
    lines = []
    for item in recent:
        question = item.get("question", "")
        answer = item.get("answer", "")
        feedback = item.get("explanation", "")
        correctness = "correct" if item.get("is_correct") else "incorrect"
        lines.append(
            f"Q: {question}\nA: {answer}\nResult: {correctness}. Explanation: {feedback}"
        )
    return "\n\n".join(lines)


def generate_question(name: str, subject: str, difficulty: str, history: List[Dict[str, Any]]) -> str:
    history_context = format_history_context(history)
    system_prompt = (
        "You are QuestAI, a friendly adaptive quiz tutor. Generate one clear, concise, open-ended "
        "question for the user based on the requested subject and difficulty. The question should "
        "be answerable in a short sentence or calculation and should not include the answer."
    )

    user_prompt_lines = [
        f"Learner name: {name}",
        f"Subject: {subject}",
        f"Difficulty: {difficulty}",
        "Prior attempts: " + (history_context if history_context else "None yet."),
        "Respond strictly as JSON with the shape: {\"question\": \"...\"}.",
    ]
    user_prompt = "\n".join(user_prompt_lines)
    content = call_ollama(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    try:
        parsed = json.loads(content)
        question = parsed.get("question")
        if not question:
            raise ValueError
        return question
    except Exception:
        # Fall back to raw text if parsing fails
        return content


def check_answer(question: str, answer: str) -> Dict[str, Any]:
    system_prompt = (
        "You are a concise grader. Given a question and a learner's answer, judge correctness. "
        "Respond as compact JSON with keys: is_correct (true/false) and explanation (1-3 sentences)."
    )
    user_prompt = json.dumps({"question": question, "answer": answer})
    content = call_ollama(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    try:
        parsed = json.loads(content)
        is_correct = bool(parsed.get("is_correct"))
        explanation = parsed.get("explanation") or ""
    except Exception:
        is_correct = "correct" in content.lower()
        explanation = content
    return {"is_correct": is_correct, "explanation": explanation}


def show_summary(history: List[Dict[str, Any]]) -> None:
    if not history:
        print("No attempts yet.")
        return
    total = len(history)
    correct = sum(1 for item in history if item.get("is_correct"))
    print("\n=== Quiz Summary ===")
    print(f"Questions answered: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {correct/total:.1%}")
    print("Last few:")
    for item in history[-5:]:
        status = "✅" if item.get("is_correct") else "❌"
        print(f" {status} {item.get('question')}")
    print("====================\n")


def main() -> None:
    print("Welcome to QuestAI CLI Quiz! (Powered by Ollama)")
    name = input("Your name: ").strip() or "Learner"
    subject = input("Subject to practice: ").strip() or "General knowledge"
    difficulty = input("Difficulty (e.g., easy, medium, hard): ").strip() or "medium"

    history = load_history()
    print("\nCommands: n = next question, s = summary and exit, q = quit immediately.\n")

    while True:
        command = input("Enter command [n/s/q]: ").strip().lower()
        if command == "q":
            print("Goodbye!")
            break
        if command == "s":
            show_summary(history)
            break
        if command != "n":
            print("Please choose 'n', 's', or 'q'.")
            continue

        try:
            question = generate_question(name, subject, difficulty, history)
        except OllamaError as exc:
            print(f"Could not generate question: {exc}")
            continue

        print(f"\nQuestion: {question}\n")
        answer = input("Your answer (or type 'q' to quit): ").strip()
        if answer.lower() == "q":
            print("Goodbye!")
            break

        try:
            result = check_answer(question, answer)
        except OllamaError as exc:
            print(f"Could not grade answer: {exc}")
            continue

        is_correct = result.get("is_correct")
        explanation = result.get("explanation")
        status = "✅ Correct!" if is_correct else "❌ Not quite."
        print(f"{status} Explanation: {explanation}\n")

        history.append(
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "name": name,
                "subject": subject,
                "difficulty": difficulty,
                "question": question,
                "answer": answer,
                "is_correct": is_correct,
                "explanation": explanation,
            }
        )
        save_history(history)

    save_history(history)


if __name__ == "__main__":
    main()
