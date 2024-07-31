# URL Shortener Service

A URL shortener service built with FastAPI, PostgreSQL, and Auth0 for authentication. This service allows users to shorten URLs, retrieve original URLs, list their shortened URLs, and delete them.

## Features

- Shorten URLs with a unique key.
- Retrieve the original URL from a shortened key.
- List all shortened URLs with pagination.
- Delete shortened URLs.
- Authentication using Auth0.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
  - [Authentication](#authentication)
  - [Shorten URL](#shorten-url)
  - [List Shortened URLs](#list-shortened-urls)
  - [Delete Shortened URL](#delete-shortened-url)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Clone the Repository

```bash
git clone https://github.com/akinolaemmanuel49/URL-Shortener-Service.git
cd URL-Shortener-Service
```

### Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

1. **Create an `.env` file** in the root directory and add the following environment variables:

    ```ini
    VERSION=1.0
    BASE_URL_PATH=/api
    SHORTENED_URL_BASE=http://localhost:8000/
    TOKEN_URI=http://localhost:8000/api/auth/token
    LOGOUT_REDIRECT_URI=http://localhost:8000
    APP_SECRET_KEY=your_secret_key

    APP_NAME=URL Shortener Service
    ADMIN_EMAIL=admin@example.com
    ITEMS_PER_PAGE=10
    DATABASE=postgresql+asyncpg://username:password@localhost/database_name

    PG_USERNAME=username
    PG_PASSWORD=password
    PG_DATABASE_NAME=database_name
    PG_HOST=localhost

    AUTH0_DOMAIN=your-auth0-domain
    AUTH0_CLIENT_ID=your-auth0-client-id
    AUTH0_CLIENT_SECRET=your-auth0-client-secret
    AUTH0_ALGORITHMS=RS256
    AUTH0_API_AUDIENCE=your-api-audience
    AUTH0_ISSUER=your-auth0-issuer
    ```

2. **Run Database Migrations**

    ```bash
    fastapi run
    ```

## Usage

1. **Start the Application**

    ```bash
    fastapi run
    ```

2. **Access the Application**

    Navigate to `http://localhost:8000` in your browser. You can use the provided endpoints to interact with the service.

## API Documentation

### Authentication

- **Login:** Redirects to Auth0 for authentication.

    `GET /api/auth/login`

- **Logout:** Logs the user out and redirects to a specified URL.

    `GET /api/auth/logout`

- **Get Access Token:** Exchange authorization code for an access token.

    `GET /api/auth/token`

### Shorten URL

- **Endpoint:** `POST /api/shorten/`

- **Request Body:**

    ```json
    {
        "original_url": "http://example.com"
    }
    ```

- **Response:**

    ```json
    {
        "shortened_url": "http://localhost:8000/abc123",
        "original_url": "http://example.com",
        "created": true
    }
    ```

### List Shortened URLs

- **Endpoint:** `GET /api/shorten/`

- **Query Parameters:**

    - `limit` (optional): Number of results per page.
    - `offset` (optional): Starting point for pagination.

- **Response:**

    ```json
    [
        {
            "shortened_url": "http://localhost:8000/abc123",
            "original_url": "http://example.com"
        }
    ]
    ```

### Delete Shortened URL

- **Endpoint:** `DELETE /api/shorten/{key}`

- **Response:**

    ```json
    {
        "message": "successfully deleted"
    }
    ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request to the repository.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.