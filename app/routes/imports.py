import csv
import io
import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import db, Asset, Celular, Software, Email
from datetime import datetime

bp_imports = Blueprint('imports', __name__)

# --- IMPORTAÇÃO DE ATIVOS (COMPUTADORES) ---
@bp_imports.route('/api/import/assets', methods=['POST'])
@jwt_required()
def import_assets():
    """Importar computadores/patrimonios do CSV com todos os dados"""
    try:
        if 'file' not in request.files: 
            return jsonify({"erro": "Nenhum arquivo"}), 400
        
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({"erro": "Arquivo vazio"}), 400
        
        content = file.stream.read().decode("UTF8", errors='ignore')
        if not content:
            return jsonify({"erro": "Arquivo sem conteúdo"}), 400
        
        delimiter = ';' if ';' in content.split('\n')[0] else ','
        stream = io.StringIO(content, newline=None)
        csv_input = csv.DictReader(stream, delimiter=delimiter)
        
        sucessos = 0
        erros = []
        linha = 1
        
        for row in csv_input:
            linha += 1
            if not row or all(not v for v in row.values()):
                continue
                
            # Normaliza chaves (remove espaços, minúsculo, caracteres especiais)
            row_norm = {}
            for k, v in row.items():
                if not k:
                    continue
                # Normalizar: minúsculo, remove espaços, caracteres especiais
                key_clean = k.strip().lower().replace('ç', 'c').replace('ã', 'a').replace('õ', 'o').replace('.', '').replace(' ', '_').lstrip('0123456789_')
                row_norm[key_clean] = v.strip() if v else ''
            
            # Campo obrigatório: PAT (Patrimônio)
            patrimonio = row_norm.get('pat', '')
            if not patrimonio:
                continue  # Pula linhas vazias
            
            # Verifica duplicidade
            if Asset.query.filter_by(patrimonio=patrimonio).first():
                erros.append(f"Linha {linha}: Ativo {patrimonio} já existe")
                continue
            
            # Mapeia campos de identificação
            filial = row_norm.get('centro_de_custo_filial', '') or row_norm.get('filial', '')
            responsavel = row_norm.get('em_uso', '') or row_norm.get('responsavel', '')
            tipo = row_norm.get('tipo', 'Desktop')
            modelo = row_norm.get('modelo', '')
            hostname = row_norm.get('hostname', '')
            observacoes = row_norm.get('observacao', '')
            
            # Mapeia dados técnicos/segurança
            anydesk = row_norm.get('anydesk', '')
            senha_bios = row_norm.get('senha_bios', '')
            senha_windows = row_norm.get('senha_windows', '')
            bitlocker = row_norm.get('bitlocker', '')
            
            # Mapeia informações de rede
            vpn = row_norm.get('vpn', '')
            senha_vpn = row_norm.get('senha_vpn', '')
            
            # Tenta extrair IPs dos campos de rede
            gix_remoto = row_norm.get('gix_remoto_10_1_1_134_135', '') or row_norm.get('gix_remoto', '')
            duapi = row_norm.get('duapi_10_1_1_122', '') or row_norm.get('duapi', '')
            dominio = row_norm.get('dominio_10_1_1_129', '') or row_norm.get('dominio', '')
            
            # Mapeia informações de comunicação (emails/softphone)
            softphone = row_norm.get('softphone', '')
            zimbra = row_norm.get('zimbra', '')
            conta_google = row_norm.get('conta_google', '')
            email_secundario = row_norm.get('email_secundario', '')
            conta_google_2 = row_norm.get('conta_google_2', '')
            
            # Criar ativo
            asset = Asset(
                patrimonio=patrimonio,
                tipo='Notebook' if tipo.lower() in ['notebook', 'note'] else 'Desktop',
                modelo=modelo or 'Não informado',
                filial=filial or 'Não informada',
                responsavel=responsavel or 'Não atribuído',
                status='Ativo',
                observacoes=observacoes or 'Importado via CSV',
                anydesk=anydesk,
                especificacoes={
                    'hostname': hostname,
                    'gix_remoto': gix_remoto,
                    'duapi': duapi,
                    'dominio': dominio,
                    'vpn': vpn,
                    'senha_bios': senha_bios,
                    'senha_windows': senha_windows,
                    'senha_vpn': senha_vpn,
                    'bitlocker': bitlocker,
                    'softphone': softphone,
                    'zimbra': zimbra,
                    'conta_google': conta_google,
                    'email_secundario': email_secundario,
                    'conta_google_2': conta_google_2
                }
            )
            asset.atualizado_em = datetime.now()
            
            try:
                db.session.add(asset)
                db.session.flush()
                asset_id = asset.id
                
                # Criar softwares vinculados
                softwares_list = []
                for i in range(1, 4):
                    pat_software = row_norm.get(f'pat_software_{i}', '')
                    nome_software = row_norm.get(f'software_{i}', '')
                    
                    if pat_software and nome_software:
                        soft = Software(
                            nome=nome_software,
                            patrimonio=pat_software,
                            asset_id=asset_id,
                            status='Instalado'
                        )
                        softwares_list.append(soft)
                
                # Adicionar softwares ao asset
                if softwares_list:
                    for soft in softwares_list:
                        db.session.add(soft)
                
                # Criar emails/comunicação se existirem
                emails_list = []
                email_fields = {
                    'softphone': softphone,
                    'zimbra': zimbra,
                    'conta_google': conta_google,
                    'email_secundario': email_secundario,
                    'conta_google_2': conta_google_2
                }
                
                for tipo_email, email_valor in email_fields.items():
                    if email_valor and '@' in email_valor:
                        email_obj = Email(
                            endereco=email_valor,
                            tipo=tipo_email,
                            asset_id=asset_id,
                            ativo=True
                        )
                        emails_list.append(email_obj)
                
                if emails_list:
                    for email_obj in emails_list:
                        db.session.add(email_obj)
                
                db.session.commit()
                sucessos += 1
                
            except Exception as e:
                db.session.rollback()
                erros.append(f"Linha {linha}: Erro ao inserir - {str(e)}")
                continue
        
        return jsonify({
            "msg": f"Importação concluída! {sucessos} ativos criados.",
            "sucessos": sucessos,
            "total_erros": len(erros),
            "erros": erros[:10]  # Retorna até 10 erros para não sobrecarregar a resposta
        })
        
    except Exception as e:
        return jsonify({"erro": f"Erro na importação: {str(e)}"}), 500

