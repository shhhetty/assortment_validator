import streamlit as st
import requests
import json
import pandas as pd
from collections import Counter
import re

# Page configuration
st.set_page_config(
    page_title="Advanced Search Quality Checker",
    page_icon="🔎",
    layout="wide"
)

# Main analysis function
def run_analysis(shop_id, environment, search_keyword, check_groups, match_types, result_size):
    """
    Performs a search API call and analyzes the results for relevance.
    Also formats product data for external LLM analysis.
    """
    url = f'https://search-{environment}-dlp-adept-search.search-prod.adeptmind.app/search?shop_id={shop_id}'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "query": search_keyword,
        "size": result_size,
        "force_exploding_variants": False,
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        response.raise_for_status()

        products = response.json().get("products", [])

        if not products:
            return {"status": "error", "message": f"No products were returned for the search term '{search_keyword}'."}

        irrelevant_products_data = []
        relevant_products_data = []
        failure_reason_counter = Counter()
        llm_formatted_texts = [] #List to hold formatted text for LLM

        for i, product_payload in enumerate(products):
            # --- LLM Data Extraction ---
            title = product_payload.get('title', 'N/A')
            description = product_payload.get('description', 'N/A')
            product_text_for_llm = f"""prod {i + 1}:
title: {title}
description: {description}"""
            llm_formatted_texts.append(product_text_for_llm)

            product_as_string = json.dumps(product_payload, ensure_ascii=False).lower()
            product_as_string = product_as_string.replace('\u00a0', ' ')
            product_as_string = product_as_string.replace('\\u00a0', ' ')
            product_as_string = product_as_string.replace('  ', ' ')

            failed_group_indices = []
            # --- MODIFIED: Check each group with its specific match type ---
            for group_idx, group_variations in enumerate(check_groups):
                match_type_for_group = match_types[group_idx]
                match_found = False
                for variation in group_variations:
                    if match_type_for_group == 'Text Contains':
                        if variation in product_as_string:
                            match_found = True
                            break
                    elif match_type_for_group == 'Text Equals':
                        if re.search(r'\b' + re.escape(variation) + r'\b', product_as_string):
                            match_found = True
                            break
                if not match_found:
                    failed_group_indices.append(group_idx)

            if not failed_group_indices:
                relevant_products_data.append({
                    "Position": i + 1,
                    "Product ID": product_payload.get('product_id', 'N/A'),
                    "Product Name": title
                })
            else:
                irrelevant_products_data.append({
                    "Position": i + 1,
                    "Product ID": product_payload.get('product_id', 'N/A'),
                    "Product Name": title,
                    "failed_indices": failed_group_indices
                })
                failure_reason_counter.update(failed_group_indices)

        # --- Format Final LLM Output ---
        final_llm_output = f"search term: {search_keyword}\n\n"
        final_llm_output += "\n\n".join(llm_formatted_texts)

        return {
            "status": "success",
            "total_products": len(products),
            "relevant_products": relevant_products_data,
            "irrelevant_products": irrelevant_products_data,
            "failure_summary": failure_reason_counter,
            "llm_formatted_output": final_llm_output
        }

    except requests.exceptions.HTTPError as e:
        return {"status": "error", "message": f"API Error (Status Code: {e.response.status_code}): {e.response.text}"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Network Error: Could not connect to the API. Details: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}

# --- Streamlit UI ---
st.title("🔎 Word Checker")
st.markdown("Use this tool to check if search results contain **all** the required 'word' groups.")

with st.sidebar:
    st.header("⚙️ Configuration")
    shop_id = st.text_input("Shop ID", value="")
    environment = st.selectbox("Environment", ["prod", "staging"], index=0)
    search_result_size = st.number_input("Search Result Size", min_value=1, max_value=1000, value=500)

    # --- MODIFIED: State management for match types synchronized with check groups ---
    st.header("Check Group Management")
    if 'check_groups_state' not in st.session_state:
        st.session_state.check_groups_state = [""]
        st.session_state.match_types_state = ["Text Contains"] # Default match type

    def add_check_group():
        st.session_state.check_groups_state.append("")
        st.session_state.match_types_state.append("Text Contains") # Add default match type for new group

    def remove_check_group(index):
        st.session_state.check_groups_state.pop(index)
        st.session_state.match_types_state.pop(index) # Remove corresponding match type

    def reset_check_groups():
        st.session_state.check_groups_state = [""]
        st.session_state.match_types_state = ["Text Contains"]

    st.button("Add another check group", on_click=add_check_group, use_container_width=True)
    st.button("Reset to 1 check group", on_click=reset_check_groups, use_container_width=True)

st.subheader("Required Concepts")
st.markdown("A product is relevant **only if it contains a match from EACH group below**.")

