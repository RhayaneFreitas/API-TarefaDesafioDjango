from openpyxl import Workbook
from django.http import HttpResponse

class Report:
    def __init__(self, title, columns, data):
        self.title = title
        self.columns = columns
        self.data = data
        
    def export(self):
        raise  NotImplementedError('Método de exportação deve ser implementado')
        
class ReportExcel(Report):
        
    def export(self):
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = self.title
        worksheet.append(self.columns)
        
        for row in self.data:
            worksheet.append(row) # Cada item da lista está sendo descompactado e sendo passado um valor sozinho
            
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={self.title}.xlsx'
        workbook.save(response)

        return response 