#!/usr/bin/env python3
# contém os handlers de requisição

if __name__ == "__main__":
  print("Este arquivo não deve ser executado. Ele é um módulo!")
  sys.exit(0)

import sys, falcon
from falcon.media.validators import jsonschema as jsonschema


# superclasse para os handlers
class Handler(object):
  description = "Este é o módulo abstrato que não faz nada."
  usage = "GET"
  route = "/nil"
  db = None

  def __init__(self, database):
    self.db = database


# documentação gerada automagicamente
class Help(Handler):
  description = "Sim, esta API gera a própria documentação =)"
  usage = "GET retorna tudo"
  route = "/"
  instances = {}

  def add_handler(self, name, h):
    self.instances[name] = {
      "descricao": h.description,
      "como_usar": h.usage,
      "rota": h.route
    }

  def on_get(self, req, resp):
    resp.media = self.instances


# testar tokens e deletar também
class Token(Handler):
  description = "Testar ou revogar tokens de autenticação."
  usage = "GET testa, DELETE revoga."
  route = "/token/{token}"

  def on_get(self, req, resp, token):
    resp.media = {
      "token_ok": self.db.token_ok(token),
      "perm_level": self.db.token_perm(token)
    }

  def on_delete(self, req, resp, token):
    self.db.revoke(token)


# criar e listar tokens
class Tokens(Handler):
  description = "Criar e listar tokens"
  usage = "PUT lista todos, POST cria um."
  route = "/tokens"

  put_schema = {
  "type": "object",
  "title": "Listagem de tokens",
    "properties": {
      "token": {
        "type": "string",
        "description": "Token de admin (nível mínimo 2)"
      }
    },
    "required": ["token"]
  }

  post_schema = {
    "type": "object",
    "title": "Criação de um token via POST",
    "properties": {
      "segredo": {
        "type": "string",
        "description": "O segredo do token",
        "minLength": 1,
        "maxLength": 512
      },
      "perm_level": {
        "type": "integer",
        "description": "Nível de permissão (0=read, 1=write, 2=admin)",
        "minimum": 0,
        "maximum": 2
      },
      "token": {
        "type": "string",
        "description": "Token de admin (nível mínimo 2)"
      }
    },
    "required": ["segredo", "perm_level", "token"]
  }

  @jsonschema.validate(put_schema)
  def on_put(self, req, resp):
    resp.media = self.db.all_tokens()

  @jsonschema.validate(post_schema)
  def on_post(self, req, resp):
    perm = self.db.token_perm(req.media.get("token"))
    if perm is not None and perm >= 2:
      self.db.add_token(req.media.get("segredo"), req.media.get("perm_level"))
    else:
      resp.status = falcon.HTTP_403


# criar e listar dispensers
class Dispensers(Handler):
  description = "Adicionar/listar dispensers."
  usage = "GET lista todos, POST cria um."
  route = "/dispensers"

  post_schema = {
    "type": "object",
    "title": "Inserção de dispenser via POST.",
    "description": "Info de um dispenser para adicionar.",
    "properties": {
      "vol_max": {
        "type": "integer",
        "description": "Volume máximo em mL.",
        "minimum": 0
      },
      "nome": {
        "type": "string",
        "description": "Nome simples para o dispenser.",
        "minLength": 3
      },
      "desc": {
        "type": "string",
        "description": "Descrição detalhada opcional do dispenser"
      },
      "token": {
        "type": "string",
        "description": "Seu token de admin (perm mínimo = 2)"
      }
    },
    "required": ["vol_max", "nome", "token"]
  }

  def on_get(self, req, resp):
    resp.media = self.db.all_dispensers()

  @jsonschema.validate(post_schema)
  def on_post(self, req, resp):
    perm = self.db.token_perm(req.media.get("token"))
    if perm is not None and perm >= 2:
      self.db.add_dispenser(
        req.media.get("vol_max"),
        req.media.get("nome"),
        req.media.get("desc") or ""
      )
    else:
      resp.status = falcon.HTTP_403


