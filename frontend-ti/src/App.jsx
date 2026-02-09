import React, { useState, useEffect, useMemo } from 'react';
import { 
  Box, Flex, Heading, Text, Button, Table, Thead, Tbody, Tr, Th, Td, 
  Badge, Input, Select, useToast, Modal, ModalOverlay, ModalContent, 
  ModalHeader, ModalBody, ModalCloseButton, FormControl, FormLabel,
  VStack, HStack, IconButton, Tabs, TabList, TabPanels, Tab, TabPanel,
  Textarea, InputGroup, InputRightElement, Divider, Avatar, Tooltip,
  Checkbox, List, ListItem, ListIcon, useDisclosure
} from '@chakra-ui/react';
import { 
  AddIcon, EditIcon, DeleteIcon, ViewIcon, ViewOffIcon, SettingsIcon, 
  SearchIcon, RepeatIcon, SmallCloseIcon, PhoneIcon, CheckCircleIcon, WarningIcon, DownloadIcon
} from '@chakra-ui/icons';
import { FaLaptop, FaMobileAlt, FaEnvelope, FaSave, FaClipboardList, FaUsers } from 'react-icons/fa';
import axios from 'axios';

// Componentes
import Login from './Login';
import Logs from './Logs';
import UsersManagement from './UsersManagement';
import CelularesComponent from './Celulares';
import SoftwaresComponent from './Softwares';
import EmailsComponent from './Emails';
import ImportModal from './components/ImportModal';

const API_URL = 'http://127.0.0.1:5000/api';

const SETORES_POR_TIPO = {
  'Administrativo': ['Análise de Crédito', 'Auxiliar Televendas', 'Cadastro', 'Cadastro de Produto', 'Cobrança', 'Comercial', 'Compras', 'Contabil / Fiscal', 'Controladoria', 'Controle de Estoque', 'Dep. Pessoal', 'Direção', 'Ecommerce', 'Financeiro', 'Garantia', 'Gerente Televendas', 'Liberação de Pedido / Depósito', 'Logística', 'Marketing', 'Negociação', 'Pricing', 'Projeto', 'RH', 'Servidor', 'TI', 'Televendas'].sort(),
  'Loja': ['Balcão', 'Caixa', 'Conferência', 'Estoque', 'Faturamento', 'Gerente Loja', 'Recebimento', 'Servidor', 'Televendas', 'Televendas Loja', 'Vendas', 'Vendas Ar', 'Vendas WhatsApp'].sort(),
  'CD': ['Assistente Inventário', 'Conferência', 'Doca', 'Estoque', 'Expedição', 'Faturamento', 'Garantia', 'Gerente CD', 'Organização', 'Recebimento', 'Servidor'].sort()
};

const initialFormState = {
  patrimonio: '', filial: '', setor: '', responsavel: '', hostname: '', tipo: 'Notebook', modelo: '', obs: '',
  ip: '', anydesk: '', duapi: '', dominio: 'Não', senha_bios: '', senha_windows: '', vpn_login: '', senha_vpn: '', gix_remoto: '',
  ramal: '', is_softphone: false
};

// Componente Botão Sidebar
const SidebarBtn = ({ label, icon, id, paginaAtual, setPaginaAtual, color = "teal" }) => (
  <Button
    w="full" justifyContent="flex-start" variant="ghost"
    color={paginaAtual === id ? `${color}.300` : "gray.400"}
    bg={paginaAtual === id ? "whiteAlpha.100" : "transparent"}
    borderLeft={paginaAtual === id ? `4px solid` : "4px solid transparent"}
    borderColor={`${color}.300`}
    _hover={{ bg: 'whiteAlpha.200', color: 'white' }}
    leftIcon={icon} onClick={() => setPaginaAtual(id)}
    size="lg" fontWeight={paginaAtual === id ? "bold" : "normal"} mb={1}
  >
    {label}
  </Button>
);

