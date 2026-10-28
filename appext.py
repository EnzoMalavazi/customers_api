from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr,Field
from sqlalchemy import text, create_engine

from database_ext import out_engine
import random 



class User_ext(BaseModel):
    external_code: int = Field(gt = 0, le= 30)
    name: str
    contact_email: EmailStr 

app_ext = FastAPI()

@app_ext.get('/')
def home():

    with out_engine.connect() as out:
        resultado = out.execute(text("""Select * from projetos.external Order by id Desc Limit 1"""))
        dados = []
        resultado = resultado.fetchall()
        for linha in resultado:
            dados.append(dict(linha._mapping))

    return {'API':'Rodando', 'Ultimo user criado': dados}

@app_ext.post('/external/companies')
def create_user_ext_viaPayloadINT (user:User_ext):

    email =str( user.contact_email).lower()
    
    if(not email.endswith("@blaze.com")):
        raise HTTPException(status_code= 400 , detail= 'Not a company email')
    
    repartido = user.name.split(' ')
    
    company_name = ', '.join([repartido[0],repartido[-1]]) # ou ', '.join([stringe.split(' ')[0],stringe.split(' ')[-1]])
    
    external_code = f'EXT-{random.randint(user.external_code,40)}'

    with out_engine.connect() as out:
        resultado = out.execute(text("""
                        Insert into projetos.external (external_code,company_name,email) values (:external_code, :company_name,:contact_email) RETURNING id
                    """), parameters={'external_code':external_code, 'company_name':company_name, 'contact_email':user.contact_email})
        id = resultado.scalar_one()
        out.commit() 

    return {'id': id,'external_code':external_code, 'status': 'created'}

@app_ext.get('/external/users/{id}')
def get_user_ext_by_id(id:int):
    with out_engine.connect() as out:
        resultado = out.execute(text("""Select * from projetos.external where id = :id"""), parameters={'id':id})
        dados = []
        resultado = resultado.fetchall()
        for linha in resultado:
            dados.append(dict(linha._mapping))
    if(len(dados) == 0):
        raise HTTPException(status_code= '404', detail= 'User not found')
    return {'user':dados}

@app_ext.get('/external/users')
def get_user_ext():
    with out_engine.connect() as out:
        resultado = out.execute(text("""Select external_code from projetos.external"""))
        dados = []
        resultado = resultado.fetchall()
        for linha in resultado: ## ou usar direto o dados = resultado.scalars().all() ja faz a lista direto
            dados.append(linha.external_code) # ou append(linha._mapping["external_code"])
            print(linha.external_code   ) 
    if(len(dados) == 0):
        raise HTTPException(status_code= '404', detail= 'User not found')
    return {'External_codes':dados}

@app_ext.get('/external/users/data/{external_code}')
def get_ext_user_data(external_code: str):
    print(external_code)
    with out_engine.connect() as out:
        resultado = out.execute(text("""Select * from projetos.external where external_code = :external_code"""), parameters={'external_code':external_code})
        dados = []
        resultado = resultado.fetchall()
        for linha in resultado:
            dados.append(dict(linha._mapping))
    if(len(dados) == 0):
        raise HTTPException(status_code= 404, detail= f'User not found {external_code}')
    print('broke here')
    return dados

# fetchall() → quando você quer várias linhas completas, especialmente várias colunas;
# scalar_one() → quando espera uma linha e um valor, como RETURNING id;
# scalars().all() → quando espera várias linhas, mas só uma coluna.