#!/usr/bin/env python3
# código pra mexer no banco de dados

import sys, os, sqlite3, logging
from datetime import datetime

# garantir que somos um módulo
if __name__ == "__main__":
  print("Este arquivo não deve ser executado. Ele é um módulo!")
  sys.exit(0)

# representa o banco da API
class Banco(object):
  def __init__(self, filnam):
    if not os.path.isfile(filnam):
      logging.error(f"Arquivo do banco {filnam} não existe!")
      sys.exit(1)
    self.filnam = filnam
    self.conn = sqlite3.connect(filnam)
    self.conn.row_factory = sqlite3.Row
    logging.info("Conectado ao banco.")

  def get_token(self, secret):
    c = self.conn.cursor()
    c.execute(
      "SELECT perm_level FROM tokens WHERE segredo=? AND revogado=0;",
      (secret,)
    )
    return c.fetchone()

  def all_tokens(self):
    c = self.conn.cursor()
    c.execute("SELECT segredo, perm_level, revogado FROM tokens;")
    return list(map(dict, c.fetchall()))

  def token_ok(self, token):
    return self.get_token(token) is not None

  def token_perm(self, token):
    k = self.get_token(token)
    return k["perm_level"] if k is not None else -1

  def revoke(self, token):
    c = self.conn.cursor()
    c.execute("UPDATE tokens SET revogado=1 WHERE segredo=?;", (token,))
    self.conn.commit()

  def add_token(self, secret, perm_level):
    c = self.conn.cursor()
    c.execute(
      "INSERT INTO tokens (segredo, perm_level) VALUES (?, ?);",
      (secret, perm_level)
    )
    self.conn.commit()

  def dispenser_history(self, dispenser_id):
    c = self.conn.cursor()
    c.execute(
      "SELECT id_acesso, token, id_dispenser, valor_antes, delta, "
      "valor_depois, tipo_evento, quando FROM acessos WHERE id_dispenser=? "
      "ORDER BY id_acesso DESC;",
      (dispenser_id,)
    )
    return list(map(dict, c.fetchall()))
  
  # expensive!
  def value_at(self, dispenser_id, when):
    det = self.dispenser_details(dispenser_id)
    val = 0
    for acc in det["historico"]:
      qnd = datetime.fromisoformat(acc["quando"])
      if qnd > when:
        break
      val = acc["valor_depois"]
    return val

  def all_dispensers(self):
    c = self.conn.cursor()
    c.execute("SELECT id, vol_max, nome, desc FROM dispensers;")
    return list(map(dict, c.fetchall()))

  def dispenser_details(self, dispenser_id):
    c = self.conn.cursor()
    c.execute(
      "SELECT id, vol_max, nome, desc FROM dispensers WHERE id=?;",
      (dispenser_id,)
    )
    row = c.fetchone()
    if row is None:
      return None
    dispenser = dict(row)
    dispenser["historico"] = self.dispenser_history(row["id"])
    dispenser["valor_atual"] = 0
    if len(dispenser["historico"]):
      dispenser["valor_atual"] = dispenser["historico"][0]["valor_depois"]
    return dispenser

  def add_dispenser(self, vol_max, name, desc = ""):
    c = self.conn.cursor()
    c.execute(
      "INSERT INTO dispensers (vol_max, nome, desc) "
      "VALUES (?, ?, ?);", (vol_max, name, desc)
    )
    self.conn.commit()

  def dispenser_exists(self, dispenser_id):
    return self.dispenser_details(dispenser_id) is not None

  def edit_dispenser(self, dispenser_id, vol_max, name, desc = ""):
    c = self.conn.cursor()
    c.execute(
      "UPDATE dispensers SET vol_max=?, nome=?, desc=? WHERE id=?;",
      (vol_max, name, desc, dispenser_id)
    )
    self.conn.commit()

  def delete_dispenser(self, dispenser_id):
    c = self.conn.cursor()
    c.execute("DELETE FROM dispensers WHERE id=?;", (dispenser_id,))
    self.conn.commit()

  def dispenser_set(self, dispenser_id, token, etype, val, is_delta = False):
    current = self.dispenser_details(dispenser_id)["valor_atual"]
    if is_delta:
      after = max(0, current + val)
    else:
      after = max(0, val)
    delta = after - current
    isonow = datetime.now().isoformat()
    c = self.conn.cursor()
    c.execute(
      "INSERT INTO acessos (token, id_dispenser, valor_antes, delta, "
      "valor_depois, tipo_evento, quando) VALUES (?, ?, ?, ?, ?, ?, ?);",
      (token, dispenser_id, current, delta, after, etype, isonow)
    )
    self.conn.commit()

  def dispenser_recharge(self, dispenser_id, token):
    val = self.dispenser_details(dispenser_id)["vol_max"]
    self.dispenser_set(dispenser_id, token, "recarga", val, False)
