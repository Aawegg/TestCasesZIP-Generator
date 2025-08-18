import streamlit as st
import os
import zipfile
import io
import re

def parse_test_cases(text):
    """Parse test case text to extract input and output for each test case."""
    test_cases = []
    # Split text into individual test cases based on "Test: #" pattern
    test_blocks = re.split(r'Test: #\d+', text)[1:]  # Skip first split (before Test #1)
    
    for block in test_blocks:
        # Extract Input and Output (mapped to Jury's answer)
        input_match = re.search(r'Input\n([\s\S]*?)(?:\nOutput|\Z)', block)
        output_match = re.search(r'Output\n([\s\S]*?)(?:\nAnswer|\Z)', block)
        
        if input_match and output_match:
            inp = input_match.group(1).strip()
            out = output_match.group(1).strip()
            if inp and out:  # Only add non-empty pairs
                test_cases.append((inp, out))
    
    return test_cases

def save_and_zip_test_cases(taskid, test_cases):
    """Save test cases to files and create a ZIP file."""
    base_dir = f"{taskid}"
    zip_dir = os.path.join(base_dir, f"{taskid}_TestCases")
    os.makedirs(zip_dir, exist_ok=True)

    # Write input/output files
    for idx, (input_data, output_data) in enumerate(test_cases, start=1):
        input_filename = os.path.join(zip_dir, f"{taskid}_Input_TestCase_{idx}.txt")
        output_filename = os.path.join(zip_dir, f"{taskid}_Output_TestCase_{idx}.txt")
        
        with open(input_filename, 'w') as f_in:
            f_in.write(input_data + '\n')
        
        with open(output_filename, 'w') as f_out:
            f_out.write(output_data + '\n')

    # Create ZIP file
    zip_path = os.path.join(base_dir, f"{taskid}_TestCases.zip")
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filename in os.listdir(zip_dir):
            file_path = os.path.join(zip_dir, filename)
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname)
    
    zip_buffer.seek(0)
    return zip_buffer, zip_path

def main():
    st.title("Codeforces Test Case Manager")

    # Problem ID
    problem_id = st.text_input("Problem ID (e.g., 1942G):", key="problem_id")

    # Initialize session state for test cases
    if "test_cases" not in st.session_state:
        st.session_state.test_cases = []

    # Form for pasting test case text
    st.subheader("Paste Test Cases")
    with st.form(key="paste_test_case_form"):
        paste_text = st.text_area("Paste test case text here:", height=200, key="paste_text")
        paste_submit = st.form_submit_button("➕ Add Pasted Test Cases")

        if paste_submit and paste_text.strip():
            new_test_cases = parse_test_cases(paste_text)
            if new_test_cases:
                st.session_state.test_cases.extend(new_test_cases)
                st.success(f"✅ Added {len(new_test_cases)} test case(s) from pasted text!")
            else:
                st.warning("No valid test cases found in the pasted text!")

    # Form for multiple test case inputs
    st.subheader("Add Multiple Test Cases Manually")
    with st.form(key="multi_test_case_form"):
        test_case_inputs = []
        test_case_outputs = []
        for i in range(5):  # Allow up to 5 test cases
            st.markdown(f"### Test Case {i+1}")
            col1, col2 = st.columns(2)
            with col1:
                inp = st.text_area(f"Input {i+1}:", height=100, key=f"input_{i}")
            with col2:
                out = st.text_area(f"Output {i+1}:", height=100, key=f"output_{i}")
            test_case_inputs.append(inp)
            test_case_outputs.append(out)
        submit_button = st.form_submit_button("➕ Add Test Cases")

        if submit_button:
            added = 0
            for i, (inp, out) in enumerate(zip(test_case_inputs, test_case_outputs)):
                inp = inp.strip()
                out = out.strip()
                if inp and out:  # Only add non-empty test cases
                    st.session_state.test_cases.append((inp, out))
                    added += 1
            if added > 0:
                st.success(f"✅ Added {added} test case(s)!")
            else:
                st.warning("No valid test cases provided (both input and output are required for each)!")

    # Buttons for other actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✏️ Edit Selected"):
            selected = st.session_state.get("selected_test_case", None)
            if selected is None:
                st.warning("Select a test case to edit!")
            else:
                new_inp = st.text_area("Edit Test Case Input:", value=st.session_state.test_cases[selected][0], key="edit_input")
                new_out = st.text_area("Edit Expected Output:", value=st.session_state.test_cases[selected][1], key="edit_output")
                if st.button("Save Changes"):
                    st.session_state.test_cases[selected] = (new_inp.strip(), new_out.strip())
                    st.success("Test case updated!")
                    st.session_state.selected_test_case = None

    with col2:
        if st.button("❌ Delete Selected"):
            selected = st.session_state.get("selected_test_case", None)
            if selected is None:
                st.warning("Select a test case to delete!")
            else:
                st.session_state.test_cases.pop(selected)
                st.success(f"✅ Test Case {selected + 1} deleted!")
                st.session_state.selected_test_case = None

    with col3:
        if st.button("💾 Save & Zip"):
            if not problem_id.strip():
                st.warning("Please enter a Problem ID!")
            elif not st.session_state.test_cases:
                st.warning("No test cases to save!")
            else:
                zip_buffer, zip_path = save_and_zip_test_cases(problem_id, st.session_state.test_cases)
                st.download_button(
                    label="Download ZIP",
                    data=zip_buffer,
                    file_name=f"{problem_id}_TestCases.zip",
                    mime="application/zip"
                )
                st.success(f"✅ ZIP created at: {zip_path}")

    # Preview of Added Test Cases
    st.subheader("Preview of Added Test Cases:")
    for idx, (inp, out) in enumerate(st.session_state.test_cases, start=1):
        display = f"#{idx} | Input: {inp[:30]}... | Output: {out[:30]}..."
        if st.button(display, key=f"select_{idx}"):
            st.session_state.selected_test_case = idx - 1

if __name__ == "__main__":
    main()