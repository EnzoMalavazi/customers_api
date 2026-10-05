from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:Senha@host:5432/user')

with engine.connect() as conn:
    schema = conn.execute(text(""" 
       Create schema if not exists projetos; 
    """))

    resultado = conn.execute(text(""" 
    create table if not exists projetos.clientes (
            ID SERIAL PRIMARY KEY,
            Customer_Name VARCHAR(50),
            Customer_Age INTEGER,
            Customer_Email VARCHAR(50),
            Access_Level VARCHAR(30),
            External_ID VARCHAR(40),
            integration_status VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP); 
"""))
    conn.commit()