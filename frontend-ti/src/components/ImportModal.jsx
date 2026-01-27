import React, { useRef, useState } from 'react';
import {
  Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalCloseButton,
  Button, Text, VStack, useToast, Alert, AlertIcon, Box, List, ListItem
} from '@chakra-ui/react';
import { AttachmentIcon } from '@chakra-ui/icons';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/api/import';

const ImportModal = ({ isOpen, onClose, type, onSuccess }) => {
  const fileInputRef = useRef();
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const toast = useToast();

  const handleUpload = async () => {
    const file = fileInputRef.current.files[0];
    if (!file) {
      toast({ title: 'Selecione um arquivo .csv', status: 'warning' });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    setReport(null);

    try {
      // type deve ser: 'celulares', 'emails' ou 'softwares'
      const res = await axios.post(`${API_URL}/${type}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setReport(res.data);
      if (onSuccess) onSuccess();
      toast({ title: 'Importação finalizada', status: 'success' });
      
    } catch (error) {
      toast({ title: 'Erro na importação', description: error.response?.data?.erro || 'Erro servidor', status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Importar {type.toUpperCase()} via CSV</ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6}>
          <VStack spacing={4} align="stretch">
            <Alert status="info" fontSize="sm">
              <AlertIcon />
              <Box>
                O arquivo deve ser <b>.csv</b> (separado por ponto e vírgula).
                <br />
                {type === 'celulares' && "Colunas: patrimonio; filial; modelo; imei; numero; responsavel"}
                
                {/* ATUALIZADO AQUI: */}
                {type === 'emails' && (
                  <>
                    Colunas: <b>endereco; pat_pc; pat_cel; conta google; conta zimbra; conta microsoft; senha google; senha zimbra; senha microsoft</b>
                    <br/>
                    <Text fontSize="xs" mt={1}>
                      * Preencha <b>pat_pc</b> OU <b>pat_cel</b> para vincular.<br/>
                      * Nas contas, use <b>Sim</b> ou <b>1</b> para criar.
                    </Text>
                  </>
                )}
                
                {type === 'softwares' && "Colunas: nome; pat_computador; chave_licenca; dt_vencimento"}
              </Box>
            </Alert>

            <input 
              type="file" 
              accept=".csv" 
              ref={fileInputRef} 
              style={{ border: '1px solid #ccc', padding: '10px', width: '100%' }}
            />

            <Button 
              leftIcon={<AttachmentIcon />} 
              colorScheme="blue" 
              isLoading={loading}
              onClick={handleUpload}
            >
              Enviar e Processar
            </Button>

            {report && (
              <Box bg="gray.50" p={3} borderRadius="md" w="100%">
                <Text fontWeight="bold" color="green.600">{report.msg}</Text>
                {report.erros && report.erros.length > 0 && (
                  <Box mt={2}>
                    <Text fontWeight="bold" color="red.500">Erros ({report.erros.length}):</Text>
                    <List spacing={1} maxH="150px" overflowY="auto" fontSize="xs" color="red.600">
                      {report.erros.map((err, i) => <ListItem key={i}>• {err}</ListItem>)}
                    </List>
                  </Box>
                )}
              </Box>
            )}
          </VStack>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};

export default ImportModal;