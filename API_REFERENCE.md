# 🔗 Referência Rápida de APIs

## Base URL
```
http://127.0.0.1:5000/api
```

## 🔐 Headers Obrigatórios
```
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json
```

---

## 📱 CELULARES

### Lista
```http
GET /celulares
GET /celulares?filial=Matriz
```

**Resposta 200:**
```json
[
  {
    "_id": "67a1b2c3d4e5f6g7h8i9j0k1",
    "patrimonio": "CEL-001",
    "filial": "Matriz",
    "modelo": "iPhone 13",
    "imei": "123456789012345",
    "numero": "(11) 98765-4321",
    "responsavel": "João Silva",
    "status": "Em Uso",
    "obs": "",
    "created_at": "2026-01-23T10:30:00",
    "updated_at": "2026-01-23T10:30:00"
  }
]
```

### Detalhe
```http
GET /celulares/{id}
```

**Resposta 200:** (mesmo formato acima)

### Criar
```http
POST /celulares
Content-Type: application/json

{
  "patrimonio": "CEL-002",
  "filial": "Matriz",
  "modelo": "Samsung Galaxy S23",
  "imei": "987654321098765",
  "numero": "(11) 97777-8888",
  "responsavel": "Maria Santos",
  "status": "Em Uso",
  "obs": "Equipamento novo"
}
```

**Resposta 201:**
```json
{
  "msg": "Celular criado com sucesso!",
  "id": "67a1b2c3d4e5f6g7h8i9j0k1"
}
```

**Erros:**
- `400` - Patrimônio e Filial obrigatórios
- `409` - Patrimônio já cadastrado

### Atualizar
```http
PUT /celulares/{id}
Content-Type: application/json

{
  "responsavel": "João Silva Updated",
  "status": "Manutenção"
}
```

**Resposta 200:**
```json
{
  "msg": "Celular atualizado com sucesso!"
}
```

### Inativar
```http
DELETE /celulares/{id}
```

**Resposta 200:**
```json
{
  "msg": "Celular inativado com sucesso!"
}
```

---

## 💻 SOFTWARES/LICENÇAS

### Lista
```http
GET /softwares
GET /softwares?asset_id={asset_id}
GET /softwares?filial=Matriz
```

**Resposta 200:**
```json
[
  {
    "_id": "67a1b2c3d4e5f6g7h8i9j0k2",
    "nome": "Microsoft Office 365",
    "versao": "2024",
    "asset_id": "67a1b2c3d4e5f6g7h8i9j0k3",
    "tipo_licenca": "Corporativa",
    "chave_licenca": "XXXX-XXXX-XXXX-XXXX",
    "dt_instalacao": "2024-01-15T00:00:00",
    "dt_vencimento": "2025-01-15T00:00:00",
    "renovacao_automatica": true,
    "custo_anual": 1200.00,
    "status": "Ativo",
    "obs": "Licença principal",
    "created_at": "2026-01-23T10:30:00",
    "updated_at": "2026-01-23T10:30:00"
  }
]
```

### Detalhe
```http
GET /softwares/{id}
```

### Criar
```http
POST /softwares
Content-Type: application/json

{
  "nome": "Adobe Creative Cloud",
  "versao": "2024",
  "asset_id": "67a1b2c3d4e5f6g7h8i9j0k3",
  "tipo_licenca": "Corporativa",
  "chave_licenca": "ABCD-EFGH-IJKL-MNOP",
  "dt_instalacao": "2024-01-01",
  "dt_vencimento": "2025-01-01",
  "renovacao_automatica": false,
  "custo_anual": 5000.00,
  "obs": "Design team"
}
```

**Resposta 201:**
```json
{
  "msg": "Software/Licença criado com sucesso!",
  "id": "67a1b2c3d4e5f6g7h8i9j0k2"
}
```

### Atualizar
```http
PUT /softwares/{id}
Content-Type: application/json

{
  "dt_vencimento": "2026-01-01",
  "renovacao_automatica": true
}
```

### Inativar
```http
DELETE /softwares/{id}
```

### Verificar Vencimento
```http
GET /softwares/verificar-vencimento?dias=30
```

**Resposta 200:** (Lista softwares vencendo nos próximos 30 dias)

---

## 📧 EMAILS (ZIMBRA/GOOGLE)

### Lista
```http
GET /emails
GET /emails?asset_id={asset_id}
GET /emails?tipo=google
GET /emails?tipo=zimbra
```

**Resposta 200:**
```json
[
  {
    "_id": "67a1b2c3d4e5f6g7h8i9j0k4",
    "endereco": "joao.silva@empresa.com",
    "tipo": "google",
    "asset_id": "67a1b2c3d4e5f6g7h8i9j0k3",
    "usuario": "joao.silva@empresa.com",
    "senha": "Senha@Segura123",
    "recuperacao": "joao.pessoal@gmail.com",
    "data_criacao": "2024-01-15T00:00:00",
    "status": "Ativo",
    "obs": "Email principal",
    "created_at": "2026-01-23T10:30:00",
    "updated_at": "2026-01-23T10:30:00"
  }
]
```

