import React, { useState, useEffect } from 'react';
import {
  Box, Button, Table, Thead, Tbody, Tr, Th, Td, Badge, IconButton,
  Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalCloseButton,
  ModalFooter, FormControl, FormLabel, Input, Select, VStack, HStack,
  useToast, Text, InputRightElement
} from '@chakra-ui/react';
import { AddIcon, EditIcon, DeleteIcon, ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/api';

function EmailsPatrimonioComponent({ assetId, assetType = 'workstation' }) {
  const [emails, setEmails] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(null);
  const [formData, setFormData] = useState({
    endereco: '',
    tipo: 'google',
    usuario: '',
    senha: '',
    recuperacao: ''
  });
  const [showPassword, setShowPassword] = useState({});
  const toast = useToast();

  useEffect(() => {
    if (assetId) {
      fetchEmails();
    }
  }, [assetId]);

  const fetchEmails = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/emails?asset_id=${assetId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEmails(response.data.filter(e => e.status !== 'Inativo'));
    } catch (error) {
      console.error('Erro ao carregar emails:', error);
    }
  };

  const handleOpenCreate = () => {
    setFormData({
      endereco: '',
      tipo: 'google',
      usuario: '',
      senha: '',
      recuperacao: ''
    });
    setIsEditing(null);
    setIsOpen(true);
  };

  const handleOpenEdit = (email) => {
    setFormData({
      endereco: email.endereco,
      tipo: email.tipo,
      usuario: email.usuario,
      senha: email.senha,
      recuperacao: email.recuperacao
    });
    setIsEditing(email._id);
    setIsOpen(true);
  };

  const handleSave = async () => {
    if (!formData.endereco || !formData.tipo) {
      toast({
        title: 'Erro',
        description: 'Endereço e Tipo são obrigatórios',
        status: 'error'
      });
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const dados = {
        ...formData,
        asset_id: assetId,
        asset_type: assetType,
        status: 'Ativo'
      };

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
    return tipo === 'google' ? 'red' : 'purple';
  };

  const getTipoLabel = (tipo) => {
    return tipo === 'google' ? 'Google' : 'Zimbra';
  };

  return (
    <Box>
      <HStack justify="space-between" mb={4}>
        <Text fontWeight="bold">Emails Corporativos</Text>
        <Button leftIcon={<AddIcon />} colorScheme="blue" size="sm" onClick={handleOpenCreate}>
          Adicionar Email
        </Button>
      </HStack>

      {emails.length === 0 ? (
        <Box p={4} bg="gray.50" borderRadius="md" textAlign="center">
          <Text color="gray.500" fontSize="sm">Nenhum email cadastrado</Text>
        </Box>
      ) : (
        <Box overflowX="auto" borderWidth="1px" borderRadius="md" mb={4}>
          <Table variant="striped" colorScheme="gray" size="sm">
            <Thead bg="gray.100">
              <Tr>
                <Th>Email</Th>
                <Th>Tipo</Th>
                <Th>Usuário</Th>
                <Th>Ações</Th>
              </Tr>
            </Thead>
            <Tbody>
              {emails.map(email => (
                <Tr key={email._id}>
                  <Td fontSize="sm">{email.endereco}</Td>
                  <Td>
                    <Badge colorScheme={getTipoColor(email.tipo)}>
                      {getTipoLabel(email.tipo)}
                    </Badge>
                  </Td>
                  <Td fontSize="sm">{email.usuario || '-'}</Td>
                  <Td>
                    <HStack spacing={2}>
                      <IconButton
                        icon={<EditIcon />}
                        size="xs"
                        colorScheme="blue"
                        variant="ghost"
                        onClick={() => handleOpenEdit(email)}
                      />
                      <IconButton
                        icon={<DeleteIcon />}
                        size="xs"
                        colorScheme="red"
                        variant="ghost"
                        onClick={() => handleDelete(email._id, email.endereco)}
                      />
                    </HStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      )}

      {/* Modal de Criar/Editar */}
      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} size="md">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{isEditing ? 'Editar Email' : 'Novo Email'}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={3}>
              <FormControl isRequired>
                <FormLabel fontSize="sm">Endereço Email</FormLabel>
                <Input
                  size="sm"
                  type="email"
                  value={formData.endereco}
                  onChange={(e) => setFormData({ ...formData, endereco: e.target.value })}
                  placeholder="user@empresa.com"
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel fontSize="sm">Tipo</FormLabel>
                <Select
                  size="sm"
                  value={formData.tipo}
                  onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
                >
                  <option value="google">Google Workspace</option>
                  <option value="zimbra">Zimbra</option>
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel fontSize="sm">Usuário</FormLabel>
                <Input
                  size="sm"
                  value={formData.usuario}
                  onChange={(e) => setFormData({ ...formData, usuario: e.target.value })}
                  placeholder="usuário de login"
                />
              </FormControl>

              <FormControl>
                <FormLabel fontSize="sm">Senha</FormLabel>
                <InputRightElement width="4.5rem">
                  <IconButton
                    icon={showPassword['senha'] ? <ViewOffIcon /> : <ViewIcon />}
                    size="xs"
                    variant="ghost"
                    onClick={() => toggleShowPassword('senha')}
                  />
                </InputRightElement>
                <Input
                  size="sm"
                  type={showPassword['senha'] ? 'text' : 'password'}
                  value={formData.senha}
                  onChange={(e) => setFormData({ ...formData, senha: e.target.value })}
                  placeholder="senha"
                />
              </FormControl>

              <FormControl>
                <FormLabel fontSize="sm">Email Recuperação</FormLabel>
                <Input
                  size="sm"
                  type="email"
                  value={formData.recuperacao}
                  onChange={(e) => setFormData({ ...formData, recuperacao: e.target.value })}
                  placeholder="recuperacao@email.com"
                />
              </FormControl>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button size="sm" variant="ghost" mr={3} onClick={() => setIsOpen(false)}>
              Cancelar
            </Button>
            <Button size="sm" colorScheme="blue" onClick={handleSave}>
              Salvar
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
}

export default EmailsPatrimonioComponent;
