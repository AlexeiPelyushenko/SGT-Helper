import json
import os
import re
import io
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from PIL import Image, ImageTk

class SGTHelperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Spectral Graph Theory Helper")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        self.json_path = "info.json"
        self.data_store = self.load_data()
        self.current_topic = None
        self.latex_cache = {}  # Cache rendered LaTeX images
        self.last_canvas_width = 0  # Track canvas width for resize detection
        
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
        
        # Content display with scrollbar - using Canvas for LaTeX rendering
        content_frame = ttk.Frame(right_panel)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(content_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.content_canvas = tk.Canvas(content_frame, yscrollcommand=scrollbar.set,
                                       bg="white", highlightthickness=0)
        self.content_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.config(command=self.content_canvas.yview)
        
        # Bind mousewheel to canvas
        def on_mousewheel(event):
            self.content_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.content_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Handle canvas resize to redraw content (only if width changed significantly)
        def on_canvas_configure(event):
            new_width = event.width
            if self.current_topic and abs(new_width - self.last_canvas_width) > 10:
                self.last_canvas_width = new_width
                self.display_topic_content(self.current_topic)
        self.content_canvas.bind('<Configure>', on_canvas_configure)
        
        # Content buttons
        content_btn_frame = ttk.Frame(right_panel)
        content_btn_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(content_btn_frame, text="Add Entry", command=self.add_entry).grid(row=0, column=0, padx=2, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(content_btn_frame, text="Edit Entry", command=self.edit_entry).grid(row=0, column=1, padx=2, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(content_btn_frame, text="Delete Entry", command=self.delete_entry).grid(row=0, column=2, padx=2, pady=5, sticky=(tk.W, tk.E))
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
    
    def render_latex_to_image(self, latex_text: str, dpi: int = 100, fontsize: int = 11, save_path: str = None) -> ImageTk.PhotoImage:
        """Render LaTeX text to a PIL Image using matplotlib's mathtext, then convert to PhotoImage.
        
        Args:
            latex_text: The LaTeX text to render
            dpi: Resolution (dots per inch) for the image
            fontsize: Font size for the LaTeX rendering
            save_path: Optional path to save the image file (e.g., 'latex_output.png')
        
        Returns:
            ImageTk.PhotoImage object for use in tkinter
        """
        # Check cache first
        cache_key = f"{latex_text}_{dpi}_{fontsize}"
        if cache_key in self.latex_cache:
            return self.latex_cache[cache_key]
        
        try:
            # Use matplotlib's mathtext renderer (works without LaTeX installation)
            # Start with very small figure size - bbox_inches='tight' will crop to content
            # This prevents excessive whitespace for short expressions like v_1
            fig = plt.figure(figsize=(0.1, 0.1))
            fig.patch.set_facecolor('white')
            ax = fig.add_subplot(111)
            ax.axis('off')
            
            # Render LaTeX using mathtext (usetex=False uses built-in renderer)
            # Remove $ signs if present (we'll add them)
            clean_text = latex_text.strip().strip('$')
            # Use smaller fontsize for inline math to match text better
            inline_fontsize = max(fontsize - 2, 8)  # Smaller for inline to match text size
            ax.text(0.5, 0.5, f'${clean_text}$', fontsize=inline_fontsize, 
                   ha='center', va='center', usetex=False)
            
            # Convert to image with zero padding
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight', 
                       facecolor='white', edgecolor='none', pad_inches=0, transparent=True)
            buf.seek(0)
            img = Image.open(buf)
            
            # Crop white space from the image
            # Convert to RGB if RGBA
            if img.mode == 'RGBA':
                # Create white background
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])
                img = rgb_img
            
            # Crop white space, but add a bit of white padding at the bottom and right for spacing
            bbox = img.getbbox()
            if bbox:
                left, top, right, bottom = bbox
                # Add a few pixels of white padding at the bottom to align with text baseline
                bottom_padding = 2  # Add 2 pixels of white space at bottom
                right_padding = 2  # Add 2 pixels of white space at right
                # Create new image with white background and padding
                new_width = (right - left) + right_padding
                new_height = (bottom - top) + bottom_padding
                padded_img = Image.new('RGB', (new_width, new_height), (255, 255, 255))
                # Paste the cropped image onto the white background
                padded_img.paste(img.crop((left, top, right, bottom)), (0, 0))
                img = padded_img
            
            # Save the image if save_path is provided
            if save_path:
                img.save(save_path, 'PNG')
                print(f"LaTeX image saved to: {save_path}")
            
            photo = ImageTk.PhotoImage(img)
            
            plt.close(fig)
            
            # Cache the result
            self.latex_cache[cache_key] = photo
            return photo
        except Exception as e:
            # If LaTeX rendering fails, return None
            print(f"LaTeX rendering error: {e}")
            return None
    
    def parse_latex(self, text: str) -> List[Tuple[str, bool]]:
        """
        Parse text and identify LaTeX portions.
        Returns list of (content, is_latex) tuples.
        Supports $...$ for inline math and $$...$$ for display math.
        """
        parts = []
        # Pattern to match $...$ or $$...$$
        pattern = r'\$\$([^$]+)\$\$|\$([^$]+)\$'
        
        last_end = 0
        for match in re.finditer(pattern, text):
            start, end = match.span()
            # Add text before LaTeX
            if start > last_end:
                parts.append((text[last_end:start], False))
            
            # Add LaTeX (prefer $$...$$ over $...$)
            latex_content = match.group(1) or match.group(2)
            is_display = match.group(1) is not None  # True if $$...$$
            parts.append((latex_content, True))
            
            last_end = end
        
        # Add remaining text
        if last_end < len(text):
            parts.append((text[last_end:], False))
        
        # If no LaTeX found, return entire text as non-LaTeX
        if not parts:
            parts.append((text, False))
        
        return parts
    
    def display_topic_content(self, topic: str):
        """Display content for the selected topic with LaTeX rendering."""
        self.topic_label.config(text=f"Topic: {topic}")
        
        # Clear canvas and image references
        self.content_canvas.delete("all")
        self.content_canvas.image_refs = []
        
        if topic in self.data_store:
            entries = self.data_store[topic]
            y_position = 20
            font = ("Arial", 11)
            line_height = 25
            margin_left = 10
            text_indent = 40
            canvas_width = self.content_canvas.winfo_width() or 800
            self.last_canvas_width = canvas_width
            
            for i, entry in enumerate(entries, 1):
                # Entry number
                self.content_canvas.create_text(margin_left, y_position, 
                                              text=f"{i}. ", anchor="nw", 
                                              font=("Arial", 11, "bold"))
                
                # Parse and render entry
                parts = self.parse_latex(entry)
                
                x_position = text_indent
                current_y = y_position
                max_height_in_line = line_height
                
                for part_text, is_latex in parts:
                    if is_latex:
                        # Render LaTeX inline with text - use smaller size for compact rendering
                        latex_image = self.render_latex_to_image(part_text, dpi=100, fontsize=12)
                        if latex_image:
                            # Get image dimensions
                            img_width = latex_image.width()
                            img_height = latex_image.height()
                            
                            # Check if LaTeX fits on current line
                            if x_position + img_width > canvas_width - 20 and x_position > text_indent:
                                # Move to next line only if it doesn't fit
                                current_y += max_height_in_line
                                x_position = text_indent
                                max_height_in_line = line_height
                            
                            # Align LaTeX inline with text - position at same y as text
                            # For inline math, align the bottom of LaTeX with text baseline
                            # Text baseline is approximately at current_y + line_height * 0.8
                            text_baseline = current_y + int(line_height * 0.8)
                            # Position LaTeX so its baseline aligns with text baseline
                            # Most LaTeX sits on the baseline, so align bottom of image with baseline
                            img_y = text_baseline - img_height
                            
                            # Ensure LaTeX doesn't go above the line (clip to current_y)
                            if img_y < current_y:
                                img_y = current_y
                            
                            img_id = self.content_canvas.create_image(x_position, img_y, 
                                                                    anchor="nw", image=latex_image)
                            # Keep reference to prevent garbage collection
                            self.content_canvas.image_refs.append(latex_image)
                            
                            # Update position to continue after LaTeX on same line
                            x_position += img_width + 1  # Minimal gap after LaTeX
                            # Update line height to accommodate LaTeX if it extends below
                            line_bottom = max(current_y + line_height, img_y + img_height)
                            max_height_in_line = line_bottom - current_y
                        else:
                            # Fallback to text if rendering fails
                            fallback_text = f"${part_text}$"
                            text_id = self.content_canvas.create_text(x_position, current_y, 
                                                                    text=fallback_text, 
                                                                    anchor="nw", font=font)
                            bbox = self.content_canvas.bbox(text_id)
                            if bbox:
                                x_position = bbox[2] + 5
                    else:
                        # Regular text - handle line breaks and word wrapping
                        if part_text.strip():
                            lines = part_text.split('\n')
                            for line_idx, line in enumerate(lines):
                                if line.strip():
                                    words = line.split(' ')
                                    for word in words:
                                        if not word:
                                            continue
                                        
                                        word_with_space = word + ' '
                                        
                                        # Estimate word width first
                                        # Create text at a position we can measure
                                        test_id = self.content_canvas.create_text(0, 0, 
                                                                                 text=word_with_space, 
                                                                                 font=font, anchor="nw")
                                        bbox = self.content_canvas.bbox(test_id)
                                        word_width = (bbox[2] - bbox[0]) if bbox else len(word_with_space) * 7
                                        
                                        # Check if word fits on current line
                                        if x_position + word_width > canvas_width - 20 and x_position > text_indent:
                                            current_y += max_height_in_line
                                            x_position = text_indent
                                            max_height_in_line = line_height
                                        
                                        # Delete test item and create actual text at correct position
                                        self.content_canvas.delete(test_id)
                                        text_id = self.content_canvas.create_text(x_position, current_y, 
                                                                                text=word_with_space, 
                                                                                font=font, anchor="nw")
                                        bbox = self.content_canvas.bbox(text_id)
                                        
                                        if bbox:
                                            x_position = bbox[2]
                                            max_height_in_line = max(max_height_in_line, line_height)
                                
                                # Handle explicit line breaks
                                if line_idx < len(lines) - 1:
                                    current_y += max_height_in_line
                                    x_position = text_indent
                                    max_height_in_line = line_height
                
                y_position = current_y + max_height_in_line + 20  # Space between entries
            
            # Update scroll region
            self.content_canvas.update_idletasks()
            scroll_region = self.content_canvas.bbox("all")
            if scroll_region:
                self.content_canvas.config(scrollregion=scroll_region)
        
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
        
        entries = self.data_store[self.current_topic]
        if not entries:
            messagebox.showinfo("Info", "No entries to delete!")
            return
        
        # Show a dialog to select entry to delete
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
    
def test_program():
    root = tk.Tk()
    app = SGTHelperGUI(root)
    txt = "v_1"
    app.render_latex_to_image(txt, 100, 10, "img/img3.png")


if __name__ == "__main__":
    test = False
    if test:
        test_program()
    else:
        main()
