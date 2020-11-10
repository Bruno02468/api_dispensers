CREATE TABLE "dispensers" (
  "id" INTEGER NOT NULL UNIQUE,
  "vol_max" INTEGER NOT NULL DEFAULT 500,
  "nome" TEXT NOT NULL UNIQUE,
  "desc" TEXT,
  PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "tokens" (
  "segredo" TEXT NOT NULL UNIQUE,
  "revogado" INTEGER NOT NULL DEFAULT 0,
  "perm_level" INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY("hash")
);

CREATE TABLE "acessos" (
  "id_acesso" INTEGER NOT NULL UNIQUE,
  "token" TEXT NOT NULL DEFAULT '?',
  "id_dispenser" INTEGER NOT NULL,
  "valor_antes" INTEGER NOT NULL,
  "delta" INTEGER NOT NULL,
  "valor_depois" INTEGER NOT NULL,
  "tipo_evento" TEXT NOT NULL,
  "quando" TEXT NOT NULL,
  PRIMARY KEY("id_acesso" AUTOINCREMENT)
);
