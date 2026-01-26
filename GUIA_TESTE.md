# 🧪 Guia de Teste - Sistema de Inventário TI

## Pré-requisitos
- Node.js e npm instalados
- Python 3.10+
- MongoDB em execução localmente
- Terminal com acesso aos diretórios do projeto

---

## 1️⃣ Iniciar o Backend (Python/Flask)

### Terminal 1: Backend
```powershell
# Navegar para a pasta do projeto
cd C:\Users\User\Documents\Programa\inventario_ti

# Ativar o ambiente virtual (se estiver usando .venv)
.\.venv\Scripts\Activate.ps1

# Instalar dependências (se necessário)
pip install -r requirements.txt

# Iniciar o servidor Flask
python run.py
```

**Esperado:** 
```
Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

---

## 2️⃣ Iniciar o Frontend (React/Vite)

### Terminal 2: Frontend
```powershell
# Navegar para a pasta frontend
cd C:\Users\User\Documents\Programa\inventario_ti\frontend-ti

# Instalar dependências (primeira vez)
npm install

# Iniciar o servidor de desenvolvimento
npm run dev
```

**Esperado:**
```
VITE v... ready in XXX ms

➜ Local:   http://localhost:5173/
```

---

## 3️⃣ Acessar a Aplicação

1. Abra o navegador em: **http://localhost:5173**
2. Faça login com credenciais padrão:
   - **Usuário:** admin
   - **Senha:** admin123

---

## 4️⃣ Testar Novos Módulos

### A. Testar Módulo de Celulares

#### Criar Celular
1. No menu lateral, clique em **"Celulares"**
2. Clique em **"Novo Celular"**
3. Preencha os dados:
   - **Patrimônio:** CEL-001
   - **Filial:** (selecione uma)
   - **Modelo:** iPhone 13 Pro
   - **IMEI:** 123456789012345
   - **Número:** (11) 98765-4321
   - **Responsável:** João Silva
4. Clique em **"Salvar"**

#### Verificar Erro de Duplicação
1. Tente criar outro celular com PAT "CEL-001"
2. Deve retornar erro: "Patrimônio já cadastrado"

---

### B. Testar Módulo de Softwares

#### Criar Software
1. No menu lateral, clique em **"Softwares"**
2. Clique em **"Novo Software"**
3. Preencha os dados:
   - **Nome do Software:** Microsoft Office 365
   - **Versão:** 2024
   - **Asset:** (selecione um computador)
   - **Tipo de Licença:** Corporativa
   - **Data Instalação:** 2024-01-15
   - **Data Vencimento:** 2025-01-15
   - **Custo Anual:** 1200.00
4. Marque "Renovação Automática"
5. Clique em **"Salvar"**

#### Verificar Cores de Vencimento
1. Crie softwares com datas próximas a hoje
2. Verifique as cores na tabela:
   - 🟢 Verde = Vence em mais de 30 dias
   - 🟠 Laranja = Vence em menos de 30 dias
   - 🔴 Vermelho = Já venceu

---

### C. Testar Módulo de Emails

#### Criar Email Google
1. No menu lateral, clique em **"Emails"**
2. Clique em **"Novo Email"**
3. Preencha os dados:
   - **Endereço:** joao.silva@empresa.com
   - **Tipo:** Google Workspace
   - **Asset:** (selecione um computador)
   - **Usuário:** joao.silva@empresa.com
   - **Senha:** (digite uma senha - será protegida)
   - **Email de Recuperação:** joao.pessoal@gmail.com
4. Clique em **"Salvar"**

#### Testar Proteção de Senha
1. Na tabela, localize o email criado
2. Clique em editar
3. Veja que a senha aparece como `●●●●●●●●`
4. Clique no ícone do olho para ver a senha temporariamente

#### Criar Email Zimbra
1. Repita o processo anterior, mas selecione **"Zimbra"** como tipo
2. Verifique se o badge muda de cor (vermelho para Zimbra, azul para Google)

---

## 5️⃣ Testar Integração com Inventário Existente

### Vincular Software a Computador
1. Vá para **"Inventário"**
2. Clique em um computador para editar
3. Vá para a aba **"Softwares"**
4. Clique em **"Add Software"**
5. Preencha os dados
6. Clique em **"Salvar"**

---

## 6️⃣ Testar Auditoria

1. Vá para **"Auditoria"** (requer permissão de admin)
2. Verifique se todas as operações foram registradas:
   - Criação de celulares
   - Alteração de softwares
   - Criação de emails
3. Cada log deve conter:
   - Tipo de operação (Create/Update/Delete)
   - Usuário que fez a operação
   - Data/Hora
   - Dados antigos vs novos

---

## 7️⃣ Testar API via Curl/Postman

### Autenticar
```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Resposta esperada:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "usuario": {
    "id": "...",
    "username": "admin",
    "nome": "Administrador",
    "filial": "Matriz",
    "permissoes": ["admin"]
  }
}
```

### Listar Celulares
```bash
curl -X GET http://127.0.0.1:5000/api/celulares \
  -H "Authorization: Bearer {TOKEN}"