def parse_date(date_str):
    if not date_str: return None
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%Y/%m/%d'):
        try: return datetime.strptime(date_str, fmt)
        except ValueError: continue
    return None

def is_valid_email(text):
    return text and '@' in text and '.' in text

@bp_imports.route('/api/import/celulares', methods=['POST'])
def import_celulares():
    """Importar celulares: PAT, Filial, Em uso, AnyDesk, Senha, Cel. Princ., Cel. Sec., Conta Google, Sub Tipo, Marca, Modelo, Propriedade, Serial 1, IMEI 1, IMEI 2"""
    if 'file' not in request.files: 
        return jsonify({"erro": "Nenhum arquivo"}), 400
    
    file = request.files['file']
    content = file.stream.read().decode("UTF8")
    delimiter = ';' if ';' in content.split('\n')[0] else ','
    stream = io.StringIO(content, newline=None)
    csv_input = csv.DictReader(stream, delimiter=delimiter)
    
    sucessos = 0
    erros = []
    linha = 1
    
    for row in csv_input:
        linha += 1
        # Normaliza chaves (remove espaços, pontos e põe minúsculo)
        row = {k.strip().lower().replace('º', 'o').replace('.', '').replace(' ', '_'): v.strip() for k, v in row.items() if k}
        
        # Campo obrigatório: PAT
        patrimonio = row.get('pat') or row.get('patrimonio')
        if not patrimonio: 
            erros.append(f"Linha {linha}: Patrimônio vazio")
            continue
            
        # Verifica duplicidade
        if Celular.query.filter_by(patrimonio=patrimonio).first():
            erros.append(f"Linha {linha}: Celular {patrimonio} já existe")
            continue
        
        # Mapeia todos os campos do CSV
        filial = row.get('filial', '')
        em_uso = row.get('em_uso', '')
        anydesk = row.get('anydesk', '')
        senha = row.get('senha', '')
        cel_princ = row.get('cel_princ', '') or row.get('numero_principal', '')
        cel_sec = row.get('cel_sec', '') or row.get('numero_secundario', '')
        conta_google = row.get('conta_google_principal', '') or row.get('conta_google', '')
        sub_tipo = row.get('sub_tipo', '')
        marca = row.get('marca', '')
        modelo = row.get('modelo', '')
        propriedade = row.get('propriedade', '')
        serial_1 = row.get('serial_1', '')
        imei_1 = row.get('imei_1', '') or row.get('imei', '')
        imei_2 = row.get('imei_2', '')
        
        # Inserir celular com todos os campos
        celular = Celular(
            patrimonio=patrimonio,
            filial=filial,
            modelo=modelo,
            imei=imei_1,
            numero=cel_princ,
            responsavel=em_uso,
            status="Em Uso" if em_uso else row.get('status', 'Reserva'),
            observacoes="Importado via CSV"
        )
        celular.atualizado_em = datetime.now()
        db.session.add(celular)
        db.session.commit()
        sucessos += 1
        
    return jsonify({"msg": f"Processado! {sucessos} celulares criados.", "erros": erros})

