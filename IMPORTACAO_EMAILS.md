# Importação e Vinculação de Emails

## Resumo da Implementação

Foi criado um sistema completo para importar emails do arquivo `emails.csv` e vinculá-los aos assets (computadores) do sistema.

### 📋 Arquivos Criados

#### 1. **importar_emails.py**
Script para importar emails do arquivo CSV para o banco de dados.

**Funcionalidades:**
- Lê o arquivo `emails.csv` no formato: `Tipo;Conta;Senha`
- Normaliza os tipos de email (Google, Microsoft, Zimbra, Matriz, Canon)
- Criptografa as senhas com bcrypt
- Atualiza emails que já existem
- Importa novos emails com uma única execução

**Como usar:**
```bash
python importar_emails.py
```

**Resultado da importação:**
- ✅ **322 emails importados**
- ✏️ **255 emails atualizados**
- ❌ **0 erros**

**Distribuição por tipo:**
- Google: 181 emails
- Zimbra: 321 emails  
- Microsoft: 73 emails
- Matriz: 1 email
- Canon: 1 email

#### 2. **vincular_emails.py**
Script para vincular emails aos assets/computadores automaticamente.

**Estratégias de vinculação:**
1. Procura por correspondência entre o nome de usuário do email e o responsável do asset
2. Procura por padrões numéricos que correspondam ao patrimônio do asset
3. Permite vinculação manual via API

**Como usar:**
```bash
python vincular_emails.py
```

**Resultado da vinculação:**
- ✅ **157 emails vinculados automaticamente**
- ⚠️ **165 emails ainda sem vinculação** (podem ser vinculados manualmente)

### 📊 Estrutura do Banco de Dados

Os emails são armazenados na tabela `emails` com os seguintes campos:

```sql
CREATE TABLE emails (
    id INTEGER PRIMARY KEY,
    endereco VARCHAR(120) UNIQUE NOT NULL,  -- exemplo: credito@refricril.com.br
    tipo VARCHAR(50) NOT NULL,              -- google, microsoft, zimbra, matriz, canon
    asset_id INTEGER,                       -- FK para assets (computador responsável)
    usuario VARCHAR(120),                   -- nome de usuário (parte antes do @)
    senha VARCHAR(255),                     -- senha criptografada com bcrypt
    recuperacao VARCHAR(120),               -- email de recuperação (opcional)
    observacoes TEXT,                       -- anotações
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP,
    atualizado_em TIMESTAMP
);
```

### 🔗 Vinculação Manual via API

Para vincular um email manualmente a um asset, use a API:

```bash
PUT /api/emails/<email_id>
Content-Type: application/json

{
    "asset_id": <asset_id>
}
```

Exemplo:
```bash
curl -X PUT http://localhost:5000/api/emails/1 \
  -H "Content-Type: application/json" \
  -d '{"asset_id": 5}'
```

### 📝 Próximos Passos

1. **Criar endpoint na API para vincular emails:**
   - `PUT /api/emails/<id>` - Atualizar email
   - `GET /api/emails` - Listar todos os emails
   - `GET /api/emails/<id>` - Obter detalhes do email

2. **Interface de vinculação no frontend:**
   - Tabela listando emails sem vinculação
   - Dropdown para selecionar asset
   - Botão para confirmar vinculação

3. **Validações:**
   - Verificar unicidade de emails
   - Validar formato de email
   - Criptografar senhas antes de armazenar

### 🔐 Segurança

- ✅ Senhas são criptografadas com bcrypt
- ✅ Arquivo CSV não é armazenado permanentemente
- ⚠️ Considere adicionar permissões de acesso às senhas (apenas admin)
- ⚠️ Implementar auditoria de acessos às senhas

### 📌 Notas Importantes

- O arquivo `emails.csv` deve estar na raiz do projeto
- O delimitador deve ser ponto-e-vírgula (;)
- A primeira linha deve conter: `Tipo;Conta;Senha`
- Senhas vazias serão aceitas (NULL no banco)
- Emails duplicados serão atualizados com novas informações

