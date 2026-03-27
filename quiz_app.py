import tkinter as tk
from tkinter import messagebox, scrolledtext
import random
import re
import os

QUESTION_FILE = r"C:\Users\User\Desktop\Quiz\品管考試題庫.js" 


def load_question_bank(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到題庫檔案：{file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    match = re.search(r'let\s+questionBank\s*=\s*\[(.*)\]\s*;?\s*$', text, re.DOTALL)
    if not match:
        raise ValueError("題庫格式錯誤：找不到 questionBank 陣列")

    content = match.group(1)
    blocks = re.findall(r'\{.*?\}', content, re.DOTALL)

    question_bank = []

    for block in blocks:
        q_match = re.search(r'q\s*:\s*"((?:[^"\\]|\\.)*)"', block, re.DOTALL)
        options_match = re.search(r'options\s*:\s*\[(.*?)\]', block, re.DOTALL)
        answer_match = re.search(r'answer\s*:\s*"([A-D])"', block)

        if not q_match or not options_match or not answer_match:
            continue

        q_text = q_match.group(1)
        options_raw = options_match.group(1)
        answer = answer_match.group(1)

        option_list = re.findall(r'"((?:[^"\\]|\\.)*)"', options_raw, re.DOTALL)

        if len(option_list) != 4:
            continue

        question_bank.append({
            "q": q_text.strip(),
            "options": [opt.strip() for opt in option_list],
            "answer": answer.strip()
        })

    if not question_bank:
        raise ValueError("題庫載入失敗：沒有成功解析任何題目")

    return question_bank


class QuizApp:
    def __init__(self, root, question_bank):
        self.root = root
        self.root.title("品管題庫隨機測驗")
        self.root.geometry("1000x700")

        self.all_questions = question_bank

        if len(self.all_questions) >= 100:
            self.questions = random.sample(self.all_questions, 100)
        else:
            self.questions = random.sample(self.all_questions, len(self.all_questions))
            messagebox.showwarning("提醒", f"題庫不足 100 題，目前只抽出 {len(self.questions)} 題")

        self.total_questions = len(self.questions)
        self.current_index = 0
        self.user_answers = [None] * self.total_questions
        self.selected_option = tk.StringVar(value="")

        self.build_ui()
        self.show_question()

    def build_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=10)

        self.title_label = tk.Label(
            top_frame,
            text="品管題庫測驗",
            font=("Microsoft JhengHei", 20, "bold")
        )
        self.title_label.pack()

        self.progress_label = tk.Label(self.root, text="", font=("Microsoft JhengHei", 12))
        self.progress_label.pack(pady=5)

        self.question_text = tk.Message(
            self.root,
            text="",
            width=900,
            font=("Microsoft JhengHei", 14),
            justify="left"
        )
        self.question_text.pack(padx=20, pady=20, anchor="w")

        self.option_buttons = []
        for value in ["A", "B", "C", "D"]:
            rb = tk.Radiobutton(
                self.root,
                text="",
                variable=self.selected_option,
                value=value,
                font=("Microsoft JhengHei", 13),
                anchor="w",
                justify="left",
                wraplength=900
            )
            rb.pack(fill="x", padx=40, pady=5, anchor="w")
            self.option_buttons.append(rb)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=25)

        self.prev_button = tk.Button(
            btn_frame, text="上一題", width=12,
            font=("Microsoft JhengHei", 12),
            command=self.prev_question
        )
        self.prev_button.grid(row=0, column=0, padx=10)

        self.next_button = tk.Button(
            btn_frame, text="下一題", width=12,
            font=("Microsoft JhengHei", 12),
            command=self.next_question
        )
        self.next_button.grid(row=0, column=1, padx=10)

        self.submit_button = tk.Button(
            btn_frame, text="交卷", width=12,
            font=("Microsoft JhengHei", 12),
            command=self.submit_quiz
        )
        self.submit_button.grid(row=0, column=2, padx=10)

        self.jump_button = tk.Button(
            btn_frame, text="跳到題號", width=12,
            font=("Microsoft JhengHei", 12),
            command=self.jump_to_question
        )
        self.jump_button.grid(row=0, column=3, padx=10)

        jump_frame = tk.Frame(self.root)
        jump_frame.pack()

        tk.Label(jump_frame, text="題號：", font=("Microsoft JhengHei", 11)).pack(side="left")
        self.jump_entry = tk.Entry(jump_frame, width=8, font=("Microsoft JhengHei", 11))
        self.jump_entry.pack(side="left", padx=5)

        self.answer_status_label = tk.Label(self.root, text="", font=("Microsoft JhengHei", 11))
        self.answer_status_label.pack(pady=10)

    def save_current_answer(self):
        ans = self.selected_option.get().strip()
        self.user_answers[self.current_index] = ans if ans else None

    def show_question(self):
        q = self.questions[self.current_index]

        self.progress_label.config(
            text=f"第 {self.current_index + 1} / {self.total_questions} 題"
        )

        self.question_text.config(text=q["q"])

        for i, opt in enumerate(q["options"]):
            self.option_buttons[i].config(text=opt)

        old_answer = self.user_answers[self.current_index]
        self.selected_option.set(old_answer if old_answer else "")

        answered_count = sum(1 for x in self.user_answers if x is not None)
        self.answer_status_label.config(
            text=f"目前已作答：{answered_count} / {self.total_questions}"
        )

    def prev_question(self):
        self.save_current_answer()
        if self.current_index > 0:
            self.current_index -= 1
            self.show_question()

    def next_question(self):
        self.save_current_answer()
        if self.current_index < self.total_questions - 1:
            self.current_index += 1
            self.show_question()

    def jump_to_question(self):
        self.save_current_answer()
        value = self.jump_entry.get().strip()

        if not value.isdigit():
            messagebox.showerror("錯誤", "請輸入數字題號")
            return

        num = int(value)
        if num < 1 or num > self.total_questions:
            messagebox.showerror("錯誤", f"題號必須介於 1 到 {self.total_questions}")
            return

        self.current_index = num - 1
        self.show_question()

    def submit_quiz(self):
        self.save_current_answer()

        unanswered = [i + 1 for i, ans in enumerate(self.user_answers) if ans is None]
        if unanswered:
            confirm = messagebox.askyesno(
                "尚未作答",
                f"還有 {len(unanswered)} 題未作答，確定要交卷？"
            )
            if not confirm:
                return

        score, correct_count, wrong_details = self.calculate_result()
        self.show_result(score, correct_count, wrong_details)

    def calculate_result(self):
        correct_count = 0
        wrong_details = []

        for i, q in enumerate(self.questions):
            correct_answer = q["answer"]
            user_answer = self.user_answers[i]

            if user_answer == correct_answer:
                correct_count += 1
            else:
                wrong_details.append({
                    "index": i + 1,
                    "question": q["q"],
                    "options": q["options"],
                    "correct": correct_answer,
                    "user": user_answer if user_answer else "未作答"
                })

        score = round(correct_count / self.total_questions * 100, 2)
        return score, correct_count, wrong_details

    def show_result(self, score, correct_count, wrong_details):
        result_window = tk.Toplevel(self.root)
        result_window.title("測驗結果")
        result_window.geometry("1000x700")

        summary = (
            f"總題數：{self.total_questions}\n"
            f"答對題數：{correct_count}\n"
            f"答錯題數：{self.total_questions - correct_count}\n"
            f"分數：{score}"
        )

        tk.Label(
            result_window,
            text="測驗結果",
            font=("Microsoft JhengHei", 18, "bold")
        ).pack(pady=10)

        tk.Label(
            result_window,
            text=summary,
            font=("Microsoft JhengHei", 13),
            justify="left"
        ).pack(pady=10)

        text_area = scrolledtext.ScrolledText(
            result_window,
            wrap=tk.WORD,
            font=("Microsoft JhengHei", 11)
        )
        text_area.pack(fill="both", expand=True, padx=15, pady=15)

        if not wrong_details:
            text_area.insert(tk.END, "全部答對\n")
        else:
            for item in wrong_details:
                text_area.insert(tk.END, f"第 {item['index']} 題\n")
                text_area.insert(tk.END, f"題目：{item['question']}\n")
                for opt in item["options"]:
                    text_area.insert(tk.END, f"{opt}\n")
                text_area.insert(tk.END, f"你的答案：{item['user']}\n")
                text_area.insert(tk.END, f"正確答案：{item['correct']}\n")
                text_area.insert(tk.END, "-" * 60 + "\n")

        text_area.config(state="disabled")


def main():
    try:
        question_bank = load_question_bank(QUESTION_FILE)
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("載入失敗", str(e))
        return

    root = tk.Tk()
    app = QuizApp(root, question_bank)
    root.mainloop()


if __name__ == "__main__":
    main()