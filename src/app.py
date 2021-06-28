import sys
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path
from datetime import datetime
from os import system, name


### variables ###
input_dir = Path.cwd().parent/"input"
output_dir = Path.cwd().parent/"output"


### FUNCTIONS ###
def translate(filename):

    # set chrome options
    chrome_options = Options()
    chrome_options.headless = True

    # create driver
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(60)

    # acessa o google tradutor
    # a URL do site já está configurada para que o texto de origem seja inglês e o texto de saída seja português
    driver.get(
        "https://translate.google.com.br/?hl=pt-BR&tab=wT&sl=en&tl=pt&op=docs")

    # no botão "escolher arquivos", inserir o caminho completo até o arquivo .txt
    input_file = driver.find_element_by_name("file")
    input_file.send_keys(str(filename))

    # clica no botão traduzir
    driver.find_element_by_xpath(
        '//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/div[3]/c-wiz/div[2]/c-wiz/div/form/div[2]/div[2]/button/span').click()

    # pega o texto que foi traduzido
    text = driver.find_element_by_tag_name("pre").text

    # finalizando o driver do chrome
    driver.quit()

    # por fim, salva o texto traduzido num arquivo TXT, dentro do diretório output
    output_file = output_dir/filename.name

    with open(output_file, "w", encoding="utf-8") as outputfile:
        outputfile.write(text)


def strsplit(chars, qty):
    charslist = [chars[0:qty]]
    chars = chars.lstrip(chars[0:qty])

    if len(chars) != 0:
        charslist += strsplit(chars, qty)

    return charslist


def get_args(args):

    if len(args) != 2:
        raise IndexError("Requires only one argument: docs or single")

    else:
        arg = args[1].lower()

    if arg not in ("docs", "single"):
        raise ValueError("Argument must be docs or single")

    return "single" if arg == "single" else "docs"


def concat():
    output_file = output_dir/"output.txt"
    output_texts = ""

    for file in output_dir.iterdir():

        with open(file, "r", encoding="utf-8") as input_file:
            output_texts += input_file.read()

        file.unlink()

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(output_texts)


def mkfiles(type_of_translation):
    input_file = input_dir/"input.txt"

    if type_of_translation != "single":
        return

    with open(input_file, "r", encoding="utf-8") as file:
        text = file.read()
        textslist = strsplit(text, 25000)

    # remove o arquivo input
    input_file.unlink()

    for inputtext in textslist:
        current_time = datetime.now().strftime("%H%M%S%f")
        input_file = input_dir/f"{current_time}.txt"

        with open(input_file, "w", encoding="utf-8") as file:
            file.write(inputtext)


def print_process():
    _ = system("cls") if name == "nt" else "clear"
    print(f"\t*{len(inputfiles)} files waiting to be translated*")


### MAIN ###
# verifica se os diretórios input e output existem. Se não existirem, cria os diretórios
input_dir.mkdir(exist_ok=True)
output_dir.mkdir(exist_ok=True)


# pega o tipo de tradução
type_of_translation = get_args(sys.argv)
mkfiles(type_of_translation)

# cria uma lista com todos os arquivos dentro do diretório input
inputfiles = list(input_dir.iterdir())

# então, enquanto houver elementos dentro da lista, realiza os processos a seguir.
# nota: são criados múltiplos conjuntos de 20 threads, isso significa que são traduzidos apenas 20 arquivos por vez. Isso se dá pois quando há mais de 40 threads trabalhando em paralelo, pode ocorrer esgotamento da memória em disco
while len(inputfiles) != 0:

    # pega 20 arquivos dentro do diretório input e cria uma thread individual para cada processo de tradução
    [threading.Thread(target=translate, kwargs={"filename": file}).start() for file in inputfiles[0:20]]

    # depois remove da lista esses 20 arquivos que estão sendo traduzidos
    [inputfiles.remove(element) for element in inputfiles[0:20]]

    # observa as threads em andamento. Quando as 20 threads forem concluídas, pula para o próximo conjunto de tradução
    while threading.active_count() > 1:
        print_process()


# depois que todos os arquivos dentro do diretório input forem traduzidos, concatena os arquivos traduzidos no diretório output dentro de um único arquivo
concat()
