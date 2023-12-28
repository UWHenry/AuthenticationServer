# Project README
This project is a FastAPI-based web application that provides a simple user management system with token-based authentication using JSON Web Tokens (JWT). The application uses SQLAlchemy to interact with a PostgreSQL database, and the implementation is entirely asynchronous.

## Table of Contents
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Usage](#usage)
* [Features](#features)

## Prerequisites
Before you proceed, make sure you have the following installed on your machine:
* Docker & Docker Compose: https://www.docker.com/get-started
  
## Installation
1. Clone the repository to your local machine:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
2. Build and start the services using Docker Compose:
   ```bash
   docker compose up -d
   ```

## Usage
Once the services are up and running, you can access the application through a web browser.
* Backend API: http://localhost:8000/
* Swagger API documentation: http://localhost:8443/docs

## Features
* FastAPI: Backend framework for building the API.
    * User Management
        * Create, retrieve, update, and delete user information through dedicated endpoints.
    * Token-based Authentication
        * Utilizes JWT for access tokens to secure API endpoints.
    * Token Expiration Cleanup
        * Periodically deletes expired tokens to maintain system cleanliness.
        * Cleanup interval is set to every 60 minutes (TOKEN_CLEANUP_MINUTES).
    * Async Implementation
        * Leverages FastAPI's asynchronous capabilities and uses SQLAlchemy with async support for efficient database interactions.
    * Testing
        * Includes a suite of tests to ensure the correctness and reliability of the implemented functionalities. 
        * Use pytest to run the tests.
* PostgreSQL: Database management system.