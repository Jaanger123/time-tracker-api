from decouple import Config, RepositoryEnv

DOTENV_PATH = '.env'

config = Config(RepositoryEnv(DOTENV_PATH))