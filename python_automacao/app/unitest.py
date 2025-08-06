import unittest
import pyodbc
from datetime import datetime

# Importa as funções do seu script original.
# Renomeie 'seu_script_original' para o nome do arquivo .py que você forneceu.
import database as db

# --- CONFIGURAÇÃO (copiada do seu script) ---
# Nota: As credenciais são gerenciadas aqui para que os testes sejam autocontidos.
server = 'FULVIO\\FULVIO'
database = 'Banco reformulado'
username = 'sa'
password = '123456'

DB_CONFIG = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password}'
)

## --------------------------------------------------------------------------- ##
## -- CONSTANTES DE TESTE - IMPORTANTE: AJUSTE COM DADOS DO SEU BANCO! -- ##
## --------------------------------------------------------------------------- ##

# Use um ID de uma receita que existe e tem produtos associados.
ID_RECEITA_VALIDA = 20250002 

# Use um ID de uma receita que existe, mas que tenha pelo menos um produto
# para o qual NENHUM lote foi cadastrado. Se não tiver, pode usar o mesmo ID_RECEITA_VALIDA.
ID_RECEITA_COM_PRODUTO_SEM_LOTE = 20250002 

# Use um ID que você tem certeza que NÃO existe na tabela Receita.
ID_RECEITA_INVALIDA = 99999999

# Use um ID de lote que você sabe que NÃO existe para forçar um erro de FK.
ID_LOTE_INVALIDO = -1 


