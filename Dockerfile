FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY models.py app.py ./

ENV PORT=5250

EXPOSE 5250

CMD ["streamlit", "run", "app.py", "--server.port=5250", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"]
