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

## Operations API

The operations blueprint is registered by `app.py` under `/operations`:

- `GET /operations/dashboard` - operational metrics for activities, services, revenue, capacity, check-ins and late-return risks.
- `GET|POST /operations/activities` - list or create scheduled activities with capacity.
- `POST /operations/activities/{activity_id}/participants` - register a passenger and enforce capacity.
- `GET|POST /operations/checkins` - monitor or record passenger check-in status.
- `GET /operations/late-return-risks` - list passengers marked `LATE`, `MISSING` or `AT_RISK`.
- `POST /operations/transactions` - record service revenue.
- `GET|PUT /operations/reports/{trip_id}` - read or save a post-trip operations report.

The current `OperationsService` uses an in-memory store so the API can be exercised without a database. Replace it with a repository implementation before production deployment; data is cleared when the API process restarts.