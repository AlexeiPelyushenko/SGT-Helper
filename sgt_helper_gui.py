import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, List

class SGTHelperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Spectral Graph Theory Helper")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        self.json_path = "info.json"
        self.data_store = self.load_data()
        self.current_topic = None
        
        self.setup_ui()
        self.refresh_topic_list()
        
    def load_data(self) -> Dict:
        """Load data from JSON file, create if it doesn't exist."""
        if not os.path.exists(self.json_path):
            with open(self.json_path, "w", encoding="utf-8") as f:
                f.write("{}")
        with open(self.json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def save_data(self):
        """Save data to JSON file."""
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(self.data_store, f, indent=4)
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Spectral Graph Theory Helper", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Left panel - Topics
        left_panel = ttk.LabelFrame(main_frame, text="Topics", padding="10")
        left_panel.grid(row=1, column=0, sticky="news", padx=(0, 20))
        left_panel.rowconfigure(1, weight=1)
        
        # Topic list with scrollbar
        topic_frame = ttk.Frame(left_panel)
        topic_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        topic_frame.columnconfigure(0, weight=1)
        topic_frame.rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(topic_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.topic_listbox = tk.Listbox(topic_frame, yscrollcommand=scrollbar.set,
                                        font=("Arial", 11), selectmode=tk.SINGLE)
        self.topic_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.topic_listbox.bind('<<ListboxSelect>>', self.on_topic_select)
        scrollbar.config(command=self.topic_listbox.yview)
        
        # Topic buttons
        topic_btn_frame = ttk.Frame(left_panel)
        topic_btn_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(topic_btn_frame, text="Add Topic", command=self.add_topic).grid(row=0, column=0, padx=2, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(topic_btn_frame, text="Delete Topic", command=self.delete_topic).grid(row=0, column=1, padx=2, pady=5, sticky=(tk.W, tk.E))
        topic_btn_frame.columnconfigure(0, weight=1)
        topic_btn_frame.columnconfigure(1, weight=1)
        
        # Right panel - Content
        right_panel = ttk.LabelFrame(main_frame, text="Content", padding="10")
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        
        # Current topic label
        self.topic_label = ttk.Label(right_panel, text="Select a topic to view/edit content", 
                                     font=("Arial", 12, "bold"))
        self.topic_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)
        
        # Content display with scrollbar
        self.content_text = scrolledtext.ScrolledText(right_panel, wrap=tk.WORD, 
                                                      font=("Arial", 11), height=15)
        self.content_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Content buttons
        content_btn_frame = ttk.Frame(right_panel)
        content_btn_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(content_btn_frame, text="Add Entry", command=self.add_entry).grid(row=0, column=0, padx=2, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(content_btn_frame, text="Edit Entry", command=self.edit_entry).grid(row=0, column=1, padx=2, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(content_btn_frame, text="Delete Selected", command=self.delete_entry).grid(row=0, column=2, padx=2, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(content_btn_frame, text="Save", command=self.save_and_refresh).grid(row=0, column=3, padx=2, pady=5, sticky=(tk.W, tk.E))
        content_btn_frame.columnconfigure(0, weight=1)
        content_btn_frame.columnconfigure(1, weight=1)
        content_btn_frame.columnconfigure(2, weight=1)
        content_btn_frame.columnconfigure(3, weight=1)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def refresh_topic_list(self):
        """Refresh the topic listbox."""
        self.topic_listbox.delete(0, tk.END)
        for topic in sorted(self.data_store.keys()):
            self.topic_listbox.insert(tk.END, topic)
    
    def on_topic_select(self, event):
        """Handle topic selection."""
        selection = self.topic_listbox.curselection()
        if selection:
            topic = self.topic_listbox.get(selection[0])
            self.current_topic = topic
            self.display_topic_content(topic)
    
    def display_topic_content(self, topic: str):
        """Display content for the selected topic."""
        self.topic_label.config(text=f"Topic: {topic}")
        self.content_text.delete(1.0, tk.END)
        
        if topic in self.data_store:
            entries = self.data_store[topic]
            for i, entry in enumerate(entries, 1):
                self.content_text.insert(tk.END, f"{i}. {entry}\n\n")
        
        self.status_label.config(text=f"Displaying content for: {topic}")
    
    def add_topic(self):
        """Add a new topic."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Topic")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Topic name:", font=("Arial", 11)).pack(pady=10)
        
        entry = ttk.Entry(dialog, width=40, font=("Arial", 11))
        entry.pack(pady=5)
        entry.focus()
        
        def confirm():
            topic_name = entry.get().strip()
            if topic_name:
                if topic_name in self.data_store:
                    messagebox.showwarning("Warning", f"Topic '{topic_name}' already exists!")
                else:
                    self.data_store[topic_name] = []
                    self.refresh_topic_list()
                    self.save_data()
                    self.status_label.config(text=f"Added topic: {topic_name}")
                    dialog.destroy()
            else:
                messagebox.showwarning("Warning", "Topic name cannot be empty!")
        
        def cancel():
            dialog.destroy()
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add", command=confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=cancel).pack(side=tk.LEFT, padx=5)
        
        entry.bind('<Return>', lambda e: confirm())
        entry.bind('<Escape>', lambda e: cancel())
    
    def delete_topic(self):
        """Delete the selected topic."""
        selection = self.topic_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a topic to delete!")
            return
        
        topic = self.topic_listbox.get(selection[0])
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete topic '{topic}'?"):
            del self.data_store[topic]
            self.refresh_topic_list()
            self.current_topic = None
            self.topic_label.config(text="Select a topic to view/edit content")
            self.content_text.delete(1.0, tk.END)
            self.save_data()
            self.status_label.config(text=f"Deleted topic: {topic}")
    
    def add_entry(self):
        """Add a new entry to the current topic."""
        if not self.current_topic:
            messagebox.showwarning("Warning", "Please select a topic first!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Add Entry to {self.current_topic}")
        dialog.geometry("500x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Entry content:", font=("Arial", 11)).pack(pady=10)
        
        text_widget = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, width=50, height=6, font=("Arial", 11))
        text_widget.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        text_widget.focus()
        
        def confirm():
            content = text_widget.get(1.0, tk.END).strip()
            if content:
                self.data_store[self.current_topic].append(content)
                self.display_topic_content(self.current_topic)
                self.save_data()
                self.status_label.config(text=f"Added entry to: {self.current_topic}")
                dialog.destroy()
            else:
                messagebox.showwarning("Warning", "Entry content cannot be empty!")
        
        def cancel():
            dialog.destroy()
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add", command=confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=cancel).pack(side=tk.LEFT, padx=5)
    
    def delete_entry(self):
        """Delete the selected entry from the current topic."""
        if not self.current_topic:
            messagebox.showwarning("Warning", "Please select a topic first!")
            return
        
        # Get cursor position to determine which entry is selected
        cursor_pos = self.content_text.index(tk.INSERT)
        line_num = int(cursor_pos.split('.')[0])
        
        # Find which entry number this line belongs to
        entries = self.data_store[self.current_topic]
        if not entries:
            messagebox.showinfo("Info", "No entries to delete!")
            return
        
        # Simple approach: show a dialog to select entry number
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Delete Entry from {self.current_topic}")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Select entry to delete:", font=("Arial", 11)).pack(pady=10)
        
        listbox = tk.Listbox(dialog, font=("Arial", 11), height=10)
        listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        
        for i, entry in enumerate(entries, 1):
            # Show first 50 chars of entry
            preview = entry[:50] + "..." if len(entry) > 50 else entry
            listbox.insert(tk.END, f"{i}. {preview}")
        
        def confirm():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                entry_preview = entries[index][:50] + "..." if len(entries[index]) > 50 else entries[index]
                if messagebox.askyesno("Confirm Delete", f"Delete entry:\n{entry_preview}?"):
                    del self.data_store[self.current_topic][index]
                    self.display_topic_content(self.current_topic)
                    self.save_data()
                    self.status_label.config(text=f"Deleted entry from: {self.current_topic}")
                    dialog.destroy()
            else:
                messagebox.showwarning("Warning", "Please select an entry to delete!")
        
        def cancel():
            dialog.destroy()
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Delete", command=confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=cancel).pack(side=tk.LEFT, padx=5)
        
        listbox.bind('<Double-Button-1>', lambda e: confirm())
    
    def edit_entry(self):
        """Edit an existing entry in the current topic."""
        if not self.current_topic:
            messagebox.showwarning("Warning", "Please select a topic first!")
            return
        
        entries = self.data_store[self.current_topic]
        if not entries:
            messagebox.showinfo("Info", "No entries to edit!")
            return
        
        # Show a dialog to select entry to edit
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Entry from {self.current_topic}")
        dialog.geometry("500x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Select entry to edit:", font=("Arial", 11)).pack(pady=10)
        
        listbox = tk.Listbox(dialog, font=("Arial", 11), height=8)
        listbox.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        
        for i, entry in enumerate(entries, 1):
            # Show first 50 chars of entry
            preview = entry[:50] + "..." if len(entry) > 50 else entry
            listbox.insert(tk.END, f"{i}. {preview}")
        
        def confirm():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                # Open edit dialog with the selected entry's content
                edit_dialog = tk.Toplevel(dialog)
                edit_dialog.title(f"Edit Entry {index + 1}")
                edit_dialog.geometry("500x250")
                edit_dialog.transient(dialog)
                edit_dialog.grab_set()
                
                ttk.Label(edit_dialog, text="Edit entry content:", font=("Arial", 11)).pack(pady=10)
                
                text_widget = scrolledtext.ScrolledText(edit_dialog, wrap=tk.WORD, width=50, height=8, font=("Arial", 11))
                text_widget.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
                text_widget.insert(1.0, entries[index])
                text_widget.focus()
                
                def save_edit():
                    new_content = text_widget.get(1.0, tk.END).strip()
                    if new_content:
                        self.data_store[self.current_topic][index] = new_content
                        self.display_topic_content(self.current_topic)
                        self.save_data()
                        self.status_label.config(text=f"Edited entry {index + 1} in: {self.current_topic}")
                        edit_dialog.destroy()
                        dialog.destroy()
                    else:
                        messagebox.showwarning("Warning", "Entry content cannot be empty!")
                
                def cancel_edit():
                    edit_dialog.destroy()
                
                btn_frame = ttk.Frame(edit_dialog)
                btn_frame.pack(pady=10)
                ttk.Button(btn_frame, text="Save", command=save_edit).pack(side=tk.LEFT, padx=5)
                ttk.Button(btn_frame, text="Cancel", command=cancel_edit).pack(side=tk.LEFT, padx=5)
                
                text_widget.bind('<Control-Return>', lambda e: save_edit())
            else:
                messagebox.showwarning("Warning", "Please select an entry to edit!")
        
        def cancel():
            dialog.destroy()
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Edit", command=confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=cancel).pack(side=tk.LEFT, padx=5)
        
        listbox.bind('<Double-Button-1>', lambda e: confirm())
    
    def save_and_refresh(self):
        """Save data and refresh display."""
        self.save_data()
        if self.current_topic:
            self.display_topic_content(self.current_topic)
        self.status_label.config(text="Data saved successfully!")
    
    def on_closing(self):
        """Handle window close event."""
        self.save_data()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = SGTHelperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
