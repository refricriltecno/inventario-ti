import React, { useState, useEffect } from 'react';
import {
  Box, Button, Heading, Table, Thead, Tbody, Tr, Th, Td, Badge, VStack, HStack, 
  Select, Text, useToast, Spinner, Center
} from '@chakra-ui/react';
import { ViewIcon } from '@chakra-ui/icons';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/api';

function Logs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filtroUsuario, setFiltroUsuario] = useState('');
  const [usuarios, setUsuarios] = useState([]);
  const [stats, setStats] = useState(null);
  const toast = useToast();

  const token = localStorage.getItem('token');

  useEffect(() => {
    fetchLogs();
    fetchStats();
  }, [filtroUsuario]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const params = filtroUsuario ? { usuario: filtroUsuario } : {};
      const response = await axios.get(`${API_URL}/logs`, 
        { 
          params,
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setLogs(response.data);
    } catch (error) {
      toast({ title: 'Erro', description: 'Falha ao carregar logs', status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/logs/estatisticas`,
        { 
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setStats(response.data);
      setUsuarios(response.data.usuarios);
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  const getAcaoBadge = (acao) => {
    const cores = {
      'CRIACAO': 'green',
      'ALTERACAO': 'blue',
      'ADICAO': 'purple',
      'REMOCAO': 'red',
      'ATUALIZACAO': 'orange'
    };
    return cores[acao] || 'gray';
  };

  const formatarData = (dataIso) => {
    const data = new Date(dataIso);
    return data.toLocaleString('pt-BR');
  };

  if (loading && !logs.length) {
    return (
      <Center h="60vh">
        <Spinner size="lg" color="teal.500" />
      </Center>
    );
  }

  return (
    <Box p={6}>
      <HStack justify="space-between" mb={6}>
        <Heading size="lg">Auditoria e Logs</Heading>
        <Button colorScheme="teal" onClick={fetchLogs}>Atualizar</Button>
      </HStack>

      {stats && (
        <HStack spacing={8} mb={6} bg="gray.50" p={4} borderRadius="lg">
          <Box>
            <Text fontSize="sm" color="gray.600">Total de Logs</Text>
            <Text fontSize="2xl" fontWeight="bold" color="teal.600">{stats.total_logs}</Text>
          </Box>
          <Box>
            <Text fontSize="sm" color="gray.600">Usuários</Text>
            <Text fontSize="2xl" fontWeight="bold" color="teal.600">{stats.usuarios.length}</Text>
          </Box>
          <Box>
            <Text fontSize="sm" color="gray.600">Tipos de Ação</Text>
            <HStack spacing={2} mt={1}>
              {Object.entries(stats.logs_por_acao).map(([acao, count]) => (
                <Badge key={acao} colorScheme={getAcaoBadge(acao)}>
                  {acao}: {count}
                </Badge>
              ))}
            </HStack>
          </Box>
        </HStack>
      )}

      <Box bg="white" shadow="sm" p={4} borderRadius="lg" mb={6}>
        <Text mb={2} fontSize="sm" fontWeight="bold" color="gray.700">Filtrar por Usuário</Text>
        <Select
          value={filtroUsuario}
          onChange={(e) => setFiltroUsuario(e.target.value)}
          placeholder="Todos os usuários"
          maxW="300px"
        >
          {usuarios.map(u => (
            <option key={u} value={u}>{u}</option>
          ))}
        </Select>
      </Box>

      <Box bg="white" shadow="sm" borderRadius="lg" overflow="hidden">
        <Table variant="simple" size="sm">
          <Thead bg="gray.100">
            <Tr>
              <Th>Data/Hora</Th>
              <Th>Ação</Th>
              <Th>Usuário</Th>
              <Th>Detalhes</Th>
              <Th>Campo</Th>
              <Th>Valor Anterior</Th>
              <Th>Valor Novo</Th>
            </Tr>
          </Thead>
          <Tbody>
            {logs.length === 0 ? (
              <Tr>
                <Td colSpan="7" textAlign="center" py={8}>
                  <Text color="gray.500">Nenhum log encontrado</Text>
                </Td>
              </Tr>
            ) : (
              logs.map((log) => (
                <Tr key={log._id} _hover={{ bg: 'gray.50' }}>
                  <Td fontSize="xs">{formatarData(log.data)}</Td>
                  <Td>
                    <Badge colorScheme={getAcaoBadge(log.acao)}>
                      {log.acao}
                    </Badge>
                  </Td>
                  <Td fontSize="sm" fontWeight="medium">{log.usuario}</Td>
                  <Td fontSize="xs">{log.detalhes || '-'}</Td>
                  <Td fontSize="xs" fontWeight="bold">{log.campo || '-'}</Td>
                  <Td fontSize="xs" bg="red.50">
                    {log.valor_anterior || (log.itens_removidos?.length ? `${log.itens_removidos.length} item(s)` : '-')}
                  </Td>
                  <Td fontSize="xs" bg="green.50">
                    {log.valor_novo || (log.itens_adicionados?.length ? `${log.itens_adicionados.length} item(s)` : '-')}
                  </Td>
                </Tr>
              ))
            )}
          </Tbody>
        </Table>
      </Box>
    </Box>
  );
}

export default Logs;
