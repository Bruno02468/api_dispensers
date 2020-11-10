/* scripts simples pra mexer com a api */

const in_key = document.getElementById("in_key");
const divbefore = document.getElementById("before");
const divafter = document.getElementById("after");
const keylist = document.getElementById("keys");
const keysec = document.getElementById("keysec");
const keyperm = document.getElementById("keyperm");
const dlist = document.getElementById("dispensers");
const dsel = document.getElementById("dispensers_sel");
const dact = document.getElementById("dispenser_action");
const in_did = document.getElementById("dispenser_id");
const dvol = document.getElementById("vol_max");
const dname = document.getElementById("dispenser_name");
const ddesc = document.getElementById("dispenser_desc");
const dedit = document.getElementById("dedit");
const curml = document.getElementById("current");
const curdesc = document.getElementById("seldesc");
const base = "/dispenser_api";
let token = "";

function bora() {
  token = in_key.value;
  fetch(base + "/token/" + token)
  .then(resp => resp.json()).then(function(json) {
    if (json["token_ok"]) {
      if (json["perm_level"] >= 2) {
        divbefore.style.display = "none";
        divafter.style.display = "block";
        refresh_all();
        setInterval(refresh_all, 1000);
      } else {
        alert("sem permissões");
      }
    } else {
      alert("token inexistente ou revogado");
    }
  });
  return false;
}

function refresh_all() {
  key_refresh();
  dispenser_refresh();
  details();
}

function key_refresh() {
  fetch(base + "/tokens", {
    body: JSON.stringify({"token": token}),
    headers: {
      "Content-Type": "application/json"
    },
    method: "PUT"
  })
  .then(resp => resp.json()).then(function(json) {
    keylist.innerHTML = "";
    for (let k of json) {
      let li = document.createElement("li");
      let ra = document.createElement("a");
      ra.href = "javascript:void(0);";
      ra.addEventListener("click", function() {
        key_revoke(k["segredo"]);
      });
      ra.innerText = "revogar";
      let rev = k["revogado"] ? "sim" : "não";
      li.innerText = "segredo \"" + k["segredo"] + "\" - nível "
        + k["perm_level"] + " - revogado? " + rev + " - ";
      li.appendChild(ra);
      keylist.appendChild(li);
    }
  });
}

function key_revoke(secret) {
  fetch(base + "/token/" + secret, {
    body: JSON.stringify({"token": token}),
    headers: {
      "Content-Type": "application/json"
    },
    method: "DELETE"
  })
  .then(resp => resp).then(function() {
    key_refresh();
  });
}

function key_new() {
  let sec = keysec.value;
  let perm = parseInt(keyperm.value);
  fetch(base + "/tokens", {
    body: JSON.stringify({
      "token": token,
      "segredo": sec,
      "perm_level": perm
    }),
    headers: {
      "Content-Type": "application/json"
    },
    method: "POST"
  })
  .then(resp => resp.json()).then(function(json) {
    key_refresh();
  });
  keysec.value = "";
  keyperm.value = 1;
  return false;
}

function dispenser_refresh() {
  fetch(base + "/dispensers")
  .then(resp => resp.json()).then(function(json) {
    dlist.innerHTML = "";
    let dprev = dsel.value;
    dsel.innerHTML = "";
    for (let d of json) {
      let li = document.createElement("li");
      let ra = document.createElement("a");
      ra.href = "javascript:void(0);";
      ra.addEventListener("click", function() {
        dispenser_delete(d["id"]);
      });
      ra.innerText = "deletar";
      let edl = document.createElement("a");
      edl.href = "javascript:void(0);";
      edl.addEventListener("click", function() {
        dact.value = "edit";
        in_did.value = d["id"];
        dvol.value = d["vol_max"];
        dname.value = d["nome"];
        ddesc.value = d["desc"];
        dedit.innerText = "editar o dispenser #" + d["id"];
      });
      edl.innerText = "editar";
      li.innerText = "#" + d["id"] + ": \"" + d["nome"] + "\" - máx "
        + d["vol_max"] + " mL - ";
      let spacer = document.createTextNode(" - ");
      li.append(edl);
      li.append(spacer);
      li.append(ra);
      dlist.appendChild(li);
      let opt = document.createElement("option");
      opt.value = d["id"];
      opt.innerText = d["nome"];
      dsel.appendChild(opt);
    }
    dsel.value = dprev;
  });
}

function dispenser_delete(did) {
  fetch(base + "/dispenser/" + did, {
    body: JSON.stringify({"token": token}),
    headers: {
      "Content-Type": "application/json"
    },
    method: "DELETE"
  })
  .then(resp => resp).then(function() {
    dispenser_refresh();
  });
}

function dispenser_alter() {
  let body = {
    "token": token,
    "vol_max": parseInt(dvol.value),
    "nome": dname.value,
    "desc": ddesc.value,
  };
  let did = in_did.value || 0;
  let act = null;
  let mth = null;
  if (parseInt(did) && dact.value == "edit") {
    act = "/dispenser/" + did;
    mth = "PUT";
  } else {
    act = "/dispensers";
    mth = "POST";
  }
  fetch(base + act, {
    body: JSON.stringify(body),
    headers: {
      "Content-Type": "application/json"
    },
    method: mth
  })
  .then(resp => resp).then(function() {
    dispenser_refresh();
    dname.value = "";
    dvol.value = "";
    ddesc.value = "";
    dact.value = "create";
  });
  return false;
}

function details() {
  let did = dsel.value;
  if (!did) return;
  fetch(base + "/dispenser/" + did)
  .then(resp => resp.json()).then(function(json) {
    let perc = Math.ceil(json["valor_atual"]/json["vol_max"]*100);
    curml.innerText = json["valor_atual"] + " mL (" + perc + "%)";
    curdesc.innerText = json["desc"];
  });
}

function consume() {
  let did = dsel.value;
  if (!did) return;
  fetch(base + "/aciona/" + did + "/consumo_admin", {
    body: JSON.stringify({
      "token": token,
      "delta": -10
    }),
    headers: {
      "Content-Type": "application/json"
    },
    method: "POST"
  })
  .then(resp => resp).then(function() {
    details();
  });
}

function recharge() {
  let did = dsel.value;
  if (!did) return;
  fetch(base + "/recarga/" + did, {
    body: JSON.stringify({
      "token": token
    }),
    headers: {
      "Content-Type": "application/json"
    },
    method: "POST"
  })
  .then(resp => resp).then(function() {
    details();
  });
}
