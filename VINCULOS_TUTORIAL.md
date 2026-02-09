# 📋 Documentação: Correção de Vínculos Ativos ↔ E-mails ↔ Softwares

## 🎯 Problema Identificado
Após a migração de MongoDB para PostgreSQL, o vínculo entre E-mails/Softwares e Ativos (Computadores) não estava funcionando porque:

1. **Mudança de ID**: MongoDB usava ObjectId (texto), PostgreSQL usa Integer
2. **Falta de Relacionamentos**: O ORM SQLAlchemy precisava de Foreign Keys explícitas
3. **API Incompleta**: Os endpoints não retornavam dados aninhados dos relacionamentos

## ✅ Soluções Implementadas

### 1. **Modelo de Dados (app/models.py)**
- ✅ Adicionado método `to_dict(include_relationships=False)` ao modelo Asset
- ✅ Quando `include_relationships=True`, retorna emails e softwares aninhados
- ✅ Foreign Keys já estavam configuradas corretamente em Email e Software

### 2. **Novos Endpoints da API**

#### GET /api/assets/{id}
Retorna um Asset com dados completos e relacionamentos aninhados:
```json
{
  "id": "1",
  "patrimonio": "DESKTOP-001",
  "tipo": "Computador",
  "emails": [
    {
      "id": "1",
      "endereco": "user@empresa.com",
      "tipo": "google",
      "asset_id": "1",
      "asset_patrimonio": "DESKTOP-001"
    }
  ],
  "softwares": [
    {
      "id": "1",
      "nome": "Microsoft Office",
      "versao": "2021",
      "asset_id": "1",
      "asset_patrimonio": "DESKTOP-001"
    }
  ]
}
```

#### GET /api/assets/{id}/emails
Retorna apenas os e-mails vinculados a um asset:
```json
[
  {
    "id": "1",
    "endereco": "user@empresa.com",
    "tipo": "google",
    "asset_patrimonio": "DESKTOP-001"
  }
]
```

#### GET /api/assets/{id}/softwares
Retorna apenas os softwares vinculados a um asset:
```json
[
  {
    "id": "1",
    "nome": "Microsoft Office",
    "versao": "2021",
    "asset_patrimonio": "DESKTOP-001"
  }
]
```

### 3. **Scripts de Diagnóstico e Correção**

#### diagnosticar_vinculos.py
Verifica a integridade dos dados:
```bash
python diagnosticar_vinculos.py
```
Detecta:
- ✅ E-mails órfãos (sem asset_id)
- ✅ E-mails com asset_id inválido
- ✅ Softwares órfãos (sem asset_id)
- ✅ Softwares com asset_id inválido
- ✅ Assets sem relacionamentos

#### corrigir_vinculos.py
Corrige automaticamente problemas encontrados:
```bash
python corrigir_vinculos.py
```
Oferece opções para:
- Deletar registros órfãos
- Desvincular registros inválidos
- Re-vincular automaticamente

## 🔧 Como Usar no Frontend (React)

### Exemplo: Carregar Asset com E-mails
```javascript
// Antes (não trazia e-mails)
GET /api/assets/1
// Resposta: apenas dados básicos do asset

// Agora (traz e-mails aninhados)
GET /api/assets/1
// Resposta: asset + emails + softwares
```

### Código React (Exemplo)
```jsx
import { useEffect, useState } from 'react';
import axios from 'axios';

export function AssetDetail({ assetId }) {
  const [asset, setAsset] = useState(null);
  
  useEffect(() => {
    axios.get(`/api/assets/${assetId}`)
      .then(res => {
        setAsset(res.data);
        console.log('E-mails vinculados:', res.data.emails);
        console.log('Softwares vinculados:', res.data.softwares);
      });
  }, [assetId]);
  
  if (!asset) return <div>Carregando...</div>;
  
  return (
    <div>
      <h2>{asset.patrimonio}</h2>
      
      <h3>E-mails</h3>
      {asset.emails.map(email => (
        <div key={email.id}>{email.endereco}</div>
      ))}
      
      <h3>Softwares</h3>
      {asset.softwares.map(soft => (
        <div key={soft.id}>{soft.nome} {soft.versao}</div>
      ))}
    </div>
  );
}
```

## 📊 Estrutura de Integridade Referencial

```
Workstations (Assets)
  ├─ id (Primary Key)
  ├─ patrimonio
  ├─ hostname
  └─ ... outros campos

E-mails
  ├─ id (Primary Key)
  ├─ endereco
  └─ asset_id (Foreign Key → Workstations.id) ← VÍNCULO CRÍTICO

Softwares
  ├─ id (Primary Key)
  ├─ nome
  └─ asset_id (Foreign Key → Workstations.id) ← VÍNCULO CRÍTICO
```

## 🚀 Próximos Passos

1. **Frontend**: Atualizar componentes React para usar os novos endpoints com dados aninhados
2. **Componentes de Edição**: Criar abas para exibir/editar e-mails e softwares lado-a-lado
3. **Validação**: Adicionar validação ao criar e-mails/softwares para garantir asset_id válido
4. **UI**: Implementar indicadores visuais de "vinculado"/"desvinculado"

## 🔍 Diagnóstico Rápido

```bash
# Ver status dos vínculos
python diagnosticar_vinculos.py

# Se houver problemas:
python corrigir_vinculos.py

# Depois, verificar novamente
python diagnosticar_vinculos.py
```

## ✨ Resultado Final

Agora quando você:
1. Abre um Asset no frontend
2. A API retorna TODOS os dados (Asset + E-mails + Softwares)
3. Frontend pode exibir em abas ou seções
4. Vínculo é transparente e robusto no PostgreSQL
