import json
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mbox


class Task:
    
    def __init__(self, name, description, priority, due_date):
        self.name = name
        self.description = description
        self.priority = priority
        self.due_date = due_date

        
    def to_dict(self):
        return {"name": self.name, "description": self.description, "priority": self.priority, "due_date": self.due_date}


class TaskManager:
    
    def __init__(self, json_file="tasks.json"):
        self.json_file = json_file 
        self.tasks = [] 
        self.current_key = "" 
        self.ascending = True 
        self.load_tasks_from_json()

        
    # load tasks from JSON file
    def load_tasks_from_json(self):
        try:
            with open(self.json_file, "r") as file:
                try:
                    tasks = json.load(file)
                    for task in tasks:
                        self.tasks.append(Task(task["name"], task["description"], task["priority"], task["due_date"]))
                except json.JSONDecodeError:
                    print("Error! The fle is not in a valid JSON format.")
        except FileNotFoundError:
            pass


    def save_tasks_to_json(self):
        try:
            with open(self.json_file,"w") as file:
                json.dump([task.to_dict() for task in self.tasks], file, indent = 2)
        except IOError:
            print("Error!Couldnt find file.")
        
        

    def get_filtered_task(self, name_filter=None, priority_filter=None, due_date_filter=None):
        filtered_tasks=self.tasks
        if name_filter:
            filtered_tasks = [task for task in filtered_tasks if name_filter.lower() in task.name.lower()]
        if priority_filter:
            filtered_tasks = [task for task in filtered_tasks if priority_filter.lower() == task.priority.lower()]
        if due_date_filter:
            filtered_tasks = [task for task in filtered_tasks if due_date_filter == task.due_date]
        return filtered_tasks
    

   
    def sort_tasks(self, sort_key='name'):
        if self.current_key == sort_key:
            self.ascending = not self.ascending 
        else:
            self.ascending= True
        self.current_key = sort_key

        if sort_key == "name":
            if self.ascending:
                self.tasks.sort(key=lambda task: task.name.lower())
            else:
                self.tasks.sort(key=lambda task: task.name.lower(),reverse=True)
        elif sort_key == "description":
            if self.ascending:
                self.tasks.sort(key=lambda task: task.description.lower())
            else:
                self.tasks.sort(key=lambda task: task.description.lower(),reverse=True)
        elif sort_key == "priority":
            priority_ranking = {"High":1,"Medium":2,"Low":3}
            if self.ascending:
                self.tasks.sort(key=lambda task: priority_ranking.get(task.priority,4))
            else:
                self.tasks.sort(key=lambda task: priority_ranking.get(task.priority,4),reverse=True)

        elif sort_key == "due_date":
            if self.ascending:
                self.tasks.sort(key=lambda task: task.due_date)
            else:
                self.tasks.sort(key=lambda task: task.due_date,reverse=True)
        return self.tasks
            
        

