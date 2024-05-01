# Use an official Python runtime as the base image
FROM python:3.9-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8501 available for Streamlit app
EXPOSE 8501

# Run the Streamlit app using the command specified in the CMD directive
CMD ["python", "-m", "streamlit", "run", "app.py"]