# acessar e alterar dispensers
class Dispenser(Handler):
  description = "Acessar e alterar dispensers individuais."
  usage = "GET retorna dados, PUT edita, DELETE remove."
  route = "/dispenser/{id_dispenser}"

  put_schema = {
    "type": "object",
    "title": "Edição de dispenser via PUT.",
    "description": "Info de um dispenser para editar.",
    "properties": {
      "vol_max": {
        "type": "integer",
        "description": "Volume máximo em mL.",
        "minimum": 0
      },
      "nome": {
        "type": "string",
        "description": "Nome simples para o dispenser.",
        "minLength": 3
      },
      "desc": {
        "type": "string",
        "description": "Descrição detalhada opcional do dispenser"
      },
      "token": {
        "type": "string",
        "description": "Seu token de admin (perm mínimo = 2)"
      }
    },
    "required": ["vol_max", "nome", "token"]
  }

  delete_schema = {
    "type": "object",
    "description": "Deleção de dispenser via DELETE",
    "properties": {
      "token": {
        "type": "string",
        "description": "Seu token de admin (perm mínimo = 2)"
      }
    },
    "required": ["token"]
  }

  def on_get(self, req, resp, id_dispenser):
    if self.db.dispenser_exists(id_dispenser):
      resp.media = self.db.dispenser_details(id_dispenser)
    else:
      resp.status = falcon.HTTP_404

  @jsonschema.validate(put_schema)
  def on_put(self, req, resp, id_dispenser):
    perm = self.db.token_perm(req.media.get("token"))
    if perm is not None and perm >= 2:
      if self.db.dispenser_exists(id_dispenser):
        self.db.edit_dispenser(
          id_dispenser,
          req.media.get("vol_max"),
          req.media.get("nome"),
          req.media.get("desc") or ""
        )
      else:
        resp.status = falcon.HTTP_404
    else:
      resp.status = falcon.HTTP_403

  @jsonschema.validate(delete_schema)
  def on_delete(self, req, resp, id_dispenser):
    perm = self.db.token_perm(req.media.get("token"))
    if perm is not None and perm >= 2:
      if self.db.dispenser_exists(id_dispenser):
        self.db.delete_dispenser(id_dispenser)
      else:
        resp.status = falcon.HTTP_404
    else:
      resp.status = falcon.HTTP_403


# informar acionamento
class Acionamento(Handler):
  description = "Usado pelos dispensers para informar acionamentos."
  usage = "POST informa um acionamento por delta. PUT informa valor final."
  route = "/aciona/{id_dispenser}/{tipo}"

  post_schema = {
    "type": "object",
    "title": "Acionamento por delta",
    "description": "Informa uma variação de volume.",
    "properties": {
      "delta": {
        "type": "integer",
        "description": "Variação de volume"
      },
      "token": {
        "type": "string",
        "description": "Seu token de dispenser (perm mínimo = 1)"
      }
    },
    "required": ["delta", "token"]
  }

  put_schema = {
    "type": "object",
    "title": "Acionamento por valor absoluto",
    "description": "Informa um valor de volume.",
    "properties": {
      "total": {
        "type": "integer",
        "description": "Valor de volume total"
      },
      "token": {
        "type": "string",
        "description": "Seu token de dispenser (perm mínimo = 1)"
      }
    },
    "required": ["total", "token"]
  }

  @jsonschema.validate(post_schema)
  def on_post(self, req, resp, id_dispenser, tipo):
    perm = self.db.token_perm(req.media.get("token"))
    if perm is not None and perm >= 1:
      if self.db.dispenser_exists(id_dispenser):
        self.db.dispenser_set(
          id_dispenser,
          req.media.get("token"),
          tipo,
          req.media.get("delta"),
          True
        )
      else:
        resp.status = falcon.HTTP_404
    else:
      resp.status = falcon.HTTP_403

  @jsonschema.validate(put_schema)
  def on_put(self, req, resp, id_dispenser, tipo):
    perm = self.db.token_perm(req.media.get("token"))
    if perm is not None and perm >= 1:
      if self.db.dispenser_exists(id_dispenser):
        self.db.dispenser_set(
          id_dispenser,
          req.media.get("token"),
          tipo,
          req.media.get("total"),
          False
        )
      else:
        resp.status = falcon.HTTP_404
    else:
      resp.status = falcon.HTTP_403


# informar recarga de dispenser
class Recharge(Handler):
  description = "Informar recarga de dispenser."
  usage = "POST informa uma recarga."
  route = "/recarga/{id_dispenser}"

  post_schema = {
    "type": "object",
    "title": "Informa um dispenser para recarga",
    "description": "Basicamente só tem um token dentro mesmo.",
    "properties": {
      "token": {
        "type": "string",
        "description": "Seu token de dispenser (perm mínimo = 1)"
      }
    },
    "required": ["token"]
  }

  @jsonschema.validate(post_schema)
  def on_post(self, req, resp, id_dispenser):
    perm = self.db.token_perm(req.media.get("token"))
    if perm is not None and perm >= 1:
      if self.db.dispenser_exists(id_dispenser):
        self.db.dispenser_recharge(id_dispenser, req.media.get("token"))
      else:
        resp.status = falcon.HTTP_404
    else:
      resp.status = falcon.HTTP_403
