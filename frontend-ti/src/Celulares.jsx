import React, { useState, useEffect } from 'react';
import {
  Box, Flex, Heading, Button, Table, Thead, Tbody, Tr, Th, Td,
  Badge, IconButton, useDisclosure, useToast, Select,
  Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalCloseButton,
  FormControl, FormLabel, Input, VStack, HStack, Textarea,
  Text // <--- ADICIONADO AQUI
} from '@chakra-ui/react';
import { AddIcon, EditIcon, DeleteIcon, DownloadIcon, WarningIcon } from '@chakra-ui/icons';
import axios from 'axios';

// Importa o Modal de Importação que criamos
import ImportModal from './components/ImportModal';

const API_URL = 'http://127.0.0.1:5000/api';

const Celulares = ({ usuario }) => {
  const [celulares, setCelulares] = useState([]);
  const [filiais, setFiliais] = useState([]);
  const [filialFiltro, setFilialFiltro] = useState('');
  
  // Estado para o formulário de cadastro/edição
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [isEditing, setIsEditing] = useState(null);
  const [formData, setFormData] = useState({
    patrimonio: '', filial: '', modelo: '', imei: '', imei_2: '',
    numero: '', numero_secundario: '', anydesk: '', conta_google: '',
    marca: '', responsavel: '', status: 'Em Uso', obs: '',
    senha: '', sub_tipo: '', propriedade: '', serial: ''
  });

  // Estado para o Modal de Importação
  const { 
    isOpen: isImportOpen, 
    onOpen: onImportOpen, 
    onClose: onImportClose 
  } = useDisclosure();

  const toast = useToast();

  // Carregar dados iniciais
  const fetchData = async () => {
    try {
      // Busca Celulares (com filtro opcional)
      const params = filialFiltro ? { filial: filialFiltro } : {};
      const resCel = await axios.get(`${API_URL}/celulares`, { params });
      setCelulares(resCel.data);

      // Busca Filiais (para o Select)
      const resFil = await axios.get(`${API_URL}/filiais`);
      setFiliais(resFil.data);
    } catch (error) {
      console.error("Erro ao buscar dados", error);
      toast({ title: 'Erro ao carregar dados', status: 'error' });
    }
  };

  useEffect(() => {
    fetchData();
  }, [filialFiltro]);

  // Handlers do Formulário
  const handleOpenCreate = () => {
    setFormData({
      patrimonio: '', filial: '', modelo: '', imei: '', imei_2: '',
      numero: '', numero_secundario: '', anydesk: '', conta_google: '',
      marca: '', responsavel: '', status: 'Em Uso', obs: '',
      senha: '', sub_tipo: '', propriedade: '', serial: ''
    });
    setIsEditing(null);
    onOpen();
  };

  const handleOpenEdit = (celular) => {
    setFormData({ ...celular });
    setIsEditing(celular.id);
    onOpen();
  };

  const handleSave = async () => {
    try {
      if (isEditing) {
        await axios.put(`${API_URL}/celulares/${isEditing}`, formData);
        toast({ title: 'Celular atualizado!', status: 'success' });
      } else {
        await axios.post(`${API_URL}/celulares`, formData);
        toast({ title: 'Celular cadastrado!', status: 'success' });
      }
      onClose();
      fetchData();
    } catch (error) {
      const msg = error.response?.data?.erro || 'Erro ao salvar';
      toast({ title: 'Erro', description: msg, status: 'error' });
    }
  };

  const handleDelete = async (id, patrimonio, forceHard = false) => {
    const isAdmin = usuario?.permissoes?.includes('admin');
    if (!forceHard && !window.confirm(`Deseja inativar o celular ${patrimonio}?`)) return;
    const hard = forceHard || (isAdmin && window.confirm('Excluir definitivamente? OK = excluir, Cancelar = só inativar'));
    if (hard && !isAdmin) return; // segurança extra no client
    try {
      const url = `${API_URL}/celulares/${id}${hard ? '?hard=true' : ''}`;
      await axios.delete(url, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } });
      toast({ title: hard ? 'Celular excluído' : 'Celular inativado', status: 'info' });
      fetchData();
    } catch (error) {
      const msg = error.response?.data?.erro || 'Erro ao excluir';
      toast({ title: 'Erro', description: msg, status: 'error' });
    }
  };

  // Cores dos Status
  const getStatusColor = (status) => {
    switch (status) {
      case 'Em Uso': return 'green';
      case 'Reserva': return 'blue';
      case 'Manutenção': return 'orange';
      case 'Inativo': return 'red';
      default: return 'gray';
    }
  };

  return (
    <Box p={5}>
      {/* Cabeçalho e Ações */}
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="lg">Celulares Corporativos</Heading>
        <HStack>
          {/* BOTÃO DE IMPORTAR */}
          <Button 
            leftIcon={<DownloadIcon />} 
            variant="outline" 
            colorScheme="blue" 
            onClick={onImportOpen}
          >
            Importar CSV
          </Button>
          
          <Button leftIcon={<AddIcon />} colorScheme="teal" onClick={handleOpenCreate}>
            Novo Celular
          </Button>
        </HStack>
      </Flex>

      {/* Filtro */}
      <Box mb={6} maxW="300px">
        <Select 
          placeholder="Filtrar por Filial" 
          value={filialFiltro} 
          onChange={(e) => setFilialFiltro(e.target.value)}
          bg="white"
        >
          {filiais.map(f => (
            <option key={f.id} value={f.nome}>{f.nome}</option>
          ))}
        </Select>
      </Box>

      {/* Tabela de Listagem */}
      <Box bg="white" shadow="md" borderRadius="lg" overflow="hidden">
        <Table variant="simple">
          <Thead bg="gray.50">
            <Tr>
              <Th>Patrimônio</Th>
              <Th>Filial</Th>
              <Th>Modelo</Th>
              <Th>Linha (Número)</Th>
              <Th>Responsável</Th>
              <Th>Status</Th>
              <Th>Ações</Th>
            </Tr>
          </Thead>
          <Tbody>
            {celulares.map((cel) => (
              <Tr key={cel.id} _hover={{ bg: "gray.50" }}>
                <Td fontWeight="bold">{cel.patrimonio}</Td>
                <Td>{cel.filial}</Td>
                <Td>
                  {cel.modelo}
                  <br/>
                  <Text as="span" fontSize="xs" color="gray.500">IMEI: {cel.imei || '-'}</Text>
                </Td>
                <Td>{cel.numero}</Td>
                <Td>{cel.responsavel}</Td>
                <Td>
                  <Badge colorScheme={getStatusColor(cel.status)}>
                    {cel.status}
                  </Badge>
                </Td>
                <Td>
                  <IconButton 
                    icon={<EditIcon />} 
                    size="sm" 
                    mr={2}
                    colorScheme="blue" 
                    variant="ghost" 
                    onClick={() => handleOpenEdit(cel)} 
                  />
                  <IconButton 
                    icon={<DeleteIcon />} 
                    size="sm" 
                    colorScheme="red" 
                    variant="ghost" 
                    onClick={() => handleDelete(cel.id, cel.patrimonio)} 
                    aria-label="Inativar"
                  />
                  {usuario?.permissoes?.includes('admin') && (
                    <IconButton
                      icon={<WarningIcon />}
                      size="sm"
                      colorScheme="orange"
                      variant="ghost"
                      aria-label="Excluir definitivamente"
                      onClick={() => {
                        if (window.confirm(`Excluir DEFINITIVAMENTE ${cel.patrimonio}? Esta ação não pode ser desfeita.`)) {
                          handleDelete(cel.id, cel.patrimonio, true);
                        }
                      }}
                    />
                  )}
                </Td>
              </Tr>
            ))}
            {celulares.length === 0 && (
              <Tr>
                <Td colSpan={7} textAlign="center" py={4} color="gray.500"> {/* CORRIGIDO PARA colSpan */}
                  Nenhum celular encontrado.
                </Td>
              </Tr>
            )}
          </Tbody>
        </Table>
      </Box>

      {/* Modal de Cadastro/Edição */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{isEditing ? 'Editar Celular' : 'Novo Celular'}</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <VStack spacing={4}>
              <HStack w="full">
                <FormControl isRequired>
                  <FormLabel>Patrimônio</FormLabel>
                  <Input 
                    value={formData.patrimonio} 
                    onChange={e => setFormData({...formData, patrimonio: e.target.value})} 
                  />
                </FormControl>
                <FormControl isRequired>
                  <FormLabel>Filial</FormLabel>
                  <Select 
                    value={formData.filial} 
                    onChange={e => setFormData({...formData, filial: e.target.value})}
                  >
                    <option value="">Selecione...</option>
                    {filiais.map(f => (
                      <option key={f.id} value={f.nome}>{f.nome}</option>
                    ))}
                  </Select>
                </FormControl>
              </HStack>

              <HStack w="full">
                <FormControl>
                  <FormLabel>Marca</FormLabel>
                  <Input 
                    placeholder="Ex: Samsung"
                    value={formData.marca} 
                    onChange={e => setFormData({...formData, marca: e.target.value})} 
                  />
                </FormControl>
                <FormControl>
                  <FormLabel>Modelo</FormLabel>
                  <Input 
                    placeholder="Ex: Galaxy A54"
                    value={formData.modelo} 
                    onChange={e => setFormData({...formData, modelo: e.target.value})} 
                  />
                </FormControl>
                <FormControl>
                  <FormLabel>Sub Tipo</FormLabel>
                  <Input 
                    placeholder="Ex: Smartphone"
                    value={formData.sub_tipo} 
                    onChange={e => setFormData({...formData, sub_tipo: e.target.value})} 
                  />
                </FormControl>
              </HStack>

              <HStack w="full">
                <FormControl>
                  <FormLabel>IMEI 1</FormLabel>
                  <Input 
                    value={formData.imei} 
                    onChange={e => setFormData({...formData, imei: e.target.value})} 
                  />
                </FormControl>
                <FormControl>
                  <FormLabel>IMEI 2</FormLabel>
                  <Input 
                    value={formData.imei_2} 
                    onChange={e => setFormData({...formData, imei_2: e.target.value})} 
                  />
                </FormControl>
                <FormControl>
                  <FormLabel>Serial</FormLabel>
                  <Input 
                    value={formData.serial} 
                    onChange={e => setFormData({...formData, serial: e.target.value})} 
                  />
                </FormControl>
              </HStack>

              <HStack w="full">
                <FormControl>
                  <FormLabel>Nº Principal</FormLabel>
                  <Input 
                    placeholder="(00) 00000-0000"
                    value={formData.numero} 
                    onChange={e => setFormData({...formData, numero: e.target.value})} 
                  />
                </FormControl>
                <FormControl>
                  <FormLabel>Nº Secundário</FormLabel>
                  <Input 
                    placeholder="(00) 00000-0000"
                    value={formData.numero_secundario} 
                    onChange={e => setFormData({...formData, numero_secundario: e.target.value})} 
                  />
                </FormControl>
              </HStack>

              <HStack w="full">
                <FormControl>
                  <FormLabel>Conta Google</FormLabel>
                  <Input 
                    placeholder="usuario@gmail.com"
                    value={formData.conta_google} 
                    onChange={e => setFormData({...formData, conta_google: e.target.value})} 
                  />
                </FormControl>
                <FormControl>
                  <FormLabel>Senha</FormLabel>
                  <Input 
                    type="password"
                    value={formData.senha} 
                    onChange={e => setFormData({...formData, senha: e.target.value})} 
                  />
                </FormControl>
              </HStack>

              <HStack w="full">
                <FormControl>
                  <FormLabel>AnyDesk</FormLabel>
                  <Input 
                    placeholder="123456789"
                    value={formData.anydesk} 
                    onChange={e => setFormData({...formData, anydesk: e.target.value})} 
                  />
                </FormControl>
                <FormControl>
                  <FormLabel>Propriedade</FormLabel>
                  <Input 
                    placeholder="Empresa/Pessoal"
                    value={formData.propriedade} 
                    onChange={e => setFormData({...formData, propriedade: e.target.value})} 
                  />
                </FormControl>
              </HStack>

              <HStack w="full">
                <FormControl>
                  <FormLabel>Status</FormLabel>
                  <Select 
                    value={formData.status} 
                    onChange={e => setFormData({...formData, status: e.target.value})}
                  >
                    <option value="Em Uso">Em Uso</option>
                    <option value="Reserva">Reserva (Estoque)</option>
                    <option value="Manutenção">Manutenção</option>
                    <option value="Inativo">Inativo / Baixado</option>
                  </Select>
                </FormControl>
                <FormControl>
                  <FormLabel>Responsável</FormLabel>
                  <Input 
                    value={formData.responsavel} 
                    onChange={e => setFormData({...formData, responsavel: e.target.value})} 
                  />
                </FormControl>
              </HStack>

              <FormControl>
                <FormLabel>Observações</FormLabel>
                <Textarea 
                  value={formData.obs} 
                  onChange={e => setFormData({...formData, obs: e.target.value})} 
                />
              </FormControl>

              <Button colorScheme="teal" w="full" onClick={handleSave}>
                Salvar
              </Button>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>

      {/* Modal de Importação (Reutilizável) */}
      <ImportModal 
        isOpen={isImportOpen} 
        onClose={onImportClose} 
        type="celulares" 
        onSuccess={fetchData} 
      />

    </Box>
  );
};

export default Celulares;