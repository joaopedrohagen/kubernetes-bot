from dynaconf import Dynaconf

settings = Dynaconf(
  environments = True,
  env = 'default',
  settings_file = ['app/settings.toml', 'app/.secrets.toml'],
  lowercase_read = True
)
