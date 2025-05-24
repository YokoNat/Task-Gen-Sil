# Silently Task Generator — Implementation Plan

## Overview
This document outlines the step-by-step plan for implementing the requested changes to the Silently Task Generator application. The plan is based on the user's notes and aims to enhance the UI and functionality while preserving existing features.

## Step-by-Step Plan

### 1. Add a "Create Task" Button
- **Description:** Add a "Create Task" button to the UI. When clicked, prompt the user to enter a title for the new task. Ensure that the title is unique and ends with `.csv`.
- **Implementation:**
  - Add a button labeled "Create Task" in the UI.
  - On click, prompt the user for a task title.
  - Validate the title to ensure it is unique and ends with `.csv`.
  - If valid, create a new task file in the TASKS directory.

### 2. Template Selection for New Tasks
- **Description:** When creating a new task, prompt the user to select a template from the Templates directory.
- **Implementation:**
  - List available templates from the Templates directory.
  - Allow the user to select a template.
  - Use the selected template as the base for the new task file.

### 3. Display Dynamic Values for Existing Tasks
- **Description:** When an existing task is selected, display the values for Product, Presale, Price Range, and Extra Filter dynamically.
- **Implementation:**
  - Ensure that the UI reflects the current values from the CSV file for each field.
  - Update the UI to show the values dynamically when a task is selected.

### 4. Extra Filter Field Enhancement
- **Description:** Modify the Extra Filter field to allow users to input Section and Price separately, and combine them into the format `Section:Price`.
- **Implementation:**
  - Create two input fields under Extra Filter: one for Section and one for Price.
  - Add a "+" button to allow users to add additional section filters.
  - Combine the inputs into the format `Section:Price` and update the Extra Filter field accordingly.

### 5. Handling Multiple Products in Merged Tasks
- **Description:** If a task has multiple products (e.g., after merging), display tabs for each product, allowing users to modify fields specific to each product.
- **Implementation:**
  - Check the number of unique products in the task file.
  - If more than one product exists, create tabs for each product.
  - Allow users to switch between tabs to modify fields specific to each product.

### 6. Testing and Validation
- **Description:** Thoroughly test all new features and modifications to ensure they work as expected.
- **Implementation:**
  - Write test cases for each new feature.
  - Validate the UI and functionality in various scenarios, including edge cases.

### 7. Documentation and User Guide
- **Description:** Update the README.md and any other documentation to reflect the new features and changes.
- **Implementation:**
  - Document the new "Create Task" functionality, template selection, and Extra Filter enhancements.
  - Provide a user guide for navigating the updated UI.

## Conclusion
This plan provides a structured approach to implementing the requested changes. Each step is designed to be modular and testable, ensuring a smooth development process. Once this plan is approved, we will proceed to implement each step one at a time. 