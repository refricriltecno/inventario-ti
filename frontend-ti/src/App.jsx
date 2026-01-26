import React, { useState, useEffect } from 'react';
import { 
  Box, Flex, Heading, Text, Button, Table, Thead, Tbody, Tr, Th, Td, 
  Badge, Input, Select, useToast, Modal, ModalOverlay, ModalContent, 
  ModalHeader, ModalBody, ModalCloseButton, FormControl, FormLabel,
  VStack, HStack, IconButton, Tabs, TabList, TabPanels, Tab, TabPanel,
  Textarea, InputGroup, InputRightElement, Divider, List, ListItem, ListIcon,
  Checkbox, MenuButton, Menu, MenuItem, MenuList
} from '@chakra-ui/react';
import { AddIcon, EditIcon, DeleteIcon, ViewIcon, ViewOffIcon, SettingsIcon, CheckCircleIcon, PhoneIcon, SmallCloseIcon } from '@chakra-ui/icons';
import axios from 'axios';
import Login from './Login';
import Logs from './Logs';
import AssetDetail from './AssetDetail';
import UsersManagement from './UsersManagement';
import CelularesComponent from './Celulares';
import SoftwaresComponent from './Softwares';
import EmailsComponent from './Emails';
import EmailsPatrimonioComponent from './EmailsPatrimonio';
import SoftwaresPatrimonioComponent from './SoftwaresPatrimonio';

const API_URL = 'http://127.0.0.1:5000/api';

const SETORES_POR_TIPO = {
  'Administrativo': [
    'Análise de Crédito', 'Auxiliar Televendas', 'Cadastro', 'Cadastro de Produto', 
    'Cobrança', 'Comercial', 'Compras', 'Contabil / Fiscal', 'Controladoria', 
    'Controle de Estoque', 'Dep. Pessoal', 'Direção', 'Ecommerce', 'Financeiro', 
    'Garantia', 'Gerente Televendas', 'Liberação de Pedido / Depósito', 'Logística', 
    'Marketing', 'Negociação', 'Pricing', 'Projeto', 'RH', 'Servidor', 'Televendas'
  ].sort(),
  'Loja': [
    'Balcão', 'Caixa', 'Conferência', 'Estoque', 'Faturamento', 'Gerente Loja', 
    'Recebimento', 'Servidor', 'Televendas', 'Televendas Loja', 'Vendas', 
    'Vendas Ar', 'Vendas WhatsApp'
  ].sort(),
  'CD': [
    'Assistente Inventário', 'Conferência', 'Doca', 'Estoque', 'Expedição', 
    'Faturamento', 'Garantia', 'Gerente CD', 'Organização', 'Recebimento', 'Servidor'
  ].sort()
};

const initialFormState = {
  patrimonio: '', filial: '', setor: '', responsavel: '', 
  hostname: '', tipo: 'Notebook', modelo: '', obs: '',
  ip: '', anydesk: '', duapi: '', dominio: 'Não',
  senha_bios: '', senha_windows: '', vpn_login: '', senha_vpn: '', gix_remoto: '',
  email_google: '', email_zimbra: '', 
  ramal: '', is_softphone: false
};

