import chromadb
from nlp_toolkit.vectordbs import ChromaCrud
from nlp_toolkit.embedders import SentenceEmbedder
import streamlit as st
import pandas as pd
from utils import get_options
from sidebar import create_side_bar

st.set_page_config(layout="wide",page_title="Similarity Annotation Tool")

if not "current_id" in st.session_state:    
    st.session_state.current_id = 0
if not "doc" in st.session_state:
    st.session_state.doc = None
if not "recommends" in st.session_state:
    st.session_state.recommends = None

@st.cache_resource()
def get_db():
    storage = "./chroma_storage"
    client = chromadb.PersistentClient(path=storage)
    collection = client.get_or_create_collection(
        name="app", 
        embedding_function=SentenceEmbedder().make_chroma(),
        metadata={"hnsw:space": "cosine"})
    return ChromaCrud(collection, storage)

def get_data(n_results):
    db = get_db()
    return db.recommend(n_results = n_results)

def get_recommends(doc, *args, **kwargs):
    db = get_db()
    return db.recommend_by_doc(doc, *args, **kwargs)
    
st.markdown("# Similarity Annotation Tool")
st.markdown("----")

db = get_db()

n_results, label_set, annot_field = create_side_bar(db)
        
if st.session_state.doc is None:
    doc, recommends = get_data(n_results)
    st.session_state.doc = doc
    st.session_state.recommends = recommends

col1, col2 = st.columns(2)
with col1:
    if st.button("Change Query Doc", use_container_width=True):
        doc, recommends = get_data(n_results)
        st.session_state.doc = doc
        st.session_state.recommends = recommends
        st.session_state.current_id = 0
    st.markdown("#### Query Document")
    st.data_editor(pd.DataFrame(
        [{"name":k,"value":v} for k,v in st.session_state.doc.metadata.items()]
        +[{"name":"distance","value":"---"}]
    ), use_container_width=True,hide_index=True, key = 'doc_meta')
    st.markdown(st.session_state.doc.document)
    
with col2:
    col1, col2, col3, col4 = st.columns(4)
    with col2:
        if st.button("Next", use_container_width=True, key = 'next_doc'):
            st.session_state.current_id += 1
    with col1:
        if st.button("Previous", use_container_width=True, key = 'pervious_doc'):
            st.session_state.current_id -= 1
    with col3:
        if st.button("Refresh", use_container_width=True, key = 'refresh_recommends'):
            recommends = get_recommends(st.session_state.doc, n_results = n_results)
            st.session_state.recommends = recommends

    loc = st.session_state.current_id + 1 if st.session_state.current_id >=0 else len(st.session_state.recommends) + st.session_state.current_id + 1
    st.markdown("#### Recommend Document" + f" [{loc}/{len(st.session_state.recommends)}]")

    cur_doc = st.session_state.recommends[st.session_state.current_id]
    st.data_editor(pd.DataFrame(
        [{"name":k,"value":v} for k,v in cur_doc.metadata.items()] +
        [{"name":"distance","value":cur_doc.distance}]
    ), use_container_width=True,hide_index=True, key = 'sim_doc_meta')
    st.markdown(cur_doc.document)
    
    for option in get_options(label_set):
        btn = st.button(option, key=option, use_container_width=True)
        if btn:
            db.update_metafield(ids = [cur_doc.id],**{annot_field:option})
            st.success(f"Updated metadata `{annot_field}` with value `{option}`")
            recommends = get_recommends(st.session_state.doc, n_results = n_results)
            st.session_state.recommends = recommends
        

    
    