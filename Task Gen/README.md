📘 Silently Task Generator — Full Application Documentation
🧠 Overview
The Silently Task Generator is a native Windows desktop application that automates the creation, editing, deletion, duplication, and merging of task CSV files used in the ticket reselling operation. Each task corresponds to a Ticketmaster/LiveNation event and includes a list of account-level task rows.

This app replaces manual duplication of templates and entry of values like event URLs, price filters, and presale codes, while ensuring file consistency and preventing duplication.

🧱 System Architecture
📂 Directory Structure
plaintext
Copy
Edit
C:\Users\Administrator\Desktop\shhh\
├── tasks\
│   ├── TASKS\            <-- Active task files (1 per event)
│   └── Templates\        <-- Reusable templates for different configurations
TASKS/: Where the final task files are saved and read from

Templates/: Contains reusable base CSVs with static fields

🖥️ App Type
Environment: Windows 10

Framework: Python (preferred) + tkinter GUI

File Watcher: Uses watchdog to monitor live changes to the TASKS/ directory

📑 File Format Summary
✅ Task Files (CSV)
Each file = 1 event = 1 task

Each row = 1 account’s task

Templates provide 90% of static data (account IDs, proxy, mode, etc.)

Dynamic columns:

Product (event URL)

Quantity (defaults to 2 from template)

Presale (optional)

Price_range (optional)

Extra_filter (built from structured UI input)

📋 Template Files
Stored in Templates/

Each is a fully structured CSV with pre-filled static data

When creating a task, a template is selected and used as the base

🧩 Dynamic Field Behavior
Field	Required	Description
Product	Yes	Event URL
Quantity	No	Always defaulted to 2 from template
Presale	No	Optional presale code
Price_range	No	Optional price filter
Extra_filter	No	Built from UI with Section/Price table

🧠 Extra Filter Logic
UI Input (Table Form):
Section	Price
100	100
105-108	250
FloorA	150

Generates CSV Column:
plaintext
Copy
Edit
100:100, 105-108:250, FloorA:150
Each entry follows format:

ruby
Copy
Edit
<Section>:<Price>
Joined by comma and space.

🧭 App Features
🗂 Task List Panel
Live-displays all files from TASKS/

Real-time updates when files are added, deleted, or renamed

Clicking on a task opens detail panel

🧾 Task Detail Panel
View/edit dynamic fields

Edit button unlocks all editable fields

Fields:

Product

Presale

Price Range

Extra Filter (via table)

Save button rewrites the file

Rename functionality prevents overwriting

➕ New Task Creation
Select a template

Fill dynamic fields

Name the task (must be unique)

Save generates a copy of the template with dynamic fields populated

✏️ Edit Task
Loads selected CSV

Unlocks editable fields

On save, overwrites file

❌ Delete Task
Two-step confirmation dialog

Permanently deletes file from TASKS/

📑 Duplicate Task
Prefills new task form with selected task’s values

Forces rename on save

🔗 Merge Tasks
Multi-select tasks from list

Merges all rows into a copy of the first-selected file

Prompts for new task name

Combined task saved to TASKS/

🔄 File Watcher Behavior
Monitors TASKS/ in real time

When a .csv file is created, deleted, or renamed:

UI list updates instantly

Internal cache is refreshed

Built using watchdog.Observer

⚙️ Component Breakdown
📁 file_watcher.py
Monitors TASKS folder

Triggers UI refresh on events

📁 task_manager.py
Loads/saves CSVs

Applies dynamic values to template rows

Handles merging, duplication, and field updates

📁 ui_main.py
Launches main window

Renders task list, form panels

Manages state and button logic

📁 extra_filter_builder.py
Converts UI inputs (section/price) into valid Extra_filter string

🚦 User Workflow Examples
Create a New Task
Click New Task

Select template from dropdown

Fill:

Product: https://ticketmaster.com/event123

Presale: ILOVECODES (optional)

Price Range: 150-500 (optional)

Extra Filters:

less
Copy
Edit
Section | Price
100     | 100
FloorA  | 200
Enter name: drake-boston-5pm

Click Save

Task appears in task list

Edit an Existing Task
Click on drake-boston-5pm

Click Edit

Modify Extra Filters or Presale

Click Save

Delete a Task
Click Delete

Confirm in 2-step dialog

Task removed from folder and UI

Duplicate a Task
Click Duplicate on an existing task

Fields prefilled

Change task name

Click Save

Merge Tasks
Ctrl+Click to select multiple tasks

Click Merge

Enter new task name

All rows combined into one file

🧪 Validation Rules
No duplicate filenames allowed in TASKS/

Event URL (Product) must be filled before save

All other fields are optional

App doesn’t block “empty” task files — controller has freedom

🛠 Dependencies
pandas — for reading/writing CSVs

watchdog — for file system monitoring

tkinter — UI framework

ttkbootstrap (optional) — improved styling for tkinter

