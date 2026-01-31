FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . . 
# this copies everything in current directory including requirements.txt which we have copied ABOVE 
# if we added this part before above RUN command WITHOUT using COPY requirements.txt seprately
# then for any changes in our directory pip install will run again and install everything on each build 
# this happens because above RUN command is dependent on requirements.txt and since we copy it with everything using COPY .. 
# any changes in . would make docker think that changes are done to requirements.txt 

CMD ["gunicorn", "ledger_service.wsgi:application", "--bind", "0.0.0.0:8000"]
# instead of python manage.py runserver, which is not suitable for production