import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
import os
import re
import csv
import requests
import urllib.request
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import time

# Constantes
OUTPUT_FOLDER = "output"
BASE_URL = 'https://shopee.com.br/api/v4/recommend/recommend?bundle=shop_page_product_tab_main&limit=999&offset=0&section=shop_page_product_tab_main_sec&shopid='
HEADERS = ["ad_id", "title", "stock", "price", "sales", "rating", "likes", "views", "description", "reviews"]

# Verifica se a pasta output existe, caso contrário, cria
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Inicializar o executor global
executor = ThreadPoolExecutor(max_workers=20)


# Função para buscar os dados da Shopee
def fetch_shopee_data(seller_id):
    try:
        response = requests.get(BASE_URL + seller_id, timeout=5)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as e:
        return None, f"Erro na requisição: {e}"


# Função para extrair o seller_id de um link
def extract_seller_id(link):
    match = re.search(r'i\.(\d+)\.', link)
    if match:
        return match.group(1), None
    return None, "Link inválido ou seller_id não encontrado"


# Função para salvar informações em CSV
def save_to_csv(data, path):
    with open(path, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)


# Função para baixar imagens
def download_images(images, folder):
    for idx, image in enumerate(images):
        image_url = f"https://cf.shopee.com.br/file/{image}_tn"
        urllib.request.urlretrieve(image_url, f"{folder}/image_{idx}.jpg")


# Função para iniciar o scraping
def start_scraping():
    input_data = clientid_entry.get().strip()
    log_text.delete(1.0, tk.END)
    progress_bar["value"] = 0

    if not input_data:
        messagebox.showerror("Erro", "Por favor, insira um clientid ou um link de produto válido.")
        return

    if "shopee" in input_data:
        seller_id, error = extract_seller_id(input_data)
        if error:
            messagebox.showerror("Erro", error)
            return
    else:
        seller_id = input_data

    shopee_data, error = fetch_shopee_data(seller_id)
    if error:
        messagebox.showerror("Erro", error)
        return

    total_products = len(shopee_data['data']['sections'][0]['data']['item'])
    remaining_label.config(text=f"Produtos totais: {total_products}")
    start_button.config(state=tk.NORMAL)


# Função para efetuar o scraping
def perform_scraping():
    global executor
    executor = ThreadPoolExecutor(max_workers=20)
    input_data = clientid_entry.get().strip()

    start_time = time.time()

    if "shopee" in input_data:
        seller_id, _ = extract_seller_id(input_data)
    else:
        seller_id = input_data

    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    seller_folder = f"{OUTPUT_FOLDER}/{seller_id}_{current_time}"

    if os.path.exists(seller_folder):
        messagebox.showinfo("Info", "Scraping já realizado para este clientid.")
        return

    os.makedirs(seller_folder, exist_ok=True)
    csv_path = f"{seller_folder}/informacoes_{current_time}.csv"
    save_to_csv(HEADERS, csv_path)

    shopee_data, _ = fetch_shopee_data(seller_id)
    total_products = len(shopee_data['data']['sections'][0]['data']['item'])

    for i, ad in enumerate(shopee_data['data']['sections'][0]['data']['item']):
        executor.submit(save_product_data, ad, i, total_products, seller_folder, csv_path)

    end_time = time.time()
    elapsed_time = end_time - start_time

    status_label.config(text=f"Scraping concluído em {elapsed_time:.2f} segundos.")


# Função para salvar os dados do produto
def save_product_data(ad, index, total, seller_folder, csv_path):
    start_time = time.time()

    ad_id = ad['itemid']
    title = ad['name']
    log_text.insert(tk.END, f"Salvando produto: {title}\n")
    log_text.yview(tk.END)
    remaining_label.config(text=f"Produtos restantes: {total - index - 1}")

    description = "Exemplo de descrição"  # Aqui você pode extrair a descrição real do produto
    reviews = "Exemplo de avaliações"  # Aqui você pode extrair as avaliações reais do produto

    save_to_csv([ad_id, title, ad['stock'], ad['price'], ad['historical_sold'], ad['item_rating']['rating_count'][0],
                 ad['liked_count'], ad['view_count'], description, reviews], csv_path)

    ad_folder = f"{seller_folder}/{ad_id}"
    os.makedirs(ad_folder, exist_ok=True)
    download_images(ad['images'], ad_folder)

    progress_bar["value"] = (index + 1) / total * 100

    end_time = time.time()
    elapsed_time = end_time - start_time
    log_text.insert(tk.END, f"Produto: {title} salvo em {elapsed_time:.2f} segundos.\n")


# Interface Gráfica
root = tk.Tk()
root.title("Shopee Scraper Final")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

clientid_label = ttk.Label(frame, text="Digite o clientid ou link do produto:")
clientid_label.grid(row=0, column=0, sticky=tk.W, pady=5)
clientid_entry = ttk.Entry(frame, width=40)
clientid_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

fetch_button = ttk.Button(frame, text="Buscar Dados", command=start_scraping)
fetch_button.grid(row=1, columnspan=2, pady=5)

start_button = ttk.Button(frame, text="Iniciar Scraping", state=tk.DISABLED, command=perform_scraping)
start_button.grid(row=2, columnspan=2, pady=5)

progress_bar = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
progress_bar.grid(row=3, columnspan=2, pady=5)

status_label = ttk.Label(frame, text="Status: Aguardando")
status_label.grid(row=4, columnspan=2, sticky=tk.W, pady=5)

remaining_label = ttk.Label(frame, text="Produtos totais: N/A")
remaining_label.grid(row=5, columnspan=2, sticky=tk.W, pady=5)

log_text = scrolledtext.ScrolledText(frame, width=50, height=10)
log_text.grid(row=6, columnspan=2, pady=10)

root.mainloop()
