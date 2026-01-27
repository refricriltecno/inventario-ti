import React, { useState, useEffect } from 'react';
import {
  Box, Button, Table, Thead, Tbody, Tr, Th, Td, Badge, IconButton,
  Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalCloseButton,
  ModalFooter, FormControl, FormLabel, Input, Select, VStack, HStack,
  useToast, Text, InputGroup, InputRightElement, Divider, Tabs, TabList, TabPanels, Tab, TabPanel,
  useDisclosure // <--- Adicionado
} from '@chakra-ui/react';
import { AddIcon, EditIcon, DeleteIcon, ViewIcon, ViewOffIcon, DownloadIcon } from '@chakra-ui/icons'; // <--- DownloadIcon
import axios from 'axios';
import ImportModal from './components/ImportModal'; // <--- Import Component

const API_URL = 'http://127.0.0.1:5000/api';

const initialEmailState = {
  endereco: '',
  tipo: 'google',
  asset_id: '',
  asset_type: 'workstation',
  usuario: '',
  senha: '',
  recuperacao: '',
  data_criacao: '',
  status: 'Ativo',
  obs: ''
};

function EmailsComponent({ usuario, assets, celulares }) {
  const [emails, setEmails] = useState([]);
  
  // Controle do Modal de Cadastro/Edição
  const [isOpen, setIsOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(null);
  const [formData, setFormData] = useState(initialEmailState);
  const [showPassword, setShowPassword] = useState({});
  
  // Filtros
  const [filtroTipo, setFiltroTipo] = useState('');
  const [filtroPatrimonio, setFiltroPatrimonio] = useState('');
  
  // Controle do Modal de Importação (NOVO)
  const { 
    isOpen: isImportOpen, 
    onOpen: onImportOpen, 
    onClose: onImportClose 
  } = useDisclosure();

  const toast = useToast();

  useEffect(() => {
    fetchEmails();
  }, [filtroTipo, filtroPatrimonio]);

  const fetchEmails = async () => {
    try {
      const token = localStorage.getItem('token');
      const params = {};
      if (filtroTipo) params.tipo = filtroTipo;
      
      const response = await axios.get(`${API_URL}/emails`, {
        params,
        headers: { Authorization: `Bearer ${token}` }
      });
      
      let emailsFiltrados = response.data.filter(e => e.status !== 'Inativo');
      
      if (filtroPatrimonio) {
        emailsFiltrados = emailsFiltrados.filter(e => e.asset_id === filtroPatrimonio);
      }
      
      setEmails(emailsFiltrados);
    } catch (error) {
      toast({ title: 'Erro ao carregar emails', status: 'error' });
    }
  };

  const handleOpenCreate = () => {
    setFormData(initialEmailState);
    setIsEditing(null);
    setIsOpen(true);
  };

  const handleOpenEdit = (email) => {
    setFormData(email);
    setIsEditing(email._id);
    setIsOpen(true);
  };

  const handleSave = async () => {
    if (!formData.endereco || !formData.asset_id || !formData.tipo) {
      toast({
        title: 'Erro',
        description: 'Endereço, Asset e Tipo são obrigatórios',
        status: 'error'
      });
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const dados = { ...formData };
      if (dados._id) delete dados._id;

      if (isEditing) {
        await axios.put(`${API_URL}/emails/${isEditing}`, dados, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast({ title: 'Email atualizado!', status: 'success' });
      } else {
        await axios.post(`${API_URL}/emails`, dados, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast({ title: 'Email criado!', status: 'success' });
      }
      setIsOpen(false);
      fetchEmails();
    } catch (error) {
      toast({
        title: 'Erro',
        description: error.response?.data?.erro || 'Erro ao salvar',
        status: 'error'
      });
    }
  };

  const handleDelete = async (id, endereco) => {
    if (window.confirm(`Tem certeza que deseja inativar "${endereco}"?`)) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`${API_URL}/emails/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast({ title: 'Email inativado!', status: 'success' });
        fetchEmails();
      } catch (error) {
        toast({ title: 'Erro ao inativar', status: 'error' });
      }
    }
  };

  const toggleShowPassword = (fieldName) => {
    setShowPassword(prev => ({ ...prev, [fieldName]: !prev[fieldName] }));
  };

  const getTipoColor = (tipo) => {
    if (tipo === 'google') return 'red';
    if (tipo === 'microsoft') return 'blue';
    return 'purple'; // zimbra
  };

  const getTipoLabel = (tipo) => {
    if (tipo === 'google') return 'Google Workspace';
    if (tipo === 'microsoft') return 'Microsoft 365';
    return 'Zimbra';
  };

  const getPatrimonioLabel = (assetId, assetType) => {
    if (assetType === 'celular' || assetType === 'cellphone') {
      const cel = celulares?.find(c => c._id === assetId);
      return cel ? `CEL: ${cel.patrimonio}` : 'Celular não encontrado';
    }
    const asset = assets?.find(a => a._id === assetId);
    return asset ? asset.patrimonio : 'Asset não encontrado';
  };

  return (
    <Box p={6}>
      <HStack justify="space-between" mb={6}>
        <Text fontSize="2xl" fontWeight="bold">E-mails Corporativos</Text>
        <HStack>
          {/* BOTÃO IMPORTAR */}
          <Button 
            leftIcon={<DownloadIcon />} 
            variant="outline" 
            colorScheme="blue" 
            onClick={onImportOpen}
          >
            Importar CSV
          </Button>
          <Button leftIcon={<AddIcon />} colorScheme="green" onClick={handleOpenCreate}>
            Novo Email
          </Button>
        </HStack>
      </HStack>

      <HStack mb={4} spacing={4}>
        <FormControl maxW="200px">
          <FormLabel fontSize="sm">Filtrar por Tipo</FormLabel>
          <Select
            value={filtroTipo}
            onChange={(e) => setFiltroTipo(e.target.value)}
            placeholder="Todos"
          >
            <option value="google">Google Workspace</option>
            <option value="microsoft">Microsoft 365</option>
            <option value="zimbra">Zimbra</option>
          </Select>
        </FormControl>

        <FormControl maxW="250px">
          <FormLabel fontSize="sm">Filtrar por Patrimônio</FormLabel>
          <Select
            value={filtroPatrimonio}
            onChange={(e) => setFiltroPatrimonio(e.target.value)}
            placeholder="Todos"
          >
            {assets?.map(a => (
              <option key={a._id} value={a._id}>{a.patrimonio}</option>
            ))}
            {celulares?.map(c => (
              <option key={c._id} value={c._id}>CEL: {c.patrimonio}</option>
            ))}
          </Select>
        </FormControl>
      </HStack>

      <Box overflowX="auto" borderWidth="1px" borderRadius="lg">
        <Table variant="striped" colorScheme="gray" size="sm">
          <Thead bg="gray.100">
            <Tr>
              <Th>Endereço</Th>
              <Th>Tipo</Th>
              <Th>Patrimônio</Th>
              <Th>Usuário</Th>
              <Th>Status</Th>
              <Th>Ações</Th>
            </Tr>
          </Thead>
          <Tbody>
            {emails.map(email => (
              <Tr key={email._id}>
                <Td fontWeight="bold" fontSize="sm">{email.endereco}</Td>
                <Td>
                  <Badge colorScheme={getTipoColor(email.tipo)}>
                    {getTipoLabel(email.tipo)}
                  </Badge>
                </Td>
                <Td fontSize="sm" fontWeight="bold">
                  {getPatrimonioLabel(email.asset_id, email.asset_type)}
                </Td>
                <Td>{email.usuario || '-'}</Td>
                <Td>
                  <Badge colorScheme={email.status === 'Ativo' ? 'green' : 'gray'}>
                    {email.status}
                  </Badge>
                </Td>
                <Td>
                  <HStack spacing={2}>
                    <IconButton
                      icon={<EditIcon />}
                      size="sm"
                      colorScheme="blue"
                      onClick={() => handleOpenEdit(email)}
                    />
                    <IconButton
                      icon={<DeleteIcon />}
                      size="sm"
                      colorScheme="red"
                      onClick={() => handleDelete(email._id, email.endereco)}
                    />
                  </HStack>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>

      {/* Modal de Criar/Editar (MANTIDO O ORIGINAL COMPLETO) */}
      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{isEditing ? 'Editar Email' : 'Novo Email'}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Endereço Email</FormLabel>
                <Input
                  type="email"
                  value={formData.endereco}
                  onChange={(e) => setFormData({ ...formData, endereco: e.target.value })}
                  placeholder="Ex: usuario@empresa.com"
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Tipo de Email</FormLabel>
                <Select
                  value={formData.tipo}
                  onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
                >
                  <option value="google">Google Workspace</option>
                  <option value="microsoft">Microsoft 365</option>
                  <option value="zimbra">Zimbra (Legado)</option>
                </Select>
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Vinculado a</FormLabel>
                <Tabs>
                  <TabList mb="1em">
                    <Tab>Computador/Notebook</Tab>
                    <Tab>Celular</Tab>
                  </TabList>
                  <TabPanels>
                    <TabPanel>
                      <Select
                        value={formData.asset_type === 'workstation' ? formData.asset_id : ''}
                        onChange={(e) => setFormData({ 
                          ...formData, 
                          asset_id: e.target.value,
                          asset_type: 'workstation'
                        })}
                        placeholder="Selecione um computador..."
                      >
                        {assets?.map(a => (
                          <option key={a._id} value={a._id}>
                            {a.patrimonio} - {a.hostname}
                          </option>
                        ))}
                      </Select>
                    </TabPanel>
                    <TabPanel>
                      <Select
                        value={formData.asset_type === 'celular' ? formData.asset_id : ''}
                        onChange={(e) => setFormData({ 
                          ...formData, 
                          asset_id: e.target.value,
                          asset_type: 'celular'
                        })}
                        placeholder="Selecione um celular..."
                      >
                        {celulares?.map(c => (
                          <option key={c._id} value={c._id}>
                            {c.patrimonio} - {c.modelo}
                          </option>
                        ))}
                      </Select>
                    </TabPanel>
                  </TabPanels>
                </Tabs>
              </FormControl>

              <FormControl>
                <FormLabel>Usuário Login</FormLabel>
                <Input
                  value={formData.usuario}
                  onChange={(e) => setFormData({ ...formData, usuario: e.target.value })}
                  placeholder="Ex: usuario ou usuario@empresa.com"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Senha</FormLabel>
                <InputGroup>
                  <Input
                    type={showPassword['senha'] ? 'text' : 'password'}
                    value={formData.senha}
                    onChange={(e) => setFormData({ ...formData, senha: e.target.value })}
                    placeholder="Senha da conta"
                  />
                  <InputRightElement>
                    <IconButton
                      icon={showPassword['senha'] ? <ViewOffIcon /> : <ViewIcon />}
                      size="sm"
                      variant="ghost"
                      onClick={() => toggleShowPassword('senha')}
                    />
                  </InputRightElement>
                </InputGroup>
              </FormControl>

              <FormControl>
                <FormLabel>Email de Recuperação</FormLabel>
                <Input
                  type="email"
                  value={formData.recuperacao}
                  onChange={(e) => setFormData({ ...formData, recuperacao: e.target.value })}
                  placeholder="Email alternativo para recuperação"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Data de Criação</FormLabel>
                <Input
                  type="date"
                  value={formData.data_criacao}
                  onChange={(e) => setFormData({ ...formData, data_criacao: e.target.value })}
                />
              </FormControl>

              <FormControl>
                <FormLabel>Observações</FormLabel>
                <Input
                  value={formData.obs}
                  onChange={(e) => setFormData({ ...formData, obs: e.target.value })}
                  placeholder="Notas adicionais"
                />
              </FormControl>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={() => setIsOpen(false)}>Cancelar</Button>
            <Button colorScheme="blue" onClick={handleSave}>Salvar</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
      
      {/* Modal de Importação (NOVO) */}
      <ImportModal 
        isOpen={isImportOpen} 
        onClose={onImportClose} 
        type="emails" 
        onSuccess={fetchEmails} 
      />

    </Box>
  );
}

export default EmailsComponent;