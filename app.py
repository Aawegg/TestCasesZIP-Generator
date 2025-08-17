 
import streamlit as st
import os
import zipfile
import io

def main():
    st.title("Codeforces Test Case Manager")

    # Problem ID
    problem_id = st.text_input("Problem ID (e.g., 1942G):", key="problem_id")

    # Initialize session state for test cases
    if "test_cases" not in st.session_state:
        st.session_state.test_cases = []

    # Form for multiple test case inputs
    st.subheader("Add Multiple Test Cases")
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
                base_dir = f"{problem_id}"
                os.makedirs(base_dir, exist_ok=True)
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for idx, (inp, out) in enumerate(st.session_state.test_cases, start=1):
                        in_file = f"{problem_id}_Input_TestCase_{idx}.txt"
                        out_file = f"{problem_id}_Output_TestCase_{idx}.txt"
                        zipf.writestr(in_file, inp + "\n")
                        zipf.writestr(out_file, out + "\n")
                zip_buffer.seek(0)
                st.download_button(
                    label="Download ZIP",
                    data=zip_buffer,
                    file_name=f"{problem_id}_TestCases.zip",
                    mime="application/zip"
                )
                st.success(f"📦 Saved {len(st.session_state.test_cases)} cases & created ZIP file!")

    # Preview of Added Test Cases
    st.subheader("Preview of Added Test Cases:")
    for idx, (inp, out) in enumerate(st.session_state.test_cases, start=1):
        display = f"#{idx} | Input: {inp[:30]}... | Output: {out[:30]}..."
        if st.button(display, key=f"select_{idx}"):
            st.session_state.selected_test_case = idx - 1

if __name__ == "__main__":
    main()