from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field, PositiveInt   
from sqlalchemy import text
import requests 
from database import engine

class Customer(BaseModel):
    customer_name: str
    customer_age: PositiveInt
    customer_email: EmailStr

class User_ext(BaseModel):
    external_code: int = Field(gt = 0, le= 30)
    name: str
    contact_email: EmailStr
    age: PositiveInt

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

def send_payload(user_ext: User_ext):
    payload = {"external_code": user_ext.external_code,
        "name": user_ext.name,
        "contact_email": user_ext.contact_email}
    
    r  = requests.post('http://127.0.0.1:8001/external/companies',json= payload, timeout= 5)
    
    print(r.status_code)
    print(r.json())
    
    return r.json()

@app.post('/customers')
def create_outsourced(user_ext: User_ext):
    r = send_payload(user_ext = user_ext)

    with engine.connect() as con:
      
        id_ext = r['external_code']
        if int(id_ext.split('-')[-1]) < 20:
            level = 'Outsourced-min'
        else:
            level = 'Outsourced-max'

        con.execute(text(""" INSERT INTO projetos.clientes (customer_name, customer_age,customer_email,external_id, access_level, integration_status) VALUES (:name,:age,:email,:external_id, :level, 'Integrated')    
                        """), parameters={'name': user_ext.name, 'age': user_ext.age ,'email':user_ext.contact_email,'external_id': r['external_code'], 'level': level})
        con.commit()
    return {'Response': 'created in both databases', 'external_code': r['external_code'], 'access_level': level}

@app.post('/customers/internal')
def create_customer(customer: Customer):
    with engine.connect() as con:
        con.execute(text("""
                        INSERT INTO projetos.clientes (CUSTOMER_NAME, CUSTOMER_AGE, CUSTOMER_EMAIL) values (:name, :age, :email)    
                        """), parameters={'name': customer.customer_name,'age':customer.customer_age, 'email': customer.customer_email})
        con.commit()
    return {'Response': 'created'}