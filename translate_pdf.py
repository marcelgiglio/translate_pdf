import PyPDF2
import requests
import urllib.parse
import time
import re

# Variáveis globais
PDF_PATH = '/storage/emulated/0/Download/'
PDF_FILE = 'file-name.pdf'
ORIGINAL_LANGUAGE = 'en'
TARGET_LANGUAGE = 'pt'
MAX_LENGTH = 500
RETRIES = 3

def extract_text_from_pdf(pdf_path):
    """
    Extrai o texto de um arquivo PDF.
    
    Args:
        pdf_path (str): Caminho do arquivo PDF.
    
    Returns:
        str: Texto extraído do PDF.
    """
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    # Remover múltiplos espaços e tabulações
    text = re.sub(r'\s+', ' ', text)
    return text

def split_into_sentences(text):
    """
    Divide o texto em frases usando pontuação como delimitador.
    
    Args:
        text (str): Texto completo.
    
    Returns:
        list: Lista de frases.
    """
    sentences = re.split(r'(?<=[.!?]) +', text)
    return sentences

def split_long_sentence(sentence, max_length=MAX_LENGTH):
    """
    Divide frases longas em partes menores.
    
    Args:
        sentence (str): Frase a ser dividida.
        max_length (int): Comprimento máximo de cada parte.
    
    Returns:
        list: Lista de partes menores da frase.
    """
    words = sentence.split()
    parts = []
    current_part = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 > max_length:
            parts.append(" ".join(current_part))
            current_part = [word]
            current_length = len(word)
        else:
            current_part.append(word)
            current_length += len(word) + 1

    if current_part:
        parts.append(" ".join(current_part))
    
    return parts

def translate_sentence(sentence):
    """
    Traduz uma frase usando a API do Google Translate.
    
    Args:
        sentence (str): Frase a ser traduzida.
    
    Returns:
        str: Frase traduzida.
    """
    base_url = "https://translate.googleapis.com/translate_a/single?client=gtx&dt=t&sl={}&tl={}&q=".format(ORIGINAL_LANGUAGE, TARGET_LANGUAGE)
    translated_text = ""

    for part in split_long_sentence(sentence):
        encoded_part = urllib.parse.quote(part)
        url = base_url + encoded_part
        
        for attempt in range(RETRIES):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    translated_text += response.json()[0][0][0] + " "
                    break
                else:
                    print(f"Attempt {attempt+1}: Received status code {response.status_code} from API.")
                    time.sleep(1)
            except (requests.exceptions.RequestException, requests.exceptions.ChunkedEncodingError) as e:
                print(f"Attempt {attempt+1}: Error during request: {e}")
                time.sleep(1)
        else:
            print(f"Failed to translate part after {RETRIES} retries.")
            return "[Erro na tradução]"
    
    return translated_text.strip()

def translate_and_print_sentences(sentences):
    """
    Traduz e imprime cada frase individualmente.
    
    Args:
        sentences (list): Lista de frases a serem traduzidas.
    """
    for i, sentence in enumerate(sentences):
        if sentence.strip():
            translated_text = translate_sentence(sentence)
            print(translated_text)
        else:
            print("")

def main():
    """
    Função principal que executa a sequência completa:
    - Extrai texto do PDF
    - Divide o texto em frases
    - Traduz e imprime cada frase
    """
    pdf_path = PDF_PATH + PDF_FILE
    text = extract_text_from_pdf(pdf_path)
    sentences = split_into_sentences(text)
    translate_and_print_sentences(sentences)

if __name__ == '__main__':
    main()