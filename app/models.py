from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON, ARRAY

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    filial = db.Column(db.String(100))
    permissoes = db.Column(ARRAY(db.String), default=list)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'username': self.username,
            'nome': self.nome,
            'email': self.email,
            'filial': self.filial,
            'permissoes': self.permissoes or [],
            'ativo': self.ativo
        }


class Filial(db.Model):
    __tablename__ = 'filiais'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False, index=True)
    endereco = db.Column(db.String(255))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    telefone = db.Column(db.String(20))
    ativo = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'nome': self.nome,
            'endereco': self.endereco,
            'cidade': self.cidade,
            'estado': self.estado,
            'telefone': self.telefone,
            'ativo': self.ativo
        }


class Asset(db.Model):
    __tablename__ = 'assets'
    
    id = db.Column(db.Integer, primary_key=True)
    patrimonio = db.Column(db.String(50), unique=True, nullable=False, index=True)
    tipo = db.Column(db.String(50), nullable=False)
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    numero_serie = db.Column(db.String(100))
    filial = db.Column(db.String(100))
    setor = db.Column(db.String(100))
    responsavel = db.Column(db.String(120))
    status = db.Column(db.String(50), default='Ativo')
    
    # Campos específicos por tipo
    especificacoes = db.Column(JSON)
    
    observacoes = db.Column(db.Text)
    dt_compra = db.Column(db.Date)
    dt_garantia = db.Column(db.Date)
    valor = db.Column(db.Numeric(10, 2))
    fornecedor = db.Column(db.String(120))
    nota_fiscal = db.Column(db.String(50))
    anydesk = db.Column(db.String(50))
    
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    softwares = db.relationship('Software', back_populates='asset', cascade='all, delete-orphan')
    emails = db.relationship('Email', back_populates='asset', cascade='all, delete-orphan')
    
    def to_dict(self, include_relationships=False):
        data = {
            'id': str(self.id),
            'patrimonio': self.patrimonio,
            'tipo': self.tipo,
            'marca': self.marca,
            'modelo': self.modelo,
            'numero_serie': self.numero_serie,
            'filial': self.filial,
            'setor': self.setor,
            'responsavel': self.responsavel,
            'status': self.status,
            'observacoes': self.observacoes,
            'dt_compra': self.dt_compra.isoformat() if self.dt_compra else None,
            'dt_garantia': self.dt_garantia.isoformat() if self.dt_garantia else None,
            'valor': float(self.valor) if self.valor else None,
            'fornecedor': self.fornecedor,
            'nota_fiscal': self.nota_fiscal,
            'anydesk': self.anydesk,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }
        
        # Adicionar especificações
        if self.especificacoes:
            data.update(self.especificacoes)
        
        # Adicionar relacionamentos se solicitado
        if include_relationships:
            data['softwares'] = [software.to_dict() for software in self.softwares] if self.softwares else []
            data['emails'] = [email.to_dict() for email in self.emails] if self.emails else []
            
        return data


class Celular(db.Model):
    __tablename__ = 'celulares'
    
    id = db.Column(db.Integer, primary_key=True)
    patrimonio = db.Column(db.String(50), unique=True, nullable=False, index=True)
    filial = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    imei = db.Column(db.String(20), unique=True)
    numero = db.Column(db.String(20))
    operadora = db.Column(db.String(50))
    responsavel = db.Column(db.String(120))
    status = db.Column(db.String(50), default='Ativo')
    observacoes = db.Column(db.Text)
    dt_compra = db.Column(db.Date)
    valor = db.Column(db.Numeric(10, 2))
    
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'patrimonio': self.patrimonio,
            'filial': self.filial,
            'modelo': self.modelo,
            'imei': self.imei,
            'numero': self.numero,
            'operadora': self.operadora,
            'responsavel': self.responsavel,
            'status': self.status,
            'observacoes': self.observacoes,
            'dt_compra': self.dt_compra.isoformat() if self.dt_compra else None,
            'valor': float(self.valor) if self.valor else None,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }


class Software(db.Model):
    __tablename__ = 'softwares'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    versao = db.Column(db.String(50))
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    tipo_licenca = db.Column(db.String(50))
    chave_licenca = db.Column(db.String(255))
    dt_instalacao = db.Column(db.Date)
    dt_vencimento = db.Column(db.Date)
    custo_anual = db.Column(db.Numeric(10, 2))
    renovacao_automatica = db.Column(db.Boolean, default=False)
    observacoes = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    asset = db.relationship('Asset', back_populates='softwares')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'nome': self.nome,
            'versao': self.versao,
            'asset_id': str(self.asset_id),
            'asset_patrimonio': self.asset.patrimonio if self.asset else None,
            'tipo_licenca': self.tipo_licenca,
            'chave_licenca': self.chave_licenca,
            'dt_instalacao': self.dt_instalacao.isoformat() if self.dt_instalacao else None,
            'dt_vencimento': self.dt_vencimento.isoformat() if self.dt_vencimento else None,
            'custo_anual': float(self.custo_anual) if self.custo_anual else None,
            'renovacao_automatica': self.renovacao_automatica,
            'observacoes': self.observacoes,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }


class Email(db.Model):
    __tablename__ = 'emails'
    
    id = db.Column(db.Integer, primary_key=True)
    endereco = db.Column(db.String(120), unique=True, nullable=False, index=True)
    tipo = db.Column(db.String(50), nullable=False)  # google, zimbra
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'))
    usuario = db.Column(db.String(120))
    senha = db.Column(db.String(255))  # Criptografada
    recuperacao = db.Column(db.String(120))
    observacoes = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    asset = db.relationship('Asset', back_populates='emails')
    
    def to_dict(self, include_password=False):
        data = {
            'id': str(self.id),
            'endereco': self.endereco,
            'tipo': self.tipo,
            'asset_id': str(self.asset_id) if self.asset_id else None,
            'asset_patrimonio': self.asset.patrimonio if self.asset else None,
            'usuario': self.usuario,
            'recuperacao': self.recuperacao,
            'observacoes': self.observacoes,
            'ativo': self.ativo,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }
        
        if include_password:
            data['senha'] = self.senha
        
        return data


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    usuario_nome = db.Column(db.String(120))
    acao = db.Column(db.String(50), nullable=False)  # Create, Update, Delete
    entidade = db.Column(db.String(50), nullable=False)  # Asset, Celular, Software, Email
    entidade_id = db.Column(db.String(50))
    descricao = db.Column(db.Text)
    dados_antes = db.Column(JSON)
    dados_depois = db.Column(JSON)
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'usuario_id': str(self.usuario_id) if self.usuario_id else None,
            'usuario_nome': self.usuario_nome,
            'acao': self.acao,
            'entidade': self.entidade,
            'entidade_id': self.entidade_id,
            'descricao': self.descricao,
            'dados_antes': self.dados_antes,
            'dados_depois': self.dados_depois,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
