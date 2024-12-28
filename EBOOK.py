import requests
from fpdf import FPDF
import spacy
import os
from PIL import Image
from io import BytesIO

# Carregar modelo de linguagem do spaCy
nlp = spacy.load("en_core_web_sm")

# Configurar API do Unsplash
UNSPLASH_API_KEY = "tmOTn0_vyFGc21VGinoX29e4sNDA5AeD2Rz97mnD7KA"  # Substitua pela sua chave da API
UNSPLASH_URL = "https://api.unsplash.com/search/photos"

# Função para buscar imagens no Unsplash
def buscar_imagem(query):
    params = {
        "query": query,
        "client_id": UNSPLASH_API_KEY,
        "per_page": 1
    }
    response = requests.get(UNSPLASH_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results'][0]['urls']['regular']  # URL da imagem
    return None

# Função para salvar imagem temporariamente
def salvar_imagem(url):
    response = requests.get(url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        file_path = f"temp_image.jpg"
        img.save(file_path)
        return file_path
    return None

# Função para criar PDF
def criar_pdf(arquivo_texto):
    with open(arquivo_texto, "r", encoding="utf-8") as file:
        texto = file.read()

    # Processar texto para identificar palavras-chave
    doc = nlp(texto)
    palavras_chave = list(set(ent.text for ent in doc.ents))

    # Buscar imagens para palavras-chave
    imagens = {}
    for palavra in palavras_chave:
        img_url = buscar_imagem(palavra)
        if img_url:
            imagens[palavra] = salvar_imagem(img_url)

    # Criar o PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for linha in texto.split("\n"):
        pdf.multi_cell(0, 10, linha)
        for palavra, img_path in imagens.items():
            if palavra in linha:
                if os.path.exists(img_path):
                    pdf.image(img_path, x=pdf.get_x(), y=pdf.get_y() + 10, w=60)
                    pdf.ln(30)  # Adiciona espaço após a imagem

    # Salvar PDF
    pdf.output("ebook_completo.pdf")

    # Remover imagens temporárias
    for img_path in imagens.values():
        if os.path.exists(img_path):
            os.remove(img_path)

# Caminho do arquivo de texto
arquivo_texto = "texto_ebook.txt"  # Substitua pelo nome do arquivo de entrada

# Gerar o PDF
criar_pdf(arquivo_texto)