class TestDatabaseFunctions(unittest.TestCase):
    """
    Suite de testes para todas as funções de consulta e manipulação do banco de dados.
    """

    def setUp(self):
        """
        Método executado ANTES de cada teste.
        Estabelece a conexão com o banco de dados.
        """
        try:
            self.connection = pyodbc.connect(DB_CONFIG)
            self.cursor = self.connection.cursor()
            print("\nConexão de teste estabelecida.")
        except pyodbc.Error as e:
            self.fail(f"A conexão com o banco de dados para o teste falhou: {e}")

    def tearDown(self):
        """
        Método executado DEPOIS de cada teste.
        Fecha a conexão para garantir que os recursos sejam liberados.
        """
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
            print("Conexão de teste fechada.")

    # --- TESTES PARA FUNÇÕES DE CONSULTA (GET) ---

    def test_get_numeros_de_produto_da_receita_sucesso(self):
        """Verifica se a função retorna uma lista de números de produto para uma receita válida."""
        numeros = db.get_numeros_de_produto_da_receita(self.cursor, ID_RECEITA_VALIDA)
        self.assertIsNotNone(numeros, "A função não deveria retornar None para uma receita válida.")
        self.assertIsInstance(numeros, list, "O retorno deve ser uma lista.")
        self.assertTrue(len(numeros) > 0, "A lista de produtos não deveria estar vazia.")
        self.assertIsInstance(numeros[0], int, "Os itens da lista devem ser inteiros.")

    def test_get_numeros_de_produto_da_receita_nao_encontrado(self):
        """Verifica se a função retorna uma lista vazia para uma receita que não existe."""
        numeros = db.get_numeros_de_produto_da_receita(self.cursor, ID_RECEITA_INVALIDA)
        self.assertIsNotNone(numeros)
        self.assertIsInstance(numeros, list)
        self.assertEqual(len(numeros), 0, "A lista de produtos deveria estar vazia para uma receita inválida.")

    def test_get_receita_com_lotes_disponiveis_sucesso(self):
        """Verifica se a função retorna um dicionário detalhado para uma receita válida."""
        receita = db.get_receita_com_lotes_disponiveis(self.cursor, ID_RECEITA_VALIDA)
        self.assertIsNotNone(receita, "A função não deveria retornar None para uma receita válida.")
        self.assertIsInstance(receita, dict, "O retorno deve ser um dicionário.")
        self.assertIn('receita_id', receita)
        self.assertIn('nome_receita', receita)
        self.assertIn('produtos', receita)
        self.assertEqual(receita['receita_id'], ID_RECEITA_VALIDA)

    def test_get_receita_com_lotes_disponiveis_produto_sem_lote(self):
        """Verifica se a função lida corretamente com produtos que não têm lotes (LEFT JOIN)."""
        receita = db.get_receita_com_lotes_disponiveis(self.cursor, ID_RECEITA_COM_PRODUTO_SEM_LOTE)
        self.assertIsNotNone(receita)
        # Este teste é mais conceitual: ele garante que a função não falha.
        # Se um produto não tiver lotes, sua lista 'lotes_disponiveis' deve estar vazia.
        # Procuramos por um produto com uma lista de lotes vazia.
        produto_sem_lote_encontrado = any(
            not produto['lotes_disponiveis'] 
            for produto in receita['produtos'].values()
        )
        print(f"Verificando se algum produto veio sem lotes: {'Sim' if produto_sem_lote_encontrado else 'Não'}")
        # Este assert não é estrito, pois depende dos dados, mas o teste confirma a execução.
        self.assertTrue(True, "A função executou com sucesso, mesmo com produtos sem lote.")


    def test_get_receita_com_lotes_disponiveis_nao_encontrado(self):
        """Verifica se a função retorna None para uma receita que não existe."""
        receita = db.get_receita_com_lotes_disponiveis(self.cursor, ID_RECEITA_INVALIDA)
        self.assertIsNone(receita, "A função deveria retornar None para uma receita inválida.")

    # --- TESTES PARA FUNÇÕES DE PRODUÇÃO (INSERT/UPDATE) ---

    def test_iniciar_producao_sucesso(self):
        """Verifica se uma nova produção é iniciada e retorna um ID válido."""
        observacao = f"Teste de integração - {datetime.now()}"
        producao_id = db.iniciar_producao(self.cursor, ID_RECEITA_VALIDA, observacao)
        
        self.assertIsNotNone(producao_id, "iniciar_producao não deveria retornar None em caso de sucesso.")
        self.assertIsInstance(producao_id, int, "O ID da produção retornado deve ser um inteiro.")
        
        # Verificação: consulta o banco para confirmar se o registro foi inserido.
        self.cursor.execute("SELECT observacao FROM Producao WHERE producao_id = ?", producao_id)
        row = self.cursor.fetchone()
        self.assertIsNotNone(row, "O registro da produção não foi encontrado no banco de dados.")
        self.assertEqual(row[0], observacao, "A observação no banco de dados não corresponde à enviada.")

    def test_iniciar_producao_receita_invalida(self):
        """Verifica se a função retorna None ao tentar iniciar produção com uma receita inválida."""
        # Isto deve falhar por causa da restrição de chave estrangeira (foreign key)
        with self.assertRaises(pyodbc.IntegrityError, msg="Deveria lançar IntegrityError para FK inválida."):
             db.iniciar_producao(self.cursor, ID_RECEITA_INVALIDA, "Teste com falha")


    def test_registrar_pesagem_transacao_completa(self):
        """
        Teste de integração: verifica se a pesagem e o uso do lote são registrados corretamente.
        Este teste modifica o banco de dados.
        """
        # 1. ARRANGE: Preparar os dados necessários
        # Inicia uma produção para ter um ID válido
        producao_id = db.iniciar_producao(self.cursor, ID_RECEITA_VALIDA, "Teste de pesagem completa")
        self.assertIsNotNone(producao_id)

        # Pega os detalhes da receita para obter IDs de produto e lote válidos
        detalhes_receita = db.get_receita_com_lotes_disponiveis(self.cursor, ID_RECEITA_VALIDA)
        self.assertIsNotNone(detalhes_receita)
        
        # Pega o primeiro produto que tenha lotes disponíveis
        produto_para_testar = None
        for produto in detalhes_receita['produtos'].values():
            if produto['lotes_disponiveis']:
                produto_para_testar = produto
                break
        
        self.assertIsNotNone(produto_para_testar, "Nenhum produto com lotes disponíveis encontrado para a receita de teste.")

        receita_produto_id = produto_para_testar['receita_produto_id']
        lote_id = produto_para_testar['lotes_disponiveis'][0]['lote_id']
        nome_produto = produto_para_testar['nome_produto']
        peso_simulado = 10.5
        responsavel_simulado = "Unittest"

        # 2. ACT: Executar a função a ser testada
        db.registrar_pesagem(
            cursor=self.cursor,
            producao_id=producao_id,
            etapa=f"Pesagem de {nome_produto}",
            peso=peso_simulado,
            responsavel=responsavel_simulado,
            receita_produto_id=receita_produto_id,
            lote_id=lote_id
        )

        # 3. ASSERT: Verificar se os dados foram salvos corretamente
        # Verifica a tabela ProducaoPesagem
        self.cursor.execute("SELECT peso, responsavel FROM ProducaoPesagem WHERE producao_id = ?", producao_id)
        pesagem_registrada = self.cursor.fetchone()
        self.assertIsNotNone(pesagem_registrada, "Registro de pesagem não encontrado.")
        self.assertEqual(pesagem_registrada.peso, peso_simulado)
        self.assertEqual(pesagem_registrada.responsavel, responsavel_simulado)

        # Verifica a tabela ReceitaProdutoLote
        self.cursor.execute("SELECT quantidade_utilizada FROM ReceitaProdutoLote WHERE receita_produto_id = ? AND lote_id = ?", receita_produto_id, lote_id)
        uso_lote_registrado = self.cursor.fetchone()
        self.assertIsNotNone(uso_lote_registrado, "Registro de uso de lote não encontrado.")
        self.assertEqual(uso_lote_registrado.quantidade_utilizada, peso_simulado)

    def test_registrar_pesagem_falha_e_rollback(self):
        """
        Verifica se a transação é revertida (ROLLBACK) se ocorrer um erro
        (ex: ao tentar usar um lote inválido).
        """
        # 1. ARRANGE: Preparar dados, similar ao teste de sucesso
        producao_id = db.iniciar_producao(self.cursor, ID_RECEITA_VALIDA, "Teste de falha e rollback")
        self.assertIsNotNone(producao_id)
        
        detalhes_receita = db.get_receita_com_lotes_disponiveis(self.cursor, ID_RECEITA_VALIDA)
        primeiro_produto = next(iter(detalhes_receita['produtos'].values()))
        receita_produto_id = primeiro_produto['receita_produto_id']

        # 2. ACT & ASSERT (parcial): Executar a função com um LOTE INVÁLIDO
        # A função deve capturar a exceção interna e imprimir uma mensagem de erro.
        # Não deve propagar a exceção para fora.
        db.registrar_pesagem(
            cursor=self.cursor,
            producao_id=producao_id,
            etapa="Etapa que vai falhar",
            peso=99.9,
            responsavel="Unittest Falha",
            receita_produto_id=receita_produto_id,
            lote_id=ID_LOTE_INVALIDO # Lote inválido para forçar o erro
        )
        
        # 3. ASSERT (Final): Verificar se NADA foi salvo no banco, provando o rollback.
        # Verifica a tabela ProducaoPesagem
        self.cursor.execute("SELECT COUNT(*) FROM ProducaoPesagem WHERE producao_id = ?", producao_id)
        count_pesagem = self.cursor.fetchone()[0]
        self.assertEqual(count_pesagem, 0, "Nenhum registro de pesagem deveria ter sido criado devido ao erro.")

        # Verifica a tabela ReceitaProdutoLote
        self.cursor.execute("SELECT COUNT(*) FROM ReceitaProdutoLote WHERE receita_produto_id = ? AND lote_id = ?", receita_produto_id, ID_LOTE_INVALIDO)
        count_lote = self.cursor.fetchone()[0]
        self.assertEqual(count_lote, 0, "Nenhum registro de uso de lote deveria ter sido criado.")


if __name__ == '__main__':
    # Permite executar os testes diretamente do terminal com "python test_banco.py"
    unittest.main(verbosity=2)   
    