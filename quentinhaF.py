
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# === Configurações do pedido (edite aqui) ===
URL_PAGINA = "https://espetinho-do-nino-2.ola.click/pratos/prato-baiao-de-dois-pequeno"
NOME_CLIENTE = "Victor Santana"
TELEFONE = "21971016836"
HORA_ABRE = "11:30"        # começa a tentar a partir deste horário
HORA_LIMITE = "14:00"      # para de tentar depois deste horário
FINALIZAR_PEDIDO = True   # True = clica no botão final e fecha o pedido de verdade


# Configuração da função para fazer o pedido
def fazer_pedido():
    # === Setup do Chrome ===
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    wait = WebDriverWait(driver, 60)  # Tempo máximo de espera por elemento

    try:
        driver.get(URL_PAGINA)
        time.sleep(2)  # Espera a página carregar completamente

        # === Fazendo o pedido ===

        # Clica na label com o texto "Sem molho"
        xpath_label = "//div[contains(@class, 'modifier-input-checkbox-label') and normalize-space()='Sem molho']"
        checkbox_label = wait.until(EC.presence_of_element_located((By.XPATH, xpath_label)))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", checkbox_label)
        time.sleep(1)
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath_label))).click()
        time.sleep(1)

        # Clica na label com o texto "Medalhão"
        xpath_medalhao = "//div[contains(@class, 'modifier-input-checkbox-label') and normalize-space()='Medalhão']"
        element = wait.until(EC.presence_of_element_located((By.XPATH, xpath_medalhao)))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath_medalhao))).click()
        time.sleep(1)

        # Botão de adicionar
        wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[.//div[contains(@class, 'product-add-to-cart__text') and normalize-space(text())='Adicionar']]"
        ))).click()

        # Botão veja meu pedido
        wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//a[.//span[contains(@class, 'amount-summary__button-text') and normalize-space(text())='Veja meu pedido']]"
        ))).click()

        # Botão retirada
        wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[.//span[contains(@class, 'order-button__text') and normalize-space(text())='Retirada']]"
        ))).click()
        time.sleep(1)

        # Colocando meu nome (primeira etapa - placeholder 'Write here...')
        input_nome = wait.until(EC.presence_of_element_located((
            By.XPATH, "//input[@placeholder='Write here...']"
        )))
        input_nome.send_keys(NOME_CLIENTE)

        # Botão confirmar
        wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(@class, 'checkout-submit-button') and contains(., 'Confirmar')]"
        ))).click()
        time.sleep(1)

        # Campo com nome (etapa de dados adicionais)
        campo_nome = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//input[@type='text' and @autocomplete='off']"
        )))
        campo_nome.click()
        campo_nome.send_keys(NOME_CLIENTE)
        time.sleep(1)

        # Telefone
        campo_telefone = wait.until(EC.element_to_be_clickable((By.ID, "client-phone")))
        campo_telefone.click()
        campo_telefone.send_keys(TELEFONE)

        # Botão confirmar
        wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(@class, 'checkout-submit-button') and contains(., 'Confirmar')]"
        ))).click()
        time.sleep(1)

        # Abre o dropdown de forma de pagamento
        wait.until(EC.element_to_be_clickable((
            By.XPATH, "//i[contains(@class, 'v-select__menu-icon')]"
        ))).click()

        # Seleciona "Cartão de crédito"
        wait.until(EC.element_to_be_clickable((
            By.XPATH, "//div[@role='option'][contains(., 'Cartão de crédito')]"
        ))).click()
        time.sleep(1)

        # Botão confirmar final (robusto a mudança de preço)
        confirmar_button = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//button[@type='submit' and contains(., 'Confirmar')]"
        )))
        if FINALIZAR_PEDIDO:
            confirmar_button.click()
            print(f"Pedido enviado {datetime.now():%H:%M:%S.%f}")

        time.sleep(120)  # Mantém o navegador aberto para inspeção

    except Exception as e:
        print(f"Erro: {e}")
        try:
            driver.save_screenshot("erro_pedido.png")
        except Exception:
            pass
        # Navegador mantido aberto para inspeção do que deu errado
    # finally:
    #     driver.quit()  # descomente para fechar o navegador automaticamente


# === Agendamento de alta precisão: dispara exatamente às HORA_ABRE ===
hora_abre = datetime.strptime(HORA_ABRE, "%H:%M").time()
hora_limite = datetime.strptime(HORA_LIMITE, "%H:%M").time()

_agora = datetime.now()
alvo = _agora.replace(hour=hora_abre.hour, minute=hora_abre.minute,
                      second=0, microsecond=0)

if _agora.time() >= hora_limite:
    print("Fora da janela de horário.")
else:
    # Espera até o horário exato. Longe do alvo: dorme p/ poupar CPU.
    # Últimos 3s: busy-wait puro (sem sleep) p/ máxima precisão no disparo.
    while datetime.now() < alvo:
        restante = (alvo - datetime.now()).total_seconds()
        if restante > 60:
            time.sleep(30)
        elif restante > 3:
            time.sleep(0.2)
    fazer_pedido()
