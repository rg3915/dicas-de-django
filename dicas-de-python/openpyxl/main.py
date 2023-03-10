'''
Lê uma planilha em Excel, faz uns cálculos e escreve em outra planilha com openpyxl.

https://openpyxl.readthedocs.io/en/stable
https://openpyxl.readthedocs.io/en/stable/api/openpyxl.worksheet.worksheet.html?highlight=iter_cols#openpyxl.worksheet.worksheet.Worksheet.iter_cols

https://rich.readthedocs.io/en/stable/
'''
from decimal import Decimal

import openpyxl
from openpyxl.styles import Font
from rich.console import Console
from rich.table import Table

console = Console()


def read_data_only(filename, worksheet, title, data_only=True):
    wb = openpyxl.load_workbook(filename, data_only=data_only)
    ws = wb[worksheet]

    max_row = ws.max_row
    max_col = ws.max_column

    print('\n', 'Percorre as colunas:')
    # Imprime apenas a primeira linha.
    for col in ws.iter_cols(max_row=max_row, max_col=max_col):
        print(col[0].value)

    print('\n', 'Percorre as colunas e as linhas:')
    for col in ws.iter_cols(max_row=max_row, max_col=max_col):
        for cell in col:
            print(cell.value)

    print('\n', 'Percorre as linhas:')
    # Imprime apenas a primeira coluna.
    for row in ws.iter_rows(max_row=max_row, max_col=max_col):
        print(row[0].value)

    table = Table(title=title)

    headers = [row[0].value for row in ws.iter_cols(max_row=max_row, max_col=max_col)]
    print('headers:', headers)

    for header in headers:
        table.add_column(header)

    for row in ws.iter_rows(min_row=2, max_row=max_row, max_col=max_col):
        # o rich.table só imprime strings
        values = [f'{cell.value}' for cell in row]
        table.add_row(*values)

    console.print(table)

    # O resultado de saída da função começa aqui.
    items = []
    for row in ws.iter_rows(max_row=max_row, max_col=max_col):
        items.append([cell.value for cell in row])

    return items


def get_comprimento_e_largura(descricao):
    '''
    Retorna comprimento e largura.
    '''
    # Extrai o comprimento
    comprimento, largura = 0, 0
    if 'm' in descricao[0]:
        comprimento = descricao[0][:-1]
        print(comprimento)

        comprimento = comprimento.replace(',', '.')
        comprimento = Decimal(comprimento)
        print(comprimento)
        print()
    else:
        comprimento = Decimal(descricao[0].replace(',', '.'))

    # Extrai largura
    if 'cm' in descricao[2]:
        largura = Decimal(descricao[2][:-2]) / 100
        print('largura', largura)
    else:
        largura = 1

    return (comprimento, largura)


def get_medidas(items):
    '''
    Retorna uma lista de tuplas com
    (comprimento, largura)
    '''
    # Pega somente os produtos.
    produtos = [item[2] for item in items]
    print(produtos)

    medidas = []
    for produto in produtos:
        if produto != 'produto':
            print(produto.split())
            descricao = produto.split()

            comprimento, largura = get_comprimento_e_largura(descricao)
            print('medidas:', comprimento, largura)
            medidas.append((comprimento, largura))

    table = Table(title='Medidas')

    headers = ('comprimento', 'largura')
    for header in headers:
        table.add_column(header)

    for row in medidas:
        # o rich.table só imprime strings
        values = [f'{cell}' for cell in row]
        table.add_row(*values)

    console.print(table)

    # Adiciona o cabeçalho na lista.
    medidas.insert(0, headers)

    # O metro quadrado será calculado com fórmula na planilha.
    return medidas


