from random import randint

import openpyxl


def escreve_planilha(filename, worksheet=None):
    wb = openpyxl.Workbook()

    if worksheet:
        # Deleta o worksheet, caso exista.
        if worksheet in wb.sheetnames:
            wb.remove(wb[worksheet])

        # Cria um worksheet novo.
        ws = wb.create_sheet(worksheet)
    else:
        ws = wb.active

    # Percorre as linhas, então
    for i in range(1, 12):
        ws[f'A{i}'] = 'id' if i == 1 else i - 1
        ws[f'B{i}'] = 'quantidade' if i == 1 else randint(1, 100)

    wb.save(filename)


def le_planilha(filename, worksheet, data_only=True):
    wb = openpyxl.load_workbook(filename, data_only=data_only)
    ws = wb[worksheet]

    max_row = ws.max_row
    max_col = ws.max_column

    print('\n', 'Percorre as colunas:')
    for col in ws.iter_cols(max_row=max_row, max_col=max_col):
        for cell in col:
            print(cell.value)

    print('\n', 'Percorre as linhas:')
    for row in ws.iter_rows(max_row=max_row, max_col=max_col):
        print(row[0].value, row[1].value)


if __name__ == '__main__':
    escreve_planilha(filename='teste1.xlsx', worksheet='planilha_cliente')
    escreve_planilha(filename='teste2.xlsx')
    le_planilha(filename='teste1.xlsx', worksheet='planilha_cliente')
