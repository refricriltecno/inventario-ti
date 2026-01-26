# ✅ Checklist Pré-Produção

## 🔒 Segurança

- [ ] **JWT Token**
  - [ ] Token expira automaticamente
  - [ ] Todas as rotas validam token
  - [ ] Secret key está em variável de ambiente

- [ ] **Senhas**
  - [ ] Bcrypt está sendo usado para hash
  - [ ] Senhas de BIOS/Windows/VPN não aparecem em logs
  - [ ] Campos sensíveis usam type="password" no frontend

- [ ] **Banco de Dados**
  - [ ] MongoDB usa autenticação
  - [ ] Collections têm índices para campos únicos
  - [ ] Backup automático configurado

- [ ] **CORS**
  - [ ] Apenas origin permitido está configurado
  - [ ] Métodos HTTP corretos

- [ ] **Validação de Entrada**
  - [ ] Todos os campos obrigatórios validados
  - [ ] Tipos de dados corretos
  - [ ] Limites de comprimento

---

## 📋 Funcionalidades

### Celulares
- [ ] CRUD completo funciona
- [ ] Patrimônio é único
- [ ] Filtro por filial funciona
- [ ] Status pode ser Em Uso, Reserva, Manutenção, Inativo
- [ ] Soft delete funciona (não deleta, apenas marca como inativo)

### Softwares
- [ ] CRUD completo funciona
- [ ] Vinculação com Asset funciona
- [ ] Datas de instalação e vencimento obrigatórias
- [ ] Cores de vencimento funcionam (verde/laranja/vermelho)
- [ ] Rota de verificação de vencimento funciona
- [ ] Renovação automática é um checkbox

### Emails
- [ ] CRUD completo funciona
- [ ] Tipo pode ser google ou zimbra
- [ ] Vinculação com Asset funciona
- [ ] Senha fica protegida
- [ ] Show/Hide de senha funciona
- [ ] Email de recuperação é campo opcional

### Auditoria
- [ ] Toda criação registra log
- [ ] Toda atualização registra log
- [ ] Toda deleção registra log
- [ ] Logs mostram usuário que fez operação
- [ ] Logs são imutáveis

---

## 🎨 Frontend

- [ ] Layout responsive funciona em mobile
- [ ] Tabelas scrollam horizontalmente em telas pequenas
- [ ] Cores e temas consistentes
- [ ] Mensagens de erro claras
- [ ] Toast notifications funcionam
- [ ] Botões desabilitados durante carregamento
- [ ] Ícones carregam corretamente

### Formulários
- [ ] Validação de campos obrigatórios
- [ ] Mascaras de entrada corretas
- [ ] Data picker funciona
- [ ] Select boxes carregam dados
- [ ] Imagens/ícones aparecem

### Navegação
- [ ] Menu lateral abre e fecha
- [ ] Todas as abas aparecem no menu
- [ ] Logout funciona e limpa cache
- [ ] Back/Forward do navegador funciona

---

## 🔌 Backend

- [ ] Flask inicia sem erros
- [ ] Variáveis de ambiente estão configuradas
- [ ] MongoDB conecta corretamente
- [ ] Logging de requisições funciona
- [ ] CORS headers corretos
- [ ] Tratamento de exceções implementado

### Rotas
- [ ] Todas as 15+ rotas respondendo
- [ ] Status codes corretos (200, 201, 400, 404, 409, etc)
- [ ] Campos retornam em JSON correto
- [ ] IDs ObjectId convertidos para String

### Performance
- [ ] Consultas ao BD usam índices
- [ ] Paginação implementada (se necessário)
- [ ] Cache implementado (se necessário)
- [ ] Requisições respondem em < 1s

---

## 📊 Banco de Dados

- [ ] Collections criadas: celulares, softwares, emails
- [ ] Índices criados para campos únicos
- [ ] Índices criados para buscas frequentes
- [ ] Documentos têm estrutura correta
- [ ] Timestamps (created_at, updated_at) presentes