# --- IMPORTAÇÃO DE EMAILS CORRIGIDA E ROBUSTA ---
@bp_imports.route('/api/import/emails', methods=['POST'])
def import_emails():
    if 'file' not in request.files: return jsonify({"erro": "Sem arquivo"}), 400
    
    # 1. Detectar Separador (Vírgula ou Ponto e Vírgula)
    file_content = request.files['file'].stream.read().decode("UTF8")
    first_line = file_content.split('\n')[0]
    delimiter = ';' if ';' in first_line else ','
    
    stream = io.StringIO(file_content, newline=None)
    csv_input = csv.DictReader(stream, delimiter=delimiter)
    
    sucessos = 0
    erros = []
    linha = 1

    for row in csv_input:
        linha += 1
        # Normaliza chaves (remove espaços e põe minusculo)
        row_norm = {k.strip().lower(): v.strip() for k, v in row.items() if k}
        
        # Tenta pegar PATs
        pat_pc = row_norm.get('pat_pc')
        pat_cel = row_norm.get('pat_cel')
        
        # Se não tiver PAT nenhum, pula (regra de negócio)
        if not pat_pc and not pat_cel:
            erros.append(f"Linha {linha}: Sem vínculo (PAT PC ou Celular vazios). Ignorado.")
            continue

        # Busca o Asset no Banco
        asset_found = None

        if pat_pc:
            asset_found = Asset.query.filter_by(patrimonio=pat_pc).first()
            if not asset_found and not pat_cel:
                erros.append(f"Linha {linha}: PC '{pat_pc}' não encontrado no sistema.")
                continue
        
        if not asset_found and pat_cel:
            asset_found = Celular.query.filter_by(patrimonio=pat_cel).first()
            if not asset_found:
                erros.append(f"Linha {linha}: Celular '{pat_cel}' não encontrado.")
                continue

        if not asset_found: continue

        # Definição das colunas
        tipos = [
            ('google', 'conta google', 'senha google'),
            ('zimbra', 'conta zimbra', 'senha zimbra'),
            ('microsoft', 'conta microsoft', 'senha microsoft')
        ]
        
        # Pega endereço base (caso usem Sim/Não)
        email_base_col = row_norm.get('endereço') or row_norm.get('endereco')

        for tipo_db, col_conta, col_senha in tipos:
            valor_conta = row_norm.get(col_conta, '')
            valor_senha = row_norm.get(col_senha, '')
            
            email_final = None
            
            # CENÁRIO 1: O usuário colocou o e-mail direto na coluna da conta (Ex: joao@gmail.com)
            if is_valid_email(valor_conta):
                email_final = valor_conta
            
            # CENÁRIO 2: Usuário colocou "Sim" e o e-mail está na primeira coluna
            elif valor_conta.lower() in ['sim', 's', '1', 'true', 'ativo'] and is_valid_email(email_base_col):
                email_final = email_base_col

            # Se achamos um e-mail válido para criar
            if email_final:
                # Verifica duplicidade
                if Email.query.filter_by(endereco=email_final, tipo=tipo_db).first():
                    erros.append(f"Linha {linha}: {email_final} ({tipo_db}) já existe.")
                    continue

                email = Email(
                    endereco=email_final,
                    tipo=tipo_db,
                    asset_id=asset_found.id,
                    usuario=email_final.split('@')[0],
                    senha=valor_senha, # Salva a senha específica dessa conta
                    recuperacao="",
                    ativo=True
                )
                email.atualizado_em = datetime.now()
                db.session.add(email)
                db.session.commit()
                sucessos += 1

    return jsonify({"msg": f"Sucesso! {sucessos} contas importadas.", "erros": erros})

@bp_imports.route('/api/import/softwares', methods=['POST'])
def import_softwares():
    if 'file' not in request.files: return jsonify({"erro": "Sem arquivo"}), 400
    
    content = request.files['file'].stream.read().decode("UTF8")
    delimiter = ';' if ';' in content.split('\n')[0] else ','
    stream = io.StringIO(content, newline=None)
    csv_input = csv.DictReader(stream, delimiter=delimiter)
    
    sucessos = 0
    erros = []
    linha = 1

    for row in csv_input:
        linha += 1
        row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
        
        nome = row.get('nome')
        pat_pc = row.get('pat_computador') or row.get('pat_pc') # Aceita os dois nomes
        
        if not nome or not pat_pc:
            erros.append(f"Linha {linha}: Nome ou PAT vazio")
            continue

        pc = Asset.query.filter_by(patrimonio=pat_pc).first()
        if not pc:
            erros.append(f"Linha {linha}: PC {pat_pc} não existe")
            continue

        software = Software(
            nome=nome,
            asset_id=pc.id,
            versao=row.get('versao', ''),
            tipo_licenca=row.get('tipo_licenca', 'Individual'),
            chave_licenca=row.get('chave_licenca', ''),
            dt_instalacao=parse_date(row.get('dt_instalacao')),
            dt_vencimento=parse_date(row.get('dt_vencimento')),
            custo_anual=float(row.get('custo_anual', 0) or 0),
            ativo=True
        )
        software.atualizado_em = datetime.now()
        db.session.add(software)
        db.session.commit()
        sucessos += 1

    return jsonify({"msg": f"Importado: {sucessos} softwares.", "erros": erros})