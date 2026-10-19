const api = {
  token: localStorage.getItem("mbfToken"),
  user: JSON.parse(localStorage.getItem("mbfUser") || "null")
};

const state = {
  parts: [],
  requests: [],
  movements: [],
  users: [],
  signupRequests: [],
  view: "dashboard"
};

const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(path, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        "X-Session-Token": api.token || "",
        ...(options.headers || {})
      }
    });
  } catch {
    throw new Error("Servidor nao esta rodando. Abra a pasta no VS Code, rode python server.py e acesse http://localhost:8000");
  }
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Erro no sistema");
  return data;
}

function statusOf(part) {
  if (part.quantity <= 0) return "out";
  if (part.quantity <= part.min_quantity) return "low";
  return "ok";
}

function statusLabel(status) {
  return { ok: "Normal", low: "Baixo", out: "Zerado" }[status] || status;
}

function money(value) {
  return Number(value || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function csvDownload(filename, rows) {
  const csv = rows.map(row => row.map(value => `"${String(value ?? "").replaceAll('"', '""')}"`).join(";")).join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
}

async function loadAll() {
  const [parts, requestsData, movements] = await Promise.all([
    request("/api/parts"),
    request("/api/requests"),
    request("/api/movements")
  ]);
  state.parts = parts.parts;
  state.requests = requestsData.requests;
  state.movements = movements.movements;
  if (api.user.role === "admin") {
    const [usersData, signupData] = await Promise.all([
      request("/api/users"),
      request("/api/signup-requests")
    ]);
    state.users = usersData.users;
    state.signupRequests = signupData.signup_requests;
  } else {
    state.users = [];
    state.signupRequests = [];
  }
  render();
}

function showApp() {
  $("#loginScreen").classList.add("hidden");
  $("#app").classList.remove("hidden");
  $("#userLabel").textContent = `${api.user.name} - ${api.user.role === "admin" ? "Admin" : "Usuario"}`;
  $$(".admin-only").forEach(el => el.classList.toggle("hidden", api.user.role !== "admin"));
}

function showLogin() {
  $("#loginScreen").classList.remove("hidden");
  $("#app").classList.add("hidden");
}

function render() {
  renderMetrics();
  renderParts();
  renderRequests();
  renderMovements();
  renderUsers();
  renderSignupRequests();
  renderDashboard();
  renderReports();
  updateView();
}

function renderMetrics() {
  const totalValue = state.parts.reduce((sum, part) => sum + Number(part.quantity || 0) * Number(part.unit_price || 0), 0);
  const topPart = [...state.parts].sort((a, b) => Number(b.quantity || 0) - Number(a.quantity || 0))[0];
  const suppliers = new Set(state.parts.map(part => part.supplier).filter(Boolean));
  $("#metricParts").textContent = state.parts.length;
  $("#metricLow").textContent = state.parts.filter(part => statusOf(part) !== "ok").length;
  $("#metricPending").textContent = state.requests.filter(req => req.status === "pendente").length;
  $("#metricSignup").textContent = state.signupRequests.filter(req => req.status === "pendente").length;
  $("#metricValue").textContent = money(totalValue);
  $("#metricTopPart").textContent = topPart ? topPart.name : "-";
  $("#metricSuppliers").textContent = suppliers.size;
}

function filteredParts() {
  const query = $("#searchInput").value.trim().toLowerCase();
  const category = $("#categoryFilter").value;
  return state.parts.filter(part => {
    const text = [part.code, part.name, part.location, part.category, part.supplier, part.sector].join(" ").toLowerCase();
    return text.includes(query) && (!category || part.category === category);
  });
}

function renderParts() {
  const rows = filteredParts();
  $("#partsTable").innerHTML = rows.map(part => {
    const status = statusOf(part);
    const adminActions = api.user.role === "admin"
      ? `<button class="secondary" onclick="editPart(${part.id})">Editar</button><button class="secondary" onclick="deletePart(${part.id})">Excluir</button>`
      : "";
    return `
      <tr>
        <td><strong>${part.code}</strong></td>
        <td>${part.name}<br><small>${part.description || ""}</small></td>
        <td>${part.category}</td>
        <td>${part.supplier || "-"}<br><small>${money(part.unit_price)} / ${part.unit}</small></td>
        <td>${part.location}</td>
        <td><strong>${part.quantity}</strong> ${part.unit}<br><small>Min. ${part.min_quantity}</small></td>
        <td><span class="badge ${status}">${statusLabel(status)}</span></td>
        <td><div class="row-actions"><button onclick="openRequest(${part.id})">Solicitar</button>${adminActions}</div></td>
      </tr>
    `;
  }).join("") || `<tr><td colspan="7">Nenhuma peca encontrada.</td></tr>`;
}

function renderRequests() {
  $("#requestsList").innerHTML = state.requests.map(req => {
    const adminActions = api.user.role === "admin" && req.status === "pendente"
      ? `<div class="row-actions"><button onclick="reviewRequest(${req.id}, 'aprovado')">Aprovar</button><button class="secondary" onclick="reviewRequest(${req.id}, 'rejeitado')">Rejeitar</button></div>`
      : "";
    return `
      <article class="request-card">
        <div class="row-actions">
          <strong>#${req.id} - ${req.part_code} ${req.part_name}</strong>
          <span class="badge ${req.status}">${req.status}</span>
        </div>
        <p><strong>Quantidade:</strong> ${req.quantity} ${req.unit}</p>
        <p><strong>Solicitante:</strong> ${req.user_name}</p>
        <p><strong>Comentario:</strong> ${req.comment || "Sem comentario"}</p>
        <p><strong>Resposta admin:</strong> ${req.admin_note || "Sem resposta"}</p>
        ${adminActions}
      </article>
    `;
  }).join("") || `<div class="request-card"><p>Nenhuma solicitacao encontrada.</p></div>`;
}

function renderMovements() {
  $("#movementsList").innerHTML = state.movements.map(item => `
    <article class="request-card">
      <strong>${item.type.toUpperCase()} - ${item.part_name || "Sistema"}</strong>
      <p>Quantidade: ${item.quantity}</p>
      <p>Usuario: ${item.user_name || "Sem usuario"} | ${item.created_at}</p>
      <p>${item.note || ""}</p>
    </article>
  `).join("") || `<div class="request-card"><p>Nenhuma movimentacao encontrada.</p></div>`;
}

function renderUsers() {
  const list = $("#usersList");
  if (!list) return;
  list.innerHTML = state.users.map(user => `
    <article class="request-card">
      <div class="row-actions">
        <strong>${user.name}</strong>
        <span class="badge ${user.active ? "ativo" : "bloqueado"}">${user.active ? "ativo" : "bloqueado"}</span>
      </div>
      <p>Login: ${user.username}</p>
      <p>Perfil: ${user.role === "admin" ? "Administrador" : "Usuario comum"}</p>
      <p>Setor: ${user.sector || "Nao informado"}</p>
      <div class="row-actions">
        <button class="secondary" onclick="editUser(${user.id})">Editar</button>
        <button class="secondary" onclick="deleteUser(${user.id})">Excluir</button>
      </div>
    </article>
  `).join("") || `<div class="request-card"><p>Nenhum usuario liberado.</p></div>`;
}

function renderSignupRequests() {
  const list = $("#signupRequestsList");
  if (!list) return;
  list.innerHTML = state.signupRequests.map(req => {
    const actions = req.status === "pendente"
      ? `<div class="row-actions"><button onclick="reviewSignup(${req.id}, 'aprovado')">Liberar</button><button class="secondary" onclick="reviewSignup(${req.id}, 'rejeitado')">Rejeitar</button></div>`
      : "";
    return `
      <article class="request-card">
        <div class="row-actions">
          <strong>${req.name}</strong>
          <span class="badge ${req.status}">${req.status}</span>
        </div>
        <p><strong>Login solicitado:</strong> ${req.username}</p>
        <p><strong>Setor:</strong> ${req.sector || "Nao informado"}</p>
        <p><strong>Motivo:</strong> ${req.reason || "Sem motivo informado"}</p>
        <p><strong>Resposta admin:</strong> ${req.admin_note || "Sem resposta"}</p>
        ${actions}
      </article>
    `;
  }).join("") || `<div class="request-card"><p>Nenhum pedido de cadastro.</p></div>`;
}

function renderDashboard() {
  const categoryTotals = state.parts.reduce((acc, part) => {
    acc[part.category] = (acc[part.category] || 0) + 1;
    return acc;
  }, {});
  const maxCategory = Math.max(1, ...Object.values(categoryTotals));
  $("#categoryChart").innerHTML = Object.entries(categoryTotals).map(([category, total]) => `
    <div class="chart-row">
      <header><strong>${category}</strong><span>${total}</span></header>
      <div class="bar"><span style="--w:${Math.round((total / maxCategory) * 100)}%"></span></div>
    </div>
  `).join("") || `<p>Nenhuma peca cadastrada.</p>`;

  const critical = state.parts.filter(part => statusOf(part) !== "ok");
  $("#criticalList").innerHTML = critical.map(part => `
    <article class="request-card">
      <div class="row-actions">
        <strong>${part.code} - ${part.name}</strong>
        <span class="badge ${statusOf(part)}">${statusLabel(statusOf(part))}</span>
      </div>
      <p>Atual: ${part.quantity} ${part.unit} | Minimo: ${part.min_quantity} ${part.unit}</p>
      <p>Fornecedor: ${part.supplier || "Nao informado"}</p>
    </article>
  `).join("") || `<div class="request-card"><p>Nenhum item critico no momento.</p></div>`;
}

function renderReports() {
  const critical = state.parts.filter(part => statusOf(part) !== "ok");
  $("#criticalReport").innerHTML = critical.map(part => `
    <tr>
      <td><strong>${part.code}</strong></td>
      <td>${part.name}</td>
      <td>${part.quantity} ${part.unit}</td>
      <td>${part.min_quantity} ${part.unit}</td>
      <td>${Math.max(0, part.min_quantity - part.quantity)} ${part.unit}</td>
      <td>${part.supplier || "-"}</td>
    </tr>
  `).join("") || `<tr><td colspan="6">Nenhum item abaixo do minimo.</td></tr>`;

  const requestTotals = state.requests.reduce((acc, req) => {
    acc[req.status] = (acc[req.status] || 0) + 1;
    return acc;
  }, {});
  const maxRequests = Math.max(1, ...Object.values(requestTotals));
  $("#requestChart").innerHTML = ["pendente", "aprovado", "rejeitado"].map(status => {
    const total = requestTotals[status] || 0;
    return `
      <div class="chart-row">
        <header><strong>${status}</strong><span>${total}</span></header>
        <div class="bar"><span style="--w:${Math.round((total / maxRequests) * 100)}%"></span></div>
      </div>
    `;
  }).join("");
}

function updateView() {
  const titles = {
    estoque: ["Estoque", "Consulte as pecas disponiveis e solicite ao almoxarifado."],
    dashboard: ["Dashboard", "Resumo do estoque e das solicitacoes da MBF."],
    solicitacoes: ["Solicitacoes", "Acompanhe pedidos e comentarios de alteracao."],
    admin: ["Admin pecas", "Cadastre, edite e remova pecas do estoque da MBF."],
    usuarios: ["Usuarios", "Libere novos cadastros e acompanhe quem ja tem acesso."],
    relatorios: ["Relatorios", "Exporte informacoes e acompanhe indicadores do estoque."],
    historico: ["Historico", "Veja as movimentacoes registradas no banco de dados."]
  };
  $$(".view").forEach(view => view.classList.add("hidden"));
  $(`#${state.view}View`).classList.remove("hidden");
  $$(".nav[data-view]").forEach(btn => btn.classList.toggle("active", btn.dataset.view === state.view));
  $("#pageTitle").textContent = titles[state.view][0];
  $("#pageSubtitle").textContent = titles[state.view][1];
  $(".search").classList.toggle("hidden", state.view !== "estoque");
}

function fillForm(part = null) {
  $("#partId").value = part?.id || "";
  $("#partCode").value = part?.code || "";
  $("#partName").value = part?.name || "";
  $("#partCategory").value = part?.category || "Acao";
  $("#partQuantity").value = part?.quantity ?? "";
  $("#partMin").value = part?.min_quantity ?? "";
  $("#partUnit").value = part?.unit || "un";
  $("#partLocation").value = part?.location || "";
  $("#partSupplier").value = part?.supplier || "";
  $("#partUnitPrice").value = part?.unit_price ?? "";
  $("#partSector").value = part?.sector || "";
  $("#partEntryDate").value = part?.entry_date || "";
  $("#partDescription").value = part?.description || "";
  $("#formTitle").textContent = part ? "Editar peca" : "Cadastrar peca";
}

function fillUserForm(user = null) {
  $("#userId").value = user?.id || "";
  $("#userName").value = user?.name || "";
  $("#userUsername").value = user?.username || "";
  $("#userRole").value = user?.role || "user";
  $("#userActive").value = user ? String(user.active) : "1";
  $("#userSector").value = user?.sector || "";
  $("#userPassword").value = "";
  $("#userFormTitle").textContent = user ? "Editar usuario" : "Editar usuario";
}

window.editPart = id => {
  const part = state.parts.find(item => item.id === id);
  fillForm(part);
  state.view = "admin";
  updateView();
};

window.deletePart = async id => {
  if (!confirm("Excluir esta peca do estoque?")) return;
  await request(`/api/parts/${id}`, { method: "DELETE" });
  await loadAll();
};

window.openRequest = id => {
  const part = state.parts.find(item => item.id === id);
  $("#requestPartId").value = part.id;
  $("#requestPartName").textContent = `${part.code} - ${part.name}`;
  $("#requestQuantity").value = 1;
  $("#requestComment").value = "";
  $("#requestDialog").showModal();
};

window.reviewRequest = async (id, status) => {
  const note = prompt(status === "aprovado" ? "Observacao da aprovacao:" : "Motivo da rejeicao:") || "";
  await request(`/api/requests/${id}`, {
    method: "PUT",
    body: JSON.stringify({ status, admin_note: note })
  });
  await loadAll();
};

window.reviewSignup = async (id, status) => {
  const note = prompt(status === "aprovado" ? "Observacao da liberacao:" : "Motivo da rejeicao:") || "";
  await request(`/api/signup-requests/${id}`, {
    method: "PUT",
    body: JSON.stringify({ status, admin_note: note })
  });
  await loadAll();
};

window.editUser = id => {
  const user = state.users.find(item => item.id === id);
  fillUserForm(user);
};

window.deleteUser = async id => {
  if (!confirm("Excluir este usuario?")) return;
  await request(`/api/users/${id}`, { method: "DELETE" });
  fillUserForm();
  await loadAll();
};

$("#loginForm").addEventListener("submit", async event => {
  event.preventDefault();
  $("#loginError").textContent = "";
  $("#signupSuccess").textContent = "";
  try {
    const data = await request("/api/login", {
      method: "POST",
      body: JSON.stringify({
        username: $("#username").value,
        password: $("#password").value
      })
    });
    api.token = data.token;
    api.user = data.user;
    localStorage.setItem("mbfToken", api.token);
    localStorage.setItem("mbfUser", JSON.stringify(api.user));
    showApp();
    await loadAll();
  } catch (error) {
    $("#loginError").textContent = error.message;
  }
});

$("#openSignup").addEventListener("click", () => {
  $("#signupError").textContent = "";
  $("#signupForm").reset();
  $("#signupDialog").showModal();
});

$("#cancelSignup").addEventListener("click", () => $("#signupDialog").close());

$("#signupForm").addEventListener("submit", async event => {
  event.preventDefault();
  $("#signupError").textContent = "";
  try {
    await request("/api/signup", {
      method: "POST",
      body: JSON.stringify({
        name: $("#signupName").value,
        username: $("#signupUsername").value,
        password: $("#signupPassword").value,
        sector: $("#signupSector").value,
        reason: $("#signupReason").value
      })
    });
    $("#signupDialog").close();
    $("#signupSuccess").textContent = "Pedido enviado. Aguarde o admin liberar seu cadastro.";
  } catch (error) {
    $("#signupError").textContent = error.message;
  }
});


$("#logoutBtn").addEventListener("click", async () => {
  try {
    await fetch("/api/logout", {
      method: "POST",
      headers: {
        "X-Session-Token": api.token || ""
      }
    });
  } catch (error) {
    console.error("Erro ao encerrar sessão:", error);
  } finally {
    localStorage.removeItem("mbfToken");
    localStorage.removeItem("mbfUser");
    api.token = null;
    api.user = null;
    showLogin();
  }
});


$$(".nav[data-view]").forEach(btn => {
  btn.addEventListener("click", () => {
    state.view = btn.dataset.view;
    updateView();
  });
});

$("#searchInput").addEventListener("input", renderParts);
$("#categoryFilter").addEventListener("change", renderParts);

$("#partForm").addEventListener("submit", async event => {
  event.preventDefault();
  const id = $("#partId").value;
  const part = {
    code: $("#partCode").value,
    name: $("#partName").value,
    category: $("#partCategory").value,
    quantity: Number($("#partQuantity").value),
    min_quantity: Number($("#partMin").value),
    unit: $("#partUnit").value,
    location: $("#partLocation").value,
    supplier: $("#partSupplier").value,
    unit_price: Number($("#partUnitPrice").value || 0),
    sector: $("#partSector").value,
    entry_date: $("#partEntryDate").value,
    description: $("#partDescription").value
  };
  await request(id ? `/api/parts/${id}` : "/api/parts", {
    method: id ? "PUT" : "POST",
    body: JSON.stringify(part)
  });
  fillForm();
  await loadAll();
});

$("#clearForm").addEventListener("click", () => fillForm());

$("#userForm").addEventListener("submit", async event => {
  event.preventDefault();
  const id = $("#userId").value;
  if (!id) {
    alert("Selecione um usuario na lista para editar.");
    return;
  }
  await request(`/api/users/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      name: $("#userName").value,
      username: $("#userUsername").value,
      role: $("#userRole").value,
      active: Number($("#userActive").value),
      sector: $("#userSector").value,
      password: $("#userPassword").value
    })
  });
  fillUserForm();
  await loadAll();
});

$("#clearUserForm").addEventListener("click", () => fillUserForm());

$("#exportCritical").addEventListener("click", () => {
  const rows = [["Codigo", "Peca", "Quantidade", "Minimo", "Faltam", "Fornecedor"]];
  state.parts.filter(part => statusOf(part) !== "ok").forEach(part => {
    rows.push([part.code, part.name, `${part.quantity} ${part.unit}`, `${part.min_quantity} ${part.unit}`, Math.max(0, part.min_quantity - part.quantity), part.supplier || ""]);
  });
  csvDownload("relatorio-itens-criticos.csv", rows);
});

$("#exportAll").addEventListener("click", () => {
  const rows = [["Codigo", "Peca", "Categoria", "Fornecedor", "Preco", "Setor", "Local", "Quantidade", "Minimo", "Unidade", "Data entrada"]];
  state.parts.forEach(part => {
    rows.push([part.code, part.name, part.category, part.supplier || "", part.unit_price || 0, part.sector || "", part.location, part.quantity, part.min_quantity, part.unit, part.entry_date || ""]);
  });
  csvDownload("relatorio-estoque-mbf.csv", rows);
});

$("#requestForm").addEventListener("submit", async event => {
  event.preventDefault();
  await request("/api/requests", {
    method: "POST",
    body: JSON.stringify({
      part_id: Number($("#requestPartId").value),
      quantity: Number($("#requestQuantity").value),
      comment: $("#requestComment").value
    })
  });
  $("#requestDialog").close();
  await loadAll();
  state.view = "solicitacoes";
  updateView();
});

$("#cancelRequest").addEventListener("click", () => $("#requestDialog").close());

if (api.token && api.user) {
  showApp();
  loadAll().catch(() => showLogin());
} else {
  showLogin();
}

/* Integracao com API externa ViaCEP */
const supplierCepInput = document.getElementById("supplierCep");
const supplierAddressInput = document.getElementById("supplierAddress");

if (supplierCepInput && supplierAddressInput) {
    supplierCepInput.addEventListener("blur", async () => {
        const cep = supplierCepInput.value.replace(/\D/g, "");

        supplierAddressInput.value = "";

        if (cep.length !== 8) {
            if (cep.length > 0) {
                supplierAddressInput.value = "CEP invalido";
            }
            return;
        }

        supplierAddressInput.value = "Consultando CEP...";

        try {
            const response = await fetch(
                `https://viacep.com.br/ws/${cep}/json/`
            );

            if (!response.ok) {
                throw new Error("Falha na consulta");
            }

            const endereco = await response.json();

            if (endereco.erro) {
                supplierAddressInput.value = "CEP nao encontrado";
                return;
            }

            supplierAddressInput.value = [
                endereco.logradouro,
                endereco.bairro,
                endereco.localidade,
                endereco.uf
            ].filter(Boolean).join(", ");

        } catch (error) {
            supplierAddressInput.value = "Erro ao consultar CEP";
            console.error("Erro na consulta ViaCEP:", error);
        }
    });
}
