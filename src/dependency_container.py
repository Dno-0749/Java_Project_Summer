# Dependency Injection Container

from dependency_injector import containers, providers

# Import your services and repositories here
# from infrastructure.repositories import SomeRepository
# from infrastructure.services import SomeService

class Container(containers.DeclarativeContainer):
    # Define your providers here
    # some_repository = providers.Factory(SomeRepository)
    # some_service = providers.Factory(SomeService, repository=some_repository)
    database = providers.Factory()
   