import requests
from environs import Env
import json


def get_token(client_id, secret_id):
    client_data = {
        'client_id': client_id,
        'client_secret': secret_id,
        'grant_type': 'client_credentials',
    }
    token_response = requests.post('https://api.moltin.com/oauth/access_token', data=client_data)
    token_response.raise_for_status()
    access_token = token_response.json()['access_token']
    authorization_data = {
        'authorization': f'Bearer {access_token}',
        'expires': token_response.json()['expires'],
    }
    return authorization_data


def create_file_product(token, url):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    file = {
        'file_location': (None, f'{url}'),
    }

    file_response = requests.post('https://api.moltin.com/v2/files', headers=headers, files=file)
    file_response.raise_for_status()
    file_id = file_response.json()['data']['id']
    return file_id


def bind_product_image(product_id, file_id, token):
    #file_id = create_file_product(token)
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    product_data = {
        'data': [
            {
                'type': 'file',
                'id': file_id,
            },
        ],
    }
    bind_response = requests.post(f'https://api.moltin.com/v2/products/{product_id}/relationships/files',
                                  headers=headers, json=product_data)
    bind_response.raise_for_status()



def create_product(token):
    with open('menu_pizza.json', 'r') as file:
        data = file.read()
        pizza_data = json.loads(data)
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',

    }
    for pizza in pizza_data:
        file_id = create_file_product(token, pizza['product_image']['url'])
        pizza_data = {
            'data':
                {
                    "type": "product",
                    "name": pizza['name'],
                    "slug": str(pizza['id']),
                    "sku": str(pizza['id']),
                    "description": pizza['description'],
                    "manage_stock": False,
                    "price": [
                        {
                            "amount": pizza['price'],
                            "currency": "RUB",
                            "includes_tax": True
                        }
                    ],
                    "status": "live",
                    "commodity_type": "physical",

                }
        }
        print(pizza_data)
        response_product = requests.post(f'https://api.moltin.com/v2/products', headers=headers, json=pizza_data)
        response_product.raise_for_status()
        print(response_product.json())
        product_id = response_product.json()['data']['id']
        bind_product_image(product_id, file_id, token)


def create(token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',

    }
    # data = {
    #     'data':
    #         {
    #             "type": "product",
    #             "name": "тест",
    #             "slug": "sd",
    #             "sku": "033425",
    #             "description": "вава",
    #             "manage_stock": False,
    #             "price": [
    #                 {
    #                     "amount": 58912,
    #                     "currency": "RUB",
    #                     "includes_tax": True
    #                 }
    #             ],
    #             "status": "live",
    #             "commodity_type": "physical",
    #
    #         }
    # }
    response = requests.delete('https://api.moltin.com/v2/products', headers=headers)
    response.raise_for_status()
    print(response.json())

if __name__=='__main__':
    env = Env()
    env.read_env()
    client_id = env('CLIENT_ID')
    client_secret = env('CLIENT_SECRET')
    #print(get_token(client_id,client_secret))
    create_product('73342e68a0a8cb70de24f1e210c291c12958f683')
