import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import os
import re
import csv
import requests
import urllib.request
from datetime import datetime
from threading import Thread


# Função para buscar os dados da Shopee
def fetch_shopee_data(seller_id):
    try:
        url = f'https://shopee.com.br/api/v4/recommend/recommend?bundle=shop_page_product_tab_main&limit=999&offset=0&section=shop_page_product_tab_main_sec&shopid={seller_id}'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return f"Erro na requisição: {e}"


# Função para extrair o seller_id de um link
def extract_seller_id(link):
    match = re.search(r'i\.(\d+)\.', link)
    if match:
        return match.group(1)
    return None


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
    input_data = clientid_entry.get()
    if "shopee" in input_data:
        seller_id = extract_seller_id(input_data)
    else:
        seller_id = input_data

    if not seller_id:
        status_label.config(text="Por favor, insira um clientid válido ou um link de produto válido.")
        return

    status_label.config(text="Buscando dados...")
    shopee_data = fetch_shopee_data(seller_id)

    if "Erro" in str(shopee_data):
        status_label.config(text=shopee_data)
        return

    total_products = len(shopee_data['data']['sections'][0]['data']['item'])
    remaining_label.config(text=f"Produtos totais: {total_products}")
    start_button.config(state=tk.NORMAL)


# Função para efetuar o scraping
def perform_scraping():
    input_data = clientid_entry.get()
    if "shopee" in input_data:
        seller_id = extract_seller_id(input_data)
    else:
        seller_id = input_data

    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    seller_folder = f"{seller_id}_{current_time}"

    if os.path.exists(seller_folder):
        status_label.config(text="Scraping já realizado para este clientid.")
        return

    os.makedirs(seller_folder, exist_ok=True)
    csv_path = f"{seller_folder}/informacoes_{current_time}.csv"
    save_to_csv(["ad_id", "title", "stock", "price", "sales", "rating", "likes", "views"], csv_path)

    shopee_data = fetch_shopee_data(seller_id)
    total_products = len(shopee_data['data']['sections'][0]['data']['item'])

    for i, ad in enumerate(shopee_data['data']['sections'][0]['data']['item']):
        ad_id = ad['itemid']
        title = ad['name']
        log_text.insert(tk.END, f"Salvando produto: {title}\n")
        log_text.yview(tk.END)
        remaining_label.config(text=f"Produtos restantes: {total_products - i - 1}")
        save_to_csv(
            [ad_id, title, ad['stock'], ad['price'], ad['historical_sold'], ad['item_rating']['rating_count'][0],
             ad['liked_count'], ad['view_count']], csv_path)

        ad_folder = f"{seller_folder}/{ad_id}"
        os.makedirs(ad_folder, exist_ok=True)
        download_images(ad['images'], ad_folder)

        progress_bar["value"] = (i + 1) / total_products * 100

    status_label.config(text="Scraping concluído.")


# Interface Gráfica
root = tk.Tk()
root.title("Shopee Scraper Final")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

clientid_label = ttk.Label(frame, text="Digite o clientid ou link do produto:")
clientid_label.grid(row=0, column=0, sticky=tk.W, pady=5)
clientid_entry = ttk.Entry(frame, width=40)
clientid_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

fetch_button = ttk.Button(frame, text="Buscar Dados", command=lambda: Thread(target=start_scraping).start())
fetch_button.grid(row=1, columnspan=2, pady=5)

start_button = ttk.Button(frame, text="Iniciar Scraping", state=tk.DISABLED,
                          command=lambda: Thread(target=perform_scraping).start())
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
