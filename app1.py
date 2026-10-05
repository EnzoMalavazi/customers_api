from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, PositiveInt   
from sqlalchemy import text
import requests 
from database import engine

class Customer(BaseModel):
    customer_name: str
    customer_age: PositiveInt
    customer_email: EmailStr
    external_id: str

app = FastAPI()

@app.get('/')
def root():
    with engine.connect() as con:
        resultado = con.execute(text("""Select * from projetos.clientes Order by id Desc Limit 1"""))
        resultado = resultado.fetchall()
        dados = []
        for linha in resultado:
            dados.append(dict(linha._mapping))

        return {'API':'Rodando', 'Ultimo user criado': dados}

@app.post('/customers')
def create_outsourced():
    payload = {
    "external_code": 10,
    "name": "Enzo Outsourced Payload",
    "contact_email": "enzo@blaze.com"
    }

    r = requests.post('http://127.0.0.1:8001/external/companies', json = payload)
    r = r.json()

    with engine.connect() as con:
      
        id_ext = r['external_code']
        if int(id_ext.split('-')[-1]) < 20:
            level = 'Outsourced-min'
        else:
            level = 'Outsourced-max'

        con.execute(text(""" INSERT INTO projetos.clientes (external_id, access_level, integration_status) VALUES (:external_id, :level, 'Integrated')    
                        """), parameters={'external_id': r['external_code'], 'level': level})
        con.commit()


@app.post('/customers/internal')
def create_customer(customer: Customer):
    with engine.connect() as con:
        con.execute(text("""
                        INSERT INTO projetos.clientes (CUSTOMER_NAME, CUSTOMER_AGE, CUSTOMER_EMAIL) values (:name, :age, :email,:external_id)    
                        """), parameters={'name': customer.customer_name,'age':customer.customer_age, 'email': customer.customer_email,'external_id':customer.external_id})
        con.commit()
    return {'Response': 'created'}