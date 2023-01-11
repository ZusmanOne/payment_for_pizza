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


def create_flow(token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    flow_data = {
        'data': {
            'type': 'flow',
            'name': 'Pizzeria',
            'slug': 'pizzeria',
            'description': 'We cook best pizza',
            'enabled': True,
        },
    }
    response = requests.post('https://api.moltin.com/v2/flows', headers=headers, json=flow_data)
    response.raise_for_status()
    print(response.status_code)
    print(response.json())


def create_field(token,id_flow):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    json_data = {
        'data': {
            'type': 'field',
            'name': 'longitude',
            'slug': 'longitude',
            'field_type': 'float',
            'description': "Pizzeria's longitude",
            'required': True,
            'default': 0,
            'enabled': True,
            'order': 1,
            'omit_null': False,
            'relationships': {
                'flow': {
                    'data': {
                        'type': 'flow',
                        'id': id_flow,
                    },
                },
            },
        },
    }

    response = requests.post('https://api.moltin.com/v2/fields', headers=headers, json=json_data)
    response.raise_for_status()
    print(response.json())


def add_entries(token):
    with open('addres_pizza.json', 'r') as file:
        data = file.read()
        pizza_data = json.loads(data)
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    print(headers)
    for data in pizza_data:
        print(data['address']['full'])
        entries_data = {
            "data":
                {
                    "type": "entry",
                    'address': data['address']['full'],
                    'alias': data['alias'],
                    'latitude': float(data['coordinates']['lat']),
                    'longitude': float(data['coordinates']['lon']),
                }
        }

        response = requests.post(f'https://api.moltin.com/v2/flows/pizzeria/entries', headers=headers,
                                 json=entries_data)
        response.raise_for_status()
        print(response.json())


if __name__=='__main__':
    env = Env()
    env.read_env()
    client_id = env('CLIENT_ID')
    client_secret = env('CLIENT_SECRET')
    #print(get_token(client_id,client_secret))
    #create_product('73342e68a0a8cb70de24f1e210c291c12958f683')
    #create_flow('4ac38dfb6948d32fde637e3395ce226daf40c656')
    #create_field('2764ae4eea90ab635b8bb4c8df058fd07b28dd75', 'ede13058-7b1a-42df-a5d0-d498a5576cb3')
    add_entries('2764ae4eea90ab635b8bb4c8df058fd07b28dd75')