def escreve_orcamento(filename, worksheet, items, medidas):
    wb = openpyxl.load_workbook(filename)

    # Deleta o worksheet, caso exista.
    if worksheet in wb.sheetnames:
        wb.remove(wb[worksheet])

    # Cria um worksheet novo.
    ws = wb.create_sheet(worksheet)

    # Percorre as linhas, então
    for i, item in enumerate(items, start=1):
        # Lê a partir do segundo indice
        ws[f'A{i}'] = item[0]  # id
        ws[f'B{i}'] = item[1]  # ambiente
        ws[f'C{i}'] = item[2]  # produto
        ws[f'D{i}'] = medidas[i - 1][0]  # comprimento
        ws[f'E{i}'] = medidas[i - 1][1]  # largura
        ws[f'G{i}'] = item[3]  # quantidade

    ws['K1'] = 'valor por m²'
    ws['K2'] = 90

    wb.save(filename)


def insere_linhas(filename, worksheet, items):
    wb = openpyxl.load_workbook(filename)
    ws = wb[worksheet]

    # teste
    ambientes = [
        'sala de estar',
        'sala de estar',
        'sala de estar',
        'cozinha',
        'cozinha',
        'cozinha',
        'lavabo',
        'lavabo',
        'lavabo',
    ]

    _indices = [
        i for i in range(1, len(ambientes))
        if ambientes[i] != ambientes[i - 1]
    ]
    print(_indices)

    # Fim do teste

    # Pega os ambientes, sem o cabeçalho.
    ambientes = [i[1] for i in items][1:]
    print('ambientes')
    print(ambientes)

    _indices = [
        i for i in range(1, len(ambientes))
        if ambientes[i] != ambientes[i - 1]
    ]

    '''
    Precisamos inserir as linhas de baixo para cima, então
    vamos inverter a ordem dos índices.
    '''
    indices = sorted(_indices, reverse=True)
    for i in indices:
        ws.insert_rows(i + 2, amount=2)
        ws[f'I{i+2}'] = 'subtotal'

    # E escreve no último
    ws[f'I{ws.max_row+1}'] = 'subtotal'

    wb.save(filename)


def insere_formulas(filename, worksheet):
    wb = openpyxl.load_workbook(filename)
    ws = wb[worksheet]

    max_row = ws.max_row
    max_col = ws.max_column

    ambientes = []
    for i, row in enumerate(ws.iter_rows(max_row=max_row, max_col=max_col), start=1):
        print('>>>>>>>', row[0].value)
        _id = row[0].value
        if _id:
            ws[f'F{i}'] = 'm² unit' if i == 1 else f'=D{i}*E{i}'  # metro quadrado
            ws[f'H{i}'] = 'm² total' if i == 1 else f'=G{i}*F{i}'  # metro quadrado total  # noqa: E501
            ws[f'I{i}'] = 'valor unitário' if i == 1 else f'=K$2*F{i}'
            ws[f'J{i}'] = 'subtotal' if i == 1 else f'=K$2*H{i}'

        ambientes.append(row[1].value)

    print('ambientes <---------------')
    print(ambientes)

    _indices = [
        i for i in range(1, len(ambientes))
        if ambientes[i] != ambientes[i - 1]
    ]
    print(_indices)

    '''
    Para entender isso aqui,
    vamos imprimir os indices na tabela
    '''
    for i in _indices:
        ws[f'L{i}'] = f'{i}'  # pode deletar depois

    '''
    Repare que precisamos de i+1, quando o indice é par, então
    (digitar 2, 4, 7, 9, 12, 14 manualmente na planilha)
    '''
    par, impar = [], []
    for i, indice in enumerate(_indices):
        if i % 2:  # impar
            impar.append(indice)
        else:  # par
            # porque precisamos descer uma célula no intervalo do somatório
            par.append(indice + 1)

    print('par, impar')
    print(par, impar)

    # Calcula os subtotais
    for inicial, final in zip(par, impar):
        ws[f'J{final+1}'] = f'=SUM(J{inicial}:J{final})'

    # Calcula o total com SOMASE
    ws[f'I{ws.max_row+1}'] = 'TOTAL'
    last_row = ws.max_row
    ws[f'J{last_row}'] = f'=SUMIF(I2:I{last_row}, "subtotal", J2:j{last_row})'

    wb.save(filename)