function App() {
  const [usuario, setUsuario] = useState(null);
  const [paginaAtual, setPaginaAtual] = useState('assets');
  
  const [assets, setAssets] = useState([]);
  const [celulares, setCelulares] = useState([]);
  const [softwares, setSoftwares] = useState([]);
  const [filiais, setFiliais] = useState([]);
  const [filialFiltro, setFilialFiltro] = useState('');
  const [filtros, setFiltros] = useState({
    pat: '',
    responsavel: '',
    setor: '',
    equipamento: '',
    anydesk: '',
    tipo: ''
  });
  
  const [isOpen, setIsOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(null);
  const [modalFilialOpen, setModalFilialOpen] = useState(false);
  const [formData, setFormData] = useState(initialFormState);
  
  const [novaFilial, setNovaFilial] = useState({ nome: '', tipo: 'Loja' });
  const [showPassword, setShowPassword] = useState({});
  const [setoresDisponiveis, setSetoresDisponiveis] = useState([]);
  const [responsaveisDisponiveis, setResponsaveisDisponiveis] = useState([]);

  const toast = useToast();

  // Configurar interceptor de autenticação e carregar dados na montagem
  useEffect(() => {
    const token = localStorage.getItem('token');
    const usuarioArmazenado = localStorage.getItem('usuario');
    
    if (token && usuarioArmazenado) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setUsuario(JSON.parse(usuarioArmazenado));
    }
  }, []);

  // Carregar dados quando usuário está autenticado
  useEffect(() => {
    if (usuario) {
      fetchData();
    }
  }, [usuario]);

  const handleLoginSuccess = (usuarioData) => {
    // Get token from localStorage (was just set by Login component)
    const token = localStorage.getItem('token');
    console.log('Login bem-sucedido! Token:', token ? token.substring(0, 20) + '...' : 'NÃO ENCONTRADO');
    
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Pequeno delay para garantir que o header está configurado
      setTimeout(() => {
        setUsuario(usuarioData);
        setPaginaAtual('assets');
      }, 100);
    } else {
      console.error('Token não foi salvo no localStorage após login!');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('usuario');
    delete axios.defaults.headers.common['Authorization'];
    setUsuario(null);
    setAssets([]);
    setFiliais([]);
  };

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        console.warn('Nenhum token disponível para requisição');
        return;
      }
      
      const headers = { Authorization: `Bearer ${token}` };
      
      const params = filialFiltro ? { filial: filialFiltro } : {};
      const resAssets = await axios.get(`${API_URL}/assets`, { params, headers });
      // Filtrar apenas ativos
      const ativos = resAssets.data.filter(a => a.status !== 'Inativo');
      setAssets(ativos);
      
      const resCelulares = await axios.get(`${API_URL}/celulares`, { params, headers });
      const celularesAtivos = resCelulares.data.filter(c => c.status !== 'Inativo');
      setCelulares(celularesAtivos);
      
      const resSoftwares = await axios.get(`${API_URL}/softwares`, { headers });
      const softwaresAtivos = resSoftwares.data.filter(s => s.status !== 'Inativo');
      setSoftwares(softwaresAtivos);
      
      const resFiliais = await axios.get(`${API_URL}/filiais`, { headers });
      setFiliais(resFiliais.data);
    } catch (error) { 
      console.error('Erro ao carregar dados:', error.response?.status, error.message);
      if (error.response?.status === 401 || error.response?.status === 422) {
        handleLogout();
      }
    }
  };

  useEffect(() => { 
    if (usuario) {
      fetchData(); 
    }
  }, [filialFiltro]);

  const filtrarAssets = () => {
    return assets.filter(asset => {
      if (filtros.pat && !asset.patrimonio?.toLowerCase().includes(filtros.pat.toLowerCase())) return false;
      if (filtros.responsavel && !asset.responsavel?.toLowerCase().includes(filtros.responsavel.toLowerCase())) return false;
      if (filtros.setor && !asset.setor?.toLowerCase().includes(filtros.setor.toLowerCase())) return false;
      if (filtros.equipamento && !asset.hostname?.toLowerCase().includes(filtros.equipamento.toLowerCase())) return false;
      if (filtros.anydesk && !asset.anydesk?.toLowerCase().includes(filtros.anydesk.toLowerCase())) return false;
      if (filtros.tipo && asset.tipo !== filtros.tipo) return false;
      return true;
    });
  };

  const limparFiltros = () => {
    setFiltros({
      pat: '',
      responsavel: '',
      setor: '',
      equipamento: '',
      anydesk: '',
      tipo: ''
    });
  };

  useEffect(() => {
    if (formData.filial) {
      const filialObj = filiais.find(f => f.nome === formData.filial);
      if (filialObj && filialObj.tipo) {
        let setores = SETORES_POR_TIPO[filialObj.tipo] || [];
        
        // Se o setor atual não está na lista predefinida, adicioná-lo
        if (formData.setor && !setores.includes(formData.setor)) {
          setores = [...setores, formData.setor].sort();
        }
        
        setSetoresDisponiveis(setores);
      } else {
        setSetoresDisponiveis([]);
      }
      // Buscar responsáveis (funcionários) da filial selecionada
      axios.get(`${API_URL}/funcionarios/${encodeURIComponent(formData.filial)}`)
        .then(res => {
          // Se tiver funcionários da API, usa eles
          if (res.data && res.data.length > 0) {
            setResponsaveisDisponiveis(res.data);
          } else {
            // Caso contrário, extrai responsáveis dos ativos dessa filial
            const responsaveisUnicos = [...new Set(
              assets
                .filter(a => a.filial === formData.filial && a.responsavel && a.responsavel.trim() !== '')
                .map(a => a.responsavel)
            )].sort();
            setResponsaveisDisponiveis(responsaveisUnicos);
          }
        })
        .catch(err => { 
          console.error(err); 
          // Se erro na API, tenta extrair dos ativos
          const responsaveisUnicos = [...new Set(
            assets
              .filter(a => a.filial === formData.filial && a.responsavel && a.responsavel.trim() !== '')
              .map(a => a.responsavel)
          )].sort();
          setResponsaveisDisponiveis(responsaveisUnicos);
        });
    } else {
      setSetoresDisponiveis([]);
      setResponsaveisDisponiveis([]);
    }
  }, [formData.filial, filiais, assets, formData.setor]);

  const handleOpenCreate = () => { setFormData(initialFormState); setIsEditing(null); setIsOpen(true); };
  const handleOpenEdit = (asset) => { setFormData({ ...initialFormState, ...asset }); setIsEditing(asset._id); setIsOpen(true); };
  
  const handleSave = async () => {
    try {
      if (isEditing) { await axios.put(`${API_URL}/assets/${isEditing}`, formData); } 
      else { await axios.post(`${API_URL}/assets`, formData); }
      toast({ title: 'Salvo com sucesso!', status: 'success' });
      setIsOpen(false); fetchData();
    } catch (error) { toast({ title: 'Erro', status: 'error' }); }
  };

  const handleDelete = async (id, patrimonio) => {
    if (window.confirm(`Tem certeza que deseja inativar o PAT ${patrimonio}?`)) {
      try {
        await axios.delete(`${API_URL}/assets/${id}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        toast({ title: 'Ativo inativado com sucesso!', status: 'success' });
        fetchData();
      } catch (error) {
        toast({ title: 'Erro ao inativar', status: 'error' });
      }
    }
  };

  const handleChange = (f, v) => { setFormData(prev => ({ ...prev, [f]: v })); };
  const togglePass = (f) => { setShowPassword(prev => ({...prev, [f]: !prev[f]})); };

  const handleSaveFilial = async () => {
    if (!novaFilial.nome) return;
    try {
      await axios.post(`${API_URL}/filiais`, novaFilial);
      toast({ title: 'Unidade Criada!', status: 'success' });
      setNovaFilial({ nome: '', tipo: 'Loja' });
      fetchData();
    } catch (error) { toast({ title: 'Erro - Talvez já exista?', status: 'error' }); }
  };

  const handleDeleteFilial = async (id, nome) => {
    if(!window.confirm(`Tem certeza que deseja excluir ${nome}?`)) return;
    try {
        await axios.delete(`${API_URL}/filiais/${id}`);
        toast({ title: 'Unidade Removida!', status: 'info' });
        fetchData();
    } catch (error) { toast({ title: 'Erro ao excluir', status: 'error' }); }
  };

  return (
    <>
      {!usuario ? (
        <Login onLoginSuccess={handleLoginSuccess} />
      ) : (
        <Flex h="100vh" bg="gray.50">
      <Box w="260px" bg="gray.900" color="white" p={5} display="flex" flexDirection="column">
        <VStack align="stretch" spacing={4} flex="1">
          <Box>
            <Heading size="md" mb={2} color="teal.300">TI Manager 🛡️</Heading>
            <Text fontSize="xs" color="gray.400">{usuario.nome}</Text>
            <Text fontSize="xs" color="gray.500">{usuario.filial}</Text>
          </Box>
          
          <Divider borderColor="gray.700" />
          
          <Button
            w="full"
            justifyContent="flex-start"
            bg={paginaAtual === 'assets' ? 'teal.600' : 'transparent'}
            _hover={{ bg: 'teal.700' }}
            onClick={() => { setPaginaAtual('assets'); fetchData(); }}
          >
            Inventário
          </Button>

          <Button
            w="full"
            justifyContent="flex-start"
            bg={paginaAtual === 'celulares' ? 'teal.600' : 'transparent'}
            _hover={{ bg: 'teal.700' }}
            onClick={() => setPaginaAtual('celulares')}
          >
            Celulares
          </Button>

          <Button
            w="full"
            justifyContent="flex-start"
            bg={paginaAtual === 'softwares' ? 'teal.600' : 'transparent'}
            _hover={{ bg: 'teal.700' }}
            onClick={() => setPaginaAtual('softwares')}
          >
            Softwares
          </Button>

          <Button
            w="full"
            justifyContent="flex-start"
            bg={paginaAtual === 'emails' ? 'teal.600' : 'transparent'}
            _hover={{ bg: 'teal.700' }}
            onClick={() => setPaginaAtual('emails')}
          >
            Emails
          </Button>
          
          {usuario.permissoes?.includes('admin') && (
            <>
              <Button
                w="full"
                justifyContent="flex-start"
                bg={paginaAtual === 'logs' ? 'teal.600' : 'transparent'}
                _hover={{ bg: 'teal.700' }}
                onClick={() => setPaginaAtual('logs')}
              >
                Auditoria
              </Button>
              
              <Button
                w="full"
                justifyContent="flex-start"
                bg={paginaAtual === 'usuarios' ? 'teal.600' : 'transparent'}
                _hover={{ bg: 'teal.700' }}
                onClick={() => setPaginaAtual('usuarios')}
              >
                Gerenciar Usuários
              </Button>
            </>
          )}
          
          <Box>
            <Text fontSize="xs" color="gray.500" fontWeight="bold" mb={1}>FILTRAR UNIDADE</Text>
            <Select bg="gray.800" border="none" size="sm" value={filialFiltro} onChange={(e) => setFilialFiltro(e.target.value)} isDisabled={paginaAtual !== 'assets'}>
              <option value="" style={{color:'black'}}>Todas</option>
              {filiais.map(f => <option key={f._id} value={f.nome} style={{color:'black'}}>{f.nome}</option>)}
            </Select>
          </Box>
          
          {paginaAtual === 'assets' && (
            <Button leftIcon={<SettingsIcon />} size="sm" variant="outline" colorScheme="teal" onClick={() => setModalFilialOpen(true)}>Gerenciar Unidades</Button>
          )}
        </VStack>
        
        <Divider borderColor="gray.700" />
        
        <Button
          w="full"
          leftIcon={<SmallCloseIcon />}
          colorScheme="red"
          size="sm"
          mt={4}
          onClick={handleLogout}
        >
          Sair
        </Button>
      </Box>

      <Box flex="1" p={8} overflowY="auto">
        {paginaAtual === 'assets' ? (
          <>
            <Flex justify="space-between" align="center" mb={6}>
              <Heading size="lg">Inventário</Heading>
              <Button leftIcon={<AddIcon />} colorScheme="teal" onClick={handleOpenCreate}>Novo Ativo</Button>
        </Flex>

        <Box bg="white" shadow="sm" borderRadius="lg" p={4} mb={4}>
          <Text fontWeight="bold" mb={3} fontSize="sm">Filtros</Text>
          <VStack spacing={3}>
            <HStack w="full" spacing={2}>
              <FormControl><Input size="sm" placeholder="PAT" value={filtros.pat} onChange={e => setFiltros({...filtros, pat: e.target.value})} /></FormControl>
              <FormControl><Input size="sm" placeholder="Responsável" value={filtros.responsavel} onChange={e => setFiltros({...filtros, responsavel: e.target.value})} /></FormControl>
              <FormControl><Input size="sm" placeholder="Setor" value={filtros.setor} onChange={e => setFiltros({...filtros, setor: e.target.value})} /></FormControl>
              <FormControl><Select size="sm" placeholder="Tipo" value={filtros.tipo} onChange={e => setFiltros({...filtros, tipo: e.target.value})}><option value="">Todos</option><option value="Notebook">Notebook</option><option value="Desktop">Desktop</option></Select></FormControl>
            </HStack>
            <HStack w="full" spacing={2}>
              <FormControl><Input size="sm" placeholder="Equipamento/Hostname" value={filtros.equipamento} onChange={e => setFiltros({...filtros, equipamento: e.target.value})} /></FormControl>
              <FormControl><Input size="sm" placeholder="AnyDesk" value={filtros.anydesk} onChange={e => setFiltros({...filtros, anydesk: e.target.value})} /></FormControl>
              <Button size="sm" variant="outline" colorScheme="gray" onClick={limparFiltros}>Limpar Filtros</Button>
            </HStack>
          </VStack>
          <Text fontSize="xs" color="gray.500" mt={2}>{filtrarAssets().length} de {assets.length} patrimonios</Text>
        </Box>

        <Box bg="white" shadow="sm" borderRadius="lg" overflow="hidden">
          <Table variant="simple" size="sm">
            <Thead bg="gray.100">
              <Tr><Th>Ações</Th><Th>PAT</Th><Th>Colaborador</Th><Th>Setor</Th><Th>Equipamento</Th><Th>AnyDesk</Th><Th>Local</Th></Tr>
            </Thead>
            <Tbody>
              {filtrarAssets().map((asset) => (
                <Tr key={asset._id} _hover={{ bg: "gray.50" }}>
                  <Td><HStack spacing={1}><IconButton icon={<EditIcon />} size="sm" colorScheme="blue" variant="ghost" onClick={() => handleOpenEdit(asset)} /><IconButton icon={<DeleteIcon />} size="sm" colorScheme="red" variant="ghost" onClick={() => handleDelete(asset._id, asset.patrimonio)} /></HStack></Td>
                  <Td fontWeight="bold">{asset.patrimonio}</Td>
                  <Td fontSize="sm">{asset.responsavel || '-'}</Td>
                  <Td><Badge colorScheme="purple" fontSize="xs">{asset.setor || '-'}</Badge></Td>
                  <Td fontSize="sm">{asset.hostname} <Text as="span" fontSize="xs" color="gray.500">({asset.tipo})</Text></Td>
                  <Td fontSize="sm" fontFamily="monospace">{asset.anydesk || '-'}</Td>
                  <Td fontSize="sm">{asset.filial}</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
          </>
        ) : paginaAtual === 'celulares' ? (
          <CelularesComponent usuario={usuario} filiais={filiais} assets={assets} />
        ) : paginaAtual === 'softwares' ? (
          <SoftwaresComponent usuario={usuario} assets={assets} onSoftwareAdded={() => fetchData()} />
        ) : paginaAtual === 'emails' ? (
          <EmailsComponent usuario={usuario} assets={assets} celulares={celulares} />
        ) : paginaAtual === 'logs' ? (
          <Logs />
        ) : paginaAtual === 'usuarios' ? (
          <UsersManagement />
        ) : null}
      </Box>

      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} size="4xl" scrollBehavior="inside">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader bg="teal.600" color="white">{isEditing ? `Editando ${formData.patrimonio}` : 'Novo Cadastro'}</ModalHeader>
          <ModalCloseButton color="white" />
          <ModalBody bg="gray.50" p={0}>
             <Tabs isFitted variant="enclosed">
              <TabList bg="white" pt={2} px={2}>
                <Tab _selected={{ color: 'teal.600', fontWeight:'bold', borderBottom:'none' }}>Geral</Tab>
                <Tab _selected={{ color: 'teal.600', fontWeight:'bold', borderBottom:'none' }}>Rede & Senhas</Tab>
                <Tab _selected={{ color: 'teal.600', fontWeight:'bold', borderBottom:'none' }}>Comunicação</Tab>
                <Tab _selected={{ color: 'teal.600', fontWeight:'bold', borderBottom:'none' }}>Emails</Tab>
                <Tab _selected={{ color: 'teal.600', fontWeight:'bold', borderBottom:'none' }}>Softwares</Tab>
                <Tab _selected={{ color: 'teal.600', fontWeight:'bold', borderBottom:'none' }}>Histórico</Tab>
              </TabList>
              <TabPanels p={6}>
                {/* ABA GERAL */}
                <TabPanel>
                  <VStack spacing={4}>
                    <HStack w="full">
                      <FormControl isRequired><FormLabel>Patrimônio</FormLabel><Input bg="white" value={formData.patrimonio} onChange={e => handleChange('patrimonio', e.target.value)} /></FormControl>
                      <FormControl isRequired><FormLabel>Unidade</FormLabel>
                        <Select bg="white" value={formData.filial} onChange={e => handleChange('filial', e.target.value)}>
                          <option value="">Selecione...</option>
                          {filiais.map(f => <option key={f._id} value={f.nome}>{f.nome}</option>)}
                        </Select>
                      </FormControl>
                      <FormControl isRequired><FormLabel>Setor</FormLabel><Input bg="white" placeholder={formData.filial ? "Selecione ou digite um setor" : "Escolha a Unidade"} value={formData.setor} onChange={e => handleChange('setor', e.target.value)} list="setores-list" isDisabled={!formData.filial} /><datalist id="setores-list">{setoresDisponiveis.map(s => <option key={s} value={s} />)}</datalist></FormControl>
                    </HStack>
                    <HStack w="full">
                        <FormControl isRequired><FormLabel>Responsável</FormLabel><Input bg="white" placeholder={formData.filial ? "Nome do colaborador ou selecione" : "Escolha a Unidade primeiro"} value={formData.responsavel} onChange={e => handleChange('responsavel', e.target.value)} list="responsaveis-list" isDisabled={!formData.filial} /><datalist id="responsaveis-list">{responsaveisDisponiveis.map(r => <option key={r} value={r} />)}</datalist></FormControl>
                        <FormControl><FormLabel>Status</FormLabel><Select bg="white" value={formData.status || 'Em Uso'} onChange={e => handleChange('status', e.target.value)}><option value="Em Uso">Em Uso</option><option value="Reserva">Reserva</option><option value="Manutenção">Manutenção</option></Select></FormControl>
                    </HStack>
                    <HStack w="full">
                      <FormControl><FormLabel>Hostname</FormLabel><Input bg="white" value={formData.hostname} onChange={e => handleChange('hostname', e.target.value)} /></FormControl>
                      <FormControl><FormLabel>Tipo</FormLabel><Select bg="white" value={formData.tipo} onChange={e => handleChange('tipo', e.target.value)}><option value="Notebook">Notebook</option><option value="Desktop">Desktop</option></Select></FormControl>
                      <FormControl><FormLabel>Modelo Hardware</FormLabel><Input bg="white" value={formData.modelo} onChange={e => handleChange('modelo', e.target.value)} /></FormControl>
                    </HStack>
                    <FormControl><FormLabel>Observações</FormLabel><Textarea bg="white" value={formData.obs} onChange={e => handleChange('obs', e.target.value)} /></FormControl>
                  </VStack>
                </TabPanel>

                {/* ABA REDE */}
                <TabPanel>
                  <VStack spacing={4}>
                     <HStack w="full">
                      <FormControl><FormLabel>IP Address</FormLabel><Input bg="white" value={formData.ip} onChange={e => handleChange('ip', e.target.value)} /></FormControl>
                      <FormControl><FormLabel>ID AnyDesk</FormLabel><Input bg="white" value={formData.anydesk} onChange={e => handleChange('anydesk', e.target.value)} /></FormControl>
                      <FormControl><FormLabel>Duapi</FormLabel><Input bg="white" value={formData.duapi} onChange={e => handleChange('duapi', e.target.value)} /></FormControl>
                      <FormControl><FormLabel>Domínio?</FormLabel><Select bg="white" value={formData.dominio} onChange={e => handleChange('dominio', e.target.value)}><option value="Sim">Sim</option><option value="Não">Não</option></Select></FormControl>
                    </HStack>
                    <FormControl><FormLabel>GIX Remoto</FormLabel><Input bg="white" value={formData.gix_remoto} onChange={e => handleChange('gix_remoto', e.target.value)} /></FormControl>
                    <Divider />
                    <HStack w="full">
                        <FormControl><FormLabel>Senha BIOS</FormLabel><InputGroup><Input bg="white" type={showPassword.bios ? 'text' : 'password'} value={formData.senha_bios} onChange={e => handleChange('senha_bios', e.target.value)} /><InputRightElement><IconButton size="sm" variant="ghost" icon={showPassword.bios ? <ViewOffIcon/> : <ViewIcon/>} onClick={() => togglePass('bios')} /></InputRightElement></InputGroup></FormControl>
                        <FormControl><FormLabel>Senha Windows</FormLabel><InputGroup><Input bg="white" type={showPassword.win ? 'text' : 'password'} value={formData.senha_windows} onChange={e => handleChange('senha_windows', e.target.value)} /><InputRightElement><IconButton size="sm" variant="ghost" icon={showPassword.win ? <ViewOffIcon/> : <ViewIcon/>} onClick={() => togglePass('win')} /></InputRightElement></InputGroup></FormControl>
                    </HStack>
                    <HStack w="full">
                        <FormControl><FormLabel>Usuário VPN</FormLabel><Input bg="white" value={formData.vpn_login} onChange={e => handleChange('vpn_login', e.target.value)} /></FormControl>
                        <FormControl><FormLabel>Senha VPN</FormLabel><InputGroup><Input bg="white" type={showPassword.vpn ? 'text' : 'password'} value={formData.senha_vpn} onChange={e => handleChange('senha_vpn', e.target.value)} /><InputRightElement><IconButton size="sm" variant="ghost" icon={showPassword.vpn ? <ViewOffIcon/> : <ViewIcon/>} onClick={() => togglePass('vpn')} /></InputRightElement></InputGroup></FormControl>
                    </HStack>
                  </VStack>
                </TabPanel>

                {/* ABA COMUNICAÇÃO */}
                <TabPanel>
                    <VStack spacing={4}>
                        <FormControl><FormLabel>Email Google</FormLabel><Input bg="white" value={formData.email_google} onChange={e => handleChange('email_google', e.target.value)} /></FormControl>
                        <FormControl><FormLabel>Email Zimbra</FormLabel><Input bg="white" value={formData.email_zimbra} onChange={e => handleChange('email_zimbra', e.target.value)} /></FormControl>
                        
                        <HStack w="full" align="flex-end">
                            <FormControl>
                                <FormLabel>Ramal <PhoneIcon ml={2} color="gray.400" /></FormLabel>
                                <Input bg="white" placeholder="Ex: 2024" value={formData.ramal} onChange={e => handleChange('ramal', e.target.value)} />
                            </FormControl>
                            <FormControl w="auto" pb={2}>
                                <Checkbox 
                                    size="lg" 
                                    colorScheme="teal" 
                                    isChecked={formData.is_softphone} 
                                    onChange={e => handleChange('is_softphone', e.target.checked)}
                                >
                                    Usa Softphone?
                                </Checkbox>
                            </FormControl>
                        </HStack>
                    </VStack>
                </TabPanel>

                {/* ABA EMAILS CORPORATIVOS */}
                <TabPanel>
                  {formData._id ? (
                    <EmailsPatrimonioComponent assetId={formData._id} assetType="workstation" />
                  ) : (
                    <Box p={4} bg="blue.50" borderRadius="md" borderLeft="4px solid" borderLeftColor="blue.500">
                      <Text fontSize="sm" color="blue.700">
                        ℹ️ Salve o patrimônio primeiro para gerenciar os emails corporativos.
                      </Text>
                    </Box>
                  )}
                </TabPanel>

                {/* ABA SOFTWARES VINCULADOS */}
                <TabPanel>
                  {formData._id ? (
                    <SoftwaresPatrimonioComponent assetId={formData._id} onSoftwareAdded={() => fetchData()} />
                  ) : (
                    <Box p={4} bg="blue.50" borderRadius="md" borderLeft="4px solid" borderLeftColor="blue.500">
                      <Text fontSize="sm" color="blue.700">
                        ℹ️ Salve o patrimônio primeiro para vincular softwares.
                      </Text>
                    </Box>
                  )}
                </TabPanel>

                {/* ABA HISTÓRICO DE ALTERAÇÕES */}
                <TabPanel>
                  <AssetDetail asset={formData} onClose={() => {}} onSave={() => {}} />
                </TabPanel>
              </TabPanels>
             </Tabs>
            <Box p={4} bg="gray.100" textAlign="right">
                <Button variant="ghost" mr={3} onClick={() => setIsOpen(false)}>Cancelar</Button>
                <Button colorScheme="teal" onClick={handleSave}>Salvar</Button>
            </Box>
          </ModalBody>
        </ModalContent>
      </Modal>

      <Modal isOpen={modalFilialOpen} onClose={() => setModalFilialOpen(false)} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Gerenciar Unidades</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <Box bg="gray.50" p={4} borderRadius="md" mb={4}>
                <Text fontWeight="bold" mb={2}>Adicionar Nova</Text>
                <HStack>
                    <Input placeholder="Nome (Ex: 01 - Matriz)" bg="white" value={novaFilial.nome} onChange={(e) => setNovaFilial({...novaFilial, nome: e.target.value})} />
                    <Select bg="white" w="180px" value={novaFilial.tipo} onChange={(e) => setNovaFilial({...novaFilial, tipo: e.target.value})}>
                        <option value="Loja">Loja</option>
                        <option value="Administrativo">Administrativo</option>
                        <option value="CD">CD</option>
                    </Select>
                    <Button colorScheme="teal" onClick={handleSaveFilial}>Add</Button>
                </HStack>
            </Box>
            <Divider mb={4} />
            <Text fontWeight="bold" mb={2}>Unidades Cadastradas</Text>
            <Box maxH="300px" overflowY="auto" borderWidth="1px" borderRadius="md">
                <List spacing={0}>
                    {filiais.map((f, index) => (
                        <ListItem key={f._id} display="flex" justifyContent="space-between" alignItems="center" p={2} borderBottom="1px solid #eee" bg={index % 2 === 0 ? "white" : "gray.50"}>
                            <HStack>
                                <ListIcon as={CheckCircleIcon} color="green.500" />
                                <Box>
                                    <Text fontWeight="bold" fontSize="sm">{f.nome}</Text>
                                    <Badge fontSize="xs" colorScheme={f.tipo === 'Administrativo' ? 'purple' : 'gray'}>{f.tipo}</Badge>
                                </Box>
                            </HStack>
                            <IconButton icon={<DeleteIcon />} size="xs" colorScheme="red" variant="ghost" onClick={() => handleDeleteFilial(f._id, f.nome)} />
                        </ListItem>
                    ))}
                </List>
            </Box>
          </ModalBody>
        </ModalContent>
      </Modal>
        </Flex>
      )}
    </>
  );
}

export default App;