### Detalhe
```http
GET /emails/{id}
```

### Criar
```http
POST /emails
Content-Type: application/json

{
  "endereco": "maria.santos@empresa.com",
  "tipo": "google",
  "asset_id": "67a1b2c3d4e5f6g7h8i9j0k3",
  "usuario": "maria.santos@empresa.com",
  "senha": "SenhaSegura@2024",
  "recuperacao": "maria.pessoal@gmail.com",
  "data_criacao": "2024-01-01",
  "obs": "Email corporativo"
}
```

**Resposta 201:**
```json
{
  "msg": "Email criado com sucesso!",
  "id": "67a1b2c3d4e5f6g7h8i9j0k4"
}
```

### Atualizar
```http
PUT /emails/{id}
Content-Type: application/json

{
  "senha": "NovaSenha@2024",
  "recuperacao": "novo.email@gmail.com"
}
```

### Inativar
```http
DELETE /emails/{id}
```

---

## 🔍 AUDITORIA/LOGS (Existente)

### Todos os Logs
```http
GET /auth/logs
```

**Resposta 200:**
```json
[
  {
    "_id": "67a1b2c3d4e5f6g7h8i9j0k5",
    "ativo_id": "67a1b2c3d4e5f6g7h8i9j0k1",
    "usuario": "admin",
    "operacao": "CREATE",
    "dados_antigos": null,
    "dados_novos": { "patrimonio": "CEL-001", ... },
    "timestamp": "2026-01-23T10:30:00",
    "tipo": "celular"
  }
]
```

### Logs de um Ativo Específico
```http
GET /auth/logs/{ativo_id}
```

---

## ✅ Códigos de Resposta HTTP

| Código | Significado | Exemplo |
|--------|------------|---------|
| 200 | OK | Sucesso geral |
| 201 | Created | Recurso criado |
| 400 | Bad Request | Dados inválidos |
| 401 | Unauthorized | Token ausente/inválido |
| 404 | Not Found | Recurso não existe |
| 409 | Conflict | Duplicação de dados únicos |
| 422 | Unprocessable | Token expirado |
| 500 | Server Error | Erro interno |

---

## 🛠️ Exemplos com cURL

### Login
```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

### Criar Celular
```bash
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

curl -X POST http://127.0.0.1:5000/api/celulares \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patrimonio": "CEL-001",
    "filial": "Matriz",
    "modelo": "iPhone 13",
    "numero": "(11) 98765-4321",
    "responsavel": "João",
    "status": "Em Uso"
  }'
```

### Listar Softwares
```bash
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

curl -X GET "http://127.0.0.1:5000/api/softwares?asset_id=ASSET_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### Criar Email
```bash
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

curl -X POST http://127.0.0.1:5000/api/emails \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "endereco": "user@empresa.com",
    "tipo": "google",
    "asset_id": "ASSET_ID",
    "usuario": "user@empresa.com",
    "senha": "SenhaSegura123",
    "recuperacao": "user@gmail.com"
  }'
```

### Verificar Softwares Vencendo
```bash
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

curl -X GET "http://127.0.0.1:5000/api/softwares/verificar-vencimento?dias=30" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📝 Validações Importantes

| Campo | Tipo | Obrigatório | Único | Exemplo |
|-------|------|-------------|-------|---------|
| patrimonio (Celular) | String | ✓ | ✓ | CEL-001 |
| filial | String | ✓ | ✗ | Matriz |
| nome (Software) | String | ✓ | ✗ | Office 365 |
| asset_id | ObjectId | ✓ | ✗ | 67a1b2c... |
| tipo (Email) | String | ✓ | ✗ | google/zimbra |
| endereco (Email) | String | ✓ | ✗ | user@empresa.com |
| dt_vencimento | Date | ✗ | ✗ | 2025-01-15 |

---

## 🔄 Fluxo Típico

```
1. Login → Obter JWT Token
   POST /auth/login

2. Criar Recurso → Usar Token
   POST /celulares, /softwares, /emails

3. Listar Recursos
   GET /celulares, /softwares, /emails

4. Editar Recurso
   PUT /celulares/{id}, /softwares/{id}, /emails/{id}

5. Inativar Recurso
   DELETE /celulares/{id}, /softwares/{id}, /emails/{id}

6. Verificar Auditoria
   GET /auth/logs
```

---

## 🚨 Tratamento de Erros

### Exemplo de Erro 400
```json
{
  "erro": "Patrimônio e Filial são obrigatórios"
}
```

### Exemplo de Erro 409
```json
{
  "erro": "Patrimônio já cadastrado"
}
```

### Exemplo de Erro 401
```json
{
  "erro": "Token ausente"
}
```

---

**Última atualização:** 23/01/2026
**Versão da API:** 1.0.0
