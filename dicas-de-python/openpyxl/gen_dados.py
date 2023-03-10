from random import choice, randint, random

import openpyxl

ambientes = [
    'sala de estar',
    'sala de espera',
    'hall de entrada',
    'recepção',
    'cozinha',
    'sacada',
    'área de serviço',
    'lavabo',
    'toalete',
    'banheiro',
    'quarto',
    'quarto crianças',
    'quarto casal',
]

produtos = [
    'piso paginado',
    'parede',
    'rodapé',
    'soleira',
    'tabeira',
    'filete',
]

for i in range(15):
    ambiente = choice(ambientes)
    for j in range(randint(1, 6)):
        # print(ambiente)
        produto = choice(produtos)
        if produto == 'piso paginado' or produto == 'parede':
            descricao = f'{str(round(randint(1,60)* random(), 2)).replace(".", ",")} m² {produto}'  # noqa: E501
        else:
            descricao = f'{str(round(randint(1,60)* random(), 2)).replace(".", ",")}m x {randint(1,20)}cm {produto}'  # noqa: E501
        # print(descricao)
        quantidade = randint(1, 15)


def escreve_planilha_cliente(filename, worksheet):
    wb = openpyxl.Workbook()

    # Deleta o worksheet, caso exista.
    if worksheet in wb.sheetnames:
        wb.remove(wb[worksheet])

    # Cria um worksheet novo.
    ws = wb.create_sheet(worksheet)

    # Percorre as linhas, então
    for i in range(1, 2001):
        ambiente = choice(ambientes)
        for j in range(randint(4, 8)):
            ws[f'A{i}'] = 'id' if i == 1 else i - 1
            ws[f'B{i}'] = 'ambiente' if i == 1 else ambiente

            produto = choice(produtos)
            if produto == 'piso paginado' or produto == 'parede':
                descricao = f'{str(round(randint(1,60)* random(), 2)).replace(".", ",")} m² {produto}'  # noqa: E501
            else:
                descricao = f'{str(round(randint(1,60)* random(), 2)).replace(".", ",")}m x {randint(1,20)}cm {produto}'  # noqa E501

            ws[f'C{i}'] = 'produto' if i == 1 else descricao
            ws[f'D{i}'] = 'quantidade' if i == 1 else randint(1, 15)

    ws['E1'] = 'valor unitário'
    ws['F1'] = 'subtotal'

    wb.save(filename)


if __name__ == '__main__':
    filename = 'orcamento.xlsx'
    worksheet = 'planilha_cliente'
    escreve_planilha_cliente(filename, worksheet)
