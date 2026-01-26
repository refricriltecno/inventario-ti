import React, { useState, useEffect } from 'react';
import {
  Box, Button, Table, Thead, Tbody, Tr, Th, Td, Badge, IconButton, VStack, HStack,
  useToast, Text, Select, FormControl, FormLabel, Input
} from '@chakra-ui/react';
import { AddIcon, DeleteIcon } from '@chakra-ui/icons';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/api';

function SoftwaresPatrimonioComponent({ assetId, onSoftwareAdded }) {
  const [softwares, setSoftwares] = useState([]);
  const [softwaresDisponiveis, setSoftwaresDisponiveis] = useState([]);
  const [softwareSelected, setSoftwareSelected] = useState('');
  const toast = useToast();

  useEffect(() => {
    if (assetId) {
      carregarSoftwares();
    }
  }, [assetId]);

  const carregarSoftwares = async () => {
    try {
      const token = localStorage.getItem('token');
      // Carregar softwares globais
      const resGlobal = await axios.get(`${API_URL}/softwares`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSoftwaresDisponiveis(resGlobal.data.filter(s => s.status !== 'Inativo'));

      // Carregar softwares vinculados ao asset
      const resAsset = await axios.get(`${API_URL}/softwares?asset_id=${assetId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSoftwares(resAsset.data.filter(s => s.status !== 'Inativo'));
    } catch (error) {
      console.error('Erro ao carregar softwares:', error);
    }
  };

  const handleAdicionarSoftware = async () => {
    if (!softwareSelected) {
      toast({
        title: 'Erro',
        description: 'Selecione um software',
        status: 'error'
      });
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const software = softwaresDisponiveis.find(s => s._id === softwareSelected);
      
      if (!software) {
        toast({
          title: 'Erro',
          description: 'Software não encontrado',
          status: 'error'
        });
        return;
      }

      // Verificar se já está vinculado
      if (softwares.find(s => s._id === softwareSelected)) {
        toast({
          title: 'Aviso',
          description: 'Este software já está vinculado',
          status: 'warning'
        });
        return;
      }

      // Adicionar ao array
      setSoftwares([...softwares, software]);
      setSoftwareSelected('');
      
      toast({
        title: 'Software adicionado!',
        status: 'success'
      });

      // Notificar o pai
      if (onSoftwareAdded) {
        onSoftwareAdded();
      }
    } catch (error) {
      toast({
        title: 'Erro',
        description: error.response?.data?.erro || 'Erro ao adicionar software',
        status: 'error'
      });
    }
  };

  const handleRemoverSoftware = (softwareId) => {
    if (window.confirm('Tem certeza que deseja remover este software?')) {
      setSoftwares(softwares.filter(s => s._id !== softwareId));
      toast({
        title: 'Software removido!',
        status: 'info'
      });
    }
  };

  const verificarVencimento = (dtVencimento) => {
    if (!dtVencimento) return { color: 'gray', label: 'Sem data' };
    
    const vencimento = new Date(dtVencimento);
    const hoje = new Date();
    const dias = Math.ceil((vencimento - hoje) / (1000 * 60 * 60 * 24));
    
    if (dias < 0) return { color: 'red', label: 'VENCIDO' };
    if (dias < 30) return { color: 'orange', label: `${dias}d` };
    return { color: 'green', label: 'OK' };
  };

  return (
    <Box>
      <VStack spacing={4} align="stretch">
        <Box>
          <HStack mb={3}>
            <FormControl>
              <FormLabel fontSize="sm">Adicionar Software</FormLabel>
              <HStack>
                <Select
                  size="sm"
                  placeholder="Selecione um software"
                  value={softwareSelected}
                  onChange={(e) => setSoftwareSelected(e.target.value)}
                  bg="white"
                >
                  {softwaresDisponiveis
                    .filter(s => !softwares.find(sf => sf._id === s._id))
                    .map(s => (
                      <option key={s._id} value={s._id}>
                        {s.nome} - {s.versao || 'sem versão'}
                      </option>
                    ))}
                </Select>
                <Button
                  size="sm"
                  colorScheme="blue"
                  leftIcon={<AddIcon />}
                  onClick={handleAdicionarSoftware}
                  mt="1.5em"
                >
                  Add
                </Button>
              </HStack>
            </FormControl>
          </HStack>
        </Box>

        {softwares.length === 0 ? (
          <Box p={4} bg="gray.50" borderRadius="md" textAlign="center">
            <Text color="gray.500" fontSize="sm">Nenhum software vinculado</Text>
          </Box>
        ) : (
          <Box overflowX="auto" borderWidth="1px" borderRadius="md">
            <Table variant="striped" colorScheme="gray" size="sm">
              <Thead bg="gray.100">
                <Tr>
                  <Th>Software</Th>
                  <Th>Versão</Th>
                  <Th>Vencimento</Th>
                  <Th>Status</Th>
                  <Th>Ações</Th>
                </Tr>
              </Thead>
              <Tbody>
                {softwares.map(software => {
                  const vencStatus = verificarVencimento(software.dt_vencimento);
                  return (
                    <Tr key={software._id}>
                      <Td fontSize="sm" fontWeight="500">{software.nome}</Td>
                      <Td fontSize="sm">{software.versao || '-'}</Td>
                      <Td fontSize="sm">
                        {software.dt_vencimento 
                          ? new Date(software.dt_vencimento).toLocaleDateString('pt-BR')
                          : '-'}
                      </Td>
                      <Td>
                        <Badge colorScheme={vencStatus.color}>
                          {vencStatus.label}
                        </Badge>
                      </Td>
                      <Td>
                        <IconButton
                          icon={<DeleteIcon />}
                          size="xs"
                          colorScheme="red"
                          variant="ghost"
                          onClick={() => handleRemoverSoftware(software._id)}
                        />
                      </Td>
                    </Tr>
                  );
                })}
              </Tbody>
            </Table>
          </Box>
        )}
      </VStack>
    </Box>
  );
}

export default SoftwaresPatrimonioComponent;
