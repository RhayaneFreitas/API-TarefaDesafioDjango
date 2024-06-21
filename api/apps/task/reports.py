from openpyxl import Workbook
from django.http import HttpResponse
from weasyprint import HTML
from django.template.loader import get_template

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
    
class ReportPDF(Report):
    def export(self):
        # Gerar o conteúdo HTML do relatório usando um template
        context = {
            'title': self.title,
            'columns': self.columns,
            'data': self.data,
        }
        template = get_template('report_user_created_and_finished.html')  # Carrega o template HTML
        html_content = template.render(context)  # Renderiza o template com os dados
        
        # Converter o HTML para PDF usando WeasyPrint
        pdf_file = HTML(string=html_content).write_pdf()
        
        # Retornar o PDF como uma resposta HTTP
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{self.title}.pdf"'
        return response