```

### Criar Celular
```bash
curl -X POST http://127.0.0.1:5000/api/celulares \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "patrimonio": "CEL-002",
    "filial": "Matriz",
    "modelo": "Samsung Galaxy S23",
    "imei": "987654321098765",
    "numero": "(11) 97777-8888",
    "responsavel": "Maria Santos",
    "status": "Em Uso"
  }'
```

### Criar Software
```bash
curl -X POST http://127.0.0.1:5000/api/softwares \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "nome": "Adobe Creative Cloud",
    "versao": "2024",
    "asset_id": "{ASSET_ID}",
    "tipo_licenca": "Corporativa",
    "chave_licenca": "XXXX-XXXX-XXXX-XXXX",
    "dt_instalacao": "2024-01-01",
    "dt_vencimento": "2025-01-01",
    "custo_anual": 5000
  }'
```

### Criar Email
```bash
curl -X POST http://127.0.0.1:5000/api/emails \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "endereco": "maria.santos@empresa.com",
    "tipo": "google",
    "asset_id": "{ASSET_ID}",
    "usuario": "maria.santos",
    "senha": "Senha@Segura123",
    "recuperacao": "maria.pessoal@gmail.com"
  }'
```

---

## 8️⃣ Verificar Logs do Navegador

### Abrir DevTools (F12)
1. Pressione **F12** no navegador
2. Vá para a aba **"Console"**
3. Procure por mensagens de erro
4. Vá para **"Network"** para ver requisições HTTP

### Logs esperados de sucesso:
```
✓ Login bem-sucedido! Token: eyJ0eXAiOi...
✓ Celular criado com sucesso!
✓ Software atualizado com sucesso!
✓ Email inativado com sucesso!
```

---

## 🔍 Troubleshooting

### Erro: "Token inválido" ou "401"
- Verifique se o token está sendo enviado corretamente
- Tente fazer login novamente
- Verifique se o token não expirou

### Erro: "Patrimônio já cadastrado"
- Isso é esperado se tentar criar dois celulares/softwares com mesmo PAT
- Use um número diferente

### Erro: "Asset não encontrado"
- Verifique se o asset_id é válido
- Crie um computador/notebook primeiro em "Inventário"

### Frontend não carrega
- Verifique se o backend está rodando em http://127.0.0.1:5000
- Verifique a aba "Network" no DevTools

### MongoDB não conecta
- Verifique se MongoDB está rodando
- Padrão: mongodb://localhost:27017

---

## ✅ Checklist de Testes

- [ ] Backend inicia sem erros
- [ ] Frontend inicia e conecta ao backend
- [ ] Login funciona corretamente
- [ ] Criar celular com sucesso
- [ ] Erro ao duplicar PAT de celular
- [ ] Editar celular funciona
- [ ] Inativar celular funciona
- [ ] Criar software com vencimento próximo (laranja)
- [ ] Criar software vencido (vermelho)
- [ ] Filtar softwares por asset funciona
- [ ] Criar email Google funciona
- [ ] Criar email Zimbra funciona
- [ ] Mostrar/ocultar senha funciona
- [ ] Filtrar emails por tipo funciona
- [ ] Histórico de auditoria registra alterações
- [ ] API via Postman/Curl funciona
- [ ] Logout funciona

---

**Última atualização:** 23/01/2026
**Desenvolvido por:** GitHub Copilot
