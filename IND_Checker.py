import pandas as pd
import re
import string
import streamlit as st

# --- Load IND Excel ---
ind_df = pd.read_excel("ind.XLSX")

# --- Normalize & Match Functions ---
def normalize_name(name):
    name = name.lower()
    name = re.sub(r'\b(b\.v\.|bv|n\.v\.|nv|ltd|inc|llc)\b', '', name)
    name = name.translate(str.maketrans('', '', string.punctuation))
    return name.strip()

def refine_company_name(name):
    parts = name.split('\n')
    candidates = [p.strip() for p in parts if re.search(r'[A-Z]', p) and not re.search(r'(hour|day|apply|viewed|response|typically)', p, re.IGNORECASE)]
    return candidates[-1] if candidates else name.strip()

def is_fast_whole_word_match(a, b):
    return f" {a} " in f" {b} " or f" {b} " in f" {a} "

# --- Streamlit UI ---
st.title("IND Company Matcher")

st.markdown("Paste the full job description text below (copied from LinkedIn or similar):")
job_description = st.text_area("Job Description", height=300)

if st.button("Match Companies"):
    if job_description.strip() == "":
        st.warning("Please paste a job description first.")
    else:
        # Extract company names
        extracted_raw = re.findall(r'([A-Za-z0-9&\-\.\'\s]+?)\s+logo', job_description)
        refined_names = list({refine_company_name(name.strip()) for name in extracted_raw})

        # Normalize
        normalized_extracted = {normalize_name(name): name for name in refined_names}
        normalized_ind = {normalize_name(name): name for name in ind_df['Organisation'].dropna().unique()}

        # Match
        matches = []
        for norm_ext, orig_ext in normalized_extracted.items():
            for norm_ind, orig_ind in normalized_ind.items():
                if is_fast_whole_word_match(norm_ext, norm_ind):
                    matches.append(f"{orig_ext} : {orig_ind}")
                    break

        # Display results
        if matches:
            st.success("? Matches found:")
            for match in matches:
                st.text(match)
        else:
            st.warning("No IND-listed companies found in the job description.")
