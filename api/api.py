#!/usr/bin/env python3
# produz a API como carregável WSGI

import sys, logging, inspect

# setar logging
loglevel = logging.INFO
if "-d" in sys.argv or "--debug" in sys.argv or True:
  loglevel = logging.DEBUG
logging.basicConfig(format="[%(asctime)s] [%(levelname)s] %(message)s",
                    datefmt="%d/%m/%Y %H:%M:%S", level=loglevel)

# temos falcon?
try:
  import falcon
except:
  logging.critical("Instale Falcon!")
  sys.exit(1)

# gerar a API
import handlers, banco
db = banco.Banco("banco.db")
api = falcon.API()
instances = {}
for subname in dir(handlers):
  member = getattr(handlers, subname)
  if not inspect.isclass(member) or handlers.Handler not in member.mro():
    continue
  handler = member(db)
  print(f"{handler.__class__.__name__} tá on")
  instances[subname] = handler
  api.add_route(handler.route, handler)

for name, handler in instances.items():
  instances["Help"].add_handler(name, handler)

logging.info("API online!")

application = api