function App() {
  const [usuario, setUsuario] = useState(null);
  const [paginaAtual, setPaginaAtual] = useState('assets');
  
  // --- DADOS COMPLETOS ---
  const [assets, setAssets] = useState([]);
  const [filiais, setFiliais] = useState([]);
  const [celulares, setCelulares] = useState([]);
  const [emails, setEmails] = useState([]);     // <--- RESTAURADO
  const [softwares, setSoftwares] = useState([]); // <--- RESTAURADO
  const [lastUpdate, setLastUpdate] = useState(new Date());
  
  const [filiaisFiltro, setFiliaisFiltro] = useState('');
  const [filtros, setFiltros] = useState({ pat: '', responsavel: '', setor: '', equipamento: '', anydesk: '', tipo: '' });
  
  const [isOpen, setIsOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(null);
  const [modalFilialOpen, setModalFilialOpen] = useState(false);
  const { 
    isOpen: isImportOpen, 
    onOpen: onImportOpen, 
    onClose: onImportClose 
  } = useDisclosure();
  const [formData, setFormData] = useState(initialFormState);
  const [novaFilial, setNovaFilial] = useState({ nome: '', tipo: 'Loja' });
  const [showPassword, setShowPassword] = useState({});
  const [respMenuOpen, setRespMenuOpen] = useState(false);
  const [setoresDisponiveis, setSetoresDisponiveis] = useState([]);
  const [responsaveisDisponiveis, setResponsaveisDisponiveis] = useState([]);

  const toast = useToast();

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userStored = localStorage.getItem('usuario');
    if (token && userStored) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setUsuario(JSON.parse(userStored));
    }
  }, []);

  const handleLoginSuccess = (userData) => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setUsuario(userData);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('usuario');
    setUsuario(null);
  };

  const fetchData = async (silent = false) => {
    if (!usuario) return;
    try {
      const resF = await axios.get(`${API_URL}/filiais`);
      setFiliais(resF.data);

      if (paginaAtual === 'assets' || paginaAtual === 'emails' || paginaAtual === 'softwares') {
        const params = filiaisFiltro ? { filial: filiaisFiltro } : {};
        const resA = await axios.get(`${API_URL}/assets`, { params });
        setAssets(resA.data.filter(a => a.status !== 'Inativo'));
      }

      // Busca dados secundários para popular as abas
      const resC = await axios.get(`${API_URL}/celulares`);
      setCelulares(resC.data.filter(c => c.status !== 'Inativo'));

      const resE = await axios.get(`${API_URL}/emails`);
      setEmails(resE.data.filter(e => e.status !== 'Inativo'));

      const resS = await axios.get(`${API_URL}/softwares`);
      setSoftwares(resS.data.filter(s => s.status !== 'Inativo'));
      
      setLastUpdate(new Date());
    } catch (error) {
      if (error.response?.status === 401) handleLogout();
    }
  };

  useEffect(() => {
    fetchData();
    const intervalId = setInterval(() => {
      if (!isOpen && !modalFilialOpen) fetchData(true);
    }, 5000);
    return () => clearInterval(intervalId);
  }, [usuario, paginaAtual, filiaisFiltro, isOpen]);

  // Socket.IO removido - não implementado no backend
  // Usando polling a cada 5 segundos como mecanismo de sincronização

  const filteredAssets = useMemo(() => {
    return assets.filter(asset => {
      if (filtros.pat && !asset.patrimonio?.toLowerCase().includes(filtros.pat.toLowerCase())) return false;
      if (filtros.responsavel && !asset.responsavel?.toLowerCase().includes(filtros.responsavel.toLowerCase())) return false;
      if (filtros.setor && !asset.setor?.toLowerCase().includes(filtros.setor.toLowerCase())) return false;
      if (filtros.equipamento && !asset.hostname?.toLowerCase().includes(filtros.equipamento.toLowerCase())) return false;
      if (filtros.anydesk && !asset.anydesk?.toLowerCase().includes(filtros.anydesk.toLowerCase())) return false;
      if (filtros.tipo && asset.tipo !== filtros.tipo) return false;
      return true;
    });
  }, [assets, filtros]);

  const responsaveisFiltrados = useMemo(() => {
    const termo = (formData.responsavel || '').toLowerCase();
    return responsaveisDisponiveis
      .filter(r => r.toLowerCase().includes(termo))
      .slice(0, 20);
  }, [responsaveisDisponiveis, formData.responsavel]);

  const handleOpenCreate = () => { setFormData(initialFormState); setIsEditing(null); setIsOpen(true); };
  const handleOpenEdit = (asset) => { setFormData({ ...initialFormState, ...asset }); setIsEditing(asset.id); setIsOpen(true); };
  
  const handleSave = async () => {
    try {
      if (isEditing) await axios.put(`${API_URL}/assets/${isEditing}`, formData);
      else await axios.post(`${API_URL}/assets`, formData);
      toast({ title: 'Salvo!', status: 'success', duration: 2000 });
      setIsOpen(false); 
      fetchData();
    } catch (error) { toast({ title: 'Erro', status: 'error' }); }
  };

  const handleDelete = async (id, pat, forceHard = false) => {
    if (!forceHard && !window.confirm(`Inativar ${pat}?`)) return;
    const hard = forceHard || window.confirm('Deseja excluir definitivamente? OK = Excluir, Cancelar = Apenas inativar');
    try {
      const url = `${API_URL}/assets/${id}${hard ? '?hard=true' : ''}`;
      await axios.delete(url);
      toast({ title: hard ? 'Excluído' : 'Inativado', status: 'info', duration: 2000 });
      fetchData();
    } catch(e){ toast({ title: 'Erro ao excluir/inativar', status: 'error' }); }
  };

  const handleSaveFilial = async () => {
    if (!novaFilial.nome) return;
    try {
      await axios.post(`${API_URL}/filiais`, novaFilial);
      toast({ title: 'Unidade Criada!', status: 'success' });
      setNovaFilial({ nome: '', tipo: 'Loja' });
      setModalFilialOpen(false);
      fetchData();
    } catch (error) { toast({ title: 'Erro - Talvez já exista?', status: 'error' }); }
  };

  const handleChange = (f, v) => setFormData(p => ({...p, [f]: v}));
  const togglePass = (f) => setShowPassword(p => ({...p, [f]: !p[f]}));

  useEffect(() => {
    if (formData.filial) {
      const fObj = filiais.find(f => f.nome === formData.filial);
      if (fObj && fObj.tipo) {
        let setores = SETORES_POR_TIPO[fObj.tipo] || [];
        setSetoresDisponiveis(setores);
      } else {
        setSetoresDisponiveis([]);
      }

      const fetchResponsaveis = async () => {
        try {
          const encodedFilial = encodeURIComponent(formData.filial);
          const res = await axios.get(`${API_URL}/funcionarios/${encodedFilial}`);
          setResponsaveisDisponiveis(res.data);
        } catch (error) {
          const respsLocais = [...new Set(
            assets.filter(a => a.filial === formData.filial).map(a => a.responsavel)
          )].filter(Boolean).sort();
          setResponsaveisDisponiveis(respsLocais);
        }
      };
      fetchResponsaveis();
      
    } else {
      setSetoresDisponiveis([]);
      setResponsaveisDisponiveis([]);
    }
  }, [formData.filial, filiais]);

  if (!usuario) return <Login onLoginSuccess={handleLoginSuccess} />;

  return (
    <Flex h="100vh" overflow="hidden">
      <Box w="260px" bgGradient="linear(to-b, gray.900, gray.800)" color="white" display="flex" flexDirection="column" boxShadow="2xl" zIndex={10}>
        <Flex p={6} align="center" borderBottom="1px solid" borderColor="whiteAlpha.100" mb={4}>
          <Box p={2} bg="teal.500" borderRadius="md" mr={3}><SettingsIcon boxSize={5} color="white" /></Box>
          <Box><Heading size="sm" letterSpacing="wide">TI MANAGER</Heading><Text fontSize="xs" color="gray.400">v2.1 • Online</Text></Box>
        </Flex>
        <VStack align="stretch" spacing={1} flex="1" px={3}>
          <Text fontSize="xs" fontWeight="bold" color="gray.500" px={3} mb={2} mt={2}>GESTÃO</Text>
          <SidebarBtn id="assets" label="Computadores" icon={<FaLaptop />} paginaAtual={paginaAtual} setPaginaAtual={setPaginaAtual} />
          <SidebarBtn id="celulares" label="Celulares" icon={<FaMobileAlt />} paginaAtual={paginaAtual} setPaginaAtual={setPaginaAtual} />
          <SidebarBtn id="softwares" label="Softwares" icon={<FaSave />} paginaAtual={paginaAtual} setPaginaAtual={setPaginaAtual} />
          <SidebarBtn id="emails" label="Emails" icon={<FaEnvelope />} paginaAtual={paginaAtual} setPaginaAtual={setPaginaAtual} />
          {usuario.permissoes?.includes('admin') && (
            <>
              <Text fontSize="xs" fontWeight="bold" color="gray.500" px={3} mb={2} mt={6}>ADMINISTRAÇÃO</Text>
              <SidebarBtn id="logs" label="Auditoria" icon={<FaClipboardList />} paginaAtual={paginaAtual} setPaginaAtual={setPaginaAtual} color="orange" />
              <SidebarBtn id="usuarios" label="Usuários" icon={<FaUsers />} paginaAtual={paginaAtual} setPaginaAtual={setPaginaAtual} color="purple" />
            </>
          )}
        </VStack>
        <Box p={4} bg="blackAlpha.300" borderTop="1px solid" borderColor="whiteAlpha.100">
          <Flex align="center" mb={3}>
            <Avatar size="sm" name={usuario.nome} bg="teal.500" mr={3} />
            <Box flex="1"><Text fontSize="sm" fontWeight="bold" isTruncated>{usuario.nome}</Text><Badge colorScheme="teal" fontSize="xx-small">{usuario.filial}</Badge></Box>
            <Tooltip label="Sair"><IconButton icon={<SmallCloseIcon />} size="xs" colorScheme="red" variant="ghost" onClick={handleLogout} /></Tooltip>
          </Flex>
          {paginaAtual === 'assets' && (
             <Select size="xs" variant="filled" bg="gray.700" color="gray.300" _hover={{ bg: 'gray.600' }} value={filiaisFiltro} onChange={e => setFiliaisFiltro(e.target.value)}>
                <option value="">Todas as Filiais</option>
                {filiais.map(f => <option key={f.id} value={f.nome}>{f.nome}</option>)}
             </Select>
          )}
        </Box>
      </Box>

      <Box flex="1" bg="gray.50" overflowY="auto" p={6}>
        <Flex justify="space-between" align="center" mb={6}>
          <Box>
            <Heading size="lg" color="gray.700">
              {paginaAtual === 'assets' && "Inventário de Ativos"}
              {paginaAtual === 'celulares' && "Dispositivos Móveis"}
              {paginaAtual === 'softwares' && "Gestão de Licenças"}
              {paginaAtual === 'emails' && "Contas de E-mail"}
              {paginaAtual === 'logs' && "Logs de Auditoria"}
              {paginaAtual === 'usuarios' && "Controle de Acesso"}
            </Heading>
            <Text fontSize="xs" color="gray.400" mt={1}>Última atualização: {lastUpdate.toLocaleTimeString()} (Tempo Real)</Text>
          </Box>
          {paginaAtual === 'assets' && (
             <HStack>
               <Button leftIcon={<SettingsIcon />} variant="outline" onClick={() => setModalFilialOpen(true)}>Unidades</Button>
               <Button leftIcon={<DownloadIcon />} colorScheme="green" variant="outline" onClick={onImportOpen}>Importar CSV</Button>
               <Button leftIcon={<AddIcon />} colorScheme="teal" onClick={handleOpenCreate}>Novo Ativo</Button>
             </HStack>
          )}
        </Flex>

        {paginaAtual === 'assets' ? (
          <>
            <Box bg="white" p={4} borderRadius="lg" shadow="sm" mb={6} border="1px solid" borderColor="gray.100">
              <HStack spacing={3}>
                <InputGroup size="sm">
                  <InputRightElement pointerEvents="none"><SearchIcon color="gray.300" /></InputRightElement>
                  <Input placeholder="Buscar PAT..." value={filtros.pat} onChange={e => setFiltros({...filtros, pat: e.target.value})} />
                </InputGroup>
                <Input size="sm" placeholder="Responsável" value={filtros.responsavel} onChange={e => setFiltros({...filtros, responsavel: e.target.value})} />
                <Input size="sm" placeholder="Setor" value={filtros.setor} onChange={e => setFiltros({...filtros, setor: e.target.value})} />
                <Select size="sm" placeholder="Tipo" value={filtros.tipo} onChange={e => setFiltros({...filtros, tipo: e.target.value})} w="150px">
                   <option key="tipo-todos" value="">Todos</option>
                   <option key="tipo-notebook" value="Notebook">Notebook</option>
                   <option key="tipo-desktop" value="Desktop">Desktop</option>
                </Select>
                <IconButton aria-label="Limpar" icon={<RepeatIcon />} size="sm" onClick={() => setFiltros({pat: '', responsavel: '', setor: '', equipamento: '', anydesk: '', tipo: ''})} />
              </HStack>
            </Box>
            <Box bg="white" shadow="sm" borderRadius="lg" overflow="hidden" border="1px solid" borderColor="gray.100">
              <Table variant="simple" size="sm" sx={{'th': {fontSize: 'xs', textTransform: 'uppercase', color: 'gray.500'}}}>
                <Thead bg="gray.50">
                  <Tr><Th>Ações</Th><Th>PAT</Th><Th>Colaborador</Th><Th>Setor</Th><Th>Equipamento</Th><Th>AnyDesk</Th><Th>Local</Th></Tr>
                </Thead>
                <Tbody>
                  {filteredAssets.map((asset) => (
                    <Tr key={asset.id} _hover={{ bg: "teal.50", transition: "0.2s" }}>
                      <Td>
                        <HStack spacing={1}>
                          <IconButton icon={<EditIcon />} size="xs" colorScheme="blue" variant="solid" onClick={() => handleOpenEdit(asset)} />
                          <IconButton
                            icon={<DeleteIcon />}
                            size="xs"
                            colorScheme="red"
                            variant="ghost"
                            onClick={() => handleDelete(asset.id, asset.patrimonio)}
                            aria-label="Inativar ou excluir"
                          />
                          <IconButton
                            icon={<WarningIcon />}
                            size="xs"
                            colorScheme="orange"
                            variant="ghost"
                            title="Excluir definitivamente"
                            onClick={() => {
                              const hard = window.confirm(`Excluir DEFINITIVAMENTE ${asset.patrimonio}? Esta ação não pode ser desfeita.`);
                              if (!hard) return;
                              handleDelete(asset.id, asset.patrimonio, true);
                            }}
                          />
                        </HStack>
                      </Td>
                      <Td fontWeight="bold" color="teal.700">{asset.patrimonio}</Td>
                      <Td fontWeight="medium">{asset.responsavel}</Td>
                      <Td><Badge variant="subtle" colorScheme="purple">{asset.setor}</Badge></Td>
                      <Td>{asset.hostname} <Text as="span" fontSize="xs" color="gray.400">({asset.tipo})</Text></Td>
                      <Td fontFamily="monospace" fontSize="xs">{asset.anydesk || '-'}</Td>
                      <Td fontSize="xs" color="gray.500">{asset.filial}</Td>
                    </Tr>
                  ))}
                  {filteredAssets.length === 0 && <Tr><Td colSpan={7} textAlign="center" py={6} color="gray.400">Nenhum ativo encontrado.</Td></Tr>}
                </Tbody>
              </Table>
            </Box>
          </>
        ) : paginaAtual === 'celulares' ? (
          <CelularesComponent usuario={usuario} filiais={filiais} assets={assets} />
        ) : paginaAtual === 'softwares' ? (
          <SoftwaresComponent usuario={usuario} assets={assets} />
        ) : paginaAtual === 'emails' ? (
          <EmailsComponent usuario={usuario} assets={assets} celulares={celulares} />
        ) : paginaAtual === 'logs' ? (
          <Logs />
        ) : paginaAtual === 'usuarios' ? (
          <UsersManagement />
        ) : null}
      </Box>

      {/* MODAL DE ATIVOS COMPLETO */}
      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} size="4xl" scrollBehavior="inside">
        <ModalOverlay backdropFilter="blur(5px)" />
        <ModalContent>
          <ModalHeader bg="teal.600" color="white" borderTopRadius="md">{isEditing ? `Editando ${formData.patrimonio}` : 'Novo Ativo'}</ModalHeader>
          <ModalCloseButton color="white" />
          <ModalBody bg="gray.50" p={0}>
             <Tabs isFitted variant="enclosed" colorScheme="teal">
              <TabList bg="white" pt={2} px={2} borderBottom="1px solid" borderColor="gray.200">
                <Tab _selected={{ color: 'teal.600', fontWeight:'bold', borderBottom:'2px solid teal' }}>Geral</Tab>
                <Tab _selected={{ color: 'teal.600', fontWeight:'bold', borderBottom:'2px solid teal' }}>Rede & Acesso</Tab>
                <Tab _selected={{ color: 'teal.600', fontWeight:'bold', borderBottom:'2px solid teal' }}>Comunicação</Tab>
                <Tab _selected={{ color: 'teal.600', fontWeight:'bold', borderBottom:'2px solid teal' }}>E-mails</Tab>
                <Tab _selected={{ color: 'teal.600', fontWeight:'bold', borderBottom:'2px solid teal' }}>Softwares</Tab>
              </TabList>
              <TabPanels p={6}>
                <TabPanel>
                  <VStack spacing={5}>
                    <HStack w="full">
                      <FormControl isRequired><FormLabel>Patrimônio</FormLabel><Input bg="white" value={formData.patrimonio || ''} onChange={e => handleChange('patrimonio', e.target.value)} borderColor="gray.300" _hover={{borderColor: 'teal.400'}} /></FormControl>
                      <FormControl isRequired><FormLabel>Unidade</FormLabel>
                        <Select bg="white" value={formData.filial || ''} onChange={e => handleChange('filial', e.target.value)}>
                          <option value="">Selecione...</option>
                          {filiais.map(f => <option key={f.id} value={f.nome}>{f.nome}</option>)}
                        </Select>
                      </FormControl>
                      <FormControl isRequired>
                        <FormLabel>Setor</FormLabel>
                        <Select bg="white" placeholder={formData.filial ? "Selecione o Setor" : "Selecione a Unidade primeiro"} value={formData.setor || ''} onChange={e => handleChange('setor', e.target.value)} isDisabled={!formData.filial}>
                          {setoresDisponiveis.map(s => <option key={s} value={s}>{s}</option>)}
                        </Select>
                      </FormControl>
                    </HStack>
                    <HStack w="full">
                        <FormControl isRequired position="relative">
                          <FormLabel>Responsável</FormLabel>
                          <Input
                            bg="white"
                            value={formData.responsavel || ''}
                            onChange={e => handleChange('responsavel', e.target.value)}
                            onFocus={() => setRespMenuOpen(true)}
                            onBlur={() => setTimeout(() => setRespMenuOpen(false), 120)}
                            placeholder="Digite para filtrar"
                          />
                          {respMenuOpen && responsaveisFiltrados.length > 0 && (
                            <Box
                              position="absolute"
                              zIndex={10}
                              top="100%"
                              left={0}
                              right={0}
                              bg="white"
                              borderWidth="1px"
                              borderRadius="md"
                              shadow="md"
                              mt={1}
                              maxH="240px"
                              overflowY="auto"
                            >
                              {responsaveisFiltrados.map(r => (
                                <Box
                                  as="button"
                                  type="button"
                                  key={r}
                                  w="full"
                                  textAlign="left"
                                  px={3}
                                  py={2}
                                  _hover={{ bg: 'gray.100' }}
                                  onMouseDown={() => {
                                    handleChange('responsavel', r);
                                    setRespMenuOpen(false);
                                  }}
                                >
                                  {r}
                                </Box>
                              ))}
                            </Box>
                          )}
                        </FormControl>
                        <FormControl>
                          <FormLabel>Status</FormLabel>
                          <Select bg="white" value={formData.status || 'Em Uso'} onChange={e => handleChange('status', e.target.value)}>
                            <option key="status-em-uso" value="Em Uso">Em Uso</option>
                            <option key="status-reserva" value="Reserva">Reserva</option>
                            <option key="status-manutencao" value="Manutenção">Manutenção</option>
                          </Select>
                        </FormControl>
                    </HStack>
                    <Divider />
                    <HStack w="full">
                      <FormControl><FormLabel>Hostname</FormLabel><Input bg="white" value={formData.hostname || ''} onChange={e => handleChange('hostname', e.target.value)} /></FormControl>
                      <FormControl>
                        <FormLabel>Tipo</FormLabel>
                        <Select bg="white" value={formData.tipo || 'Desktop'} onChange={e => handleChange('tipo', e.target.value)}>
                          <option key="tipo-notebook" value="Notebook">Notebook</option>
                          <option key="tipo-desktop" value="Desktop">Desktop</option>
                        </Select>
                      </FormControl>
                      <FormControl><FormLabel>Modelo</FormLabel><Input bg="white" value={formData.modelo || ''} onChange={e => handleChange('modelo', e.target.value)} /></FormControl>
                    </HStack>
                    <FormControl><FormLabel>Observações</FormLabel><Textarea bg="white" value={formData.obs || ''} onChange={e => handleChange('obs', e.target.value)} /></FormControl>
                  </VStack>
                </TabPanel>
                <TabPanel>
                  <VStack spacing={4}>
                     <HStack w="full">
                      <FormControl><FormLabel>IP Address</FormLabel><Input bg="white" value={formData.ip || ''} onChange={e => handleChange('ip', e.target.value)} /></FormControl>
                      <FormControl><FormLabel>AnyDesk ID</FormLabel><Input bg="white" value={formData.anydesk || ''} onChange={e => handleChange('anydesk', e.target.value)} /></FormControl>
                      <FormControl>
                        <FormLabel>Domínio?</FormLabel>
                        <Select bg="white" value={formData.dominio || 'Não'} onChange={e => handleChange('dominio', e.target.value)}>
                          <option key="dominio-sim" value="Sim">Sim</option>
                          <option key="dominio-nao" value="Não">Não</option>
                        </Select>
                      </FormControl>
                    </HStack>
                    <Divider />
                    <HStack w="full">
                        <FormControl><FormLabel>Senha BIOS</FormLabel><InputGroup><Input bg="white" type={showPassword.bios ? 'text' : 'password'} value={formData.senha_bios || ''} onChange={e => handleChange('senha_bios', e.target.value)} /><InputRightElement><IconButton size="sm" variant="ghost" icon={showPassword.bios ? <ViewOffIcon/> : <ViewIcon/>} onClick={() => togglePass('bios')} /></InputRightElement></InputGroup></FormControl>
                        <FormControl><FormLabel>Senha Windows</FormLabel><InputGroup><Input bg="white" type={showPassword.win ? 'text' : 'password'} value={formData.senha_windows || ''} onChange={e => handleChange('senha_windows', e.target.value)} /><InputRightElement><IconButton size="sm" variant="ghost" icon={showPassword.win ? <ViewOffIcon/> : <ViewIcon/>} onClick={() => togglePass('win')} /></InputRightElement></InputGroup></FormControl>
                    </HStack>
                  </VStack>
                </TabPanel>
                <TabPanel>
                    <VStack spacing={4}>
                        <HStack w="full" align="flex-end">
                            <FormControl>
                                <FormLabel>Ramal <PhoneIcon ml={2} color="gray.400" /></FormLabel>
                                <Input bg="white" placeholder="Ex: 2024" value={formData.ramal || ''} onChange={e => handleChange('ramal', e.target.value)} />
                            </FormControl>
                            <FormControl w="auto" pb={2}>
                                <Checkbox size="lg" colorScheme="teal" isChecked={formData.is_softphone} onChange={e => handleChange('is_softphone', e.target.checked)}>Usa Softphone?</Checkbox>
                            </FormControl>
                        </HStack>
                    </VStack>
                </TabPanel>
                
                {/* --- ABA EMAILS --- */}
                <TabPanel>
                  {isEditing ? (
                    <List spacing={3}>
                      {emails.filter(e => e.asset_id === isEditing).map(e => (
                        <ListItem key={e.id} display="flex" alignItems="center">
                          <ListIcon as={FaEnvelope} color="teal.500" />
                          <Box>
                            <Text fontWeight="bold">{e.endereco}</Text>
                            <Badge fontSize="xs" colorScheme={e.tipo === 'google' ? 'red' : 'purple'}>{e.tipo}</Badge>
                            <HStack spacing={2} mt={1} align="center">
                              <Text fontSize="sm" color="gray.600">
                                Senha: {showPassword[`email_${e.id}`] ? (e.senha || '—') : '••••••'}
                              </Text>
                              {e.senha && (
                                <IconButton
                                  aria-label="Ver senha"
                                  size="xs"
                                  variant="ghost"
                                  icon={showPassword[`email_${e.id}`] ? <ViewOffIcon /> : <ViewIcon />}
                                  onClick={() => togglePass(`email_${e.id}`)}
                                />
                              )}
                            </HStack>
                          </Box>
                        </ListItem>
                      ))}
                      {emails.filter(e => e.asset_id === isEditing).length === 0 && <Text fontSize="sm" color="gray.500">Nenhum email vinculado.</Text>}
                    </List>
                  ) : (
                    <Text fontSize="sm" color="gray.500">Salve o ativo primeiro para visualizar e-mails vinculados.</Text>
                  )}
                </TabPanel>
                
                {/* --- ABA SOFTWARES --- */}
                <TabPanel>
                  {isEditing ? (
                    <Table size="sm" variant="simple">
                      <Thead><Tr><Th>Software</Th><Th>Licença</Th><Th>Vencimento</Th></Tr></Thead>
                      <Tbody>
                        {softwares.filter(s => s.asset_id === isEditing).map(s => (
                          <Tr key={s.id}><Td>{s.nome}</Td><Td>{s.tipo_licenca}</Td><Td>{s.dt_vencimento ? new Date(s.dt_vencimento).toLocaleDateString() : '-'}</Td></Tr>
                        ))}
                        {softwares.filter(s => s.asset_id === isEditing).length === 0 && <Tr><Td colSpan={3}>Nenhum software vinculado.</Td></Tr>}
                      </Tbody>
                    </Table>
                  ) : (
                    <Text fontSize="sm" color="gray.500">Salve o ativo primeiro para visualizar softwares vinculados.</Text>
                  )}
                </TabPanel>

              </TabPanels>
             </Tabs>
            <Box p={4} bg="gray.100" textAlign="right" borderTop="1px solid" borderColor="gray.200">
                <Button variant="ghost" mr={3} onClick={() => setIsOpen(false)}>Cancelar</Button>
                <Button colorScheme="teal" onClick={handleSave} leftIcon={<FaSave />}>Salvar Dados</Button>
            </Box>
          </ModalBody>
        </ModalContent>
      </Modal>

      <Modal isOpen={modalFilialOpen} onClose={() => setModalFilialOpen(false)}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Gerenciar Unidades</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
             <Text mb={2}>Adicionar nova unidade:</Text>
             <HStack mb={4}>
                <Input placeholder="Nome" value={novaFilial.nome} onChange={e => setNovaFilial({...novaFilial, nome: e.target.value})} />
                <Select w="150px" value={novaFilial.tipo} onChange={e => setNovaFilial({...novaFilial, tipo: e.target.value})}>
                    <option key="tipo-loja" value="Loja">Loja</option>
                    <option key="tipo-admin" value="Administrativo">Admin</option>
                    <option key="tipo-cd" value="CD">CD</option>
                </Select>
                <Button onClick={handleSaveFilial}>Add</Button>
             </HStack>
          </ModalBody>
        </ModalContent>
      </Modal>

      <ImportModal 
        isOpen={isImportOpen}
        onClose={onImportClose}
        type="assets"
        onSuccess={() => {
          fetchData();
          onImportClose();
        }}
      />
    </Flex>
  );
}

export default App;