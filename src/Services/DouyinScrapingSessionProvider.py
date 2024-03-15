from src.config.AppConfig import create_test_core_params


class DouyinGhostSession:
    ...

    def get_core_params(self) :
        return create_test_core_params()


class DouyinServices:
    def get_session(self) -> DouyinGhostSession:
        return DouyinGhostSession()


DouyinServicesInstance = DouyinServices()