class TaskManagerGUI:
    
    def __init__(self,root):
        self.root = root
        self.root.title("Personal Task Manager")
        self.task_manager = TaskManager()
        self.setup_gui()
        

    def setup_gui(self):
        frame = tk.Frame(self.root, relief = "sunken", borderwidth=2)
        frame.pack(padx=10, pady=10)

        label_name = tk.Label(frame, text="Name:", font=("Times New Roman", 10))
        label_name.grid(row=0, column=0, padx=(20,0))
        self.name_entry=tk.Entry(frame)
        self.name_entry.grid(row=0, column=1)

        label_priority = tk.Label(frame, text="Priority:", font=("Times New Roman", 10))
        label_priority.grid(row=0, column=2, padx=(20,0))
        priority_choices = ["Low", "Medium", "High"]
        self.priority_drop_down = ttk.Combobox(frame, values = priority_choices)
        self.priority_drop_down.grid(row=0, column=3)

        label_due_date = tk.Label(frame, text="Due Date (DD/MM/YYYY):", font=("Times New Roman", 10))
        label_due_date.grid(row=0, column=4, padx=(20,0))
        self.due_date_entry=tk.Entry(frame)
        self.due_date_entry.grid(row=0, column=5)

        filter_button = tk.Button(frame, text="Filter", command=self.apply_filter, font=("Arial", 10, "bold"), relief="raised", bd=3, activebackground="black", activeforeground="white")
        filter_button.grid(row=0, column=6, padx=25)

        self.tree = ttk.Treeview(self.root, show="headings")
        self.tree['columns'] = ("Name", "Description", "Priority", "Due Date")

        self.tree.column("Name", width=150, minwidth=100)
        self.tree.column("Description", width=250, minwidth=150)
        self.tree.column("Priority", width=100, minwidth=80)
        self.tree.column("Due Date", width=120, minwidth=100)

        self.tree.heading("Name", text="Name", command=lambda:self.sort_tasks("name"))
        self.tree.heading("Description", text="Description", command=lambda:self.sort_tasks("description"))
        self.tree.heading("Priority", text="Priority", command=lambda:self.sort_tasks("priority"))
        self.tree.heading("Due Date", text="Due Date", command=lambda:self.sort_tasks("due_date"))

        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        lower_frame = tk.Frame(self.root, relief="groove", borderwidth = 3)
        lower_frame.pack(pady=(0,30))

        add_task_button = tk.Button(lower_frame, text="Add Task", command=self.add_task)
        add_task_button.pack(side="left",padx=5)
        update_task_button = tk.Button(lower_frame, text="Update Task", command=self.update_task)
        update_task_button.pack(side="left")
        delete_task_button = tk.Button(lower_frame, text="Delete Task", command=self.delete_task)
        delete_task_button.pack(side="right", padx=5)
         
        self.populate_tree()


    def populate_tree(self):
        for each_row in self.tree.get_children():
            self.tree.delete(each_row)

        for task in self.task_manager.tasks: 
            self.tree.insert("", "end", values=(task.name, task.description, task.priority, task.due_date))
                         
                     
    def apply_filter(self):
        name = self.name_entry.get()
        priority = self.priority_drop_down.get()
        due_date = self.due_date_entry.get()

        filtered_tasks = self.task_manager.get_filtered_task(name_filter=name, priority_filter=priority, due_date_filter=due_date)
        
        for each_row in self.tree.get_children():
            self.tree.delete(each_row)
        for task in filtered_tasks:
            self.tree.insert("", "end", values=(task.name, task.description, task.priority, task.due_date))



    def sort_tasks(self, sort_key):
        self.task_manager.sort_tasks(sort_key)
        self.populate_tree()


    def add_task(self):
        add_task_window=tk.Toplevel(self.root)
        add_task_window.title("Add New Task")
        add_task_window.geometry("300x200")

        label_name = tk.Label(add_task_window, text="Name:", font=("Times New Roman", 10))
        label_name.grid(row=0, column=0, padx=(20,0))
        name_entry=tk.Entry(add_task_window)
        name_entry.grid(row=0, column=1)

        label_description = tk.Label(add_task_window, text="Description:" , font=("Times New Roman", 10))
        label_description.grid(row=1, column=0, padx=(20,0))
        description_entry=tk.Entry(add_task_window)
        description_entry.grid(row=1, column=1)

        label_priority = tk.Label(add_task_window, text="Priority (Low/Medium/High):", font=("Times New Roman", 10))
        label_priority.grid(row=2, column=0, padx=(20,0))
        priority_choices = ["Low", "Medium", "High"]
        priority_drop_down = ttk.Combobox(add_task_window, values = priority_choices)
        priority_drop_down.grid(row=2, column=1)

        label_due_date = tk.Label(add_task_window, text="Due Date (DD/MM/YYYY):", font=("Times New Roman", 10))
        label_due_date.grid(row=3, column=0, padx=(20,0))
        due_date_entry=tk.Entry(add_task_window)
        due_date_entry.grid(row=3, column=1)

        def save_new_task():
            name = name_entry.get()
            description = description_entry.get()
            priority = priority_drop_down.get().capitalize()
            due_date = due_date_entry.get()

            if not name:
                mbox.showerror("Error", "Enter a name. ")
                return
            if priority not in priority_choices:
                mbox.showerror("Error", "Invalid format for priority")
                return
            if len(due_date) != 10 or due_date[2] != "/" or due_date[5] != "/":
                mbox.showerror("Error","Invalid date format")
                return
            
            date, month, year = due_date.split("/")
            date, month, year = int(date), int(month), int(year)


            if date <1 or date >31:
                mbox.showerror("Error","Date must be between 1 and 31")
                return

            if month <1 or month >12: 
                mbox.showerror("Error","Month must be between 01 and 12.")
                return
            
            if year <2000 or year > 2100:
                mbox.showerror("Error","Year must be between 2000 and 2100.")
                return
            
            self.task_manager.tasks.append(Task(name, description, priority, due_date))
            self.task_manager.save_tasks_to_json()
            self.populate_tree()
            add_task_window.destroy()

        save_button = tk.Button(add_task_window, text = "Save Task", command = save_new_task)            
        save_button.grid(row=4,columnspan=2)


    def update_task(self):
        selected_task=self.tree.focus()
        if not selected_task:
            mbox.showwarning("warning","No task selected!")
            return

        values=self.tree.item(selected_task,"values")

        update_task_window=tk.Toplevel(self.root)
        update_task_window.title("Update New Task")
        update_task_window.geometry("300x200")

        label_name = tk.Label(update_task_window, text="Name:", font=("Times New Roman", 10))
        label_name.grid(row=0, column=0, padx=(20,0))
        name_entry=tk.Entry(update_task_window)
        name_entry.insert(0, values[0])
        name_entry.grid(row=0, column=1)

        label_description = tk.Label(update_task_window, text="Description:" , font=("Times New Roman", 10))
        label_description.grid(row=1, column=0, padx=(20,0))
        description_entry=tk.Entry(update_task_window)
        description_entry.insert(0, values[1])
        description_entry.grid(row=1, column=1)

        label_priority = tk.Label(update_task_window, text="Priority (Low/Medium/High):", font=("Times New Roman", 10))
        label_priority.grid(row=2, column=0, padx=(20,0))
        priority_choices = ["Low", "Medium", "High"]
        priority_drop_down = ttk.Combobox(update_task_window, values = priority_choices)
        priority_drop_down.insert(0, values[2])
        priority_drop_down.grid(row=2, column=1)

        label_due_date = tk.Label(update_task_window, text="Due Date (DD/MM/YYYY):", font=("Times New Roman", 10))
        label_due_date.grid(row=3, column=0, padx=(20,0))
        due_date_entry=tk.Entry(update_task_window)
        due_date_entry.insert(0, values[3])
        due_date_entry.grid(row=3, column=1)

        def save_updated_task():
            name = name_entry.get()
            description = description_entry.get()
            priority = priority_drop_down.get().capitalize()
            due_date = due_date_entry.get()

            if not name:
                mbox.showerror("Error", "Enter a name. ")
                return
            
            if priority not in priority_choices:
               mbox.showerror("Error", "Invalid format for priority")
               return
            if len(due_date) != 10 or due_date[2] != "/" or due_date[5] != "/":
               mbox.showerror("Error","Invalid date format")
               return
            
            date, month, year = due_date.split("/")
            date, month, year = int(date), int(month), int(year)

            if date < 1 or date > 31:
                mbox.showerror("Error","Date must be between 1 and 31")
                return

            if month < 1 or month > 12: 
                mbox.showerror("Error","Month must be between 01 and 12.")
                return
            
            if year < 2000 or year > 2100:
                mbox.showerror("Error","Year must be between 2000 and 2100.")
                return
        
            index = self.tree.index(selected_task)
            self.task_manager.tasks[index] = Task(name_entry, description, priority, due_date)
            self.task_manager.save_tasks_to_json()
            self.populate_tree()
            update_task_window.destroy()

        save_button = tk.Button(update_task_window, text = "Save Task", command = save_updated_task)            
        save_button.grid(row=4,columnspan=2)

        
    def delete_task(self):
        selected_task = self.tree.focus()
        if not selected_task:
            mbox.showwarning("Warning", "No task selected!")
            return

        confirm = mbox.askyesno("Confirm Delete", "Are you sure you want to delete the selected task?")
        if confirm:
            index = self.tree.index(selected_task)
            del self.task_manager.tasks[index]
            self.task_manager.save_tasks_to_json()
            self.populate_tree()

            
    
if __name__ == "__main__":
    root=tk.Tk()
    app=TaskManagerGUI(root)
    root.mainloop()

        

