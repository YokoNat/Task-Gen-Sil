import tkinter as tk
import os
from tkinter import messagebox, simpledialog, ttk
from task_manager import TaskManager
import pandas as pd
import threading
from file_watcher import FileWatcher
import math

DYNAMIC_FIELDS = ['product', 'presale', 'price_range', 'extra_filter']

class SilentlyTaskGeneratorApp:
    def __init__(self, root):
        root.title('Silently Task Generator')
        root.geometry('800x600')  # Initial size, can be adjusted later

        # Main container
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Task List Panel (left)
        self.task_list_panel = tk.Frame(self.main_frame, width=250, bg='#f0f0f0', relief=tk.RIDGE, borderwidth=2)
        self.task_list_panel.pack(side=tk.LEFT, fill=tk.Y)
        self.task_list_panel.pack_propagate(False)

        # Merge button
        self.merge_button = tk.Button(self.task_list_panel, text='Merge', font=('Arial', 12), command=self.merge_tasks)
        self.merge_button.pack(pady=(10, 0), padx=10, fill=tk.X)

        # Task List label
        label = tk.Label(self.task_list_panel, text='Task List', font=('Arial', 14), bg='#f0f0f0')
        label.pack(pady=10)

        # Listbox for tasks (enable multi-select)
        self.task_listbox = tk.Listbox(self.task_list_panel, font=('Arial', 12), selectmode=tk.EXTENDED)
        self.task_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.task_listbox.bind('<<ListboxSelect>>', self.on_task_select)
        self.ignore_listbox_event = False  # Flag to ignore listbox events

        # Populate Listbox with tasks from TASKS directory
        tasks_dir = os.path.join(os.path.dirname(__file__), '../shhh/tasks/TASKS')
        print(f"Tasks directory absolute path: {os.path.abspath(tasks_dir)}")  # Debug log
        self.task_manager = TaskManager(tasks_dir)
        self.tasks_dir = tasks_dir
        self.refresh_task_list()

        # File watcher setup
        self.file_watcher = FileWatcher(self.tasks_dir, self.on_tasks_dir_change)
        self.watcher_thread = threading.Thread(target=self.file_watcher.start, daemon=True)
        self.watcher_thread.start()
        root.protocol('WM_DELETE_WINDOW', self.on_close)

        # Task Detail Panel (right)
        self.right_panel = tk.Frame(self.main_frame, relief=tk.GROOVE, borderwidth=2)
        self.right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.detail_label = tk.Label(self.right_panel, text='Select a task to view details', font=('Arial', 14))
        self.detail_label.pack(pady=20)

        # Store field widgets for later use
        self.field_widgets = {}
        self.edit_button = None
        self.save_button = None
        self.delete_button = None
        self.duplicate_button = None
        self.current_task = None
        self.current_df = None

        # Add a 'Create Task' button to the UI
        self.create_task_button = tk.Button(self.task_list_panel, text="Create Task", command=self.create_task)
        self.create_task_button.pack(pady=5)

    def refresh_task_list(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.task_manager.list_tasks():
            self.task_listbox.insert(tk.END, task)

    def on_tasks_dir_change(self, *args):
        # Called from file watcher thread; must update UI in main thread
        self.task_listbox.after(0, self.refresh_task_list)

    def clear_detail_panel(self):
        for widget in self.right_panel.winfo_children():
            if widget != self.detail_label:
                widget.destroy()
        self.field_widgets = {}
        self.edit_button = None
        self.save_button = None
        self.delete_button = None
        self.duplicate_button = None
        self.current_task = None
        self.current_df = None

    def on_task_select(self, event):
        if getattr(self, 'ignore_listbox_event', False):
            return  # Ignore event triggered by tab change
        selection = self.task_listbox.curselection()
        # If selection is empty, restore last selected index and do nothing
        if len(selection) == 0:
            if hasattr(self, 'last_selected_index') and self.last_selected_index is not None:
                self.task_listbox.selection_set(self.last_selected_index)
                self.task_listbox.activate(self.last_selected_index)
            return
        # Only update if a new task is explicitly selected
        if len(selection) == 1:
            if hasattr(self, 'last_selected_index') and self.last_selected_index == selection[0]:
                return  # Same task, do nothing
            self.last_selected_index = selection[0]  # Remember last selected index
            self.clear_detail_panel()
            filename = self.task_listbox.get(selection[0])
            self.current_task = filename
            self.detail_label.config(text=f'Task: {filename}')
            try:
                print(f"Loading task file: {filename}")  # Debug log
                df = self.task_manager.load_task(filename)
                print(f"Loaded DataFrame shape: {df.shape}")  # Debug log
                print(f"DataFrame columns: {df.columns.tolist()}")  # Debug log
                self.current_df = df

                unique_products = df['product'].dropna().unique()

                # --- NEW: Create tabs for each unique product or single panel ---
                if len(unique_products) > 1:
                    self.notebook = ttk.Notebook(self.right_panel)
                    self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                    self.tab_field_widgets = {}

                    def on_tab_changed(event):
                        self.ignore_listbox_event = True
                        # Use after_idle to allow Tkinter to process events before setting flag back
                        self.right_panel.after_idle(lambda: setattr(self, 'ignore_listbox_event', False))
                        # When tab changes, ensure the correct filters UI is shown/rebuilt if needed
                        selected_tab = self.notebook.select()
                        # The filter UI is now built within each tab frame, so no explicit show/hide is needed here
                        # The rebuild logic is handled in the on_add/delete/cancel callbacks if they are triggered.

                    self.notebook.bind('<<NotebookTabChanged>>', on_tab_changed)

                    for prod in unique_products:
                        tab = tk.Frame(self.notebook)
                        self.notebook.add(tab, text=prod)
                        prod_rows = df[df['product'] == prod]
                        first_row = prod_rows.iloc[0]
                        field_widgets = {}
                        for i, field in enumerate(DYNAMIC_FIELDS):
                            label = tk.Label(tab, text=field, font=('Arial', 12))
                            label.pack(anchor='w', padx=20, pady=(10 if i==0 else 2, 2))
                            value = first_row.get(field, '')
                            if value is None or (isinstance(value, float) and math.isnan(value)):
                                value = ''
                            entry = tk.Entry(tab, font=('Arial', 12))
                            entry.insert(0, str(value))
                            entry.pack(fill=tk.X, padx=20, pady=2)
                            field_widgets[field] = entry

                        self.tab_field_widgets[prod] = field_widgets
                        # --- Filters Table UI for this tab ---
                        extra_filter_entry = field_widgets.get('extra_filter')
                        if extra_filter_entry:
                             # Pass the tab frame as the parent for the filter UI
                            self.build_filters_ui(tab, extra_filter_entry, first_row.get('extra_filter', ''), row_data=first_row)

                    # Place main Save/Cancel/Delete buttons below the notebook
                    self.save_button = tk.Button(self.right_panel, text='Save Task', font=('Arial', 12), command=self.save_edits)
                    self.save_button.pack(pady=10)
                    self.cancel_button = tk.Button(self.right_panel, text='Cancel Task', font=('Arial', 12), command=self.cancel_edits)
                    self.cancel_button.pack(pady=10)
                    self.delete_button = tk.Button(self.right_panel, text='Delete Task', font=('Arial', 12), fg='red', command=self.confirm_delete)
                    self.delete_button.pack(pady=10)

                else:
                    # Single product, show as before in the main panel
                    row = df.iloc[0]
                    for i, field in enumerate(DYNAMIC_FIELDS):
                        label = tk.Label(self.right_panel, text=field, font=('Arial', 12))
                        label.pack(anchor='w', padx=20, pady=(10 if i==0 else 2, 2))
                        value = row.get(field, '')
                        if value is None or (isinstance(value, float) and math.isnan(value)):
                            value = ''
                        entry = tk.Entry(self.right_panel, font=('Arial', 12))
                        entry.insert(0, str(value))
                        entry.pack(fill=tk.X, padx=20, pady=2)
                        self.field_widgets[field] = entry

                    # --- Filters Table UI for single product ---
                    extra_filter_entry = self.field_widgets.get('extra_filter')
                    if extra_filter_entry:
                         # Pass the right_panel as the parent for the filter UI
                        self.build_filters_ui(self.right_panel, extra_filter_entry, row.get('extra_filter', ''), row_data=row)

                    # Place main Save/Cancel/Delete buttons below the fields
                    self.save_button = tk.Button(self.right_panel, text='Save Task', font=('Arial', 12), command=self.save_edits)
                    self.save_button.pack(pady=10)
                    self.cancel_button = tk.Button(self.right_panel, text='Cancel Task', font=('Arial', 12), command=self.cancel_edits)
                    self.cancel_button.pack(pady=10)
                    self.delete_button = tk.Button(self.right_panel, text='Delete Task', font=('Arial', 12), fg='red', command=self.confirm_delete)
                    self.delete_button.pack(pady=10)

            except Exception as e:
                msg = tk.Label(self.right_panel, text=f'Error loading file: {e}', fg='red', font=('Arial', 12, 'italic'))
                msg.pack(pady=10)
        else:
            self.clear_detail_panel()
            self.detail_label.config(text='Select a task to view details')

    def enable_editing(self):
        pass  # No longer needed, fields are always editable

    def save_edits(self):
        if self.current_task and self.current_df is not None and not self.current_df.empty:
            # If using tabs (multiple products)
            if hasattr(self, 'notebook') and hasattr(self, 'tab_field_widgets') and self.notebook.winfo_exists():
                # Get currently selected tab/product
                current_tab_index = self.notebook.index(self.notebook.select())
                product = self.notebook.tab(current_tab_index, 'text')
                field_widgets = self.tab_field_widgets[product]
                # Update all rows for this product in the DataFrame
                for field, entry in field_widgets.items():
                    value = entry.get()
                    # Ensure 'product' field itself is not updated here from the entry, 
                    # as it's the key for the tab and shouldn't change via the filter editor.
                    # Other dynamic fields are updated for rows matching this product.
                    if field != 'product' and field in self.current_df.columns:
                         self.current_df.loc[self.current_df['product'] == product, field] = value

                # Also update the extra_filter field in the DataFrame based on the filters table state for this product
                # Get the current filters from the UI table for this product tab
                current_filters_in_ui = []
                # Need to get the actual filters from the currently displayed filter rows for this product tab
                # Accessing filter_rows requires knowing which filters_frame is active
                # A better approach is to store filters state per product tab
                # For now, let's assume filters is the list currently used by build_filters_table
                # This needs refinement, but for Step 1, focus is on notebook error
                # The on_save_row/on_cancel logic already updates the extra_filter entry widget
                # We need to ensure this update is also reflected in the self.current_df for the correct rows.
                # This part needs to be revisited in later steps (Step 3 primarily).
                pass # Placeholder for future filter update logic in DataFrame


            else:
                # Single product, update all rows using the main field widgets
                for field, entry in self.field_widgets.items():
                    value = entry.get()
                    if field in self.current_df.columns:
                        self.current_df[field] = value

            # Save the updated DataFrame back to the CSV (applies to both cases)
            try:
                self.task_manager.save_task(self.current_task, self.current_df)
                # Do not hide the save button; keep it visible
                # Preserve selection in the listbox
                if hasattr(self, 'last_selected_index') and self.last_selected_index is not None:
                    self.task_listbox.selection_set(self.last_selected_index)
                    self.task_listbox.activate(self.last_selected_index)

                # --- Update row_data reference for the filter Cancel button ---
                if hasattr(self, 'notebook') and self.notebook.winfo_exists():
                    # Multi-product case: Get the filters_frame for the current tab
                    current_tab_index = self.notebook.index(self.notebook.select())
                    # Access the frame that is the parent of the filter_table_content_frame within this tab
                    # This frame was created in build_filters_ui and should hold the row_data
                    current_tab_frame = self.notebook.winfo_children()[current_tab_index]
                    for child in current_tab_frame.winfo_children():
                        if hasattr(child, 'filters_list') and hasattr(child, 'row_data'):
                            # Found the filters_frame for this tab
                            product = self.notebook.tab(current_tab_index, 'text')
                            prod_rows = self.current_df[self.current_df['product'] == product]
                            if not prod_rows.empty:
                                child.row_data = prod_rows.iloc[0] # Update row_data with the latest from df
                            break # Found the frame, exit loop
                else:\
                    # Single product case: The filters_frame is directly in self.right_panel
                    for child in self.right_panel.winfo_children():
                         # Find the filters_frame - it has the filters_list and row_data attributes
                         if hasattr(child, 'filters_list') and hasattr(child, 'row_data'):
                             child.row_data = self.current_df.iloc[0] # Update row_data with the latest from df
                             break # Found the frame, exit loop
                # --- End update row_data reference ---

                messagebox.showinfo('Saved', f'Task "{self.current_task}" saved successfully.')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to save: {e}')

    def confirm_delete(self):
        if not self.current_task:
            return
        # First confirmation
        if not messagebox.askyesno('Confirm Delete', f'Are you sure you want to delete "{self.current_task}"?'):
            return
        # Second confirmation
        if not messagebox.askyesno('Confirm Delete', f'This will permanently delete "{self.current_task}". Are you absolutely sure?'):
            return
        # Delete the file
        try:
            os.remove(os.path.join(self.tasks_dir, self.current_task))
            messagebox.showinfo('Deleted', f'Task "{self.current_task}" deleted.')
            self.refresh_task_list()
            self.clear_detail_panel()
            self.detail_label.config(text='Select a task to view details')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to delete: {e}')

    def duplicate_task(self):
        if not self.current_task or self.current_df is None:
            return
        # Prompt for new unique task name
        new_name = simpledialog.askstring('Duplicate Task', 'Enter a new name for the duplicated task (must end with .csv):')
        if not new_name:
            return
        if not new_name.lower().endswith('.csv'):
            new_name += '.csv'
        if new_name in self.task_manager.list_tasks():
            messagebox.showerror('Error', f'A task named "{new_name}" already exists.')
            return
        try:
            self.task_manager.save_task(new_name, self.current_df.copy())
            messagebox.showinfo('Duplicated', f'Task duplicated as "{new_name}".')
            self.refresh_task_list()
            # Select the new task in the listbox
            idx = self.task_manager.list_tasks().index(new_name)
            self.task_listbox.selection_clear(0, tk.END)
            self.task_listbox.selection_set(idx)
            self.task_listbox.activate(idx)
            self.on_task_select(None)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to duplicate: {e}')

    def merge_tasks(self):
        selection = self.task_listbox.curselection()
        if len(selection) < 2:
            messagebox.showerror('Error', 'Select at least two tasks to merge.')
            return
        selected_files = [self.task_listbox.get(i) for i in selection]
        # Prompt for new unique task name
        new_name = simpledialog.askstring('Merge Tasks', 'Enter a name for the merged task (must end with .csv):')
        if not new_name:
            return
        if not new_name.lower().endswith('.csv'):
            new_name += '.csv'
        if new_name in self.task_manager.list_tasks():
            messagebox.showerror('Error', f'A task named "{new_name}" already exists.')
            return
        try:
            # Merge all rows from selected files
            merged_df = pd.DataFrame()
            for file in selected_files:
                df = self.task_manager.load_task(file)
                merged_df = pd.concat([merged_df, df], ignore_index=True)
            self.task_manager.save_task(new_name, merged_df)
            messagebox.showinfo('Merged', f'Tasks merged as "{new_name}".')
            self.refresh_task_list()
            # Select the new merged task in the listbox
            idx = self.task_manager.list_tasks().index(new_name)
            self.task_listbox.selection_clear(0, tk.END)
            self.task_listbox.selection_set(idx)
            self.task_listbox.activate(idx)
            self.on_task_select(None)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to merge: {e}')

    def create_task(self):
        # Prompt the user for a task title
        title = simpledialog.askstring("Create Task", "Enter task title (must end with .csv):")
        if title:
            if not title.endswith('.csv'):
                title += '.csv'
            # Check if the title is unique
            if title in self.task_listbox.get(0, tk.END):
                messagebox.showerror("Error", "A task with this title already exists.")
                return
            # Prompt the user to select a template
            templates_dir = os.path.join(os.path.dirname(__file__), '../shhh/tasks/Templates')
            templates = [f for f in os.listdir(templates_dir) if f.endswith('.csv')]
            if not templates:
                messagebox.showerror("Error", "No templates found in the Templates directory.")
                return
            template = simpledialog.askstring("Select Template", f"Available templates: {', '.join(templates)}. Enter the template name:")
            if not template:
                return
            if template not in templates:
                messagebox.showerror("Error", "Invalid template selected.")
                return
            # Create a new task file in the TASKS directory using the selected template
            new_task_path = os.path.join('TASKS', title)
            template_path = os.path.join(templates_dir, template)
            with open(template_path, 'r') as f:
                template_content = f.read()
            with open(new_task_path, 'w') as f:
                f.write(template_content)
            self.refresh_task_list()
            messagebox.showinfo("Success", f"Task '{title}' created successfully using template '{template}'.")

    def on_close(self):
        self.file_watcher.stop()
        self.root_destroy()

    def root_destroy(self):
        # Helper to allow testability/mocking
        self.main_frame.master.destroy()

    def cancel_edits(self):
        if self.current_task:
            try:
                df = self.task_manager.load_task(self.current_task)
                self.current_df = df
                if not df.empty:
                    # If using tabs (multiple products)
                    if hasattr(self, 'notebook') and hasattr(self, 'tab_field_widgets') and self.notebook.winfo_exists():
                        # Get currently selected tab/product
                        current_tab_index = self.notebook.index(self.notebook.select())
                        product = self.notebook.tab(current_tab_index, 'text')
                        field_widgets = self.tab_field_widgets[product]
                        prod_rows = df[df['product'] == product]
                        if not prod_rows.empty:
                            row = prod_rows.iloc[0]
                            # Update all fields for this product
                            for field, entry in field_widgets.items():
                                value = row.get(field, '')
                                if value is None or (isinstance(value, float) and math.isnan(value)):
                                    value = ''
                                entry.delete(0, tk.END)
                                entry.insert(0, str(value))
                            
                            # Rebuild the filters UI for this product
                            current_tab_frame = self.notebook.winfo_children()[current_tab_index]
                            for child in current_tab_frame.winfo_children():
                                if hasattr(child, 'filters_list') and hasattr(child, 'row_data'):
                                    # Found the filters_frame for this tab
                                    child.destroy()  # Remove old filters UI
                                    # Rebuild filters UI with original values
                                    extra_filter_entry = field_widgets.get('extra_filter')
                                    if extra_filter_entry:
                                        self.build_filters_ui(current_tab_frame, extra_filter_entry, row.get('extra_filter', ''), row_data=row)
                                    break
                    else:
                        # Single product case
                        row = df.iloc[0]
                        # Update main fields
                        for field, entry in self.field_widgets.items():
                            value = row.get(field, '')
                            if value is None or (isinstance(value, float) and math.isnan(value)):
                                value = ''
                            entry.delete(0, tk.END)
                            entry.insert(0, str(value))
                        
                        # Rebuild the filters UI
                        for child in self.right_panel.winfo_children():
                            if hasattr(child, 'filters_list') and hasattr(child, 'row_data'):
                                # Found the filters_frame
                                child.destroy()  # Remove old filters UI
                                # Rebuild filters UI with original values
                                extra_filter_entry = self.field_widgets.get('extra_filter')
                                if extra_filter_entry:
                                    self.build_filters_ui(self.right_panel, extra_filter_entry, row.get('extra_filter', ''), row_data=row)
                                break
            except Exception as e:
                messagebox.showerror('Error', f'Failed to reload: {e}')

    # Helper function to build the filters UI for a given parent frame
    def build_filters_ui(self, parent, extra_filter_entry, initial_filter_value, row_data=None, filters_list=None):
        # Ensure 'filters' is always bound
        filters = [] # Initialize filters
        if filters_list is None:
             filters.extend(self.parse_extra_filter(initial_filter_value))
        else:
             filters.extend(filters_list) # Use the provided list

        filters_frame = tk.Frame(parent) # Main frame for filters section
        filters_frame.pack(fill=tk.X)

        # Header for the filter table
        header_frame = tk.Frame(filters_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=(10, 2))
        tk.Label(header_frame, text='Section', font=('Arial', 12, 'bold')).grid(row=0, column=0, padx=5)
        tk.Label(header_frame, text='Price', font=('Arial', 12, 'bold')).grid(row=0, column=1, padx=5)
        tk.Label(header_frame, text='', font=('Arial', 12, 'bold')).grid(row=0, column=2, padx=5)

        # Frame to hold the actual filter rows, Add, and Cancel buttons - this is the part we will rebuild
        filter_table_content_frame = tk.Frame(filters_frame)
        filter_table_content_frame.pack(fill=tk.X)

        # Store necessary context on the filters_frame for callbacks
        filters_frame.filters_list = filters
        filters_frame.extra_filter_entry = extra_filter_entry
        filters_frame.row_data = row_data # Keep original row data for cancel
        filters_frame.filter_table_content_frame = filter_table_content_frame # Store reference to the frame to rebuild

        def on_delete_row(idx, current_filters, current_entry, parent_frame_for_rebuild, original_row_data):
            current_filters.pop(idx)
            # Rebuild *only* the filter table content frame
            # Use filters_frame.filter_table_content_frame as the parent for rebuilding
            content_frame = filters_frame.filter_table_content_frame
            for widget in content_frame.winfo_children():
                 widget.destroy() # Clear existing content
            self.build_filter_table_content(content_frame, current_entry, current_filters, on_delete_row, on_add_row, on_cancel, row_data)
            # Update extra_filter field after deleting
            ef_val = ', '.join(f'{s}:{p}' for s, p in current_filters if s and p)
            current_entry.delete(0, tk.END)
            current_entry.insert(0, ef_val)

        def on_add_row(current_filters, current_entry, parent_frame_for_rebuild, original_row_data):
            # Get current values from all existing rows before rebuilding
            current_values = []
            content_frame = filters_frame.filter_table_content_frame
            for section_var, price_var, _ in content_frame.filter_rows:
                current_values.append((section_var.get().strip(), price_var.get().strip()))
            
            # Update the filters list with current values
            current_filters.clear()
            current_filters.extend(current_values)
            # Add the new empty row
            current_filters.append(('', ''))
            
            # Rebuild the filter table content
            for widget in content_frame.winfo_children():
                 widget.destroy() # Clear existing content
            self.build_filter_table_content(content_frame, current_entry, current_filters, on_delete_row, on_add_row, on_cancel, row_data)

        def on_cancel(current_entry, parent_frame_for_rebuild, original_row_data):
            # This function is no longer needed as the filter Cancel button is removed.
            pass

        # Add trace callback to extra_filter_entry to detect and create filters
        def on_extra_filter_change(*args):
            text = extra_filter_entry.get().strip()
            if text:
                # Parse the text to find potential filters
                new_filters = self.parse_extra_filter(text)
                if new_filters:
                    # Update the filters list
                    filters.clear()
                    filters.extend(new_filters)
                    # Rebuild the filter table
                    content_frame = filters_frame.filter_table_content_frame
                    for widget in content_frame.winfo_children():
                        widget.destroy()
                    self.build_filter_table_content(content_frame, extra_filter_entry, filters, on_delete_row, on_add_row, on_cancel, row_data)

        extra_filter_entry.bind('<KeyRelease>', on_extra_filter_change)

        # Build the initial filter table content
        self.build_filter_table_content(filter_table_content_frame, extra_filter_entry, filters, on_delete_row, on_add_row, on_cancel, row_data)

        return filters_frame # Return the main filters frame

    def build_filter_table_content(self, parent_content_frame, extra_filter_entry, filters_list, on_delete_row, on_add_row, on_cancel, original_row_data):
        parent_content_frame.filter_rows = [] # Store filter rows specific to this instance on the content frame
        for i, (section, price) in enumerate(filters_list):
            row_frame = tk.Frame(parent_content_frame)
            row_frame.pack(fill=tk.X, padx=20, pady=2)
            section_var = tk.StringVar(value=section)
            price_var = tk.StringVar(value=price)
            section_entry = tk.Entry(row_frame, textvariable=section_var, font=('Arial', 12), width=30)  # Increased width for grouped sections
            section_entry.grid(row=0, column=0, padx=5)
            price_entry = tk.Entry(row_frame, textvariable=price_var, font=('Arial', 12), width=10)
            price_entry.grid(row=0, column=1, padx=5)

            # Add trace callbacks to both section and price variables
            def update_extra_filter(*args, idx=i):
                # Get current values from all rows
                current_filters = []
                for section_var, price_var, _ in parent_content_frame.filter_rows:
                    section_val = section_var.get().strip()
                    price_val = price_var.get().strip()
                    if section_val and price_val:  # Only add if both fields have values
                        current_filters.append((section_val, price_val))
                
                # Update extra_filter entry
                ef_val = ', '.join(f'{s}:{p}' for s, p in current_filters)
                extra_filter_entry.delete(0, tk.END)
                extra_filter_entry.insert(0, ef_val)

            section_var.trace_add('write', update_extra_filter)
            price_var.trace_add('write', update_extra_filter)

            # Pass original_row_data to delete callback
            del_btn = tk.Button(row_frame, text='Delete', font=('Arial', 10), command=lambda idx=i: on_delete_row(idx, filters_list, extra_filter_entry, parent_content_frame.master, original_row_data))
            del_btn.grid(row=0, column=2, padx=2)
            parent_content_frame.filter_rows.append((section_var, price_var, row_frame))

        # Pass relevant context to callbacks
        # Pass original_row_data to add callback
        add_btn = tk.Button(parent_content_frame, text='Add another filter', font=('Arial', 11), command=lambda: on_add_row(filters_list, extra_filter_entry, parent_content_frame.master, original_row_data))
        add_btn.pack(pady=5)

    def parse_extra_filter(self, value):
        # Parse 'Section:Price, Section2:Price2' into [(Section, Price), ...]
        # Handle cases like 'FLR1:350, FLR2,FLR3,FLR4:326, FLR6:250'
        if not value or not isinstance(value, str):
            return []
        filters = []
        
        # Split on commas that are followed by a space and then a section:price pattern
        # This preserves commas within the section part
        parts = []
        current_part = []
        for item in value.split(','):
            item = item.strip()
            if ':' in item:
                # If we have accumulated items, add them to the current part
                if current_part:
                    current_part.append(item)
                    parts.append(','.join(current_part))
                    current_part = []
                else:
                    parts.append(item)
            else:
                current_part.append(item)
        
        # Add any remaining items
        if current_part:
            parts.append(','.join(current_part))
        
        # Process each part
        for part in parts:
            if ':' in part:
                # Split on the last colon to handle sections that might contain colons
                sections, price = part.rsplit(':', 1)
                # Keep the sections together as one filter
                filters.append((sections.strip(), price.strip()))
            elif part:
                filters.append((part.strip(), ''))
        
        return filters

if __name__ == "__main__":
    root = tk.Tk()
    app = SilentlyTaskGeneratorApp(root)
    root.mainloop() 