import pandas
from io import BytesIO


def convert_list_of_dict_to_excel_table(data_list):
    df = pandas.DataFrame(data_list)
    output = BytesIO()
    with pandas.ExcelWriter(output) as writer:
        df.to_excel(writer)
    output.seek(0)
    return output


def convert_list_of_dict_to_csv(data_list):
    df = pandas.DataFrame(data_list)
    output = BytesIO()
    df.to_csv(output)
    output.seek(0)
    return output
