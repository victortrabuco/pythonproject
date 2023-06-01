# coding: latin-1

import sqlite3
import json
import requests
import os
from os.path    import abspath
from getpass    import getpass
from datetime   import datetime
from time       import sleep
from os         import system, path
from zipfile    import ZipFile
system("cls")


def executa_comando(comando, valores=()):
    global conexao
    cursor = conexao.cursor()
    cursor.execute(comando, valores)
    resultado = cursor.fetchall()
    cursor.close()
    conexao.commit()
    return resultado

def valida_input(mensagem, tipo, valores_aceitos=None):
    while True:
        try:
            selecao = tipo(input(mensagem))
            if valores_aceitos:
                if not selecao in valores_aceitos:
                    raise Exception(f"Digite apenas um dos valores {str(valores_aceitos)}")
            break
        except ValueError:
            print(f"Digite um valor válido!")
        except Exception as erro:
            print(erro)
    return selecao

#LUCAS LORRAN
def agendar_manutencao():
    placa = valida_input("Digite a placa do carro (sem espaços e/ou traços): ", str)
    id_carro = relatorio_carros(placa)
    if not id_carro:
        print("Carro não encontrado! Tente novamente!\n")
        agendar_manutencao()
    descricao = valida_input("Digite a descricao da manutencao: ", str)
    data_manutencao = valida_input("Digite a data do agendamento. Ex dd/mm/aaaa: ", str)
    executa_comando("INSERT INTO manutencao_carros(carroid, descricao_problema, data_manutencao) VALUES (?, ?, ?)", (id_carro, descricao, data_manutencao, ))
    print("\nAgendamento realizado com sucesso!")
    valida_input("Digite 0 para voltar ao menu: ", int, [0])

#LUCAS LORRAN
def relatorio_agendamentos_manutencao():
    campos = {
                "Marca Modelo": 4,
                "Placa": 7,
                "Descricao da manutencao": 1,
                "Data do agendamento": 2}
    
    resultado = executa_comando(f"SELECT * FROM manutencao_carros a INNER JOIN carros b ON a.carroid = b.carroid")
    print(f"\nAgendamentos de manutenção encontrados: {len(resultado)}\n")
    for tupla in resultado:
        for coluna, indice in campos.items():
            print(f"{coluna}: {tupla[indice]}")
        print("")
    print("")

    valida_input("Digite 0 para voltar ao menu: ", int, [0])

#LUCAS LORRAN
#Victor Trabuco - mudanças realizadas 13-05
def agendar_teste_drive():
    placa = valida_input("Digite a placa do carro (sem espaços e/ou traços): ", str)
    id_carro = relatorio_carros(placa)
    if not id_carro:
        print("Carro não encontrado! Tente novamente!")
        agendar_teste_drive()
    cpf = valida_input("\nDigite o CPF do cliente (sem pontos, traços ou espaços): ", str)
    id_cliente = relatorio_clientes(cpf)
    if not id_cliente:
        print("Cliente não cadastrado! Faça o cadastro do cliente")
        cadastra_cliente(cpf)
        id_cliente = relatorio_clientes(cpf)
        
    data_teste_drive = valida_input("Digite a data do teste drive. Ex dd/mm/aaaa: ", str)
    horario_teste_drive = valida_input("Digite o horario do teste drive. Ex hh:mm: ", str)

    executa_comando("INSERT INTO testes_drive(carroid, clienteid, data_teste_drive, horario_teste_drive) VALUES (?, ?, ?, ?)", (id_carro, id_cliente, data_teste_drive, horario_teste_drive, ))
    print("\nAgendamento realizado com sucesso!")

    valida_input("\nDigite 0 para voltar ao menu: ", int, [0])


#LUCAS LORRAN
#Victor Trabuco - mudanças realizadas 13-05
def relatorio_agendamentos_teste_drive():
    campos = {
                "Marca e modelo": 5,
                "Ano Modelo": 7,
                "Placa": 8,
                "Nome do cliente": 13,
                "Data do teste drive": 2,
                "Hora do teste drive": 3
                }
    query = "SELECT * FROM testes_drive a INNER JOIN carros b ON a.carroid = b.carroid INNER JOIN clientes c on a.clienteid = c.clienteid"
    resultado = executa_comando(query)
    print(f"\nTotal de teste drives agendados: {len(resultado)}\n")
    for tupla in resultado:
        for coluna, indice in campos.items():
            print(f"{coluna}: {tupla[indice]}")
        print("")
    print("")
    
    valida_input("Digite 0 para voltar ao menu: ", int, [0])

