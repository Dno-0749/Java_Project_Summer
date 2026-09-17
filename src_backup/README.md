# Flask Clean Architecture

This project is structured using the Clean Architecture principles, which promotes separation of concerns and maintainability. Below is an overview of the project's structure and its components.

## Directory Structure

- **migrations/**: Contains database migration files.
- **scripts/**: Contains scripts for running and managing the application, such as `run_postgres.sh` for PostgreSQL.
- **api/**: Contains the API-related components.
  - **controllers/**: Controllers for handling API requests.
  - **schemas/**: Marshmallow schemas for data validation and serialization.
  - **middleware.py**: Middleware functions for processing requests and responses.
  - **responses.py**: Functions for handling API responses.
  - **requests.py**: Functions for handling API requests.
- **infrastructure/**: Contains components that interact with external systems.
  - **services/**: Services that use third-party libraries or services (e.g., email service).
  - **databases/**: Database adapters and initialization code.
  - **repositories/**: Repositories for interacting with the databases.
  - **models/**: Database models.
- **domain/**: Contains the core business logic.
  - **constants.py**: Constants used throughout the application.
  - **exceptions.py**: Custom exceptions for the application.
  - **models/**: Business logic models.
- **services/**: Services for interacting with the domain (business logic).
- **app.py**: The main entry point of the application, initializing the app and setting up routes.
- **config.py**: Configuration settings for the application.
- **cors.py**: Handles Cross-Origin Resource Sharing (CORS) settings.
- **create_app.py**: Factory function to create the Flask application instance.
- **dependency_container.py**: Manages dependency injection for the application.
- **error_handler.py**: Defines error handling logic for the application.
- **logging.py**: Sets up logging configurations for the application.

## Getting Started

To get started with the project, ensure you have the necessary dependencies installed and follow the setup instructions provided in the respective files. 

## Contributing

Contributions are welcome! Please follow the contribution guidelines outlined in the project documentation.