### Dados de Teste
- [ ] Pelo menos 5 celulares cadastrados
- [ ] Pelo menos 5 softwares cadastrados
- [ ] Pelo menos 3 emails cadastrados
- [ ] Dados variados por filial

---

## 🧪 Testes

### Testes Manuais Executados
- [ ] Login/Logout
- [ ] Criar celular
- [ ] Editar celular
- [ ] Inativar celular
- [ ] Filtrar celulares por filial
- [ ] Criar software
- [ ] Editar software
- [ ] Inativar software
- [ ] Filtrar software por asset
- [ ] Verificar cores de vencimento
- [ ] Criar email google
- [ ] Criar email zimbra
- [ ] Mostrar/ocultar senha
- [ ] Filtrar emails por tipo
- [ ] Verificar auditoria

### Testes de Erro
- [ ] Criar celular sem patrimônio → erro
- [ ] Criar celular com patrimônio duplicado → erro 409
- [ ] Criar software sem asset → erro
- [ ] Criar email sem tipo válido → erro
- [ ] Requisitar sem token → erro 401
- [ ] Requisitar com token expirado → erro 422

### Testes de Integração
- [ ] Criar celular → aparece na lista
- [ ] Editar celular → dado atualiza na tabela
- [ ] Inativar celular → desaparece da lista (soft delete)
- [ ] Criar software com celular → vinculação funciona
- [ ] Criar email com computador → vinculação funciona

---

## 📈 Performance

- [ ] Tempo de carregamento inicial < 3s
- [ ] Tabulações respondem em < 1s
- [ ] Filtros respondem em < 500ms
- [ ] Requisições de criação < 2s
- [ ] Sem memory leaks (verificar DevTools)
- [ ] Sem erros de CORS no console

---

## 📱 Responsividade

- [ ] Desktop (1920px) - funciona
- [ ] Tablet (768px) - funciona
- [ ] Mobile (320px) - funciona
- [ ] Menu lateral responsivo
- [ ] Tabelas scrollam em mobile
- [ ] Modais aparecem correto em mobile

---

## 🚀 Deploy

- [ ] Variáveis de ambiente em .env
- [ ] CORS origins configurados
- [ ] JWT secret em variável ambiente
- [ ] MongoDB connection string segura
- [ ] Logs configurados
- [ ] Error handling em produção
- [ ] HTTPS ativado
- [ ] HSTS headers configurados
- [ ] Rate limiting implementado
- [ ] Backup automático agendado

---

## 📚 Documentação

- [ ] README.md completo
- [ ] IMPLEMENTACOES.md atualizado
- [ ] API_REFERENCE.md atualizado
- [ ] ARQUITETURA.md explicando estrutura
- [ ] GUIA_TESTE.md com exemplos
- [ ] Comentários no código
- [ ] Docstrings em funções importantes

---

## 👥 Permissões e Usuários

- [ ] Admin pode acessar todas as funcionalidades
- [ ] Usuários normais podem criar/editar/visualizar
- [ ] Usuários normais não podem deletar usuários
- [ ] Permissões validadas no backend
- [ ] Permissões validadas no frontend

---

## 🔍 Monitoria

- [ ] Logs centralizados
- [ ] Alertas para erros críticos
- [ ] Dashboard de status
- [ ] Monitoramento de performance
- [ ] Alertas de limite de espaço disco

---

## 📞 Suporte

- [ ] Documentação clara para usuários finais
- [ ] FAQ documentado
- [ ] Contatos de suporte definidos
- [ ] Plano de rollback em caso de erro

---

## Assinatura

**Data:** ___/___/2026

**Responsável:** _____________________

**Aprovado por:** _____________________

---

## Notas Adicionais

```
[Espaço para anotações sobre a verificação]



```

---

**Última atualização:** 23/01/2026
**Versão:** 1.0.0
