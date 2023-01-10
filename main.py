import json
import requests


def download_address():
    address_url = 'https://dvmn.org/media/filer_public/90/90/9090ecbf-249f-42c7-8635-a96985268b88/addresses.json'
    response = requests.get(address_url)
    content = response.json()
    with open('addres_pizza.json', 'w') as file:
        json.dump(content, file, indent=2, ensure_ascii=False)


def download_menu():
    menu_url = 'https://dvmn.org/media/filer_public/a2/5a/a25a7cbd-541c-4caf-9bf9-70dcdf4a592e/menu.json'
    response = requests.get(menu_url)
    response.raise_for_status()
    content = response.json()
    with open('menu_pizza.json', 'w') as file:
        json.dump(content, file, indent=2, ensure_ascii=False)





if __name__ == '__main__':
    download_menu()
    download_address()
    with open('menu_pizza.json', 'r') as file:
        data = file.read()
        json_data = json.loads(data)

    for i in json_data:
        print(i['product_image']['url'])