# --- MODIFIED: UI for per-group match type selection ---
for i in range(len(st.session_state.check_groups_state)):
    st.markdown(f"**Check Group {i+1}**")
    col1, col2, col3 = st.columns([4, 2, 1])
    with col1:
        st.session_state.check_groups_state[i] = st.text_input(
            "Comma-separated variations",
            value=st.session_state.check_groups_state[i],
            key=f"check_group_input_{i}",
            label_visibility="collapsed",
            placeholder=f"e.g., hdr10+, hdr 10+, hdr 10plus"
        )
    with col2:
        st.session_state.match_types_state[i] = st.radio(
            "Match Type",
            options=["Text Contains", "Text Equals"],
            key=f"match_type_{i}",
            horizontal=True,
            label_visibility="collapsed"
        )
    with col3:
        if len(st.session_state.check_groups_state) > 1:
            st.button(f"🗑️ Delete", key=f"del_{i}", on_click=remove_check_group, args=(i,), use_container_width=True)

st.markdown("---")

with st.form("search_form"):
    st.subheader("🔍 Search and Analyze")
    search_keyword_input = st.text_input(
        "Enter the keyword to SEARCH on the API",
        placeholder="e.g., samsung hdr10+ tvs"
    )
    submitted = st.form_submit_button("Analyze Assortment", type="primary", use_container_width=True)

if submitted:
    check_group_inputs = st.session_state.check_groups_state
    
    if not all([shop_id, search_keyword_input] + [inp.strip() for inp in check_group_inputs]):
        st.warning("Please fill in all fields: Shop ID, Search Keyword, and all Check Groups cannot be empty.")
    else:
        search_keyword = search_keyword_input.strip()
        check_groups = [ [kw.strip().lower() for kw in group_str.split(',')] for group_str in check_group_inputs if group_str.strip() ]
        match_types = st.session_state.match_types_state # Get the list of match types
        
        if not check_groups:
             st.error("You must define at least one valid check group.")
        else:
            with st.spinner(f"Analyzing top {search_result_size} results for '{search_keyword}'..."):
                # --- MODIFIED: Pass the list of match types to the analysis function ---
                analysis_result = run_analysis(shop_id.strip(), environment, search_keyword, check_groups, match_types, search_result_size)

            st.subheader("📊 Assortment Quality")

            if analysis_result["status"] == "error":
                st.error(f"**Error:** {analysis_result['message']}")
            elif analysis_result["status"] == "success":
                st.markdown(f"**Search Term:** `{search_keyword}`")
                
                total = analysis_result['total_products']
                relevant_list = analysis_result['relevant_products']
                irrelevant_list = analysis_result['irrelevant_products']
                relevance_percentage = (len(relevant_list) / total * 100) if total > 0 else 0
                
                col1, col2 = st.columns(2)
                col1.metric("Relevance Score", f"{len(relevant_list)} / {total}", help="Products containing a match from ALL check groups.")
                col2.metric("Relevance Percentage", f"{relevance_percentage:.1f}%")
                
                st.markdown("---")
                
                with st.expander("📋 Formatted Output for LLM Analysis", expanded=False):
                    llm_output = analysis_result.get("llm_formatted_output", "No output generated.")
                    st.text_area(
                        label="Copy the text below to use in an external LLM tool:",
                        value=llm_output,
                        height=400,
                        key="llm_output_textarea"
                    )
                
                col_irrelevant, col_relevant = st.columns(2)
                with col_irrelevant:
                    if irrelevant_list:
                        st.error(f"🚨 Found {len(irrelevant_list)} Irrelevant Products")
                        with st.expander("Show Failure Analysis"):
                            failure_summary = analysis_result['failure_summary']
                            summary_data = []
                            for group_idx, count in sorted(failure_summary.items()):
                                group_name = f"Group {group_idx+1}: '{check_groups[group_idx][0]}...'"
                                summary_data.append({"Missing Concept Group": group_name, "Number of Products Failed": count})
                            if summary_data:
                                st.table(pd.DataFrame(summary_data))
                        
                        for item in irrelevant_list:
                            failed_reasons = [f"'{check_groups[idx][0]}...'" for idx in item['failed_indices']]
                            item["Missing Concepts"] = f"Missing: {', '.join(failed_reasons)}"
                        
                        df_irrelevant = pd.DataFrame(irrelevant_list).drop(columns=['failed_indices'])
                        st.dataframe(df_irrelevant, use_container_width=True)
                    else:
                        st.info("No irrelevant products found.")

                with col_relevant:
                    if relevant_list:
                        st.success(f"✅ Found {len(relevant_list)} Relevant Products")
                        df_relevant = pd.DataFrame(relevant_list)
                        st.dataframe(df_relevant, use_container_width=True)
                    else:
                        st.info("No relevant products found.")

                if not irrelevant_list and total > 0:
                    st.success("Perfect! All returned products were relevant.")
