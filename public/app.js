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

function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[char]);
}

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
  const safeCSV = value => {
    let text = String(value ?? "");
    if (/^\s*[=+@\-\t\r]/.test(text)) text = "'" + text;
    return `"${text.replaceAll('"', '""')}"`;
  };
  const csv = rows.map(row => row.map(safeCSV).join(";")).join("\n");
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
  // Nunca reutilizar uma tela administrativa da sessão anterior.
  state.view = "dashboard";
  $("#loginScreen").classList.add("hidden");
  $("#app").classList.remove("hidden");
  $("#userLabel").textContent = `${api.user.name} - ${api.user.role === "admin" ? "Admin" : "Usuário"}`;
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
    const partId = Number(part.id);
    if (!Number.isSafeInteger(partId) || partId <= 0) return "";
    const adminActions = api.user.role === "admin"
      ? `<button class="secondary" onclick="editPart(${partId})">Editar</button><button class="secondary" onclick="deletePart(${partId})">Excluir</button>`
      : "";
    return `
      <tr>
        <td><strong>${escapeHTML(part.code)}</strong></td>
        <td>${escapeHTML(part.name)}<br><small>${escapeHTML(part.description || "")}</small></td>
        <td>${escapeHTML(part.category)}</td>
        <td>${escapeHTML(part.supplier || "-")}<br><small>${escapeHTML(money(part.unit_price))} / ${escapeHTML(part.unit)}</small></td>
        <td>${escapeHTML(part.location)}</td>
        <td><strong>${escapeHTML(part.quantity)}</strong> ${escapeHTML(part.unit)}<br><small>Min. ${escapeHTML(part.min_quantity)}</small></td>
        <td><span class="badge ${status}">${escapeHTML(statusLabel(status))}</span></td>
        <td><div class="row-actions"><button onclick="openRequest(${partId})">Solicitar</button>${adminActions}</div></td>
      </tr>
    `;
  }).join("") || `<tr><td colspan="7">Nenhuma peca encontrada.</td></tr>`;
}

function renderRequests() {
  $("#requestsList").innerHTML = state.requests.map(req => {
    const requestId = Number(req.id);
    const safeRequestId = Number.isSafeInteger(requestId) && requestId > 0 ? requestId : null;
    const adminActions = api.user.role === "admin" && req.status === "pendente" && safeRequestId !== null
      ? `<div class="row-actions"><button onclick="reviewRequest(${safeRequestId}, 'aprovado')">Aprovar</button><button class="secondary" onclick="reviewRequest(${safeRequestId}, 'rejeitado')">Rejeitar</button></div>`
      : "";
    return `
      <article class="request-card">
        <div class="row-actions">
         <strong>#${escapeHTML(req.id)} - ${escapeHTML(req.part_code)} - ${escapeHTML(req.part_name)}</strong>
          <span class="badge ${escapeHTML(req.status)}">${escapeHTML(req.status)}</span>
        </div>
        <p><strong>Quantidade:</strong> ${escapeHTML(req.quantity)} ${escapeHTML(req.unit)}</p>
        <p><strong>Solicitante:</strong> ${escapeHTML(req.user_name)}</p>
        <p><strong>Comentario:</strong> ${escapeHTML(req.comment || "Sem comentario")}</p>
        <p><strong>Resposta admin:</strong> ${escapeHTML(req.admin_note || "Sem resposta")}</p>
        ${adminActions}
      </article>
    `;
  }).join("") || `<div class="request-card"><p>Nenhuma solicitacao encontrada.</p></div>`;
}

function renderMovements() {
  $("#movementsList").innerHTML = state.movements.map(item => `
    <article class="request-card">
      <strong>${escapeHTML(String(item.type || "").toUpperCase())} - ${escapeHTML(item.part_name || "Sistema")}</strong>
      <p>Quantidade: ${escapeHTML(item.quantity)}</p>
      <p>Usuario: ${escapeHTML(item.user_name || "Sem usuario")} | ${escapeHTML(item.created_at)}</p>
      <p>${escapeHTML(item.note || "")}</p>
    </article>
  `).join("") || `<div class="request-card"><p>Nenhuma movimentacao encontrada.</p></div>`;
}

function renderUsers() {
  const list = $("#usersList");
  if (!list) return;
  list.innerHTML = state.users.map(user => {
  const userId = Number(user.id);
  if (!Number.isSafeInteger(userId) || userId <= 0) return "";

  return `
    <article class="request-card">
      <div class="row-actions">
        <strong>${escapeHTML(user.name)}</strong>
        <span class="badge ${user.active ? "ativo" : "bloqueado"}">${user.active ? "ativo" : "bloqueado"}</span>
      </div>
      <p>Login: ${escapeHTML(user.username)}</p>
      <p>Perfil: ${user.role === "admin" ? "Administrador" : "Usuário comum"}</p>
      <p>Setor: ${escapeHTML(user.sector || "Não informado")}</p>
      <div class="row-actions">
        <button class="secondary" onclick="editUser(${userId})">Editar</button>
        <button class="secondary" onclick="deleteUser(${userId})">Excluir</button>
      </div>
    </article>
    `;
  }).join("") || `<div class="request-card"><p>Nenhum usuario liberado.</p></div>`;
}

