from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from threading import Thread
from pathlib import Path


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
    driver.implicitly_wait(10)

    # access google translate
    driver.get(
        "https://translate.google.com.br/?hl=pt-BR&tab=wT&sl=en&tl=pt&op=docs")

    # no botão "escolher arquivos", inserir o caminho completo até o arquivo .txt
    input_file = driver.find_element_by_name("file")
    input_file.send_keys(str(filename))

    # clica em traduzir
    driver.find_element_by_xpath(
        '//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/div[3]/c-wiz/div[2]/c-wiz/div/form/div[2]/div[2]/button/span').click()

    # pega o texto que foi traduzido
    text = driver.find_element_by_tag_name("pre").text

    # finish driver
    driver.quit()

    # save the text into a file
    filename = output_dir/filename.name

    with open(filename, "w", encoding="utf-8") as outputfile:
        outputfile.write(text)


### MAIN ###
# verifica se os diretórios input e output existem. Se não existirem, cria os diretórios
input_dir.mkdir(exist_ok=True)
output_dir.mkdir(exist_ok=True)


# percorre o diretório input
for file in input_dir.iterdir():
    Thread(target=translate, kwargs={"filename": file}).start()