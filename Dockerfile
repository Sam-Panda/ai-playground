# Use an official Python runtime as the base image
FROM python:3.12.5-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirement.txt .
# Install the Python dependencies
RUN pip install --no-cache-dir -r requirement.txt
# Copy the rest of the application code into the container, except .env file
COPY . .
# Set environment variables

ENV MI_CLINET_ID=''
ENV COSMOS_ENDPOINT=''
ENV AZURE_SEARCH_SERVICE_ENDPOINT=''
ENV CLIENT_ID=''
ENV CLIENT_SECRET=''
ENV TENANT_ID=''
ENV AZURE_COSMOSDB_RESOURCE_ID_CONNECTION_STRING=''
ENV AZURE_OPENAI_ENDPOINT=''


# Set the command to run the application
# CMD ["ls", "-la" , "."]

# # Set the command to run the application
CMD ["./entrypoint.sh"]



