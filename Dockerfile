# Use an official Python runtime as a parent image
FROM python:3
ENV PTYHONUNBUFFERED 1

# Set environment variable
ENV NEO4J_URL=neo4j NEO4J_USERNAME=neo4j NEO4J_PASSWORD=neo4j2

# Make port 80 available to the world outside this container
EXPOSE 8000

# Set the working directory to /app
RUN mkdir /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY api/ ./api
COPY libs/ ./libs
COPY mapper/ ./mapper
COPY requirements.txt .
COPY manage.py .

# Install any needed packages specified in requirements.txt
# RUN pip install --upgrade pip 
RUN pip install -r ./requirements.txt

#Uncomment if you're building with docker-compose and neo4j is alreading running
# WORKDIR /app/libs
# RUN python main.py
# WORKDIR /app

# Run app.py when the container launches
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
