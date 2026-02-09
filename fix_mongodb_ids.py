"""Script para corrigir todas as referências ._id para .id no frontend"""
import os
import re

def fix_mongodb_ids(directory):
    """Recursivamente corrige todas as referências ._id para .id em arquivos JSX"""
    
    for root, dirs, files in os.walk(directory):
        # Ignorar node_modules e dist
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', '.git']]
        
        for file in files:
            if file.endswith('.jsx'):
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Contar quantas vezes _id aparece
                count = len(re.findall(r'\._id', content))
                
                # Corrigir ._id para .id (mas não alterar ._id dentro de strings se possível)
                # Usar lookahead/lookbehind para evitar caracteres de palavra
                new_content = re.sub(r'(\s|\(|\[|\{|\.)_id(?![\w])', r'\1id', content)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"✅ {filepath}: {count} ocorrências corrigidas")
                else:
                    print(f"⏭️  {filepath}: nenhuma mudança necessária")

if __name__ == '__main__':
    frontend_dir = r'c:\Users\User\Documents\Programa\inventario_ti\frontend-ti\src'
    
    print("="*70)
    print("🔧 CORRIGINDO REFERÊNCIAS MONGODB IDS PARA POSTGRESQL IDS")
    print("="*70)
    print()
    
    fix_mongodb_ids(frontend_dir)
    
    print()
    print("="*70)
    print("✅ CORRIGIDO! Todas as referências ._id foram alteradas para .id")
    print("="*70)
