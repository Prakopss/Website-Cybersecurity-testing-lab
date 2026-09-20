FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Initialize SQLite database
RUN python database.py

# Default port (kompatibel dengan Hugging Face Spaces & Cloud Docker)
ENV PORT=7860
EXPOSE 7860

CMD ["python", "app.py"]

