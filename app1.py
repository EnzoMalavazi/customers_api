from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, PositiveInt   
from sqlalchemy import text, create_engine
# import requests 
from database import engine

class Customer(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr

app = FastAPI()

@app.get('/')
def root():
    with engine.connect() as con:
        resultado = con.execute(text("""Select * from projetos.clientes Order by id Desc Limit 1"""))
        dados = []
        for linha in resultado:
            dados.append(dict(linha._mapping))

        return {'API':'Rodando', 'Ultimo user criado': dados}

@app.get('/creation_bruno')
def teste():  
    info = create_customer(Customer(name= 'Bruno', age='130',email = 'bruno@email.com'))
    return  {'API':'Rodando', 'info': info}


@app.post('/customers')
def create_customer(customer: Customer):
    
    with engine.connect() as con:
        resultado = con.execute(text(""" insert into projetos.clientes(customer_name,customer_age, customer_email) 
        Values(:name,:age,:email)
                            """ ), parameters = {'name':customer.name,'age':customer.age, 'email':customer.email})
        con.commit()
    return customer


## API externa para teste de POST
@app.post('/external/users')
def create_user_ext(user:Customer):
    return user