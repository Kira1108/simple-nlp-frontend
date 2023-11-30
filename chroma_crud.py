import random
from chromadb import Collection
from dataclasses import dataclass
from typing import List, Tuple
import pandas as pd
import datetime
import uuid
import numpy as np
import sqlite3

def delete_metadata_by_key(key_name:str):

    with sqlite3.connect("/Users/wanghuan/Projects/chroma_crud/chroma_storage/chroma.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute(f"delete from embedding_metadata where key ='{key_name}';")
        conn.commit()

@dataclass
class Document:
    """A document has a id, embeding, metadata and document text."""
    
    id: str
    embedding: List[float] = None
    metadata: dict = None
    document:str = None
    
@dataclass
class QueryResult(Document):
    distance: float = None

@dataclass
class ChromaCrud:
    
    collection:Collection
    
    def __post_init__(self):
        self._ids = None

    @property
    def ids(self) -> list:
        """Get ids of all documents in collection"""
        
        if self._ids is None:
            self._ids = self.collection.get(include = [])['ids']
        
        return self._ids

    def random_doc(self, where:dict = None) -> str:
        
        """Get a random document from the collection"""
        id_ = random.choice(self.ids)
        query_result = self.collection.get(
            ids = [id_], 
            include = ['documents','metadatas','embeddings'], 
            where = where)
        
        return Document(id = query_result['ids'][0], 
                        metadata = query_result['metadatas'][0],
                        embedding = query_result['embeddings'][0],
                        document = query_result['documents'][0])
    
    def random_docs(self, n:int = 10, where:dict = None) -> List[Document]:
        """Get n random documents from the collection"""
        n = min(n, len(self.ids))
        ids = random.sample(self.ids, n)
        docs = self.collection.get(ids = ids, include = ['documents','metadatas'], where = where)
        return  [Document(id = id_, document = docs['documents'][i], metadata = docs['metadatas'][i]) 
                 for i, id_ in enumerate(ids)]
    
    def query(self, query_text:str, n_results:int = 10 , where:dict = None) -> dict:
        """Query database with a query text string"""
        rst = self.collection.query(
            query_texts = [query_text], 
            n_results = n_results, 
            include = ["metadatas", "documents", "distances","embeddings"], where = where)
        
        query_docs = []
        for index, id_ in enumerate(rst['ids'][0]):
            embedding = rst['embeddings'][0][index] if rst['embeddings'] is not None else None
            metadata = rst['metadatas'][0][index] if rst['metadatas'] is not None else None
            document = rst['documents'][0][index] if rst['documents'] is not None else None
            result_doc = QueryResult(id=id_, embedding=embedding, metadata=metadata, 
                                    document=document, distance=rst['distances'][0][index])
            query_docs.append(result_doc)
            
        return query_docs

    
    def recommend(self, n_results:int = 10, where:dict = None, where_query:dict = None) -> Tuple[Document, List[QueryResult]]:
        """Randomly select a document and query the database for n_results similar documents"""
        doc = self.random_doc(where = where)
        query_results = self.query(doc.document, n_results = n_results, where = where_query)
        return doc, query_results
    
    def insert_dateframe(self, 
                         df:pd.DataFrame, 
                         id_col:str = None, 
                         doc_col:str = "text", 
                         meta_cols:list = None, 
                         embeddings:List[List[float]] = None) -> None:
        
        if id_col is None: 
            ids =  [str(uuid.uuid4()) for _ in range(len(df))]
            id_col = ""
        else:
            ids = df[id_col].astype(str).tolist()
        
        # create time and updatetime columns
        df['create_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df['update_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if embeddings is not None and isinstance(embeddings, np.ndarray):
            embeddings = embeddings.tolist()
            
        documents = df[doc_col].tolist()
    
        if meta_cols is None:
            meta_cols = [col for col in df.columns 
                            if col not in [id_col, doc_col]]  

        metadatas = df[meta_cols].to_dict(orient = 'records')

        params = dict(
            documents = documents,
            embeddings = embeddings,
            metadatas = metadatas,
            ids = ids
        )

        params = {k:v for k,v in params.items() if v is not None}
        self.collection.add(**params)
        print("Successful added to collection")
        
        
    def insert_dataframe_batch(self,
                         df:pd.DataFrame, 
                         id_col:str = None, 
                         doc_col:str = "text", 
                         meta_cols:list = None, 
                         embeddings:List[List[float]] = None,
                         batch_size:int = 256) -> None:
        
        n_batchs = int(np.ceil(len(df)/batch_size))
    
        for i in range(n_batchs):
            print(f"Inserting batch {i+1}/{n_batchs}")
            
            if embeddings is not None:
                batch_embedding = embeddings[i*batch_size:(i+1)*batch_size]
            else:
                batch_embedding = None
                
            self.insert_dataframe(
                df = df.iloc[i*batch_size:(i+1)*batch_size], 
                id_col = id_col,
                doc_col = doc_col,
                meta_cols = meta_cols,
                embeddings = batch_embedding)
        
        print("Successful added all data to collection")
    
    def update_metafield(self, ids = None, **kwargs) -> None:
        """The only thing you can update is the metafield."""
        
        # if no ids is provided, update all ids.
        if ids is None:
            ids = self.collection.get(include=[])['ids']
        
        # add an updatetime to update meta dictionary  
        kwargs.update(update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        self.collection.update(
            ids = ids,
            metadatas = [kwargs] * len(ids)
        )
        print("Update metdata successfully.")    
        
    def delete_by_key(self, key_name):
        delete_metadata_by_key(key_name)