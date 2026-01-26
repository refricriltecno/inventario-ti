# Sistema de Inventário de TI - Implementações Realizadas

## 📋 Resumo das Mudanças

### 1. **Backend - Novas Rotas**

#### **Celulares** (`app/routes/celulares.py`)
- `GET /api/celulares` - Listar celulares (com filtro opcional por filial)
- `GET /api/celulares/<id>` - Obter detalhes de um celular
- `POST /api/celulares` - Criar novo celular
- `PUT /api/celulares/<id>` - Atualizar celular
- `DELETE /api/celulares/<id>` - Inativar celular (soft delete)

**Campos de Celular:**
- `patrimonio` (obrigatório) - Número PAT do celular
- `filial` (obrigatório) - Filial onde se encontra
- `modelo` - Modelo do celular
- `imei` - Número IMEI
- `numero` - Número de telefone
- `responsavel` - Pessoa responsável
- `status` - Em Uso, Reserva, Manutenção, Inativo
- `obs` - Observações

#### **Softwares/Licenças** (`app/routes/softwares.py`)
- `GET /api/softwares` - Listar softwares (com filtros por asset_id ou filial)
- `GET /api/softwares/<id>` - Obter detalhes de um software
- `POST /api/softwares` - Criar novo software/licença
- `PUT /api/softwares/<id>` - Atualizar software
- `DELETE /api/softwares/<id>` - Inativar software
- `GET /api/softwares/verificar-vencimento` - Listar softwares prestes a vencer

**Campos de Software:**
- `nome` (obrigatório) - Nome do software
- `versao` - Versão instalada
- `asset_id` (obrigatório) - ID do computador/notebook
- `tipo_licenca` - Individual, Volume, Corporativa, Trial, Open Source
- `chave_licenca` - Chave de licença (protegida)
- `dt_instalacao` - Data de instalação
- `dt_vencimento` - Data de vencimento
- `renovacao_automatica` - Checkbox para renovação automática
- `custo_anual` - Valor da licença/ano
- `status` - Ativo, Inativo
- `obs` - Observações

#### **Emails (Zimbra/Google)** (`app/routes/emails.py`)
- `GET /api/emails` - Listar emails (com filtros por asset_id, filial ou tipo)
- `GET /api/emails/<id>` - Obter detalhes de um email
- `POST /api/emails` - Criar novo email corporativo
- `PUT /api/emails/<id>` - Atualizar email
- `DELETE /api/emails/<id>` - Inativar email

**Campos de Email:**
- `endereco` (obrigatório) - Endereço de email
- `tipo` (obrigatório) - 'google' ou 'zimbra'
- `asset_id` (obrigatório) - ID do computador/notebook
- `usuario` - Usuário de login
- `senha` - Senha (protegida)
- `recuperacao` - Email de recuperação
- `data_criacao` - Data de criação da conta
- `status` - Ativo, Inativo
- `obs` - Observações

### 2. **Frontend - Novos Componentes**

#### **Celulares.jsx**
- Tabela com listagem de celulares
- Filtro por filial
- Modal para criar/editar celulares
- Indicador visual de status (badge colorida)
- Soft delete com confirmação

#### **Softwares.jsx**
- Tabela com listagem de softwares
- Filtro por asset
- Modal para criar/editar softwares
- Verificação de vencimento (cores: vermelho=vencido, laranja=próximo a vencer)
- Campos de controle de licenças (chave, data de instalação/vencimento, renovação automática)

#### **Emails.jsx**
- Tabela com listagem de emails corporativos
- Filtro por tipo (Google Workspace / Zimbra)
- Modal para criar/editar emails
- Campo de senha protegido com botão mostrar/ocultar
- Suporte a email de recuperação

### 3. **Atualizações no App.jsx**
- Importação dos 3 novos componentes
- Adição de 3 novos botões no menu lateral (Celulares, Softwares, Emails)
- Integração das abas de navegação
- Sistema de roteamento entre as páginas

