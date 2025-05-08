from django.db import models
from datetime import timedelta

class Profissional(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Servico(models.Model):
    nome = models.CharField(max_length=100)
    duracao_padrao = models.PositiveIntegerField(help_text="Duração padrão em minutos")
    valor_padrao = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome
    
class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=15, blank=True, null=True)


    def __str__(self):
        return self.nome

class Agendamento(models.Model):
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE)
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    data_hora_agendamento = models.DateTimeField(auto_now_add=True)
    data_hora_inicio = models.DateTimeField()
    data_hora_fim = models.DateTimeField()
    valor_cobrado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.servico.nome} com {self.profissional.nome} em {self.data_hora_inicio}"