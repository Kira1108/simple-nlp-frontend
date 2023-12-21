import streamlit as st
from utils import (
    create_default_label, 
    get_labelset_names,
    save_labelset)
from io import StringIO

def create_side_bar(db):
    with st.sidebar:
        st.markdown("# Document Query Options")
        
        # select label set to annotate data  
        st.markdown("**Select Label Set**")
        label_set = st.selectbox("Label Set", get_labelset_names(), key = "use_label_set")
        
        # select which metadatafield to annotate
        st.markdown("Choose which metadata field to annotate on")
        annot_field = st.selectbox("Annotation Field", list(db.random_doc().metadata.keys()), key = "meta_field_annot")

        st.markdown("**Create Label Set**")
        col1, col2 = st.columns(2)
        with col1:
            uploaded_file = st.file_uploader("Upload Label Set", type=["txt"], key="label_set_upload")
        with col2:
            if uploaded_file is not None:
                content = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
                label_set_name = st.text_input("Label Set Name", key="label_set_name", value=uploaded_file.name.split(".")[0])
                if st.button("Upload", key="label_set_upload_button", use_container_width=True):
                    save_labelset(label_set_name, content)
                    st.success(f"Uploaded label set `{label_set_name}`")
        
        # how many similar documents to retrieve
        st.markdown("**Query Settings:·**")
        n_results = st.number_input(label = "Number of Results", min_value =  1, key = 'n_results',value = 400)
        
        # n_results = st.slider("Number of Results", 1, 1000, 400, 10, key="n_results")
        st.markdown("**Create/Reset Metadata Field**")
        
        # create a metadata field with default value
        col1, col2 = st.columns(2)
        with col1:
            k = st.text_input("Meta Data Name", key="label_name")
        with col2:
            v = st.text_input("Meta Data Value", key="label_value")
        if st.button("Create", key="create_label", use_container_width=True):
            create_default_label(db, k, v)
            st.success(f"Created metadata `{k}` with value `{v}`")
            
        # delete a metadata field  
        st.markdown("**Delete Metadata Field**")
        del_key = st.text_input("Delete Meta Data Name", key="del_label_name")
        if st.button("Delete", key="del_label", use_container_width=True):
            db.delete_by_key(del_key)
            st.success(f"Deleted metadata `{del_key}`")
             
    return n_results, label_set, annot_field