def cadastra_usuario():
    novo_usuario = valida_input("Digite o nome do usuario: ", str)
    while True:
        nova_senha = getpass("Digite a senha do usuario: ")
        if not nova_senha == getpass("Confirme a senha: "):
            print("As senhas não coincidem!")
            continue
        else:
            break
    resultado = executa_comando("SELECT COUNT(usuario) FROM usuarios WHERE usuario = ?", (novo_usuario, ))
    if resultado[0][0] > 0:
        print("Esse nome de usuário já existe! Por favor, tente novamente")
        cadastra_usuario()
    try:
        executa_comando("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (novo_usuario, nova_senha, ))
        return
    except:
        print("Ocorreu um erro ao cadastrar o usuario! Por favor, tente novamente!")
        cadastra_usuario()
        
def valida_login():
    while True:
        usuario = valida_input("Digite seu usuario: ", str)
        senha = getpass("Digite sua senha: ")
        resultado = executa_comando("SELECT senha FROM usuarios WHERE usuario = ?", (usuario, ))
        system("cls")
        if not len(resultado):
            print("Usuario não encontrado!")
            continue
        if not resultado[0][0] == senha:
            print("Senha incorreta!")
            continue
        return usuario
        
def cadastra_carro():
    nome_carro = valida_input("Digite a marca e modelo do carro: ", str)
    quilometragem =  valida_input("Digite a quiilometragem: ", int)
    ano =  valida_input("Digite o ano do modelo: ", int)
    placa = valida_input("Digite a placa do carro (sem espaços e/ou traços): ", str)
    valor_compra = valida_input("Digite o valor de compra: ", float)
    valor_sugerido = valor_compra + (valor_compra * 0.30)
    executa_comando("INSERT INTO carros (marca_modelo, quilometragem, ano, placa, valor_compra, valor_sugerido, status) VALUES (?, ?, ?, ?, ?, ?, ?)", (nome_carro, quilometragem, ano, placa, valor_compra, valor_sugerido, "Disponivel", ))
    print("\nCarro cadastrado com sucesso!")
    valida_input("Digite 0 para voltar ao menu: ", int, [0])
    
def venda_carro():
    placa = valida_input("Digite a placa do carro (sem espaços e/ou traços): ", str)
    id_carro = relatorio_carros(placa)
    if not id_carro:
        print("Carro não encontrado! Tente novamente!")
        venda_carro()
    cpf = valida_input("\nDigite o CPF do cliente (sem pontos, traços ou espaços): ", str)
    id_cliente = relatorio_clientes(cpf)
    if not id_cliente:
        print("Cliente não cadastrado! Faça o cadastro do cliente")
        cadastra_cliente(cpf)
        id_cliente = relatorio_clientes(cpf)    
    opcao = valida_input("Digite 0 se quer apenas reservar o carro, ou 1 caso seja uma venda: ", int, [0, 1])
    if opcao == 1:
        valor_venda = valida_input("\nDigite o valor de venda: ", float)
        executa_comando("INSERT INTO carros_vendidos (carroid, clienteid, valor_venda) VALUES (?, ?, ?)", (id_carro, id_cliente, valor_venda, ))
        opcao_data = valida_input("Se a data de venda for hoje, digite 1. Caso contrário, digite 0: ", int, [0, 1])
        if not opcao_data:
            data_venda = valida_input("Digite a data de venda do veículo: ", str)
        else:
            data_venda =  datetime.now().strftime("%d/%m/%Y")
        executa_comando("UPDATE carros_vendidos SET data_venda = ? WHERE carroid = ?", (data_venda, id_carro, ))
        executa_comando("UPDATE carros SET status = ? WHERE carroid = ?", ("Vendido", id_carro,))
        print("\nCarro vendido com sucesso!")
    elif opcao == 0:
        executa_comando("UPDATE carros SET status = ? WHERE carroid = ?", ("Reservado", id_carro,))
        print("\nCarro reservado com sucesso!")
    valida_input("Digite 0 para voltar ao menu: ", int, [0])
    

def relatorio_vendidos():
    campos = {
                "Marca e modelo": 5,
                "Quilometragem": 6,
                "Ano Modelo": 7,
                "Valor de compra": 9,
                "Valor sugerido de venda": 10,
                "Valor de venda final": 2,
                "Data da venda": 3,
                "Nome do comprador": 13,
                "Data de Nascimento": 14,
                "CPF": 15}
    query = "SELECT * FROM carros_vendidos a INNER JOIN carros b ON a.carroid = b.carroid INNER JOIN clientes c on a.clienteid = c.clienteid"
    resultado = executa_comando(query)
    print(f"\nTotal de carros vendidos: {len(resultado)}\n")
    for tupla in resultado:
        for coluna, indice in campos.items():
            print(f"{coluna}: {tupla[indice]}")
        print("")
    print("")
    valida_input("Digite 0 para voltar ao menu: ", int, [0])
    
def cadastra_cliente(cpf_informado=None):
    nome = valida_input("Digite o nome completo do cliente: ", str)
    data_nasc = valida_input("Digite a data de nascimento: ", str)
    if not cpf_informado:
        cpf = valida_input("Digite o CPF (sem pontos, traços ou espaços): ", str)
    else:
        cpf = cpf_informado
    executa_comando("INSERT INTO clientes (nome, data_nascimento, cpf) VALUES (?, ?, ?)", (nome, data_nasc, cpf, ))
    print("\nCliente cadastrado com sucesso!")
    if not cpf_informado:
        valida_input("Digite 0 para voltar ao menu: ", int, [0])

def relatorio_carros(placa=()):
    campos = {
                "Marca e Modelo": 1,
                "Quilometragem": 2,
                "Ano modelo": 3,
                "Placa": 4,
                "Valor de compra": 5,
                "Valor sugerido de venda": 6,
                "Status": 7}
    if placa:
        filtro_placa = "AND placa = ?"
        placa = (placa, )
    else:
        filtro_placa = ""
    resultado = executa_comando(f"SELECT * FROM carros WHERE (Status = 'Disponivel' OR Status = 'Reservado') {filtro_placa} ORDER BY marca_modelo ASC", placa)
    print(f"\nTotal de carros disponíveis ou apenas reservados: {len(resultado)}\n")
    for tupla in resultado:
        for coluna, indice in campos.items():
            print(f"{coluna}: {tupla[indice]}")
        if placa:
            return tupla[0]
        print("")
    print("")
    if not placa:
        valida_input("Digite 0 para voltar ao menu: ", int, [0])
    
def relatorio_clientes(cpf=()):
    campos = {
                "Nome": 1,
                "Data de Nascimento": 2,
                "CPF": 3}
    if cpf:
        filtro_cpf = "WHERE cpf = ?"
        cpf = (cpf, )
    else:
        filtro_cpf = ""
    resultado = executa_comando(f"SELECT * FROM clientes {filtro_cpf} ORDER BY nome ASC", cpf)
    print(f"\nClientes encontrados: {len(resultado)}\n")
    for tupla in resultado:
        for coluna, indice in campos.items():
            print(f"{coluna}: {tupla[indice]}")
        if cpf:
            return tupla[0]
        print("")
    print("")
    if not cpf:
        valida_input("Digite 0 para voltar ao menu: ", int, [0])

def importar_json(nome_tabela):
    nome_arquivo = f"{nome_tabela}.json"
    url = f"http://127.0.0.1/arquivos/{nome_arquivo}"
    res = requests.get(url)
    
    with open(nome_arquivo, "wb") as arquivo:
        arquivo.write(res.content)
    arquivo.close()
    
    arquivo_json = json.load(open(nome_arquivo))
    
    colunas_tabelas = {
        "carros":
            ["carroid", 
             "marca_modelo",
             "quilometragem",
             "ano",
             "placa",
             "valor_compra",
             "valor_sugerido",
             "status"],
        "carros_vendidos":
            ["carroid",
             "clienteid",
             "valor_venda",
             "data_venda"],
        "clientes":
            ["clienteid",
             "nome",
             "data_nascimento",
             "cpf"],
        "usuarios":
            ["userid",
             "usuario",
             "senha"],
        "manutencao_carros":
            ["carroid",
             "descricao_problema",
             "data_manutencao"],
        "testes_drive":
            ["carroid",
             "clienteid",
             "data_teste_drive",
             "horario_teste_drive"]}
    
    colunas = colunas_tabelas[nome_tabela]
    for linha in arquivo_json[nome_tabela]:
        valores = tuple(linha[c] for c in colunas)
        valores_query = tuple("?" * len(colunas))
        valores_query = str(valores_query).replace("'", "")
        executa_comando(f"INSERT INTO {nome_tabela} VALUES {str(valores_query)}", valores)
    
    print("Dados importados com sucesso!\n")
    print(f"Tabela: {nome_tabela}")    
    
    resultado = executa_comando(f"SELECT * FROM {nome_tabela}")
    for linha in resultado:
        print("\n")
        for indice, coluna in enumerate(colunas_tabelas[nome_tabela]):
            print(f"{coluna}: {linha[indice]}")
    print("\n")

def exportar_json():
    colunas_tabelas = {
        "carros":
            ["carroid", 
             "marca_modelo",
             "quilometragem",
             "ano",
             "placa",
             "valor_compra",
             "valor_sugerido",
             "status"],
        "carros_vendidos":
            ["carroid",
             "clienteid",
             "valor_venda",
             "data_venda"],
        "clientes":
            ["clienteid",
             "nome",
             "data_nascimento",
             "cpf"],
        "usuarios":
            ["userid",
             "usuario",
             "senha"],
        "manutencao_carros":
            ["carroid",
             "descricao_problema",
             "data_manutencao"],
        "testes_drive":
            ["carroid",
             "clienteid",
             "data_teste_drive",
             "horario_teste_drive"]}
    
    lista_arquivos = []
    for tabela in colunas_tabelas:
        result = {}
        result[tabela] = []
        resultado = executa_comando(f"SELECT * FROM {tabela}")
        for tupla in resultado:
            valores = {}
            for indice, coluna in enumerate(colunas_tabelas[tabela]):
                valores[coluna] = tupla[indice]
            result[tabela].append(valores)
        arquivo_json = open(f"{tabela}.json", "w")
        lista_arquivos.append(f"{tabela}.json")
        resultado_json = json.dumps(result)
        arquivo_json.write(resultado_json)
        arquivo_json.close()
    with ZipFile("resultado.zip", "w") as arquivo_zip:
        for arquivo in lista_arquivos:
            arquivo_zip.write(arquivo)
    arquivo_zip.close()
    print(f"Dados exportados com sucesso!")
    valida_input("Digite 0 para voltar ao menu: ", int, [0])
    
def altera_senha(usuario):
    while True:
        senha = getpass("Digite a nova senha: ")
        if not senha == getpass("Confirme a nova senha:"):
            print("As senhas digitadas não correspondem!\n")
            continue
        else:
            executa_comando("UPDATE usuarios SET senha = ? WHERE usuario = ?", (senha, usuario,))
            system("cls")
            print("Senha alterada com sucesso!")
            valida_input("Digite 0 para voltar ao menu: ", int, [0])
            break

def inicio_sistema():
    print("Primeira execução identificada! Criando estruturas...")
    executa_comando("CREATE TABLE usuarios (userid INTEGER PRIMARY KEY AUTOINCREMENT, usuario VARCHAR(30) NOT NULL, senha VARCHAR(30) NOT NULL)")
    executa_comando("CREATE TABLE carros_vendidos (carroid INTEGER NOT NULL PRIMARY KEY, clienteid INTEGER NOT NULL, valor_venda REAL, data_venda VARCHAR(10))")
    executa_comando("CREATE TABLE clientes (clienteid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, nome VARCHAR(150) NOT NULL, data_nascimento VARCHAR(10), cpf VARCHAR(11))")
    executa_comando("CREATE TABLE carros (carroid INTEGER PRIMARY KEY AUTOINCREMENT, marca_modelo VARCHAR(150), quilometragem INTEGER, ano INTEGER, placa VARCHAR(10), valor_compra REAL, valor_sugerido REAL, status VARCHAR(30))")
    executa_comando("CREATE TABLE manutencao_carros(carroid INTEGER NOT NULL, descricao_problema VARCHAR(200), data_manutencao VARCHAR(10))")
    executa_comando("CREATE TABLE testes_drive(carroid INTEGER NOT NULL, clienteid INTEGER NOT NULL, data_teste_drive VARCHAR(10), horario_teste_drive VARCHAR(6))")
    sleep(5)
    opcao = valida_input("Digite 0 para iniciar uma nova base ou 1 para importar do servidor: ", int, [0, 1])
    if opcao == 0:
        return
    if opcao == 1:
        tabelas = ["usuarios", "carros_vendidos", "clientes", "carros", "manutencao_carros", "testes_drive"]
        for i, tabela in enumerate(tabelas):
            print(f"Importando tabela '{tabela}' [{i + 1} de {len(tabelas)}]")
            importar_json(tabela)
        
def sobre():
    print("Tema do projeto: Sistema de compra e venda de veículos")
    print("Objetivo: Implementar diversas funcionalidades do Python em um sistema\npara controlar a compra e venda de veículos, cadastro de clientes, manutenção e teste drive\n")
    print("Desenvolvedores responsáveis:")
    print("Victor Fomm Trabuco - 2840481913027")
    print("Lucas Lorran Nunes de Oliveira - 2840481823045")
    print("Ciro Anphylo - 2840482023014")
    valida_input("Digite 0 para voltar ao menu: ", int, [0])

caminho_db = abspath("db/Loja.sqlite")

if not path.exists(caminho_db):
    primeira_execucao = True
else:
    primeira_execucao = False
    
conexao = sqlite3.connect(caminho_db)

if primeira_execucao:
    inicio_sistema()

print("Procurou? Achou! - Venda de Veiculos\n")

resultado = executa_comando("SELECT COUNT(usuario) AS count_usuarios FROM usuarios")

if resultado[0][0] == 0:
    print("Primeiro acesso identificado! Por favor cadastre um novo usuario")
    print("Após o cadastro você já poderá fazer login\n")
    cadastra_usuario()
    system("cls")
    print("Cadastro efetuado com sucesso! Agora já é possível fazer login\n")
    
usuario = valida_login()

opcao = 1
while opcao:
    system("cls")
    print("Procurou? Achou! - Venda de Veiculos\n")
    print("[1] Cadastrar carro")
    print("[2] Carros na loja")
    print("[3] Carros vendidos")
    print("[4] Vender carro")
    print("[5] Cadastrar cliente")
    print("[6] Relatório de clientes")
    print("[7] Exportar dados")
    print("[8] Alterar senha de acesso")
    print("[9] Cadastrar novo usuario")
    print("[10] Agendar manutencao no veiculo")
    print("[11] Relatorio de agendamentos de manutencao")
    print("[12] Agendar Teste Drive")
    print("[13] Relatorio de agendamentos de Teste Drive")
    print("[14] Sobre o sistema")
    print("[0] Sair")
    
    opcao = valida_input("\nDigite a opcao desejada: ", int, [i for i in range(0, 15)])
    if not opcao:
        conexao.close()
        system("cls")
        print("Sistema encerrado com sucesso!")
        break
    elif opcao == 1:
        system("cls")
        cadastra_carro()
        continue
    elif opcao == 2:
        system("cls")
        relatorio_carros()
        continue
    elif opcao == 3:
        system("cls")
        relatorio_vendidos()
        continue
    elif opcao == 4:
        system("cls")
        venda_carro()
        continue
    elif opcao == 5:
        system("cls")
        cadastra_cliente()
        continue
    elif opcao == 6:
        system("cls")
        relatorio_clientes()
        continue
    elif opcao == 7:
        system("cls")
        exportar_json()
        continue
    elif opcao == 8:
        system("cls")
        altera_senha(usuario)
        continue
    elif opcao == 9:
        system("cls")
        cadastra_usuario()
        continue
    elif opcao == 10:
        system("cls")
        agendar_manutencao()
        continue
    elif opcao == 11:
        system("cls")
        relatorio_agendamentos_manutencao()
        continue
    elif opcao == 12:
        system("cls")
        agendar_teste_drive()
        continue
    elif opcao == 13:
        system("cls")
        relatorio_agendamentos_teste_drive()
        continue
    elif opcao == 20:
        system("cls")
        sobre()
        continue
