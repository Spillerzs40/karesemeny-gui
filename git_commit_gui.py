import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import subprocess

class CommitMessageBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("Commit & Push Builder – Angol & Magyar")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        # Commit típus kiválasztása
        ttk.Label(root, text="Commit típus:", font=("Segoe UI", 10, "bold")).pack(pady=5)
        self.commit_type = ttk.Combobox(root, values=["feat", "fix", "docs", "chore", "release"], state="readonly")
        self.commit_type.current(0)
        self.commit_type.pack(pady=5)

        # Angol üzenet
        ttk.Label(root, text="Message (EN):", font=("Segoe UI", 10, "bold")).pack(pady=5)
        self.en_text = tk.Text(root, height=4, width=80)
        self.en_text.pack(pady=5)

        # Magyar üzenet
        ttk.Label(root, text="Üzenet (HU):", font=("Segoe UI", 10, "bold")).pack(pady=5)
        self.hu_text = tk.Text(root, height=4, width=80)
        self.hu_text.pack(pady=5)

        # Gombok
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="📋 Másolás vágólapra", command=self.copy_to_clipboard).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✅ Commit Git-be", command=self.commit_to_git).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🚀 Push GitHub-ra", command=self.push_to_github).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="❌ Kilépés", command=root.destroy).pack(side="left", padx=5)

    def build_commit_message(self):
        commit_type = self.commit_type.get()
        en_msg = self.en_text.get("1.0", "end").strip()
        hu_msg = self.hu_text.get("1.0", "end").strip()
        if not en_msg or not hu_msg:
            messagebox.showwarning("Hiányzó üzenet", "Kérlek töltsd ki az angol és magyar üzenetet is!")
            return None
        return f"{commit_type}: {en_msg}\n{commit_type}: {hu_msg}"

    def copy_to_clipboard(self):
        final_msg = self.build_commit_message()
        if final_msg:
            pyperclip.copy(final_msg)
            messagebox.showinfo("Másolva", "A commit üzenet a vágólapra másolva!")

    def commit_to_git(self):
        final_msg = self.build_commit_message()
        if not final_msg:
            return
        try:
            result = subprocess.run(['git', 'commit', '-m', final_msg], capture_output=True, text=True)
            if result.returncode == 0:
                messagebox.showinfo("Siker", f"Commit sikeres!\n\n{result.stdout}")
            else:
                messagebox.showerror("Hiba", f"A commit sikertelen!\n\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Hiba", f"Hiba történt a commit során: {e}")

    def push_to_github(self):
        try:
            result = subprocess.run(['git', 'push'], capture_output=True, text=True)
            if result.returncode == 0:
                messagebox.showinfo("Siker", f"Push sikeres!\n\n{result.stdout}")
            else:
                messagebox.showerror("Hiba", f"A push sikertelen!\n\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Hiba", f"Hiba történt a push során: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CommitMessageBuilder(root)
    root.mainloop()