import React, { useState, useEffect } from 'react';
import {
  Box, Button, Table, Thead, Tbody, Tr, Th, Td, Badge, IconButton,
  Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalCloseButton,
  ModalFooter, FormControl, FormLabel, Input, Select, VStack, HStack,
  useToast, InputGroup, InputRightElement, Divider, Text
} from '@chakra-ui/react';
import { AddIcon, EditIcon, DeleteIcon, ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/api';

const initialCelularState = {
  patrimonio: '',
  filial: '',
  modelo: '',
  imei: '',
  numero: '',
  responsavel: '',
  status: 'Em Uso',
  obs: ''
};

function CelularesComponent({ usuario, filiais, assets }) {
  const [celulares, setCelulares] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(null);
  const [formData, setFormData] = useState(initialCelularState);
  const [showPassword, setShowPassword] = useState({});
  const [filtroFilial, setFiltroFilial] = useState('');
  const toast = useToast();

  useEffect(() => {
    fetchCelulares();
  }, [filtroFilial]);

  const fetchCelulares = async () => {
    try {
      const token = localStorage.getItem('token');
      const params = filtroFilial ? { filial: filtroFilial } : {};
      const response = await axios.get(`${API_URL}/celulares`, {
        params,
        headers: { Authorization: `Bearer ${token}` }
      });
      setCelulares(response.data.filter(c => c.status !== 'Inativo'));
    } catch (error) {
      toast({ title: 'Erro ao carregar celulares', status: 'error' });
    }
  };

  const handleOpenCreate = () => {
    setFormData(initialCelularState);
    setIsEditing(null);
    setIsOpen(true);
  };

  const handleOpenEdit = (celular) => {
    setFormData(celular);
    setIsEditing(celular._id);
    setIsOpen(true);
  };

  const handleSave = async () => {
    if (!formData.patrimonio || !formData.filial) {
      toast({ title: 'Erro', description: 'Patrimônio e Filial são obrigatórios', status: 'error' });
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (isEditing) {
        await axios.put(`${API_URL}/celulares/${isEditing}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast({ title: 'Celular atualizado!', status: 'success' });
      } else {
        await axios.post(`${API_URL}/celulares`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast({ title: 'Celular criado!', status: 'success' });
      }
      setIsOpen(false);
      fetchCelulares();
    } catch (error) {
      toast({
        title: 'Erro',
        description: error.response?.data?.erro || 'Erro ao salvar',
        status: 'error'
      });
    }
  };

  const handleDelete = async (id, patrimonio) => {
    if (window.confirm(`Tem certeza que deseja inativar o celular ${patrimonio}?`)) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`${API_URL}/celulares/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        toast({ title: 'Celular inativado!', status: 'success' });
        fetchCelulares();
      } catch (error) {
        toast({ title: 'Erro ao inativar', status: 'error' });
      }
    }
  };

  const toggleShowField = (fieldName) => {
    setShowPassword(prev => ({ ...prev, [fieldName]: !prev[fieldName] }));
  };

  const getStatusColor = (status) => {
    const colors = { 'Em Uso': 'green', 'Reserva': 'blue', 'Manutenção': 'orange', 'Inativo': 'gray' };
    return colors[status] || 'gray';
  };

  return (
    <Box p={6}>
      <HStack justify="space-between" mb={6}>
        <Text fontSize="2xl" fontWeight="bold">Celulares</Text>
        <Button leftIcon={<AddIcon />} colorScheme="green" onClick={handleOpenCreate}>
          Novo Celular
        </Button>
      </HStack>

      <HStack mb={4} spacing={4}>
        <FormControl maxW="200px">
          <FormLabel fontSize="sm">Filtrar por Filial</FormLabel>
          <Select
            value={filtroFilial}
            onChange={(e) => setFiltroFilial(e.target.value)}
            placeholder="Todas"
          >
            {filiais.map(f => (
              <option key={f._id} value={f.nome}>{f.nome}</option>
            ))}
          </Select>
        </FormControl>
      </HStack>

      <Box overflowX="auto" borderWidth="1px" borderRadius="lg">
        <Table variant="striped" colorScheme="gray">
          <Thead bg="gray.100">
            <Tr>
              <Th>PAT</Th>
              <Th>Modelo</Th>
              <Th>IMEI</Th>
              <Th>Número</Th>
              <Th>Responsável</Th>
              <Th>Status</Th>
              <Th>Ações</Th>
            </Tr>
          </Thead>
          <Tbody>
            {celulares.map(celular => (
              <Tr key={celular._id}>
                <Td fontWeight="bold">{celular.patrimonio}</Td>
                <Td>{celular.modelo}</Td>
                <Td fontSize="sm">{celular.imei || '-'}</Td>
                <Td>{celular.numero || '-'}</Td>
                <Td>{celular.responsavel}</Td>
                <Td>
                  <Badge colorScheme={getStatusColor(celular.status)}>
                    {celular.status}
                  </Badge>
                </Td>
                <Td>
                  <HStack spacing={2}>
                    <IconButton
                      icon={<EditIcon />}
                      size="sm"
                      colorScheme="blue"
                      onClick={() => handleOpenEdit(celular)}
                    />
                    <IconButton
                      icon={<DeleteIcon />}
                      size="sm"
                      colorScheme="red"
                      onClick={() => handleDelete(celular._id, celular.patrimonio)}
                    />
                  </HStack>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>

      {/* Modal de Criar/Editar */}
      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{isEditing ? 'Editar Celular' : 'Novo Celular'}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Patrimônio</FormLabel>
                <Input
                  value={formData.patrimonio}
                  onChange={(e) => setFormData({ ...formData, patrimonio: e.target.value })}
                  placeholder="Ex: CEL-001"
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Filial</FormLabel>
                <Select
                  value={formData.filial}
                  onChange={(e) => setFormData({ ...formData, filial: e.target.value })}
                >
                  <option value="">Selecione...</option>
                  {filiais.map(f => (
                    <option key={f._id} value={f.nome}>{f.nome}</option>
                  ))}
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>Modelo</FormLabel>
                <Input
                  value={formData.modelo}
                  onChange={(e) => setFormData({ ...formData, modelo: e.target.value })}
                  placeholder="Ex: iPhone 13"
                />
              </FormControl>

              <FormControl>
                <FormLabel>IMEI</FormLabel>
                <Input
                  value={formData.imei}
                  onChange={(e) => setFormData({ ...formData, imei: e.target.value })}
                  placeholder="Número IMEI"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Número</FormLabel>
                <Input
                  value={formData.numero}
                  onChange={(e) => setFormData({ ...formData, numero: e.target.value })}
                  placeholder="Ex: (11) 99999-8888"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Responsável</FormLabel>
                <Input
                  value={formData.responsavel}
                  onChange={(e) => setFormData({ ...formData, responsavel: e.target.value })}
                  placeholder="Nome do responsável"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Status</FormLabel>
                <Select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                >
                  <option>Em Uso</option>
                  <option>Reserva</option>
                  <option>Manutenção</option>
                  <option>Inativo</option>
                </Select>
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
    </Box>
  );
}

export default CelularesComponent;
