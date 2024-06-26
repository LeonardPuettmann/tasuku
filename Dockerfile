# Use an official Python runtime as the base image
FROM python:3.11-slim-bullseye

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements.txt file
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip

# Add the current directory contents into the container at /app
ADD . /app

# Make port 8501 available for Streamlit app
EXPOSE 8501

# Run the Streamlit app using the command specified in the CMD directive
CMD ["python", "-m", "streamlit", "run", "app.py"]