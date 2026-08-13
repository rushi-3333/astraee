import os
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions

# ============================================================
# Paths
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DB_DIR = os.path.join(BASE_DIR, 'chroma_db')

client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name='all-MiniLM-L6-v2'
)

# ============================================================
# Dataset Configuration
# ============================================================

DATASETS_CONFIG = {
    'ride_collection': {
        'csv_path': os.path.join(
            BASE_DIR,
            'Ride_model',
            'hyderabad_ride_comparison_dataset.csv'
        ),
        'text_fields': [
            'platform',
            'pickup_location',
            'destination',
            'vehicle_type',
            'traffic_level',
            'weather_condition',
            'demand_level'
        ],
        'id_field': 'ride_id'
    },

    'food_collection': {
        'csv_path': os.path.join(
            BASE_DIR,
            'Food_model',
            'food_comparison_dataset_swiggy_zomato.csv'
        ),
        'text_fields': [
            'platform',
            'food_item',
            'restaurant_name',
            'category',
            'demand_level',
            'time_slot'
        ],
        'id_field': 'food_id'
    },

    'medicine_collection': {
        'csv_path': os.path.join(
            BASE_DIR,
            'medicine_model',
            'medicine_comparison_dataset_netmeds_pharmeasy_apollo.csv'
        ),
        'text_fields': [
            'platform',
            'medicine_name',
            'composition',
            'manufacturer',
            'pack_size',
            'stock_status'
        ],
        'id_field': 'medicine_id'
    },

    'shopping_collection': {
        'csv_path': os.path.join(
            BASE_DIR,
            'Shopping_model',
            'shopping_comparison_dataset_amazon_flipkart_ajio.csv'
        ),
        'text_fields': [
            'platform',
            'product_name',
            'brand',
            'category',
            'subcategory',
            'seller_name'
        ],
        'id_field': 'product_id'
    }
}

# ============================================================
# Metadata Cleaning
# ============================================================

def sanitize_metadata(row_dict):

    clean = {}

    for key, value in row_dict.items():

        if pd.isna(value):
            clean[key] = ''

        elif isinstance(value, (int, float, str, bool)):
            clean[key] = value

        else:
            clean[key] = str(value)

    return clean

# ============================================================
# Build Search Document
# ============================================================

def build_document(row, fields):

    parts = []

    for field in fields:

        if field in row.index and pd.notna(row[field]):
            parts.append(str(row[field]))

    return ' '.join(parts)

# ============================================================
# Ingest Dataset
# ============================================================

def ingest_dataset(collection_name, config):

    csv_path = config['csv_path']

    if not os.path.exists(csv_path):
        print(f'[ERROR] File not found: {csv_path}')
        return

    print(f'Loading {collection_name}...')
    print(f'CSV: {csv_path}')

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    text_fields = config['text_fields']
    id_field = config['id_field']

    missing = [
        field for field in text_fields + [id_field]
        if field not in df.columns
    ]

    if missing:
        print(f'[ERROR] Missing columns in {collection_name}: {missing}')
        return

    try:
        client.delete_collection(collection_name)
        print(f'Existing collection {collection_name} removed.')
    except Exception:
        pass

    collection = client.create_collection(
        name=collection_name,
        embedding_function=embedding_fn,
        metadata={'hnsw:space': 'cosine'}
    )

    ids = []
    documents = []
    metadatas = []

    for idx, row in df.iterrows():

        document = build_document(row, text_fields)

        doc_id = (
            str(row[id_field])
            if pd.notna(row[id_field])
            else f'{collection_name}_{idx}'
        )

        ids.append(doc_id)
        documents.append(document)
        metadatas.append(sanitize_metadata(row.to_dict()))

    batch_size = 1000

    for i in range(0, len(ids), batch_size):

        collection.add(
            ids=ids[i:i+batch_size],
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size]
        )

        print(
            f'Added {min(i+batch_size, len(ids))}/{len(ids)} documents'
        )

    print(
        f'{collection_name} completed '
        f'({collection.count()} documents).\\n'
    )

# ============================================================
# Main
# ============================================================

if __name__ == '__main__':

    print('='*60)
    print('Building ASTRAE ChromaDB')
    print('='*60)

    for collection_name, config in DATASETS_CONFIG.items():
        ingest_dataset(collection_name, config)

    print('='*60)
    print('ChromaDB build completed successfully!')
    print('='*60)