import dotenv


def update_environment_variable(key: str, value: str) -> None:
    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)
    dotenv.set_key(dotenv_file, key, value)
