import streamlit as st
import pandas as pd
import networkx as nx
import community.community_louvain as community_louvain
import zipfile

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Smart RecSys Demo", layout="wide")

st.title("🛒 Smart RecSys: Motor de Recomendación Contextual")
st.markdown("""
**Bienvenido al checkout del futuro.** Selecciona productos para el carrito y mira cómo nuestra IA detecta el contexto y personaliza las ofertas.
""")

# ==========================================
# 1. CARGA DE DATOS (CACHEADA)
# ==========================================
@st.cache_resource
def load_data_and_models():
    print("Cargando datos para la Demo...")
    
    # 1. Cargar Datos Crudos
    with zipfile.ZipFile('data/order_products__prior.csv.zip', 'r') as z:
        order_details = pd.read_csv(z.open('order_products__prior.csv'))
    with zipfile.ZipFile('data/products.csv.zip', 'r') as z:
        products = pd.read_csv(z.open('products.csv'))
        
    # 2. Filtrar Top Productos (Para velocidad de la demo)
    top_n = 1000
    top_products = order_details['product_id'].value_counts().head(top_n).index
    df_filtered = order_details[order_details['product_id'].isin(top_products)]
    df_merged = pd.merge(df_filtered, products[['product_id', 'product_name']], on='product_id')
    
    # 3. Construir Grafo y Comunidades (Lógica Unidad 5)
    df_pairs = pd.merge(df_merged, df_merged, on='order_id')
    df_pairs = df_pairs[df_pairs['product_id_x'] < df_pairs['product_id_y']]
    edge_weights = df_pairs.groupby(['product_name_x', 'product_name_y']).size().reset_index(name='weight')
    
    G = nx.Graph()
    for _, row in edge_weights.iterrows():
        G.add_edge(row['product_name_x'], row['product_name_y'], weight=row['weight'])
        
    pagerank = nx.pagerank(G, weight='weight')
    partition = community_louvain.best_partition(G, weight='weight')
    
    # 4. Pre-calcular métricas simples de co-ocurrencia (Simulación de Reglas)
    # Para la demo en vivo, usamos una matriz de correlación simple como proxy de las reglas
    # para que sea ultra-rápido al cambiar opciones.
    basket_matrix = df_merged.groupby(['order_id', 'product_name'])['product_id'].count().unstack().fillna(0)
    cooc_matrix = basket_matrix.T.dot(basket_matrix)
    
    return products, G, pagerank, partition, cooc_matrix, list(G.nodes())

# Cargamos todo (esto tarda unos segundos solo la primera vez)
with st.spinner('Iniciando el cerebro de Smart RecSys...'):
    products_df, G, pagerank, partition, cooc_matrix, product_list = load_data_and_models()

# ==========================================
# 2. INTERFAZ DE USUARIO (SIDEBAR)
# ==========================================
st.sidebar.header("🛍️ Tu Carrito")
carrito = st.sidebar.multiselect(
    "¿Qué estás comprando hoy?",
    options=product_list,
    default=['Bag of Organic Bananas', 'Organic Hass Avocado']
)

# ==========================================
# 3. MOTOR DE RANKING (LTR)
# ==========================================
if carrito:
    # 1. Detectar Contexto del Carrito
    comm_ids = [partition.get(item, -1) for item in carrito]
    carrito_comm = max(set(comm_ids), key=comm_ids.count)
    
    st.subheader(f"🔍 Contexto Detectado: Comunidad #{carrito_comm}")
    if carrito_comm == 0: # Ajustar según tus resultados reales, suele ser orgánicos
        st.info("El sistema ha detectado un perfil **'Saludable / Orgánico'**.")
    else:
        st.info(f"Perfil de compra detectado basado en la comunidad topológica {carrito_comm}.")

    # 2. Generar Candidatos
    # Buscamos productos conectados a los del carrito
    candidates = set()
    for item in carrito:
        if item in G:
            neighbors = list(G.neighbors(item))
            candidates.update(neighbors)
    
    # Eliminar los que ya están en el carrito
    candidates = [c for c in candidates if c not in carrito]
    
    # 3. Calcular Scores (LTR)
    ranking_data = []
    for prod in candidates:
        # Score de Co-ocurrencia (Proxy de Lift para demo rápida)
        cooc_score = sum([cooc_matrix.at[item, prod] for item in carrito])
        
        # Score de Comunidad
        is_same_comm = 1 if partition[prod] == carrito_comm else 0
        
        # Score de Autoridad
        pr = pagerank[prod]
        
        # Fórmula LTR simplificada 
        final_score = (cooc_score * 0.1) + (is_same_comm * 100) + (pr * 100)
        
        ranking_data.append({
            'Producto': prod,
            'Score': final_score,
            'Misma Comunidad': '✅' if is_same_comm else '❌',
            'Autoridad (PR)': f"{pr:.4f}"
        })
    
    # Ordenar
    df_rank = pd.DataFrame(ranking_data).sort_values(by='Score', ascending=False).head(5)
    
    # ==========================================
    # 4. MOSTRAR RESULTADOS
    # ==========================================
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Top 5 Recomendaciones Personalizadas")
        st.dataframe(df_rank, use_container_width=True)
        
        # Gráfico de barras
        st.bar_chart(df_rank.set_index('Producto')['Score'])

    with col2:
        st.subheader("🧠 ¿Por qué?")
        top_prod = df_rank.iloc[0]['Producto']
        st.write(f"Recomendamos **{top_prod}** principalmente porque:")
        st.markdown(f"""
        1. Pertenece a la **misma comunidad** ({df_rank.iloc[0]['Misma Comunidad']}) que tu carrito.
        2. Tiene una alta **conectividad estructural** con lo que llevas.
        3. Es un producto **autoridad** en su categoría.
        """)
        st.success("¡Probabilidad de venta cruzada: ALTA!")

else:
    st.warning("Tu carrito está vacío. Selecciona productos en el menú de la izquierda.")