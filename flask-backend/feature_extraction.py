import re
import os

# Função para remover comentários do código Java
def remove_comments(code):
    code = re.sub(r"//.*", "", code)  # Remove comentários de linha
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)  # Remove blocos de comentário
    return code

# Verifica se há validação antes do uso
def has_validation_before(lines, i, validation_keywords):
    for j in range(max(0, i - 3), i):
        if any(keyword in lines[j] for keyword in validation_keywords):
            return True
    return False

def extract_unchecked_exceptions(code):
    features = {
        'num_null_pointer': 0,
        'num_array_index_out_of_bounds': 0,
        'num_string_index_out_of_bounds': 0,
        'num_arithmetic_exceptions': 0,
        'num_class_cast_exceptions': 0,
        #'num_illegal_argument_exceptions': 0,
        'num_number_format_exceptions': 0,
        'num_concurrent_modification_exceptions': 0,
        'Bugs': ''  
    }
    
    if not code:
        print("Código vazio ou não encontrado.")
        return features

    code = remove_comments(code)
    lines = code.split("\n")

    for i, line in enumerate(lines):
        lines[i] = line.strip()

        # NullPointerException → Uso inseguro de objetos nulos
        if "." in line and "(" in line:  # Indica uma chamada de método
            var_name_match = re.search(r"(\w+)\.", line)  # Captura a variável antes do ponto
            if var_name_match:
                var_name = var_name_match.group(1)
            
            # Verifica se há uma validação explícita para essa variável
            if not has_validation_before(lines, i, [f"{var_name} != null", f"{var_name} == null"]):
                features['num_null_pointer'] += 1


        # ArrayIndexOutOfBoundsException → Acesso sem verificação ao índice do array
        if "[" in line and "]" in line:
            if not has_validation_before(lines, i, ["if(", "for(", "while("]):
                features['num_array_index_out_of_bounds'] += 1

        # StringIndexOutOfBoundsException → Índice inválido em operações com String
        if any(op in line for op in [".charAt(", ".substring("]):
            if not has_validation_before(lines, i, ["if(", ".length()"]):
                features['num_string_index_out_of_bounds'] += 1  

        # ArithmeticException → Divisão por zero
        if "/ 0" in line or "/0" in line:
            features['num_arithmetic_exceptions'] += 1

        # ClassCastException → Cast inseguro de classes
        if re.search(r"\(\s*[A-Z][a-zA-Z0-9_]*\s*\)", line):  # Detecta casts explícitos
            prev_line = lines[i - 1].strip() if i > 0 else ""  # Obtém a linha anterior
            if "instanceof" not in prev_line:  # Só conta se não houver instanceof antes
                features['num_class_cast_exceptions'] += 1


        # IllegalArgumentException → Argumento inválido passado para métodos
        #if "throw new IllegalArgumentException" in line:
        #   features['num_illegal_argument_exceptions'] += 1

        # NumberFormatException → Conversão inválida de String para número
        if any(op in line for op in ["Integer.parseInt(", "Double.parseDouble(", "Float.parseFloat(", "Short.parseShort(", "Byte.parseByte(", "Long.parseLong("]):
            if not has_validation_before(lines, i, ["try {"]):
                features['num_number_format_exceptions'] += 1  

        # Detectar NumberFormatException em conversão de números hexadecimais
        if re.search(r"if\s*\(\s*hexDigits\s*>\s*(8|16)\s*\)", line):
            prev_line = lines[i - 1].strip() if i > 0 else ""  # Linha anterior para contexto
            next_line = lines[i + 1].strip() if i < len(lines) - 1 else ""  # Próxima linha
            
            # Verificar se a condição firstSigDigit > '7' está presente
            if "firstSigDigit" not in next_line and "firstSigDigit" not in prev_line:
                features['num_number_format_exceptions'] += 1  # Contar possível erro

        # ConcurrentModificationException → Modificação de coleção durante iteração
        if ".remove(" in line or ".add(" in line:
            if has_validation_before(lines, i, ["for(", "while("]):
                features['num_concurrent_modification_exceptions'] += 1  

    return features