import React, { useState, useEffect } from 'react';
import {
  Box, Tabs, TabList, TabPanels, Tab, TabPanel, Heading, Text, 
  Badge, Table, Thead, Tbody, Tr, Th, Td, Spinner, Center, FormControl, 
  FormLabel, Input, Button, VStack, HStack, useToast
} from '@chakra-ui/react';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/api';

function AssetDetail({ asset, onClose, onSave }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState(asset);
  const toast = useToast();
  const token = localStorage.getItem('token');

  useEffect(() => {
    if (asset._id) {
      fetchLogs();
    }
  }, [asset._id]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${API_URL}/logs/ativo/${asset._id}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setLogs(response.data);
    } catch (error) {
      console.error('Erro ao carregar logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const formatarData = (dataIso) => {
    const data = new Date(dataIso);
    return data.toLocaleString('pt-BR');
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

  return (
    <Box>
      <Tabs>
        <TabList>
          <Tab>Detalhes</Tab>
          <Tab>Histórico de Alterações</Tab>
        </TabList>

        <TabPanels>
          <TabPanel>
            <VStack align="stretch" spacing={4}>
              <HStack>
                <Text fontWeight="bold">ID:</Text>
                <Text>{asset._id}</Text>
              </HStack>
              
              <FormControl>
                <FormLabel>Nome/Modelo</FormLabel>
                <Input 
                  value={formData.nome || ''} 
                  onChange={(e) => handleChange('nome', e.target.value)}
                />
              </FormControl>

              <FormControl>
                <FormLabel>Patrimônio</FormLabel>
                <Input 
                  value={formData.patrimonio || ''} 
                  onChange={(e) => handleChange('patrimonio', e.target.value)}
                />
              </FormControl>

              <FormControl>
                <FormLabel>Filial</FormLabel>
                <Input value={formData.filial || ''} isReadOnly />
              </FormControl>

              <Button colorScheme="teal" onClick={() => onSave(formData)}>
                Salvar Alterações
              </Button>
            </VStack>
          </TabPanel>

          <TabPanel>
            {loading ? (
              <Center><Spinner /></Center>
            ) : logs.length === 0 ? (
              <Text color="gray.500">Nenhum log encontrado</Text>
            ) : (
              <Box overflowX="auto">
                <Table size="sm">
                  <Thead bg="gray.100">
                    <Tr>
                      <Th>Data/Hora</Th>
                      <Th>Ação</Th>
                      <Th>Usuário</Th>
                      <Th>Campo</Th>
                      <Th>Valor Anterior</Th>
                      <Th>Valor Novo</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {logs.map((log) => (
                      <Tr key={log._id}>
                        <Td fontSize="xs">{formatarData(log.data)}</Td>
                        <Td>
                          <Badge colorScheme={getAcaoBadge(log.acao)}>
                            {log.acao}
                          </Badge>
                        </Td>
                        <Td fontSize="sm">{log.usuario}</Td>
                        <Td fontSize="xs" fontWeight="bold">{log.campo || '-'}</Td>
                        <Td fontSize="xs" bg="red.50" maxW="150px" isTruncated>
                          {log.valor_anterior || '-'}
                        </Td>
                        <Td fontSize="xs" bg="green.50" maxW="150px" isTruncated>
                          {log.valor_novo || '-'}
                        </Td>
                      </Tr>
                    ))}
                  </Tbody>
                </Table>
              </Box>
            )}
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
}

export default AssetDetail;
