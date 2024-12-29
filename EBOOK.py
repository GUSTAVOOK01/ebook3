import requests
from fpdf import FPDF
import spacy
import os
from PIL import Image
from io import BytesIO

# Carregar modelo de linguagem do spaCy para português
nlp = spacy.load("pt_core_news_sm")

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
def salvar_imagem(url, palavra):
    palavra_limpa = palavra.replace("\n", "").replace(" ", "_").replace("\\", "_").replace("/", "_")
    response = requests.get(url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        file_path = f"{palavra_limpa}_image.jpg"  # Nome seguro para a imagem
        img.save(file_path)
        return file_path
    return None

# Função para filtrar palavras-chave irrelevantes
def filtrar_palavras_chave(palavras):
    palavras_filtradas = []
    for palavra in palavras:
        if len(palavra) > 2 and palavra.lower() not in ["o", "a", "os", "as", "de", "do", "da", "e", "que", "para"]:
            palavras_filtradas.append(palavra)
    return palavras_filtradas

# Função para criar PDF com formatação avançada
def criar_pdf(arquivo_texto):
    with open(arquivo_texto, "r", encoding="utf-8") as file:
        texto = file.read()

    # Processar texto para identificar palavras-chave e filtrar
    doc = nlp(texto)
    palavras_chave = filtrar_palavras_chave(list(set(ent.text for ent in doc.ents)))

    # Buscar imagens para palavras-chave
    imagens = {}
    for palavra in palavras_chave:
        img_url = buscar_imagem(palavra)
        if img_url:
            imagens[palavra] = salvar_imagem(img_url, palavra)

    # Criar o PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Adicionar texto ao PDF com destaques e formatação
    for linha in texto.split("\n"):
        if any(palavra in linha for palavra in palavras_chave):
            pdf.set_text_color(0, 0, 255)  # Azul para destacar palavras-chave
        else:
            pdf.set_text_color(0, 0, 0)  # Preto para texto comum
        pdf.multi_cell(0, 10, linha)
        pdf.set_text_color(0, 0, 0)  # Resetar cor do texto

        # Adicionar imagens relacionadas
        for palavra, img_path in imagens.items():
            if palavra in linha:
                if os.path.exists(img_path):
                    pdf.ln(5)  # Adiciona espaço antes da imagem
                    try:
                        pdf.image(img_path, x=10, w=100)
                        pdf.ln(50)  # Adiciona espaço após a imagem
                    except Exception as e:
                        print(f"Erro ao adicionar imagem: {img_path} - {e}")

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
