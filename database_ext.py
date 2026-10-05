from sqlalchemy import create_engine,text   

out_engine = create_engine('postgresql://postgres:senha@host:5432/usu')

with out_engine.connect() as out:
    out.execute(text("""
            Create table if not exists projetos.external(
                ID Serial primary key,
                external_code VARCHAR(50),
                company_name  VARCHAR(50),
                email         Varchar(20),
                created_at Timestamp default CURRENT_TIMESTAMP
            )
"""))
    out.commit()