function renderSignupRequests() {
  const list = $("#signupRequestsList");
  if (!list) return;
  list.innerHTML = state.signupRequests.map(req => {
    const reqId = Number(req.id);
    if (!Number.isSafeInteger(reqId) || reqId <= 0) return "";

    const actions = req.status === "pendente"
    ? `<div class="row-actions">
      <button onclick="reviewSignup(${reqId}, 'aprovado')">Liberar</button>
      <button class="secondary" onclick="reviewSignup(${reqId}, 'rejeitado')">Rejeitar</button>
    </div>`
    : "";
    return `
      <article class="request-card">
        <div class="row-actions">
          <strong>${escapeHTML(req.name)}</strong>
          <span class="badge ${escapeHTML(req.status)}">${escapeHTML(req.status)}</span>
        </div>
        <p><strong>Login solicitado:</strong> ${escapeHTML(req.username)}</p>
        <p><strong>Setor:</strong> ${escapeHTML(req.sector || "Não informado")}</p>
        <p><strong>Motivo:</strong> ${escapeHTML(req.reason || "Sem motivo informado")}</p>
        <p><strong>Resposta admin:</strong> ${escapeHTML(req.admin_note || "Sem resposta")}</p>
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
      <header><strong>${escapeHTML(category)}</strong><span>${total}</span></header>
      <div class="bar"><span style="--w:${Math.round((total / maxCategory) * 100)}%"></span></div>
    </div>
  `).join("") || `<p>Nenhuma peca cadastrada.</p>`;

  const critical = state.parts.filter(part => statusOf(part) !== "ok");
  $("#criticalList").innerHTML = critical.map(part => `
    <article class="request-card">
      <div class="row-actions">
        <strong>${escapeHTML(part.code)} - ${escapeHTML(part.name)}</strong>
        <span class="badge ${statusOf(part)}">${statusLabel(statusOf(part))}</span>
      </div>
      <p>Atual: ${escapeHTML(part.quantity)} ${escapeHTML(part.unit)} | Minimo: ${escapeHTML(part.min_quantity)} ${escapeHTML(part.unit)}</p>
      <p>Fornecedor: ${escapeHTML(part.supplier || "Não informado")}</p>
    </article>
  `).join("") || `<div class="request-card"><p>Nenhum item critico no momento.</p></div>`;
}

function renderReports() {
  const critical = state.parts.filter(part => statusOf(part) !== "ok");
  $("#criticalReport").innerHTML = critical.map(part => `
    <tr>
      <td><strong>${escapeHTML(part.code)}</strong></td>
      <td>${escapeHTML(part.name)}</td>
      <td>${escapeHTML(part.quantity)} ${escapeHTML(part.unit)}</td>
      <td>${escapeHTML(part.min_quantity)} ${escapeHTML(part.unit)}</td>
      <td>${escapeHTML(Math.max(0, part.min_quantity - part.quantity))} ${escapeHTML(part.unit)}</td>
      <td>${escapeHTML(part.supplier || "-")}</td>
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
  // Proteção visual adicional: o servidor continua responsável pela autorização.
  if (api.user?.role !== "admin" && ["admin", "usuarios"].includes(state.view)) {
    state.view = "dashboard";
  }
  const titles = {
    estoque: ["Estoque", "Consulte as peças disponíveis e solicite ao almoxarifado."],
    dashboard: ["Dashboard", "Resumo do estoque e das solicitações da MBF."],
    solicitacoes: ["Solicitações", "Acompanhe pedidos e comentários de alteração."],
    admin: ["Admin peças", "Cadastre, edite e remova peças do estoque da MBF."],
    usuarios: ["Usuários", "Libere novos cadastros e acompanhe quem ja tem acesso."],
    relatorios: ["Relatórios", "Exporte informações e acompanhe indicadores do estoque."],
    historico: ["Histórico", "Veja as movimentações registradas no banco de dados."]
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
  $("#partCategory").value = part?.category || "Aço";
  $("#partQuantity").value = part?.quantity ?? "";
  $("#partMin").value = part?.min_quantity ?? "";
  $("#partUnit").value = part?.unit || "un";
  $("#partLocation").value = part?.location || "";
  $("#partSupplier").value = part?.supplier || "";
  $("#partUnitPrice").value = part?.unit_price ?? "";
  $("#partSector").value = part?.sector || "";
  $("#partEntryDate").value = part?.entry_date || "";
  $("#partDescription").value = part?.description || "";
  // O CEP não é persistido no cadastro atual; exigir nova informação ao salvar.
  $("#supplierCep").value = "";
  $("#supplierAddress").value = "";
  validatedSupplierCep = "";
  $("#formTitle").textContent = part ? "Editar peça" : "Cadastrar peça";
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
  if (!confirm("Excluir esta peça do estoque?")) return;
  try {
    await request(`/api/parts/${id}`, { method: "DELETE" });
    await loadAll();
  } catch (error) {
    alert(error.message + "\n\nPeças com solicitações ou movimentações não podem ser excluídas, pois seus registros precisam ser preservados para auditoria.");
  }
};

window.openRequest = id => {
  const part = state.parts.find(item => item.id === id);
  $("#requestPartId").value = part.id;
  $("#requestPartName").textContent = `${part.code} - ${part.name}`;
  $("#requestQuantity").value = 1;
  $("#requestComment").value = "";
  $("#requestDialog").showModal();
};

async function reviewPendingItem(endpoint, id, status, kind) {
  if (api.user?.role !== "admin") {
    alert("Apenas administradores podem analisar solicitações.");
    return;
  }
  const safeId = Number(id);
  if (!Number.isSafeInteger(safeId) || safeId <= 0) {
    alert("Identificador da solicitação inválido.");
    return;
  }
  const approving = status === "aprovado";
  const note = prompt(
    approving ? (kind === "cadastro" ? "Observação da liberação:" : "Observação da aprovação:")
              : "Motivo da rejeição:"
  );
  if (note === null) return;
  try {
    await request(`${endpoint}/${safeId}`, {
      method: "PUT",
      body: JSON.stringify({ status, admin_note: note.trim() })
    });
    await loadAll();
    alert(approving ? (kind === "cadastro" ? "Cadastro liberado com sucesso." : "Solicitação aprovada. Estoque atualizado.")
                    : "Solicitação rejeitada.");
  } catch (error) {
    console.error("Falha ao analisar solicitação:", error);
    alert("Não foi possível " + (approving ? "aprovar" : "rejeitar") + ": " + error.message);
  }
}

window.reviewRequest = (id, status) => reviewPendingItem("/api/requests", id, status, "peça");
window.reviewSignup = (id, status) => reviewPendingItem("/api/signup-requests", id, status, "cadastro");

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
    if (api.user?.role !== "admin" && ["admin", "usuarios"].includes(btn.dataset.view)) return;
    state.view = btn.dataset.view;
    updateView();
  });
});

$("#searchInput").addEventListener("input", renderParts);
$("#categoryFilter").addEventListener("change", renderParts);

$("#partForm").addEventListener("submit", async event => {
  event.preventDefault();
  const cep = $("#supplierCep").value.replace(/\D/g, "");
  if (cep.length !== 8) {
    alert("Informe o CEP do fornecedor com 8 dígitos antes de salvar.");
    $("#supplierCep").focus();
    return;
  }
  if (validatedSupplierCep !== cep || !$("#supplierAddress").value.trim() || /^(CEP invalido|CEP nao encontrado|Erro ao consultar CEP|Consultando CEP)/i.test($("#supplierAddress").value.trim())) {
    alert("Aguarde a consulta e confirme um CEP válido antes de salvar.");
    $("#supplierCep").focus();
    return;
  }
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
  const rows = [["Codigo", "Peça", "Quantidade", "Mínimo", "Faltam", "Fornecedor"]];
  state.parts.filter(part => statusOf(part) !== "ok").forEach(part => {
    rows.push([part.code, part.name, `${part.quantity} ${part.unit}`, `${part.min_quantity} ${part.unit}`, Math.max(0, part.min_quantity - part.quantity), part.supplier || ""]);
  });
  csvDownload("relatorio-itens-criticos.csv", rows);
});

$("#exportAll").addEventListener("click", () => {
  const rows = [["Codigo", "Peça", "Categoria", "Fornecedor", "Preço", "Setor", "Local", "Quantidade", "Mínimo", "Unidade", "Data entrada"]];
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
let validatedSupplierCep = "";

if (supplierCepInput && supplierAddressInput) {
    supplierCepInput.addEventListener("input", () => {
        validatedSupplierCep = "";
        supplierAddressInput.value = "";
    });
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
            if (supplierCepInput.value.replace(/\D/g, "") !== cep) return;

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
            if (supplierAddressInput.value.trim()) validatedSupplierCep = cep;

        } catch (error) {
            if (supplierCepInput.value.replace(/\D/g, "") !== cep) return;
            supplierAddressInput.value = "Erro ao consultar CEP";
            console.error("Erro na consulta ViaCEP:", error);
        }
    });
}
