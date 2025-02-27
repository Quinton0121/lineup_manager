

import tkinter as tk
import intake_interview

#import subprocess
# def run_script():
#     subprocess.run(["python3", "intake_interview.py"])


def run_script():
    intake_interview.main()

def run_function():
    intake_interview.reset()

def submit_input():
    input_value = entry.get()
    intake_interview.change_lineup_no(int(input_value))



root = tk.Tk()
root.title("Run Script")

# logo = tk.PhotoImage(file="Logo.png")
# logo_label = tk.Label(root, image=logo)
# logo_label.pack(side="right", anchor="n")


label = tk.Label(root, text="Run Script")
label.place(relx=0.5, rely=0.3, anchor="center")

run_button = tk.Button(root, text="Run", command=run_script)
run_button.place(relx=0.5, rely=0.5, anchor="center")
#run_button.pack(pady=root.winfo_height() * 0.45)

entry = tk.Entry(root)
entry.place(relx=0.5, rely=0.12, anchor="center")

reset_button = tk.Button(root, text="Reset", command=run_function)
reset_button.place(relx=0.5, rely=0.8, anchor="center")


submit_button = tk.Button(root, text="Submit", command=submit_input)
submit_button.place(relx=0.5, rely=0.10, anchor="center")








root.mainloop()