# 🛡️ TI Manager - Sistema Integrado de Gestão de Ativos

> Sistema corporativo para controle centralizado de inventário de TI (ITAM), gerenciando computadores, dispositivos móveis, licenças de software e identidades.

![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)
![Backend](https://img.shields.io/badge/Backend-Python%20%7C%20Flask-blue)
![Frontend](https://img.shields.io/badge/Frontend-React%20%7C%20Vite-61DAFB)
![Database](https://img.shields.io/badge/Database-MongoDB-green)

## 🎯 Objetivo
Substituir controles manuais (planilhas) por uma plataforma Web segura e auditável, garantindo a integridade dos dados, histórico de movimentação de ativos e controle de custos de licenciamento entre Matriz, Filiais e Centros de Distribuição.

## ✨ Funcionalidades Principais

### 🖥️ Gestão de Workstations
- Cadastro completo de Desktops e Notebooks (Hardware, Hostname, Modelo).
- **Segurança:** Armazenamento seguro de senhas administrativas (BIOS, Windows, VPN) com visualização protegida.
- **Rede:** Registro de IPs, IDs de acesso remoto (AnyDesk/TeamViewer).
- **Histórico:** Log automático de troca de responsáveis e setores.

### 📱 Dispositivos Móveis
- Controle de celulares corporativos por IMEI e número da linha.
- Vínculo direto com o colaborador responsável.
- Status de ciclo de vida (Em uso, Reserva, Manutenção).

### 💾 Softwares & Licenças
- Controle de validade de licenças com **alertas visuais** (Vencido/A Vencer).
- Gestão de chaves de ativação (License Keys) protegidas.
- Previsibilidade de custos anuais e renovações automáticas.

### 📧 Gestão de E-mails
- Controle de contas Google Workspace e Zimbra vinculadas ao ativo principal.
- Armazenamento de credenciais iniciais e e-mails de recuperação.

### 🔒 Auditoria & Segurança
- **Logs Imutáveis:** Rastreabilidade total de quem alterou o que e quando.
- **Soft Delete:** Exclusão lógica para preservação de histórico.
- **Autenticação:** Proteção de rotas e dados sensíveis.

---

## 🛠️ Tecnologias Utilizadas

**Backend:**
- Python 3.10+
- Flask (API REST)
- PyMongo (Driver MongoDB)
- Flask-CORS

**Frontend:**
- React.js (Vite)
- Chakra UI v2 (Interface)
- Axios (Integração API)

**Banco de Dados:**
- MongoDB Atlas (Cloud) ou Local

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos
- Python 3.10 ou superior
- Node.js 18+ e npm
- Uma string de conexão do MongoDB

### 1. Configuração do Backend (API)

```bash
# Clone o repositório
git clone [https://github.com/seu-usuario/inventario-ti.git](https://github.com/seu-usuario/inventario-ti.git)
cd inventario-ti

# Crie e ative o ambiente virtual (Windows)
python -m venv venv
.\venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Configure o Banco de Dados
# Edite o arquivo config.py e insira sua MONGO_URI

# (Opcional) Popule o banco com dados iniciais de Filiais
python popular_banco.py

# Inicie o Servidor
python run.py
O Backend rodará em http://127.0.0.1:5000

2. Configuração do Frontend (Interface)
Abra um novo terminal:

Bash
cd frontend-ti

# Instale as dependências
npm install

# Force a instalação da versão correta do Chakra UI (se necessário)
npm install @chakra-ui/react@2.8.2 @chakra-ui/icons@2.1.1 framer-motion

# Inicie o Frontend
npm run dev
O Frontend rodará em http://localhost:5173

📂 Estrutura do Projeto
Plaintext
/inventario-ti
│
├── app/
│   ├── routes/          # Rotas da API (Assets, Emails, Softwares...)
│   ├── services/        # Lógica de Auditoria e Logs
│   ├── static/          # Arquivos estáticos
│   └── templates/       # (Legado) Templates Jinja2
│
├── frontend-ti/         # Aplicação React
│   ├── src/
│   │   ├── components/  # Componentes reutilizáveis
│   │   ├── App.jsx      # Componente Principal
│   │   └── main.jsx     # Ponto de entrada
│
├── config.py            # Configuração do MongoDB
├── run.py               # Inicializador do Flask
└── requirements.txt     # Dependências Python
🤝 Contribuição
Faça um Fork do projeto

Crie uma Branch para sua Feature (git checkout -b feature/NovaFeature)

Faça o Commit (git commit -m 'Add some NovaFeature')

Faça o Push (git push origin feature/NovaFeature)

Abra um Pull Request

Desenvolvido por Equipe de TI - 2026


### Dicas Extras para valorizar seu repositório:

1.  **Adicione Screenshots:** Assim que o sistema estiver rodando bonito com alguns dados fictícios, tire prints das telas (Lista de Ativos, Modal de Edição com as abas, Tela de Softwares com os alertas de vencimento). Coloque uma pasta `/docs/img` e linke no README logo após a descrição. Isso "vende" o projeto visualmente.
2.  **Scripts de Automação:** Mencionei o `python popular_banco.py` no passo a passo, pois isso ajuda quem for testar a não pegar um sistema vazio sem as lojas cadastradas.
