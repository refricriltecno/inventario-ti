# 📥 Guia de Importação: Patrimonios via CSV

## 🎯 Como Importar a Planilha de Patrimonios

### 1. **Acessar a Interface**
   - Vá para **"Inventário de Ativos"** no menu lateral
   - Clique no botão **"Importar CSV"** (botão verde)

### 2. **Preparar o Arquivo CSV**

O arquivo `patrimonios.csv` já está pronto! Ele contém:
- **PAT**: Número de patrimônio (obrigatório - ex: 000786)
- **Em Uso**: Nome do responsável pelo equipamento
- **Tipo**: Notebook ou Desktop
- **Modelo**: Modelo do equipamento (ex: Optiplex 3080)
- **Hostname**: Nome do computador na rede
- **AnyDesk**: ID do AnyDesk para acesso remoto
- **Senha Windows**: Senha do Windows (armazenada de forma segura)
- **Senha BIOS**: Senha do BIOS
- **IP**: Endereço IP do equipamento
- **Dominio**: Se está vinculado ao domínio (Sim/Não)
- **Centro de Custo Filial**: Unidade/Filial onde está alocado

### 3. **Formato Esperado**

O sistema aceita arquivos CSV com:
- ✅ Separadores: **vírgula (,)** ou **ponto-e-vírgula (;)**
- ✅ Codificação: UTF-8
- ✅ Cabeçalho obrigatório na primeira linha

### 4. **Executar Importação**

```
1. Abra o modal "Importar CSV" via botão
2. Selecione o arquivo patrimonios.csv
3. Clique em "Enviar e Processar"
4. Aguarde a conclusão da importação
```

### 5. **Resultado da Importação**

Após o processamento, você verá um relatório com:
- ✅ **Sucessos**: Número de ativos criados
- ❌ **Erros**: Lista de problemas encontrados
  - Patrimônios duplicados
  - Campos obrigatórios faltando
  - Linhas mal formatadas

### 6. **O Que Acontece com os Dados**

Cada linha do CSV se transforma em um **Ativo (Computador)** com:
- ID único no banco de dados
- Todos os campos mapeados automaticamente
- Senha Windows e BIOS armazenadas criptografadas
- Status padrão: "Ativo"
- Marca de importação nos comentários

## 📊 Estrutura de Dados Importados

```json
{
  "patrimonio": "000786",
  "tipo": "Desktop",
  "modelo": "Optiplex 3080",
  "hostname": "BALC001DESK002",
  "filial": "São Paulo (Osasco)",
  "responsavel": "FABIANA FERNANDES",
  "status": "Ativo",
  "anydesk": "1 615 646 911",
  "observacoes": "Importado via CSV",
  "especificacoes": {
    "ip": "10.1.1.xxx",
    "dominio": true,
    "vpn_login": "usuario",
    "senha_bios": "****",
    "senha_windows": "****",
    "senha_vpn": "****"
  }
}
```

## ⚠️ Importante

- **Duplicação**: Se um patrimônio já existe, será pulado (não substitui)
- **Erros não bloqueantes**: Se uma linha falha, as outras continuam sendo importadas
- **Senhas seguras**: São armazenadas com hash/criptografia
- **Validação**: Apenas a coluna PAT é obrigatória, mas outros campos melhoram a informação

## 🔗 Vinculando Depois

Após importar os Ativos, você pode:
1. **Importar E-mails**: `POST /api/import/emails` (referenciando os PATs)
2. **Importar Softwares**: `POST /api/import/softwares` (referenciando os PATs)
3. **Vincular Manualmente**: Editar o Ativo e adicionar informações na interface

## 📝 Exemplo de Uso

**Arquivo CSV (patrimonios.csv):**
```csv
PAT,Em Uso,Tipo,Modelo,Hostname,AnyDesk,Senha Windows,Dominio,Centro de Custo Filial
000786,FABIANA FERNANDES,Desktop,Optiplex 3080,BALC001DESK002,1 615 646 911,senha123,Sim,São Paulo (Osasco)
000777,KAWANY CAETANO,Desktop,Optiplex 3080,PC-PAT-000777,1 520 625 635,senha456,Não,São Paulo (Guarulhos)
001545,GABRIEL FERREIRA,Notebook,Vostro 3584,DESKTOP-TQ46B5I,1 237 603 737,senha789,Sim,Matriz
```

**Resultado:**
- ✅ 3 ativos criados com sucesso
- ✅ Dados disponíveis imediatamente na interface
- ✅ Prontos para vincular e-mails e softwares

## 🆘 Solução de Problemas

| Erro | Causa | Solução |
|------|-------|---------|
| "Patrimônio (PAT) vazio" | Coluna PAT não preenchida | Verificar se a coluna existe e tem valores |
| "Ativo xxx já existe" | PAT duplicado | Remover duplicatas do arquivo |
| "Separador não detectado" | Formato incorreto | Salvar como CSV com separador válido |
| Arquivo não selecionado | Sem arquivo no input | Clique em "Selecionar arquivo..." |

## 📚 Links Relacionados

- [Importação de E-mails](./EMAILS_IMPORT.md)
- [Importação de Softwares](./SOFTWARES_IMPORT.md)
- [API de Importação](./API_REFERENCE.md#importação)