def escreve_planilha_cliente_final(filename, worksheet_in, worksheet_out):
    wb = openpyxl.load_workbook(filename)

    # Deleta o worksheet, caso exista.
    if worksheet_out in wb.sheetnames:
        wb.remove(wb[worksheet_out])

    ws_in = wb[worksheet_in]
    ws_out = wb.create_sheet(worksheet_out)

    max_row = ws_in.max_row
    max_col = ws_in.max_column

    for i, row in enumerate(ws_in.iter_rows(max_row=max_row, max_col=max_col), start=1):
        ws_out[f'A{i}'] = row[0].value
        ws_out[f'B{i}'] = row[1].value
        ws_out[f'C{i}'] = row[2].value
        ws_out[f'D{i}'] = row[3].value
        ws_out[f'E{i}'] = 'valor unitário' if i == 1 else f'=VLOOKUP($A{i},planilha_orcamento!A:I,9,FALSE)'  # noqa: E501
        ws_out[f'F{i}'] = 'subtotal' if i == 1 else f'=E{i}*D{i}'

    # Calcula total geral
    ws_out[f'E{max_row+1}'] = 'TOTAL'
    ws_out[f'F{max_row+1}'] = f'=SUM(F2:F{max_row})'

    wb.save(filename)


def aplica_negrito_planilha_orcamento(filename):
    wb = openpyxl.load_workbook(filename)
    ws = wb['planilha_orcamento']

    cols = 'A B C D E F G H I J K'.split()
    for col in cols:
        # Negrito
        ws[f'{col}1'].font = Font(
            name='Arial',
            size=10,
            bold=True,
            italic=False
        )

    max_row = ws.max_row
    max_col = ws.max_column

    for i, row in enumerate(ws.iter_rows(max_row=max_row, max_col=max_col), start=1):
        if 'subtotal' == row[8].value or 'TOTAL' == row[8].value:
            # Total
            ws[f'I{i}'].font = Font(
                name='Arial',
                size=10,
                bold=True,
                italic=False
            )
            ws[f'J{i}'].font = Font(
                name='Arial',
                size=10,
                bold=True,
                italic=False
            )

    wb.save(filename)


def aplica_negrito_planilha_cliente_final(filename):
    wb = openpyxl.load_workbook(filename)
    ws = wb['planilha_cliente_final']

    cols = 'A B C D E F'.split()
    for col in cols:
        # Negrito
        ws[f'{col}1'].font = Font(
            name='Arial',
            size=10,
            bold=True,
            italic=False
        )

    # Total
    ws[f'E{ws.max_row}'].font = Font(
        name='Arial',
        size=10,
        bold=True,
        italic=False
    )
    ws[f'F{ws.max_row}'].font = Font(
        name='Arial',
        size=10,
        bold=True,
        italic=False
    )

    wb.save(filename)


if __name__ == '__main__':
    filename = 'orcamento.xlsx'
    items = read_data_only(
        filename=filename,
        worksheet='planilha_cliente',
        title='Planilha do Cliente'
    )
    print(items, '\n')

    medidas = get_medidas(items)
    print(medidas)

    escreve_orcamento(
        filename=filename,
        worksheet='planilha_orcamento',
        items=items,
        medidas=medidas
    )

    # Primeiro insere as linhas
    insere_linhas(
        filename=filename,
        worksheet='planilha_orcamento',
        items=items
    )

    # Depois as fórmulas
    insere_formulas(
        filename=filename,
        worksheet='planilha_orcamento',
    )

    read_data_only(
        filename=filename,
        worksheet='planilha_orcamento',
        title='Planilha Orçamento',
        data_only=False
    )

    escreve_planilha_cliente_final(
        filename=filename,
        worksheet_in='planilha_cliente',
        worksheet_out='planilha_cliente_final',
    )

    aplica_negrito_planilha_orcamento(filename)
    aplica_negrito_planilha_cliente_final(filename)

    read_data_only(
        filename=filename,
        worksheet='planilha_cliente_final',
        title='Planilha Cliente Final',
        data_only=False
    )