### 4. **Atualização no __init__.py**
- Registro dos blueprints das novas rotas

---

## 🚀 Como Usar

### **Acessar os Novos Módulos:**
1. Faça login no sistema
2. No menu lateral esquerdo, clique em:
   - **Celulares** - Para gerenciar dispositivos móveis
   - **Softwares** - Para gerenciar licenças de software
   - **Emails** - Para gerenciar contas corporativas (Google/Zimbra)

### **Criar um Novo Registro:**
1. Clique no botão **"Novo [Tipo]"** no canto superior direito
2. Preencha os campos obrigatórios (marcados com *)
3. Clique em **"Salvar"**

### **Editar um Registro:**
1. Na tabela, clique no ícone **lápis** (edit) na linha do registro
2. Modifique os dados
3. Clique em **"Salvar"**

### **Inativar um Registro:**
1. Na tabela, clique no ícone **lixeira** (delete)
2. Confirme a ação na janela de diálogo
3. O registro será marcado como "Inativo" mas não será deletado

### **Filtrar Registros:**
- **Celulares:** Filtre por filial na combobox superior
- **Softwares:** Filtre por asset (computador/notebook)
- **Emails:** Filtre por tipo (Google Workspace ou Zimbra)

---

## 🔐 Segurança e Auditoria

- **Senhas e Chaves Protegidas:** Campos sensíveis (BIOS, Windows, VPN, Licenças) aparecem como `●●●●●●` por padrão
- **Mostrar/Ocultar:** Clique no ícone do olho para visualizar senhas temporariamente
- **Auditoria Automática:** Toda alteração é registrada automaticamente no sistema de logs
- **Soft Delete:** Nenhum registro é permanentemente deletado; apenas marcado como "Inativo"

---

## 📊 Modelo de Dados (MongoDB)

### **Collection: celulares**
```javascript
{
  patrimonio: String (único),
  filial: String,
  modelo: String,
  imei: String,
  numero: String,
  responsavel: String,
  status: String,
  obs: String,
  created_at: Date,
  updated_at: Date
}
```

### **Collection: softwares**
```javascript
{
  nome: String,
  versao: String,
  asset_id: ObjectId,
  tipo_licenca: String,
  chave_licenca: String,
  dt_instalacao: Date,
  dt_vencimento: Date,
  renovacao_automatica: Boolean,
  custo_anual: Number,
  status: String,
  obs: String,
  created_at: Date,
  updated_at: Date
}
```

### **Collection: emails**
```javascript
{
  endereco: String,
  tipo: String (google|zimbra),
  asset_id: ObjectId,
  usuario: String,
  senha: String,
  recuperacao: String,
  data_criacao: Date,
  status: String,
  obs: String,
  created_at: Date,
  updated_at: Date
}
```

---

## 🧪 Testes Recomendados

1. **Teste de Criação:**
   - Crie um novo celular com dados válidos
   - Verifique se aparece na lista
   - Verifique se o histórico foi registrado

2. **Teste de Unicidade de PAT:**
   - Tente criar dois celulares com o mesmo PAT
   - Verifique se retorna erro 409 (Conflict)

3. **Teste de Vencimento de Licenças:**
   - Crie softwares com datas de vencimento próximas
   - Verifique se as cores dos badges mudam corretamente

4. **Teste de Autenticação:**
   - Verifique se sem token JWT as requisições retornam 401
   - Verifique se com token inválido retorna 422

5. **Teste de Auditoria:**
   - Faça alterações em qualquer registro
   - Verifique na aba "Auditoria" se a mudança foi registrada

---

## ⚠️ Próximas Melhorias

- [ ] Relatórios avançados de licenças em vencimento
- [ ] Importação em massa (CSV)
- [ ] Exportação de relatórios (PDF/Excel)
- [ ] Integração com calendário para alertas de vencimento
- [ ] Dashboard com estatísticas gerais
- [ ] Backup automático de dados

---

**Desenvolvido em:** 23/01/2026
**Sistema:** TI Manager - Inventário Corporativo
