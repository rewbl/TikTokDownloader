from src.config.AppConfig import create_test_core_params
from src.config.RuntimeParameters import RuntimeCoreParameters


class DouyinGhostSession:
    ...

    def get_core_params(self) -> RuntimeCoreParameters:
        return create_test_core_params()


class DouyinServices:
    def get_session(self) -> DouyinGhostSession:
        return DouyinGhostSession()


DouyinServicesInstance = DouyinServices()
