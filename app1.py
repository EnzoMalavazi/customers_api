from fastapi import FastAPI, HTTPException
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
    try:
    
        r  = requests.post('http://127.0.0.1:8001/external/companies',json= payload, timeout= 5)
    
    except requests.exceptions.Timeout:
    
        raise HTTPException(status_code= 504, detail= 'External API Timeout') 

    except requests.exceptions.ConnectionError:

        raise HTTPException( status_code= 503, detail= 'External API connection Error')
    
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

        resultado = con.execute(text(""" INSERT INTO projetos.clientes (customer_name, customer_age,customer_email,external_id, access_level, integration_status) VALUES (:name,:age,:email,:external_id, :level, 'Integrated')
                             RETURNING ID    
                        """), parameters={'name': user_ext.name, 'age': user_ext.age ,'email':user_ext.contact_email,'external_id': r['external_code'], 'level': level})
        id = resultado.scalar()
        con.commit()

    return {'id':id,'name': user_ext.name, 'email':user_ext.contact_email,'Response': 'created in both databases', 'external_code': r['external_code'], 'access_level': level}


@app.post('/customers/internal', status_code= 201)
def create_customer(customer: Customer):
    with engine.connect() as con:
        resultado = con.execute(text("""
                        INSERT INTO projetos.clientes (CUSTOMER_NAME, CUSTOMER_AGE, CUSTOMER_EMAIL) values (:name, :age, :email)
                        Returning ID    
                        """), parameters={'name': customer.customer_name,'age':customer.customer_age, 'email': customer.customer_email})
        id = resultado.scalar_one()
        con.commit()
    return {'ID': id,'Response': 'created','name':customer.customer_name, 'email': customer.customer_email, 'age': customer.customer_age}

def compare_ext_codes(ext_codes : list): 
    with engine.connect() as out:
        data = out.execute(text("""
                                Select external_id from projetos.clientes
                                """))
        external_ids_interiordb = data.scalars().all()
        pending_list = []
        for i in  ext_codes['External_codes']:
            if i not in external_ids_interiordb: 
                pending_list.append(i)

@app.get("/customers/external/pending")
def get_ext_users():
    try:
        data  = requests.get('http://127.0.0.1:8001/external/users',timeout= 5 )
    except requests.exceptions.Timeout:
        raise HTTPException(status_code= 504, detail= 'External API Timeout ')
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code= 503, detail='External API connection Error')
    print(data.json())
    return  data.json()

@app.post('/customers/external/{external_code}/integrate')
def att_users_ext(): ## criar a função de post de atualização dos users continuar ela

    ext_codes = get_ext_users()
    validar = compare_ext_codes(ext_codes=ext_codes)
    return False