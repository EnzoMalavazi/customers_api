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
def create_user_ext(user:User_ext):
    if('@blaze.com' not in user.contact_email):
        raise HTTPException(status_code= '400', detail= 'Not a company email')
    repartido = user.name.split(' ')
    company_name = ', '.join([repartido[0],repartido[-1]])
    external_code = f'EXT-{random.randint(user.external_code,40)}'

    with out_engine.connect() as out:
        out.execute(text("""
                        Insert into projetos.external (external_code,company_name,email) values (:external_code, :company_name,:contact_email)
                    """), parameters={'external_code':external_code, 'company_name':company_name, 'contact_email':user.contact_email})
        out.commit()

    return {'external_code':external_code, 'status': 'created'}

@app_ext.get('/external/users/{id}')
def get_user_ext(id:int):
    with out_engine.connect() as out:
        resultado = out.execute(text("""Select * from projetos.external where id = :id"""), parameters={'id':id})
        dados = []
        resultado = resultado.fetchall()
        for linha in resultado:
            dados.append(dict(linha._mapping))
    if(len(dados) == 0):
        raise HTTPException(status_code= '404', detail= 'User not found')
    return {'user':dados}