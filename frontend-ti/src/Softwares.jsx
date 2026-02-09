import React, { useState, useEffect } from 'react';
import {
  Box, Button, Table, Thead, Tbody, Tr, Th, Td, Badge, IconButton,
  Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalCloseButton,
  ModalFooter, FormControl, FormLabel, Input, Select, VStack, HStack,
  useToast, Text, Checkbox, useDisclosure // <--- Adicionado
} from '@chakra-ui/react';
import { AddIcon, EditIcon, DeleteIcon, DownloadIcon } from '@chakra-ui/icons'; // <--- DownloadIcon
import axios from 'axios';
import ImportModal from './components/ImportModal'; // <--- Import Component

const API_URL = 'http://127.0.0.1:5000/api';

const initialSoftwareState = {
  nome: '',
  versao: '',
  asset_id: '',
  tipo_licenca: 'Individual',
  chave_licenca: '',
  dt_instalacao: '',
  dt_vencimento: '',
  renovacao_automatica: false,
  custo_anual: '',
  status: 'Ativo',
  obs: ''
};

function SoftwaresComponent({ usuario, assets, onSoftwareAdded }) {
  const [softwares, setSoftwares] = useState([]);
  
  // Controle Modal Criar/Editar
  const [isOpen, setIsOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(null);
  const [formData, setFormData] = useState(initialSoftwareState);
  
  // Filtro
  const [filtroAsset, setFiltroAsset] = useState('');
  
  // Controle Modal Importação (NOVO)
  const { 
    isOpen: isImportOpen, 
    onOpen: onImportOpen, 
    onClose: onImportClose 
  } = useDisclosure();
  
  const toast = useToast();

  useEffect(() => {
    fetchSoftwares();
  }, [filtroAsset]);

  const fetchSoftwares = async () => {
    try {
      const token = localStorage.getItem('token');
      const params = filtroAsset ? { asset_id: filtroAsset } : {};
      const response = await axios.get(`${API_URL}/softwares`, {
        params,
        headers: { Authorization: `Bearer ${token}` }
      });
      setSoftwares(response.data.filter(s => s.status !== 'Inativo'));
    } catch (error) {
      toast({ title: 'Erro ao carregar softwares', status: 'error' });
    }
  };

  const handleOpenCreate = () => {
    setFormData(initialSoftwareState);
    setIsEditing(null);
    setIsOpen(true);
  };

  const handleOpenEdit = (software) => {
    setFormData(software);
    setIsEditing(software.id);
    setIsOpen(true);
  };

  const handleSave = async () => {
    if (!formData.nome || !formData.asset_id) {
      toast({
        title: 'Erro',
        description: 'Nome e Asset são obrigatórios',
        status: 'error'
      });
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const dados = { ...formData };
      if (dados.id) delete dados.id;

      if (isEditing) {
        await axios.put(`${API_URL}/softwares/${isEditing}`, dados, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast({ title: 'Software atualizado!', status: 'success' });
      } else {
        await axios.post(`${API_URL}/softwares`, dados, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast({ title: 'Software criado!', status: 'success' });
      }
      setIsOpen(false);
      fetchSoftwares();
      if(onSoftwareAdded) onSoftwareAdded();
    } catch (error) {
      toast({
        title: 'Erro',
        description: error.response?.data?.erro || 'Erro ao salvar',
        status: 'error'
      });
    }
  };

  const handleDelete = async (id, nome) => {
    if (window.confirm(`Tem certeza que deseja inativar "${nome}"?`)) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`${API_URL}/softwares/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast({ title: 'Software inativado!', status: 'success' });
        fetchSoftwares();
      } catch (error) {
        toast({ title: 'Erro ao inativar', status: 'error' });
      }
    }
  };

  const formatarData = (data) => {
    if (!data) return '-';
    return new Date(data).toLocaleDateString('pt-BR');
  };

  const verificarVencimento = (dtVencimento) => {
    if (!dtVencimento) return 'gray';
    const vencimento = new Date(dtVencimento);
    const hoje = new Date();
    const dias = Math.ceil((vencimento - hoje) / (1000 * 60 * 60 * 24));

    if (dias < 0) return 'red';
    if (dias < 30) return 'orange';
    return 'green';
  };

  return (
    <Box p={6}>
      <HStack justify="space-between" mb={6}>
        <Text fontSize="2xl" fontWeight="bold">Softwares & Licenças</Text>
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
            Novo Software
          </Button>
        </HStack>
      </HStack>

      <HStack mb={4} spacing={4}>
        <FormControl maxW="250px">
          <FormLabel fontSize="sm">Filtrar por Asset</FormLabel>
          <Select
            value={filtroAsset}
            onChange={(e) => setFiltroAsset(e.target.value)}
            placeholder="Todos"
          >
            {assets.map(a => (
              <option key={a.id} value={a.id}>{a.patrimonio} - {a.hostname}</option>
            ))}
          </Select>
        </FormControl>
      </HStack>

      <Box overflowX="auto" borderWidth="1px" borderRadius="lg">
        <Table variant="striped" colorScheme="gray" size="sm">
          <Thead bg="gray.100">
            <Tr>
              <Th>Software</Th>
              <Th>Versão</Th>
              <Th>Tipo Licença</Th>
              <Th>Data Instalação</Th>
              <Th>Vencimento</Th>
              <Th>Status</Th>
              <Th>Ações</Th>
            </Tr>
          </Thead>
          <Tbody>
            {softwares.map(software => (
              <Tr key={software.id}>
                <Td fontWeight="bold">{software.nome}</Td>
                <Td>{software.versao || '-'}</Td>
                <Td>{software.tipo_licenca}</Td>
                <Td fontSize="sm">{formatarData(software.dt_instalacao)}</Td>
                <Td fontSize="sm">
                  <Badge colorScheme={verificarVencimento(software.dt_vencimento)}>
                    {formatarData(software.dt_vencimento)}
                  </Badge>
                </Td>
                <Td>
                  <Badge colorScheme={software.status === 'Ativo' ? 'green' : 'gray'}>
                    {software.status}
                  </Badge>
                </Td>
                <Td>
                  <HStack spacing={2}>
                    <IconButton
                      icon={<EditIcon />}
                      size="sm"
                      colorScheme="blue"
                      onClick={() => handleOpenEdit(software)}
                    />
                    <IconButton
                      icon={<DeleteIcon />}
                      size="sm"
                      colorScheme="red"
                      onClick={() => handleDelete(software.id, software.nome)}
                    />
                  </HStack>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>

      {/* Modal de Criar/Editar (MANTIDO COMPLETO) */}
      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{isEditing ? 'Editar Software' : 'Novo Software'}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Nome do Software</FormLabel>
                <Input
                  value={formData.nome}
                  onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                  placeholder="Ex: Microsoft Office 365"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Versão</FormLabel>
                <Input
                  value={formData.versao}
                  onChange={(e) => setFormData({ ...formData, versao: e.target.value })}
                  placeholder="Ex: 2024"
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Asset</FormLabel>
                <Select
                  value={formData.asset_id}
                  onChange={(e) => setFormData({ ...formData, asset_id: e.target.value })}
                >
                  <option value="">Selecione um Asset...</option>
                  {assets.map(a => (
                    <option key={a.id} value={a.id}>
                      {a.patrimonio} - {a.hostname}
                    </option>
                  ))}
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>Tipo de Licença</FormLabel>
                <Select
                  value={formData.tipo_licenca}
                  onChange={(e) => setFormData({ ...formData, tipo_licenca: e.target.value })}
                >
                  <option>Individual</option>
                  <option>Volume</option>
                  <option>Corporativa</option>
                  <option>Trial</option>
                  <option>Open Source</option>
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>Chave de Licença</FormLabel>
                <Input
                  type="password"
                  value={formData.chave_licenca}
                  onChange={(e) => setFormData({ ...formData, chave_licenca: e.target.value })}
                  placeholder="Chave de licença (protegida)"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Data Instalação</FormLabel>
                <Input
                  type="date"
                  value={formData.dt_instalacao}
                  onChange={(e) => setFormData({ ...formData, dt_instalacao: e.target.value })}
                />
              </FormControl>

              <FormControl>
                <FormLabel>Data Vencimento</FormLabel>
                <Input
                  type="date"
                  value={formData.dt_vencimento}
                  onChange={(e) => setFormData({ ...formData, dt_vencimento: e.target.value })}
                />
              </FormControl>

              <FormControl>
                <FormLabel>Custo Anual</FormLabel>
                <Input
                  type="number"
                  value={formData.custo_anual}
                  onChange={(e) => setFormData({ ...formData, custo_anual: e.target.value })}
                  placeholder="Ex: 1200.00"
                />
              </FormControl>

              <Checkbox
                isChecked={formData.renovacao_automatica}
                onChange={(e) => setFormData({ ...formData, renovacao_automatica: e.target.checked })}
              >
                Renovação Automática
              </Checkbox>

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
        type="softwares" 
        onSuccess={() => {
          fetchSoftwares();
          if(onSoftwareAdded) onSoftwareAdded();
        }} 
      />

    </Box>
  );
}

export default SoftwaresComponent;