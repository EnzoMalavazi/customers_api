from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:senha@host:porta/usuario')

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
            External_ID integer,
            integration_status VARCHAR(20),
            Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP); 
"""))
    conn.commit()