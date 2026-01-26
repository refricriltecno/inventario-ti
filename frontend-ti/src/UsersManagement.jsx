import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  ModalFooter,
  FormControl,
  FormLabel,
  Input,
  Select,
  Checkbox,
  Stack,
  HStack,
  useDisclosure,
  useToast,
  Spinner,
  Badge,
} from '@chakra-ui/react';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/api';

export default function UsersManagement() {
  const [usuarios, setUsuarios] = useState([]);
  const [filiais, setFiliais] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [newUser, setNewUser] = useState({
    username: '',
    password: '',
    nome: '',
    filial: '',
    permissoes: ['view'],
  });
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { isOpen: isNewOpen, onOpen: onNewOpen, onClose: onNewClose } = useDisclosure();
  const toast = useToast();

  useEffect(() => {
    fetchUsuarios();
    fetchFiliais();
  }, []);

  const getToken = () => localStorage.getItem('token');

  const fetchUsuarios = async () => {
    setLoading(true);
    try {
      const token = getToken();
      const res = await axios.get(`${API_URL}/auth/usuarios`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUsuarios(res.data);
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Não foi possível carregar usuários',
        status: 'error',
        duration: 3,
      });
    }
    setLoading(false);
  };

  const fetchFiliais = async () => {
    try {
      const res = await axios.get(`${API_URL}/filiais`);
      setFiliais(res.data);
    } catch (error) {
      console.error('Erro ao carregar filiais:', error);
    }
  };;

  const handleEditUser = (usuario) => {
    setEditingUser({
      ...usuario,
      permissoes: usuario.permissoes || ['view'],
    });
    onOpen();
  };

  const handleNewUser = () => {
    setNewUser({
      username: '',
      password: '',
      nome: '',
      filial: '',
      permissoes: ['view'],
    });
    onNewOpen();
  };

  const handleSaveEdit = async () => {
    try {
      const token = getToken();
      await axios.put(`${API_URL}/auth/usuarios/${editingUser._id}`, editingUser, {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast({
        title: 'Sucesso',
        description: 'Usuário atualizado!',
        status: 'success',
        duration: 3,
      });
      fetchUsuarios();
      onClose();
    } catch (error) {
      toast({
        title: 'Erro',
        description: error.response?.data?.erro || 'Erro ao atualizar usuário',
        status: 'error',
        duration: 3,
      });
    }
  };

  const handleCreateUser = async () => {
    try {
      const token = getToken();
      await axios.post(`${API_URL}/auth/register`, newUser, {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast({
        title: 'Sucesso',
        description: 'Usuário criado!',
        status: 'success',
        duration: 3,
      });
      fetchUsuarios();
      onNewClose();
    } catch (error) {
      toast({
        title: 'Erro',
        description: error.response?.data?.erro || 'Erro ao criar usuário',
        status: 'error',
        duration: 3,
      });
    }
  };

  const handleDeleteUser = async (usuarioId) => {
    if (window.confirm('Tem certeza que deseja deletar este usuário?')) {
      try {
        const token = getToken();
        await axios.delete(`${API_URL}/auth/usuarios/${usuarioId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        toast({
          title: 'Sucesso',
          description: 'Usuário deletado!',
          status: 'success',
          duration: 3,
        });
        fetchUsuarios();
      } catch (error) {
        toast({
          title: 'Erro',
          description: error.response?.data?.erro || 'Erro ao deletar usuário',
          status: 'error',
          duration: 3,
        });
      }
    }
  };

  const togglePermissao = (permissao) => {
    if (editingUser) {
      const perms = editingUser.permissoes || [];
      if (perms.includes(permissao)) {
        setEditingUser({
          ...editingUser,
          permissoes: perms.filter(p => p !== permissao),
        });
      } else {
        setEditingUser({
          ...editingUser,
          permissoes: [...perms, permissao],
        });
      }
    }
  };

  const toggleNewPermissao = (permissao) => {
    const perms = newUser.permissoes || [];
    if (perms.includes(permissao)) {
      setNewUser({
        ...newUser,
        permissoes: perms.filter(p => p !== permissao),
      });
    } else {
      setNewUser({
        ...newUser,
        permissoes: [...perms, permissao],
      });
    }
  };

  return (
    <Box p={6}>
      <HStack mb={6} justify="space-between">
        <h1 style={{ fontSize: '24px', fontWeight: 'bold' }}>Gerenciamento de Usuários</h1>
        <Button colorScheme="blue" onClick={handleNewUser}>
          + Novo Usuário
        </Button>
      </HStack>

      {loading ? (
        <Spinner />
      ) : (
        <Box overflowX="auto">
          <Table variant="striped">
            <Thead>
              <Tr bg="gray.100">
                <Th>Usuário</Th>
                <Th>Nome</Th>
                <Th>Filial</Th>
                <Th>Status</Th>
                <Th>Permissões</Th>
                <Th>Último Login</Th>
                <Th>Ações</Th>
              </Tr>
            </Thead>
            <Tbody>
              {usuarios.map((u) => (
                <Tr key={u._id}>
                  <Td>{u.username}</Td>
                  <Td>{u.nome}</Td>
                  <Td>{u.filial}</Td>
                  <Td>
                    <Badge colorScheme={u.ativo ? 'green' : 'red'}>
                      {u.ativo ? 'Ativo' : 'Inativo'}
                    </Badge>
                  </Td>
                  <Td>
                    <Stack spacing={1}>
                      {(u.permissoes || []).map(p => (
                        <Badge key={p} colorScheme="purple" fontSize="xs">
                          {p}
                        </Badge>
                      ))}
                    </Stack>
                  </Td>
                  <Td>{u.ultimo_login ? new Date(u.ultimo_login).toLocaleDateString('pt-BR') : '-'}</Td>
                  <Td>
                    <HStack spacing={2}>
                      <Button
                        size="sm"
                        colorScheme="blue"
                        onClick={() => handleEditUser(u)}
                      >
                        Editar
                      </Button>
                      <Button
                        size="sm"
                        colorScheme="red"
                        onClick={() => handleDeleteUser(u._id)}
                      >
                        Deletar
                      </Button>
                    </HStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      )}

      {/* Modal de Edição */}
      <Modal isOpen={isOpen} onClose={onClose} size="md">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Editar Usuário</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {editingUser && (
              <Stack spacing={4}>
                <FormControl>
                  <FormLabel>Nome</FormLabel>
                  <Input
                    value={editingUser.nome}
                    onChange={(e) =>
                      setEditingUser({ ...editingUser, nome: e.target.value })
                    }
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Filial</FormLabel>
                  <Select
                    value={editingUser.filial}
                    onChange={(e) =>
                      setEditingUser({ ...editingUser, filial: e.target.value })
                    }
                  >
                    <option value="">Selecione uma filial</option>
                    {filiais.map((f) => (
                      <option key={f._id} value={f.nome}>
                        {f.nome}
                      </option>
                    ))}
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>Status</FormLabel>
                  <Select
                    value={editingUser.ativo ? 'ativo' : 'inativo'}
                    onChange={(e) =>
                      setEditingUser({
                        ...editingUser,
                        ativo: e.target.value === 'ativo',
                      })
                    }
                  >
                    <option value="ativo">Ativo</option>
                    <option value="inativo">Inativo</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>Permissões</FormLabel>
                  <Stack spacing={2}>
                    {['view', 'edit', 'delete', 'admin'].map((perm) => (
                      <Checkbox
                        key={perm}
                        isChecked={(editingUser.permissoes || []).includes(perm)}
                        onChange={() => togglePermissao(perm)}
                      >
                        {perm === 'view' && 'Visualizar'}
                        {perm === 'edit' && 'Editar'}
                        {perm === 'delete' && 'Deletar'}
                        {perm === 'admin' && 'Administrador'}
                      </Checkbox>
                    ))}
                  </Stack>
                </FormControl>
              </Stack>
            )}
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancelar
            </Button>
            <Button colorScheme="blue" onClick={handleSaveEdit}>
              Salvar
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Modal de Novo Usuário */}
      <Modal isOpen={isNewOpen} onClose={onNewClose} size="md">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Novo Usuário</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Stack spacing={4}>
              <FormControl>
                <FormLabel>Username</FormLabel>
                <Input
                  value={newUser.username}
                  onChange={(e) =>
                    setNewUser({ ...newUser, username: e.target.value })
                  }
                  placeholder="Ex: joao.silva"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Senha</FormLabel>
                <Input
                  type="password"
                  value={newUser.password}
                  onChange={(e) =>
                    setNewUser({ ...newUser, password: e.target.value })
                  }
                />
              </FormControl>

              <FormControl>
                <FormLabel>Nome</FormLabel>
                <Input
                  value={newUser.nome}
                  onChange={(e) =>
                    setNewUser({ ...newUser, nome: e.target.value })
                  }
                />
              </FormControl>

              <FormControl>
                <FormLabel>Filial</FormLabel>
                <Select
                  value={newUser.filial}
                  onChange={(e) =>
                    setNewUser({ ...newUser, filial: e.target.value })
                  }
                >
                  <option value="">Selecione uma filial</option>
                  {filiais.map((f) => (
                    <option key={f._id} value={f.nome}>
                      {f.nome}
                    </option>
                  ))}
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>Permissões</FormLabel>
                <Stack spacing={2}>
                  {['view', 'edit', 'delete', 'admin'].map((perm) => (
                    <Checkbox
                      key={perm}
                      isChecked={(newUser.permissoes || []).includes(perm)}
                      onChange={() => toggleNewPermissao(perm)}
                    >
                      {perm === 'view' && 'Visualizar'}
                      {perm === 'edit' && 'Editar'}
                      {perm === 'delete' && 'Deletar'}
                      {perm === 'admin' && 'Administrador'}
                    </Checkbox>
                  ))}
                </Stack>
              </FormControl>
            </Stack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onNewClose}>
              Cancelar
            </Button>
            <Button colorScheme="green" onClick={handleCreateUser}>
              Criar
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
}
