import React, { useState } from 'react';
import { Box, Button, FormControl, FormLabel, Heading, Input, VStack, useToast, Text, Container, Center } from '@chakra-ui/react';
import { LockIcon } from '@chakra-ui/icons';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/api';

function Login({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  const handleLogin = async () => {
    if (!username || !password) {
      toast({ title: 'Erro', description: 'Preencha username e senha', status: 'error' });
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/auth/login`, {
        username,
        password
      });

      const { access_token, usuario } = response.data;
      
      // Armazenar token no localStorage
      localStorage.setItem('token', access_token);
      localStorage.setItem('usuario', JSON.stringify(usuario));
      
      toast({ title: 'Bem-vindo!', description: `Login como ${usuario.nome}`, status: 'success' });
      
      // Chamar callback para atualizar o estado da app
      onLoginSuccess(usuario);
    } catch (error) {
      toast({ title: 'Erro', description: error.response?.data?.erro || 'Falha no login', status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleLogin();
    }
  };

  return (
    <Center h="100vh" bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
      <Container maxW="sm">
        <Box bg="white" shadow="lg" rounded="lg" p={8}>
          <VStack spacing={6}>
            <Box textAlign="center">
              <LockIcon w={12} h={12} color="teal.500" mb={4} />
              <Heading size="lg" color="gray.800">TI Manager</Heading>
              <Text color="gray.600" fontSize="sm" mt={2}>Inventário de Ativos</Text>
            </Box>

            <FormControl isRequired>
              <FormLabel color="gray.700">Usuário</FormLabel>
              <Input
                type="text"
                placeholder="admin"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onKeyPress={handleKeyPress}
                bg="gray.50"
                borderColor="gray.300"
              />
            </FormControl>

            <FormControl isRequired>
              <FormLabel color="gray.700">Senha</FormLabel>
              <Input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyPress={handleKeyPress}
                bg="gray.50"
                borderColor="gray.300"
              />
            </FormControl>

            <Button
              w="full"
              colorScheme="teal"
              size="lg"
              onClick={handleLogin}
              isLoading={loading}
            >
              Entrar
            </Button>

            <Box textAlign="center" w="full">
              <Text fontSize="xs" color="gray.500">
                Desenvolvido pela Refricril
              </Text>
            </Box>
          </VStack>
        </Box>
      </Container>
    </Center>
  );
}

export default Login;
