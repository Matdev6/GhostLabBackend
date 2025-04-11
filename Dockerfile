FROM python:3.11-slim


COPY . /app
WORKDIR /app


# Copia o requirements.txt da pasta app
COPY app/requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt 
# Cria o diretório no container
RUN mkdir -p /app/uploads


# Copia todo o conteúdo da pasta app para dentro do container
COPY app /app

# Expõe a porta do FastAPI
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
