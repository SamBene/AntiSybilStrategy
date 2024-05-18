import json
import random
import asyncio
from g4f.client import Client
from web3 import Web3

def generate_ethereum_address():
    # Создаем объект Web3 с подключением к локальной ноде Ethereum
    w3 = Web3(Web3.WebsocketProvider('ws://localhost:8545'))  # Замените адрес и порт ноды при необходимости

    # Генерируем случайный приватный ключ
    private_key = w3.eth.account.create().privateKey.hex()

    # Получаем адрес из приватного ключа
    address = w3.eth.account.from_key(private_key).address

    return private_key, address

def select_and_shuffle_elements(input_file, output_file, num_elements):
    # Читаем входной JSON файл
    combined_data = []
    num_files = 7
    # Перебираем все файлы в указанной директории с заданным префиксом
    for i in range(1, num_files + 1):
        filename = f"addresses_{i}.json"
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            combined_data.extend(data)

    
    # Выбираем случайное количество элементов
    selected_elements = random.sample(combined_data, num_elements)
    
    # Перемешиваем выбранные элементы
    random.shuffle(selected_elements)
    
    # Записываем результат в выходной текстовый файл
    with open(output_file, 'w', encoding='utf-8') as file:
        for element in selected_elements:
            file.write(f"{element}\n")
    return selected_elements

def read_file_to_variable(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content



client = Client()

async def ask_gpt(content):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": content}]
    )
    return response.choices[0].message.content

async def main(generate_random_reward_address, address_to_get_reward):
    # Пример использования
    input_file = 'addresses_from_large_balances.json'
    output_file = 'addresses_to_report.txt'
    output_file_final = "text_to_report.txt"


    addresses = select_and_shuffle_elements(input_file, output_file, num_elements)
    addresses = "\n".join(addresses)
    if(generate_random_reward_address):
        private_key, ethereum_address = generate_ethereum_address()
        print("Генерируем рандомный адрес...\nPrivate Key:", private_key)
        print("Ethereum Address:", ethereum_address)
        address_to_get_reward = ethereum_address

    text_to_propose_final = "$$$"+text_to_propose+"$$$"
    #print(text_to_propose_final)

    print(f"\n{num_elements} случайных элементов записаны в файл {output_file}\n\n")

    total_generations = 5
    for i in range(total_generations):
        print(f"Идет генерация правильного ответа {i+1}/{total_generations}\n\n")
        try:
            text_answer = await ask_gpt(f'''{description_for_chatGPT}
                            {text_to_propose_final}. Также оставь знаки $ в тексте
                            
                          ''')

            #print(text_answer)
            text_answer = text_answer.split("$$$")[1]

            final_text = f'''# Reported Addresses\n{addresses}\n{text_answer}\n# Reward Address (If Eligible)\n{address_to_get_reward}'''

            print(final_text)

            with open(output_file_final, 'w', encoding='utf-8') as file:
                file.write(final_text)
            break
        except Exception as E:
            print(E)
            pass


# ИЗМЕНИТЕ ПОД ВАШИ НАСТРОЙКИ:
num_elements = 20  # Количество элементов для выбора
generate_random_reward_address = 1 # 1 - генерировать рандомный адрес, для получения ревардов, 0 - вы сами напишите адрес в address_to_get_reward
address_to_get_reward = "0x..." # адрес для получения ревардов

# Пример написания запроса для чат гпт. Первый пункт про адреса сибилов пропускаем, так как они генерируются из кода, то же самое и с кошельком для ревардов, вы уже его задали.
# адрес для получения реварлдов пишем выше в переменную address_to_get_reward
text_to_propose = f'''
# Description
Wallets were created simultaneously on the Arbitrum network, funded with identical amounts, have the same number of transactions, and the date of the last transaction on the wallet is the same.

# Detailed Methodology & Walkthrough
1. Wallets are filtered by creation date and grouped into clusters every 48 hours.
2. The clusters are checked for wallets that were funded with identical amounts of Ether on the Arbitrum network (with a 10% margin of error).
3. Clusters that pass the previous checks are then checked for the number of transactions. If the wallets have an identical number of transactions on the Arbitrum network (with a margin of error of 3-5 transactions), they are placed in a cluster.
4. The final step is to determine the date of the last transaction on the Arbitrum network. If all wallets in the cluster have the same creation date, the same initial funding amount, the same number of transactions, and the same date of the last transaction, we obtain the final cluster.
'''
# Тут вы пишите свой или юзаете мой шаблон, чтобы чат гпт нормально сгенерировал ответ и поменял ответ у текст выше
description_for_chatGPT = '''Перепиши мой текст другими словами на английском языке, строго по шаблону #, без всяких дополнительный ответов, придумай другие критерии к оценке либо оставляй существующие, также можешь менять кол-во пунктов, чтобы не всегда их было 4, но чтобы было похоже что писал другой человек.'''


# КОНЕЦ НАСТРОЕК




asyncio.run(main(generate_random_reward_address, address_to_get_reward))
